import pytest

from journal_digital import Corpus


@pytest.mark.xfail(strict=True, reason="Red Phase")
def test_count_intertitle():
    corpus = Corpus("txt", texts_to_include="intertitles")
    c = 0
    for file in corpus:
        c += 1
    assert c == 4327


@pytest.mark.xfail(strict=True, reason="Red Phase")
def text_count_speech():
    corpus = Corpus("txt", texts_to_include="speech")
    c = 0
    for file in corpus:
        c += 1
    assert c == 2544
