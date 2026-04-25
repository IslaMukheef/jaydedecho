#!/usr/bin/env python3
"""
Quick test script for API connectivity without requiring a camera
Tests: Gemini Vision, ElevenLabs TTS, Router
"""

import sys
import os
import numpy as np
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from config import Config
from vision import Vision
from speech import Speech
from router import Router


def create_test_frame():
    """Create a fake frame for testing"""
    # Create a simple 640x480 RGB image (blue square)
    frame = np.zeros((480, 640, 3), dtype=np.uint8)
    frame[:, :] = [200, 100, 50]  # BGR color (blue-ish)
    return frame


def test_vision():
    """Test Gemini Vision API"""
    print("\n=== Testing Vision API (Gemini) ===")
    config = Config()
    vision = Vision(config)

    if vision.model is None:
        print("❌ Vision API not initialized")
        return False

    frame = create_test_frame()
    print("Testing: describe_scene()")
    response = vision.describe_scene(frame)
    print(f"Response: {response[:100]}...")

    if "Could not" not in response:
        print("✅ Vision API working!")
        return True
    else:
        print(f"⚠️  Vision returned error: {response}")
        return False


def test_speech():
    """Test System TTS"""
    print("\n=== Testing Speech API (System TTS) ===")
    config = Config()
    speech = Speech(config)

    if not speech.available:
        print("❌ Speech API not initialized")
        return False

    print("Testing: speak()")
    success = speech.speak("This is a test of the voice system")

    if success:
        print("✅ Speech API working!")
        return True
    else:
        print("❌ Speech API failed")
        return False


def test_router():
    """Test Router API"""
    print("\n=== Testing Router ===")
    config = Config()
    router = Router(config)

    print("Testing: plan_route()")
    response = router.plan_route("Downtown Toronto")
    print(f"Response: {response[:100]}...")

    if "Route" in response or "route" in response:
        print("✅ Router working!")
        return True
    else:
        print("⚠️  Router returned: {response}")
        return False


def main():
    print("=" * 60)
    print("JaydeEcho - API Connectivity Test")
    print("=" * 60)

    results = {
        "Vision": False,
        "Speech": False,
        "Router": False,
    }

    try:
        results["Vision"] = test_vision()
    except Exception as e:
        print(f"❌ Vision test error: {e}")

    try:
        results["Speech"] = test_speech()
    except Exception as e:
        print(f"❌ Speech test error: {e}")

    try:
        results["Router"] = test_router()
    except Exception as e:
        print(f"❌ Router test error: {e}")

    print("\n" + "=" * 60)
    print("Test Results:")
    for name, passed in results.items():
        status = "✅" if passed else "❌"
        print(f"  {status} {name}")

    print("=" * 60)

    if all(results.values()):
        print("\n🎉 All systems operational!")
        return 0
    else:
        print("\n⚠️  Some systems need attention")
        return 1


if __name__ == "__main__":
    sys.exit(main())
