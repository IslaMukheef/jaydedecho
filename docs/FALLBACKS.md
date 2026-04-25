# Fallback & Degraded Mode Strategies

## Network Connectivity

### No Internet Connection
**Vision Module:**
- Pre-cached responses for common queries
- Fallback to generic descriptions
- Example: "Camera working but cannot analyze. Internet required."

**Speech Module:**
- Local TTS fallback (if `pyttsx3` available)
- Use system `espeak` on Linux
- Voice quality will be lower but functional

**Navigation:**
- Use offline maps (download area beforehand)
- Provide last known route if planning fails
- Cache recent routes for re-announcement

**Implementation:**
```python
def describe_scene_offline(frame):
    """Fallback when API unavailable"""
    # Check if similar frame in cache
    cached_description = check_frame_cache(frame)
    if cached_description:
        return cached_description
    
    # Generic fallback
    return "Image captured but cannot be analyzed offline. Connect to internet for vision features."
```

### Intermittent Connection
- Queue API requests with exponential backoff
- Inform user: "Will analyze when connection available"
- Play cached responses while waiting

---

## API Failures

### Gemini API Down
```python
# Fallback chain
1. Check response cache (same image/prompt = cached result)
2. Use backup model (if available)
3. Provide generic description: "Analyzing image structure..."
4. Suggest: "Try again in a moment"
```

### ElevenLabs TTS Unavailable
```python
# Fallback: System TTS
import pyttsx3

def speak_offline(text):
    engine = pyttsx3.init()
    engine.say(text)
    engine.runAndWait()
    
# Voice quality: lower but functional
```

### OpenRouteService Down
```python
# Fallback: Mock routes
def get_route_offline(destination):
    return "Route planning unavailable. Network issue. Try: main street north, then turn right."
```

---

## Hardware Failures

### Camera Not Found
**Detection:**
```python
if cap is None or not cap.isOpened():
    logger.error("Camera initialization failed")
```

**Fallback:**
1. List available cameras
2. Try alternate device IDs (1, 2, etc.)
3. Check USB permissions
4. Suggest: "Is camera plugged in? Check USB cable."

**Escalation:**
```
User: "What's in front of me?"
AI: "Camera not found. Trying alternate device... Still looking..."
AI: "Camera unavailable. Check that it's plugged in and try again."
```

### Microphone Unavailable (Future Voice Input)
- Fall back to keyboard input
- Prompt: "Microphone unavailable. Type your question:"

### Speaker Failure
- Log warning but continue operation
- Output text representation
- Suggest: "Check audio devices in system settings"

---

## Performance Degradation

### Slow Network (<1 Mbps)
- Reduce image resolution before sending to API
- Use aggressive compression: `quality=60` instead of `quality=90`
- Warn user: "Network slow. Response may take longer."

**Implementation:**
```python
def encode_frame_compressed(frame, quality=70):
    """Compress before sending over slow network"""
    _, buffer = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, quality])
    return base64.b64encode(buffer).decode()
```

### High Latency (>5 sec)
- Provide progress updates every second
- "Still analyzing...", "Almost done..."
- Allow user to cancel if too slow

### API Rate Limiting
```python
from time import sleep
import random

def api_call_with_backoff(func, max_retries=3):
    for attempt in range(max_retries):
        try:
            return func()
        except RateLimitError:
            wait_time = (2 ** attempt) + random.uniform(0, 1)
            logger.warning(f"Rate limited. Waiting {wait_time}s...")
            sleep(wait_time)
    
    raise Exception("API rate limit exceeded")
```

---

## Future: On-Device Fallback (Gemma 4 + Ollama)

### Hybrid Strategy
**For quick, common queries:**
```python
if query in QUICK_QUERIES:
    # Use local Gemma 4
    response = ollama_model.generate(query)
else:
    # Use cloud Gemini for complex reasoning
    response = gemini_api.generate(query)
```

### Installation
```bash
# Download Gemma 4
ollama pull gemma2:2b  # ~2GB, fast on most machines

# Or locally compile
# See: https://github.com/ollama/ollama
```

### When to Use Local
- Offline mode / no internet
- Privacy-sensitive queries
- Fast response needed (<500ms)
- Known to work well locally

### When to Use Cloud
- Complex spatial reasoning
- Unclear input
- High accuracy needed
- User preference

---

## Data Recovery & Logging

### Session Logging
```python
# Log every action for offline sync
LOG_DIR = "~/.jaydeecho/logs"

logger.info("Route request failed. Queued for retry.")
# Action saved → Retry when connection returns
```

### Cache Strategy
```python
# Frame cache: 10 most recent
FRAME_CACHE_SIZE = 10

# Response cache: 100 recent responses
RESPONSE_CACHE = {}

# Shared cache file
CACHE_DB = "~/.jaydeecho/cache.json"
```

### Clean Shutdown
- Save current game state
- Log last route position
- Graceful cleanup on error
```python
def shutdown():
    save_cache()
    close_camera()
    log_session_end()
```

---

## User Communication

### Error Messages (Voice-Friendly)
```
BAD: "Cannot execute due to network timeout exception"
GOOD: "Network is slow. Retrying..."

BAD: "HTTP 503 Service Unavailable"
GOOD: "Analysis service temporarily down. Try again soon."

BAD: "CUDA out of memory"
GOOD: "Processing too much data. Simplifying image quality."
```

### Transparent Operation
- Always explain delays
- "Sending to Google Gemini..."
- "Waiting for response..."
- "Processing audio..."

### Recovery Guidance
```
Problem: API key invalid
Solution: "Check your Gemini API key in the .env file"

Problem: Camera permission denied
Solution: "Allow camera access in system settings"

Problem: No route found
Solution: "Is the destination name correct? Try 'Queen and Main'"
```

---

## Testing Fallbacks

### Simulate Network Failure
```bash
# Linux: block internet
sudo iptables -A OUTPUT -j DROP
# ... test offline mode ...
sudo iptables -D OUTPUT -j DROP
```

### Simulate API Failures
```python
# Mock failing API
class MockGeminiFailure:
    def generate_content(self, prompt):
        raise Exception("API Error: Service unavailable")

# Test fallback response
```

### Simulate Hardware Failure
```python
# Set camera to None
camera.cap = None

# Test graceful degradation
frame = camera.capture_frame()  # Should return None
# System should fall back without crashing
```
