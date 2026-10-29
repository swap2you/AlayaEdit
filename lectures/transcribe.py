"""Original-language transcription with word timings.

This follows the same shape as production tools such as ClipTo, Whisper, and
Gemini Transcribe: decode the audio, keep word times, and do not translate
inside the speech model. Translation is a later pass so the original wording
stays available.
"""

from __future__ import annotations

import json
import os
from pathlib import Path

from faster_whisper import WhisperModel

from lectures.audio import decode_lecture


def _cuda_dll_paths() -> list[Path]:
    import importlib.util

    found = []
    for package in ("nvidia.cublas", "nvidia.cuda_nvrtc", "nvidia.cudnn"):
        spec = importlib.util.find_spec(package)
        if not spec or not spec.submodule_search_locations:
            continue
        for folder in spec.submodule_search_locations:
            binary = Path(folder) / "bin"
            if binary.exists():
                found.append(binary)
    return found


def _prepare_cuda() -> None:
    for folder in _cuda_dll_paths():
        if hasattr(os, "add_dll_directory"):
            os.add_dll_directory(str(folder))
        os.environ["PATH"] = str(folder) + os.pathsep + os.environ.get("PATH", "")

HINDI_PROMPT = (
    "यह हिंदी प्रवचन है। वक्ता राधा गोविंद स्वामी महाराज हैं। "
    "यशोदा, नंद, कृष्ण, वृंदावन, वात्सल्य।"
)


def _device() -> tuple[str, str]:
    try:
        import ctranslate2

        _prepare_cuda()
        if ctranslate2.get_cuda_device_count() > 0:
            return "cuda", "int8"
    except Exception:
        pass
    return "cpu", "int8"


def transcribe_lecture(
    audio: Path,
    out_dir: Path,
    *,
    model_name: str = "large-v3",
    language: str | None = None,
    condition_on_previous_text: bool = False,
    clip_start: float = 0.0,
    clip_end: float | None = None,
    prompt: str | None = None,
) -> dict:
    out_dir.mkdir(parents=True, exist_ok=True)
    samples = decode_lecture(audio)
    if clip_start or clip_end is not None:
        start_index = int(clip_start * 16000)
        end_index = int(clip_end * 16000) if clip_end is not None else len(samples)
        samples = samples[start_index:end_index]
    device, compute_type = _device()
    if prompt is None:
        prompt = HINDI_PROMPT if language in (None, "hi") else None

    def start(use_device: str, use_compute: str):
        model = WhisperModel(model_name, device=use_device, compute_type=use_compute)
        return model.transcribe(
            samples,
            language=language,
            task="transcribe",
            word_timestamps=True,
            vad_filter=True,
            vad_parameters={"min_silence_duration_ms": 500},
            beam_size=5,
            temperature=0.0,
            condition_on_previous_text=condition_on_previous_text,
            hallucination_silence_threshold=2.0,
            initial_prompt=prompt,
        )

    try:
        segments, info = start(device, compute_type)
        first = next(segments)
    except (RuntimeError, StopIteration) as exc:
        if isinstance(exc, StopIteration):
            raise RuntimeError("The speech model returned no audio segments.") from exc
        device, compute_type = "cpu", "int8"
        segments, info = start(device, compute_type)
        first = next(segments)

    words: list[dict] = []
    words_path = out_dir / "words.jsonl"
    with words_path.open("w", encoding="utf-8") as handle:
        upcoming = iter(segments)
        segment = first
        while segment is not None:
            for word in segment.words or []:
                row = {
                    "word": word.word,
                    "start": round(float(word.start) + clip_start, 3),
                    "end": round(float(word.end) + clip_start, 3),
                    "probability": round(float(word.probability), 4),
                }
                words.append(row)
                handle.write(json.dumps(row, ensure_ascii=False) + "\n")
            handle.flush()
            print(
                f"{segment.start + clip_start:8.1f}s  {segment.text.strip()}",
                flush=True,
            )
            segment = next(upcoming, None)
    return {
        "language": info.language,
        "language_probability": round(float(info.language_probability), 4),
        "duration": round(float(info.duration), 3),
        "device": device,
        "compute_type": compute_type,
        "model": model_name,
        "words": words,
    }
