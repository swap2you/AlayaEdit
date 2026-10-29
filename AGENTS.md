# AlayaEdit agent file

This file is enough to rebuild the working agreement of the application if the chat is gone. Read it, then `docs/WHERE_WE_STOPPED.md`, then `work/vatsalya-lila/PROGRESS.md`.

## What the application is

AlayaEdit does four jobs:

1. Download public media from a link or a Facebook, Instagram, YouTube, or TikTok page.
2. Hear a long audio file and write a timed transcript in the original language.
3. Turn that hearing into Hindi, English, a chapter with no times, and a clip table.
4. Draft or schedule a Meta Business Suite post when the user asks.

Python 3.12, uv, faster-whisper large-v3 on the NVIDIA GPU. Package layout is in `docs/ARCHITECTURE.md`.

## Rebuild on a new machine

```powershell
git clone <the AlayaEdit GitHub url>
cd AlayaEdit
uv sync
uv run playwright install chromium
```

The Whisper weights download on the first `alaya-lecture` run into `%USERPROFILE%\.cache\huggingface\hub\models--Systran--faster-whisper-large-v3`. Leave that cache in place. `lectures/transcribe.py` prepares CUDA so `cublas64_12.dll` loads. `lectures/audio.py` decodes with PyAV 19 and does not pass `metadata_errors`.

rclone for Google Drive is installed separately. On this computer the remote is `munchdrive` and the config is `%APPDATA%\rclone\rclone.conf`. Do not copy that config into Git and do not print the token.

## Secrets and heavy files

Never commit audio, video, `.playwright/`, cookies, `.env`, `config/business_suite.yaml`, or `config/schedule.yaml`. The example yaml files use placeholders.

## Lecture rule

Hear the whole file before English. Correct Bihari ज/य and ब/व into standard Hindi. Quoted scripture comes from the book, with the citation in brackets. Everyday English after that. Keep Gaudiya words.

`condition_on_previous_text` stays false. A true value once looped a pranam line.

Upload text to the series folder that already exists. Match the byte size, then delete the local MP3. A part is finished only when Hindi, English, the chapter, and the clip table are in Drive `09_Transcripts/Part NN`.

## Do not resume these

- Facebook and Munch posting. Stopped 29 Sep 2026. The user sends their own email about Munch.
- A second Vatsalya series folder. The series id is `1_J8R5TozO5TfG45y7hFlBoG3i7xsMr7X`.
- Damodar Lila 2012 parts 5 and 6. They are finished.
- Inventing Vatsalya part 3. It is not on Desire Tree.

## Where the work stopped

29 Oct 2026, Vatsalya Lila part 6 is on Drive. The next part is 7. Part 6 opens on Sūrdās and ends while Upananda is still speaking. Details: `docs/WHERE_WE_STOPPED.md`.
