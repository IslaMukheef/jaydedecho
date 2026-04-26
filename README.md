# JaydedEcho — Vision Guide Game

Named after Jayde (https://github.com/JaydedCompanion)
DevPost (https://devpost.com/software/jaydedecho)

A real-time browser vision game and accessibility experiment that guides a blind player using an "echo" voice assistant inspired by Jayde. It helps you find items, avoid people, and navigate — but beware: Jayde hates people, and seeing too many will end the game.

Inspiration

I was supposed to attend a hackathon with my friend Jayde. They didn't get in, so this was built as a playful tribute: the echo of Jayde guiding a player through social interactions and lost-item hunts. No AI replaces them — this is for fun and homage.

What it does

- The user names a target item to find.
- The browser streams camera frames to a Python backend.
- Backend queries an on‑device Ollama/LLaVA vision model to analyze each frame.
- The assistant reports: target presence, people detection (danger), scene description, and movement hints.
- Game rules: finding the target wins; seeing too many people (configurable) triggers loss.

How we built it

- Backend: Flask (server.py) that queries Ollama via HTTP
- Frontend: index.html for camera capture, encoding frames and playing TTS
- Models: Ollama-hosted vision models (llava, moondream, etc.)
- Optimizations: motion detection, reduced resolution, smart frame skipping, async speech

Key features & improvements

- Real-time object classification using local Ollama models
- Session-based consensus smoothing to reduce flicker/false positives
- Multiple difficulty rules to tune sensitivity and win/lose thresholds
- Latency optimizations (lower resolution, frame skipping, async audio)

Quick start

1) Install (one-time):

```bash
chmod +x setup.sh
./setup.sh
```

2) Start Ollama (Terminal 1):

```bash
ollama serve
```

3) Start the backend (Terminal 2):

```bash
python3 server.py
```

4) Open the game in Chrome/Chromium (for camera access):

```bash
xdg-open index.html
```

Configuration

- server.py environment variables:
  - OLLAMA_URL (default: http://localhost:11434/api/generate)
  - VISION_MODEL (default: llava)
  - HTTPS_PORT, CERT_FILE, KEY_FILE
- Change VISION_MODEL and pull the model with `ollama pull <model>` to try different tradeoffs.

Challenges we ran into

Streaming low-latency video and getting timely model responses was the hardest part. Solutions included lowering image quality, skipping redundant frames, and using confidence‑based consensus logic. Many hours of testing and tuning went into the final settings.

Accomplishments

- Implemented near real-time vision analysis with practical latency
- Built robust heuristics to avoid noisy detections and reduce false positives
- Made the game playable on modest hardware using local models

What we learned

Players rarely notice reduced image quality if it isn't mentioned — trading a bit of fidelity for speed works well.

What's next

- VR mode with occlusion so players can't see but are kept safe
- Collectible hearts to refill health and extend play
- Better model switching and on-device acceleration support

Files

```
├── server.py     ← Python backend (Flask + Ollama)
├── index.html    ← Browser frontend (camera, audio, UI)
├── setup.sh      ← One-shot installer
├── cert.pem/key.pem ← self-signed certs (auto-generated if missing)
└── README.md
```

License & credits

Named for Jayde — thanks to https://github.com/JaydedCompanion for inspiration.

If you'd like any wording changed or want additional badges/installation notes, say the word and adjustments will be made.
