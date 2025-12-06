import pytest

from journal_digital import Corpus
from journal_digital.corpus import SubtitleSegment


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


def test_read_srt_returns_list(srt_file):
    corpus = Corpus("txt")
    result = corpus.read_srt(srt_file)
    assert isinstance(result, list)
    assert len(result) == 2


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


def test_read_srt_parses_first_segment(srt_file):
    corpus = Corpus("txt")
    segments = corpus.read_srt(srt_file)
    segment = segments[0]
    assert segment.idx == 1
    assert segment.start == "00:00:09,830"
    assert segment.end == "00:00:10,730"
    assert segment.text == "First line"


def test_read_srt_parses_second_segment(srt_file):
    corpus = Corpus("txt")
    segments = corpus.read_srt(srt_file)
    segment = segments[1]
    assert segment.idx == 2
    assert segment.start == "00:00:10,769"
    assert segment.end == "00:00:11,191"
    assert segment.text == "Second line"


def test_read_srt_no_duration_by_default(srt_file):
    corpus = Corpus("txt")
    segments = corpus.read_srt(srt_file)
    for segment in segments:
        assert segment.duration_seconds is None


def test_read_srt_no_num_words_by_default(srt_file):
    corpus = Corpus("txt")
    segments = corpus.read_srt(srt_file)
    for segment in segments:
        assert segment.num_words is None


def test_set_srt_mode_sets_reader():
    corpus = Corpus("txt")
    corpus.set_srt_mode()
    assert corpus._read_file == corpus.read_srt


def test_read_srt_validates_index_sequence(srt_file):
    corpus = Corpus("txt")
    segments = corpus.read_srt(srt_file)
    # Verify indices start at 1 and increment
    assert segments[0].idx == 1
    assert segments[1].idx == 2


def test_read_srt_rejects_non_integer_index(tmpdir):
    corpus = Corpus("txt")
    srt = tmpdir / "bad.srt"
    with open(srt, "w", encoding="utf-8") as f:
        f.write("NOT_A_NUMBER\n00:00:09,830 --> 00:00:10,730\nText")
    with pytest.raises(
        ValueError, match="index 'NOT_A_NUMBER' is not an integer"
    ):
        corpus.read_srt(srt)


def test_read_srt_rejects_wrong_index_sequence(tmpdir):
    corpus = Corpus("txt")
    srt = tmpdir / "bad.srt"
    with open(srt, "w", encoding="utf-8") as f:
        f.write("2\n00:00:09,830 --> 00:00:10,730\nText")
    with pytest.raises(ValueError, match="expected index 1, got 2"):
        corpus.read_srt(srt)


def test_read_srt_rejects_malformed_timestamp(tmpdir):
    corpus = Corpus("txt")
    srt = tmpdir / "bad.srt"
    with open(srt, "w", encoding="utf-8") as f:
        f.write("1\nBAD_TIMESTAMP\nText")
    with pytest.raises(
        ValueError, match="malformed timestamp 'BAD_TIMESTAMP'"
    ):
        corpus.read_srt(srt)


def test_read_srt_validates_timestamp_format(srt_file):
    corpus = Corpus("txt")
    segments = corpus.read_srt(srt_file)
    # Verify timestamps match expected format HH:MM:SS,mmm
    import re

    time_pattern = re.compile(r"\d{2}:\d{2}:\d{2},\d{3}")
    for seg in segments:
        assert time_pattern.fullmatch(seg.start)
        assert time_pattern.fullmatch(seg.end)


# Optional calculations tests


def test_corpus_init_with_calculate_num_words():
    corpus = Corpus(mode="txt", calculate_num_words=True)
    assert corpus._calculate_num_words is True


def test_corpus_init_with_calculate_duration():
    corpus = Corpus(mode="txt", calculate_duration=True)
    assert corpus._calculate_duration is True


def test_corpus_init_defaults_to_false():
    corpus = Corpus(mode="txt")
    assert corpus._calculate_num_words is False
    assert corpus._calculate_duration is False


def test_set_calculate_words_enable():
    corpus = Corpus(mode="txt")
    corpus.set_calculate_words(True)
    assert corpus._calculate_num_words is True


def test_set_calculate_words_disable():
    corpus = Corpus(mode="txt", calculate_num_words=True)
    corpus.set_calculate_words(False)
    assert corpus._calculate_num_words is False


def test_set_calculate_words_default_true():
    corpus = Corpus(mode="txt")
    corpus.set_calculate_words()
    assert corpus._calculate_num_words is True


def test_set_calculate_duration_enable():
    corpus = Corpus(mode="txt")
    corpus.set_calculate_duration(True)
    assert corpus._calculate_duration is True


def test_set_calculate_duration_disable():
    corpus = Corpus(mode="txt", calculate_duration=True)
    corpus.set_calculate_duration(False)
    assert corpus._calculate_duration is False


def test_set_calculate_duration_default_true():
    corpus = Corpus(mode="txt")
    corpus.set_calculate_duration()
    assert corpus._calculate_duration is True


def test_read_srt_calculates_num_words_when_enabled(srt_file):
    corpus = Corpus(mode="txt", calculate_num_words=True)
    segments = corpus.read_srt(srt_file)
    # "First line" = 2 words, "Second line" = 2 words
    assert segments[0].num_words == 2
    assert segments[1].num_words == 2


def test_read_srt_num_words_none_when_disabled(srt_file):
    corpus = Corpus(mode="txt", calculate_num_words=False)
    segments = corpus.read_srt(srt_file)
    assert segments[0].num_words is None
    assert segments[1].num_words is None


def test_read_srt_calculates_duration_when_enabled(srt_file):
    corpus = Corpus(mode="txt", calculate_duration=True)
    segments = corpus.read_srt(srt_file)
    # First: 00:00:09,830 -> 00:00:10,730 = 900 milliseconds
    # Second: 00:00:10,769 -> 00:00:11,191 = 422 milliseconds
    assert segments[0].duration_seconds == 900
    assert segments[1].duration_seconds == 422


def test_read_srt_duration_none_when_disabled(srt_file):
    corpus = Corpus(mode="txt", calculate_duration=False)
    segments = corpus.read_srt(srt_file)
    assert segments[0].duration_seconds is None
    assert segments[1].duration_seconds is None


def test_read_srt_calculates_both_when_enabled(srt_file):
    corpus = Corpus(
        mode="txt", calculate_num_words=True, calculate_duration=True
    )
    segments = corpus.read_srt(srt_file)
    assert segments[0].num_words is not None
    assert segments[0].duration_seconds is not None
    assert segments[1].num_words is not None
    assert segments[1].duration_seconds is not None


@pytest.mark.slow
def test_corpus_srt_mode_iteration():
    corpus = Corpus("srt")
    _, segments = next(iter(corpus))
    assert isinstance(segments, list)
    assert len(segments) > 0
    assert isinstance(segments[0], SubtitleSegment)


@pytest.mark.slow
def test_corpus_srt_mode_all_files():
    corpus = Corpus("srt")
    count = 0
    for _, segments in corpus:
        count += 1
        assert isinstance(segments, list)
        assert all(isinstance(seg, SubtitleSegment) for seg in segments)
    assert count == 2544
