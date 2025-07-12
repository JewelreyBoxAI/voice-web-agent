import os
import json
import base64
import logging
import sys
from dotenv import load_dotenv

load_dotenv()

from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, HTMLResponse, RedirectResponse, FileResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from langchain_openai import ChatOpenAI
from langchain_core.chat_history import InMemoryChatMessageHistory
from langchain.prompts import ChatPromptTemplate
from langchain.schema.messages import HumanMessage, AIMessage
from elevenlabs.client import ElevenLabs

# ─── Logger Setup ────────────────────────────────
logger = logging.getLogger("jewelrybox_ai")
logger.setLevel(logging.INFO)

# ─── Paths & Templates ───────────────────────────
ROOT = os.path.dirname(os.path.abspath(__file__))
templates = Jinja2Templates(directory=os.path.join(ROOT, "templates"))

# ─── Load Prompt Data ────────────────────────────
try:
    with open(os.path.join(ROOT, "prompts", "prompt.json"), "r") as f:
        system_data = json.load(f)["jewelry_ai"][0]["systemPrompt"]
except FileNotFoundError:
    logger.error("prompt.json missing")
    sys.exit(1)

# Simple standardized prompt
system_prompt = f"You are {system_data['identity']}, {system_data['role']}. Provide helpful, concise responses."

# ─── Avatar Setup ────────────────────────────────
img_path = os.path.join(ROOT, "images", "male_avatar.png")
if os.path.exists(img_path):
    with open(img_path, "rb") as img:
        IMG_URI = "data:image/png;base64," + base64.b64encode(img.read()).decode()
else:
    IMG_URI = "https://via.placeholder.com/60x60/0066cc/ffffff?text=💎"

# ─── FastAPI App ─────────────────────────────────
app = FastAPI(title="JewelryBox.AI Assistant")
app.add_middleware(
    CORSMiddleware,
    allow_origins=os.getenv("ALLOWED_ORIGINS", "*").split(","),
    allow_methods=["*"],
    allow_headers=["*"],
)

# ─── LLM & Memory ────────────────────────────────
memory = InMemoryChatMessageHistory()
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.9, max_tokens=1024)

prompt_template = ChatPromptTemplate.from_messages([
    ("system", system_prompt),
    ("placeholder", "{history}"),
    ("human", "{user_input}")
])

chain = prompt_template | llm

# ─── Request Models ──────────────────────────────
class ChatRequest(BaseModel):
    user_input: str
    history: list

class VoiceTranscriptRequest(BaseModel):
    user_input: str
    ai_response: str

# ─── Unified Response Processor ──────────────────
def process_ai_response(user_input: str, ai_response: str) -> str:
    # URL injection can go here; simplified for brevity
    return ai_response

# ─── Routes ──────────────────────────────────────
@app.get("/")
async def root():
    return RedirectResponse(url="/voice")

@app.get("/voice", response_class=HTMLResponse)
async def voice_widget(request: Request):
    scheme = "https" if "onrender.com" in request.url.netloc else request.url.scheme
    return templates.TemplateResponse("voice_widget.html", {
        "request": request,
        "chat_url": f"{scheme}://{request.url.netloc}/chat",
        "voice_process_url": f"{scheme}://{request.url.netloc}/voice/process",
        "img_uri": IMG_URI,
    })

@app.post("/chat")
async def chat(req: ChatRequest):
    try:
        history_msgs = [
            HumanMessage(content=m["content"]) if m["role"] == "human" else AIMessage(content=m["content"])
            for m in req.history or []
        ]

        response = chain.invoke({"user_input": req.user_input, "history": history_msgs})
        reply = process_ai_response(req.user_input, response.content.strip())

        memory.add_user_message(req.user_input)
        memory.add_ai_message(reply)

        return JSONResponse({
            "reply": reply,
            "history": [{"role": m.type, "content": m.content} for m in memory.messages]
        })
    except Exception as e:
        logger.error(f"Chat error: {e}")
        return JSONResponse(status_code=500, content={"error": "Internal error."})

@app.post("/voice/process")
async def voice_process(req: VoiceTranscriptRequest):
    processed_response = process_ai_response(req.user_input, req.ai_response)
    return JSONResponse({"processed_response": processed_response})

@app.post("/voice/tts")
async def generate_speech(request: Request):
    try:
        body = await request.json()
        text = body.get("text", "")
        if not text:
            return JSONResponse(status_code=400, content={"error": "No text provided"})

        elevenlabs_client = ElevenLabs(api_key=os.getenv('ELEVENLABS_API_KEY'))
        voice_id = os.getenv('ELEVENLABS_VOICE_ID', 'JBFqnCBsd6RMkjVDRZzb')

        audio_stream = elevenlabs_client.text_to_speech.convert(
            text=text, voice_id=voice_id, model_id="eleven_multilingual_v2", output_format="mp3_44100_128"
        )

        audio_bytes = b"".join(audio_stream)

        return Response(
            content=audio_bytes,
            media_type="audio/mpeg",
            headers={"Content-Disposition": "attachment; filename=speech.mp3"}
        )
    except Exception as e:
        logger.error(f"TTS error: {e}")
        return JSONResponse(status_code=500, content={"error": "TTS generation failed"})

@app.post("/clear_chat")
async def clear_chat():
    memory.clear()
    return JSONResponse({"status": "ok", "message": "Chat cleared."})

@app.get("/widget", response_class=HTMLResponse)
async def widget(request: Request):
    scheme = "https" if "onrender.com" in request.url.netloc else request.url.scheme
    return templates.TemplateResponse("widget.html", {
        "request": request,
        "chat_url": f"{scheme}://{request.url.netloc}/chat",
        "img_uri": IMG_URI,
    })

@app.get("/static/images/custom_components/{filename}")
async def static_files(filename: str):
    file_path = os.path.join(ROOT, "images", "custom_components", filename)
    if os.path.exists(file_path):
        return FileResponse(file_path)
    return JSONResponse(status_code=404, content={"error": "File not found"})

@app.get("/favicon.ico")
async def favicon():
    return FileResponse(os.path.join(ROOT, "images", "diamond.ico"), media_type="image/x-icon")

# ─── CLI Sanity Test ─────────────────────────────
if __name__ == "__main__":
    print("JewelryBox.AI CLI (type 'exit')")
    cli_history = []
    while True:
        try:
            text = input("You: ")
            if text.lower() in ("exit", "quit"):
                sys.exit(0)
            res = chain.invoke({"user_input": text, "history": cli_history})
            reply = res.content.strip()
            print(f"AI: {reply}")
            memory.add_user_message(text)
            memory.add_ai_message(reply)
            cli_history = memory.messages
        except KeyboardInterrupt:
            sys.exit(0)
        except Exception as e:
            print(f"Error: {e}")
