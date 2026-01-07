import os
import subprocess
from pathlib import Path

def _run(cmd: list[str]):
    subprocess.run(cmd, check=True)

def process_video(input_path: str, output_path: str):
    """
    Creates a TikTok-ready vertical video.
    - center-crop to 9:16
    - scales to 1080x1920
    - keeps audio
    """
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)

    # Simple + reliable: center crop to 9:16 regardless of source
    # Crop width based on height to get 9:16:
    #   target_w = h * 9 / 16
    vf = "crop='ih*9/16:ih:(iw-ih*9/16)/2:0',scale=1080:1920"

    cmd = [
        "ffmpeg", "-y",
        "-i", input_path,
        "-vf", vf,
        "-c:v", "libx264", "-preset", "veryfast", "-crf", "20",
        "-c:a", "aac", "-b:a", "128k",
        "-movflags", "+faststart",
        output_path
    ]
    _run(cmd)
