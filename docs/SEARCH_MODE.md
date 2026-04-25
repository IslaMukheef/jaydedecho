# Search Mode - Find Objects Feature

## Overview

Users can now **search for specific objects** with AI assistance. The system intelligently handles found/not-found scenarios and provides a smooth workflow.

## How It Works

### Step 1: User Enters Search Term
User types what they're looking for:
- "chair"
- "door"
- "window"
- "person"
- "red bag"

### Step 2: AI Analyzes Image
System captures an image and asks: **"Where is the [object]?"**

### Step 3: Smart Response

#### ✅ Object Found
```
✅ Found it! The chair is in the left-center area of the room, 
   approximately 3 meters away. It appears to be a wooden office chair.
```
**What happens next:**
- Image displays with location details
- AI speaks the response
- User can search for something else or exit

#### ❌ Object Not Found
```
❌ No chair found. But I see: A desk with a computer, white walls, 
   a window with natural light coming through, and hardwood flooring.

Want to search again or describe the full scene?
```
**What happens next:**
- Image displays
- User can:
  - 🔍 **Try Again** - Take a new picture with different angle
  - ✓ **Done** - Exit search mode

### Step 4: Continuous Search
Users can keep searching with new pictures until they find what they need.

---

## User Journey Example

```
User: Looking for a red backpack

1. Enters "red backpack" in search field
2. AI takes picture and analyzes it
3. AI: "I don't see a red backpack, but I see: 
        A desk, office chair, and shelves with various items"
4. User clicks "Try Again (New Picture)"
5. AI takes another picture from different angle
6. AI: "Found it! The red backpack is on the top shelf 
        to your right, among other items"
7. User: "Great, found it!"
8. User clicks "Done" to exit search
```

---

## Features

### 🎯 Smart Object Detection
- Uses LLaVA vision model to locate objects
- Provides spatial descriptions (left/right/center, near/far)
- Estimates distances when visible

### 💬 Conversational Fallback
- If object not found, offers scene description
- Helps user understand environment
- Encourages trying again with new angles

### 🔄 Iterative Search
- Keep searching until object is found
- Each search uses a fresh camera frame
- No limit on search attempts

### 🖼️ Visual Feedback
- Shows captured image for each search
- Color-coded responses (green = found, red = not found)
- Clear action buttons for next step

### 🔊 Full Audio Support
- All responses spoken aloud
- Search prompts announced
- No need to read screen

---

## Technical Details

### API Endpoints

**Start Search**
```
POST /api/search
{
  "query": "what to find"
}

Response:
{
  "response": "description",
  "image": "base64 image",
  "found": true/false,
  "query": "what to find"
}
```

**Continue Search**
```
POST /api/search/continue
{
  "query": "what to find"
}

Response:
{
  "response": "updated description",
  "image": "base64 image",
  "found": true/false
}
```

### Detection Logic

Object is considered "found" if response does NOT contain:
- "i don't see"
- "i cannot see"
- "not visible"
- "cannot find"
- "don't see"
- "no sign of"

---

## Tips for Users

### Best Results
✅ Be specific: "red leather chair" instead of "thing"
✅ Try from different angles if not found
✅ Use common object names (chair, door, window)
✅ One object at a time

### What Works Well
- Common furniture (chair, table, desk)
- Doors, windows, appliances
- People, pets
- Specific colors (red bag, blue cup)
- Rooms (kitchen, bathroom, bedroom)

### Limitations
⚠️ May struggle with:
- Very small objects
- Objects partially hidden
- Objects that look similar to other things
- Very cluttered environments

---

## Example Search Scenarios

### Scenario 1: Finding a Door
```
User: "Where is the door?"
AI: "The door is straight ahead, about 5 meters away. 
     It appears to be a white wooden door on the far wall."
Result: ✅ FOUND
```

### Scenario 2: Object Not in View
```
User: "Where is my bag?"
AI: "I don't see your bag here. But I see: walls, some furniture, 
     and a window."
User: Clicks "Try Again"
AI: "Found it! Your bag is on the chair to your left."
Result: ✅ FOUND AFTER RETRY
```

### Scenario 3: Object Doesn't Exist
```
User: "Where is the spaceship?"
AI: "I don't see a spaceship. I see: a living room with furniture,
     TV, and decorations."
User: "Okay, search for the TV instead"
Result: ✅ FOUND (TV)
```

---

## Accessibility Features

- Voice input compatible (when integrated with speech recognition)
- All text spoken aloud automatically
- No visual information required
- Progressive disclosure (show image only when helpful)
- Clear audio cues for found/not-found

---

## Future Enhancements

🔮 Planned Features:
- Multi-object search ("find the red chair and the blue lamp")
- Search history ("remember where I found...")
- Search suggestions ("Did you mean...?")
- Confidence levels ("I'm 80% sure...")
- Voice-based search input
- Learning from user corrections
