# tests/test_extractors.py
from transcript.extractors.base import Segment, Transcript


def test_segment_creation():
    seg = Segment(start=1.5, end=3.0, text="hello")
    assert seg.start == 1.5
    assert seg.end == 3.0
    assert seg.text == "hello"


def test_transcript_full_text():
    segs = [
        Segment(0, 2, "first line"),
        Segment(2, 4, "second line"),
    ]
    t = Transcript(segments=segs, language="en", source_type="youtube")
    assert t.full_text == "first line\nsecond line"


def test_transcript_empty():
    t = Transcript(segments=[], language="auto", source_type="local")
    assert t.full_text == ""


def test_transcript_to_dict():
    segs = [Segment(0, 2, "hello")]
    t = Transcript(segments=segs, language="en", source_type="youtube")
    d = t.to_dict()
    assert d["language"] == "en"
    assert d["source_type"] == "youtube"
    assert len(d["segments"]) == 1
    assert d["segments"][0]["text"] == "hello"


def test_base_extractor_is_abstract():
    import pytest
    from transcript.extractors.base import BaseExtractor

    with pytest.raises(TypeError):
        BaseExtractor()
