import os
import re
from collections import namedtuple
from tqdm import tqdm

srt_input_dir = os.path.abspath("corpus")
txt_output_dir = os.path.abspath("corpus_txt")

SubtitleSegment = namedtuple("SubtitleSegment", ["idx", "start", "end", "text"])


def time_str_to_seconds(t):
    h, m, s_milli = t.split(":")
    s, milli = s_milli.split(",")
    return int(h) * 3600 + int(m) * 60 + int(s) + int(milli) / 1000.0


def parse_srt(srt_path):
    with open(srt_path, "r", encoding="utf-8") as f:
        content = f.read().strip()
    blocks = content.split("\n\n")
    time_pattern = re.compile(
        r"(\d{2}:\d{2}:\d{2},\d{3})\s*-->\s*(\d{2}:\d{2}:\d{2},\d{3})"
    )

    segments = []
    for block in blocks:
        lines = block.split("\n")
        if len(lines) >= 2:
            idx_line = lines[0].strip()
            time_line = lines[1].strip()
            text_lines = lines[2:]
            match = time_pattern.match(time_line)
            if match:
                start, end = match.groups()
                text = " ".join(
                    line.strip() for line in text_lines if line.strip()
                )
                try:
                    idx = int(idx_line)
                except ValueError:
                    continue
                segments.append(
                    SubtitleSegment(idx=idx, start=start, end=end, text=text)
                )
    return segments


def convert_srt_to_txt(input_dir, output_dir):
    input_dir = os.path.abspath(input_dir)
    output_dir = os.path.abspath(output_dir)

    srt_files = []
    for root, _, files in os.walk(input_dir):
        for file in files:
            if file.endswith(".srt"):
                srt_files.append((root, file))

    for root, file in tqdm(srt_files, desc="Processing srt files"):
        input_path = os.path.join(root, file)
        rel_dir = os.path.relpath(root, input_dir)
        target_dir = os.path.join(output_dir, rel_dir)
        os.makedirs(target_dir, exist_ok=True)
        output_filename = os.path.splitext(file)[0] + ".txt"
        output_path = os.path.join(target_dir, output_filename)

        segments = parse_srt(input_path)
        cleaned_lines = [seg.text for seg in segments if seg.text.strip()]

        with open(output_path, "w", encoding="utf-8") as outfile:
            outfile.write("\n\n".join(cleaned_lines) + "\n")


if __name__ == "__main__":
    convert_srt_to_txt(srt_input_dir, txt_output_dir)