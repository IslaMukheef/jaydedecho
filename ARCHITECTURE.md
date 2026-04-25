# JaydeEcho Architecture

## System Overview

```
User (Voice Input)
    ↓
[Trigger: Keypress / Button]
    ↓
Camera Frame Capture (OpenCV)
    ↓
Gemini Vision API (base64 image)
    ↓
Vision Response (text description)
    ↓
ElevenLabs TTS
    ↓
Speaker Output (Voice)
```

## Component Design

### 1. Camera Module (`src/camera.py`)
- Capture frames from Logitech Brio, webcam, or mobile
- Handle frame preprocessing (resize, quality checks)
- Support continuous capture for context

**Key Methods:**
- `initialize_camera()` - Setup camera device
- `capture_frame()` - Grab current frame as base64 or raw
- `get_frames_buffer()` - Keep rolling window of recent frames

### 2. Vision Module (`src/vision.py`)
- Send frames to Gemini API with context-aware prompts
- Support different query types:
  - Scene description: *"What's in front of me?"*
  - Object location: *"Where's the door on my right?"*
  - On-arrival detection: *"Are there empty seats?"*

**Key Methods:**
- `describe_scene(frame, context)` - General scene understanding
- `locate_object(frame, target, context)` - Find specific item
- `detect_seats(frame)` - Bus/venue seating detection
- `get_guidance(frame, query)` - Conversational query response

**Prompt Template (Gemini):**
```
You are an assistant for a visually impaired person. 
In this image, find [OBJECT] and tell me exactly where it is 
relative to the person holding the camera. If you do not see the 
object, suggest where to look next. Keep your answer under two 
sentences and make it conversational.
```

### 3. Speech Module (`src/speech.py`)
- Convert Gemini responses to natural speech via ElevenLabs
- Support emotional tone (urgent, calm, informative)
- Optional: Spatial audio cues (left/right emphasis)

**Key Methods:**
- `synthesize_speech(text, tone="neutral")` - Generate audio
- `play_audio(audio_data)` - Play via system speakers
- `speak_async(text)` - Non-blocking speech

### 4. Router Module (`src/router.py`)
- Route planning and step-by-step guidance
- Integration with maps API (Google Maps, OpenStreetMap)
- Contextual instructions based on current location

**Key Methods:**
- `plan_route(destination)` - Get route from current location
- `get_next_step()` - Current instruction
- `update_location(gps_data)` - Update position
- `announce_arrival()` - Notify when destination reached

### 5. Game Mode (`src/game_mode.py`)
- Interactive games (e.g., "floor is lava")
- Encourages engagement and exploration
- Voice-driven gameplay

**Key Methods:**
- `start_game(game_type)` - Initialize game
- `process_move(direction, distance)` - Handle user movement
- `check_hazard(frame)` - Detect hazards in real-time

### 6. Config Module (`src/config.py`)
- Load API keys and settings from `.env`
- Provide configuration interface
- Validate required credentials

## Interaction Flow

### Example: Navigation Scene

```
1. User: "I want to go to Oakville Place"
   → Router finds route and announces it

2. User: "Read me the first step"
   → Router: "Turn right onto Main Street"

3. User: "What's in front of me?"
   → Camera captures frame
   → Gemini describes: "You're approaching a traffic light intersection"
   → ElevenLabs speaks response

4. User: "Is the walk signal showing?"
   → Vision checks for walk signal in frame
   → Responds: "Yes, the walk signal is active"

5. User arrives at destination
   → GPS triggers arrival mode
   → Camera checks for empty seats
   → Guides user: "There's an empty seat on your left, row three"
```

### Example: Game Mode (Floor is Lava)

```
1. User: "Play floor is lava"
   → GameMode initializes hazard detection

2. Camera continuously monitors for floor/ground
   → "Move right, there's lava ahead!"
   → "Jump! Lava coming from the left!"

3. Score based on successful navigation
```

## Error Handling & Fallbacks

### No Internet Connection
- Use locally-cached routes (pre-downloaded maps)
- Voice output from local TTS fallback (if available)
- Log actions for upload when connection restored

### API Rate Limits
- Queue requests with exponential backoff
- Cache recent vision responses (same frame = no new API call)

### Camera Failure
- Alert user: "Camera not found, attempting fallback device"
- Try alternate camera sources (mobile, USB backup)

### Poor Image Quality
- Retry capture with brightness/focus adjustment
- Notify: "Image too dark, moving to a brighter area would help"

## Future Enhancements (Post-MVP)

### On-Device Vision (Gemma 4 + Ollama)
- Run vision locally for privacy
- Fallback to Gemini for complex queries
- Hybrid approach: quick local checks, deep reasoning on cloud

### GPS Integration
- Real-time location tracking
- Context-aware prompts ("You're near a coffee shop")
- Automatic route recalculation

### Multi-Modal Input
- Gesture recognition (phone accelerometer)
- Touch input for advanced options
- Button remapping for different devices

### Audio Spatialization
- Spatial audio cues (left/right/center speaker placement)
- 3D sound for immersive navigation
- Confidence levels in voice tone
