# Quick Start Guide - JaydeEcho

Get JaydeEcho running in 5 minutes.

## Prerequisites

- Python 3.9 or higher
- A webcam or Logitech Brio
- API keys from:
  - Google Gemini (free tier available)
  - ElevenLabs (free tier available)

## 1. Clone & Setup

```bash
cd /home/isla/Desktop/jaydedecho
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

## 2. Install Dependencies

```bash
pip install -r requirements.txt
```

## 3. Get API Keys

### Google Gemini API
1. Go to https://ai.google.dev
2. Click "Get API Key"
3. Create new API key for "JaydeEcho"
4. Copy the key

### ElevenLabs TTS
1. Go to https://elevenlabs.io
2. Sign up (free tier available)
3. Go to Account → API Key
4. Copy the key

## 4. Configure Environment

```bash
cp .env.example .env
```

Edit `.env` and add your API keys:
```
GEMINI_API_KEY=your_key_here
ELEVENLABS_API_KEY=your_key_here
```

## 5. Run the App

```bash
python src/main.py
```

You should see:
```
[INFO] JaydeEcho initialized successfully
[INFO] JaydeEcho started. Listening for commands...

[Press SPACE + letter for command, or enter command text]
  d = describe scene
  n = navigate (enter destination)
  g = game mode
  q = quit

>
```

## 6. Try Commands

### Describe your surroundings
```
> d
[Capturing scene...]
[Camera captures frame]
[AI analyzes image]
"You're in a modern office. There's a desk on your left with a monitor,
and a window showing trees outside to your right."
```

### Navigate somewhere
```
> n
Destination: Oakville Place
"Route planned: about 2 km, 25 minutes walking. 
First: Head north on Main Street for 150 meters."
```

### Play a game
```
> g
Game (floor_is_lava): 
"Welcome to Floor is Lava! Move around and avoid the ground.
I'll alert you when lava approaches. Press spacebar to jump. Good luck!"
```

### Quit
```
> q
[INFO] Shutting down...
[INFO] JaydeEcho shutdown complete
```

---

## Troubleshooting

### "Camera not found"
- Check that your webcam is plugged in
- Try: `ls /dev/video*` (Linux) or Device Manager (Windows)
- Test with: `python -c "import cv2; cv2.VideoCapture(0).isOpened()"`

### "GEMINI_API_KEY not set"
- Verify `.env` file exists and is in project root
- Check key is correct (no extra spaces or quotes)
- Test: `python -c "import os; from dotenv import load_dotenv; load_dotenv(); print(os.getenv('GEMINI_API_KEY'))"`

### "No module named 'cv2'"
- Reinstall OpenCV: `pip install --upgrade opencv-python`

### Audio not working
- Verify audio device: `sudo aplay -l` (Linux)
- Check volume isn't muted
- Test: `python -c "import pyaudio; print(pyaudio.PyAudio().get_device_count())"`

### Slow responses
- Check internet connection
- Use `--debug` flag for detailed logging
- Smaller image = faster processing (edit `camera_width`, `camera_height` in `.env`)

---

## Next Steps

- **Add voice input**: Implement microphone listening (see `docs/DESIGN.md`)
- **Use offline vision**: Set up Ollama with Gemma 4 for on-device processing
- **Customize voices**: Try different ElevenLabs voice IDs
- **Expand games**: Add more game modes (see `src/game_mode.py`)
- **Mobile app**: Serve via Flask web app for mobile camera

---

## File Structure Reference

```
jaydedecho/
├── src/
│   ├── main.py           # Entry point - run this
│   ├── config.py         # Configuration loading
│   ├── camera.py         # Camera capture
│   ├── vision.py         # Gemini API interface
│   ├── speech.py         # ElevenLabs TTS interface
│   ├── router.py         # Navigation & routing
│   └── game_mode.py      # Interactive games
├── docs/
│   ├── API_USAGE.md      # API integration examples
│   ├── DESIGN.md         # UX and voice design
│   └── FALLBACKS.md      # Error handling & offline mode
├── .env.example          # Environment template (copy to .env)
├── requirements.txt      # Python dependencies
├── README.md             # Project overview
└── ARCHITECTURE.md       # Technical design
```

---

## Support

For issues:
1. Check `ARCHITECTURE.md` for system design
2. Read `docs/FALLBACKS.md` for troubleshooting
3. Enable debug mode: `DEBUG=true` in `.env`
4. Check logs in `.claude/logs/` (when created)

Happy navigating! 🎤
