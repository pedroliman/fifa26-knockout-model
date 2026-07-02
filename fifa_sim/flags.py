"""Country flag images for the social-media-ready charts.

Flags are fetched from flagcdn.com (a free, public flag CDN, no key) by
ISO 3166-1 alpha-2 code and cached to disk so repeated chart renders don't
re-download. England/Scotland/Wales use flagcdn's special subdivision
codes since they compete as separate teams from the rest of the UK.
"""
from __future__ import annotations

import os
import urllib.error
import urllib.request

FLAG_HEIGHT = 240  # px; flagcdn's h{N} bucket, sized for crisp social-media output

TEAM_ISO2 = {
    "South Africa": "za",
    "Canada": "ca",
    "Brazil": "br",
    "Japan": "jp",
    "Netherlands": "nl",
    "Morocco": "ma",
    "Germany": "de",
    "Paraguay": "py",
    "Ivory Coast": "ci",
    "Norway": "no",
    "Mexico": "mx",
    "Ecuador": "ec",
    "France": "fr",
    "Sweden": "se",
    "Belgium": "be",
    "Senegal": "sn",
    "United States": "us",
    "Bosnia-Herzegovina": "ba",
    "England": "gb-eng",
    "Congo DR": "cd",
    "Portugal": "pt",
    "Croatia": "hr",
    "Spain": "es",
    "Austria": "at",
    "Switzerland": "ch",
    "Algeria": "dz",
    "Australia": "au",
    "Egypt": "eg",
    "Argentina": "ar",
    "Cape Verde": "cv",
    "Colombia": "co",
    "Ghana": "gh",
}

CACHE_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "cache", "flags"
)


def flag_path(team_name: str, height: int = FLAG_HEIGHT) -> str | None:
    """Downloads (once) and returns a local path to `team_name`'s flag PNG,
    or None if the team isn't recognized or the fetch fails."""
    iso2 = TEAM_ISO2.get(team_name)
    if iso2 is None:
        return None

    os.makedirs(CACHE_DIR, exist_ok=True)
    local_path = os.path.join(CACHE_DIR, f"{iso2}_h{height}.png")
    if os.path.exists(local_path):
        return local_path

    url = f"https://flagcdn.com/h{height}/{iso2}.png"
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (fifa26-knockout-model)"})
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = resp.read()
        with open(local_path, "wb") as f:
            f.write(data)
        return local_path
    except (urllib.error.URLError, TimeoutError, OSError):
        return None
