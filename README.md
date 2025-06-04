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

<!-- numbers --> The corpus consists of 2,229,854 words transcribed from 204 hours of speech from 2,553 videos and 302,342 words from 49,119 intertitles from 4,333 videos. <!-- numbers -->



The primary files used for this project are publicly available on
[Filmarkivet.se](https://www.filmarkivet.se/), a web
resource containing curated parts of Swedish film archives.

## Installation

Git clone repository, cd in to the directory and run:
`python -m pip install -e . `

`python -m pip install journal_digital`

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

### Develop Setup

`python -m pip install '.[dev]'`
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
