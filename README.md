# twitchtokker (Twitch -> TikTok-ready video generator)

This project:
- Uses Twitch Helix API to find the top clip for a game (Among Us by default)
- Filters to Partner streamers only
- Downloads the clip
- Converts to vertical 1080x1920
- Auto-generates subtitles using faster-whisper
- Burns subtitles into final video

## Local setup

1) Install ffmpeg (required).
2) Create venv and install deps:
   python3 -m venv botenv
   source botenv/bin/activate
   pip install -r requirements.txt

3) Create .env:
   cp .env.example .env
   (edit TWITCH_CLIENT_ID and TWITCH_CLIENT_SECRET)

4) Run:
   python main.py

Output: videos/processed/final.mp4
