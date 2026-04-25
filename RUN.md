# Running JaydeEcho

## Option 1: Web App (Recommended) 🌐

The web app works on phones, tablets, and computers.

### Start the server:

```bash
source venv/bin/activate
python3 app.py
```

You'll see:
```
==================================================
JaydeEcho Web App
==================================================
Vision Backend: ollama (or gemini)
Speech: Available ✓
Camera: Ready ✓
==================================================
Starting server on http://localhost:5000
Open http://localhost:5000 in your browser or phone
==================================================
```

### Access from:
- **Your computer**: http://localhost:5000
- **Your phone** (same network): http://192.168.x.x:5000 (replace with your computer's IP)

### Features in the web app:
✅ Navigate to addresses ("Oakville Place", "Downtown Toronto", etc.)
✅ Describe your surroundings
✅ Ask questions about what you see
✅ Play games (Floor is Lava, Obstacle Course, Sound Hunt)
✅ Everything is spoken aloud automatically

---

## Option 2: Command Line (Original) 💻

```bash
source venv/bin/activate
python3 src/main.py
```

Type commands:
- `d` = Describe scene
- `n` = Navigate to a place
- `g` = Play a game
- `q` = Quit

---

## Setup Checklist

### For Vision (choose one):

**Option A: Local Ollama (Free, Offline, Recommended)**
```bash
# Install Ollama from https://ollama.ai
# Then in a separate terminal:
ollama serve
ollama pull gemma2

# App will auto-detect Ollama running!
```

**Option B: Google Gemini (Cloud, needs API key)**
```bash
# Get a new key from https://ai.google.dev
# Add to .env:
echo "GEMINI_API_KEY=your_new_key" >> .env
```

### For Navigation:

The app uses **free address geocoding** (Nominatim/OpenStreetMap):
- No API key needed
- Works offline
- Finds real locations

You can optionally add OpenRouteService for detailed turn-by-turn, but it's not required.

### For Speech:

✅ Already working! Uses system voices (pyttsx3).
- Free
- Offline
- Works on all platforms

---

## Troubleshooting

### "Vision service unavailable"
Make sure either:
1. Ollama is running: `ollama serve` in another terminal
2. OR you have a valid GEMINI_API_KEY in `.env`

### "Could not find address"
- Try a different address format
- Try city/country: "Toronto, Ontario"
- Try known landmarks: "CN Tower, Toronto"

### "Camera not available"
- Web app works without camera too
- Click "Describe Scene" to see error

### "Address not found"
- Make sure you're connected to the internet (for geocoding)
- Try a major city first to test: "New York", "London", "Toronto"

---

## Examples

### Navigation
```
User: Where do I want to go?
Input: "Oakville Place"
→ "Route to Oakville Place: approximately 15 kilometers, about 25 minutes walking. 
   Start by heading towards your destination."
```

### Scene Description
```
User: Clicks "Describe Scene"
→ "You're in a modern office space. There's a desk on your left with a computer, 
   and large windows to your right showing trees outside."
```

### Questions
```
User: "Is there a clear path to my right?"
→ "Yes, I see a clear corridor to your right with no obstacles in the way."
```

### Games
```
User: Starts "Floor is Lava"
→ "Welcome! Move around and avoid the ground. I'll alert you when lava approaches."
→ User clicks directions
→ "Good move! You advanced safely. Score: +50"
```

---

## System Requirements

- Python 3.9+
- Camera (optional, web app works without it)
- Speakers (required for audio output)
- Internet (optional, Ollama works offline)

Supported on:
- ✅ Windows, macOS, Linux
- ✅ iOS Safari, Android Chrome
- ✅ Any browser that supports HTML5
