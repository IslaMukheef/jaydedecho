#!/usr/bin/env python3
"""Jayded Echo real-time browser vision game server."""

from __future__ import annotations

import json
import os
import re
import socket
import subprocess
import threading
import time
from collections import deque
from dataclasses import dataclass
from typing import Deque, Dict, Iterable, Tuple

import requests
from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS

app = Flask(__name__, static_folder=".")
CORS(app)

OLLAMA_URL = os.environ.get("OLLAMA_URL", "http://localhost:11434/api/generate")
VISION_MODEL = os.environ.get("VISION_MODEL", "llava")
HTTPS_PORT = int(os.environ.get("HTTPS_PORT", "5443"))
CERT_FILE = os.environ.get("CERT_FILE", "cert.pem")
KEY_FILE = os.environ.get("KEY_FILE", "key.pem")
SESSION_TTL_SECONDS = int(os.environ.get("SESSION_TTL_SECONDS", str(10 * 60)))

frame_buffers: Dict[str, "SessionBuffer"] = {}
lock = threading.Lock()


@dataclass
class FrameResult:
    target_found: bool
    target_confidence: float
    person_detected: bool
    person_confidence: float
    scene_description: str


@dataclass(frozen=True)
class DifficultyRules:
    target_window: int
    target_min_hits: int
    target_min_avg: float
    target_min_frame_conf: float
    target_score_threshold: float
    person_window: int
    person_min_hits: int
    person_min_avg: float
    person_min_frame_conf: float
    person_score_threshold: float


DIFFICULTY_RULES: dict[str, DifficultyRules] = {
    "easy": DifficultyRules(
        target_window=5,
        target_min_hits=2,
        target_min_avg=0.28,
        target_min_frame_conf=0.12,
        target_score_threshold=0.42,
        person_window=3,
        person_min_hits=2,
        person_min_avg=0.28,
        person_min_frame_conf=0.18,
        person_score_threshold=0.35,
    ),
    "hard": DifficultyRules(
        target_window=5,
        target_min_hits=2,
        target_min_avg=0.32,
        target_min_frame_conf=0.15,
        target_score_threshold=0.48,
        person_window=3,
        person_min_hits=2,
        person_min_avg=0.26,
        person_min_frame_conf=0.18,
        person_score_threshold=0.32,
    ),
}


def clamp01(value: object) -> float:
    try:
        v = float(value)
    except Exception:
        return 0.0
    if v != v:
        return 0.0
    return max(0.0, min(1.0, v))


def normalize_confidence(value: object) -> float:
    try:
        v = float(value)
    except Exception:
        return 0.0
    if v > 1.0:
        if v <= 100.0:
            v /= 100.0
        else:
            v = 1.0
    return clamp01(v)


def average(values: Iterable[object]) -> float:
    items = [clamp01(v) for v in values]
    return sum(items) / len(items) if items else 0.0


def clean_text(value: object, limit: int = 160) -> str:
    text = str(value or "").replace("\n", " ").replace("\r", " ").strip()
    text = re.sub(r"\s+", " ", text)
    return text[:limit]


def compact_words(text: str, max_words: int = 6) -> str:
    words = re.sub(r"[^\w\s-]", " ", str(text or "")).split()
    if not words:
        return ""
    return " ".join(words[:max_words])


def normalize_target(target: str) -> str:
    text = str(target or "")
    text = re.sub(r"[^\w\s-]", " ", text, flags=re.UNICODE)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def get_rules(difficulty: str) -> DifficultyRules:
    return DIFFICULTY_RULES.get((difficulty or "").strip().lower(), DIFFICULTY_RULES["easy"])


class SessionBuffer:
    def __init__(self, session_id: str):
        self.session_id = session_id
        self.target_frames: Deque[FrameResult] = deque(maxlen=5)
        self.person_frames: Deque[FrameResult] = deque(maxlen=3)
        self.last_update = time.time()

    def reset(self) -> None:
        self.target_frames.clear()
        self.person_frames.clear()
        self.last_update = time.time()

    def add(self, sample: FrameResult) -> None:
        self.target_frames.append(sample)
        self.person_frames.append(sample)
        self.last_update = time.time()

    @staticmethod
    def _score(frames: Deque[FrameResult], *, found_attr: str, conf_attr: str) -> Tuple[int, float, float]:
        recent = list(frames)
        if not recent:
            return 0, 0.0, 0.0
        hits = 0
        confs = []
        for frame in recent:
            conf = clamp01(getattr(frame, conf_attr))
            confs.append(conf)
            if getattr(frame, found_attr) and conf > 0:
                hits += 1
        avg_conf = average(confs)
        hit_ratio = hits / len(recent)
        score = (0.65 * hit_ratio) + (0.35 * avg_conf)
        return hits, avg_conf, score

    def consensus(self, rules: DifficultyRules) -> FrameResult:
        target_hits, target_avg, target_score = self._score(
            self.target_frames,
            found_attr="target_found",
            conf_attr="target_confidence",
        )
        person_hits, person_avg, person_score = self._score(
            self.person_frames,
            found_attr="person_detected",
            conf_attr="person_confidence",
        )

        target_stable = (
            len(self.target_frames) >= rules.target_min_hits
            and target_hits >= rules.target_min_hits
            and target_avg >= rules.target_min_avg
        )
        person_stable = (
            len(self.person_frames) >= rules.person_min_hits
            and person_hits >= rules.person_min_hits
            and person_avg >= rules.person_min_avg
        )

        target_found = bool(target_stable and target_score >= rules.target_score_threshold)
        person_detected = bool(person_stable and person_score >= rules.person_score_threshold)

        return FrameResult(
            target_found=target_found,
            target_confidence=clamp01(target_avg),
            person_detected=person_detected,
            person_confidence=clamp01(person_avg),
            scene_description=self.target_frames[-1].scene_description if self.target_frames else "",
        )


def cleanup_old_sessions() -> None:
    now = time.time()
    with lock:
        expired = [sid for sid, buf in frame_buffers.items() if now - buf.last_update > SESSION_TTL_SECONDS]
        for sid in expired:
            del frame_buffers[sid]


def get_local_ip() -> str:
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.connect(("8.8.8.8", 80))
        ip = sock.getsockname()[0]
        sock.close()
        return ip
    except Exception:
        return "127.0.0.1"


def ensure_cert() -> None:
    if os.path.exists(CERT_FILE) and os.path.exists(KEY_FILE):
        return
    local_ip = get_local_ip()
    san = f"subjectAltName=IP:{local_ip},IP:127.0.0.1,DNS:localhost"
    cmd = [
        "openssl", "req", "-x509", "-newkey", "rsa:2048",
        "-keyout", KEY_FILE, "-out", CERT_FILE,
        "-days", "365", "-nodes",
        "-subj", "/CN=Jayded Echo/O=VisionGame/C=CA",
        "-addext", san,
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        raise SystemExit(result.stderr or "Failed to generate certificate")


def get_frontend_file() -> str:
    for candidate in ("index.html", "old.html"):
        if os.path.exists(candidate):
            return candidate
    raise FileNotFoundError("Could not find index.html or old.html")


@app.route("/")
def index():
    return send_from_directory(".", get_frontend_file())


@app.route("/health")
def health():
    try:
        r = requests.get("http://localhost:11434/api/tags", timeout=3)
        models = [m.get("name") for m in r.json().get("models", []) if m.get("name")]
        return jsonify({"ok": True, "ollama": "connected", "models": models})
    except Exception:
        return jsonify({"ok": False, "ollama": "unreachable"}), 503


@app.route("/reset_session", methods=["POST"])
def reset_session():
    data = request.get_json(force=True, silent=True) or {}
    session_id = str(data.get("session_id", "default")).strip() or "default"
    with lock:
        if session_id in frame_buffers:
            frame_buffers[session_id].reset()
        else:
            frame_buffers[session_id] = SessionBuffer(session_id)
    return jsonify({"ok": True})


def parse_model_output(raw_response: str) -> dict:
    payload = (raw_response or "").strip()
    try:
        obj = json.loads(payload)
    except json.JSONDecodeError:
        m = re.search(r"\{.*\}", payload, flags=re.DOTALL)
        if not m:
            raise
        obj = json.loads(m.group(0))

    return {
        "target_found": bool(obj.get("target_found", False)),
        "target_confidence": normalize_confidence(obj.get("target_confidence", 0.0)),
        "person_detected": bool(obj.get("person_detected", False)),
        "person_confidence": normalize_confidence(obj.get("person_confidence", 0.0)),
        "scene_description": compact_words(clean_text(obj.get("scene_description", ""), 120), 6),
    }


def build_prompt(target: str) -> str:
    safe_target = normalize_target(target)
    return f"""
You are a strict vision classifier for a browser camera game.

Only inspect the visible image.

Decide only these two things:
1) whether the visible scene contains the target object: "{safe_target}"
2) whether any visible person is present

Rules:
- Only report what is directly visible.
- Do NOT guess, infer, or hallucinate.
- Use low confidence when unsure.
- If the target is not clearly visible, set target_found=false.
- If no person is clearly visible, set person_detected=false.
- Ignore context clues, labels, reflections, photos, drawings, shadows, or text.
- If the target is partially visible, still stay conservative.
- Scene description must be short, factual, and 4 to 6 words maximum.
- Return JSON only. No markdown. No extra text.

Return exactly:
{{
  "target_found": false,
  "target_confidence": 0.0,
  "person_detected": false,
  "person_confidence": 0.0,
  "scene_description": "short factual phrase"
}}
""".strip()


def query_ollama(image_b64: str, target: str) -> dict:
    prompt = build_prompt(target)
    try:
        response = requests.post(
            OLLAMA_URL,
            json={
                "model": VISION_MODEL,
                "prompt": prompt,
                "images": [image_b64],
                "stream": False,
                "format": "json",
                "options": {
                    "temperature": 0.0,
                    "top_p": 0.9,
                },
            },
            timeout=30,
        )
        response.raise_for_status()
        raw_response = response.json().get("response", "{}")
        return {"ok": True, "analysis": parse_model_output(raw_response)}
    except requests.exceptions.ConnectionError:
        return {"ok": False, "error": "Cannot reach Ollama — run: ollama serve"}
    except requests.exceptions.Timeout:
        return {"ok": False, "error": "Ollama timed out"}
    except json.JSONDecodeError:
        return {"ok": False, "error": "Invalid JSON from model"}
    except Exception as exc:
        return {"ok": False, "error": str(exc)}


@app.route("/analyse", methods=["POST"])
def analyse():
    cleanup_old_sessions()
    data = request.get_json(force=True, silent=True) or {}

    image_b64 = str(data.get("image", "")).strip()
    target = str(data.get("target", "")).strip()
    session_id = str(data.get("session_id", "default")).strip() or "default"
    difficulty = str(data.get("difficulty", "easy")).strip().lower() or "easy"
    rules = get_rules(difficulty)

    if not image_b64:
        return jsonify({"error": "Missing image"}), 400
    if not target:
        return jsonify({"error": "Missing target"}), 400

    if "," in image_b64:
        image_b64 = image_b64.split(",", 1)[1]

    if len(image_b64) > 900_000:
        return jsonify({"error": "Image too large"}), 413

    raw = query_ollama(image_b64, target)
    if not raw.get("ok"):
        return jsonify({"error": raw.get("error", "Analysis failed")}), 502

    analysis = raw["analysis"]
    sample = FrameResult(
        target_found=bool(analysis["target_found"]),
        target_confidence=clamp01(analysis["target_confidence"]),
        person_detected=bool(analysis["person_detected"]),
        person_confidence=clamp01(analysis["person_confidence"]),
        scene_description=str(analysis["scene_description"]),
    )

    with lock:
        buffer = frame_buffers.get(session_id)
        if buffer is None:
            buffer = SessionBuffer(session_id)
            frame_buffers[session_id] = buffer
        buffer.add(sample)
        consensus = buffer.consensus(rules)

    return jsonify({
        "ok": True,
        "target_found": bool(consensus.target_found),
        "target_confidence": round(consensus.target_confidence, 3),
        "person_detected": bool(consensus.person_detected),
        "person_confidence": round(consensus.person_confidence, 3),
        "scene_description": analysis["scene_description"],
        "difficulty": difficulty,
    })


if __name__ == "__main__":
    ensure_cert()
    ip = get_local_ip()
    print("=" * 72)
    print("  Jayded Echo Vision Game Server")
    print("=" * 72)
    print(f"  Model  : {VISION_MODEL}")
    print(f"  HTTPS  : https://{ip}:{HTTPS_PORT}")
    for name, rules in DIFFICULTY_RULES.items():
        print(
            f"  {name.title():5s}: target {rules.target_min_hits}/{rules.target_window} "
            f"avg >= {rules.target_min_avg:.2f}, score >= {rules.target_score_threshold:.2f}; "
            f"person {rules.person_min_hits}/{rules.person_window} avg >= {rules.person_min_avg:.2f}"
        )
    print("=" * 72)
    app.run(host="0.0.0.0", port=HTTPS_PORT, ssl_context=(CERT_FILE, KEY_FILE), threaded=True)
