# GitHub

Repository name: `AlayaEdit`

Description: AlayaEdit brings any media in, works it short or long, transcribes it, and plans what goes out.

Visibility: private. The history contains lecture text and Drive links for the katha library. It does not contain audio, video, or login files.

Suggested topics: media, transcription, whisper.

## Create and push

From this folder, after `gh auth login` if needed:

```powershell
gh repo create AlayaEdit --private --source=. --remote=origin --description "AlayaEdit brings any media in, works it short or long, transcribes it, and plans what goes out." --push
```

If the GitHub account uses an organization, put the owner in front of the name: `gh repo create OWNER/AlayaEdit`.

## What stays off the remote

- `*.mp3`, `*.mp4`, and other media, including the part 6 audio that is on disk for the resume
- `.playwright/` login profiles
- `config/business_suite.yaml` and `config/schedule.yaml`
- `.venv/` and the Whisper model cache

## What is on the remote

- The Python packages and the lecture builders
- `AGENTS.md`, so a new chat can rebuild the working agreement
- `.cursor/rules` and `.cursor/skills`
- `work/` text for the finished Vatsalya parts, Damodar notes, and the resume file
