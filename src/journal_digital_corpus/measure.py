import re
import subprocess
from collections import namedtuple

import pandas as pd
from settings import (
    corpus_root,
    measurements,
    measurements_description,
    name_seconds_mapping,
    video_root,
)
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
            "speech_seconds": duration_seconds,
            "num_words": num_words,
        }


class NameSeconds:
    video_root = video_root
    mapping_file = name_seconds_mapping

    def __init__(self):
        self.mapping = {}
        if self.mapping_file.exists():
            with open(self.mapping_file, "r", encoding="utf-8") as f:
                f.readline()
                for line in f.readlines():
                    name, seconds = line.strip().split("\t")
                    self.mapping[name.strip()] = int(seconds)

    def __getitem__(self, name):
        stripped_name = name.strip()
        if stripped_name in self.mapping.keys():
            return self.mapping[stripped_name]
        else:
            duration = self.get_duration(stripped_name)
            self.mapping[stripped_name] = duration
            return duration

    def get_duration(self, stripped_name):
        video_paths = list(self.video_root.glob(f"**/{stripped_name}"))

        assert len(video_paths) == 1
        video_path = video_paths[0]

        q = subprocess.run(
            [
                "ffprobe",
                "-v",
                "error",
                "-show_entries",
                "format=duration",
                "-of",
                "default=noprint_wrappers=1:nokey=1",
                str(video_path),
            ],
            check=True,
            capture_output=True,
            text=True,
        )

        return int(float(q.stdout))

    def save(self):
        with open(self.mapping_file, "w", encoding="utf-8") as f:
            for name, seconds in self.mapping.items():
                f.write(f"{name}\t{seconds}\n")


if __name__ == "__main__":
    ns = NameSeconds()

    df = pd.DataFrame(measure_corpus())
    df.sort_values(by="file", inplace=True)

    df["video_seconds"] = df.apply(
        lambda row: ns.get_duration(row["file"]), axis=1
    )

    ns.save()

    df.to_csv(measurements, sep="\t", index=False)

    df.describe().to_csv(
        measurements_description, sep="\t", float_format="%.2f"
    )
