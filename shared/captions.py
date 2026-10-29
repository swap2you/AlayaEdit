"""Post captions for ISKCON / bhakti uploads.

Hashtags mix high-volume and niche tags that were actively used with
#iskcon and #srilaprabhupada in 2026 roundups. Unrelated viral tags are omitted.
Sources: iqhashtags (#srilaprabhupada, 2026), best-hashtags (#iskcon),
captionlooms ISKCON Reels guidance (2026).
"""

from __future__ import annotations

TRENDING_BHAKTI_HASHTAGS: tuple[str, ...] = (
    "#iskcon",
    "#harekrishna",
    "#krishna",
    "#bhakti",
    "#krishnaconsciousness",
    "#srilaprabhupada",
    "#prabhupada",
    "#radhakrishna",
    "#vrindavan",
    "#iskcontemple",
    "#bhagavadgita",
    "#kirtan",
    "#haribol",
    "#devotional",
    "#spiritualreels",
)


def jai_gurudev_caption() -> str:
    dots = "\n".join("." for _ in range(6))
    tags = "\n".join(TRENDING_BHAKTI_HASHTAGS)
    return f"Jai Gurudev!\n{dots}\n\n{tags}\n"


def write_caption_sidecar(video_path) -> None:
    """Write <video>.txt next to the file so the uploader can use it as the post text."""
    from pathlib import Path

    path = Path(video_path)
    sidecar = path.with_suffix(".txt")
    if not sidecar.exists():
        sidecar.write_text(jai_gurudev_caption(), encoding="utf-8")
