import subprocess
from pathlib import Path

from swescribe.__main__ import pipeline
from tqdm import tqdm

from blank_transcripts import (
    load_empty_filenames,
    remove_empty_transcripts,
    write_empty_filenames,
)
from name_to_path import NameToPathMapper
from settings import video_root

mapper = NameToPathMapper()


def groups_to_paths(groups=["kino", "nuet", "sf", "sj", "ufa"]):
    for group in groups:
        yield from group_to_paths(group)


def group_to_paths(group, force=False):
    empty_files = load_empty_filenames()
    group_dir = video_root / group
    for video in group_dir.glob("**/*.mpg"):
        if video.name in empty_files:
            continue

        name = video.name
        srt_path = mapper(group=group, name=name)
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
    write_empty_filenames(empty_files)


if __name__ == "__main__":
    for video_path, srt_path in tqdm(groups_to_paths(), total=5217):
        pipeline(video_path, srt_path)

    remove_empty_transcripts()
