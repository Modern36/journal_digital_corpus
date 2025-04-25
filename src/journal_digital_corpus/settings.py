import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

video_root = Path(os.getenv("JOURNAL_DIGITALROOT"))
project_root = Path(__file__).parents[2]
corpus_root = project_root / "corpus"

name_year_mapping = project_root / "name_year.tsv"
name_seconds_mapping = project_root / "name_seconds.tsv"
empty_srts_file = project_root / "empty.tsv"

measurements = corpus_root / "measurements.tsv"
measurements_description = corpus_root / "measurements_description.tsv"


measurements_sum = corpus_root / "measurements_sum.tsv"
