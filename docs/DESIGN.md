# UX Design Notes - JaydeEcho

## Voice-First Interaction Principles

### 1. **Always Speak First**
- Every action should result in audio feedback
- No silent operations—user must hear confirmation
- Example: "Capturing image... processing..." (while working)

### 2. **Short & Clear Responses**
- Gemini responses are limited to 2-3 sentences max
- Avoid technical jargon
- Use spatial language: "to your left", "3 meters ahead", "ground level"

### 3. **Spatial Awareness**
- Always include left/right/center/distance in descriptions
- Use cardinal directions when possible
- Example: "Door is 2 meters to your right, on the north wall"

### 4. **Confirmation Feedback**
- Every major action needs vocal confirmation
- "Route planned", "Capturing image", "Playing game"
- Helps prevent accidental interactions

---

## Conversation Examples

### Scene Understanding
```
User: "What's in front of me?"
AI: "You're in a corridor. There's a door 5 meters ahead on your left, 
    and a staircase on your right."
```

### Object Search
```
User: "Where's the bathroom?"
AI: "I don't see a bathroom sign in view. Try moving right 
    toward the hallway for a better look."
```

### Navigation
```
User: "How do I get to Oakville Place?"
AI: "Route planned: about 2 km, 25 minutes walking. 
    First: Head north on Main Street for 150 meters."
```

### Ambiguity Handling
```
User: "Is that safe?"
AI: [captures image] "Yes, the path is clear. No obstacles detected."
```

---

## Emotional Tone Strategy

### Voice Modulation
- **Urgent**: Warnings (oncoming vehicle, hazard)
  - Faster speech rate, slightly higher pitch
  - Example: "LAVA ON YOUR LEFT! JUMP NOW!"

- **Calm**: Normal navigation
  - Standard speed and tone
  - Example: "Continue straight ahead. No obstacles."

- **Encouraging**: Game mode
  - Enthusiastic tone, supportive phrasing
  - Example: "Great move! You cleared that section! Score: 250"

### ElevenLabs Settings for Tone
```python
# Neutral (default)
stability = 0.5, similarity = 0.75

# More expressive/emotional
stability = 0.3, similarity = 0.85

# Calmer/steadier
stability = 0.7, similarity = 0.70
```

---

## Accessibility Considerations

### No Visual Feedback Needed
- ✅ Pure audio interaction
- ✅ Voice prompts instead of on-screen buttons
- ✅ No dependency on screen brightness/clarity

### Input Modalities
- **Primary**: Voice input (future enhancement)
- **Current**: Keyboard/button press (simple, reliable)
- **Future**: Gesture recognition (accelerometer)

### Response Latency
- **Target**: <2 seconds max for vision queries
  - User shouldn't have to wait in uncertainty
- **Fallback**: Quick "processing..." message if delayed

### Error Messages
- **Clear & actionable**: "Camera not found. Checking USB port..."
- **Avoid**: "ERROR 404" or technical jargon
- **Helpful**: Suggest next steps

---

## Game Mode UX

### Floor is Lava Example
```
User: "Play floor is lava"
AI: "Welcome! Avoid the lava. I'll alert you to hazards.
    You're starting in a safe zone. Move forward!"

[5 seconds pass]
AI: "Careful! Lava approaching from your right. Step left or jump!"

[User moves left]
AI: "Good dodge! +50 points. Total: 150."

[Game ends]
AI: "Game over! Final score: 1250. Well played!"
```

### Score Announcement Frequency
- Announce after major milestones
- Don't overwhelm with constant updates
- Example: Every 500 points or hazard dodge

---

## Mobile App Considerations (Future)

### Button Layout
- **Large touch targets**: Minimum 44x44 pixels
- **Haptic feedback**: Vibration on button press
- **Audio cues**: Different sounds for different buttons

### Screen Adaptation
- Low contrast mode option
- High contrast mode option
- Text size adjustable (even though audio-first)

---

## Privacy & Safety

### Data Handling
- ✅ All frames processed locally if possible
- ⚠️ Frames sent to Gemini API if cloud processing needed
- ⚠️ No frame storage on device
- ⚠️ No data sent to ElevenLabs beyond text

### User Consent
- Clearly state: "Sending image to Google Gemini for analysis"
- Allow opt-out for privacy-sensitive areas
- Option for on-device processing (future)

### Safety Guardrails
- Don't describe dangerous situations in alarming ways
- Always provide actionable guidance
- Avoid false confidence ("Definitely safe")
- Say "I'm not confident" when uncertain
