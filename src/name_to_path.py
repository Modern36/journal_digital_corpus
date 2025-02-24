from collections import defaultdict

from settings import corpus_root, metadata_file


class NameToPathMapper(object):
    def __init__(self):
        self.dict = defaultdict(str)
        with open(metadata_file, "r", encoding="utf-8") as f:
            for line in f.readlines():
                name, year = line.split("\t")
                self.dict[name] = year.strip()

    def __call__(self, *, group, name):
        short_name = name.replace(".1.mpg", "")
        year = self.dict[short_name]
        if year == "":
            year = "XXXX"
        out_dir = corpus_root / group / year
        out_dir.mkdir(exist_ok=True, parents=True)

        fname = name + ".srt"
        return out_dir / fname

    def __len__(self):
        return len(self.dict)
