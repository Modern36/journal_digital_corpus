[![Publish Python Package to PyPI](https://github.com/Modern36/journal_digital_corpus/actions/workflows/hatch-publish-to-pypi.yml/badge.svg)](https://github.com/Modern36/journal_digital_corpus/actions/workflows/hatch-publish-to-pypi.yml)
[![pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit)](https://github.com/pre-commit/pre-commit)
[![Hatch project](https://img.shields.io/badge/%F0%9F%A5%9A-Hatch-4051b5.svg)](https://github.com/pypa/hatch)
[![DOI](https://zenodo.org/badge/937956064.svg)](https://doi.org/10.5281/zenodo.15596191)


# Journal Digital Corpus

The **Journal Digital Corpus** is a curated, timestamped transcription corpus
derived from Swedish historical newsreels. It combines speech-to-text
transcriptions and intertitle OCR to enable scalable and searchable analysis of
early-to-mid 20th-century audiovisual media.

The SF Veckorevy newsreels—-screened weekly across Sweden for over five
decades—-form one of the most extensive audiovisual records of 20th-century
Swedish life. Yet their research potential has remained largely untapped due to
barriers to access and analysis. The Journal Digital Corpus offers the first
comprehensive transcription of both speech and intertitles from this material.

This corpus is the result of two purpose-built libraries:

- **[SweScribe](https://github.com/Modern36/swescribe)** – an ASR pipeline
  developed for transcription of speech in historical Swedish newsreels.
- **[stum](https://github.com/Modern36/stum)** – an OCR tool for detecting and
  transcribing intertitles in silent film footage.

<!-- numbers --> The corpus consists of 2,225,334 words transcribed from 204 hours of speech across 2,544 videos and 302,312 words from 49,107 intertitles from 4,327 videos. <!-- numbers -->





The primary files used for this project are publicly available on
[Filmarkivet.se](https://www.filmarkivet.se/), a web
resource containing curated parts of Swedish film archives.

## Installation

Git clone repository, cd in to the directory and run:
`python -m pip install -e . `

`python -m pip install journal_digital`

## Usage

### Reading the corpus in text mode

```python
from journal_digital import Corpus

# Iterate over speech transcriptions as plain text
corpus = Corpus(mode="txt")
for file, text in corpus:
    print(f"{file.stem}: {text[:100]}...")
```

### Reading the corpus in SRT mode

```python
from journal_digital import Corpus

# Iterate over speech transcriptions as timestamped segments
corpus = Corpus(mode="srt")
for file, segments in corpus:
    for segment in segments:
        print(f"[{segment.start} --> {segment.end}] {segment.text}")
```

Each segment is a `SubtitleSegment` namedtuple with fields:
- `idx`: Segment index (starts at 1)
- `start`: Start timestamp (format: `HH:MM:SS,mmm`)
- `end`: End timestamp (format: `HH:MM:SS,mmm`)
- `text`: Transcribed text
- `num_words`: Word count (optional, `None` by default)
- `duration_seconds`: Segment duration in seconds (optional, `None` by default)

## 2025-06-04

Created with `SweScribe==v0.1.0` and `stum==v.0.2.0` on `2025-06-04` without
manual editing.

## Files

- `/name_year.tsv`: Pairings of filename and publication year, based on metadata
  from [The Swedish Media Database (SMDB)](https://smdb.kb.se/).

```
/corpus
├── /intertitle
│   ├── /collection_1
│   ├── /collection_2
│   └── /collection_3
│       ├── /1920
│       │   ├── video_1.srt
│       │   ├── video_2.srt
│       │   └── video_3.srt
│       ├── /1921
│       │   ├── video_1.srt
│       │   ├── video_2.srt
│       │   └── video_3.srt
│       └── /1922
│           ├── video_1.srt
│           ├── video_2.srt
│           └── video_3.srt
├── /speech
│   ├── /collection_1
│   ├── /collection_2
│   └── /collection_3
│       ├── /1920
│       │   ├── video_1.srt
│       │   ├── video_2.srt
│       │   └── video_3.srt
│       ├── /1921
│       │   ├── video_1.srt
│       │   ├── video_2.srt
│       │   └── video_3.srt
│       └── /1922
│           ├── video_1.srt
│           ├── video_2.srt
│           └── video_3.srt
```

### Development Setup

`python -m pip install -e '.[dev]'`
`pre-commit install`

Add your path to videos got `JOURNAL_DIGITALROOT` in `.env`.


## Research Context and Licensing

### Modern Times 1936

The Journal Digital Corpus was developed for the
[Modern Times 1936](https://modernatider1936.se/en/) research
[project at Lund University](https://portal.research.lu.se/sv/projects/modern-times-1936-2),
Sweden. The project investigates what software "sees," "hears," and "perceives"
when pattern recognition technologies such as 'AI' are applied to media
historical sources. The project is
[funded by Riksbankens Jubileumsfond](https://www.rj.se/bidrag/2021/moderna-tider-1936/).

### License

The Journal Digital Corpus is licensed under the [CC-BY-NC 4.0](./LICENSE)
International license.

## References

```bibtex
@article{bain2022whisperx,
  title={WhisperX: Time-Accurate Speech Transcription of Long-Form Audio},
  author={Bain, Max and Huh, Jaesung and Han, Tengda and Zisserman, Andrew},
  journal={INTERSPEECH 2023},
  year={2023}
}
```

```bibtex
@inproceedings{malmsten2022hearing,
  title={Hearing voices at the national library : a speech corpus and acoustic model for the Swedish language},
  author={Malmsten, Martin and Haffenden, Chris and B{\"o}rjeson, Love},
  booktitle={Proceeding of Fonetik 2022 : Speech, Music and Hearing Quarterly Progress and Status Report, TMH-QPSR},
  volume={3},
  year={2022}
}
```

```bibtex
@inproceedings{zhou2017east,
  title={East: an efficient and accurate scene text detector},
  author={Zhou, Xinyu and Yao, Cong and Wen, He and Wang, Yuzhi and Zhou, Shuchang and He, Weiran and Liang, Jiajun},
  booktitle={Proceedings of the IEEE conference on Computer Vision and Pattern Recognition},
  pages={5551--5560},
  year={2017}
}
```
