# Journal Digital Corpus

Transcriptions of all  the `journal digital` videos. Created with
Swescribe -- a wrapper around WhisperX.

## Installation

Git clone repository, cd in to the directory and run:
`python -m pip install -e . `

## Version 0.0.1

Created with `SweScribe==v0.0.1` on `2025-02-25`
No manual editing done.

## files

- `/name_year.tsv` pairings of file-name and publication year, based on metadata
  from smdb.
- `/.env` is used to store environmental variables:
   - `JOURNAL_DIGITALROOT` is the **local** absolute path to the videos.


# Todo:

The plan is to add functionalities later:
 - [ ] Limit the process to specific groups
 - [ ] Limit the process to specific years
 - [ ] Outputting srt or json formats of the files
