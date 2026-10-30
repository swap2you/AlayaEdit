"""Check that an illustrated episode is complete enough to watch."""

from __future__ import annotations

import json
from pathlib import Path

import av
from PIL import Image


def _media(path: Path) -> dict:
    container = av.open(str(path))
    video = container.streams.video[0] if container.streams.video else None
    audio = container.streams.audio[0] if container.streams.audio else None
    facts = {"path": path.name, "bytes": path.stat().st_size}
    if video is not None:
        facts["width"] = video.width
        facts["height"] = video.height
        if video.duration is not None and video.time_base is not None:
            facts["video_seconds"] = round(float(video.duration * video.time_base), 2)
        facts["fps"] = round(float(video.average_rate), 3) if video.average_rate else None
    if audio is not None and audio.duration is not None and audio.time_base is not None:
        facts["audio_seconds"] = round(float(audio.duration * audio.time_base), 2)
    container.close()
    return facts


def report(episode: Path) -> dict:
    episode = episode.resolve()
    board = json.loads((episode / "03_storyboard" / "storyboard.json").read_text(encoding="utf-8"))
    notes: list[str] = []
    images = []
    for shot in board["shots"]:
        path = episode / shot["image"]
        if not path.exists():
            notes.append(f"Missing {shot['image']}")
            continue
        with Image.open(path) as image:
            images.append({"shot_id": shot["shot_id"], "width": image.width, "height": image.height, "bytes": path.stat().st_size})
            if image.width < 1280 or image.height < 720:
                notes.append(f"{shot['shot_id']} is below 720p ({image.width}x{image.height})")
    final = episode / "09_final_exports" / "bhilni-katha-pilot.mp4"
    motion = episode / "06_animated_clips" / "s08-offering-motion.mp4"
    facts = {
        "episode": episode.name,
        "shots": len(board["shots"]),
        "keyframes": images,
        "flags": notes,
        "human_review": board.get("human_review", []),
    }
    if final.exists():
        facts["final"] = _media(final)
        video_seconds = facts["final"].get("video_seconds")
        audio_seconds = facts["final"].get("audio_seconds")
        if facts["final"].get("width") != 1920 or facts["final"].get("height") != 1080:
            notes.append("Final picture is not 1920x1080")
        if video_seconds and audio_seconds and abs(video_seconds - audio_seconds) > 1.5:
            notes.append(f"Picture and voice differ by {abs(video_seconds - audio_seconds):.1f}s")
    else:
        notes.append("Final film is not rendered yet")
    if motion.exists():
        facts["motion_sample"] = _media(motion)
    facts["flags"] = notes
    out = episode / "10_quality_reports" / "qc.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(facts, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return facts
