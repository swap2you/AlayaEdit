"""Turn word timings into a timeline that covers every second of the lecture."""

from __future__ import annotations

LOW_WORD_PROBABILITY = 0.55
LONG_GAP_SECONDS = 12.0


def _overlaps(word: dict, second: int) -> bool:
    return float(word["start"]) < second + 1 and float(word["end"]) > second


def words_for_second(words: list[dict], second: int) -> list[dict]:
    return [word for word in words if _overlaps(word, second)]


def build_seconds(words: list[dict], duration: float) -> list[dict]:
    """One record per second, from 0 through the last second that contains audio."""
    last = max(int(duration), 0)
    if words:
        last = max(last, int(float(words[-1]["end"])))
    rows = []
    for second in range(last + 1):
        heard = words_for_second(words, second)
        text = "".join(word["word"] for word in heard).strip()
        low = [word for word in heard if float(word.get("probability") or 0) < LOW_WORD_PROBABILITY]
        if not heard:
            status = "silence"
        elif low:
            status = "review"
        else:
            status = "speech"
        rows.append(
            {
                "second": second,
                "status": status,
                "text": text,
                "words": [
                    {
                        "word": word["word"],
                        "start": word["start"],
                        "end": word["end"],
                        "probability": word["probability"],
                    }
                    for word in heard
                ],
            }
        )
    return rows


def review_items(words: list[dict], duration: float) -> list[dict]:
    """Places a person should listen, because the model was unsure or a long gap appeared."""
    items: list[dict] = []
    low = [word for word in words if float(word.get("probability") or 0) < LOW_WORD_PROBABILITY]
    group: list[dict] = []

    def flush() -> None:
        if not group:
            return
        items.append(
            {
                "kind": "low_confidence",
                "start": group[0]["start"],
                "end": group[-1]["end"],
                "text": "".join(word["word"] for word in group).strip(),
            }
        )
        group.clear()

    for word in low:
        if group and float(word["start"]) - float(group[-1]["end"]) > 1.5:
            flush()
        group.append(word)
    flush()

    previous_end = 0.0
    for word in words:
        gap = float(word["start"]) - previous_end
        if gap >= LONG_GAP_SECONDS:
            items.append(
                {
                    "kind": "long_gap",
                    "start": round(previous_end, 3),
                    "end": word["start"],
                    "text": "Long quiet stretch. Listen in case soft speech was missed.",
                }
            )
        previous_end = float(word["end"])
    if duration - previous_end >= LONG_GAP_SECONDS:
        items.append(
            {
                "kind": "long_gap",
                "start": round(previous_end, 3),
                "end": round(duration, 3),
                "text": "Long quiet stretch at the end. Listen in case soft speech was missed.",
            }
        )
    return items


def build_cues(words: list[dict], max_seconds: float = 8.0) -> list[dict]:
    """Readable original-language lines. Timestamps stay on the words underneath."""
    cues: list[dict] = []
    bucket: list[dict] = []

    def flush() -> None:
        if not bucket:
            return
        cues.append(
            {
                "start": bucket[0]["start"],
                "end": bucket[-1]["end"],
                "text": "".join(word["word"] for word in bucket).strip(),
                "confidence": min(float(word.get("probability") or 0) for word in bucket),
            }
        )
        bucket.clear()

    for word in words:
        if bucket and float(word["start"]) - float(bucket[0]["start"]) >= max_seconds:
            flush()
        if bucket and float(word["start"]) - float(bucket[-1]["end"]) > 1.2:
            flush()
        bucket.append(word)
        token = word["word"].rstrip()
        if token.endswith(("।", "?", "!", ".")):
            flush()
    flush()
    return cues


def format_timestamp(seconds: float) -> str:
    total_ms = max(int(round(seconds * 1000)), 0)
    hours, rem = divmod(total_ms, 3_600_000)
    minutes, rem = divmod(rem, 60_000)
    secs, ms = divmod(rem, 1000)
    return f"{hours:02d}:{minutes:02d}:{secs:02d},{ms:03d}"


def cues_to_srt(cues: list[dict], text_key: str = "text") -> str:
    blocks = []
    for index, cue in enumerate(cues, start=1):
        blocks.append(
            "\n".join(
                [
                    str(index),
                    f"{format_timestamp(cue['start'])} --> {format_timestamp(cue['end'])}",
                    str(cue.get(text_key) or "").strip(),
                    "",
                ]
            )
        )
    return "\n".join(blocks)
