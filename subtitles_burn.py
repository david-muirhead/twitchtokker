import subprocess
from pathlib import Path

def burn_subtitles(video_path: str, srt_path: str, output_path: str):
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)

    # Burn subtitles into the video with readable styling
    vf = f"subtitles={srt_path}:force_style='Fontsize=28,Outline=2,Shadow=1,MarginV=90'"

    cmd = [
        "ffmpeg", "-y",
        "-i", video_path,
        "-vf", vf,
        "-c:v", "libx264", "-preset", "veryfast", "-crf", "20",
        "-c:a", "aac", "-b:a", "128k",
        "-movflags", "+faststart",
        output_path
    ]
    subprocess.run(cmd, check=True)
