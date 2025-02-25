import pytest

from corpus import Corpus


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


def test_count_files():
    corpus = Corpus("txt")
    assert len(corpus) == 2564


def test_count_files_iter():
    corpus = Corpus("txt")
    c = 0
    for file in corpus:
        c += 1
    assert c == 2564


def test_no_empty_files():
    corpus = Corpus("txt")
    for file, text in corpus:
        assert len(text) > 0
        with open(file, "r", encoding="utf-8") as f:
            txt2 = corpus._read_file(file)
        assert text == txt2
