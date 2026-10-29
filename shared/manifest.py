from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


@dataclass
class ManifestItem:
    id: str
    source_url: str
    title: str
    media_type: str  # video | image | unknown
    local_path: str | None = None
    status: str = "pending"  # pending | downloaded | failed | queued | scheduled | published
    error: str | None = None
    platform: str | None = None
    scheduled_for: str | None = None
    updated_at: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )

    def touch(self) -> None:
        self.updated_at = datetime.now(timezone.utc).isoformat()


class Manifest:
    """Tracks downloaded media and upload/schedule state."""

    def __init__(self, path: Path) -> None:
        self.path = path
        self.items: dict[str, ManifestItem] = {}
        self.source_url: str | None = None
        self.target_dir: str | None = None
        if path.exists():
            self.load()

    def load(self) -> None:
        data = json.loads(self.path.read_text(encoding="utf-8"))
        self.source_url = data.get("source_url")
        self.target_dir = data.get("target_dir")
        self.items = {
            key: ManifestItem(**value) for key, value in data.get("items", {}).items()
        }

    def save(self) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        payload: dict[str, Any] = {
            "source_url": self.source_url,
            "target_dir": self.target_dir,
            "updated_at": datetime.now(timezone.utc).isoformat(),
            "items": {key: asdict(item) for key, item in self.items.items()},
        }
        text = json.dumps(payload, indent=2)
        tmp = self.path.with_suffix(self.path.suffix + ".tmp")
        last_error: Exception | None = None
        for attempt in range(5):
            try:
                tmp.write_text(text, encoding="utf-8")
                tmp.replace(self.path)
                return
            except OSError as exc:  # Windows can transiently lock the file
                last_error = exc
                import time

                time.sleep(0.4 * (attempt + 1))
        if last_error:
            raise last_error

    def upsert(self, item: ManifestItem) -> ManifestItem:
        item.touch()
        self.items[item.id] = item
        return item

    def downloaded(self) -> list[ManifestItem]:
        return [
            item
            for item in self.items.values()
            if item.status == "downloaded" and item.local_path
        ]

    def pending_schedule(self) -> list[ManifestItem]:
        return [
            item
            for item in self.items.values()
            if item.status in {"downloaded", "queued"} and item.local_path
        ]
