from pathlib import Path

from journal_digital.settings import speech_root


class Corpus:
    _root = speech_root

    def __init__(self, output_format="txt"):
        self.set_output_format(output_format=output_format)

    def set_output_format(self, *, output_format):
        assert output_format in ["txt", "srt"]
        self._mode = output_format
        if output_format == "txt":
            self.set_txt_mode()
        elif output_format == "srt":
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
