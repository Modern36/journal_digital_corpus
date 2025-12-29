import pytest

from journal_digital import Corpus
from journal_digital.corpus import SubtitleSegment

# Setting up counting parameters
counts = {
    "speech": 2544,
    "intertitles": 4327,
}
counts["both"] = sum(counts.values())

counts = {key: (key, count) for key, count in counts.items()}

# output_modes = {"txt", "srt"}


@pytest.mark.parametrize("sub_corpus, target_count", counts.values(), ids=counts.keys())
@pytest.mark.slow
def test_count_files(sub_corpus, target_count):
    corpus = Corpus("txt")
    corpus.set_subcorpora(sub_corpus)
    assert len(corpus) == target_count


@pytest.mark.parametrize("sub_corpus, target_count", counts.values(), ids=counts.keys())
@pytest.mark.slow
def test_count_files_iter(sub_corpus, target_count):
    corpus = Corpus("txt")
    corpus.set_subcorpora(sub_corpus)

    c = 0
    for _ in corpus:
        c += 1
    assert c == target_count


@pytest.mark.slow
def test_corpus_srt_mode_all_files(target_count=counts["speech"][1]):
    corpus = Corpus("srt")
    corpus.set_subcorpora("speech")
    count = 0
    for _, segments, *_ in corpus:
        count += 1
        assert isinstance(segments, list)
        assert all(isinstance(seg, SubtitleSegment) for seg in segments)
    assert count == target_count


# -----------------------------#
#       Unparametrized         #
# -----------------------------#


@pytest.mark.slow
def test_count_files_old():
    corpus = Corpus("txt")
    corpus.set_subcorpora("speech")
    assert len(corpus) == 2544


@pytest.mark.slow
def test_count_files_iter_old():
    corpus = Corpus("txt")
    corpus.set_subcorpora("speech")

    c = 0
    for _ in corpus:
        c += 1
    assert c == 2544


@pytest.mark.slow
def test_no_empty_files(target_count=counts["both"][1]):
    corpus = Corpus("txt")
    file_count = 0
    for doc in corpus:
        assert len(doc.content) > 0

        file = doc.path
        txt2 = corpus._read_file(file)

        assert doc.content == txt2
        file_count += 1
    assert file_count == target_count
