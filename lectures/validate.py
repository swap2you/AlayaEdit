"""Check that the timeline covers the lecture and unsure words are listed for a person."""

from __future__ import annotations

def validate_timeline(words: list[dict], seconds: list[dict], duration: float, language: str) -> list[str]:
    problems: list[str] = []
    expected = int(duration) + 1
    if len(seconds) < expected:
        problems.append(f"Timeline has {len(seconds)} seconds; the audio is {expected} seconds.")
    numbers = [row["second"] for row in seconds]
    if numbers != list(range(len(seconds))):
        problems.append("The second-by-second timeline is not continuous.")
    for row in seconds:
        if row["status"] == "silence" and row["text"]:
            problems.append(f"Second {row['second']} is marked silence but has text.")
        if row["status"] == "speech" and not row["text"]:
            problems.append(f"Second {row['second']} is marked speech but has no text.")
    for word in words:
        if float(word["start"]) < -0.05 or float(word["end"]) > duration + 1:
            problems.append(f"Word timing is outside the audio: {word['word']!r}")
            break
    if language.startswith("hi"):
        letters = [ch for word in words for ch in word["word"] if ch.isalpha()]
        devanagari = [ch for ch in letters if "\u0900" <= ch <= "\u097f"]
        if letters and len(devanagari) / len(letters) < 0.4:
            problems.append(
                "This was detected as Hindi, but most of the letters are not Devanagari. Listen to the opening."
            )
    return problems
