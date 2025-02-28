import os
import re
from collections import namedtuple
from pathlib import Path

from swescribe import num_test_cases
from swescribe.paths import srt_output_dir, txt_output_dir

SubtitleSegment = namedtuple(
    "SubtitleSegment", ["idx", "start", "end", "text"]
)


def time_str_to_seconds(t):
    h, m, s_milli = t.split(":")
    s, milli = s_milli.split(",")
    return int(h) * 3600 + int(m) * 60 + int(s) + int(milli) / 1000.0


CLEAR_INTERVALS = {
    "fil_06": [
        ("00:01:46,000", "00:03:35,000"),
        ("00:07:40,000", "00:14:11,000"),
    ],
    "fil_08": [
        ("00:06:51,000", "00:07:15,000"),
        ("00:07:46,000", "00:08:13,000"),
    ],
    "fil_10": [("00:06:16,000", "00:06:31,000")],
    "fil_11": [("00:09:35,000", "00:10:18,000")],
    "fil_14": [
        ("00:03:47,478", "00:04:43,000"),
        ("00:05:03,000", "00:05:42,000"),
    ],
    "fil_16": [
        ("00:00:34,000", "00:00:51,000"),
        ("00:01:00,000", "00:01:03,000"),
        ("00:01:08,000", "00:01:38,000"),
        ("00:01:41,000", "00:02:25,000"),
        ("00:02:35,000", "00:02:42,000"),
    ],
    "fil_27": [("00:08:44,000", "00:09:46,000")],
    "SF2672.1": [("00:04:19,000", "00:04:46,000")],
    "SF2870.1": [("00:04:20,000", "00:04:22,000")],
    "SF891D.1": [
        ("00:00:14,650", "00:00:40,000"),
        ("00:01:26,000", "00:01:32,000"),
    ],
    "SF912A.1": [("00:07:07,692", "00:07:09,473")],
    "SF915B.1": [
        ("00:00:04,000", "00:00:05,000"),
        ("00:00:53,000", "00:01:00,000"),
        ("00:02:02,483", "00:08:48,139"),
    ],
    "SF3163.1": [("00:04:37,000", "00:08:48,408")],
    "SF901A.1": [
        ("00:05:42,084", "00:05:50,000"),
        ("00:06:56,000", "00:11:21,000"),
    ],
    "Kino121.1": [("00:02:17,000", "00:09:56,000")],
    "SF1016A.1": [("00:05:48,000", "00:07:17,000")],
    "SF2651A-G.1": [("00:10:16,587", "01:03:59,350")],
    "SF3054.1": [("00:00:55,277", "00:01:29,543")],
    "SF931A.1": [("00:03:49,036", "00:03:49,496")],
    "SF991.1": [("00:05:39,000", "00:06:13,000")],
    "Kino182B.1": [("00:09:20,461", "00:10:16,135")],
    "SF1622A.1": [("00:04:00,000", "00:08:14,000")],
    "SF3009A-D.1": [("00:16:29,000", "00:17:00,000")],
    "SF3180.1": [("00:06:14,000", "00:06:16,000")],
}


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


def clear_subtitle_segments_text(segments, filename_base):
    if filename_base not in CLEAR_INTERVALS:
        return segments

    intervals = CLEAR_INTERVALS[filename_base]
    cleaned = []
    for seg in segments:
        start_sec = time_str_to_seconds(seg.start)
        end_sec = time_str_to_seconds(seg.end)

        remove = False
        for r_start, r_end in intervals:
            r_start_sec = time_str_to_seconds(r_start)
            r_end_sec = time_str_to_seconds(r_end)
            if not (end_sec < r_start_sec or start_sec > r_end_sec):
                remove = True
                break

        if remove:
            cleaned.append(
                SubtitleSegment(
                    idx=seg.idx, start=seg.start, end=seg.end, text=""
                )
            )
        else:
            cleaned.append(seg)
    return cleaned


def convert_srt_to_txt(input_dir, output_dir):
    os.makedirs(output_dir, exist_ok=True)

    srt_files = [f for f in os.listdir(input_dir) if f.endswith(".srt")]

    if len(srt_files) != num_test_cases:
        raise ValueError(
            f"Expected {num_test_cases} SRT files, found {len(srt_files)}"
        )

    for srt_file in srt_files:
        input_path = os.path.join(input_dir, srt_file)
        output_filename = os.path.splitext(srt_file)[0] + ".txt"
        output_path = os.path.join(output_dir, output_filename)

        segments = parse_srt(input_path)

        filename_base = os.path.splitext(srt_file)[0]
        cleaned_segments = clear_subtitle_segments_text(
            segments, filename_base
        )

        cleaned_lines = [
            seg.text for seg in cleaned_segments if seg.text.strip()
        ]

        with open(output_path, "w", encoding="utf-8") as outfile:
            outfile.write("\n\n".join(cleaned_lines) + "\n")


if __name__ == "__main__":
    convert_srt_to_txt(srt_output_dir, txt_output_dir)
