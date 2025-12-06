import pytest

from journal_digital.corpus import Corpus
from journal_digital.SubtitleSegment import SubtitleSegment


def test_parse_srt_basic(tmpdir):
    srt = tmpdir / "test.srt"
    with open(srt, "w", encoding="utf-8") as f:
        f.write("1\n00:00:09,830 --> 00:00:10,730\nFirst line\n\n")
        f.write("2\n00:00:10,769 --> 00:00:11,191\nSecond line\n\n")

    corpus = Corpus(
        mode="srt", calculate_num_words=True, calculate_duration=True
    )
    segments = corpus.read_srt(srt)
    assert len(segments) == 2

    # First segment
    assert segments[0].idx == 1
    assert segments[0].start == "00:00:09,830"
    assert segments[0].end == "00:00:10,730"
    assert segments[0].text == "First line"
    assert segments[0].num_words == 2
    assert segments[0].duration_seconds == 900  # 10730 - 9830 = 900ms

    # Second segment
    assert segments[1].idx == 2
    assert segments[1].start == "00:00:10,769"
    assert segments[1].end == "00:00:11,191"
    assert segments[1].text == "Second line"
    assert segments[1].num_words == 2
    assert segments[1].duration_seconds == 422  # 11191 - 10769 = 422ms


def test_parse_srt_word_count(tmpdir):
    srt = tmpdir / "test.srt"
    with open(srt, "w", encoding="utf-8") as f:
        f.write("1\n00:00:00,000 --> 00:00:01,000\nOne\n\n")
        f.write("2\n00:00:01,000 --> 00:00:02,000\nOne Two Three\n\n")
        f.write("3\n00:00:02,000 --> 00:00:03,000\n\n\n")  # Empty text

    corpus = Corpus(
        mode="srt", calculate_num_words=True, calculate_duration=True
    )
    segments = corpus.read_srt(srt)
    assert segments[0].num_words == 1
    assert segments[1].num_words == 3
    assert segments[2].num_words == 0


def test_subtitle_segment_creation():
    seg = SubtitleSegment(
        idx=1,
        start="00:00:09,830",
        end="00:00:10,730",
        text="Test text",
        num_words=2,
        duration_seconds=900,
    )
    assert seg.idx == 1
    assert seg.start == "00:00:09,830"
    assert seg.end == "00:00:10,730"
    assert seg.text == "Test text"
    assert seg.num_words == 2
    assert seg.duration_seconds == 900


def test_subtitle_segment_immutable():
    seg = SubtitleSegment(1, "00:00:00,000", "00:00:01,000", "Text", 1, 1000)
    # Namedtuples are immutable - should raise AttributeError
    with pytest.raises(AttributeError):
        seg.idx = 2


def test_subtitle_segment_fields_exist():
    assert hasattr(SubtitleSegment, "_fields")
    assert SubtitleSegment._fields == (
        "idx",
        "start",
        "end",
        "text",
        "num_words",
        "duration_seconds",
    )
