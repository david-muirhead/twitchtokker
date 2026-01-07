import subprocess
from pathlib import Path

def run(cmd):
    subprocess.run(cmd, check=True)

def make_vertical(inp, out):
    Path(out).parent.mkdir(parents=True, exist_ok=True)
    run([
        "ffmpeg","-y","-i",inp,
        "-vf","scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920",
        "-c:v","libx264","-crf","23","-preset","fast",
        "-c:a","aac","-b:a","128k",
        out
    ])

def burn_subtitles(inp, srt, out):
    style = "Fontsize=42,Outline=2,Shadow=1"
    run([
        "ffmpeg","-y","-i",inp,
        "-vf",f"subtitles={srt}:force_style='{style}'",
        "-c:v","libx264","-crf","23",
        "-c:a","copy",
        out
    ])
