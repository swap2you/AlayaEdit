"""Build the Business Suite queue from downloaded Munch clips.

Already scheduled items are left alone. Clips are ordered folder by folder
so one project finishes before the next one starts.
"""

from __future__ import annotations

import json
from pathlib import Path

from shared.manifest import Manifest, ManifestItem

DEFAULT_SOURCE = Path(
    r"C:\Users\swap2\Downloads\Personal\1. Srila GURUDEV\Video\MuchStudio Short Videos"
)

# Story order: Baal lila parts, then Yugal Geet, then the later projects.
FOLDER_ORDER = [
    "Ballila part1",
    "Ballila part 2",
    "BAALLIL PART 3",
    "Ballila part4",
    "Baal Lila 1 - TY FB Shorts",
    "Baal lila 2- Ut FB TkTok shorts",
    "Yugal Geet 1",
    "Yugal Geet 1 Rev",
    "Yugal Geet 2",
    "Yugal Geet 2 Rev",
    "Yugal Geet 3",
    "Yugal Geet 4",
    "Yugal Geet 6",
    "Yugal Geet 7",
    "Yugal Geet 7 Rev",
    "Yugal Geet 8",
    "AM 1 vlog",
    "AM 1 Mono",
    "Gaura Katha 1",
]


def build_munch_queue(source: Path, library: Path) -> Manifest:
    source = source.expanduser().resolve()
    library = library.expanduser().resolve()
    library.mkdir(parents=True, exist_ok=True)
    catalog = _catalog(source)
    manifest = Manifest(library / "manifest.json")
    manifest.source_url = "https://app.munchstudio.com/studio"
    manifest.target_dir = str(source)

    rank = {name: index for index, name in enumerate(FOLDER_ORDER)}
    folders = sorted(
        {item["folder"] for item in catalog},
        key=lambda name: (rank.get(name, len(FOLDER_ORDER)), name.lower()),
    )
    by_folder: dict[str, list[dict]] = {name: [] for name in folders}
    for item in catalog:
        by_folder[item["folder"]].append(item)

    for folder in folders:
        clips = sorted(by_folder[folder], key=lambda item: item["filename"].lower())
        for clip in clips:
            current = manifest.items.get(clip["id"])
            if current and current.status == "scheduled":
                continue
            manifest.upsert(
                ManifestItem(
                    id=clip["id"],
                    source_url="https://app.munchstudio.com/studio",
                    title=clip["title"],
                    media_type="video",
                    local_path=clip["path"],
                    status="downloaded",
                    platform="munch",
                )
            )
    manifest.save()
    return manifest


def _catalog(source: Path) -> list[dict]:
    listed = source / "munch_manifest.json"
    rows: list[dict] = []
    if listed.exists():
        payload = json.loads(listed.read_text(encoding="utf-8"))
        for item in payload.get("items") or []:
            path = Path(item["path"])
            if path.suffix.lower() != ".mp4" or not path.exists():
                continue
            rows.append(
                {
                    "id": item["id"],
                    "title": item.get("title") or path.stem,
                    "path": str(path),
                    "folder": path.parent.name,
                    "filename": path.name,
                }
            )
    known = {row["path"].lower() for row in rows}
    for path in source.rglob("*.mp4"):
        if path.name.endswith(".part") or str(path).lower() in known:
            continue
        rows.append(
            {
                "id": f"file-{path.stem}",
                "title": path.stem,
                "path": str(path),
                "folder": path.parent.name,
                "filename": path.name,
            }
        )
    return rows
