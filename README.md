# EchoFind — Vision Game

A real-time camera game for visually impaired users. 
AI analyses your live camera feed every 1.5 seconds and tells you:
- What's in front of you
- Where obstacles are
- When a person is dangerously close (game over)
- When you've found your target (win!)

## Files

```
vision-game/
├── server.py     ← Python backend (Flask + Ollama)
├── index.html    ← Browser frontend (open this in Chrome/Firefox)
├── setup.sh      ← One-shot installer
└── README.md
```

## Quick Start

### Step 1 — Install everything (once)
```bash
chmod +x setup.sh
./setup.sh
```

### Step 2 — Start Ollama (Terminal 1)
```bash
ollama serve
```

### Step 3 — Start the backend (Terminal 2)
```bash
python3 server.py
```
Server runs on **http://localhost:5050**

### Step 4 — Open the game
```bash
# Chrome/Chromium (recommended for camera access):
google-chrome index.html
# or
xdg-open index.html
```

---

## Changing the Vision Model

Edit `server.py` line:
```python
VISION_MODEL = "llava"   # Change to: moondream, llava-phi3, bakllava
```
Then pull the model:
```bash
ollama pull moondream   # fastest
ollama pull llava       # best accuracy
ollama pull llava-phi3  # balanced
```

## Game Rules

| Event | Result |
|---|---|
| Target found with ≥70% confidence | **WIN** 🎯 |
| Person detected very close | **LOSE** 🚨 |
| Stop button | Game ends |

## Troubleshooting

| Problem | Fix |
|---|---|
| "Cannot connect to Ollama" | Run `ollama serve` in a terminal |
| Camera not working | Use Chrome; allow camera in browser permissions |
| Slow analysis | Switch to `moondream` model (faster) |
| Server not reachable | Check firewall; make sure `python3 server.py` is running |
