from __future__ import annotations

import re
import shutil
import tempfile
import time
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

from playwright.sync_api import BrowserContext, Page, sync_playwright
from rich.console import Console

from shared.manifest import Manifest, ManifestItem
from uploader.config import BusinessSuiteConfig, ScheduleConfig, plan_slots

console = Console()

_WINDOW_MARKERS = (
    "date is too far",
    "too far in the future",
    "must be within",
    "outside the allowed",
    "can't schedule this far",
    "cannot schedule this far",
    "more than 75 days",
    "more than 29 days",
    "20 minutes and 29 days",
    "29 days from when you create",
    "more than 6 months",
    "select a date between",
    "choose a date between",
    "this date isn't available",
    "this date is not available",
)


def _schedule_window_blocked(page: Page) -> bool:
    try:
        if page.locator('input[placeholder="mm/dd/yyyy"][aria-invalid="true"]').count():
            return True
        body = page.inner_text("body").lower()
    except Exception:  # noqa: BLE001
        return False
    return any(marker in body for marker in _WINDOW_MARKERS)


def _slot_anchor(manifest: Manifest) -> datetime:
    """Continue after the latest saved slot so a resume does not reuse dates."""
    latest: datetime | None = None
    for item in manifest.items.values():
        if item.status != "scheduled" or not item.scheduled_for:
            continue
        try:
            when = datetime.fromisoformat(item.scheduled_for)
        except ValueError:
            continue
        if latest is None or when > latest:
            latest = when
    now = datetime.now().replace(second=0, microsecond=0)
    if latest is None:
        return now
    return latest if latest > now else now


@dataclass
class ScheduleJob:
    item: ManifestItem
    when: datetime
    caption: str


class ScheduleWindowError(RuntimeError):
    """Meta rejected the date because it is outside the scheduling window."""


class BusinessSuiteScheduler:
    """
    Browser-assisted Meta Business Suite scheduler.

    You complete Facebook SSO / 2FA in the headed browser. After login is
    detected, this helper navigates Planner/Create and schedules local media.

    Meta's UI changes frequently; selectors are intentionally text/role based
    and the flow supports dry-run exploration first.
    """

    def __init__(
        self,
        business: BusinessSuiteConfig,
        schedule: ScheduleConfig,
        *,
        dry_run: bool = True,
        interactive: bool = True,
    ) -> None:
        self.business = business
        self.schedule = schedule
        self.dry_run = dry_run
        self.interactive = interactive

    def _pause(self, message: str) -> None:
        console.print(f"[yellow]{message}[/yellow]")
        if self.interactive:
            input("Press Enter to continue...")
        else:
            console.print("[dim]Non-interactive: waiting 8s...[/dim]")
            time.sleep(8)

    def _planner_url(self) -> str:
        if self.business.planner_url:
            return self.business.planner_url
        # Current Business Suite calendar lives under content_calendar
        base = "https://business.facebook.com/latest/content_calendar"
        params: list[str] = []
        if self.business.business_id:
            params.append(f"business_id={self.business.business_id}")
        if self.business.asset_id:
            params.append(f"asset_id={self.business.asset_id}")
        return f"{base}?{'&'.join(params)}" if params else base

    def _create_url(self) -> str:
        # Reels use reels_composer; posts use composer.
        path = (
            "reels_composer"
            if self.schedule.content_type.lower() == "reel"
            else "composer"
        )
        base = f"https://business.facebook.com/latest/{path}"
        params: list[str] = []
        if self.business.business_id:
            params.append(f"business_id={self.business.business_id}")
        if self.business.asset_id:
            params.append(f"asset_id={self.business.asset_id}")
        return f"{base}?{'&'.join(params)}" if params else base

    def _wait_for_login(self, page: Page, timeout_sec: int = 600) -> None:
        console.print(
            "[yellow]Complete Facebook / Business Suite login in the opened browser "
            "(SSO, 2FA, checkpoints). Waiting until you are signed in...[/yellow]"
        )
        deadline = time.time() + timeout_sec
        while time.time() < deadline:
            url = page.url.lower()
            content = ""
            try:
                content = page.content().lower()
            except Exception:  # noqa: BLE001
                pass
            logged_out_signals = (
                "log in to facebook" in content
                or "log into facebook" in content
                or "/login" in url
                or "checkpoint" in url
            )
            logged_in_signals = (
                "business.facebook.com/latest" in url
                and "login" not in url
                and not logged_out_signals
            )
            if logged_in_signals:
                console.print("[green]Login detected.[/green]")
                return
            page.wait_for_timeout(2000)
        raise TimeoutError("Timed out waiting for Business Suite login")

    def _click_first(self, page: Page, selectors: list[str], timeout: int = 5000) -> bool:
        for selector in selectors:
            try:
                locator = page.locator(selector).first
                if locator.count() == 0:
                    continue
                locator.click(timeout=timeout)
                return True
            except Exception:  # noqa: BLE001
                continue
        return False

    def _fill_first(self, page: Page, selectors: list[str], text: str) -> bool:
        for selector in selectors:
            try:
                locator = page.locator(selector).first
                if locator.count() == 0:
                    continue
                locator.click(timeout=3000)
                locator.fill(text, timeout=5000)
                return True
            except Exception:  # noqa: BLE001
                try:
                    locator = page.locator(selector).first
                    locator.click(timeout=3000)
                    page.keyboard.type(text, delay=20)
                    return True
                except Exception:  # noqa: BLE001
                    continue
        return False

    def _fill_caption(self, page: Page, text: str) -> bool:
        """Put the Jai Gurudev caption into the reel text box, including line breaks."""
        selectors = [
            'div[aria-label*="Let viewers know" i]',
            'div[aria-label*="Write" i][contenteditable="true"]',
            'div[role="textbox"]',
            'div[contenteditable="true"]',
            'textarea[placeholder*="reel" i]',
            'textarea',
        ]
        for selector in selectors:
            try:
                locator = page.locator(selector).first
                if locator.count() == 0:
                    continue
                locator.click(timeout=3000)
                page.keyboard.press("Control+A")
                page.keyboard.insert_text(text)
                return True
            except Exception:  # noqa: BLE001
                continue
        return False

    def _attach_file(self, page: Page, media_path: Path) -> bool:
        # Prefer clicking Add Video / Add photo/video then set via file chooser.
        openers = [
            'text=Add Video',
            'span:text-is("Add Video")',
            'div[role="button"]:has-text("Add Video")',
            'button:has-text("Add Video")',
            'div[role="button"]:has-text("Add photo/video")',
            'button:has-text("Add photo/video")',
            'span:has-text("Add photo/video")',
        ]

        # Hidden inputs sometimes exist after opener click; try direct first.
        try:
            inputs = page.locator('input[type="file"]')
            if inputs.count() > 0:
                inputs.first.set_input_files(str(media_path))
                return True
        except Exception:  # noqa: BLE001
            pass

        for opener in openers:
            try:
                loc = page.locator(opener).first
                if loc.count() == 0:
                    continue
                with page.expect_file_chooser(timeout=15000) as fc_info:
                    loc.click(timeout=5000)
                chooser = fc_info.value
                chooser.set_files(str(media_path))
                console.print("[green]Attached video[/green]")
                return True
            except Exception as exc:  # noqa: BLE001
                console.print(f"[dim]Attach attempt failed ({opener}): {exc}[/dim]")
                try:
                    inputs = page.locator('input[type="file"]')
                    if inputs.count() > 0:
                        inputs.first.set_input_files(str(media_path))
                        return True
                except Exception:  # noqa: BLE001
                    continue

        # Some clip titles use characters the file dialog rejects. Upload a plain copy.
        plain = Path(tempfile.gettempdir()) / "munch-reel-upload.mp4"
        try:
            shutil.copyfile(media_path, plain)
            inputs = page.locator('input[type="file"]')
            if inputs.count() > 0:
                inputs.first.set_input_files(str(plain))
                console.print("[green]Attached video[/green]")
                return True
            with page.expect_file_chooser(timeout=15000) as fc_info:
                page.get_by_text("Add Video", exact=True).first.click(timeout=5000)
            fc_info.value.set_files(str(plain))
            console.print("[green]Attached video[/green]")
            return True
        except Exception as exc:  # noqa: BLE001
            console.print(f"[red]Could not attach file: {media_path.name} ({exc})[/red]")
            return False

    def _select_platforms(self, page: Page) -> None:
        """Best-effort: ensure Facebook + Instagram destinations stay selected."""
        for platform in self.schedule.platforms:
            label = "Facebook" if platform.lower().startswith("face") else (
                "Instagram" if platform.lower().startswith("insta") else platform.title()
            )
            self._click_first(
                page,
                [
                    f'div[role="checkbox"][aria-label*="{label}" i]',
                    f'label:has-text("{label}")',
                    f'span:has-text("{label}")',
                    f'div[aria-label*="{label}" i]',
                ],
            )
            page.wait_for_timeout(300)

    def _click_next(self, page: Page) -> bool:
        try:
            next_btn = page.get_by_role("button", name=re.compile(r"^Next$", re.I))
            if next_btn.count():
                next_btn.last.click(timeout=8000)
                return True
        except Exception:  # noqa: BLE001
            pass
        return self._click_first(
            page,
            [
                'div[role="button"]:text-is("Next")',
                'button:text-is("Next")',
                'div[aria-label="Next"]',
            ],
            timeout=8000,
        )

    def _wait_copyright_ready(self, page: Page, timeout_sec: int = 20) -> None:
        deadline = time.time() + timeout_sec
        while time.time() < deadline:
            body = ""
            try:
                body = page.inner_text("body")
            except Exception:  # noqa: BLE001
                pass
            if "Your video is safe to publish" in body:
                console.print("[green]Copyright check passed[/green]")
                return
            if "Checking for copyrighted content" not in body and body:
                return
            page.wait_for_timeout(2000)
        console.print("[yellow]Copyright check still running; continuing anyway[/yellow]")

    def _goto_share_step(self, page: Page) -> bool:
        # Share and Next stay disabled until the upload percent disappears.
        deadline = time.time() + 240
        while time.time() < deadline:
            body = ""
            try:
                body = page.inner_text("body")
            except Exception:  # noqa: BLE001
                body = ""
            if "Scheduling options" in body or "Share now" in body:
                console.print("[green]Opened Share step[/green]")
                return True
            percents = [int(value) for value in re.findall(r"(\d{1,3})%", body)]
            if any(value < 100 for value in percents):
                page.wait_for_timeout(2000)
                continue
            try:
                page.get_by_text("Share", exact=True).first.click(timeout=4000)
                page.wait_for_timeout(1500)
            except Exception:  # noqa: BLE001
                self._click_next(page)
                page.wait_for_timeout(1500)
        return False

    def _set_schedule_on_share(self, page: Page, when: datetime) -> bool:
        """On Share step: choose Schedule and set FB + IG date/time fields."""
        date_str = when.strftime("%m/%d/%Y")
        hour12 = when.strftime("%I").lstrip("0") or "12"
        minute = when.strftime("%M")
        meridiem = when.strftime("%p")  # AM/PM

        # Segmented control: Share now | Schedule | Save as draft
        try:
            page.get_by_text("Schedule", exact=True).first.click(timeout=5000)
            selected = True
        except Exception:  # noqa: BLE001
            selected = self._click_first(
                page,
                [
                    'div[role="button"]:text-is("Schedule")',
                    'label:has-text("Schedule")',
                    'text=/^Schedule$/',
                ],
                timeout=5000,
            )
        page.wait_for_timeout(1500)

        # Date fields (Facebook + Instagram) - placeholder mm/dd/yyyy
        date_inputs = page.locator('input[placeholder="mm/dd/yyyy"]')
        dates_filled = 0
        for i in range(date_inputs.count()):
            try:
                el = date_inputs.nth(i)
                el.click(timeout=3000)
                el.fill("")
                el.fill(date_str)
                el.press("Tab")
                dates_filled += 1
            except Exception:  # noqa: BLE001
                continue

        # Time parts: hours / minutes / meridiem (duplicated for FB + IG)
        hours = page.locator('input[aria-label="hours"]')
        minutes = page.locator('input[aria-label="minutes"]')
        meridiems = page.locator('input[aria-label="meridiem"]')
        times_filled = 0
        count = min(hours.count(), minutes.count(), meridiems.count(), 2)
        for i in range(count):
            try:
                hours.nth(i).fill(hour12)
                minutes.nth(i).fill(minute)
                meridiems.nth(i).fill(meridiem)
                times_filled += 1
            except Exception:  # noqa: BLE001
                continue

        console.print(
            f"Schedule UI: selected={selected} dates={dates_filled} times={times_filled} "
            f"-> {date_str} {hour12}:{minute} {meridiem}"
        )
        if _schedule_window_blocked(page):
            raise ScheduleWindowError(
                f"Meta will not accept {date_str} {hour12}:{minute} {meridiem}"
            )
        return bool(selected and dates_filled >= 1 and times_filled >= 1)

    def _schedule_one(self, page: Page, job: ScheduleJob) -> bool:
        media_path = Path(job.item.local_path) if job.item.local_path else None
        if not media_path or not media_path.exists():
            console.print(f"[red]Missing media for {job.item.id}[/red]")
            return False

        console.print(
            f"Scheduling [bold]{media_path.name}[/bold] for "
            f"{job.when.isoformat(sep=' ', timespec='minutes')} "
            f"-> {', '.join(self.schedule.platforms)}"
        )
        try:
            page.keyboard.press("Escape")
        except Exception:  # noqa: BLE001
            pass
        for attempt in range(3):
            try:
                page.goto(
                    self._create_url(),
                    wait_until="domcontentloaded",
                    timeout=90000,
                )
                break
            except Exception as exc:  # noqa: BLE001
                console.print(f"[yellow]Composer navigation failed (try {attempt + 1}/3): {exc}[/yellow]")
                page.wait_for_timeout(3000)
        else:
            console.print("[red]Could not open reels composer after retries[/red]")
            return False
        page.wait_for_timeout(3500)

        if not self._attach_file(page, media_path):
            console.print(f"[red]Could not attach {media_path.name}[/red]")
            return False
        page.wait_for_timeout(3000)

        self._wait_copyright_ready(page)

        title = (job.item.title or media_path.stem)[:80]
        caption_file = media_path.with_suffix(".txt")
        caption_text = job.caption
        if caption_file.exists():
            caption_text = caption_file.read_text(encoding="utf-8").strip() or caption_text
        self._fill_first(
            page,
            [
                'input[placeholder*="title" i]',
                'textarea[placeholder*="title" i]',
                'div[aria-label*="title" i]',
            ],
            title,
        )
        self._fill_caption(page, caption_text)

        if not self._goto_share_step(page):
            console.print("[red]Could not open Share step.[/red]")
            return False

        # Ensure Scheduling options are visible
        page.mouse.wheel(0, -2500)
        page.wait_for_timeout(500)

        if not self._set_schedule_on_share(page, job.when):
            console.print(
                f"[red]Could not set {job.when.strftime('%m/%d/%Y %I:%M %p')}.[/red]"
            )
            return False

        if self.dry_run:
            console.print("[yellow]Dry-run: schedule fields set, Schedule was not clicked.[/yellow]")
            return True

        # Footer CTA becomes "Schedule" when schedule mode is selected.
        page.wait_for_timeout(1500)
        confirmed = False
        # Prefer the bottom-most Schedule control (footer), never the segmented control near top.
        cands = page.locator('div[role="button"], button')
        best_i = None
        best_y = -1.0
        for i in range(cands.count()):
            try:
                text = (cands.nth(i).inner_text() or "").strip()
            except Exception:  # noqa: BLE001
                continue
            if text != "Schedule":
                continue
            box = cands.nth(i).bounding_box() or {"y": 0}
            if box["y"] > best_y:
                best_y = box["y"]
                best_i = i
        if best_i is not None and best_y > 500:
            try:
                cands.nth(best_i).click(timeout=8000, force=True)
                confirmed = True
            except Exception as exc:  # noqa: BLE001
                console.print(f"[dim]Footer schedule click failed: {exc}[/dim]")

        if not confirmed:
            try:
                page.get_by_role("button", name=re.compile(r"^Schedule$", re.I)).last.click(
                    timeout=8000, force=True
                )
                confirmed = True
            except Exception:  # noqa: BLE001
                confirmed = False

        if not confirmed:
            console.print("[red]Footer Schedule button not found.[/red]")
            return False
        console.print(f"[green]Clicked footer Schedule (y={best_y:.0f})[/green]")
        page.wait_for_timeout(5000)
        if _schedule_window_blocked(page):
            raise ScheduleWindowError(
                f"Meta rejected {job.when.strftime('%m/%d/%Y %I:%M %p')} after Schedule"
            )
        return True

    def explore(self) -> None:
        """Open Business Suite home + planner so we can map the UI after your SSO."""
        profile = Path(self.business.user_data_dir).resolve()
        profile.mkdir(parents=True, exist_ok=True)
        with sync_playwright() as p:
            context: BrowserContext = p.chromium.launch_persistent_context(
                user_data_dir=str(profile),
                headless=not self.business.headed,
                channel="chrome",
                args=["--disable-blink-features=AutomationControlled"],
                viewport={"width": 1400, "height": 900},
            )
            page = context.pages[0] if context.pages else context.new_page()
            page.goto(self.business.home_url, wait_until="domcontentloaded")
            self._wait_for_login(page)
            console.print(f"Opening planner: {self._planner_url()}")
            page.goto(self._planner_url(), wait_until="domcontentloaded")
            console.print(
                "[green]Planner loaded.[/green] Inspect Create / Calendar controls. "
                "Press Enter to open composer, or Ctrl+C to stop."
            )
            try:
                input("Press Enter to open Create/Composer...")
                page.goto(self._create_url(), wait_until="domcontentloaded")
                console.print("Composer open. Press Enter to close.")
                input()
            finally:
                context.close()

    def run(self, manifest: Manifest, *, limit: int | None = None) -> None:
        candidates = [
            item
            for item in manifest.pending_schedule()
            if item.media_type in self.schedule.media_types
        ]
        if limit is not None:
            candidates = candidates[:limit]
        if not candidates:
            console.print("[yellow]No downloaded media ready to schedule.[/yellow]")
            return

        slots = plan_slots(len(candidates), self.schedule, now=_slot_anchor(manifest))
        jobs = [
            ScheduleJob(
                item=item,
                when=when,
                caption=self.schedule.caption_template.format(
                    title=item.title or Path(item.local_path or "media").stem
                ),
            )
            for item, when in zip(candidates, slots, strict=True)
        ]

        profile = Path(self.business.user_data_dir).resolve()
        profile.mkdir(parents=True, exist_ok=True)

        with sync_playwright() as p:
            try:
                context = p.chromium.launch_persistent_context(
                    user_data_dir=str(profile),
                    headless=not self.business.headed,
                    channel="chrome",
                    args=["--disable-blink-features=AutomationControlled"],
                    viewport={"width": 1400, "height": 900},
                )
            except Exception:
                # Fallback if Chrome channel is unavailable.
                context = p.chromium.launch_persistent_context(
                    user_data_dir=str(profile),
                    headless=not self.business.headed,
                    args=["--disable-blink-features=AutomationControlled"],
                    viewport={"width": 1400, "height": 900},
                )

            page = context.pages[0] if context.pages else context.new_page()
            page.goto(self.business.home_url, wait_until="domcontentloaded")
            self._wait_for_login(page)

            failures = 0
            for job in jobs:
                ok = False
                for attempt in range(2):
                    try:
                        ok = self._schedule_one(page, job)
                    except ScheduleWindowError as exc:
                        console.print(f"[red]{exc}[/red]")
                        console.print(
                            "[yellow]Stopped so later clips stay unscheduled and can "
                            "be continued on the next run.[/yellow]"
                        )
                        ok = False
                        attempt = 99
                        failures = 99
                        break
                    except Exception as exc:  # noqa: BLE001
                        console.print(f"[red]Schedule error for {job.item.id}: {exc}[/red]")
                        ok = False
                    if ok:
                        break
                    console.print(f"[yellow]Retrying {Path(job.item.local_path or '').name}[/yellow]")
                    page.wait_for_timeout(2000)
                if failures >= 99:
                    break
                if ok:
                    failures = 0
                    job.item.status = "queued" if self.dry_run else "scheduled"
                    job.item.scheduled_for = job.when.isoformat()
                    job.item.error = None
                    manifest.upsert(job.item)
                    manifest.save()
                else:
                    failures += 1
                    job.item.error = "Business Suite schedule step failed"
                    manifest.upsert(job.item)
                    manifest.save()
                    if failures >= 6:
                        console.print(
                            "[red]Stopped after 6 schedule failures in a row.[/red]"
                        )
                        break

            console.print("[green]Uploader pass finished.[/green]")
            context.close()
