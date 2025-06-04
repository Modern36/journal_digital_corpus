from collections import defaultdict
from pathlib import Path

from journal_digital.settings import name_year_mapping, speech_root


class NameToPathMapper(object):
    def __init__(
        self,
        root: Path = speech_root,
    ):
        self.root = root
        self.dict = defaultdict(str)
        with open(name_year_mapping, "r", encoding="utf-8") as f:
            for line in f.readlines():
                name, year = line.split("\t")
                self.dict[name] = year.strip()

    def __call__(self, *, group, name):
        short_name = name.replace(".1.mpg", "")
        year = self.dict[short_name]
        if year == "":
            year = "XXXX"
        out_dir = self.root / group / year
        out_dir.mkdir(exist_ok=True, parents=True)

        fname = name + ".srt"
        return out_dir / fname

    def __len__(self):
        return len(self.dict)
