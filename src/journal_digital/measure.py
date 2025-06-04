import re
from collections import namedtuple
from pathlib import Path

import pandas as pd
from NameSeconds import NameSeconds
from settings import intertitle_root, speech_root
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
    return int(
        int(hours) * 3600 + int(minutes) * 60 + int(seconds) + int(milli) / 1000.0
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


def measure_corpus(corpus_subdir: Path):
    ns = NameSeconds()

    srts = tqdm(list(corpus_subdir.glob("**/*.srt")))
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
            "speech_seconds": duration_seconds,
            "num_words": num_words,
            "video_seconds": ns[srt.stem],
        }

    ns.save()


def store_corpus_measurements(corpus_subdir: Path):
    measurements = corpus_subdir / "measurements.tsv"
    measurements_description = corpus_subdir / "measurements_description.tsv"
    measurements_sum = corpus_subdir / "measurements_sum.tsv"

    df = pd.DataFrame(measure_corpus(corpus_subdir))
    df.sort_values(by="file", inplace=True)

    df.to_csv(measurements, sep="\t", index=False)

    df.describe().to_csv(measurements_description, sep="\t", float_format="%.2f")

    sum_df = df.sum().reset_index()
    sum_df.iloc[0, 0] = "num_files"
    sum_df.iloc[0, 1] = len(df)
    sum_df.to_csv(
        measurements_sum,
        sep="\t",
        float_format="%.2f",
        index=False,
        header=False,
    )


if __name__ == "__main__":
    store_corpus_measurements(speech_root)
    store_corpus_measurements(intertitle_root)
