"""
generate_sfx.py
Run once to generate all SFX files needed by the video pipeline.
Uses ElevenLabs Sound Effects API (POST /v1/sound-generation).
Saves files directly to the sfx/ folder.

Usage:
    python generate_sfx.py
"""

import os
import requests
import time
from dotenv import load_dotenv

load_dotenv()

ELEVENLABS_API_KEY = os.environ.get("ELEVENLABS_API_KEY", "")
SFX_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "sfx")

if not ELEVENLABS_API_KEY:
    raise Exception("ELEVENLABS_API_KEY not set in .env")

os.makedirs(SFX_DIR, exist_ok=True)

# Each entry: (filename_in_sfx_map, elevenlabs_prompt, duration_seconds)
SFX_TO_GENERATE = [
    (
        "alexzavesa-swoosh-1-463607.mp3",
        "a smooth fast whoosh sound effect, like a line chart or graph appearing on screen, clean and modern, no reverb",
        1.0,
    ),
    (
        "universfield-new-notification-010-352755.mp3",
        "a soft satisfying card pop sound effect, like a UI card appearing on screen, subtle and clean, modern app sound",
        0.8,
    ),
    (
        "universfield-new-notification-013-363676.mp3",
        "a gentle positive chime sound effect, like a solution or success notification, soft and uplifting, clean tone",
        1.0,
    ),
    (
        "universfield-new-notification-014-363678.mp3",
        "a short alert ping sound effect, like a warning or attention notification, crisp and clear, neutral tone",
        0.8,
    ),
    (
        "freesound_community-punch-boxing-02wav-14897.mp3",
        "a sharp impact hit sound effect, like a heavy data point or problem landing on screen, punchy and short",
        0.6,
    ),
    (
        "dragon-studio-mouse-click-4-393911.mp3",
        "a tiny clean mouse click sound effect, short and crisp, like a UI button tap, minimal and modern",
        0.5,
    ),
]


def generate_sfx(prompt: str, duration: float, out_path: str) -> bool:
    if os.path.exists(out_path):
        print(f"  ✅ Already exists, skipping: {os.path.basename(out_path)}")
        return True

    print(f"  🎵 Generating: {os.path.basename(out_path)}")
    print(f"     Prompt: {prompt[:80]}...")

    try:
        resp = requests.post(
            "https://api.elevenlabs.io/v1/sound-generation",
            headers={
                "xi-api-key": ELEVENLABS_API_KEY,
                "Content-Type": "application/json",
            },
            json={
                "text": prompt,
                "duration_seconds": duration,
                "prompt_influence": 0.3,
            },
            timeout=60,
        )

        if resp.status_code != 200:
            print(f"  ❌ HTTP {resp.status_code}: {resp.text[:200]}")
            return False

        with open(out_path, "wb") as f:
            f.write(resp.content)

        size_kb = len(resp.content) // 1024
        print(f"  ✅ Saved {size_kb}KB -> {os.path.basename(out_path)}")
        return True

    except Exception as e:
        print(f"  ❌ Failed: {e}")
        return False


if __name__ == "__main__":
    print(f"\n🔊 Generating {len(SFX_TO_GENERATE)} SFX files into {SFX_DIR}/\n")

    success = 0
    for filename, prompt, duration in SFX_TO_GENERATE:
        out_path = os.path.join(SFX_DIR, filename)
        ok = generate_sfx(prompt, duration, out_path)
        if ok:
            success += 1
        time.sleep(1)  # brief pause between calls

    print(f"\n{'='*50}")
    print(f"✅ Done: {success}/{len(SFX_TO_GENERATE)} SFX files generated")
    print(f"📁 Saved to: {SFX_DIR}")

    if success < len(SFX_TO_GENERATE):
        print("⚠  Some files failed. Re-run the script to retry missing ones.")