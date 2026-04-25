#!/usr/bin/env python3
"""
Jayded Echo — Vision Game Server
- Serves index.html at /  (phone just opens https://YOUR-IP:5443)
- POST /analyse  — receives a JPEG frame, queries Ollama, returns JSON
- GET  /health   — connectivity check

Requirements:
    pip install flask flask-cors requests pyopenssl

Start:
    ollama serve            (terminal 1)
    python3 server.py       (terminal 2)
    Open https://YOUR-LAN-IP:5443 on phone

RECOMMENDED MODEL: llava
    - Most reliable for object and person detection
    - Good balance of speed and accuracy
    - Detects both objects and people consistently

    Setup:
    ollama pull llava

Alternative models:
    - llava:13b: More accurate but slower
    - moondream: Faster but less reliable for this task
    - llava-phi: Fastest but less accurate
"""

import json, os, subprocess, socket
import requests
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS

app = Flask(__name__, static_folder=".")
CORS(app)

# ── Config ─────────────────────────────────────────────────────────────────
OLLAMA_URL   = "http://localhost:11434/api/generate"
VISION_MODEL = "llava"             # Most reliable for object/person detection
                                   # Note: Slower than moondream but more accurate
                                   # Alternatives: llava:13b (more accurate), moondream (faster)
HTTPS_PORT   = 5443
CERT_FILE    = "cert.pem"
KEY_FILE     = "key.pem"
# ───────────────────────────────────────────────────────────────────────────

def get_local_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "127.0.0.1"

def ensure_cert():
    if os.path.exists(CERT_FILE) and os.path.exists(KEY_FILE):
        return
    local_ip = get_local_ip()
    print(f"  Generating self-signed TLS certificate for {local_ip} ...")
    san = f"subjectAltName=IP:{local_ip},IP:127.0.0.1,DNS:localhost"
    cmd = [
        "openssl", "req", "-x509", "-newkey", "rsa:2048",
        "-keyout", KEY_FILE, "-out", CERT_FILE,
        "-days", "365", "-nodes",
        "-subj", "/CN=Jayded Echo/O=VisionGame/C=CA",
        "-addext", san,
    ]
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        print("  ERROR:", r.stderr)
        raise SystemExit(1)
    print(f"  cert.pem + key.pem written.")

# ── Routes ──────────────────────────────────────────────────────────────────

@app.route("/")
def index():
    """Serve the game UI — phone just opens https://IP:5443"""
    return send_from_directory(".", "index.html")

@app.route("/health")
def health():
    try:
        r = requests.get("http://localhost:11434/api/tags", timeout=3)
        models = [m["name"] for m in r.json().get("models", [])]
        return jsonify({"ok": True, "ollama": "connected", "models": models})
    except Exception:
        return jsonify({"ok": False, "ollama": "unreachable — run: ollama serve"})

@app.route("/analyse", methods=["POST"])
def analyse():
    """
    Receive one JPEG/WebP frame, query Ollama, return structured JSON.
    The frontend sends frames sequentially — it awaits this response
    before capturing the next frame, so there is no queue buildup.

    Optimizations:
    - Supports both JPEG and WebP formats (WebP is more efficient)
    - Validates image size before processing
    - Generous size limit for mobile (800KB) - Ollama handles compression well
    """
    data = request.get_json(force=True) or {}
    image_b64 = data.get("image", "").strip()
    target    = data.get("target", "").strip()
    if not image_b64:
        return jsonify({"ok": False, "error": "Missing image"}), 400
    if not target:
        return jsonify({"ok": False, "error": "Missing target"}), 400

    # Remove data URL prefix if present (handles both JPEG and WebP)
    if "," in image_b64:
        image_b64 = image_b64.split(",", 1)[1]

    # Validate base64 length - allow up to 800KB for mobile quality
    # Base64 adds ~33% overhead, so 800KB base64 ≈ 600KB actual image
    if len(image_b64) > 800000:
        return jsonify({"ok": False, "error": "Image too large"}), 413

    return jsonify(_query_ollama(image_b64, target))

# ── Ollama ──────────────────────────────────────────────────────────────────

def _query_ollama(b64_img: str, target: str) -> dict:
    prompt = f"""Analyze this image and respond with ONLY a JSON object (no markdown, no extra text).

{{
  "target_found": true or false,
  "target_confidence": 0-100,
  "person_detected": true or false,
  "person_confidence": 0-100,
  "obstacles": ["obstacle names"],
  "direction_hint": "turn left or move forward",
  "scene_description": "one sentence about what's in the image",
  "urgency": "normal"
}}

Task: Find a "{target}" in this image.

RULES:
- target_found: Is the target object visible in this image? true/false
- target_confidence: How close/clear is it? 0-100 where 100 = very close to camera
- person_detected: Is there a person/human in this image? true/false
- person_confidence: How certain are you? 0-100 where 100 = definitely a person
- obstacles: List any hazards or blocking objects
- direction_hint: Suggest how to move (left, right, forward, etc)
- scene_description: Brief description of the scene
- urgency: normal

Be precise and accurate. Return ONLY valid JSON."""

    try:
        print(f"[DEBUG] Querying ollama with target: {target}")
        r = requests.post(OLLAMA_URL, json={
            "model": VISION_MODEL,
            "prompt": prompt,
            "images": [b64_img],
            "stream": False,
            "format": "json",
        }, timeout=25)
        r.raise_for_status()

        raw_response = r.json().get("response", "{}")
        print(f"[DEBUG] Raw response: {raw_response[:200]}")

        analysis = json.loads(raw_response)

        # Validate required fields exist
        analysis.setdefault("target_found", False)
        analysis.setdefault("target_confidence", 0)
        analysis.setdefault("person_detected", False)
        analysis.setdefault("person_confidence", 0)
        analysis.setdefault("obstacles", [])
        analysis.setdefault("direction_hint", "")
        analysis.setdefault("scene_description", "")
        analysis.setdefault("urgency", "normal")

        print(f"[DEBUG] Parsed analysis: target={analysis.get('target_found')}, person={analysis.get('person_detected')}")
        return {"ok": True, "analysis": analysis}

    except requests.exceptions.ConnectionError:
        return {"ok": False, "error": "Cannot reach Ollama — run: ollama serve"}
    except requests.exceptions.Timeout:
        return {"ok": False, "error": "Ollama timed out"}
    except json.JSONDecodeError as e:
        print(f"[DEBUG] JSON decode error: {e}")
        return {"ok": False, "error": f"Bad JSON from model"}
    except Exception as e:
        print(f"[DEBUG] Exception: {e}")
        return {"ok": False, "error": str(e)}

# ── Main ────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    ensure_cert()
    ip = get_local_ip()
    print("=" * 60)
    print("  Jayded Echo Vision Game")
    print("=" * 60)
    print(f"  Model  : {VISION_MODEL}")
    if VISION_MODEL != "llava":
        print(f"  ℹ️  Using {VISION_MODEL} (note: try llava for better detection)")
    print(f"  Local  : https://localhost:{HTTPS_PORT}")
    print(f"  Phone  : https://{ip}:{HTTPS_PORT}   <-- open this on mobile")
    print()
    print("  First time on phone:")
    print("    Chrome : tap Advanced -> Proceed")
    print("    Safari : tap Show Details -> visit website")
    print("    iOS    : download cert.pem, install via")
    print("             Settings > General > VPN & Device Management")
    print()
    print("  Run Ollama first:  ollama serve")
    print(f"  Pull model:        ollama pull {VISION_MODEL}")
    print("=" * 60)
    app.run(host="0.0.0.0", port=HTTPS_PORT,
            ssl_context=(CERT_FILE, KEY_FILE),
            debug=False, threaded=True)
