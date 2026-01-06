import subprocess
from pathlib import Path

def download_clip(url: str, output_path: str) -> None:
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)

    # yt-dlp is the most reliable option for Twitch clip URLs
    cmd = [
        "yt-dlp",
        "-f", "mp4/best",
        "-o", output_path,
        url
    ]
    subprocess.run(cmd, check=True)
