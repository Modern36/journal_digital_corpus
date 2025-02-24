from src.name_to_path import NameToPathMapper


def test_creation():
    mapper = NameToPathMapper()
    assert len(mapper.dict) == 5144
