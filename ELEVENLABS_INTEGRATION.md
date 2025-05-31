# ElevenLabs Voice Integration

This document explains the ElevenLabs Text-to-Speech integration that replaces the OpenAI Realtime voice functionality in JewelryBox AI.

## Overview

We've replaced the complex OpenAI Realtime WebRTC implementation with a simpler, more reliable approach using:

- **ElevenLabs TTS API** for high-quality voice synthesis
- **Web Speech API** for speech recognition (voice input)
- **HTTP-based audio streaming** instead of WebRTC

## Architecture

### Voice Input Flow
1. User clicks microphone button
2. Browser's Web Speech API captures speech
3. Speech is transcribed to text in real-time
4. Text is sent through the normal chat pipeline
5. AI processes the request using existing prompt chain logic

### Voice Output Flow
1. AI generates text response (same as text chat)
2. Text response is sent to ElevenLabs TTS API
3. ElevenLabs returns MP3 audio
4. Audio is played in the browser

## Benefits of This Approach

### ✅ Advantages
- **Simplified Architecture**: No complex WebRTC or session management
- **Better Audio Quality**: ElevenLabs voices are more natural than OpenAI Realtime
- **Maintained Logic**: All existing agent prompt chains work identically
- **Browser Compatibility**: Works in all modern browsers that support Web Speech API
- **Cost Effective**: Pay-per-use pricing without session overhead
- **Customizable Voices**: Easy to change voices via environment variables

### ⚠️ Considerations
- **Internet Required**: Both speech recognition and TTS require internet connection
- **Browser Support**: Web Speech API works best in Chrome/Edge
- **Latency**: Slightly higher latency than real-time streaming (but still very responsive)

## Environment Variables

Add these to your `.env` file:

```env
# OpenAI API Key for the chat functionality
OPENAI_API_KEY=your_openai_api_key_here

# ElevenLabs API Key for voice synthesis
ELEVENLABS_API_KEY=your_elevenlabs_api_key_here

# ElevenLabs Voice ID (optional, defaults to Rachel)
ELEVENLABS_VOICE_ID=JBFqnCBsd6RMkjVDRZzb

# CORS settings
ALLOWED_ORIGINS=*
```

## Voice Selection

The system uses the voice ID from `ELEVENLABS_VOICE_ID` environment variable. Popular voice IDs:

- **Rachel** (Default): `JBFqnCBsd6RMkjVDRZzb`
- **Adam**: `pNInz6obpgDQGcFmaJgB` 
- **Antoni**: `ErXwobaYiN019PkySvjV`
- **Arnold**: `VR6AewLTigWG4xSOukaG`
- **Bella**: `EXAVITQu4vr4xnSDxMaL`
- **Domi**: `AZnzlk1XvdvUeBnXmlld`
- **Elli**: `MF3mGyEYCl7XYWbV9V6O`
- **Josh**: `TxGEqnHWrfWFTfGW9XjX`
- **Sam**: `yoZ06aMxZJJ28mfd3POQ`

## API Endpoints

### POST /voice/tts
Converts text to speech using ElevenLabs.

**Request:**
```json
{
  "text": "Hello, welcome to Diamond Family Jewelers!"
}
```

**Response:**
- Content-Type: `audio/mpeg`
- Body: MP3 audio data

## Frontend Implementation

The voice widget supports two modes:

### Text Mode (💬)
- Traditional text input/output
- Keyboard interaction
- Copy/paste support

### Voice Mode (🎤)
- Click microphone to start speech recognition
- Voice responses automatically play as audio
- Visual feedback for listening/processing states

## Browser Support

### Recommended Browsers
- **Chrome**: Full support for Web Speech API
- **Edge**: Full support for Web Speech API
- **Firefox**: Limited speech recognition support
- **Safari**: Basic support, may have limitations

### Fallback Behavior
If speech recognition is not supported, the system:
1. Shows a warning message
2. Automatically switches back to text mode
3. Maintains full functionality via text input

## Usage Instructions

1. **Open the voice widget** at `/voice`
2. **Choose mode** using the 💬/🎤 toggle in the header
3. **For voice mode:**
   - Click the microphone button to start listening
   - Speak your question clearly
   - Wait for the AI response (both text and audio)
   - Click microphone again for follow-up questions

## Troubleshooting

### Common Issues

**"Voice recognition not supported"**
- Use Chrome or Edge browser
- Ensure you're on HTTPS (required for speech recognition)
- Check browser permissions for microphone access

**"Failed to generate speech"**
- Verify `ELEVENLABS_API_KEY` is set correctly
- Check your ElevenLabs account has sufficient credits
- Ensure `ELEVENLABS_VOICE_ID` is valid

**Audio doesn't play**
- Check browser audio permissions
- Verify speakers/headphones are working
- Try refreshing the page

### Debugging

Enable debug mode by opening browser console and checking for:
- Speech recognition events
- TTS API responses
- Audio playback errors

## Future Enhancements

This implementation provides a foundation for:

- **Voice Selection Menu**: Choose from multiple ElevenLabs voices
- **Voice Cloning**: Custom voices for brand personality
- **Multi-language Support**: Support for different languages
- **Streaming TTS**: Real-time audio generation for faster responses
- **Voice Settings**: Adjust speed, tone, and other voice parameters

## Technical Details

### Dependencies
- `elevenlabs>=2.1.0`: Official ElevenLabs Python SDK
- Web Speech API: Browser-native speech recognition
- HTML5 Audio: For audio playback

### Security
- API keys stored in environment variables
- Audio data not persisted on server
- HTTPS required for microphone access

This integration maintains all existing functionality while providing a superior voice experience through ElevenLabs' industry-leading TTS technology. 