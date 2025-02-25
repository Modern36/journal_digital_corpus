import pytest


@pytest.fixture(scope="module")
def srt_file(tmp_path):
    srt = tmp_path / "file.srt"
    with open(srt, "x", encoding="utf-8") as f:
        f.write(
            "1\n00:00:09,830 --> 00:00:10,730\nFirst line"
            "\n\n2\n00:00:10,769 --> 00:00:11,191\nSecond line\n"
        )
    return srt


@pytest.mark.xfail(strict=True, reason="Red phase")
def test_read_txt(srt_file):
    corpus = Corpus("txt")

    with open(srt_file) as f:
        text = corpus._read_file(f)

    assert text == "First line\n\nSecond line"
