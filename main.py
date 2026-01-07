from config import (
    TWITCH_CLIENT_ID,
    TWITCH_CLIENT_SECRET,
    GAME_NAME,
    LOOKBACK_HOURS,
    FETCH_FIRST,
    MIN_CLIPS_PER_CREATOR,
    CREATOR_CLIP_BONUS,
    RAW_VIDEO,
    FINAL_VIDEO,
)

from twitch_clips import (
    get_app_token,
    get_game_id,
    get_top_clip_for_game,
)

from downloader import download_clip

def main():
    print("🔑 Authenticating with Twitch")
    token = get_app_token(TWITCH_CLIENT_ID, TWITCH_CLIENT_SECRET)

    print(f"🎮 Resolving game: {GAME_NAME}")
    game_id = get_game_id(GAME_NAME, token)

    print("📈 Selecting trending creator clip")
    clip = get_top_clip_for_game(
        game_id=game_id,
        token=token,
        lookback_hours=LOOKBACK_HOURS,
        fetch_first=FETCH_FIRST,
        partner_only=True,
        english_only=True,
        min_clips_per_creator=MIN_CLIPS_PER_CREATOR,
        creator_clip_bonus=CREATOR_CLIP_BONUS,
    )

    print(f"🏆 Selected: {clip['broadcaster_name']} ({clip['views']} views)")
    print(f"🔗 {clip['url']}")

    download_clip(clip["url"], RAW_VIDEO)

    print("✅ Clip downloaded — continuing with existing pipeline")

if __name__ == "__main__":
    main()
