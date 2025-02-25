import subprocess
from pathlib import Path

from swescribe.__main__ import pipeline
from tqdm import tqdm

from name_to_path import NameToPathMapper
from settings import corpus_root, empty_srts_file, video_root

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


def emtpy_srt():
    for srt in corpus_root.glob("**/*.srt"):
        with open(srt, "r", encoding="utf8") as f:
            text = f.read()
        if text.strip() == "":
            yield srt


def load_empty_filenames():
    if not empty_srts_file.exists():
        return set()
    with open(empty_srts_file, "r", encoding="utf8") as f:
        return {line.strip() for line in f.readlines()}


def write_empty_filenames(empyt_ids_set: list):
    with open(empty_srts_file, "w", encoding="utf8") as f:
        f.write("\n".join(empyt_ids_set))


def remove_empty_transcripts():
    empty_ids = load_empty_filenames() | {
        empty_srt.name.replace(".srt", "") for empty_srt in emtpy_srt()
    }

    write_empty_filenames(sorted(empty_ids))

    for empty_id in empty_ids:
        files = list(corpus_root.glob(f"**/{empty_id}.srt"))
        assert len(files) in {0, 1}

        if not files:
            continue

        for file in files:
            file.unlink()
        # delete emtpy dir
        if len(list(file.parent.iterdir())) == 0:
            file.parent.rmdir()
            if len(list(file.parents[1].iterdir())) == 0:
                file.parents[1].rmdir()


if __name__ == "__main__":
    for video_path, srt_path in tqdm(groups_to_paths(), total=5217):
        pipeline(video_path, srt_path)

    remove_empty_transcripts()
