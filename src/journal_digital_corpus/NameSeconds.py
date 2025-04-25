import subprocess

from journal_digital_corpus.settings import name_seconds_mapping, video_root


class NameSeconds:
    video_root = video_root
    mapping_file = name_seconds_mapping

    def __init__(self):
        self.mapping = {}
        if self.mapping_file.exists():
            with open(self.mapping_file, "r", encoding="utf-8") as f:
                f.readline()
                for line in f.readlines():
                    name, seconds = line.strip().split("\t")
                    self.mapping[name.strip()] = int(seconds)

    def __getitem__(self, name):
        stripped_name = name.strip()
        if stripped_name in self.mapping.keys():
            return self.mapping[stripped_name]
        else:
            duration = self.get_duration(stripped_name)
            self.mapping[stripped_name] = duration
            return duration

    def get_duration(self, stripped_name):
        video_paths = list(self.video_root.glob(f"**/{stripped_name}"))

        assert len(video_paths) == 1
        video_path = video_paths[0]

        q = subprocess.run(
            [
                "ffprobe",
                "-v",
                "error",
                "-show_entries",
                "format=duration",
                "-of",
                "default=noprint_wrappers=1:nokey=1",
                str(video_path),
            ],
            check=True,
            capture_output=True,
            text=True,
        )

        return int(float(q.stdout))

    def save(self):
        with open(self.mapping_file, "w", encoding="utf-8") as f:
            for name, seconds in self.mapping.items():
                f.write(f"{name}\t{seconds}\n")
