from __future__ import annotations

import hashlib
import shutil
from pathlib import Path

from shared.manifest import Manifest, ManifestItem
from shared.paths import ensure_dir, safe_slug

VIDEO_EXTS = {".mp4", ".mkv", ".webm", ".mov", ".m4v", ".avi"}
IMAGE_EXTS = {".jpg", ".jpeg", ".png", ".webp", ".gif"}


def _media_type(path: Path) -> str:
    ext = path.suffix.lower()
    if ext in VIDEO_EXTS:
        return "video"
    if ext in IMAGE_EXTS:
        return "image"
    return "unknown"


def import_folder(
    source_dir: Path,
    library_dir: Path,
    *,
    limit: int = 5,
    prefer_hd: bool = True,
    max_bytes: int = 40_000_000,
    copy_files: bool = True,
) -> Manifest:
    """
    Build a media library + manifest from an existing folder of videos/images.
    Copies into library with short names to avoid FB path/filename issues.
    """
    source_dir = source_dir.expanduser().resolve()
    library_dir = ensure_dir(library_dir.expanduser().resolve())
    videos_dir = ensure_dir(library_dir / "local" / "batch" / "videos")
    images_dir = ensure_dir(library_dir / "local" / "batch" / "images")

    files = [
        p
        for p in source_dir.iterdir()
        if p.is_file() and p.suffix.lower() in VIDEO_EXTS | IMAGE_EXTS
    ]

    def score(path: Path) -> tuple[int, int, str]:
        size = path.stat().st_size
        hd = 0 if (prefer_hd and "HD" in path.name.upper() and size <= max_bytes) else 1
        oversized = 0 if size <= max_bytes else 1
        return (hd, oversized, path.name.lower())

    files = sorted(files, key=score)[:limit]

    manifest = Manifest(library_dir / "manifest.json")
    manifest.source_url = str(source_dir)
    manifest.target_dir = str(library_dir)
    manifest.items.clear()

    for idx, src in enumerate(files, start=1):
        media_type = _media_type(src)
        dest_dir = videos_dir if media_type == "video" else images_dir
        short_name = f"video_{idx:02d}{src.suffix.lower()}" if media_type == "video" else f"image_{idx:02d}{src.suffix.lower()}"
        dest = dest_dir / short_name
        if copy_files:
            shutil.copy2(src, dest)
            local_path = dest
        else:
            local_path = src

        item_id = hashlib.sha1(str(src).encode("utf-8")).hexdigest()[:12]
        title = safe_slug(src.stem[:40]) or short_name
        manifest.upsert(
            ManifestItem(
                id=item_id,
                source_url=str(src),
                title=title.replace("_", " "),
                media_type=media_type,
                local_path=str(local_path),
                status="downloaded",
                platform="local",
            )
        )

    manifest.save()
    return manifest
