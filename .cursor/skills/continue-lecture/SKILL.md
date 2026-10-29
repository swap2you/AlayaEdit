---
name: continue-lecture
description: >-
  Hear, transcribe, translate, and file a lecture part in AlayaEdit. Use when
  the user says to resume, restart, continue a katha or lecture, start the next
  part, transcribe audio, write Hindi and English captions, a chapter, or clip
  marks, or names Vatsalya Lila, Damodar Lila, or Guru Maharaj.
---

# Continue a lecture

Read `work/vatsalya-lila/PROGRESS.md` and `docs/WHERE_WE_STOPPED.md` before doing anything. The first row that is not `on Drive` is the part to finish.

## Hear

```powershell
uv run alaya-lecture "<audio url or local mp3>" --language hi -o work/vatsalya-lila/part-NN --prompt "यह हिंदी प्रवचन है। वक्ता राधा गोविंद स्वामी महाराज हैं।"
```

`condition_on_previous_text` stays false. Task is transcribe, not translate. GPU cache stays at `%USERPROFILE%\.cache\huggingface\hub\models--Systran--faster-whisper-large-v3`.

## Write

Hear the whole part, then write sentence-level Hindi and English in a builder under `transcriptions/`, using `transcriptions/_build_vatsalya_05.py` as the shape. One range list, one group list, contiguous cue numbers.

Chapter: Hindi paragraph, then English, no times. Clips: a markdown table.

| Kind | Start | End | Topic | What he says |
|---|---|---|---|---|

Kinds are only `Under 3 minutes`, `Under 5 minutes`, and `Under 10 minutes`.

## File

Upload text only to the existing series folder. Do not upload the MP3 again. Do not create a second series folder. After `rclone check --size-only` matches, delete the local MP3. Update `PROGRESS.md` and `MAP.md`.

Drive series: `1_J8R5TozO5TfG45y7hFlBoG3i7xsMr7X`. Remote name on this machine: `munchdrive`. Do not print the rclone token.

## Vatsalya, the existing parts

Parts 1, 2, and 4 through 13 are on Drive. The first row in `PROGRESS.md` that is not `on Drive` is part 3, and it is missing. Do not invent it. Do not start another hearing of a part already filed. Part 13 ends on the aarti of the Bhagavatam.

Damodar Lila 2012 parts 5 and 6 are finished. Do not revise them.
