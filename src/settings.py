from dotenv import load_dotenv
import os
from pathlib import Path

load_dotenv()

video_root = os.getenv("JOURNLA_DIGITALROOT")
corpus_root = Path(__file__).parents[1] / "corpus"
