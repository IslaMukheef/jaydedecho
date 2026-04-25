"""
JaydeEcho Web App - Flask-based UI for phone/browser access
"""

from flask import Flask, render_template, request, jsonify
import sys
from pathlib import Path
import threading
import json

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from config import Config
from camera import Camera
from vision import Vision
from speech import Speech
from router import Router
from game_mode import GameMode

app = Flask(__name__)

# Initialize components
config = Config()
camera = Camera(config)
vision = Vision(config)
speech = Speech(config)
router = Router(config)
game_mode = GameMode(config)

# Store session state
session_state = {
    "game_active": False,
    "current_game": None,
    "route_active": False,
    "current_route": None,
}


@app.route("/")
def index():
    """Serve main page"""
    return render_template("index.html")


@app.route("/api/status")
def status():
    """Get system status"""
    return jsonify({
        "vision_backend": vision.backend or "unavailable",
        "vision_model": vision.model or "none",
        "speech_available": speech.available,
        "camera_ready": camera.cap is not None and camera.cap.isOpened(),
        "current_camera": camera.current_device_id,
    })


@app.route("/api/cameras", methods=["GET"])
def list_cameras():
    """List all available camera devices"""
    try:
        cameras = camera.list_available_cameras()
        return jsonify({"cameras": cameras})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/camera/switch", methods=["POST"])
def switch_camera():
    """Switch to a different camera device"""
    try:
        data = request.json
        device_id = data.get("device_id", 0)

        success = camera.switch_camera(device_id)

        if success:
            message = f"Camera switched to device {device_id}"
            threading.Thread(target=speech.speak, args=(message,), daemon=True).start()
            return jsonify({"success": True, "message": message, "device": device_id})
        else:
            return jsonify({"success": False, "error": f"Failed to switch to camera {device_id}"}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/stream/frame", methods=["GET"])
def stream_frame():
    """Get current camera frame as JPEG"""
    try:
        frame = camera.capture_frame()
        if frame is None:
            return jsonify({"error": "Camera not available"}), 400

        import cv2
        _, buffer = cv2.imencode(".jpg", frame, [cv2.IMWRITE_JPEG_QUALITY, 80])
        import base64
        frame_b64 = base64.b64encode(buffer).decode("utf-8")

        return jsonify({
            "frame": f"data:image/jpeg;base64,{frame_b64}"
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/describe", methods=["POST"])
def describe_scene():
    """Describe current scene from camera"""
    try:
        frame = camera.capture_frame()
        if frame is None:
            return jsonify({"error": "Camera not available"}), 400

        # Convert frame to base64 for display
        import cv2
        _, buffer = cv2.imencode(".jpg", frame)
        import base64
        frame_b64 = base64.b64encode(buffer).decode("utf-8")

        response = vision.describe_scene(frame)

        # Speak the response
        threading.Thread(target=speech.speak, args=(response,), daemon=True).start()

        return jsonify({
            "response": response,
            "image": f"data:image/jpeg;base64,{frame_b64}"
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/navigate", methods=["POST"])
def navigate():
    """Plan route to destination"""
    try:
        data = request.json
        destination = data.get("destination", "").strip()

        if not destination:
            return jsonify({"error": "No destination provided"}), 400

        # Plan route
        route_response = router.plan_route(destination)

        # Speak the route
        threading.Thread(target=speech.speak, args=(route_response,), daemon=True).start()

        session_state["route_active"] = True
        session_state["current_route"] = destination

        return jsonify({"response": route_response})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/query", methods=["POST"])
def query_vision():
    """Ask a question about the scene"""
    try:
        data = request.json
        query = data.get("query", "").strip()

        if not query:
            return jsonify({"error": "No query provided"}), 400

        frame = camera.capture_frame()
        if frame is None:
            return jsonify({"error": "Camera not available"}), 400

        # Convert frame to base64 for display
        import cv2
        _, buffer = cv2.imencode(".jpg", frame)
        import base64
        frame_b64 = base64.b64encode(buffer).decode("utf-8")

        response = vision.get_guidance(frame, query)

        # Speak the response
        threading.Thread(target=speech.speak, args=(response,), daemon=True).start()

        return jsonify({
            "response": response,
            "image": f"data:image/jpeg;base64,{frame_b64}"
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/game/start", methods=["POST"])
def start_game():
    """Start a game"""
    try:
        data = request.json
        game_type = data.get("game", "floor_is_lava")

        game_msg = game_mode.start_game(game_type)

        # Speak game start message
        threading.Thread(target=speech.speak, args=(game_msg,), daemon=True).start()

        session_state["game_active"] = True
        session_state["current_game"] = game_type

        return jsonify({"response": game_msg})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/game/move", methods=["POST"])
def game_move():
    """Process game movement"""
    try:
        data = request.json
        direction = data.get("direction", "forward")
        distance = float(data.get("distance", 1.0))

        response = game_mode.process_move(direction, distance)

        # Speak response
        threading.Thread(target=speech.speak, args=(response,), daemon=True).start()

        return jsonify({"response": response})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/game/end", methods=["POST"])
def end_game():
    """End current game"""
    try:
        response = game_mode.end_game()

        # Speak end message
        threading.Thread(target=speech.speak, args=(response,), daemon=True).start()

        session_state["game_active"] = False
        session_state["current_game"] = None

        return jsonify({"response": response})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/search", methods=["POST"])
def search_object():
    """Search for a specific object in the scene"""
    try:
        data = request.json
        query = data.get("query", "").strip()

        if not query:
            return jsonify({"error": "What are you looking for?"}), 400

        frame = camera.capture_frame()
        if frame is None:
            return jsonify({"error": "Camera not available"}), 400

        # Convert frame to base64
        import cv2
        _, buffer = cv2.imencode(".jpg", frame)
        import base64
        frame_b64 = base64.b64encode(buffer).decode("utf-8")

        # Try to locate the object
        location_response = vision.locate_object(frame, query)

        # Check if object was found
        not_found_phrases = [
            "i don't see", "i cannot see", "not visible", "not in the image",
            "cannot find", "don't see", "no sign of", "not appear"
        ]
        object_found = not any(phrase in location_response.lower() for phrase in not_found_phrases)

        if object_found:
            response_text = f"✅ Found it! {location_response}"
            speech_text = response_text
        else:
            # Get scene description as fallback
            scene_desc = vision.describe_scene(frame)
            response_text = f"❌ No {query} found. But I see: {scene_desc}\n\nWant me to describe the full scene or search again?"
            speech_text = f"I don't see a {query}. {scene_desc}. Do you want me to search again or describe the full scene?"

        # Speak response
        threading.Thread(target=speech.speak, args=(speech_text,), daemon=True).start()

        return jsonify({
            "response": response_text,
            "image": f"data:image/jpeg;base64,{frame_b64}",
            "found": object_found,
            "query": query
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/search/continue", methods=["POST"])
def continue_search():
    """Continue search with another picture"""
    try:
        data = request.json
        query = data.get("query", "")

        frame = camera.capture_frame()
        if frame is None:
            return jsonify({"error": "Camera not available"}), 400

        # Convert frame to base64
        import cv2
        _, buffer = cv2.imencode(".jpg", frame)
        import base64
        frame_b64 = base64.b64encode(buffer).decode("utf-8")

        # Retry search
        response = vision.locate_object(frame, query)

        # Check if found
        not_found_phrases = [
            "i don't see", "i cannot see", "not visible", "not in the image",
            "cannot find", "don't see", "no sign of", "not appear"
        ]
        object_found = not any(phrase in response.lower() for phrase in not_found_phrases)

        if object_found:
            response_text = f"✅ Found it! {response}"
        else:
            response_text = f"Still searching... {response}\n\nWant to try again?"

        # Speak
        threading.Thread(target=speech.speak, args=(response_text,), daemon=True).start()

        return jsonify({
            "response": response_text,
            "image": f"data:image/jpeg;base64,{frame_b64}",
            "found": object_found
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/speak", methods=["POST"])
def speak_text():
    """Speak text directly"""
    try:
        data = request.json
        text = data.get("text", "").strip()
        tone = data.get("tone", "neutral")

        if not text:
            return jsonify({"error": "No text provided"}), 400

        threading.Thread(target=speech.speak, args=(text, tone), daemon=True).start()

        return jsonify({"status": "speaking"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.errorhandler(404)
def not_found(e):
    """Handle 404 errors"""
    return jsonify({"error": "Not found"}), 404


@app.errorhandler(500)
def server_error(e):
    """Handle 500 errors"""
    return jsonify({"error": "Server error"}), 500


if __name__ == "__main__":
    print("=" * 60)
    print("JaydeEcho Web App")
    print("=" * 60)
    print(f"Vision Backend: {vision.backend or 'unavailable'}")
    print(f"Speech: {'Available' if speech.available else 'Unavailable'}")
    print(f"Camera: {'Ready' if camera.cap is not None else 'Not found'}")
    print("=" * 60)
    print("Starting server on http://localhost:5000")
    print("Open http://localhost:5000 in your browser or phone")
    print("=" * 60)

    app.run(debug=False, host="0.0.0.0", port=5000)
