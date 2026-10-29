"""Facts pulled from YouTube Studio. Do not treat these as a license to edit."""

CHANNEL = {
    "name": "HH Radha Govind Das Goswami Maharaj",
    "channel_id": "UCU5iTetw7fAdCFnFHKM966g",
    "handle": "@HHRadhaGovindDasGoswami",
    "url": "https://www.youtube.com/@HHRadhaGovindDasGoswami",
    "studio": "https://studio.youtube.com/channel/UCU5iTetw7fAdCFnFHKM966g",
    "website": "https://radhagovindgoswami.com",
    "measured_on": "2026-09-29",
    "subscribers": 11226,
    "subscribers_gained_28d": 99,
    "views_28d": 7895,
    "watch_hours_28d": 916.8,
    "estimated_revenue_28d_usd": 7.62,
    "long_form_uploads": 344,
    "public": 339,
    "unlisted": 1,
    "private": 4,
    "shorts": 23,
    "videos_over_50_min": 83,
    "descriptions_with_chapters": 6,
    "all_ads_on": True,
    "ad_review": "safe",
    "copyright_strikes": False,
    "partner_since": "2021-02-12",
}

# Titles already on the channel that match how people search.
# New titles follow this shape. The generic English clip titles do not.
TITLE_PATTERN = (
    "{hindi question or line} | {english topic} · राधा गोविंद महाराज"
)

# These recent public titles have almost no views and no Maharaj name.
# They are the only titles worth replacing. The bilingual library stays.
WEAK_RECENT_TITLES = (
    "Krishna's divine protection.",
    "The battle begins!",
    "The spiritual leader is seen",
    "Who is the supreme Vasudeva?",
    "The true meaning of Vasudeva.",
)

RULES = (
    "Do not rename the existing Hindi-English katha library.",
    "Do not upload the 613 Munch clips in one batch.",
    "A 16:9 file does not become a Short because the title contains #shorts.",
    "Maharaj's face is enlarged from a real photograph. It is never redrawn.",
    "No text or graphic sits on the face.",
    "Clipto is for lectures longer than 50 minutes. Save the transcript locally.",
    "Polish a description from the transcript. Do not change what was said.",
    "Do not file copyright removals unless asked.",
    "Do not use #1mview, #videoviral, or #trending.",
)
