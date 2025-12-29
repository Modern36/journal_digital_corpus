"""Journal Digital Corpus - Access to timestamped transcriptions from Swedish newsreels.

This module provides the Corpus class for iterating over and reading transcription
files from the Journal Digital corpus, which contains speech-to-text and intertitle
OCR from SF Veckorevy newsreels.
"""

import re
from collections import namedtuple
from itertools import islice
from pathlib import Path

from journal_digital.settings import intertitle_root, speech_root

CorpusDocument = namedtuple(
    "CorpusDocument",
    ["filename", "content", "collection", "year", "subcorpus", "path"],
)

SubtitleSegment = namedtuple(
    "SubtitleSegment",
    ["idx", "start", "end", "text", "num_words", "duration_seconds"],
)


def batched(iterable, n, *, strict=False):
    if n < 1:
        raise ValueError("n must be at least one")
    iterator = iter(iterable)
    while batch := tuple(islice(iterator, n)):
        if strict and len(batch) != n:
            raise ValueError("batched(): incomplete batch")
        yield batch


class Corpus:
    """Iterator for transcription files in the Journal Digital corpus.

    Provides lazy iteration over SRT transcription files with two output modes:
    - 'txt': Returns plain text (every 4th line from SRT files)
    - 'srt': Returns SubtitleSegment namedtuples with optional calculations

    The class supports optional word count and duration calculations that can
    be enabled at initialization or via setter methods.

    Attributes:
        _root (Path): Root directory for corpus files (default: speech_root)
        _mode (str): Current output mode ('txt' or 'srt')
        _calculate_num_words (bool): Whether to calculate word counts
        _calculate_duration (bool): Whether to calculate segment durations
    """

    _intertitle = True
    _speech = True

    def __init__(
        self,
        mode="txt",
        texts_to_include=None,
        calculate_num_words=False,
        calculate_duration=False,
    ):
        """Initialize the Corpus iterator.

        Args:
            mode (str): Output mode - 'txt' for plain text or 'srt' for SubtitleSegments
            calculate_num_words (bool): If True, calculate word counts (srt mode only)
            calculate_duration (bool): If True, calculate durations in milliseconds (srt mode only)
        """
        self._calculate_num_words = calculate_num_words
        self._calculate_duration = calculate_duration
        self.set_mode(mode=mode)
        if texts_to_include:
            self.set_subcorpora(texts_to_include)

    def set_mode(self, *, mode):
        """Set the output mode for corpus iteration.

        Args:
            mode (str): Either 'txt' or 'srt'

        Raises:
            AssertionError: If mode is not 'txt' or 'srt'
        """
        assert mode in {"txt", "srt"}
        self._mode = mode
        if mode == "txt":
            self.set_txt_mode()
        else:
            self.set_srt_mode()

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

    def set_srt_mode(self):
        """Set reader to SRT mode (returns SubtitleSegment namedtuples)."""
        self._read_file = self.read_srt

    def set_txt_mode(self):
        """Set reader to text mode (returns plain text strings)."""
        self._read_file = self.read_txt

    def set_calculate_words(self, setting=True):
        """Enable or disable word count calculation.

        Args:
            setting (bool): True to enable, False to disable (default: True)
        """
        self._calculate_num_words = setting

    def set_calculate_duration(self, setting=True):
        """Enable or disable duration calculation.

        Args:
            setting (bool): True to enable, False to disable (default: True)
        """
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
        """Read an SRT file and extract plain text content.

        Extracts every 4th line (index % 4 == 2) from the SRT file,
        which corresponds to the subtitle text lines.

        Args:
            file (Path): Path to the SRT file

        Returns:
            str: Newline-joined text content from all subtitle segments
        """
        with open(file, "r", encoding="utf-8") as f:
            result = "\n".join(
                line for i, line in enumerate(f.readlines()) if i % 4 == 2
            )
        return result

    def read_srt(self, file: Path):
        """Parse an SRT file into SubtitleSegment namedtuples.

        Reads and validates SRT file format, parsing each segment into a
        SubtitleSegment with optional word count and duration calculations.

        Validation includes:
        - Index must be an integer starting at 1, incrementing by 1
        - Timestamp must match format HH:MM:SS,mmm --> HH:MM:SS,mmm
        - All required lines must be present

        Args:
            file (Path): Path to the SRT file

        Returns:
            list[SubtitleSegment]: List of parsed subtitle segments with fields:
                - idx (int): Segment index (1-based)
                - start (str): Start timestamp
                - end (str): End timestamp
                - text (str): Subtitle text
                - num_words (int|None): Word count if enabled, else None
                - duration_seconds (int|None): Duration in milliseconds if enabled, else None

        Raises:
            ValueError: If SRT format is invalid (missing lines, bad timestamps, etc.)
        """
        time_pattern = re.compile(
            r"(\d{2}:\d{2}:\d{2},\d{3})\s*-->\s*(\d{2}:\d{2}:\d{2},\d{3})"
        )
        segments = []
        expected_idx = None
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

            if expected_idx is None:
                if idx not in (0, 1):
                    raise ValueError(
                        f"Invalid SRT segment in {file}: expected index 1, got {idx}"
                    )
                expected_idx = idx
            elif idx != expected_idx:
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

    def _files(self):
        if self._intertitle:
            for file in intertitle_root.glob("**/*.srt"):
                yield file, "intertitle"
        if self._speech:
            for file in speech_root.glob("**/*.srt"):
                yield file, "speech"

    def __iter__(self):
        """Iterate over all SRT files in the selected sub-corpus.

        Yields CorpusDocument (NamedTuple):
            filename: name of the .srt file
            content: str with all text or list of subtitle segments depending on output mode
            collection: name of the collection {'sf', 'sj', 'kino', 'nuet'}
            year: year the video was published
            subcorpus: {'speech', 'intertitle'}
            path: absolute path to the .srt file
        """
        for file, subcorpus in self._files():
            yield CorpusDocument(
                filename=file.stem,
                content=self._read_file(file),
                collection=file.parent.parent.name,
                year=file.parent.name,
                subcorpus=subcorpus,
                path=file.resolve(),
            )

    def __len__(self):
        """Return the total number of files in the corpus.

        Note: This consumes the iterator, so it's O(n) where n is file count.

        Returns:
            int: Number of SRT files in the corpus
        """
        return len([_ for _ in self])
