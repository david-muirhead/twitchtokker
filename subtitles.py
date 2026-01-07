from pathlib import Path
from faster_whisper import WhisperModel

def _fmt(t):
    ms = int(t * 1000)
    h, ms = divmod(ms, 3600000)
    m, ms = divmod(ms, 60000)
    s, ms = divmod(ms, 1000)
    return f"{h:02}:{m:02}:{s:02},{ms:03}"

def transcribe_to_srt(video, out, model="small"):
    Path(out).parent.mkdir(parents=True, exist_ok=True)
    model = WhisperModel(model, device="cpu", compute_type="int8")
    segments, _ = model.transcribe(video)

    lines = []
    i = 1
    for seg in segments:
        if seg.text.strip():
            lines += [
                str(i),
                f"{_fmt(seg.start)} --> {_fmt(seg.end)}",
                seg.text.strip(),
                ""
            ]
            i += 1

    Path(out).write_text("\n".join(lines), encoding="utf-8")
