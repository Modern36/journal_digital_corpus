from collections import namedtuple

SubtitleSegment = namedtuple(
    "SubtitleSegment",
    ["idx", "start", "end", "text", "num_words", "duration_seconds"],
)
