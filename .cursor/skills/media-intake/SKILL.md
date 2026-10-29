---
name: media-intake
description: >-
  Download public media, keep a library, and prepare a Meta Business Suite
  schedule in AlayaEdit. Use when the user gives a video or page URL, asks to
  download Facebook, Instagram, YouTube, or TikTok media, or asks to plan or
  schedule posts.
---

# Media intake

## Download

```powershell
uv run alaya-download "SOURCE_URL" -o .\media_library -n 1
```

Results land in `media_library/<platform>/<source>/videos|images/` plus `manifest.json`. That folder is gitignored.

A Facebook reels tab opens a browser, collects visible `/reel/` links, downloads the new ones, scrolls, and stops when several scrolls add nothing. Login, if it appears, is completed by the person at the computer. The profile stays in `.playwright/`.

## Schedule

Copy `config/business_suite.example.yaml` to `config/business_suite.yaml` and `config/schedule.example.yaml` to `config/schedule.yaml`. Fill the real ids locally. Those copies stay off Git.

```powershell
uv run alaya-upload --explore
uv run alaya-upload .\media_library --limit 1
uv run alaya-upload .\media_library --limit 1 --live
```

`--explore` and the dry run do not click Schedule. `--live` does.

Facebook and Munch posting stopped on 29 Sep 2026. Run a live schedule only when the user asks for it in the current conversation.
