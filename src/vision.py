"""
Vision module - interfaces with local Ollama or cloud Gemini API
Provides scene description, object detection, and conversational guidance
"""

import logging
from typing import Optional
import numpy as np
import base64
import cv2
import requests
import json

try:
    import google.generativeai as genai
except ImportError:
    genai = None

logger = logging.getLogger(__name__)


class Vision:
    """Vision AI interface using local Ollama (preferred) or cloud Gemini"""

    def __init__(self, config):
        """Initialize vision backend (Ollama first, then Gemini)"""
        self.config = config
        self.model = None
        self.backend = None  # "ollama" or "gemini"
        self.ollama_url = "http://localhost:11434"

        # Try Ollama first (local, free, offline)
        if self._init_ollama():
            return

        # Fallback to Gemini
        if self._init_gemini():
            return

        logger.error("No vision backend available (install Ollama or set GEMINI_API_KEY)")

    def _init_ollama(self) -> bool:
        """Try to initialize Ollama backend"""
        try:
            # Check if Ollama is running
            response = requests.get(f"{self.ollama_url}/api/tags", timeout=2)
            if response.status_code == 200:
                models = response.json().get("models", [])
                if models:
                    # Prefer vision-capable models
                    vision_models = ["llava", "bakllava", "minicpm-v"]
                    text_models = ["gemma2", "mistral", "llama2"]

                    # Try to find a vision model first
                    for model_info in models:
                        model_name = model_info["name"].split(":")[0]
                        if any(v in model_name.lower() for v in vision_models):
                            self.model = model_name
                            self.backend = "ollama"
                            logger.info(f"✓ Ollama initialized with vision model: {model_name}")
                            return True

                    # Fallback to any available model
                    model_name = models[0]["name"].split(":")[0]
                    self.model = model_name
                    self.backend = "ollama"

                    # Warn if not a vision model
                    is_vision = any(v in model_name.lower() for v in vision_models)
                    if not is_vision:
                        logger.warning(f"Model '{model_name}' is text-only. For best results, install a vision model:")
                        logger.warning("  ollama pull llava          # Best for images")
                        logger.warning("  ollama pull bakllava       # Faster alternative")
                    else:
                        logger.info(f"✓ Ollama initialized with model: {model_name}")

                    return True
                else:
                    logger.warning("Ollama running but no models installed")
                    logger.info("Install a model with:")
                    logger.info("  ollama pull llava          # Vision model (recommended)")
                    logger.info("  ollama pull gemma2         # Text model")
                    return False
        except (requests.ConnectionError, requests.Timeout):
            logger.debug("Ollama not running (http://localhost:11434)")
            return False
        except Exception as e:
            logger.debug(f"Ollama init failed: {e}")
            return False

    def _init_gemini(self) -> bool:
        """Try to initialize Gemini backend"""
        if not self.config.gemini_api_key:
            logger.debug("GEMINI_API_KEY not set")
            return False

        if genai is None:
            logger.warning("google.generativeai not installed")
            return False

        try:
            genai.configure(api_key=self.config.gemini_api_key)

            # Try to use latest available model
            model_names = [
                "gemini-2.0-flash",
                "gemini-1.5-pro",
                "gemini-1.5-flash",
            ]

            for model_name in model_names:
                try:
                    model = genai.GenerativeModel(model_name)
                    self.model = model
                    self.backend = "gemini"
                    logger.info(f"✓ Gemini API initialized with model: {model_name}")
                    return True
                except Exception as e:
                    logger.debug(f"Model {model_name} not available: {e}")
                    continue

            logger.error("No compatible Gemini model found")
            return False

        except Exception as e:
            logger.error(f"Failed to initialize Gemini: {e}")
            return False

    def _encode_frame(self, frame: np.ndarray) -> str:
        """Encode numpy frame to base64 JPEG"""
        try:
            _, buffer = cv2.imencode(".jpg", frame, [cv2.IMWRITE_JPEG_QUALITY, 85])
            encoded = base64.standard_b64encode(buffer).decode("utf-8")
            return encoded
        except Exception as e:
            logger.error(f"Error encoding frame: {e}")
            return ""

    def _query_ollama(self, frame_b64: str, prompt: str) -> str:
        """Query local Ollama model with image"""
        try:
            url = f"{self.ollama_url}/api/generate"

            # Check if model is vision-capable
            vision_models = ["llava", "bakllava", "minicpm-v"]
            is_vision_model = any(v in self.model.lower() for v in vision_models)

            if not is_vision_model:
                # Text-only model - can't process images
                logger.warning(f"Model '{self.model}' is text-only. Cannot process images.")
                return (
                    f"⚠️ Current model '{self.model}' cannot process images. "
                    f"Please install a vision model:\n\n"
                    f"Run in terminal: ollama pull llava\n\n"
                    f"Then restart the app."
                )

            # Vision model - send image
            payload = {
                "model": self.model,
                "prompt": prompt,
                "images": [frame_b64],  # Base64 encoded image
                "stream": False,
            }

            logger.info(f"Querying Ollama vision model '{self.model}' with image")
            response = requests.post(url, json=payload, timeout=120)  # Vision takes longer

            if response.status_code == 200:
                result = response.json()
                text = result.get("response", "").strip()

                if text:
                    logger.info(f"Ollama response received: {text[:100]}...")
                    return text
                else:
                    logger.warning("Ollama returned empty response")
                    return "I processed the image but couldn't generate a response. Try again?"
            else:
                logger.error(f"Ollama error {response.status_code}: {response.text}")
                return f"Ollama error: {response.status_code}"

        except requests.Timeout:
            return "Ollama request timed out. Vision processing takes time - please wait or try a smaller model."
        except Exception as e:
            logger.error(f"Error querying Ollama: {e}")
            return f"Error: {str(e)}"

    def _query_gemini(self, frame_b64: str, prompt: str) -> str:
        """Query Gemini API with image"""
        try:
            response = self.model.generate_content(
                [
                    prompt,
                    {
                        "mime_type": "image/jpeg",
                        "data": frame_b64,
                    }
                ],
                stream=False
            )
            return response.text
        except Exception as e:
            logger.error(f"Error querying Gemini: {e}")
            return f"Error querying Gemini: {str(e)}"

    def describe_scene(self, frame: np.ndarray, context: str = "") -> str:
        """
        Describe what's visible in the camera frame
        Returns natural language description suitable for audio output
        """
        if self.model is None or self.backend is None:
            return "Vision service unavailable. Install Ollama or set GEMINI_API_KEY."

        try:
            frame_b64 = self._encode_frame(frame)
            if not frame_b64:
                return "Could not encode image for analysis"

            prompt = f"""You are an assistant for a visually impaired person.

Describe what you see in this image in a natural, conversational way.
Focus on spatial awareness: what's in front, to the sides, obstacles, and interesting details.
Keep your response under 3 sentences and make it directly useful for navigation.
{f'Context: {context}' if context else ''}"""

            if self.backend == "ollama":
                return self._query_ollama(frame_b64, prompt)
            else:
                return self._query_gemini(frame_b64, prompt)

        except Exception as e:
            logger.error(f"Error in describe_scene: {e}")
            return f"Could not analyze image: {str(e)}"

    def locate_object(self, frame: np.ndarray, target: str, context: str = "") -> str:
        """Find and locate a specific object in the frame"""
        if self.model is None or self.backend is None:
            return "Vision service unavailable."

        try:
            frame_b64 = self._encode_frame(frame)
            if not frame_b64:
                return "Could not encode image for analysis"

            prompt = f"""You are an assistant for a visually impaired person.

In this image, find the {target} and tell me EXACTLY where it is relative to the
person holding the camera (left/right/center, near/far, etc).

If you do not see the {target}, suggest where the person should look next.

Keep your answer under two sentences and make it conversational.
{f'Context: {context}' if context else ''}"""

            if self.backend == "ollama":
                return self._query_ollama(frame_b64, prompt)
            else:
                return self._query_gemini(frame_b64, prompt)

        except Exception as e:
            logger.error(f"Error in locate_object: {e}")
            return f"Could not locate {target}: {str(e)}"

    def detect_seats(self, frame: np.ndarray) -> str:
        """Detect empty seats in a bus or venue"""
        if self.model is None or self.backend is None:
            return "Vision service unavailable."

        try:
            frame_b64 = self._encode_frame(frame)
            if not frame_b64:
                return "Could not encode image for analysis"

            prompt = """You are an assistant for a visually impaired person on a bus or in a venue.

Look at this image and identify empty seats or standing room.
Describe EXACTLY where the empty seats are relative to the camera perspective.
Include approximate distances (near, middle, far) and directions (left, center, right).

Keep your answer under 2 sentences and be specific about locations."""

            if self.backend == "ollama":
                return self._query_ollama(frame_b64, prompt)
            else:
                return self._query_gemini(frame_b64, prompt)

        except Exception as e:
            logger.error(f"Error in detect_seats: {e}")
            return f"Could not detect seating: {str(e)}"

    def get_guidance(self, frame: np.ndarray, query: str, context: str = "") -> str:
        """Provide guidance for natural language queries with vision context"""
        if self.model is None or self.backend is None:
            return "Vision service unavailable."

        try:
            frame_b64 = self._encode_frame(frame)
            if not frame_b64:
                return "Could not encode image for analysis"

            query_lower = query.lower()

            if "where" in query_lower or "find" in query_lower or "see" in query_lower:
                if " the " in query_lower:
                    target = query_lower.split(" the ")[-1].strip("?").strip()
                    return self.locate_object(frame, target, context)
                elif "seat" in query_lower or "chair" in query_lower or "empty" in query_lower:
                    return self.detect_seats(frame)
                else:
                    return self.describe_scene(frame, context)
            else:
                prompt = f"""You are an assistant for a visually impaired person.

User question: {query}

Look at the image and answer their question in a natural, conversational way.
Focus on spatial and practical information.
Keep your answer concise (under 2 sentences if possible).
{f'Context: {context}' if context else ''}"""

                if self.backend == "ollama":
                    return self._query_ollama(frame_b64, prompt)
                else:
                    return self._query_gemini(frame_b64, prompt)

        except Exception as e:
            logger.error(f"Error in get_guidance: {e}")
            return f"Could not provide guidance: {str(e)}"
