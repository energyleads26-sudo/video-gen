"""
Run this once before starting the video pipeline server.
Creates all required directories and placeholder files.
Usage: python setup_folders.py
"""

import os

# ── Directories to create ────────────────────────────────────────────
dirs = [
    "Audio_Voice",
    "bg_musics",
    "bg_musics/generated",
    "sfx",
    "fonts",
    "backgrounds",
    "backgrounds/energy_center_usa",
    "backgrounds/be_neutral_now",
    # Manim runtime dirs (also auto-created at runtime, but good to have)
    "/tmp/finance_explainer_manim_cache",
    "/tmp/finance_explainer_manim_logs",
    "/tmp/finance_explainer_manim_sources",
]

for d in dirs:
    os.makedirs(d, exist_ok=True)
    print(f"  ✅ {d}")

# ── .gitkeep files so empty folders survive git ───────────────────────
gitkeep_dirs = [
    "Audio_Voice",
    "bg_musics/generated",
    "sfx",
    "fonts",
    "backgrounds/energy_center_usa",
    "backgrounds/be_neutral_now",
]

for d in gitkeep_dirs:
    path = os.path.join(d, ".gitkeep")
    if not os.path.exists(path):
        open(path, "w").close()
        print(f"  📄 {path}")

print("\n✅ All folders ready. Add your sfx and font files before starting the server.")