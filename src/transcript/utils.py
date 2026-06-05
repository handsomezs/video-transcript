# src/transcript/utils.py
import json
from transcript.extractors.base import Transcript


def _format_timestamp(seconds: float) -> str:
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    millis = int((seconds % 1) * 1000)
    return f"{hours:02d}:{minutes:02d}:{secs:02d},{millis:03d}"


def to_txt(transcript: Transcript) -> str:
    return "\n".join(s.text for s in transcript.segments)


def to_srt(transcript: Transcript) -> str:
    blocks = []
    for i, seg in enumerate(transcript.segments, 1):
        start_ts = _format_timestamp(seg.start)
        end_ts = _format_timestamp(seg.end)
        blocks.append(f"{i}\n{start_ts} --> {end_ts}\n{seg.text}")
    return "\n\n".join(blocks) + ("\n" if blocks else "")


def to_json(transcript: Transcript) -> str:
    return json.dumps(transcript.to_dict(), ensure_ascii=False, indent=2)
