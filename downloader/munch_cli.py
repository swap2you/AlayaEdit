from __future__ import annotations

import argparse
import sys
from pathlib import Path

from rich.console import Console

from downloader.munch_studio import download_munch_studio

console = Console()

DEFAULT_DEST = Path(
    r"C:\Users\swap2\Downloads\Personal\1. Srila GURUDEV\Video\MuchStudio Short Videos"
)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="media-munch",
        description=(
            "Sign in to Munch Studio and download generated clips in batches of 10. "
            "Each project is saved in its own folder, keeping the original file names."
        ),
    )
    parser.add_argument(
        "-o",
        "--output",
        type=Path,
        default=DEFAULT_DEST,
        help="Folder that will contain one subfolder per Munch project",
    )
    parser.add_argument(
        "--project",
        help="Only download projects whose title contains this text",
    )
    args = parser.parse_args(argv)
    try:
        download_munch_studio(args.output, project_filter=args.project)
    except TimeoutError as exc:
        console.print(f"[red]{exc}[/red]")
        return 2
    except KeyboardInterrupt:
        console.print("[yellow]Interrupted[/yellow]")
        return 130
    return 0


if __name__ == "__main__":
    sys.exit(main())
