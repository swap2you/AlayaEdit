"""Copy a local lecture or download a direct audio/video link."""

from __future__ import annotations

import shutil
import urllib.request
from pathlib import Path
from urllib.parse import unquote, urlparse

from shared.paths import safe_slug

USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"
)


def _filename_from_url(url: str) -> str:
    name = Path(unquote(urlparse(url).path)).name
    return name or "lecture"


def download_url(url: str, dest_dir: Path) -> Path:
    dest_dir.mkdir(parents=True, exist_ok=True)
    dest = dest_dir / _filename_from_url(url)
    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(request, timeout=180) as response, dest.open("wb") as handle:
        shutil.copyfileobj(response, handle, length=1024 * 1024)
    if dest.stat().st_size < 100_000:
        raise RuntimeError(f"Download looks empty ({dest.stat().st_size} bytes): {url}")
    return dest


def resolve_source(source: str, work_dir: Path, fallback: Path | None = None) -> tuple[Path, str]:
    """Return the audio file and where it came from.

    A web link is tried first. ``fallback`` is used only when that download fails.
    """
    path = Path(source)
    if path.exists():
        return path, str(path)
    if source.startswith("http://") or source.startswith("https://"):
        try:
            return download_url(source, work_dir / "source"), source
        except Exception as exc:
            if fallback and fallback.exists():
                return fallback, f"{source} (download failed: {exc}; used local file)"
            raise
    raise FileNotFoundError(source)


def lecture_slug(source: str) -> str:
    if source.startswith("http://") or source.startswith("https://"):
        return safe_slug(Path(unquote(urlparse(source).path)).stem or "lecture")
    return safe_slug(Path(source).stem or "lecture")
