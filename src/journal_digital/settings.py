import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

try:
    video_str_path = os.environ["JOURNAL_DIGITALROOT"]

    if not video_str_path or video_str_path == ".":
        video_str_path = "/tmp"
except KeyError:
    Warning(
        "Could not find environment variable JOURNAL_DIGITALROOT."
        'defaulting to "/tmp"'
    )
    video_str_path = "/tmp"

video_root = Path(video_str_path)
assert video_root.exists(), f"Video root {video_root} does not exist."
assert video_root.is_dir(), f"Video root {video_root} is not a directory."

project_root = Path(__file__).parents[2]
package_root = Path(__file__).parent
corpus_root = package_root / "corpus"
speech_root = corpus_root / "speech"
intertitle_root = corpus_root / "intertitle"

name_year_mapping = project_root / "name_year.tsv"
name_seconds_mapping = project_root / "name_seconds.tsv"
empty_srts_file = project_root / "empty.tsv"
