import subprocess

from settings import name_seconds_mapping, video_root


class NameSeconds:
    """A class to manage video duration mappings by name, with caching and persistence.

    This class maintains a mapping of video names to their durations in seconds,
    caching results to avoid repeated ffprobe calls. It also saves the mapping
    to a file for persistence across sessions.
    """

    video_root = video_root
    mapping_file = name_seconds_mapping

    def __init__(self):
        """Initialize the NameSeconds object by loading existing mappings from file."""
        self.mapping = {}
        if self.mapping_file.exists():
            with open(self.mapping_file, "r", encoding="utf-8") as f:
                f.readline()
                for line in f.readlines():
                    name, seconds = line.strip().split("\t")
                    self.mapping[name.strip()] = int(seconds)

    def __getitem__(self, name):
        """Get the duration of a video by name, retrieving it if not cached.

        If the video name is not in the cache, this method will call ffprobe
        to determine the duration and cache the result.

        Args:
            name (str): The name of the video to get the duration for.

        Returns:
            int: The duration of the video in seconds.
        """
        stripped_name = name.strip()
        if stripped_name in self.mapping.keys():
            return self.mapping[stripped_name]
        else:
            duration = self.get_duration(stripped_name)
            self.mapping[stripped_name] = duration
            return duration

    def get_duration(self, stripped_name):
        """Get the duration of a video by calling ffprobe.

        This method uses ffprobe to determine the duration of a video file
        and returns it as an integer.

        Args:
            stripped_name (str): The name of the video file to get duration for.

        Returns:
            int: The duration of the video in seconds.
        """
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
        """Save the current mapping of video names to durations to the mapping file."""
        with open(self.mapping_file, "w", encoding="utf-8") as f:
            for name, seconds in self.mapping.items():
                f.write(f"{name}\t{seconds}\n")
