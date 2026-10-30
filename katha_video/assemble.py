"""Cut an authorized excerpt and lay it under still pictures with a slow camera move.

The move is a push, a pull, or a small sideways drift. Faces are not regenerated,
so they cannot melt between frames. Software H.264 is used on purpose, so a
lecture hearing can keep the NVIDIA GPU.
"""

from __future__ import annotations

import csv
import json
import subprocess
from pathlib import Path

import av
import numpy as np
from PIL import Image

FPS = 24
SIZE = (1920, 1080)
MODES = ("in", "left", "out", "right")


def load_storyboard(episode: Path) -> dict:
    path = episode / "03_storyboard" / "storyboard.json"
    return json.loads(path.read_text(encoding="utf-8"))


def write_csv(episode: Path, board: dict) -> Path:
    path = episode / "03_storyboard" / "storyboard.csv"
    fields = [
        "shot_id",
        "audio_start",
        "audio_end",
        "exact_spoken_text",
        "location",
        "characters",
        "shot_size",
        "camera_angle",
        "action",
        "emotion",
        "lighting",
        "image_prompt",
        "motion_prompt",
        "negative_prompt",
        "duration",
        "continuity_notes",
        "status",
    ]
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        for shot in board["shots"]:
            row = {key: shot.get(key, "") for key in fields}
            if isinstance(row["characters"], list):
                row["characters"] = ", ".join(row["characters"])
            writer.writerow(row)
    return path


def cut_audio(source: Path, dest: Path, start: float, end: float) -> float:
    dest.parent.mkdir(parents=True, exist_ok=True)
    inp = av.open(str(source))
    in_stream = inp.streams.audio[0]
    out = av.open(str(dest), "w")
    out_stream = out.add_stream("aac", rate=44100)
    out_stream.layout = "mono"
    resampler = av.audio.resampler.AudioResampler(format="fltp", layout="mono", rate=44100)
    last = start
    for frame in inp.decode(in_stream):
        if frame.pts is None:
            continue
        when = float(frame.pts * in_stream.time_base)
        if when < start:
            continue
        if when >= end:
            break
        last = when
        for resampled in resampler.resample(frame):
            resampled.pts = None
            for packet in out_stream.encode(resampled):
                out.mux(packet)
    for packet in out_stream.encode(None):
        out.mux(packet)
    out.close()
    inp.close()
    return last - start


def _cover(image: Image.Image) -> np.ndarray:
    image = image.convert("RGB")
    width, height = image.size
    scale = max(SIZE[0] / width, SIZE[1] / height, 1.0)
    # A little extra resolution so the push-in does not soften the face.
    scale *= 1.2
    resized = image.resize(
        (max(int(width * scale), SIZE[0]), max(int(height * scale), SIZE[1])),
        Image.Resampling.LANCZOS,
    )
    return np.asarray(resized)


def _crop(frame: np.ndarray, index: int, count: int, mode: str) -> np.ndarray:
    height, width = frame.shape[:2]
    progress = 0.0 if count <= 1 else index / (count - 1)
    if mode == "in":
        zoom, px, py = 1.0 + 0.08 * progress, 0.5, 0.46
    elif mode == "out":
        zoom, px, py = 1.08 - 0.08 * progress, 0.5, 0.5
    elif mode == "left":
        zoom, px, py = 1.07, 0.40 + 0.20 * progress, 0.48
    else:
        zoom, px, py = 1.07, 0.60 - 0.20 * progress, 0.50
    crop_h = int(height / zoom)
    crop_w = int(crop_h * SIZE[0] / SIZE[1])
    if crop_w > width:
        crop_w = int(width / zoom)
        crop_h = int(crop_w * SIZE[1] / SIZE[0])
    crop_w = min(crop_w, width)
    crop_h = min(crop_h, height)
    x = int((width - crop_w) * px)
    y = int((height - crop_h) * py)
    x = max(0, min(x, width - crop_w))
    y = max(0, min(y, height - crop_h))
    crop = frame[y : y + crop_h, x : x + crop_w]
    picture = Image.fromarray(crop).resize(SIZE, Image.Resampling.BILINEAR)
    return np.asarray(picture)


def render_video(episode: Path, board: dict, dest: Path) -> int:
    dest.parent.mkdir(parents=True, exist_ok=True)
    shots = board["shots"]
    span = float(board["audio_end"]) - float(board["audio_start"])
    total = max(1, round(span * FPS))
    raw = [float(shot["duration"]) * FPS for shot in shots]
    counts = [max(1, int(value)) for value in raw]
    counts[-1] += total - sum(counts)
    if counts[-1] < 1:
        counts[0] += counts[-1] - 1
        counts[-1] = 1

    container = av.open(str(dest), "w")
    stream = container.add_stream("libx264", rate=FPS)
    stream.width = SIZE[0]
    stream.height = SIZE[1]
    stream.pix_fmt = "yuv420p"
    stream.options = {"crf": "18", "preset": "veryfast"}
    written = 0
    for shot_index, shot in enumerate(shots):
        image_path = episode / shot["image"]
        source = _cover(Image.open(image_path))
        mode = MODES[shot_index % len(MODES)]
        count = counts[shot_index]
        print(f"  {shot['shot_id']}  {count / FPS:.1f}s  {mode}  {image_path.name}", flush=True)
        for index in range(count):
            picture = _crop(source, index, count, mode)
            frame = av.VideoFrame.from_ndarray(picture, format="rgb24")
            frame.pts = written
            written += 1
            for packet in stream.encode(frame):
                container.mux(packet)
    for packet in stream.encode(None):
        container.mux(packet)
    container.close()
    return written


def ffmpeg_bin() -> Path:
    root = Path(__file__).resolve().parents[1] / "tools" / "ffmpeg"
    found = sorted(root.rglob("ffmpeg.exe"))
    if not found:
        raise FileNotFoundError(f"ffmpeg.exe not under {root}")
    return found[0]


def _duration(path: Path) -> float | None:
    if not path.exists():
        return None
    container = av.open(str(path))
    stream = container.streams.video[0] if container.streams.video else container.streams.audio[0]
    seconds = None
    if stream.duration is not None and stream.time_base is not None:
        seconds = float(stream.duration * stream.time_base)
    container.close()
    return seconds


def mux(video: Path, audio: Path, dest: Path) -> None:
    dest.parent.mkdir(parents=True, exist_ok=True)
    command = [
        str(ffmpeg_bin()),
        "-y",
        "-i",
        str(video),
        "-i",
        str(audio),
        "-c:v",
        "copy",
        "-c:a",
        "copy",
        "-shortest",
        "-movflags",
        "+faststart",
        str(dest),
    ]
    subprocess.run(command, check=True, capture_output=True)


def assemble(episode: Path) -> Path:
    episode = episode.resolve()
    board = load_storyboard(episode)
    write_csv(episode, board)
    source = episode / board["source_audio"]
    narration = episode / "07_audio_mix" / "narration.m4a"
    silent = episode / "08_edit_project" / "picture.mp4"
    final = episode / "09_final_exports" / "bhilni-katha-pilot.mp4"
    expected = float(board["audio_end"]) - float(board["audio_start"])
    print(f"Audio {board['audio_start']:.2f}–{board['audio_end']:.2f} from {source.name}", flush=True)
    heard = _duration(narration)
    if heard is not None and abs(heard - expected) < 1.0:
        print("Audio already cut", flush=True)
    else:
        cut_audio(source, narration, float(board["audio_start"]), float(board["audio_end"]))
    seen = _duration(silent)
    if seen is not None and abs(seen - expected) < 1.0:
        print("Picture already rendered", flush=True)
    else:
        print("Picture", flush=True)
        render_video(episode, board, silent)
    print("Join", flush=True)
    mux(silent, narration, final)
    return final
