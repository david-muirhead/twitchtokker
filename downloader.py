import subprocess
from pathlib import Path

def download_clip(url, output):
    Path(output).parent.mkdir(parents=True, exist_ok=True)
    subprocess.run(["yt-dlp", "-f", "mp4/best", "-o", output, url], check=True)
