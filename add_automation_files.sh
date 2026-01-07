#!/usr/bin/env bash
set -e

echo "📦 Adding automation files to existing repo..."

mkdir -p videos/raw videos/processed logs cookies

# -------------------------
# .env.example
# -------------------------
cat > .env.example <<'EOF'
TWITCH_CLIENT_ID=your_client_id_here
TWITCH_CLIENT_SECRET=your_client_secret_here

GAME_NAME=Among Us
LOOKBACK_HOURS=24
PARTNER_ONLY=true

WHISPER_MODEL=small
HASHTAGS=#AmongUs #twitch #gaming #fyp

ENABLE_TIKTOK_UPLOAD=false
TIKTOK_COOKIES_TXT=cookies/cookies.txt
TIKTOK_HEADLESS=true
EOF

# -------------------------
# cookies/README.md
# -------------------------
mkdir -p cookies
cat > cookies/README.md <<'EOF'
TikTok cookies

This project uses tiktok-uploader for automatic uploads.

You MUST provide a Netscape-format cookies.txt file.

Steps:
1. Log into TikTok in Chrome (local machine)
2. Export cookies as cookies.txt (Netscape format)
3. Place it here: cookies/cookies.txt
4. DO NOT commit cookies to git
EOF

# -------------------------
# twitch_clips.py
# -------------------------
cat > twitch_clips.py <<'EOF'
import os
import requests
from datetime import datetime, timedelta, timezone

TWITCH_TOKEN_URL = "https://id.twitch.tv/oauth2/token"
TWITCH_API_URL = "https://api.twitch.tv/helix"

def _headers(token):
    return {
        "Client-ID": os.environ["TWITCH_CLIENT_ID"],
        "Authorization": f"Bearer {token}",
    }

def get_app_token(client_id, client_secret):
    r = requests.post(
        TWITCH_TOKEN_URL,
        params={
            "client_id": client_id,
            "client_secret": client_secret,
            "grant_type": "client_credentials",
        },
    )
    r.raise_for_status()
    return r.json()["access_token"]

def get_game_id(game_name, token):
    r = requests.get(
        f"{TWITCH_API_URL}/games",
        headers=_headers(token),
        params={"name": game_name},
    )
    r.raise_for_status()
    return r.json()["data"][0]["id"]

def get_top_clip_for_game(game_id, token, lookback_hours=24, partner_only=True):
    started_at = (datetime.now(timezone.utc) - timedelta(hours=lookback_hours)).isoformat()

    r = requests.get(
        f"{TWITCH_API_URL}/clips",
        headers=_headers(token),
        params={"game_id": game_id, "first": 50, "started_at": started_at},
    )
    r.raise_for_status()
    clips = r.json()["data"]

    if partner_only:
        broadcaster_ids = list({c["broadcaster_id"] for c in clips})
        users = requests.get(
            f"{TWITCH_API_URL}/users",
            headers=_headers(token),
            params=[("id", uid) for uid in broadcaster_ids],
        ).json()["data"]

        partners = {u["id"] for u in users if u["broadcaster_type"] == "partner"}
        clips = [c for c in clips if c["broadcaster_id"] in partners]

    clips.sort(key=lambda c: c["view_count"], reverse=True)
    top = clips[0]

    return {
        "url": top["url"],
        "title": top["title"],
        "views": top["view_count"],
        "broadcaster": top["broadcaster_name"],
    }
EOF

# -------------------------
# downloader.py
# -------------------------
cat > downloader.py <<'EOF'
import subprocess
from pathlib import Path

def download_clip(url, output):
    Path(output).parent.mkdir(parents=True, exist_ok=True)
    subprocess.run(["yt-dlp", "-f", "mp4/best", "-o", output, url], check=True)
EOF

# -------------------------
# subtitles.py
# -------------------------
cat > subtitles.py <<'EOF'
from pathlib import Path
from faster_whisper import WhisperModel

def _fmt(t):
    ms = int(t * 1000)
    h, ms = divmod(ms, 3600000)
    m, ms = divmod(ms, 60000)
    s, ms = divmod(ms, 1000)
    return f"{h:02}:{m:02}:{s:02},{ms:03}"

def transcribe_to_srt(video, out, model="small"):
    Path(out).parent.mkdir(parents=True, exist_ok=True)
    model = WhisperModel(model, device="cpu", compute_type="int8")
    segments, _ = model.transcribe(video)

    lines = []
    i = 1
    for seg in segments:
        if seg.text.strip():
            lines += [
                str(i),
                f"{_fmt(seg.start)} --> {_fmt(seg.end)}",
                seg.text.strip(),
                ""
            ]
            i += 1

    Path(out).write_text("\n".join(lines), encoding="utf-8")
EOF

# -------------------------
# video.py
# -------------------------
cat > video.py <<'EOF'
import subprocess
from pathlib import Path

def run(cmd):
    subprocess.run(cmd, check=True)

def make_vertical(inp, out):
    Path(out).parent.mkdir(parents=True, exist_ok=True)
    run([
        "ffmpeg","-y","-i",inp,
        "-vf","scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920",
        "-c:v","libx264","-crf","23","-preset","fast",
        "-c:a","aac","-b:a","128k",
        out
    ])

def burn_subtitles(inp, srt, out):
    style = "Fontsize=42,Outline=2,Shadow=1"
    run([
        "ffmpeg","-y","-i",inp,
        "-vf",f"subtitles={srt}:force_style='{style}'",
        "-c:v","libx264","-crf","23",
        "-c:a","copy",
        out
    ])
EOF

# -------------------------
# tiktok_upload.py
# -------------------------
cat > tiktok_upload.py <<'EOF'
import os
import subprocess
from pathlib import Path

def upload_to_tiktok(video, caption):
    cookies = os.getenv("TIKTOK_COOKIES_TXT", "cookies/cookies.txt")
    if not Path(cookies).exists():
        raise RuntimeError("cookies.txt missing")

    subprocess.run(
        ["tiktok-uploader", "-video", video, "-description", caption, "-cookies", cookies],
        check=True
    )
EOF

# -------------------------
# Dockerfile
# -------------------------
cat > Dockerfile <<'EOF'
FROM python:3.12-slim

RUN apt-get update && apt-get install -y \
    ffmpeg chromium chromium-driver xvfb \
    libatk-bridge2.0-0 libgtk-3-0 libnss3 \
    libxcomposite1 libxdamage1 libxrandr2 \
    libgbm1 libasound2 libdrm2 libxshmfence1 \
    && rm -rf /var/lib/apt/lists/*

ENV DISPLAY=:99
WORKDIR /app
COPY . .
RUN pip install -r requirements.txt
CMD ["bash","-lc","xvfb-run -a python main.py"]
EOF

echo "✅ Additional automation files created."
echo "Next:"
echo "  git add ."
echo "  git commit -m 'Add partner-only Twitch + subtitles + TikTok upload'"
echo "  git push"
