import os

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

from twitch_clips import get_app_token, get_game_id, get_top_clip_for_game
from downloader import download_clip


def _try_import_processing():
    """
    Tries multiple module/function names so this works with your existing repo
    without you having to perfectly match my earlier naming.
    """
    candidates = [
        ("video_processing", "process_video"),
        ("video_process", "process_video"),
        ("processing", "process_video"),
        ("video", "process_video"),
        ("video_processing", "make_vertical_video"),
        ("processing", "make_vertical_video"),
    ]
    for mod, fn in candidates:
        try:
            m = __import__(mod, fromlist=[fn])
            return getattr(m, fn), f"{mod}.{fn}"
        except Exception:
            pass
    return None, None


def _try_import_subtitles():
    candidates = [
        ("subtitles", "transcribe_to_srt"),
        ("subtitle", "transcribe_to_srt"),
        ("whisper_srt", "transcribe_to_srt"),
    ]
    for mod, fn in candidates:
        try:
            m = __import__(mod, fromlist=[fn])
            return getattr(m, fn), f"{mod}.{fn}"
        except Exception:
            pass
    return None, None


def _try_import_burn():
        ("subtitles_burn", "burn_subtitles"),
        ("subtitles", "burn_subtitles"),
        ("subtitle", "burn_subtitles"),
        ("video_processing", "burn_subtitles"),
        ("processing", "burn_subtitles"),
    ]
    for mod, fn in candidates:
        try:
            m = __import__(mod, fromlist=[fn])
            return getattr(m, fn), f"{mod}.{fn}"
        except Exception:
            pass
    return None, None


def _try_import_upload():
    candidates = [
        ("tiktok_upload", "upload_video_tiktok"),
        ("upload", "upload_video_tiktok"),
        ("uploader", "upload_video_tiktok"),
    ]
    for mod, fn in candidates:
        try:
            m = __import__(mod, fromlist=[fn])
            return getattr(m, fn), f"{mod}.{fn}"
        except Exception:
            pass
    return None, None


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

    print(f"🏆 Selected: {clip.get('broadcaster_name')} ({clip.get('views')} views)")
    print(f"🔗 {clip.get('url')}")
    if clip.get("title"):
        print(f"📝 Title: {clip['title']}")

    print(f"⬇️ Downloading clip -> {RAW_VIDEO}")
    download_clip(url=clip["url"], output_path=RAW_VIDEO)
    print("✅ Clip downloaded")

    # ---------- VIDEO PROCESSING ----------
    process_fn, process_name = _try_import_processing()
    if process_fn:
        print(f"🎬 Processing video using {process_name}: {RAW_VIDEO} -> {FINAL_VIDEO}")
        # Try common signatures
        try:
            process_fn(RAW_VIDEO, FINAL_VIDEO)
        except TypeError:
            # some versions accept keyword args
            process_fn(input_path=RAW_VIDEO, output_path=FINAL_VIDEO)
        print("✅ Video processing complete")
    else:
        print("⚠️ No video processing function found. Skipping processing step.")
        print(f"   (Expected modules like video_processing.py / processing.py)")

    # ---------- SUBTITLES ----------
    # We’ll create an SRT alongside the final video path
    srt_path = os.path.splitext(FINAL_VIDEO)[0] + ".srt"
    transcribe_fn, transcribe_name = _try_import_subtitles()
    burn_fn, burn_name = _try_import_burn()

    if transcribe_fn:
        model = os.getenv("WHISPER_MODEL", "small")
        print(f"🗣️ Creating subtitles using {transcribe_name} (model={model}) -> {srt_path}")
        # Handle both parameter naming styles safely
        try:
            transcribe_fn(FINAL_VIDEO, srt_path, model)
        except TypeError:
            try:
                transcribe_fn(video_path=FINAL_VIDEO, srt_path=srt_path, model_name=model)
            except TypeError:
                transcribe_fn(video_path=FINAL_VIDEO, srt_path=srt_path, model=model)
        print("✅ Subtitles created")
    else:
        print("⚠️ No subtitle transcription function found. Skipping subtitles step.")

    if burn_fn and os.path.exists(srt_path):
        burned_path = os.path.splitext(FINAL_VIDEO)[0] + "_subbed.mp4"
        print(f"🔥 Burning subtitles using {burn_name}: {FINAL_VIDEO} + {srt_path} -> {burned_path}")
        try:
            burn_fn(FINAL_VIDEO, srt_path, burned_path)
        except TypeError:
            burn_fn(video_path=FINAL_VIDEO, srt_path=srt_path, output_path=burned_path)
        FINAL_TO_UPLOAD = burned_path
        print("✅ Subtitles burned into video")
    else:
        FINAL_TO_UPLOAD = FINAL_VIDEO
        if not burn_fn:
            print("⚠️ No burn_subtitles() found. Uploading without burned-in captions.")
        elif not os.path.exists(srt_path):
            print("⚠️ SRT not found (no subtitles generated). Uploading without burned-in captions.")

    # ---------- UPLOAD ----------
    upload_enabled = os.getenv("UPLOAD_ENABLED", "true").lower() in ("1", "true", "yes")
    upload_fn, upload_name = _try_import_upload()

    caption = clip.get("title") or f"{GAME_NAME} clip"
    if upload_enabled and upload_fn:
        print(f"🚀 Uploading to TikTok using {upload_name}...")
        try:
            upload_fn(FINAL_TO_UPLOAD, caption)
        except TypeError:
            # Some upload functions accept cookies file or extra args
            cookies_file = os.getenv("TIKTOK_COOKIES", "cookies.json")
            upload_fn(FINAL_TO_UPLOAD, caption, cookies_file)
        print("✅ Upload finished (if no errors above)")
    else:
        if not upload_enabled:
            print("⏸️ UPLOAD_ENABLED=false -> skipping upload step.")
        else:
            print("⚠️ No upload function found. Skipping upload step.")
            print("   (Expected tiktok_upload.py with upload_video_tiktok())")

    print("🎉 Done.")


if __name__ == "__main__":
    main()
