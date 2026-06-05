# src/transcript/engine.py
from transcript.extractors.base import BaseExtractor


class TranscriptEngine:
    def __init__(self, extractors: list[BaseExtractor] | None = None):
        self.extractors = extractors or []

    def _find_extractor(self, input_path: str) -> BaseExtractor:
        for ext in self.extractors:
            if ext.supports(input_path):
                return ext
        raise ValueError(f"无法处理该输入: {input_path}")

    def _find_listable_extractor(self, input_path: str) -> BaseExtractor:
        for ext in self.extractors:
            if ext.supports(input_path) and hasattr(ext, "list_subtitles"):
                return ext
        raise ValueError(f"该输入不支持列出字幕: {input_path}")

    def get_transcript(
        self, input_path: str, lang: str = "auto", fmt: str = "txt"
    ) -> str:
        extractor = self._find_extractor(input_path)
        transcript = extractor.extract(input_path, lang=lang)

        from transcript.utils import to_txt, to_srt, to_json

        if fmt == "srt":
            return to_srt(transcript)
        elif fmt == "json":
            return to_json(transcript)
        return to_txt(transcript)

    def list_subtitles(self, input_path: str) -> list[dict]:
        extractor = self._find_listable_extractor(input_path)
        subtitles = extractor.list_subtitles(input_path)
        if not subtitles:
            raise ValueError(f"未找到可用字幕: {input_path}")
        return subtitles
