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


def test_speech_subcorpus_metadata():
    corpus = Corpus("txt", texts_to_include="speech")
    for doc in corpus:
        assert doc.subcorpus == "speech"
        assert doc.collection in ("kino", "nuet", "sf", "sj")
        assert doc.year.isdigit() or doc.year == "XXXX"
        assert doc.filename
        assert doc.content
        break


def test_intertitle_subcorpus_metadata():
    corpus = Corpus("txt", texts_to_include="intertitles")
    for doc in corpus:
        assert doc.subcorpus == "intertitle"
        assert doc.collection in ("kino", "nuet", "sf", "sj")
        assert doc.year.isdigit() or doc.year == "XXXX"
        assert doc.filename
        assert doc.content
        break


def test_both_subcorpora_metadata():
    corpus = Corpus("txt", texts_to_include="both")
    subcorpora_seen = set()
    for doc in corpus:
        assert doc.subcorpus in ("speech", "intertitle")
        assert doc.collection in ("kino", "nuet", "sf", "sj")
        assert doc.year.isdigit() or doc.year == "XXXX"
        assert doc.filename
        assert doc.content
        subcorpora_seen.add(doc.subcorpus)
        if len(subcorpora_seen) == 2:
            break
    assert subcorpora_seen == {"speech", "intertitle"}


def test_metadata_attributes_exist():
    corpus = Corpus("txt", texts_to_include="speech")
    doc = next(iter(corpus))
    assert hasattr(doc, "filename")
    assert hasattr(doc, "content")
    assert hasattr(doc, "collection")
    assert hasattr(doc, "year")
    assert hasattr(doc, "subcorpus")
