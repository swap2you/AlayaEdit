"""Decode lecture audio to the 16 kHz mono samples Whisper expects.

PyAV 19 removed the metadata_errors argument that faster-whisper still passes,
so this decoder opens the file directly.
"""

from __future__ import annotations

import gc
import io
from pathlib import Path

import av
import numpy as np
from faster_whisper.audio import _group_frames, _ignore_invalid_frames, _resample_frames


def decode_lecture(path: Path, sampling_rate: int = 16000) -> np.ndarray:
    resampler = av.audio.resampler.AudioResampler(
        format="s16",
        layout="mono",
        rate=sampling_rate,
    )
    raw = io.BytesIO()
    dtype = None
    with av.open(str(path), mode="r") as container:
        frames = container.decode(audio=0)
        frames = _ignore_invalid_frames(frames)
        frames = _group_frames(frames, 500000)
        frames = _resample_frames(frames, resampler)
        for frame in frames:
            array = frame.to_ndarray()
            dtype = array.dtype
            raw.write(array)
    del resampler
    gc.collect()
    audio = np.frombuffer(raw.getbuffer(), dtype=dtype)
    return audio.astype(np.float32) / 32768.0
