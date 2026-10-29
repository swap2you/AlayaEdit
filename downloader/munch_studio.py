"""Download generated Munch Studio clips into one folder per project.

Uses the signed-in browser session only for the Munch API. Each clip is
exported at 16:9 (the YouTube size these projects were made in), saved with
the clip title, and given a Jai Gurudev caption sidecar for later uploads.
"""

from __future__ import annotations

import json
import re
import shutil
import time
import urllib.parse
import urllib.request
from pathlib import Path

from playwright.sync_api import Page, sync_playwright
from rich.console import Console

from shared.captions import write_caption_sidecar

console = Console()

STUDIO_URL = "https://app.munchstudio.com/studio"
API = "https://api.munchstudio.com"
BATCH_SIZE = 10
# YouTube / landscape export. The download menu sends the ratio and the pixel size.
ASPECT_RATIO = [16, 9]
RESOLUTION = [1920, 1080]
POLL_SECONDS = 4
BATCH_TIMEOUT_SECONDS = 12 * 60


def _safe_name(value: str, max_len: int = 120) -> str:
    cleaned = re.sub(r'[<>:"/\\|?*\n\r\t]+', " ", value)
    cleaned = re.sub(r"\s+", " ", cleaned).strip(" .")
    return (cleaned or "clip")[:max_len]


def _unique_path(directory: Path, filename: str) -> Path:
    target = directory / filename
    if not target.exists():
        return target
    stem = target.stem
    suffix = target.suffix
    index = 2
    while True:
        candidate = directory / f"{stem} ({index}){suffix}"
        if not candidate.exists():
            return candidate
        index += 1


def _launch(profile: Path):
    profile.mkdir(parents=True, exist_ok=True)
    playwright = sync_playwright().start()
    last_error: Exception | None = None
    for attempt in range(4):
        try:
            context = playwright.chromium.launch_persistent_context(
                user_data_dir=str(profile),
                headless=False,
                channel="chrome",
                accept_downloads=True,
                viewport={"width": 1440, "height": 900},
                args=["--disable-blink-features=AutomationControlled"],
            )
            return playwright, context
        except Exception as exc:  # noqa: BLE001
            last_error = exc
            message = str(exc).lower()
            if "existing browser session" in message or "target closed" in message:
                time.sleep(2 + attempt)
                continue
            break
    try:
        context = playwright.chromium.launch_persistent_context(
            user_data_dir=str(profile),
            headless=False,
            accept_downloads=True,
            viewport={"width": 1440, "height": 900},
        )
        return playwright, context
    except Exception:
        playwright.stop()
        raise last_error or RuntimeError("Could not open a browser for Munch Studio")


def _api(page: Page, method: str, path: str, body: dict | None = None) -> tuple[int, object]:
    result = page.evaluate(
        """async ({method, path, body}) => {
            const response = await fetch('https://api.munchstudio.com' + path, {
                method,
                credentials: 'include',
                headers: body ? {'content-type': 'application/json'} : {},
                body: body ? JSON.stringify(body) : undefined,
            });
            const text = await response.text();
            let parsed = text;
            try { parsed = JSON.parse(text); } catch (err) {}
            return {status: response.status, body: parsed};
        }""",
        {"method": method, "path": path, "body": body},
    )
    return int(result["status"]), result["body"]


def _active_brand(page: Page) -> tuple[str, str] | None:
    status, payload = _api(page, "GET", "/workspace/brands-overview?includeArchived=false")
    if status == 401 or not isinstance(payload, dict):
        return None
    brands = payload.get("brands") or []
    if not brands:
        return None
    brand = next((item for item in brands if item.get("isDefault")), brands[0])
    brand_id = brand.get("id")
    if not brand_id:
        return None
    return str(brand_id), str(brand.get("name") or "Munch")


def _wait_for_login(page: Page, timeout_sec: int = 600) -> tuple[str, str]:
    brand = _active_brand(page)
    if brand:
        console.print(f"[green]Munch Studio signed in as {brand[1]}.[/green]")
        return brand
    console.print(
        "[yellow]Sign in to Munch Studio in the opened browser. "
        "Waiting until the account loads...[/yellow]"
    )
    deadline = time.time() + timeout_sec
    while time.time() < deadline:
        page.wait_for_timeout(2000)
        brand = _active_brand(page)
        if brand:
            console.print(f"[green]Munch Studio login detected ({brand[1]}).[/green]")
            return brand
    raise TimeoutError("Timed out waiting for Munch Studio login")


def _list_video_projects(page: Page, brand_id: str) -> list[dict]:
    projects: list[dict] = []
    cursor: str | None = None
    seen_cursors: set[str] = set()
    while True:
        path = f"/brand/{brand_id}/studio/feed?mode=collapsed&pageSize=20"
        if cursor:
            path += "&cursor=" + urllib.parse.quote(cursor, safe="")
        status, payload = _api(page, "GET", path)
        if status != 200 or not isinstance(payload, dict):
            raise RuntimeError(f"Could not list Munch projects ({status})")
        for entry in payload.get("items") or []:
            folder = entry.get("folder") or {}
            if folder.get("kind") != "CLIP":
                continue
            if int(folder.get("itemCount") or 0) <= 0:
                continue
            if folder.get("isSample"):
                continue
            projects.append(
                {
                    "id": folder["projectId"],
                    "name": folder.get("name") or "Untitled project",
                    "item_count": int(folder.get("itemCount") or 0),
                }
            )
        cursor = payload.get("nextCursor")
        if not cursor or cursor in seen_cursors:
            break
        seen_cursors.add(cursor)
    return projects


def _list_clips(page: Page, brand_id: str, project_id: str) -> list[dict]:
    status, payload = _api(
        page,
        "GET",
        f"/brand/{brand_id}/projects/{project_id}/items?kind=CLIP&mode=meta",
    )
    if status != 200 or not isinstance(payload, dict):
        raise RuntimeError(f"Could not list clips for {project_id} ({status})")
    clips: list[dict] = []
    for item in payload.get("items") or []:
        publishable_id = item.get("publishableItemId")
        if not publishable_id:
            continue
        publishable = item.get("publishableItem") or {}
        title = (publishable.get("title") or "").strip() or str(publishable_id)
        clips.append({"id": publishable_id, "title": title})
    return clips


def _load_done(manifest_path: Path) -> tuple[dict[str, str], dict[str, str]]:
    if not manifest_path.exists():
        return {}, {}
    try:
        payload = json.loads(manifest_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}, {}
    done: dict[str, str] = {}
    titles: dict[str, str] = {}
    for item in payload.get("items") or []:
        item_id = item.get("id")
        local_path = item.get("path")
        if item_id and item.get("title"):
            titles[item_id] = item["title"]
        if item_id and local_path and Path(local_path).exists():
            done[item_id] = local_path
    return done, titles


def _save_manifest(manifest_path: Path, done: dict[str, str], titles: dict[str, str]) -> None:
    items = [
        {"id": item_id, "title": titles.get(item_id, ""), "path": path, "status": "downloaded"}
        for item_id, path in sorted(done.items())
    ]
    projects: dict[str, int] = {}
    for path in done.values():
        projects[Path(path).parent.name] = projects.get(Path(path).parent.name, 0) + 1
    payload = {
        "items": items,
        "projects": [
            {"name": name, "clips": count, "status": "downloaded"}
            for name, count in sorted(projects.items())
        ],
    }
    text = json.dumps(payload, indent=2)
    temporary = manifest_path.with_suffix(".json.tmp")
    temporary.write_text(text, encoding="utf-8")
    temporary.replace(manifest_path)


def _start_export(page: Page, brand_id: str, clip_ids: list[str]) -> list[dict]:
    last_detail = "unknown error"
    for attempt in range(4):
        status, payload = _api(
            page,
            "POST",
            f"/brand/{brand_id}/exports/bulk-download",
            {
                "publishableItemIds": clip_ids,
                "aspectRatio": ASPECT_RATIO,
                "resolution": RESOLUTION,
            },
        )
        if status == 200 and isinstance(payload, dict) and payload.get("processes"):
            return payload["processes"]
        last_detail = payload if isinstance(payload, str) else json.dumps(payload)[:500]
        if status not in (429, 500, 502, 503) or attempt == 3:
            break
        wait = 20 * (attempt + 1)
        console.print(f"[yellow]  export start returned {status}. Retrying in {wait}s.[/yellow]")
        page.wait_for_timeout(wait * 1000)
    raise RuntimeError(f"Munch export failed: {last_detail}")


def _poll_exports(page: Page, brand_id: str, process_ids: list[str]) -> dict[str, dict]:
    pending = set(process_ids)
    finished: dict[str, dict] = {}
    deadline = time.time() + BATCH_TIMEOUT_SECONDS
    while pending and time.time() < deadline:
        page.wait_for_timeout(POLL_SECONDS * 1000)
        joined = ",".join(pending)
        status, payload = _api(
            page,
            "GET",
            f"/brand/{brand_id}/exports/check?exportIds={joined}",
        )
        if status != 200 or not isinstance(payload, dict):
            console.print(f"[yellow]Export status check returned {status}. Retrying.[/yellow]")
            continue
        for export_id, row in (payload.get("done") or {}).items():
            finished[export_id] = row
            pending.discard(export_id)
        for export_id, row in (payload.get("error") or {}).items():
            finished[export_id] = {**row, "_failed": True}
            pending.discard(export_id)
        processing = payload.get("processing") or {}
        if processing:
            percents = [
                str(row.get("progressPercentage"))
                for row in processing.values()
                if isinstance(row, dict)
            ]
            console.print(f"  rendering {len(processing)} file(s): {', '.join(percents)}")
    for export_id in pending:
        finished[export_id] = {"_failed": True, "status": "timeout"}
    return finished


def _download_file(url: str, target: Path) -> None:
    target.parent.mkdir(parents=True, exist_ok=True)
    temporary = target.with_suffix(target.suffix + ".part")
    request = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(request, timeout=300) as response, temporary.open("wb") as handle:
        shutil.copyfileobj(response, handle)
    temporary.replace(target)


def _save_export(
    row: dict,
    *,
    fallback_title: str,
    project_dir: Path,
) -> Path | None:
    if row.get("_failed"):
        return None
    storage_url = row.get("storageUrl")
    if storage_url:
        filename = _safe_name(fallback_title) + ".mp4"
        target = _unique_path(project_dir, filename)
        _download_file(storage_url, target)
        write_caption_sidecar(target)
        return target
    children = [url for url in (row.get("childrenStorageUrls") or []) if url]
    if len(children) == 1:
        filename = _safe_name(fallback_title) + ".mp4"
        target = _unique_path(project_dir, filename)
        _download_file(children[0], target)
        write_caption_sidecar(target)
        return target
    return None


def _download_project(
    page: Page,
    *,
    brand_id: str,
    project: dict,
    dest: Path,
    done: dict[str, str],
    titles: dict[str, str],
    manifest_path: Path,
) -> int:
    project_dir = dest / _safe_name(project["name"], max_len=80)
    project_dir.mkdir(parents=True, exist_ok=True)
    clips = _list_clips(page, brand_id, project["id"])
    pending = []
    for clip in clips:
        titles[clip["id"]] = clip["title"]
        existing = done.get(clip["id"])
        if existing and Path(existing).exists():
            continue
        pending.append(clip)
    console.print(
        f"[bold]{project['name']}[/bold]  {len(clips)} clip(s), {len(pending)} to download"
    )
    saved = 0
    for offset in range(0, len(pending), BATCH_SIZE):
        batch = pending[offset : offset + BATCH_SIZE]
        console.print(f"  exporting {offset + 1}-{offset + len(batch)} of {len(pending)}")
        by_id = {clip["id"]: clip["title"] for clip in batch}
        try:
            processes = _start_export(page, brand_id, [clip["id"] for clip in batch])
        except Exception as exc:  # noqa: BLE001
            console.print(f"[yellow]  batch failed: {exc}[/yellow]")
            continue
        name_by_process = {item["processId"]: item.get("name") or "" for item in processes}
        rows = _poll_exports(page, brand_id, list(name_by_process))
        for process_id, row in rows.items():
            title = name_by_process.get(process_id) or by_id.get(row.get("publishableItemId"), "clip")
            publishable_id = row.get("publishableItemId")
            path = _save_export(row, fallback_title=title, project_dir=project_dir)
            if path is None:
                console.print(f"[yellow]  skipped {title}: export did not finish[/yellow]")
                continue
            if publishable_id:
                done[publishable_id] = str(path)
                titles[publishable_id] = title
            saved += 1
            console.print(f"[green]  saved {path.name}[/green]")
        _save_manifest(manifest_path, done, titles)
    return saved


def download_munch_studio(
    dest: Path,
    *,
    user_data_dir: Path | None = None,
    project_filter: str | None = None,
) -> int:
    dest = dest.expanduser().resolve()
    dest.mkdir(parents=True, exist_ok=True)
    profile = (user_data_dir or Path(".playwright/munch-studio-profile")).resolve()
    manifest_path = dest / "munch_manifest.json"
    done, titles = _load_done(manifest_path)
    playwright, context = _launch(profile)
    saved_total = 0
    try:
        page = context.pages[0] if context.pages else context.new_page()
        page.goto(STUDIO_URL, wait_until="domcontentloaded", timeout=90000)
        page.wait_for_timeout(2000)
        brand_id, brand_name = _wait_for_login(page)
        console.print(f"Brand: {brand_name}")
        projects = _list_video_projects(page, brand_id)
        if project_filter:
            needle = project_filter.lower()
            projects = [project for project in projects if needle in project["name"].lower()]
        console.print(f"Found {len(projects)} video project(s).")
        for project in projects:
            try:
                saved_total += _download_project(
                    page,
                    brand_id=brand_id,
                    project=project,
                    dest=dest,
                    done=done,
                    titles=titles,
                    manifest_path=manifest_path,
                )
            except Exception as exc:  # noqa: BLE001
                console.print(f"[red]Project failed ({project['name']}): {exc}[/red]")
                continue
        console.print(f"[green]Saved {saved_total} new clip(s) -> {dest}[/green]")
        return saved_total
    finally:
        context.close()
        playwright.stop()
