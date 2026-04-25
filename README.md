# JaydeEcho

A voice-first AI assistant for visually impaired users that helps them navigate and understand their surroundings using real-time computer vision and natural speech interaction.

## Core Features

### 1. Route Guidance
Navigate to destinations with step-by-step directions.
- User: *"I want to go to Oakville Place, how can I get there?"*
- Assistant: Provides turn-by-turn guidance

### 2. On-Arrival Assistance
Detects bus/environment and identifies empty seats, helping the user orient themselves at their destination.

### 3. Conversational AI
Natural two-way dialogue, not fixed commands.
- User: *"What's in front of me?"*
- Assistant: Describes the scene
- User: *"Is there a clear path to the door on my right?"*
- Assistant: Real-time guidance with spatial awareness

### 4. Game Mode
Interactive "floor is lava" style games to make the experience engaging.

### 5. Voice Output
- ElevenLabs API for natural, empathetic text-to-speech
- Emotional and spatial audio (urgent warnings, left/right directions)

## Tech Stack

### Ultra-Lean 2-Day Approach
- **Camera Capture**: Python + OpenCV (Logitech Brio or mobile web app)
- **Vision AI**: Google Gemini API (base64 image understanding)
- **Voice Output**: ElevenLabs API (natural speech synthesis)
- **Trigger**: Single keypress or button to capture → analyze → speak

### Future Roadmap
- On-device models using Gemma 4 via Ollama (privacy-first alternative to cloud APIs)

## Quick Start

### Prerequisites
- Python 3.9+
- Gemini API key (Google Cloud)
- ElevenLabs API key
- Camera device (Logitech Brio, webcam, or mobile)

### Setup

```bash
# Install dependencies
pip install -r requirements.txt

# Create environment config
cp .env.example .env
# Edit .env with your API keys
```

### Run

```bash
python src/main.py
```

## Project Structure

```
jaydedecho/
├── README.md                 # This file
├── ARCHITECTURE.md           # Technical design & flow
├── requirements.txt          # Python dependencies
├── .env.example              # Environment template
├── src/
│   ├── main.py              # Entry point
│   ├── camera.py            # Camera capture (OpenCV)
│   ├── vision.py            # Gemini vision API client
│   ├── speech.py            # ElevenLabs TTS client
│   ├── router.py            # Route guidance logic
│   ├── game_mode.py         # Game mode (floor is lava, etc)
│   └── config.py            # Configuration management
└── docs/
    ├── API_USAGE.md         # API call patterns
    ├── DESIGN.md            # UX design notes
    └── FALLBACKS.md         # Offline/degraded mode strategies
```

## Development Notes

- **Fallback Strategy**: If local models are unavailable, all vision processing uses Gemini API
- **Presentation**: Future versions can highlight on-device Gemma 4 via Ollama for privacy
- **Accessibility**: All interactions are audio-first (voice input/output)
