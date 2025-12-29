from pathlib import Path

from settings import intertitle_root, speech_root


def emtpy_srt(corpus_dir):
    for srt in corpus_dir.glob("**/*.srt"):
        with open(srt, "r", encoding="utf8") as f:
            text = f.read()
        if text.strip() == "":
            yield srt


def load_empty_filenames(empty_srts_file):
    if empty_srts_file.is_dir():
        empty_srts_file = empty_srts_file / "empty.tsv"
    if not empty_srts_file.exists():
        return set()
    with open(empty_srts_file, "r", encoding="utf8") as f:
        return {line.strip() for line in f.readlines()}


def write_empty_filenames(empty_srts_file, empyt_ids_set: list):
    if empty_srts_file.is_dir():
        empty_srts_file = empty_srts_file / "empty.tsv"

    with open(empty_srts_file, "w", encoding="utf8") as f:
        f.write("\n".join(empyt_ids_set))


def remove_empty_transcripts(corpus_dir: Path):
    empty_srts_file = corpus_dir / "empty.tsv"
    empty_ids = load_empty_filenames(empty_srts_file) | {
        empty_srt.name.replace(".srt", "")
        for empty_srt in emtpy_srt(corpus_dir)
    }

    write_empty_filenames(empty_srts_file, sorted(empty_ids))

    for empty_id in empty_ids:
        files = list(corpus_dir.glob(f"**/{empty_id}.srt"))
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
    for sub_corpus in (speech_root, intertitle_root):
        remove_empty_transcripts(sub_corpus)
