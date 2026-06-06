# src/transcript/extractors/bilibili.py
import re
import tempfile
import os
from transcript.extractors.base import BaseExtractor, Transcript, Segment


class BilibiliExtractor(BaseExtractor):
    BILIBILI_PATTERN = re.compile(
        r"(?:https?://)?(?:www\.)?bilibili\.com/video/([\w]+)"
    )
    B23_PATTERN = re.compile(r"(?:https?://)?b23\.tv/([\w]+)")

    def supports(self, input_path: str) -> bool:
        return bool(
            self.BILIBILI_PATTERN.search(input_path)
            or self.B23_PATTERN.search(input_path)
        )

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
                        "type": "auto" if lang in auto_subs else "manual",
                        "ext": track.get("ext", "vtt"),
                    })
            return result

    def extract(self, input_path: str, lang: str = "auto") -> Transcript:
        import yt_dlp

        with tempfile.TemporaryDirectory() as tmpdir:
            langs = [lang] if lang != "auto" else ["zh-Hans", "zh", "en"]
            opts = {
                "quiet": True,
                "no_warnings": True,
                "skip_download": True,
                "writesubtitles": True,
                "writeautomaticsub": True,
                "subtitleslangs": langs,
                "subtitlesformat": "srt",
                "outtmpl": f"{tmpdir}/%(id)s.%(ext)s",
            }
            with yt_dlp.YoutubeDL(opts) as ydl:
                info = ydl.extract_info(input_path, download=True)
                video_id = info["id"]

            srt_file = self._find_srt(tmpdir, video_id)
            if not srt_file:
                raise ValueError("该B站视频暂无可用字幕")

            return self._parse_srt(srt_file)

    def _find_srt(self, tmpdir: str, video_id: str) -> str | None:
        for f in os.listdir(tmpdir):
            if video_id in f and f.endswith((".srt", ".vtt")):
                return os.path.join(tmpdir, f)
        return None

    def _parse_srt(self, filepath: str) -> Transcript:
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()

        blocks = re.split(r"\n\s*\n", content.strip())
        srt_pattern = re.compile(
            r"(?:\d+\n)?(\d{1,2}:\d{2}:\d{2}[.,]\d{1,3})\s*-->\s*(\d{1,2}:\d{2}:\d{2}[.,]\d{1,3})\n(.+)",
            re.DOTALL,
        )
        segments = []

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

        return Transcript(segments=segments, language=language, source_type="bilibili")

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
