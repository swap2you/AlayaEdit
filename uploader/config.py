from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any

import yaml


@dataclass
class ScheduleConfig:
    posts_per_day: int = 2
    start_date: str | None = None  # YYYY-MM-DD; used when interval_hours is null
    start_after_minutes: int = 30  # first slot at least this far from now
    interval_hours: float | None = None  # if set, space posts this many hours apart
    timezone_note: str = "Uses your local machine clock when computing slots"
    daily_times: list[str] = field(default_factory=lambda: ["10:00", "18:00"])
    platforms: list[str] = field(default_factory=lambda: ["facebook", "instagram"])
    content_type: str = "reel"  # reel | post | story
    caption_template: str = "{title}"
    media_types: list[str] = field(default_factory=lambda: ["video", "image"])

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> ScheduleConfig:
        interval = data.get("interval_hours")
        return cls(
            posts_per_day=int(data.get("posts_per_day", 2)),
            start_date=data.get("start_date"),
            start_after_minutes=int(data.get("start_after_minutes", 30)),
            interval_hours=float(interval) if interval is not None else None,
            timezone_note=data.get("timezone_note", cls.timezone_note),
            daily_times=list(data.get("daily_times", ["10:00", "18:00"])),
            platforms=list(data.get("platforms", ["facebook", "instagram"])),
            content_type=str(data.get("content_type", "reel")),
            caption_template=str(data.get("caption_template", "{title}")),
            media_types=list(data.get("media_types", ["video", "image"])),
        )


@dataclass
class BusinessSuiteConfig:
    home_url: str
    planner_url: str | None = None
    business_id: str | None = None
    asset_id: str | None = None
    headed: bool = True
    user_data_dir: str = ".playwright/business-suite-profile"

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> BusinessSuiteConfig:
        return cls(
            home_url=str(data["home_url"]),
            planner_url=data.get("planner_url"),
            business_id=data.get("business_id"),
            asset_id=data.get("asset_id"),
            headed=bool(data.get("headed", True)),
            user_data_dir=str(data.get("user_data_dir", ".playwright/business-suite-profile")),
        )


def load_yaml(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    return yaml.safe_load(path.read_text(encoding="utf-8")) or {}


def load_schedule_config(path: Path) -> ScheduleConfig:
    return ScheduleConfig.from_dict(load_yaml(path))


def load_business_config(path: Path) -> BusinessSuiteConfig:
    data = load_yaml(path)
    if "home_url" not in data:
        raise ValueError(f"Missing home_url in {path}")
    return BusinessSuiteConfig.from_dict(data)


def plan_slots(
    count: int,
    config: ScheduleConfig,
    *,
    now: datetime | None = None,
) -> list[datetime]:
    """Build upcoming schedule datetimes for the next N posts."""
    now = now or datetime.now().replace(second=0, microsecond=0)
    earliest = now + timedelta(minutes=max(20, config.start_after_minutes))

    if config.interval_hours and config.interval_hours > 0:
        slots: list[datetime] = []
        cursor = earliest
        # Align to next even minute
        if cursor.second or cursor.microsecond:
            cursor = cursor.replace(second=0, microsecond=0) + timedelta(minutes=1)
        for _ in range(count):
            slots.append(cursor)
            cursor = cursor + timedelta(hours=config.interval_hours)
        return slots

    if config.start_date:
        day = datetime.strptime(config.start_date, "%Y-%m-%d").date()
    else:
        day = (now + timedelta(days=1)).date()

    times = config.daily_times[: config.posts_per_day] or ["10:00"]
    slots = []
    while len(slots) < count:
        for t in times:
            hour, minute = map(int, t.split(":"))
            candidate = datetime(day.year, day.month, day.day, hour, minute)
            if candidate >= earliest:
                slots.append(candidate)
            if len(slots) >= count:
                break
        day = day + timedelta(days=1)
    return slots
