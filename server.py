#!/usr/bin/env python3
"""
EchoFind — Vision Game Server
- Serves index.html at /  (phone just opens https://YOUR-IP:5443)
- POST /analyse  — receives a JPEG frame, queries Ollama, returns JSON
- GET  /health   — connectivity check

Requirements:
    pip install flask flask-cors requests pyopenssl

Start:
    ollama serve            (terminal 1)
    python3 server.py       (terminal 2)
    Open https://YOUR-LAN-IP:5443 on phone
"""

import json, os, subprocess, socket
import requests
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS

app = Flask(__name__, static_folder=".")
CORS(app)

# ── Config ─────────────────────────────────────────────────────────────────
OLLAMA_URL   = "http://localhost:11434/api/generate"
VISION_MODEL = "llava"        # or: moondream  llava-phi3  bakllava
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
        "-subj", "/CN=EchoFind/O=VisionGame/C=CA",
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
    Receive one JPEG frame, query Ollama, return structured JSON.
    The frontend sends frames sequentially — it awaits this response
    before capturing the next frame, so there is no queue buildup.
    """
    data = request.get_json(force=True) or {}
    image_b64 = data.get("image", "")
    target    = data.get("target", "").strip()
    if not image_b64:
        return jsonify({"ok": False, "error": "Missing image"}), 400
    if not target:
        return jsonify({"ok": False, "error": "Missing target"}), 400
    if "," in image_b64:
        image_b64 = image_b64.split(",", 1)[1]
    return jsonify(_query_ollama(image_b64, target))

# ── Ollama ──────────────────────────────────────────────────────────────────

def _query_ollama(b64_img: str, target: str) -> dict:
    prompt = f"""You are helping a visually impaired person find a '{target}' via their phone camera.

Respond ONLY with a JSON object — no markdown, no extra text.

{{
  "target_found": true | false,
  "target_confidence": 0-100,
  "person_detected": true | false,
  "person_proximity": "none" | "far" | "close" | "very_close",
  "person_position": "center" | "left" | "right" | "none",
  "obstacles": ["list of obstacles"],
  "direction_hint": "short spoken direction e.g. 'turn left slowly'",
  "scene_description": "one sentence describing what the camera sees",
  "urgency": "normal" | "warning" | "danger"
}}

Target: {target}

IMPORTANT NOTES:
- target_confidence should INCREASE as the target gets CLOSER to the camera (0 = not found, 100 = very close to camera)
- When the target fills the frame or is very close, set confidence to 85-100
- When barely visible or far away, set confidence to 20-50
- Confidence reflects HOW CLOSE the target is to the camera lens
- person_position should be "center" if person is in the middle 1/3 of the screen
- person_position should be "left" if person is on the left side (left 1/3 of screen)
- person_position should be "right" if person is on the right side (right 1/3 of screen)
- person_position should be "none" if no person detected
- Be concise — direction_hint will be spoken aloud."""

    try:
        r = requests.post(OLLAMA_URL, json={
            "model": VISION_MODEL,
            "prompt": prompt,
            "images": [b64_img],
            "stream": False,
            "format": "json",
        }, timeout=20)
        r.raise_for_status()
        raw = r.json().get("response", "{}")
        return {"ok": True, "analysis": json.loads(raw)}
    except requests.exceptions.ConnectionError:
        return {"ok": False, "error": "Cannot reach Ollama — run: ollama serve"}
    except requests.exceptions.Timeout:
        return {"ok": False, "error": "Ollama timed out — try moondream model"}
    except json.JSONDecodeError as e:
        return {"ok": False, "error": f"Bad JSON from model: {e}"}
    except Exception as e:
        return {"ok": False, "error": str(e)}

# ── Main ────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    ensure_cert()
    ip = get_local_ip()
    print("=" * 60)
    print("  EchoFind Vision Game")
    print("=" * 60)
    print(f"  Model  : {VISION_MODEL}")
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
