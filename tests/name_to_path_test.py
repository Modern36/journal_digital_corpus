from journal_digital_corpus.name_to_path import NameToPathMapper
from journal_digital_corpus.settings import speech_root


def test_creation():
    mapper = NameToPathMapper(speech_root)
    assert len(mapper.dict) == 5144
    assert len(mapper) == 5144
