# API Usage Guide

## Google Gemini Vision API

### Authentication
```python
import google.generativeai as genai

genai.configure(api_key="your-api-key")
model = genai.GenerativeModel("gemini-1.5-flash")
```

### Image Input (Base64)
```python
import base64

# Read image file
with open("image.jpg", "rb") as f:
    image_data = base64.standard_b64encode(f.read()).decode("utf-8")

# Send to Gemini
response = model.generate_content([
    "Describe this image",
    {
        "mime_type": "image/jpeg",
        "data": image_data,
    }
])
```

### Vision Prompts
```python
# Scene description
prompt = """You are an assistant for a visually impaired person.
Describe what you see in a natural way. Focus on spatial awareness.
Keep your response under 3 sentences."""

# Object location
prompt = """Find the [OBJECT] and tell me where it is relative to 
the person holding the camera. If not found, suggest where to look."""

# Response is in response.text
```

## ElevenLabs TTS API

### Authentication
```python
from elevenlabs import set_api_key, generate, stream

set_api_key("your-api-key")
```

### Generate Speech
```python
audio = generate(
    text="Hello, this is a test",
    voice="21m00Tcm4TlvDq8ikWAM",  # Voice ID
    model="eleven_monolingual_v1"
)

# Stream directly to speakers
stream(audio)
```

### Voice Settings
- `voice`: Voice ID (e.g., "21m00Tcm4TlvDq8ikWAM")
- `model`: "eleven_monolingual_v1" or "eleven_multilingual_v1"
- `stream`: Return audio stream (True) or bytes (False)

### Common Voice IDs
- **Rachel**: 21m00Tcm4TlvDq8ikWAM
- **Bella**: EXAVITQu4vr4xnSDxMaL
- **Antoni**: ErXwobaYp0DKuxZXhKC5
- **Sam**: yoZ06aMxZJJ28mfd3POQ

## OpenRouteService (Maps & Routing)

### Authentication
```python
import openrouteservice

client = openrouteservice.Client(key="your-api-key")
```

### Get Route
```python
coords = [
    [8.681495, 49.41461],  # Start coordinates [lon, lat]
    [8.687872, 49.420318]  # End coordinates [lon, lat]
]

route = client.directions(
    coordinates=coords,
    profile='foot-walking',
    format='geojson'
)

# Access route segments
for segment in route['features'][0]['properties']['segments']:
    print(segment['duration'])  # Time in seconds
    print(segment['distance'])  # Distance in meters
```

## Camera / OpenCV

### Capture from Webcam
```python
import cv2
import base64

cap = cv2.VideoCapture(0)  # 0 = default camera

ret, frame = cap.read()
if ret:
    # Convert to base64
    _, buffer = cv2.imencode('.jpg', frame)
    encoded = base64.b64encode(buffer).decode('utf-8')
    
    # Use encoded data with Gemini
    response = model.generate_content([
        "Describe this image",
        {"mime_type": "image/jpeg", "data": encoded}
    ])

cap.release()
```

### Camera Settings
```python
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
cap.set(cv2.CAP_PROP_FPS, 30)
cap.set(cv2.CAP_PROP_AUTOFOCUS, 1)
```

## Rate Limits & Pricing

### Gemini API
- **Rate Limit**: Requests per minute varies by tier
- **Pricing**: Free tier available, pay-as-you-go after
- **Recommended**: Cache repeated prompts to reduce costs

### ElevenLabs
- **Rate Limit**: Depends on subscription
- **Pricing**: Character-based (per 1000 characters)
- **Tip**: Batch text generation when possible

### OpenRouteService
- **Rate Limit**: Requests per minute varies by plan
- **Pricing**: Free tier (2500 requests/month), paid tiers above
