import re
from itertools import batched
from pathlib import Path

from journal_digital.measure import SubtitleSegment
from journal_digital.settings import speech_root


class Corpus:
    _root = speech_root

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
        self._read_file = self.read_srt

    def set_txt_mode(self):
        self._read_file = self.read_txt

    def read_txt(self, file: Path):
        with open(file, "r", encoding="utf-8") as f:
            result = "\n".join(
                line for i, line in enumerate(f.readlines()) if i % 4 == 2
            )
        return result

    def read_srt(self, file: Path):
        time_pattern = re.compile(
            r"(\d{2}:\d{2}:\d{2},\d{3})\s*-->\s*(\d{2}:\d{2}:\d{2},\d{3})"
        )
        segments = []
        expected_idx = 1
        with open(file, "r", encoding="utf-8") as f:
            lines = [line.rstrip() for line in f.readlines()]

        for idx_line, time_line, text_line, *_ in batched(lines, 4):
            if not idx_line:
                raise ValueError(
                    f"Invalid SRT segment in {file}: missing index line"
                )

            try:
                idx = int(idx_line)
            except ValueError:
                raise ValueError(
                    f"Invalid SRT segment in {file}: index '{idx_line}' is not an integer"
                )

            if idx != expected_idx:
                raise ValueError(
                    f"Invalid SRT segment in {file}: expected index {expected_idx}, got {idx}"
                )

            if not time_line:
                raise ValueError(
                    f"Invalid SRT segment in {file}: missing timestamp line"
                )

            match = time_pattern.match(time_line)
            if not match:
                raise ValueError(
                    f"Invalid SRT segment in {file}: malformed timestamp '{time_line}'"
                )

            start, end = match.groups()

            segment = SubtitleSegment(
                idx=idx,
                start=start,
                end=end,
                text=text_line,
                num_words=None,
                duration_seconds=None,
            )
            segments.append(segment)
            expected_idx += 1

        return segments

    def __iter__(self):
        for file in self._root.glob("**/*.srt"):
            yield file, self._read_file(file)

    def __len__(self):
        return len([_ for _ in self])
