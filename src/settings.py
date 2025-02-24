import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

video_root = Path(os.getenv("JOURNLA_DIGITALROOT"))
project_root = Path(__file__).parents[1]
corpus_root = project_root / "corpus"
metadata_file = project_root / "name_year.tsv"
