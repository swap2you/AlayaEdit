"""Transcribe a lecture link or a local file into a timed original-language transcript."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from rich.console import Console

from lectures.ingest import lecture_slug, resolve_source
from lectures.timeline import build_cues, build_seconds, cues_to_srt, review_items
from lectures.transcribe import transcribe_lecture
from lectures.validate import validate_timeline

console = Console()


def _write_review(path: Path, items: list[dict], problems: list[str]) -> None:
    lines = [
        "# Listen to these spots",
        "",
        "The transcript covers every second. These rows are the places the speech model was unsure, or where a long quiet stretch might hide soft speech.",
        "A person can play the lecture at the start time and type what they hear.",
        "",
    ]
    if problems:
        lines.append("## Checks that did not pass")
        lines.append("")
        lines.extend(f"- {problem}" for problem in problems)
        lines.append("")
    if not items:
        lines.append("No low-confidence words and no long gaps were found.")
    else:
        lines.append("| Start | End | Why | What the model heard |")
        lines.append("|---:|---:|---|---|")
        for item in items:
            text = str(item["text"]).replace("|", "/")
            lines.append(
                f"| {item['start']:.1f} | {item['end']:.1f} | {item['kind']} | {text} |"
            )
    lines.append("")
    path.write_text("\n".join(lines), encoding="utf-8")


def transcribe_source(
    source: str,
    output: Path,
    *,
    fallback: Path | None = None,
    language: str | None = None,
    model_name: str = "large-v3",
    prompt: str | None = None,
) -> Path:
    output.mkdir(parents=True, exist_ok=True)
    audio, origin = resolve_source(source, output, fallback)
    console.print(f"Audio: {audio}")
    console.print(f"From: {origin}")
    heard = transcribe_lecture(
        audio, output, model_name=model_name, language=language, prompt=prompt
    )
    words = heard["words"]
    duration = float(heard["duration"])
    seconds = build_seconds(words, duration)
    cues = build_cues(words)
    reviews = review_items(words, duration)
    problems = validate_timeline(words, seconds, duration, heard["language"] or "")

    (output / "original.srt").write_text(cues_to_srt(cues), encoding="utf-8")
    (output / "seconds.jsonl").write_text(
        "\n".join(json.dumps(row, ensure_ascii=False) for row in seconds) + "\n",
        encoding="utf-8",
    )
    meta = {
        "source": source,
        "origin": origin,
        "audio": str(audio),
        "language": heard["language"],
        "language_probability": heard["language_probability"],
        "duration_seconds": duration,
        "model": heard["model"],
        "device": heard["device"],
        "word_count": len(words),
        "cue_count": len(cues),
        "review_count": len(reviews),
        "validation_problems": problems,
        "english": "not_yet",
    }
    (output / "meta.json").write_text(json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8")
    (output / "cues.json").write_text(json.dumps(cues, ensure_ascii=False, indent=2), encoding="utf-8")
    _write_review(output / "REVIEW.md", reviews, problems)
    console.print(
        f"Language {heard['language']} ({heard['language_probability']}), "
        f"{duration / 60:.1f} min, {len(words)} words, {len(reviews)} spots to review."
    )
    if problems:
        console.print("[yellow]Validation still has items. See REVIEW.md.[/yellow]")
        for problem in problems:
            console.print(f"- {problem}")
    return output


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="media-lecture",
        description=(
            "Transcribe a lecture from a link or a local file. "
            "The first pass is the original language, with a time on every word and every second."
        ),
    )
    parser.add_argument("source", help="Web link or local audio/video path")
    parser.add_argument("-o", "--output", type=Path, help="Folder for the transcript files")
    parser.add_argument("--fallback", type=Path, help="Local file to use if the link cannot be downloaded")
    parser.add_argument("--language", help="Force a language code such as hi or en. Default is detect.")
    parser.add_argument("--model", default="large-v3", help="Whisper model name")
    parser.add_argument("--prompt", help="Hint for names and the katha. Hindi spelling, not a translation.")
    args = parser.parse_args(argv)
    output = args.output or Path("output") / "lectures" / lecture_slug(args.source)
    try:
        transcribe_source(
            args.source,
            output,
            fallback=args.fallback,
            language=args.language,
            model_name=args.model,
            prompt=args.prompt,
        )
    except Exception as exc:
        console.print(f"[red]{exc}[/red]")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
