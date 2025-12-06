import pytest

from journal_digital import Corpus
from journal_digital.measure import SubtitleSegment


@pytest.fixture(scope="module")
def srt_file(tmpdir_factory):
    tmpdir = tmpdir_factory.mktemp("corpus")
    srt = tmpdir / "file.srt"
    with open(srt, "x", encoding="utf-8") as f:
        f.write(
            "1\n00:00:09,830 --> 00:00:10,730\nFirst line"
            "\n\n2\n00:00:10,769 --> 00:00:11,191\nSecond line"
        )
    return srt


def test_read_txt(srt_file):
    corpus = Corpus("txt")

    text = corpus._read_file(srt_file)

    assert text == "First line\n\nSecond line"


@pytest.mark.slow
def test_count_files():
    corpus = Corpus("txt")
    assert len(corpus) == 2544


@pytest.mark.slow
def test_count_files_iter():
    corpus = Corpus("txt")
    c = 0
    for file in corpus:
        c += 1
    assert c == 2544


@pytest.mark.slow
def test_no_empty_files():
    corpus = Corpus("txt")
    for file, text in corpus:
        assert len(text) > 0
        with open(file, "r", encoding="utf-8"):
            txt2 = corpus._read_file(file)
        assert text == txt2


# RED PHASE: SRT Mode Tests


@pytest.mark.xfail(strict=True, reason="Red Phase: SRT mode not implemented")
def test_read_srt_returns_list(srt_file):
    corpus = Corpus("txt")
    result = corpus.read_srt(srt_file)
    assert isinstance(result, list)
    assert len(result) == 2


@pytest.mark.xfail(strict=True, reason="Red Phase: SRT mode not implemented")
def test_read_srt_returns_subtitle_segments(srt_file):
    corpus = Corpus("txt")
    segments = corpus.read_srt(srt_file)
    assert all(isinstance(seg, SubtitleSegment) for seg in segments)
    first = segments[0]
    assert hasattr(first, "idx")
    assert hasattr(first, "start")
    assert hasattr(first, "end")
    assert hasattr(first, "text")
    assert hasattr(first, "num_words")
    assert hasattr(first, "duration_seconds")


@pytest.mark.xfail(strict=True, reason="Red Phase: SRT mode not implemented")
def test_read_srt_parses_first_segment(srt_file):
    corpus = Corpus("txt")
    segments = corpus.read_srt(srt_file)
    segment = segments[0]
    assert segment.idx == 1
    assert segment.start == "00:00:09,830"
    assert segment.end == "00:00:10,730"
    assert segment.text == "First line"


@pytest.mark.xfail(strict=True, reason="Red Phase: SRT mode not implemented")
def test_read_srt_parses_second_segment(srt_file):
    corpus = Corpus("txt")
    segments = corpus.read_srt(srt_file)
    segment = segments[1]
    assert segment.idx == 2
    assert segment.start == "00:00:10,769"
    assert segment.end == "00:00:11,191"
    assert segment.text == "Second line"


@pytest.mark.xfail(strict=True, reason="Red Phase: SRT mode not implemented")
def test_read_srt_no_duration_by_default(srt_file):
    corpus = Corpus("txt")
    segments = corpus.read_srt(srt_file)
    for segment in segments:
        assert segment.duration_seconds is None


@pytest.mark.xfail(strict=True, reason="Red Phase: SRT mode not implemented")
def test_read_srt_no_num_words_by_default(srt_file):
    corpus = Corpus("txt")
    segments = corpus.read_srt(srt_file)
    for segment in segments:
        assert segment.num_words is None


@pytest.mark.xfail(strict=True, reason="Red Phase: SRT mode not implemented")
def test_set_srt_mode_sets_reader():
    corpus = Corpus("txt")
    corpus.set_srt_mode()
    assert corpus._read_file == corpus.read_srt


@pytest.mark.slow
@pytest.mark.xfail(strict=True, reason="Red Phase: SRT mode not implemented")
def test_corpus_srt_mode_iteration():
    corpus = Corpus("srt")
    file, segments = next(iter(corpus))
    assert isinstance(segments, list)
    assert len(segments) > 0
    assert isinstance(segments[0], SubtitleSegment)
