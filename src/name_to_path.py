from settings import metadata_file
from settings import corpus_root


class NameToPathMapper(object):
    def __init__(self):
        self.dict = {}
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
