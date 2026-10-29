# AlayaEdit

AlayaEdit brings any media in, works it short or long, transcribes it, and plans what goes out.

The previous folder, `FBVideoDownloader`, is still on this computer. This folder is the one to keep. Open it, then use the commands below.

## Setup

```powershell
cd C:\Development\Workspace\AlayaEdit
uv sync
uv run playwright install chromium
copy config\business_suite.example.yaml config\business_suite.yaml
copy config\schedule.example.yaml config\schedule.yaml
```

`config/business_suite.yaml` and `config/schedule.yaml` stay off Git.

## Commands

| Command | What it does |
|---|---|
| `uv run alaya-download "URL" -o .\media_library` | Download public video or images from a link or a reels tab |
| `uv run alaya-lecture "URL-or-file" --language hi -o work\<series>\part-NN` | Hear an audio file and write a timed transcript |
| `uv run alaya-upload .\media_library --limit 1` | Fill a Business Suite draft and stop before Schedule |
| `uv run alaya-munch` | Older Munch studio helper |

`media-download`, `media-lecture`, `media-upload`, and `media-munch` call the same programs.

## Where the code lives

| Folder | Role |
|---|---|
| `downloader/` | Fetch public media, including a Facebook reels tab |
| `uploader/` | Meta Business Suite drafts and schedules |
| `lectures/` | Decode audio, transcribe on the GPU, write a timed transcript |
| `transcriptions/` | Builders that turn a raw hearing into Hindi, English, a chapter, and clips |
| `youtube/` | Channel notes for titles and thumbnails |
| `shared/` | Manifests, captions, paths |
| `work/` | Finished text, and the note that says which part to do next |
| `docs/` | How to rebuild the application and how to put it on GitHub |

Lecture audio and downloaded video are kept on disk and on Drive. They are not part of the Git history.

## Where the work stopped

Vatsalya Lila part 6. Parts 1, 2, 4, and 5 are on Drive. Part 3 is missing from the source. The hearing of part 6 was cancelled on 28 Oct 2026 before it finished. Start again from `docs/WHERE_WE_STOPPED.md`.
