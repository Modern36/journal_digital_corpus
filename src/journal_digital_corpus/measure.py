import re
from collections import namedtuple

from settings import corpus_root, measurements
from tqdm import tqdm

SubtitleSegment = namedtuple(
    "SubtitleSegment",
    ["idx", "start", "end", "text", "num_words", "duration_seconds"],
)
time_pattern = re.compile(
    r"(\d{2}:\d{2}:\d{2},\d{3})\s*-->\s*(\d{2}:\d{2}:\d{2},\d{3})"
)


def srt_time_to_seconds(t):
    hours, minutes, s_milli = t.split(":")
    seconds, milli = s_milli.split(",")
    return (
        int(hours) * 3600
        + int(minutes) * 60
        + int(seconds)
        + int(milli) / 1000.0
    )


def parse_srt(srt_path):
    with open(srt_path, "r", encoding="utf-8") as f:
        content = f.read().strip()

    for block in content.split("\n\n"):
        idx_line, time_line, text_line = block.split("\n")
        match = time_pattern.match(time_line)
        start, end = match.groups()
        idx = int(idx_line)

        start_second = srt_time_to_seconds(start)
        end_second = srt_time_to_seconds(end)
        duration_seconds = end_second - start_second
        num_words = len(text_line.split())

        yield SubtitleSegment(
            idx=idx,
            start=start,
            end=end,
            text=text_line,
            duration_seconds=duration_seconds,
            num_words=num_words,
        )


def measure_corpus():
    srts = tqdm(list(corpus_root.glob("**/*.srt")))
    for srt in srts:
        srts.desc = srt.stem
        num_segments = 0
        duration_seconds = 0
        num_words = 0
        for segment in parse_srt(srt):
            num_segments += 1
            duration_seconds += segment.duration_seconds
            num_words += segment.num_words
        yield {
            "file": srt.stem,
            "num_segments": num_segments,
            "duration_seconds": duration_seconds,
            "num_words": num_words,
        }
