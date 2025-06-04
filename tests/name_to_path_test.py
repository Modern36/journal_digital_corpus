from journal_digital.name_to_path import NameToPathMapper
from journal_digital.settings import speech_root


def test_creation():
    mapper = NameToPathMapper(speech_root)
    assert len(mapper.dict) == 5144
    assert len(mapper) == 5144
