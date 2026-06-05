# tests/test_engine.py
import pytest
from transcript.engine import TranscriptEngine
from transcript.extractors.base import Transcript, Segment


class FakeExtractor:
    """Fake extractor for testing engine dispatch."""
    def __init__(self, name, should_support=True):
        self.name = name
        self.should_support = should_support
        self.last_input = None

    def supports(self, input_path):
        return self.should_support

    def extract(self, input_path, lang="auto"):
        self.last_input = input_path
        return Transcript(
            segments=[Segment(0, 1, f"from {self.name}")],
            language=lang,
            source_type=self.name,
        )


class TestTranscriptEngine:
    def test_init_registers_extractors(self):
        engine = TranscriptEngine(extractors=[])
        assert engine.extractors == []

    def test_dispatch_to_correct_extractor(self):
        yt = FakeExtractor("youtube")
        bi = FakeExtractor("bilibili")
        engine = TranscriptEngine(extractors=[yt, bi])
        result = engine.get_transcript("https://youtube.com/watch?v=abc")
        assert result == "from youtube"

    def test_no_suitable_extractor_raises(self):
        bad = FakeExtractor("only_one", should_support=False)
        engine = TranscriptEngine(extractors=[bad])
        with pytest.raises(ValueError, match="无法处理该输入"):
            engine.get_transcript("some-random-string")

    def test_list_subtitles(self):
        class ListExtractor(FakeExtractor):
            def list_subtitles(self, input_path):
                return [{"language": "zh-Hans", "type": "auto"}]

        engine = TranscriptEngine(extractors=[ListExtractor("yt")])
        result = engine.list_subtitles("https://youtube.com/watch?v=abc")
        assert len(result) == 1
        assert result[0]["language"] == "zh-Hans"

    def test_list_subtitles_empty_raises(self):
        class NoListExtractor(FakeExtractor):
            def list_subtitles(self, input_path):
                return []

        engine = TranscriptEngine(extractors=[NoListExtractor("yt")])
        with pytest.raises(ValueError, match="未找到可用字幕"):
            engine.list_subtitles("https://youtube.com/watch?v=abc")

    def test_get_transcript_srt_format(self):
        yt = FakeExtractor("youtube")
        engine = TranscriptEngine(extractors=[yt])
        result = engine.get_transcript("https://youtube.com/watch?v=abc", fmt="srt")
        assert "00:00:00,000" in result
        assert "from youtube" in result

    def test_get_transcript_json_format(self):
        yt = FakeExtractor("youtube")
        engine = TranscriptEngine(extractors=[yt])
        result = engine.get_transcript("https://youtube.com/watch?v=abc", fmt="json")
        assert '"source_type"' in result
