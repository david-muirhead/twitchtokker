import os
from dotenv import load_dotenv

load_dotenv()

TWITCH_CLIENT_ID = os.getenv("TWITCH_CLIENT_ID", "").strip()
TWITCH_CLIENT_SECRET = os.getenv("TWITCH_CLIENT_SECRET", "").strip()

FETCH_FIRST = int(os.getenv("FETCH_FIRST", "100"))

GAME_NAME = os.getenv("GAME_NAME", "Among Us").strip()
LOOKBACK_HOURS = int(os.getenv("LOOKBACK_HOURS", "24"))
PARTNER_ONLY = os.getenv("PARTNER_ONLY", "true").lower() in ("1", "true", "yes", "y")

WHISPER_MODEL = os.getenv("WHISPER_MODEL", "small").strip()

HASHTAGS = os.getenv("HASHTAGS", "#AmongUs #twitch #gaming #fyp").strip()

RAW_VIDEO = "videos/raw/clip.mp4"
VERTICAL_VIDEO = "videos/processed/vertical.mp4"
SUB_SRT = "videos/processed/subtitles.srt"
FINAL_VIDEO = "videos/processed/final.mp4"
LOG_FILE = "logs/run.log"
