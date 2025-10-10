import multiprocessing
import subprocess

from stum.video_to_srt import pipeline as stum_pipeline
from swescribe.__main__ import pipeline as swescribe_pipeline
from tqdm import tqdm

from journal_digital.blank_transcripts import (
    load_empty_filenames,
    remove_empty_transcripts,
    write_empty_filenames,
)
from journal_digital.name_to_path import NameToPathMapper
from journal_digital.settings import intertitle_root, speech_root, video_root

speech_path_mapper = NameToPathMapper(speech_root)
intetitel_path_mapper = NameToPathMapper(intertitle_root)

groups = ("kino", "nuet", "sf", "sj")


def speech_path_pairs():
    for group in groups:
        yield from group_to_speech_paths(group)


def intertitle_path_pairs():
    for group in groups:
        yield from group_to_intertitle_paths(group)


def group_to_intertitle_paths(group, force=False):
    group_dir = video_root / group
    empty_files = load_empty_filenames(intertitle_root)
    for video in group_dir.glob("**/*.mpg"):
        if video.name in empty_files:
            continue

        name = video.name
        srt_path = intetitel_path_mapper(group=group, name=name)
        if srt_path.exists() and not force:
            continue

        yield video, srt_path


def group_to_speech_paths(group, force=False):
    group_dir = video_root / group
    empty_files = load_empty_filenames(speech_root)
    for video in group_dir.glob("**/*.mpg"):
        if video.name in empty_files:
            continue

        name = video.name
        srt_path = speech_path_mapper(group=group, name=name)
        if not (force and srt_path.exists()):
            continue

        q = subprocess.run(
            [
                "ffprobe",
                "-v",
                "error",
                "-select_streams",
                "a",
                "-show_entries",
                "stream=index",
                "-of",
                "csv=p=0",
                str(video),
            ],
            check=True,
            capture_output=True,
            text=True,
        )
        if q.stdout == "":
            empty_files.add(name)
            continue
        if force:
            yield video, srt_path
        elif not srt_path.exists():
            yield video, srt_path
    write_empty_filenames(speech_root, empty_files)


def tuple_stum_pipeline(pair):
    video_path, srt_path = pair
    stum_pipeline(video_path, srt_path)
    return srt_path.exists()


if __name__ == "__main__":
    for video_path, srt_path in tqdm(
        speech_path_pairs(),
        total=5217,
        desc="Speech Transcription",
    ):
        swescribe_pipeline(video_path, srt_path)

    remove_empty_transcripts(speech_root)

    with multiprocessing.Pool() as pool:
        bad = tqdm(
            desc="Intertitle Transcription",
            total=5217 - 880,
        )
        for task in pool.imap_unordered(
            tuple_stum_pipeline, intertitle_path_pairs(), chunksize=10
        ):
            if task:
                bad.update(1)

    remove_empty_transcripts(intertitle_root)
