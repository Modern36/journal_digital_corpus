"""Measure and store statistics about the Journal Digital corpus.

This module provides functionality to:
- Measure corpus statistics (segments, duration, word counts) from SRT files
- Store measurements as TSV files for analysis
- Update README.md with corpus statistics

The module can be run directly to measure both speech and intertitle corpora
and update the README with current statistics.
"""

import re
import subprocess
from pathlib import Path

import pandas as pd
from tqdm import tqdm

from journal_digital.corpus import Corpus
from journal_digital.settings import (
    intertitle_root,
    name_seconds_mapping,
    speech_root,
    video_root,
)


class VideoDurationCache:
    """A class to manage video duration mappings by name, with caching and persistence.

    This class maintains a mapping of video names to their durations in seconds,
    caching results to avoid repeated ffprobe calls. It also saves the mapping
    to a file for persistence across sessions.
    """

    video_root = video_root
    mapping_file = name_seconds_mapping

    def __init__(self):
        """Initialize the NameSeconds object by loading existing mappings from file."""
        self.mapping = {}
        if not self.mapping_file.exists():
            raise FileNotFoundError(f"Could not find {self.mapping_file=}")
        if not self.video_root.exists():
            raise FileNotFoundError(f"Could not find {self.video_root=}")

        with open(self.mapping_file, "r", encoding="utf-8") as f:
            for line in f.readlines():
                name, seconds = line.strip().split("\t")
                self.mapping[name.strip()] = int(seconds)

    def __getitem__(self, name):
        """Get the duration of a video by name, retrieving it if not cached.

        If the video name is not in the cache, this method will call ffprobe
        to determine the duration and cache the result.

        Args:
            name (str): The name of the video to get the duration for.

        Returns:
            int: The duration of the video in seconds.
        """
        stripped_name = name.strip()
        if stripped_name in self.mapping.keys():
            return self.mapping[stripped_name]
        else:
            duration = self.get_duration(stripped_name)
            self.mapping[stripped_name] = duration
            return duration

    def get_duration(self, stripped_name):
        """Get the duration of a video by calling ffprobe.

        This method uses ffprobe to determine the duration of a video file
        and returns it as an integer.

        Args:
            stripped_name (str): The name of the video file to get duration for.

        Returns:
            int: The duration of the video in seconds.
        """
        video_paths = list(self.video_root.glob(f"**/{stripped_name}"))

        if len(video_paths) == 0:
            raise FileNotFoundError(
                f'Could not find file: "{stripped_name}" in "{self.video_root}"'
            )
        elif len(video_paths) > 1:
            raise FileNotFoundError(
                f'Found multiple candidets for: "{stripped_name}" in "{self.video_root}"'
            )

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
        """Save the current mapping of video names to durations to the mapping file."""
        with open(self.mapping_file, "w", encoding="utf-8") as f:
            for name, seconds in self.mapping.items():
                f.write(f"{name}\t{seconds}\n")


def measure_corpus(corpus_subdir: Path):
    """Measure statistics for all SRT files in a corpus subdirectory.

    Iterates through all .srt files in the given directory and computes:
    - Number of subtitle segments
    - Total speech duration (in seconds)
    - Total word count
    - Video duration (retrieved from cache)

    Args:
        corpus_subdir (Path): Path to corpus subdirectory containing .srt files
                             (e.g., speech_root or intertitle_root)

    Yields:
        dict: Statistics for each file with keys:
            - file (str): Filename stem
            - num_segments (int): Number of subtitle segments
            - speech_seconds (float): Total duration of speech in seconds
            - num_words (int): Total word count
            - video_seconds (int): Total video duration in seconds
    """
    video_cache = VideoDurationCache()
    corpus = Corpus(
        mode="srt", calculate_num_words=True, calculate_duration=True
    )

    srts = tqdm(list(corpus_subdir.glob("**/*.srt")))
    for srt in srts:
        srts.desc = srt.stem
        num_segments = 0
        duration_seconds = 0
        num_words = 0
        for segment in corpus.read_srt(srt):
            num_segments += 1
            duration_seconds += segment.duration_seconds / 1000
            num_words += segment.num_words
        yield {
            "file": srt.stem,
            "num_segments": num_segments,
            "speech_seconds": duration_seconds,
            "num_words": num_words,
            "video_seconds": video_cache[srt.stem],
        }
    else:
        video_cache.save()


def store_corpus_measurements(corpus_subdir: Path):
    """Measure corpus and save statistics to TSV files.

    Computes statistics for all SRT files in the corpus subdirectory and
    saves three files:
    - measurements.tsv: Per-file statistics
    - measurements_description.tsv: Statistical summary (describe())
    - measurements_sum.tsv: Sum totals across all files

    Args:
        corpus_subdir (Path): Path to corpus subdirectory containing .srt files
                             (e.g., speech_root or intertitle_root)

    Returns:
        pd.DataFrame: Transposed DataFrame of sum statistics
    """
    measurements = corpus_subdir / "measurements.tsv"
    measurements_description = corpus_subdir / "measurements_description.tsv"
    measurements_sum = corpus_subdir / "measurements_sum.tsv"

    df = pd.DataFrame(measure_corpus(corpus_subdir))
    df.sort_values(by="file", inplace=True)

    df.to_csv(measurements, sep="\t", index=False, float_format="%.2f")

    df.describe().to_csv(
        measurements_description, sep="\t", float_format="%.2f"
    )

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
    return sum_df.set_index("index").T


if __name__ == "__main__":
    speech = store_corpus_measurements(speech_root)
    intertitle = store_corpus_measurements(intertitle_root)

    speech_files = speech.num_files.values[0]
    speech_hours = int(speech.speech_seconds.values[0] / 3600)
    speech_words = speech.num_words.values[0]

    intertitle_files = intertitle.num_files.values[0]
    intertitle_count = intertitle.num_segments.values[0]
    intertitle_words = intertitle.num_words.values[0]

    readme_path = Path(__file__).parents[2] / "README.md"
    assert readme_path.exists()

    readme = readme_path.read_text()
    readme = re.sub(
        "<!-- numbers -->.+<!-- numbers -->",
        f"""<!-- numbers --> The corpus consists of {speech_words:,} words transcribed from {speech_hours:,} hours of speech across {speech_files:,} videos and {intertitle_words:,} words from {intertitle_count:,} intertitles from {intertitle_files:,} videos. <!-- numbers -->
""",
        readme,
    )

    readme = re.sub(
        "\n\n+",
        "\n\n",
        readme,
    )

    readme_path.write_text(readme, encoding="utf-8")
