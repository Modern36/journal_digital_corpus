# Journal Digital Corpus

Transcriptions of all  the `journal digital` videos. Created with
Swescribe -- a wrapper around WhisperX.

## Version 0.0.0-alpha

Created with `SweScribe==v0.0.1`
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
