import re
from collections import namedtuple
from itertools import batched
from pathlib import Path

from journal_digital.settings import speech_root

SubtitleSegment = namedtuple(
    "SubtitleSegment",
    ["idx", "start", "end", "text", "num_words", "duration_seconds"],
)


class Corpus:
    _root = speech_root

    def __init__(
        self, mode="txt", calculate_num_words=False, calculate_duration=False
    ):
        self._calculate_num_words = calculate_num_words
        self._calculate_duration = calculate_duration
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

    def set_calculate_words(self, setting=True):
        self._calculate_num_words = setting

    def set_calculate_duration(self, setting=True):
        self._calculate_duration = setting

    def _srt_time_to_milliseconds(self, t):
        hours, minutes, s_milli = t.split(":")
        seconds, milli = s_milli.split(",")
        return (
            int(hours) * 3600000
            + int(minutes) * 60000
            + int(seconds) * 1000
            + int(milli)
        )

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

            num_words = (
                len(text_line.split()) if self._calculate_num_words else None
            )
            if self._calculate_duration:
                start_ms = self._srt_time_to_milliseconds(start)
                end_ms = self._srt_time_to_milliseconds(end)
                duration_seconds = end_ms - start_ms
            else:
                duration_seconds = None

            segment = SubtitleSegment(
                idx=idx,
                start=start,
                end=end,
                text=text_line,
                num_words=num_words,
                duration_seconds=duration_seconds,
            )
            segments.append(segment)
            expected_idx += 1

        return segments

    def __iter__(self):
        for file in self._root.glob("**/*.srt"):
            yield file, self._read_file(file)

    def __len__(self):
        return len([_ for _ in self])
