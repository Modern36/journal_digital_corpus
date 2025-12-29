import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()


video_root = Path(os.environ.get("JOURNAL_DIGITALROOT", None))
assert video_root != Path(".")
assert video_root.exists(), f"Video root {video_root} does not exist."
assert video_root.is_dir(), f"Video root {video_root} is not a directory."

project_root = Path(__file__).parents[2]
corpus_root = project_root / "corpus"
speech_root = corpus_root / "speech"
intertitle_root = corpus_root / "intertitle"

name_year_mapping = project_root / "name_year.tsv"
name_seconds_mapping = project_root / "name_seconds.tsv"
empty_srts_file = project_root / "empty.tsv"
