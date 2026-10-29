from __future__ import annotations

import argparse
import asyncio
import sys
from pathlib import Path

from rich.console import Console
from rich.prompt import Prompt
from rich.table import Table

from downloader.engine import DownloadEngine

console = Console()


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="media-download",
        description=(
            "Download public videos/images from Facebook, Instagram, YouTube, "
            "TikTok, and other yt-dlp supported sites. Pass a single media URL "
            "or a page/profile/reels tab URL for bulk download."
        ),
    )
    parser.add_argument("url", nargs="?", help="Source URL (page, profile, reel, or single media)")
    parser.add_argument(
        "-o",
        "--output",
        help="Target folder for downloads",
    )
    parser.add_argument(
        "-n",
        "--limit",
        type=int,
        default=None,
        help="Max items to download (use small number to validate)",
    )
    parser.add_argument(
        "-c",
        "--concurrency",
        type=int,
        default=3,
        help="Parallel downloads (default: 3)",
    )
    parser.add_argument(
        "--cookies-from-browser",
        choices=["chrome", "edge", "firefox", "brave", "chromium"],
        help="Optional: reuse browser cookies for sites that gate public media",
    )
    parser.add_argument(
        "--cookies",
        type=Path,
        help="Optional Netscape cookies.txt path",
    )
    parser.add_argument(
        "--no-browse-facebook",
        action="store_true",
        help="Disable headed browser fallback for Facebook page/reels tabs",
    )
    return parser


def _prompt_missing(args: argparse.Namespace) -> argparse.Namespace:
    if not args.url:
        args.url = Prompt.ask("Source URL (page / profile / video)")
    if not args.output:
        default = str(Path.cwd() / "media_library")
        args.output = Prompt.ask("Target folder", default=default)
    return args


def _print_manifest(engine: DownloadEngine) -> None:
    table = Table(title="Download results")
    table.add_column("Status")
    table.add_column("Type")
    table.add_column("Title")
    table.add_column("Path")
    for item in engine.manifest.items.values():
        table.add_row(
            item.status,
            item.media_type,
            (item.title or "")[:60],
            item.local_path or item.error or "",
        )
    console.print(table)


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    args = _prompt_missing(args)

    target = Path(args.output).expanduser().resolve()
    console.print(f"[bold]Source:[/bold] {args.url}")
    console.print(f"[bold]Target:[/bold] {target}")
    if args.limit:
        console.print(f"[bold]Limit:[/bold] {args.limit}")

    engine = DownloadEngine(
        target,
        concurrency=args.concurrency,
        cookies_from_browser=args.cookies_from_browser,
        cookies_file=args.cookies,
        browse_facebook=not args.no_browse_facebook,
        on_progress=lambda msg: console.print(f"- {msg}"),
    )

    try:
        asyncio.run(engine.run(args.url, limit=args.limit))
    except KeyboardInterrupt:
        console.print("[yellow]Interrupted[/yellow]")
        return 130
    except TimeoutError as exc:
        console.print(f"[red]{exc}[/red]")
        console.print(
            "Re-run the same command and complete Facebook login in the browser window "
            "so the reels tab can lazy-load beyond the first page."
        )
        return 2

    _print_manifest(engine)
    ok = any(i.status == "downloaded" for i in engine.manifest.items.values())
    return 0 if ok or not engine.manifest.items else 1


if __name__ == "__main__":
    sys.exit(main())
