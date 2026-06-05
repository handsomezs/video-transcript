# tests/test_utils.py
from transcript.extractors.base import Segment, Transcript
from transcript.utils import to_txt, to_srt, to_json


def make_transcript():
    return Transcript(
        segments=[
            Segment(0.0, 2.5, "Hello world"),
            Segment(2.5, 5.0, "This is a test"),
        ],
        language="en",
        source_type="local",
    )


def test_to_txt():
    result = to_txt(make_transcript())
    assert result == "Hello world\nThis is a test"


def test_to_srt():
    result = to_srt(make_transcript())
    expected = (
        "1\n"
        "00:00:00,000 --> 00:00:02,500\n"
        "Hello world\n"
        "\n"
        "2\n"
        "00:00:02,500 --> 00:00:05,000\n"
        "This is a test\n"
    )
    assert result == expected


def test_to_json():
    result = to_json(make_transcript())
    assert '"segments"' in result
    assert '"language"' in result
    assert '"source_type"' in result


def test_to_srt_empty():
    t = Transcript(segments=[], language="en", source_type="local")
    assert to_srt(t) == ""


def test_to_txt_empty():
    t = Transcript(segments=[], language="en", source_type="local")
    assert to_txt(t) == ""
