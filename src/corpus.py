from pathlib import Path

from settings import corpus_root


class Corpus:
    _root = corpus_root

    def __init__(self, mode="txt"):
        self.set_mode(mode=mode)

    def set_mode(self, *, mode):
        assert mode in ["txt", "srt"]
        self._mode = mode
        if mode == "txt":
            self.set_txt_mode()
        elif mode == "srt":
            self.set_srt_mode()

    def set_srt_mode(self):
        raise NotImplementedError()

    def set_txt_mode(self):
        self._read_file = self.read_txt

    def read_txt(self, file: Path):
        with open(file, "r", encoding="utf-8") as f:
            result = "\n".join(
                line for i, line in enumerate(f.readlines()) if i % 4 == 2
            )
        return result

    def __iter__(self):
        for file in self._root.glob("**/*.srt"):
            yield file, self._read_file(file)

    def __len__(self):
        return len([_ for _ in self])
