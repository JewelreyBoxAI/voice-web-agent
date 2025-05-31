# 🎤 Voice Features - OpenAI Realtime Integration

## Overview

The JewelryBox AI chatbot now includes **advanced voice capabilities** powered by OpenAI's Realtime API. This enables natural, low-latency voice conversations with the AI jewelry expert.

## Features

### 🎙️ **Speech-to-Speech Conversation**
- **Real-time audio processing** with WebRTC
- **Voice Activity Detection (VAD)** - automatically detects when you start/stop speaking
- **Natural conversation flow** - no need to press buttons to talk
- **High-quality audio** with `verse` voice model

### 💬 **Dual Mode Interface**
- **Text Mode**: Traditional text-based chat
- **Voice Mode**: Full voice conversation with visual feedback
- **Seamless switching** between modes
- **Live transcription** showing what you said

### 🔊 **Audio Features**
- **WebRTC-based audio** for low latency
- **Automatic audio playback** of AI responses
- **Real-time transcription** of user speech
- **Visual status indicators** (listening, processing, speaking)

## How to Use

### 1. **Access Voice Chat**
- Navigate to `/voice` (now the default)
- The original text-only chat is still available at `/widget`

### 2. **Enable Voice Mode**
- Click the **🎤 Voice** button in the mode toggle
- Grant microphone permissions when prompted
- Wait for "Voice Ready" status

### 3. **Start Talking**
- Click the microphone button in the header to activate
- Speak naturally - the AI will detect when you finish
- Listen to the AI's voice response
- See real-time transcripts of your speech

### 4. **Visual Feedback**
- **🎤 Gray**: Voice ready, click to activate
- **🎤 Red (pulsing)**: Currently listening
- **🎤 Orange (spinning)**: Connecting to voice service
- **Status text**: Shows current voice state

## Technical Implementation

### Backend Changes

#### New Endpoints
```python
POST /voice/session
# Creates ephemeral token for OpenAI Realtime API
# Returns session configuration and authentication

GET /voice
# Serves the voice-enabled widget interface
```

#### Voice Session Configuration
- **Model**: `gpt-4o-realtime-preview-2024-12-17`
- **Voice**: `verse` (warm, conversational tone)
- **Audio Format**: PCM16 for high quality
- **VAD Settings**: Optimized for jewelry consultation
- **Instructions**: Same expert jewelry knowledge as text chat

### Frontend Integration

#### WebRTC Connection
```javascript
// Automatic microphone access and audio output
const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
pc.addTrack(stream.getTracks()[0], stream);

// Real-time audio from AI
pc.ontrack = event => audioElement.srcObject = event.streams[0];
```

#### Event Handling
- `input_audio_buffer.speech_started` - User starts speaking
- `input_audio_buffer.speech_stopped` - User stops speaking
- `response.audio_transcript.delta` - Live transcription
- `response.audio.delta` - Streaming AI audio response
- `response.done` - Response complete

## Security & Privacy

### Ephemeral Tokens
- **Short-lived tokens** (1 minute expiration)
- **Server-side generation** keeps API keys secure
- **No persistent storage** of audio data

### Microphone Access
- **Permission-based** - users must grant access
- **Local processing** - audio streamed directly to OpenAI
- **No local recording** - audio not stored on device

## Voice Conversation Examples

### Jewelry Consultation
```
User: "I'm looking for an engagement ring"
AI: "Wonderful! I'd be happy to help you find the perfect engagement ring. 
     Let me ask a few questions to narrow down the best options..."
```

### Product Information
```
User: "Tell me about different diamond cuts"
AI: "Great question! The cut of a diamond significantly affects its brilliance. 
     The most popular cuts include round brilliant, princess, cushion..."
```

### Service Inquiries
```
User: "Do you resize rings?"
AI: "Yes, we absolutely offer ring resizing services! Our skilled jewelers 
     can resize most rings. The process typically takes..."
```

## Configuration Options

### Voice Settings (Backend)
```python
{
    "voice": "verse",                    # Warm, professional tone
    "turn_detection": {
        "type": "server_vad",           # Automatic speech detection
        "threshold": 0.5,               # Sensitivity level
        "silence_duration_ms": 500      # How long to wait after speech
    },
    "temperature": 0.8,                 # Natural conversational tone
    "max_response_output_tokens": 4096  # Comprehensive responses
}
```

### Audio Quality
- **Input Format**: PCM16 (16-bit, 24kHz)
- **Output Format**: PCM16 (16-bit, 24kHz)
- **Transcription**: Whisper-1 model
- **Latency**: ~300ms typical response time

## Fallback Behavior

### Error Handling
- **Connection failures**: Falls back to text mode
- **Microphone denied**: Shows helpful error message
- **API errors**: Graceful degradation to text chat
- **Browser compatibility**: Automatic feature detection

### Browser Support
- **Chrome/Edge**: Full support
- **Firefox**: Full support
- **Safari**: Full support (iOS 14.5+)
- **Mobile browsers**: Full support with device permissions

## Development Notes

### Local Testing
```bash
# Ensure OPENAI_API_KEY is set in .env
export OPENAI_API_KEY="your-key-here"

# Run the development server
uvicorn src.app:app --reload

# Access voice chat at http://localhost:8000/voice
```

### Production Deployment
- **HTTPS required** for microphone access in production
- **Render.com/Vercel**: Automatic HTTPS handling
- **Environment variables**: Ensure OPENAI_API_KEY is set
- **CORS settings**: Configure for your domain

## Future Enhancements

### Planned Features
- **Function calling** - Voice-triggered appointment booking
- **Multi-language support** - Spanish, French jewelry consultations
- **Voice interruption** - Allow users to interrupt AI responses
- **Custom wake words** - "Hey JewelryBox" activation
- **Sentiment analysis** - Adjust tone based on customer mood

### Advanced Integrations
- **Phone integration** - Twilio voice calls
- **Video calls** - Show jewelry images during voice chat
- **AR integration** - Voice-controlled jewelry try-on
- **CRM integration** - Voice notes automatically saved

## Troubleshooting

### Common Issues

**"Voice Error" Status**
- Check microphone permissions
- Verify OPENAI_API_KEY is valid
- Ensure HTTPS in production

**No Audio Output**
- Check device audio settings
- Verify browser audio permissions
- Try refreshing the page

**Connection Timeout**
- Check internet connection
- Verify OpenAI API status
- Try switching to text mode

**High Latency**
- Check network speed
- Consider server location
- Optimize VAD settings

---

**The voice-enabled JewelryBox AI provides a natural, conversational experience that mirrors talking to an expert jeweler in person, enhancing customer engagement and satisfaction.** 🎤💎 