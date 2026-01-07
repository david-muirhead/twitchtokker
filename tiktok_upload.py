import os
import subprocess
from pathlib import Path

def upload_to_tiktok(video, caption):
    cookies = os.getenv("TIKTOK_COOKIES_TXT", "cookies/cookies.txt")
    if not Path(cookies).exists():
        raise RuntimeError("cookies.txt missing")

    subprocess.run(
        ["tiktok-uploader", "-video", video, "-description", caption, "-cookies", cookies],
        check=True
    )
