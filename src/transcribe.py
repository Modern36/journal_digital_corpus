from pathlib import Path

from swescribe.__main__ import pipeline
from tqdm import tqdm

from name_to_path import NameToPathMapper
from settings import video_root

mapper = NameToPathMapper()


def grous_to_paths(groups=["kino", "nuet", "sf", "sj", "ufa"]):
    for group in groups:
        yield from group_to_paths(group)


def group_to_paths(group, force=False):
    group_dir = video_root / group
    for video in group_dir.glob("**/*.mpg"):
        name = video.name
        srt_path = mapper(group=group, name=name)
        if not (srt_path.exists() and force):
            yield video, srt_path


if __name__ == "__main__":
    for video_path, srt_path in tqdm(grous_to_paths(), total=5217):
        pipeline(video_path, srt_path)
