from elevenlabs.client import ElevenLabs

client = ElevenLabs(api_key="sk_c2dc1279cf2b853f947bd5704b35dbe9f8c947769351bd3d")

with client.text_to_speech.with_raw_response.convert(
    text="Hello, world!",
    voice_id="21m00Tcm4TlvDq8ikWAM"
) as response:

    char_cost = response.headers.get("x-character-count")
    request_id = response.headers.get("request-id")
    audio_data = response.data

print(char_cost, request_id)
