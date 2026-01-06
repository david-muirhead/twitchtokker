import subprocess
from pathlib import Path

def run(cmd: list[str]) -> None:
    subprocess.run(cmd, check=True)

def ensure_parent(path: str) -> None:
    Path(path).parent.mkdir(parents=True, exist_ok=True)

def make_vertical(input_video: str, output_video: str) -> None:
    """
    Scale/crop to 1080x1920 for TikTok.
    """
    ensure_parent(output_video)
    cmd = [
        "ffmpeg", "-y",
        "-i", input_video,
        "-vf", "scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920",
        "-c:v", "libx264",
        "-preset", "fast",
        "-crf", "23",
        "-pix_fmt", "yuv420p",
        "-c:a", "aac",
        "-b:a", "128k",
        "-movflags", "+faststart",
        output_video
    ]
    run(cmd)

def burn_subtitles(input_video: str, srt_path: str, output_video: str) -> None:
    """
    Burn subtitles into the video (hard subs).
    """
    ensure_parent(output_video)

    # Force a readable style
    # NOTE: ffmpeg subtitles filter needs path accessible inside runtime.
    style = "Fontsize=42,PrimaryColour=&HFFFFFF&,OutlineColour=&H000000&,BorderStyle=1,Outline=2,Shadow=1"

    cmd = [
        "ffmpeg", "-y",
        "-i", input_video,
        "-vf", f"subtitles={srt_path}:force_style='{style}'",
        "-c:v", "libx264",
        "-preset", "fast",
        "-crf", "23",
        "-pix_fmt", "yuv420p",
        "-c:a", "copy",
        "-movflags", "+faststart",
        output_video
    ]
    run(cmd)
