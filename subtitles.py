from pathlib import Path
from faster_whisper import WhisperModel

def _format_srt_time(seconds: float) -> str:
    # SRT time format: HH:MM:SS,mmm
    ms = int(round(seconds * 1000))
    h = ms // 3600000
    ms %= 3600000
    m = ms // 60000
    ms %= 60000
    s = ms // 1000
    ms %= 1000
    return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"

def transcribe_to_srt(video_path: str, srt_out: str, model_name: str = "small") -> None:
    Path(srt_out).parent.mkdir(parents=True, exist_ok=True)

    # CPU-friendly defaults. If you have GPU later, you can change compute_type.
    model = WhisperModel(model_name, device="cpu", compute_type="int8")

    segments, _info = model.transcribe(video_path, vad_filter=True)

    lines = []
    idx = 1
    for seg in segments:
        start = _format_srt_time(seg.start)
        end = _format_srt_time(seg.end)
        text = (seg.text or "").strip()
        if not text:
            continue
        lines.append(str(idx))
        lines.append(f"{start} --> {end}")
        lines.append(text)
        lines.append("")  # blank line between entries
        idx += 1

    if idx == 1:
        raise RuntimeError("No speech detected; SRT would be empty.")

    Path(srt_out).write_text("\n".join(lines), encoding="utf-8")
