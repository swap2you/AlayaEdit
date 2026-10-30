"""Build an illustrated katha episode from a storyboard already on disk."""

from __future__ import annotations

import argparse
from pathlib import Path

from katha_video.assemble import assemble
from katha_video.qc import report


def main() -> None:
    parser = argparse.ArgumentParser(prog="alaya-katha")
    commands = parser.add_subparsers(dest="command", required=True)

    build = commands.add_parser("assemble", help="Cut the excerpt and render the film")
    build.add_argument("episode", type=Path)

    check = commands.add_parser("qc", help="Check files, size, and duration")
    check.add_argument("episode", type=Path)

    args = parser.parse_args()
    episode = args.episode
    if args.command == "assemble":
        final = assemble(episode)
        facts = report(episode)
        print(final)
        if facts["flags"]:
            print("Review:")
            for flag in facts["flags"]:
                print(f"- {flag}")
    else:
        facts = report(episode)
        print(facts["final"] if "final" in facts else "no film yet")
        for flag in facts["flags"]:
            print(f"- {flag}")


if __name__ == "__main__":
    main()
