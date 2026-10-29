from __future__ import annotations

import asyncio
import hashlib
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable

from yt_dlp import YoutubeDL

from shared.manifest import Manifest, ManifestItem
from shared.paths import ensure_dir, platform_from_url, safe_slug


VIDEO_EXTS = {".mp4", ".mkv", ".webm", ".mov", ".m4v", ".avi"}
IMAGE_EXTS = {".jpg", ".jpeg", ".png", ".webp", ".gif"}


@dataclass
class DownloadResult:
    ok: bool
    item_id: str
    path: Path | None = None
    error: str | None = None


def _item_id(url: str, fallback: str = "") -> str:
    digest = hashlib.sha1(url.encode("utf-8")).hexdigest()[:12]
    return f"{safe_slug(fallback)[:24]}_{digest}" if fallback else digest


def _classify_path(path: Path) -> str:
    ext = path.suffix.lower()
    if ext in VIDEO_EXTS:
        return "video"
    if ext in IMAGE_EXTS:
        return "image"
    return "unknown"


def build_ydl_opts(
    outtmpl: str,
    *,
    limit: int | None = None,
    cookies_from_browser: str | None = None,
    cookies_file: Path | None = None,
    quiet: bool = True,
) -> dict[str, Any]:
    opts: dict[str, Any] = {
        "outtmpl": outtmpl,
        "noplaylist": False,
        "ignoreerrors": True,
        "no_warnings": quiet,
        "quiet": quiet,
        "noprogress": quiet,
        "writethumbnail": False,
        "writesubtitles": False,
        # Facebook exposes progressive hd/sd; prefer those to avoid needing ffmpeg.
        "format": "hd/sd/b[ext=mp4]/bv*[ext=mp4]+ba[ext=m4a]/b/bv*+ba",
        "merge_output_format": "mp4",
        # Allow image posts where extractors support them.
        "compat_opts": [],
    }
    if limit is not None and limit > 0:
        opts["playlistend"] = limit
    if cookies_file and cookies_file.exists():
        opts["cookiefile"] = str(cookies_file)
    elif cookies_from_browser:
        opts["cookiesfrombrowser"] = (cookies_from_browser,)
    return opts


def extract_entries(
    url: str,
    *,
    limit: int | None = None,
    cookies_from_browser: str | None = None,
    cookies_file: Path | None = None,
) -> list[dict[str, Any]]:
    opts = build_ydl_opts(
        "%(id)s.%(ext)s",
        limit=limit,
        cookies_from_browser=cookies_from_browser,
        cookies_file=cookies_file,
        quiet=True,
    )
    opts["skip_download"] = True
    opts["extract_flat"] = "in_playlist"

    with YoutubeDL(opts) as ydl:
        info = ydl.extract_info(url, download=False)

    if not info:
        return []

    entries = info.get("entries")
    if entries is None:
        return [info]

    result: list[dict[str, Any]] = []
    for entry in entries:
        if not entry:
            continue
        result.append(entry)
        if limit is not None and len(result) >= limit:
            break
    return result


def _download_one(
    entry_url: str,
    outtmpl: str,
    *,
    cookies_from_browser: str | None,
    cookies_file: Path | None,
) -> tuple[bool, list[Path], str | None]:
    downloaded: list[Path] = []

    def hook(status: dict[str, Any]) -> None:
        if status.get("status") == "finished":
            filename = status.get("filename")
            if filename:
                downloaded.append(Path(filename))

    opts = build_ydl_opts(
        outtmpl,
        cookies_from_browser=cookies_from_browser,
        cookies_file=cookies_file,
        quiet=True,
    )
    opts["noplaylist"] = True
    opts["progress_hooks"] = [hook]

    try:
        with YoutubeDL(opts) as ydl:
            info = ydl.extract_info(entry_url, download=True)
            if info:
                requested = info.get("requested_downloads") or []
                for item in requested:
                    filepath = item.get("filepath")
                    if filepath:
                        path = Path(filepath)
                        if path not in downloaded:
                            downloaded.append(path)
                # Single-file fallback
                if not downloaded and info.get("filename"):
                    downloaded.append(Path(info["filename"]))
                if not downloaded:
                    # Guess from id/ext
                    ext = info.get("ext") or "mp4"
                    vid = info.get("id")
                    if vid:
                        candidate = Path(outtmpl.replace("%(id)s", str(vid)).replace("%(ext)s", str(ext)))
                        # outtmpl may contain path placeholders
                        pass
        return True, downloaded, None
    except Exception as exc:  # noqa: BLE001 - surface any extractor failure
        return False, downloaded, str(exc)


class DownloadEngine:
    def __init__(
        self,
        target_dir: Path,
        *,
        concurrency: int = 3,
        cookies_from_browser: str | None = None,
        cookies_file: Path | None = None,
        browse_facebook: bool = True,
        on_progress: Callable[[str], None] | None = None,
    ) -> None:
        self.target_dir = ensure_dir(target_dir)
        self.concurrency = max(1, concurrency)
        self.cookies_from_browser = cookies_from_browser
        self.cookies_file = cookies_file
        self.browse_facebook = browse_facebook
        self.on_progress = on_progress or (lambda _msg: None)
        self.manifest = Manifest(self.target_dir / "manifest.json")
        self.manifest.target_dir = str(self.target_dir)

    def _outtmpl_for(self, platform: str, source_slug: str) -> str:
        base = ensure_dir(self.target_dir / platform / source_slug)
        staging = ensure_dir(base / "_staging")
        return str(staging / "%(id)s.%(ext)s")

    def _videos_dir(self, platform: str, source_slug: str) -> Path:
        return ensure_dir(self.target_dir / platform / source_slug / "videos")

    def _finalize_file(self, path: Path, platform: str, source_slug: str) -> Path:
        media_type = _classify_path(path)
        bucket = "videos" if media_type == "video" else "images" if media_type == "image" else "other"
        dest_dir = ensure_dir(self.target_dir / platform / source_slug / bucket)
        dest = dest_dir / path.name
        if path.resolve() != dest.resolve():
            if dest.exists():
                path.unlink(missing_ok=True)
                return dest
            path.replace(dest)
        return dest

    def _find_existing_file(self, platform: str, source_slug: str, media_id: str) -> Path | None:
        """Return existing media file for this id if already on disk."""
        base = self.target_dir / platform / source_slug
        if not base.exists():
            return None
        for folder in ("videos", "images", "other", "_staging"):
            folder_path = base / folder
            if not folder_path.exists():
                continue
            for path in folder_path.glob(f"{media_id}.*"):
                if path.is_file() and path.suffix.lower() in VIDEO_EXTS | IMAGE_EXTS:
                    return path
        # Also scan whole target for id.* (flat copies)
        for path in self.target_dir.rglob(f"{media_id}.*"):
            if path.is_file() and path.suffix.lower() in VIDEO_EXTS | IMAGE_EXTS:
                return path
        return None

    def _entry_key(self, entry_url: str, eid: str) -> str:
        # Prefer stable Facebook reel id so skips work across runs.
        from downloader.facebook_enum import reel_id_from_url

        rid = reel_id_from_url(entry_url)
        if rid:
            return rid
        if eid and eid.isdigit():
            return eid
        return _item_id(entry_url, eid)

    def _mark_skipped(
        self,
        *,
        item_key: str,
        entry_url: str,
        title: str,
        path: Path,
        platform: str,
    ) -> DownloadResult:
        self.manifest.upsert(
            ManifestItem(
                id=item_key,
                source_url=entry_url,
                title=str(title),
                media_type=_classify_path(path),
                local_path=str(path),
                status="downloaded",
                platform=platform,
            )
        )
        self.manifest.save()
        self.on_progress(f"Skip existing: {path.name}")
        return DownloadResult(True, item_key, path)

    def _download_entry_sync(
        self,
        entry: dict[str, Any],
        *,
        source_url: str,
        platform: str,
        source_slug: str,
    ) -> DownloadResult:
        """Synchronous single-entry download (safe to call from Playwright thread)."""
        entry_url = entry.get("url") or entry.get("webpage_url") or source_url
        title = entry.get("title") or entry.get("id") or "media"
        eid = str(entry.get("id") or "")
        item_key = self._entry_key(entry_url, eid)
        outtmpl = self._outtmpl_for(platform, source_slug)

        existing = self.manifest.items.get(item_key)
        if existing and existing.status == "downloaded" and existing.local_path:
            if Path(existing.local_path).exists():
                return self._mark_skipped(
                    item_key=item_key,
                    entry_url=entry_url,
                    title=str(title),
                    path=Path(existing.local_path),
                    platform=platform,
                )

        on_disk = self._find_existing_file(platform, source_slug, item_key)
        if on_disk:
            return self._mark_skipped(
                item_key=item_key,
                entry_url=entry_url,
                title=str(title),
                path=on_disk,
                platform=platform,
            )

        self.on_progress(f"Downloading: {item_key}")
        ok, files, error = _download_one(
            entry_url,
            outtmpl,
            cookies_from_browser=self.cookies_from_browser,
            cookies_file=self.cookies_file,
        )
        if not ok or not files:
            self.manifest.upsert(
                ManifestItem(
                    id=item_key,
                    source_url=entry_url,
                    title=str(title),
                    media_type="unknown",
                    status="failed",
                    error=error or "No file produced",
                    platform=platform,
                )
            )
            self.manifest.save()
            return DownloadResult(False, item_key, error=error or "No file produced")

        final_paths = [
            self._finalize_file(path, platform, source_slug)
            for path in files
            if path.exists()
        ]
        primary = next(
            (p for p in final_paths if p.suffix.lower() in VIDEO_EXTS),
            final_paths[0] if final_paths else None,
        )
        media_type = _classify_path(primary) if primary else "unknown"
        self.manifest.upsert(
            ManifestItem(
                id=item_key,
                source_url=entry_url,
                title=str(title),
                media_type=media_type,
                local_path=str(primary) if primary else None,
                status="downloaded" if primary else "failed",
                error=None if primary else "File missing after download",
                platform=platform,
            )
        )
        self.manifest.save()
        return DownloadResult(bool(primary), item_key, primary)

    def _download_entries_sync(
        self,
        entries: list[dict[str, Any]],
        *,
        source_url: str,
        platform: str,
        source_slug: str,
    ) -> list[DownloadResult]:
        results: list[DownloadResult] = []
        with ThreadPoolExecutor(max_workers=self.concurrency) as pool:
            futures = [
                pool.submit(
                    self._download_entry_sync,
                    entry,
                    source_url=source_url,
                    platform=platform,
                    source_slug=source_slug,
                )
                for entry in entries
            ]
            for future in futures:
                results.append(future.result())
        return results

    async def _download_entries(
        self,
        entries: list[dict[str, Any]],
        *,
        source_url: str,
        platform: str,
        source_slug: str,
    ) -> list[DownloadResult]:
        loop = asyncio.get_running_loop()
        return await loop.run_in_executor(
            None,
            lambda: self._download_entries_sync(
                entries,
                source_url=source_url,
                platform=platform,
                source_slug=source_slug,
            ),
        )

    async def _run_facebook_scroll_batches(
        self,
        source_url: str,
        *,
        limit: int | None,
        platform: str,
        source_slug: str,
    ) -> Manifest:
        """Scroll reels tab in batches: harvest -> download -> scroll -> wait -> repeat."""
        from downloader.facebook_enum import harvest_facebook_reels

        cookies_out = self.target_dir / ".cookies" / "facebook_cookies.txt"
        loop = asyncio.get_running_loop()
        total_ok = 0
        total_seen = 0

        def on_batch(batch_urls: list[str], cookie_path: Path | None) -> None:
            nonlocal total_ok, total_seen
            if cookie_path and cookie_path.exists():
                self.cookies_file = cookie_path
            entries = [
                {"id": u.rstrip("/").split("/")[-1], "url": u, "title": u}
                for u in batch_urls
            ]
            total_seen += len(entries)
            self.on_progress(
                f"Downloading batch of {len(entries)} "
                f"(seen {total_seen}{f', limit {limit}' if limit else ''})..."
            )
            # Run sync downloads in this Playwright worker thread (avoids asyncio deadlock).
            results = self._download_entries_sync(
                entries,
                source_url=source_url,
                platform=platform,
                source_slug=source_slug,
            )
            total_ok += sum(1 for result in results if result.ok)

        self.on_progress(
            "Opening Facebook: scroll -> wait for load -> download batch -> repeat "
            "until no new reels appear."
        )

        await loop.run_in_executor(
            None,
            lambda: harvest_facebook_reels(
                source_url,
                limit=limit,
                cookies_out=cookies_out,
                stagnant_scrolls_to_stop=5,
                max_scrolls=200,
                wait_after_scroll_ms=2500,
                on_batch=on_batch,
            ),
        )

        self.on_progress(
            f"Done: {total_ok}/{total_seen} succeeded -> {self.target_dir}"
        )
        self.manifest.save()
        return self.manifest

    async def run(self, source_url: str, *, limit: int | None = None) -> Manifest:
        platform = platform_from_url(source_url)
        source_slug = safe_slug(
            source_url.split("?")[0].rstrip("/").split("/")[-1] or platform
        )
        # Stable slug for FB profile ids
        if "profile.php" in source_url and "id=" in source_url:
            import re as _re

            mid = _re.search(r"[?&]id=(\d+)", source_url)
            if mid:
                source_slug = mid.group(1)

        self.manifest.source_url = source_url
        self.on_progress(f"Extracting entries from {platform}...")

        # Facebook reels/page tabs: scroll-batch harvest (lazy load aware).
        if platform == "facebook" and self.browse_facebook:
            is_collection = any(
                token in source_url
                for token in ("sk=reels_tab", "/reels", "profile.php", "/people/")
            )
            if is_collection:
                return await self._run_facebook_scroll_batches(
                    source_url,
                    limit=limit,
                    platform=platform,
                    source_slug=source_slug,
                )

        loop = asyncio.get_running_loop()
        with ThreadPoolExecutor(max_workers=1) as extract_pool:
            entries = await loop.run_in_executor(
                extract_pool,
                lambda: extract_entries(
                    source_url,
                    limit=limit,
                    cookies_from_browser=self.cookies_from_browser,
                    cookies_file=self.cookies_file,
                ),
            )

        if not entries and platform == "facebook" and self.browse_facebook:
            return await self._run_facebook_scroll_batches(
                source_url,
                limit=limit,
                platform=platform,
                source_slug=source_slug,
            )

        if not entries:
            self.on_progress(
                "No downloadable entries found (private, blocked, or unsupported)."
            )
            self.manifest.save()
            return self.manifest

        if limit is not None:
            entries = entries[:limit]

        self.on_progress(
            f"Found {len(entries)} item(s). Downloading with concurrency={self.concurrency}..."
        )
        results = await self._download_entries(
            entries,
            source_url=source_url,
            platform=platform,
            source_slug=source_slug,
        )
        ok_count = sum(1 for result in results if result.ok)
        self.on_progress(f"Done: {ok_count}/{len(results)} succeeded -> {self.target_dir}")
        self.manifest.save()
        return self.manifest
