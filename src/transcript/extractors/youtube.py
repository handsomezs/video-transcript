# src/transcript/extractors/youtube.py
import re
import tempfile
import os
from transcript.extractors.base import BaseExtractor, Transcript, Segment


class YouTubeExtractor(BaseExtractor):
    YOUTUBE_PATTERN = re.compile(
        r"(?:https?://)?(?:www\.)?(?:youtube\.com/watch\?v=|youtu\.be/)([\w-]+)"
    )

    def supports(self, input_path: str) -> bool:
        return bool(self.YOUTUBE_PATTERN.search(input_path))

    def list_subtitles(self, input_path: str) -> list[dict]:
        import yt_dlp

        opts = {"quiet": True, "no_warnings": True, "skip_download": True}
        with yt_dlp.YoutubeDL(opts) as ydl:
            info = ydl.extract_info(input_path, download=False)
            subs = info.get("subtitles", {})
            auto_subs = info.get("automatic_captions", {})
            result = []
            for lang, tracks in {**subs, **auto_subs}.items():
                for track in tracks:
                    result.append({
                        "language": lang,
                        "type": "manual" if lang in subs else "auto",
                        "ext": track.get("ext", "vtt"),
                    })
            return result

    def extract(self, input_path: str, lang: str = "auto") -> Transcript:
        import yt_dlp

        with tempfile.TemporaryDirectory() as tmpdir:
            opts = {
                "quiet": True,
                "no_warnings": True,
                "skip_download": True,
                "writesubtitles": True,
                "writeautomaticsub": True,
                "subtitleslangs": [lang] if lang != "auto" else ["zh-Hans", "zh", "en"],
                "subtitlesformat": "srt",
                "outtmpl": f"{tmpdir}/%(id)s.%(ext)s",
            }
            with yt_dlp.YoutubeDL(opts) as ydl:
                info = ydl.extract_info(input_path, download=True)
                video_id = info["id"]

            srt_file = self._find_srt(tmpdir, video_id)
            if srt_file:
                return self._parse_srt(srt_file, source_type="youtube")

            raise ValueError("无法获取该视频的字幕，请尝试其他视频或使用本地转写")

    def _find_srt(self, tmpdir: str, video_id: str) -> str | None:
        for f in os.listdir(tmpdir):
            if f.startswith(video_id) and f.endswith((".srt", ".vtt")):
                return os.path.join(tmpdir, f)
        return None

    def _parse_srt(self, filepath: str, source_type: str) -> Transcript:
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()

        blocks = re.split(r"\n\s*\n", content.strip())
        segments = []
        srt_pattern = re.compile(
            r"(?:\d+\n)?(\d{1,2}:\d{2}:\d{2}[.,]\d{1,3})\s*-->\s*(\d{1,2}:\d{2}:\d{2}[.,]\d{1,3})\n(.+)",
            re.DOTALL,
        )

        for block in blocks:
            block = block.strip()
            if not block:
                continue
            m = srt_pattern.search(block)
            if m:
                start = self._ts_to_seconds(m.group(1))
                end = self._ts_to_seconds(m.group(2))
                text = m.group(3).strip().replace("\n", " ")
                if text:
                    segments.append(Segment(start=start, end=end, text=text))

        full = "".join(s.text for s in segments)
        has_cjk = any("一" <= c <= "鿿" for c in full)
        language = "zh" if has_cjk else "en"

        return Transcript(segments=segments, language=language, source_type=source_type)

    @staticmethod
    def _ts_to_seconds(ts: str) -> float:
        ts = ts.replace(",", ".")
        parts = ts.split(":")
        if len(parts) == 3:
            h, m, s = parts
            return int(h) * 3600 + int(m) * 60 + float(s)
        elif len(parts) == 2:
            m, s = parts
            return int(m) * 60 + float(s)
        return float(ts)
