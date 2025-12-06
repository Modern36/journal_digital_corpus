from journal_digital import Corpus


def test_count_intertitle():
    corpus = Corpus("txt", texts_to_include="intertitles")
    c = 0
    for file in corpus:
        c += 1
    assert c == 4327


def text_count_speech():
    corpus = Corpus("txt", texts_to_include="speech")
    c = 0
    for file in corpus:
        c += 1
    assert c == 2544
