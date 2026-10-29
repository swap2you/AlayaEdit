from __future__ import annotations

import re
from pathlib import Path
from urllib.parse import urlparse


def ensure_dir(path: Path) -> Path:
    path.mkdir(parents=True, exist_ok=True)
    return path


def safe_slug(value: str, max_len: int = 80) -> str:
    cleaned = re.sub(r"[^\w\-]+", "_", value.strip(), flags=re.UNICODE)
    cleaned = re.sub(r"_+", "_", cleaned).strip("_")
    return (cleaned or "media")[:max_len]


def platform_from_url(url: str) -> str:
    host = (urlparse(url).hostname or "").lower()
    if "facebook.com" in host or "fb.watch" in host or host.endswith("fb.com"):
        return "facebook"
    if "instagram.com" in host:
        return "instagram"
    if "youtube.com" in host or "youtu.be" in host:
        return "youtube"
    if "tiktok.com" in host:
        return "tiktok"
    if "twitter.com" in host or "x.com" in host:
        return "x"
    if "vimeo.com" in host:
        return "vimeo"
    return safe_slug(host.split(".")[0] if host else "web")
