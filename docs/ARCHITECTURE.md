# Architecture

AlayaEdit is one uv project with five Python packages. The project name is `alayaedit`. The packages keep their import names so the hearing and download code stays stable.

```text
alaya-download  ->  downloader.cli
alaya-lecture   ->  lectures.cli
alaya-upload    ->  uploader.cli
alaya-munch     ->  downloader.munch_cli
```

## downloader

`yt-dlp` fetches a single public URL. A Facebook reels tab uses Playwright: collect visible reel links, download the new ones, scroll, and stop when the page adds nothing. A manifest records what is already on disk.

## lectures

`ingest.py` accepts a URL or a local file. `audio.py` decodes to 16 kHz mono float32. `transcribe.py` runs faster-whisper large-v3, int8 on CUDA, task `transcribe`, word timestamps, VAD, and `condition_on_previous_text=False`. `timeline.py` builds cues and SRT. `validate.py` checks that every second of the file is covered and that Hindi text is mostly Devanagari.

The raw hearing is `original.srt`, `cues.json`, and `words.jsonl`. Those raw dumps stay local. The polished files are written by a script in `transcriptions/`.

## transcriptions

Each finished part has a builder, `_build_vatsalya_NN.py` or `_build_p6.py`. The builder holds sentence groups and inclusive cue ranges, checks that the ranges cover every raw cue, and writes `hindi.srt`, `english.srt`, `Chapter.md`, and `Clips.md`.

## uploader

Playwright opens Meta Business Suite with a saved profile. A dry run fills the composer and does not click Schedule. `--live` does. Posting to Facebook is off unless the user asks.

## youtube

Helpers for titles and thumbnails. Plans live with the channel notes, not in the download path.

## work

`work/<series>/PROGRESS.md` is the resume file. Finished text for a part lives in `work/<series>/part-NN/`. Audio lives beside it and is gitignored.
