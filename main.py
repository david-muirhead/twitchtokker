import os
from config import (
    TWITCH_CLIENT_ID, TWITCH_CLIENT_SECRET,
    GAME_NAME, LOOKBACK_HOURS, PARTNER_ONLY,
    RAW_VIDEO, VERTICAL_VIDEO, SUB_SRT, FINAL_VIDEO,
    WHISPER_MODEL, HASHTAGS
)
from twitch_clips import get_app_token, get_game_id, get_top_clip_for_game
from downloader import download_clip
from video import make_vertical, burn_subtitles
from subtitles import transcribe_to_srt

def main():
    if not TWITCH_CLIENT_ID or not TWITCH_CLIENT_SECRET:
        raise RuntimeError("Missing TWITCH_CLIENT_ID / TWITCH_CLIENT_SECRET in .env")

    os.makedirs("videos/raw", exist_ok=True)
    os.makedirs("videos/processed", exist_ok=True)
    os.makedirs("logs", exist_ok=True)

    print("🔑 Twitch: getting app token...")
    token = get_app_token(TWITCH_CLIENT_ID, TWITCH_CLIENT_SECRET)

    print(f"🎮 Twitch: finding game id for '{GAME_NAME}'...")
    game_id = get_game_id(GAME_NAME, token)

    print(f"🔥 Twitch: selecting top clip (partner_only={PARTNER_ONLY}, lookback_hours={LOOKBACK_HOURS})...")
    clip = get_top_clip_for_game(
        game_id=game_id,
        token=token,
        lookback_hours=LOOKBACK_HOURS,
        partner_only=PARTNER_ONLY,
        fetch_first=50
    )

    print("🏆 Selected clip:")
    print(f"   Streamer: {clip['broadcaster_name']}")
    print(f"   Views:    {clip['views']}")
    print(f"   Title:    {clip['title']}")
    print(f"   URL:      {clip['url']}")

    print(f"⬇️ Downloading to {RAW_VIDEO} ...")
    download_clip(clip["url"], RAW_VIDEO)

    print(f"📐 Making vertical video {VERTICAL_VIDEO} ...")
    make_vertical(RAW_VIDEO, VERTICAL_VIDEO)

    print(f"📝 Generating subtitles ({WHISPER_MODEL}) -> {SUB_SRT} ...")
    transcribe_to_srt(VERTICAL_VIDEO, SUB_SRT, model_name=WHISPER_MODEL)

    print(f"🔥 Burning subtitles -> {FINAL_VIDEO} ...")
    burn_subtitles(VERTICAL_VIDEO, SUB_SRT, FINAL_VIDEO)

    caption = (clip["title"] or f"Top {GAME_NAME} clip") + f"\n\n{HASHTAGS}"
    print("✅ Done.")
    print(f"🎬 Final video: {FINAL_VIDEO}")
    print(f"🧾 Suggested caption:\n{caption}")

if __name__ == "__main__":
    main()
