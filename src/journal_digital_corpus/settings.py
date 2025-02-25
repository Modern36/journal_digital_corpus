import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

video_root = Path(os.getenv("JOURNAL_DIGITALROOT"))
project_root = Path(__file__).parents[2]
corpus_root = project_root / "corpus"
metadata_file = project_root / "name_year.tsv"
empty_srts_file = project_root / "empty.tsv"
