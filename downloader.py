from pathlib import Path
import os
import subprocess

def download_clip(url: str, output_path: str = None, output: str = None) -> None:
    """
    Backward-compatible downloader.

    Supports:
      - download_clip(url, output_path)
      - download_clip(url, output)
      - download_clip(url=url, output_path="...")
      - download_clip(url=url, output="...")
    """
    if output_path is None:
        output_path = output
    if not output_path:
        raise TypeError("download_clip() missing required argument: 'output_path'")

    Path(output_path).parent.mkdir(parents=True, exist_ok=True)

    cmd = [
        "yt-dlp",
        "-f", "best[ext=mp4]/best",
        "-o", output_path,
        url,
    ]

    env = os.environ.copy()
    env["PYTHONUNBUFFERED"] = "1"

    print(f"⬇️ Downloading clip: {url}")
    subprocess.run(cmd, check=True, env=env)
    print(f"✅ Downloaded to: {output_path}")
