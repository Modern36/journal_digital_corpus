from journal_digital.name_to_path import NameToPathMapper
from journal_digital.settings import corpus_root


def test_creation():
    mapper = NameToPathMapper(corpus_root)
    assert len(mapper.dict) == 5144
    assert len(mapper) == 5144
