from pathlib import Path

from journal_digital.settings import intertitle_root, speech_root


class Corpus:
    _intertitle = True
    _speech = True

    def __init__(self, output_format="txt", texts_to_include="speech"):
        self._set_output_format(output_format=output_format)
        self.set_subcorpora(texts_to_include)

    def set_subcorpora(self, texts_to_include):
        if texts_to_include not in ["speech", "intertitles", "both"]:
            raise ValueError(
                f"Invalid texts_to_include: {texts_to_include}. "
                f"Allowed values are 'speech', 'intertitles', 'both'."
            )

        if texts_to_include == "intertitles":
            self._speech = False
            self._intertitle = True

        elif texts_to_include == "speech":
            self._speech = True
            self._intertitle = False
        else:
            self._speech = True
            self._intertitle = True

    def _set_output_format(self, *, output_format):
        if output_format not in ["txt", "srt"]:
            raise ValueError(
                f"Invalid output_format: {output_format}. "
                f"Allowed values are 'txt' and 'srt'."
            )
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
        if self._intertitle:
            for file in intertitle_root.glob("**/*.srt"):
                yield file, self._read_file(file)
        if self._speech:
            print("Speeching!")
            for file in speech_root.glob("**/*.srt"):
                print(file)
                yield file, self._read_file(file)

    def __len__(self):
        return len([_ for _ in self])
