"""
generate_music_beds.py
Run ONCE to generate one long music bed per brand via the Eleven Music API
(POST /v1/music). The video pipeline never generates music at render time
anymore -- it loops and trims these beds to fit any video length.

Also deletes the old per-video generated music cache first (music_*.mp3 and
the legacy bed.mp3), since those were duration-keyed one-offs that will
never be reused and just eat disk.

Requests a 10-minute bed to be safe (longer than any tier's max video
length, so looping rarely even kicks in). If the API rejects that length,
steps down automatically -- the pipeline loops whatever length we get, so
a shorter bed still works fine.

Usage:
    python generate_music_beds.py
"""

import os
import glob
import time
import requests
from dotenv import load_dotenv

load_dotenv()

ELEVENLABS_API_KEY = os.environ.get("ELEVENLABS_API_KEY", "")
MUSIC_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                         "bg_musics", "generated")

if not ELEVENLABS_API_KEY:
    raise Exception("ELEVENLABS_API_KEY not set in .env")

os.makedirs(MUSIC_DIR, exist_ok=True)

# Must match BRAND_VIDEO_CONFIG music_style prompts in main.py, and the
# output filenames must match BRAND_MUSIC_BED_PATHS in main.py exactly.
BEDS_TO_GENERATE = [
    (
        "bed_energy_center_usa.mp3",
        "modern corporate background music, clean piano melody with light "
        "electronic percussion, mid tempo, professional and optimistic, "
        "similar to LinkedIn or business explainer video music, no tribal "
        "sounds, no nature sounds, no drums, no ethnic instruments, no "
        "vocals, instrumental only, seamless consistent energy throughout "
        "with no big intro or outro so it can loop cleanly",
    ),
    (
        "bed_be_neutral_now.mp3",
        "modern positive background music, light piano with gentle "
        "electronic beats, clean and contemporary, similar to a feel-good "
        "explainer video or app commercial, hopeful and warm but modern, "
        "absolutely no tribal drums, no nature sounds, no ethnic "
        "instruments, no acoustic guitar, no forest ambience, no vocals, "
        "instrumental only, seamless consistent energy throughout with no "
        "big intro or outro so it can loop cleanly",
    ),
]

# 10 minutes requested; step down if the API caps generation length.
LENGTH_ATTEMPTS_MS = [600_000, 300_000, 180_000, 120_000]


def purge_old_generated():
    """Delete the old per-video duration-keyed music cache. Keeps any
    already-generated brand beds (bed_energy_center_usa / bed_be_neutral_now)."""
    keep = {fname for fname, _ in BEDS_TO_GENERATE}
    removed = 0
    for path in glob.glob(os.path.join(MUSIC_DIR, "*.mp3")):
        if os.path.basename(path) in keep:
            continue
        try:
            os.remove(path)
            removed += 1
            print(f"  🗑  Deleted old cache file: {os.path.basename(path)}")
        except Exception as e:
            print(f"  ⚠ Could not delete {os.path.basename(path)}: {e}")
    if removed == 0:
        print("  ✅ No old cache files to delete")


def generate_bed(prompt: str, out_path: str) -> bool:
    if os.path.exists(out_path) and os.path.getsize(out_path) > 10_000:
        print(f"  ✅ Already exists, skipping: {os.path.basename(out_path)}")
        return True

    for length_ms in LENGTH_ATTEMPTS_MS:
        mins = length_ms / 60_000
        print(f"  🎵 Generating {os.path.basename(out_path)} at {mins:.0f} min...")
        try:
            resp = requests.post(
                "https://api.elevenlabs.io/v1/music",
                headers={"xi-api-key": ELEVENLABS_API_KEY},
                json={
                    "prompt": prompt,
                    "music_length_ms": length_ms,
                },
                timeout=600,
            )
        except Exception as e:
            print(f"  ❌ Request failed: {e}")
            return False

        if resp.status_code == 200 and len(resp.content) > 10_000:
            with open(out_path, "wb") as f:
                f.write(resp.content)
            size_mb = len(resp.content) / (1024 * 1024)
            print(f"  ✅ Saved {size_mb:.1f}MB -> {os.path.basename(out_path)}")
            return True

        body = resp.text[:200]
        print(f"  ⚠ HTTP {resp.status_code} at {mins:.0f} min: {body}")
        # Only step down on what looks like a length/validation rejection;
        # anything else (auth, credits) won't be fixed by a shorter request.
        if resp.status_code not in (400, 422):
            return False
        print(f"  ↩  Retrying at a shorter length...")
        time.sleep(2)

    print(f"  ❌ All length attempts rejected for {os.path.basename(out_path)}")
    return False


if __name__ == "__main__":
    print(f"\n🧹 Purging old generated music in {MUSIC_DIR}/\n")
    purge_old_generated()

    print(f"\n🎵 Generating {len(BEDS_TO_GENERATE)} brand music beds\n")
    success = 0
    for filename, prompt in BEDS_TO_GENERATE:
        out_path = os.path.join(MUSIC_DIR, filename)
        if generate_bed(prompt, out_path):
            success += 1
        time.sleep(2)

    print(f"\n{'=' * 50}")
    print(f"✅ Done: {success}/{len(BEDS_TO_GENERATE)} brand beds ready")
    print(f"📁 Saved to: {MUSIC_DIR}")
    if success < len(BEDS_TO_GENERATE):
        print("⚠  Some beds failed. Fix the reported error and re-run -- "
              "existing beds are skipped, so re-running is safe.")