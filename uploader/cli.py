from __future__ import annotations

import argparse
import sys
from pathlib import Path

from rich.console import Console
from rich.prompt import Confirm, Prompt
from rich.table import Table

from shared.manifest import Manifest
from uploader.browser_scheduler import BusinessSuiteScheduler
from uploader.config import (
    load_business_config,
    load_schedule_config,
    plan_slots,
)
from uploader.import_library import import_folder

console = Console()


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="media-upload",
        description=(
            "Schedule local media into Meta Business Suite Planner. "
            "You complete Facebook SSO in the headed browser; the tool then "
            "drives Create -> attach media -> set date/time -> Schedule."
        ),
    )
    parser.add_argument(
        "library",
        nargs="?",
        help="Media library folder containing manifest.json (from downloader)",
    )
    parser.add_argument(
        "--from-folder",
        type=Path,
        help="Import videos/images from this folder into a library first",
    )
    parser.add_argument(
        "--business-config",
        type=Path,
        default=Path("config/business_suite.yaml"),
        help="Business Suite URLs / IDs",
    )
    parser.add_argument(
        "--schedule-config",
        type=Path,
        default=Path("config/schedule.yaml"),
        help="Posts-per-day / interval schedule",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=1,
        help="How many items to schedule this run (default: 1 for safe testing)",
    )
    parser.add_argument(
        "--explore",
        action="store_true",
        help="Only open Business Suite + Planner after login (no scheduling)",
    )
    parser.add_argument(
        "--live",
        action="store_true",
        help="Actually click Schedule (default is dry-run)",
    )
    parser.add_argument(
        "--yes",
        "-y",
        action="store_true",
        help="Skip confirmation prompts (still waits for SSO in browser)",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if not args.business_config.exists():
        console.print(
            f"[red]Missing {args.business_config}.[/red] "
            "Copy config/business_suite.example.yaml -> config/business_suite.yaml"
        )
        return 2
    if not args.schedule_config.exists():
        console.print(
            f"[red]Missing {args.schedule_config}.[/red] "
            "Copy config/schedule.example.yaml -> config/schedule.yaml"
        )
        return 2

    business = load_business_config(args.business_config)
    schedule = load_schedule_config(args.schedule_config)
    dry_run = not args.live
    scheduler = BusinessSuiteScheduler(
        business,
        schedule,
        dry_run=dry_run,
        interactive=not args.yes,
    )

    if args.explore:
        console.print("[bold]Explore mode[/bold]: login, then inspect Planner/Composer.")
        console.print(
            "Your Business Suite home will open. Complete SSO there; session is saved "
            "under .playwright/business-suite-profile for later runs."
        )
        scheduler.explore()
        return 0

    if args.from_folder:
        library = Path(args.library or (Path.cwd() / "media_library_upload")).resolve()
        console.print(f"Importing up to {args.limit} file(s) from {args.from_folder}")
        manifest = import_folder(
            Path(args.from_folder),
            library,
            limit=args.limit,
            prefer_hd=True,
        )
        console.print(f"Library ready: {library} ({len(manifest.items)} items)")
    else:
        if not args.library:
            args.library = Prompt.ask(
                "Media library folder",
                default=str(Path.cwd() / "media_library"),
            )
        library = Path(args.library).expanduser().resolve()
        manifest_path = library / "manifest.json"
        if not manifest_path.exists():
            console.print(
                f"[red]No manifest.json in {library}. "
                "Run the downloader first or use --from-folder.[/red]"
            )
            return 1
        manifest = Manifest(manifest_path)

    ready = manifest.pending_schedule()
    slots = plan_slots(min(len(ready), args.limit), schedule)

    table = Table(title="Upload plan")
    table.add_column("#")
    table.add_column("When")
    table.add_column("File")
    table.add_column("Platforms")
    for idx, (item, when) in enumerate(zip(ready[: args.limit], slots), start=1):
        table.add_row(
            str(idx),
            when.strftime("%Y-%m-%d %H:%M"),
            Path(item.local_path or "").name,
            ", ".join(schedule.platforms),
        )
    console.print(table)
    console.print(f"Mode: {'LIVE' if args.live else 'DRY-RUN'}")

    if args.live and not args.yes:
        if not Confirm.ask("This will schedule real posts. Continue?", default=False):
            return 0

    console.print(
        "[bold yellow]A browser will open. Complete Facebook Business Suite login "
        "if prompted, then leave the window alone while scheduling runs.[/bold yellow]"
    )
    scheduler.run(manifest, limit=args.limit)
    return 0


if __name__ == "__main__":
    sys.exit(main())
