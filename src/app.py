import json
import logging
import os
import sys
import base64
from dotenv import load_dotenv

# Load environment variables FIRST before any other imports
load_dotenv()

from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, HTMLResponse, RedirectResponse, FileResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel

# LangChain imports
from langchain_core.chat_history import InMemoryChatMessageHistory
from langchain_core.messages import BaseMessage
from langchain_openai import ChatOpenAI
from langchain.prompts import (
    ChatPromptTemplate,
    SystemMessagePromptTemplate,
    HumanMessagePromptTemplate,
    MessagesPlaceholder,
)

# Memory Manager import
from . import memory_manager

# ─── ENV + LOGGING ───────────────────────────────────────────────────────────

logger = logging.getLogger("jewelrybox_ai")
logger.setLevel(logging.INFO)

# ─── PATHS & TEMPLATES ────────────────────────────────────────────────────────

ROOT = os.path.dirname(os.path.abspath(__file__))
TEMPLATE_DIR = os.path.join(ROOT, "templates")
templates = Jinja2Templates(directory=TEMPLATE_DIR)

# ─── LOAD PROMPT CONFIG ───────────────────────────────────────────────────────

prompt_file = os.path.join(ROOT, "prompts", "prompt.json")
try:
    with open(prompt_file, "r", encoding="utf-8") as f:
        AGENT_ROLES = json.load(f)
except FileNotFoundError:
    logger.error(f"Prompt file not found at {prompt_file}")
    sys.exit("Prompt configuration is missing. Aborting startup.")

# ─── LOAD KNOWLEDGEBASE CONFIG ───────────────────────────────────────────────

kb_file = os.path.join(ROOT, "prompts", "diamond_family_kb.json")
try:
    with open(kb_file, "r", encoding="utf-8") as f:
        DIAMOND_KB = json.load(f)["diamond_family_kb"]
except FileNotFoundError:
    logger.warning(f"Knowledgebase file not found at {kb_file}")
    DIAMOND_KB = {}


# ─── ENCODE AVATAR IMAGE ──────────────────────────────────────────────────────

img_path = os.path.join(ROOT, "images", "male_avatar.png.png")
if os.path.exists(img_path):
    with open(img_path, "rb") as img:
        IMG_URI = "data:image/png;base64," + base64.b64encode(img.read()).decode()
else:
    logger.warning(f"Image not found at {img_path}, using fallback.")
    IMG_URI = "https://via.placeholder.com/60x60/0066cc/ffffff?text=💎"

# ─── FASTAPI SETUP ───────────────────────────────────────────────────────────

app = FastAPI(title="JewelryBox.AI Assistant")
app.add_middleware(
    CORSMiddleware,
    allow_origins=os.getenv("ALLOWED_ORIGINS", "").split(","),
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
)

# ─── LLM + MEMORY ─────────────────────────────────────────────────────────────

memory = InMemoryChatMessageHistory(return_messages=True)
llm = ChatOpenAI(model="gpt-4o-mini", max_tokens=1024, temperature=0.9)

system_data = AGENT_ROLES["jewelry_ai"][0]["systemPrompt"]

# ─── INJECT DESIGNER LISTS ────────────────────────────────────────────────────

designer_guardrails = DIAMOND_KB.get("productsDesigners", {}).get("guardrails", {}).get("designerVerification", {})

allowed_designers = designer_guardrails.get("allowedDesigners", [])
denied_designers = designer_guardrails.get("deniedDesigners", [])
designer_response_policy = designer_guardrails.get("responsePolicy", "If unsure, ask the user clarifying questions.")

formatted_allowed = "\n• " + "\n• ".join(sorted(allowed_designers))
formatted_denied = "\n• " + "\n• ".join(sorted(denied_designers))

logger.info(f"Loaded {len(allowed_designers)} allowed designers and {len(denied_designers)} denied designers into system prompt.")

# Format system message block
system_prompt = f"""You are {system_data['identity']}, serving as {system_data['role']}.

Tone: {system_data['tone']}

{chr(10).join(system_data['description'])}

Domains of Expertise:
{chr(10).join(system_data['knowledgeDomains'])}

Customer Service Principles:
{chr(10).join(system_data['customerServiceExcellence'])}

Anti-Looping Guidelines:
Principles:
{chr(10).join(system_data['antiLooping']['principles'])}
Variation Techniques:
{chr(10).join(system_data['antiLooping']['variationTechniques'])}
Context Awareness:
{chr(10).join(system_data['antiLooping']['contextAwareness'])}

Style Guide:
Formatting:
{chr(10).join(system_data['styleGuide']['formatting'])}
Response Structure Principles:
{chr(10).join(system_data['styleGuide']['responseStructure']['principles'])}
Formatting Guidelines:
• Headers: {system_data['styleGuide']['responseStructure']['formatting']['headers']}
• Emphasis: {system_data['styleGuide']['responseStructure']['formatting']['emphasis']}
• Lists: {system_data['styleGuide']['responseStructure']['formatting']['lists']}
• Spacing: {system_data['styleGuide']['responseStructure']['formatting']['spacing']}
• Structure: {system_data['styleGuide']['responseStructure']['formatting']['structure']}
Language:
{chr(10).join(system_data['styleGuide']['language'])}

Pricing Guidance:
{chr(10).join(system_data['pricingGuidance'])}

Care & Maintenance:
{chr(10).join(system_data['careAndMaintenance'])}

Gift Guidance:
{chr(10).join(system_data['giftGuidance'])}

Closing Style:
{chr(10).join(system_data['signatureCloser'])}

Landmine Detection and Diffusion Strategy:
{system_data['landmineDetectionAndDiffusion']['strategy']}

Risk Categories and Handling:
• Ethical Sourcing: {system_data['landmineDetectionAndDiffusion']['categories']['ethicalSourcing']}
• Pricing Risks: {system_data['landmineDetectionAndDiffusion']['categories']['pricingRisks']}
• Lab Diamond Confusion: {system_data['landmineDetectionAndDiffusion']['categories']['labDiamondConfusion']}
• Certification Claims: {system_data['landmineDetectionAndDiffusion']['categories']['certificationClaims']}
• Care and Cleaning: {system_data['landmineDetectionAndDiffusion']['categories']['careAndCleaning']}
• Service Scope: {system_data['landmineDetectionAndDiffusion']['categories']['serviceScope']}
• Memory Mismatch: {system_data['landmineDetectionAndDiffusion']['categories']['memoryMismatch']}
• Location Mismatch: {system_data['landmineDetectionAndDiffusion']['categories']['locationMismatch']}

Designer Knowledge Guardrails:

Designers Carried by Diamond Family:
{formatted_allowed}

Designers NOT Carried:
{formatted_denied}

Response Policy:
{designer_response_policy}

Knowledgebase Profile:
• Location: {DIAMOND_KB.get('businessProfile', {}).get('primaryLocation', 'N/A')}
• Website: {DIAMOND_KB.get('businessProfile', {}).get('contact', {}).get('website', 'N/A')}
• Appointment Link: {DIAMOND_KB.get('services', {}).get('scheduling', {}).get('preferredTool', 'N/A')}
• POS System: {DIAMOND_KB.get('systemTools', {}).get('POS', 'N/A')}
• CRM: {DIAMOND_KB.get('systemTools', {}).get('CRM', 'N/A')}
• Featured Event: {DIAMOND_KB.get('eventsPromotions', {}).get('calendar', [{}])[0].get('event', 'N/A')}

Tagline: {system_data['tagline']}

IMPORTANT INSTRUCTION:
{system_data['humanPrompt']}
"""

prompt_template = ChatPromptTemplate.from_messages([
    SystemMessagePromptTemplate.from_template(system_prompt),
    MessagesPlaceholder(variable_name="history"),
    HumanMessagePromptTemplate.from_template("{user_input}")
])
chain = prompt_template | llm

# ─── UNIFIED RESPONSE PROCESSOR ──────────────────────────────────────────────

def process_ai_response(user_input: str, ai_response: str) -> str:
    """
    Unified processor for both text and voice responses to ensure consistency.
    Applies URL injection and any other post-processing.
    """
    try:
        # Apply memory manager URL injection
        processed_response = memory_manager.inject_relevant_url(user_input, ai_response)
        return processed_response
    except Exception as e:
        logger.error(f"Error processing AI response: {e}")
        return ai_response  # Return original if processing fails

# ─── REQUEST MODEL ────────────────────────────────────────────────────────────

class ChatRequest(BaseModel):
    user_input: str
    history: list

class VoiceTranscriptRequest(BaseModel):
    user_input: str
    ai_response: str

# ─── ROOT REDIRECT ───────────────────────────────────────────────────────────

@app.get("/")
async def root():
    """Redirect root URL to the voice widget"""
    return RedirectResponse(url="/voice")

# ─── MAIN ROUTES ──────────────────────────────────────────────────────────────

@app.get("/voice", response_class=HTMLResponse)
async def voice_chat(request: Request):
    """Render the voice-enabled chat widget UI"""
    # Force HTTPS for production deployments (Render.com, etc.)
    scheme = "https" if "onrender.com" in str(request.url.netloc) or request.url.scheme == "https" else request.url.scheme
    
    return templates.TemplateResponse(
        "voice_widget.html",
        {
            "request": request,
            "chat_url": f"{scheme}://{request.url.netloc}/chat",
            "voice_process_url": f"{scheme}://{request.url.netloc}/voice/process",
            "img_uri": IMG_URI,
        },
    )

# ─── CHAT ENDPOINT ───────────────────────────────────────────────────────────

def serialize_messages(messages: list[BaseMessage]):
    return [{"role": msg.type, "content": msg.content} for msg in messages]

@app.post("/chat")
async def chat(req: ChatRequest):
    try:
        history = req.history or []
        result = chain.invoke({"user_input": req.user_input, "history": history})
        reply = result.content.strip()
        
        # Use unified response processor
        reply = process_ai_response(req.user_input, reply)
        
        memory.add_user_message(req.user_input)
        memory.add_ai_message(reply)
        return JSONResponse({
            "reply": reply,
            "history": serialize_messages(memory.messages)
        })
    except Exception as e:
        logger.error(f"Error in /chat: {e}", exc_info=True)
        return JSONResponse(
            status_code=500,
            content={"error": "An internal error occurred. Please try again later."}
        )

# ─── VOICE RESPONSE PROCESSOR ────────────────────────────────────────────────

@app.post("/voice/process")
async def process_voice_response(req: VoiceTranscriptRequest):
    """
    Process voice responses to ensure they match text output formatting.
    This endpoint is called by the frontend after receiving voice responses.
    """
    try:
        # Use the same processing pipeline as text chat
        processed_response = process_ai_response(req.user_input, req.ai_response)
        
        return JSONResponse({
            "processed_response": processed_response
        })
    except Exception as e:
        logger.error(f"Error processing voice response: {e}", exc_info=True)
        return JSONResponse(
            status_code=500,
            content={"error": "Failed to process voice response"}
        )

# ─── CLEAR CHAT ENDPOINT ──────────────────────────────────────────────────────

@app.post("/clear_chat")
async def clear_chat():
    """
    Clear in-memory chat history for all users (global reset).
    Note: This affects all sessions since memory is global.
    """
    try:
        memory.clear()
        return JSONResponse({"status": "ok", "message": "Chat history cleared."})
    except Exception as e:
        logger.error(f"Error clearing chat history: {e}", exc_info=True)
        return JSONResponse(
            status_code=500,
            content={"error": "Failed to clear chat history."}
        )

# ─── ELEVENLABS TTS ENDPOINT ──────────────────────────────────────────────────

@app.post("/voice/tts")
async def generate_speech(request: Request):
    """
    Generate speech using ElevenLabs TTS API.
    This endpoint takes text and returns audio using the voice ID from environment variables.
    """
    try:
        from elevenlabs.client import ElevenLabs
        
        # Get the text from request body
        body = await request.json()
        text = body.get("text", "")
        
        if not text:
            return JSONResponse(
                status_code=400,
                content={"error": "Text is required"}
            )
        
        # Initialize ElevenLabs client
        elevenlabs_client = ElevenLabs(api_key=os.getenv('ELEVENLABS_API_KEY'))
        
        # Get voice ID from environment variable, fallback to a default
        voice_id = os.getenv('ELEVENLABS_VOICE_ID', 'JBFqnCBsd6RMkjVDRZzb')  # Rachel voice as fallback
        
        # Generate audio
        audio = elevenlabs_client.text_to_speech.convert(
            text=text,
            voice_id=voice_id,
            model_id="eleven_multilingual_v2",
            output_format="mp3_44100_128",
        )
        
        # Convert audio generator to bytes
        audio_bytes = b"".join(audio)
        
        # Return audio as response
        return Response(
            content=audio_bytes,
            media_type="audio/mpeg",
            headers={
                "Content-Disposition": "attachment; filename=speech.mp3"
            }
        )
        
    except Exception as e:
        logger.error(f"Error generating speech: {e}", exc_info=True)
        return JSONResponse(
            status_code=500,
            content={"error": "Failed to generate speech"}
        )

# ─── WIDGET ENDPOINT ─────────────────────────────────────────────────────────

@app.get("/widget", response_class=HTMLResponse)
async def widget(request: Request):
    """Render the chat widget UI"""
    # Force HTTPS for production deployments (Render.com, etc.)
    scheme = "https" if "onrender.com" in str(request.url.netloc) or request.url.scheme == "https" else request.url.scheme
    
    return templates.TemplateResponse(
        "widget.html",
        {
            "request": request,
            "chat_url": f"{scheme}://{request.url.netloc}/chat",
            "img_uri": IMG_URI,
        },
    )

# ─── STATIC FILES ENDPOINT ────────────────────────────────────────────────────

@app.get("/static/images/custom_components/{filename}")
async def serve_custom_components(filename: str):
    """Serve custom component images"""
    file_path = os.path.join(ROOT, "images", "custom_components", filename)
    if os.path.exists(file_path):
        return FileResponse(file_path)
    else:
        return JSONResponse(status_code=404, content={"error": "File not found"})

# ─── FAVICON ENDPOINT ────────────────────────────────────────────────────────

@app.get("/favicon.ico")
async def favicon():
    """Serve the favicon"""
    favicon_path = os.path.join(ROOT, "images", "diamond.ico")
    return FileResponse(favicon_path, media_type="image/x-icon")

# ─── CLI SANITY TEST ───────────────────────────────────────────────────────────

if __name__ == "__main__":
    print("JewelryBox.AI CLI Test (type 'exit')")
    history = []
    while True:
        try:
            text = input("You: ").strip()
            if text.lower() in ("exit", "quit"): sys.exit(0)
            res = chain.invoke({"user_input": text, "history": history})
            reply = res.content.strip()
            print("JewelryBox.AI:", reply)
            memory.add_user_message(text)
            memory.add_ai_message(reply)
            history = memory.messages
        except KeyboardInterrupt:
            sys.exit(0)
        except Exception as e:
            print("Error:", e)