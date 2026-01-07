import inspect

def require(func, name: str, params: list[str]):
    sig = inspect.signature(func)
    missing = [p for p in params if p not in sig.parameters]
    if missing:
        raise SystemExit(f"❌ {name}{sig} missing params: {missing}")
    print(f"✅ {name}{sig}")

def main():
    from twitch_clips import get_app_token, get_game_id, get_top_clip_for_game
    from downloader import download_clip

    require(get_app_token, "get_app_token", ["client_id", "client_secret"])
    require(get_game_id, "get_game_id", ["game_name", "token"])
    require(
        get_top_clip_for_game,
        "get_top_clip_for_game",
        ["game_id", "token", "lookback_hours", "fetch_first"],
    )
    require(download_clip, "download_clip", ["url", "output_path"])

    print("\n🎉 Sanity check passed.")

if __name__ == "__main__":
    main()
