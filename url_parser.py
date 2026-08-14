"""
Parsing helpers to extract latitude/longitude (and a place name, when
available) from Google Maps URLs.

Supported URL shapes include, for example:
  https://www.google.com/maps/place/Some+Place/@-37.8136,144.9631,15z/data=!...!3d-37.8140!4d144.9633
  https://www.google.com/maps/@-37.8136,144.9631,15z
  https://www.google.com/maps?q=-37.8136,144.9631
  https://maps.google.com/maps?ll=-37.8136,144.9631
  https://www.google.com/maps/search/?api=1&query=-37.8136,144.9631
  https://maps.app.goo.gl/xxxxxxxx   (short link, resolved via HTTP redirect)
  https://goo.gl/maps/xxxxxxxx       (short link, resolved via HTTP redirect)

Author:  Leenath Wimukthi Gamage <leenathgamage@gmail.com>
License: GPL-3.0-or-later (see LICENSE)
"""

import re
import urllib.request
import urllib.parse

# Ordered by reliability: the !3d/!4d pair (when present) is the actual pin
# location for "place" links, whereas the @lat,lon in the URL is only the
# viewport center and can be slightly off. Coordinate-query style params are
# also very reliable since they are the intentional target of the link.
COORD_PATTERNS = [
    re.compile(r'!3d(-?\d+\.\d+)!4d(-?\d+\.\d+)'),
    re.compile(r'[?&]q=(-?\d+\.\d+),\s*(-?\d+\.\d+)'),
    re.compile(r'[?&]query=(-?\d+\.\d+),\s*(-?\d+\.\d+)'),
    re.compile(r'[?&]ll=(-?\d+\.\d+),\s*(-?\d+\.\d+)'),
    re.compile(r'@(-?\d+\.\d+),(-?\d+\.\d+)'),
]

NAME_PATTERN = re.compile(r'/maps/place/([^/@]+)')


def extract_coords(text):
    """Return (lat, lon) as floats found in `text`, or None."""
    for pattern in COORD_PATTERNS:
        m = pattern.search(text)
        if m:
            try:
                lat, lon = float(m.group(1)), float(m.group(2))
            except ValueError:
                continue
            if -90 <= lat <= 90 and -180 <= lon <= 180:
                return lat, lon
    return None


def extract_name(url):
    """Try to pull a human-readable place name out of a /maps/place/ URL."""
    m = NAME_PATTERN.search(url)
    if m:
        name = urllib.parse.unquote(m.group(1)).replace('+', ' ').strip()
        return name or None
    return None


def resolve_short_url(url, timeout=10):
    """
    Follow HTTP redirects for shortened links (goo.gl/maps, maps.app.goo.gl)
    and return the final resolved URL, or None on failure.
    """
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        response = urllib.request.urlopen(req, timeout=timeout)
        return response.geturl()
    except Exception:
        return None


def parse_gmaps_url(url):
    """
    Given a Google Maps URL (full or short), return (lat, lon) or None if
    no coordinates could be determined.
    """
    url = url.strip()
    if not url:
        return None

    # Try parsing directly first - works for full links without a network call.
    coords = extract_coords(url)
    if coords:
        return coords

    # Fall back to resolving short links / redirects, then re-parse.
    if url.startswith('http'):
        resolved = resolve_short_url(url)
        if resolved and resolved != url:
            coords = extract_coords(resolved)
            if coords:
                return coords

    return None


def parse_gmaps_url_full(url):
    """
    Convenience wrapper returning a dict with name/lat/lon/resolved_url/status
    for a single input URL. Useful for building table rows in the UI.
    """
    url = url.strip()
    result = {
        "input_url": url,
        "resolved_url": url,
        "name": extract_name(url),
        "lat": None,
        "lon": None,
        "status": "Could not parse",
    }
    if not url:
        result["status"] = "Empty"
        return result

    coords = extract_coords(url)
    if not coords and url.startswith('http'):
        resolved = resolve_short_url(url)
        if resolved and resolved != url:
            result["resolved_url"] = resolved
            if not result["name"]:
                result["name"] = extract_name(resolved)
            coords = extract_coords(resolved)

    if coords:
        result["lat"], result["lon"] = coords
        result["status"] = "OK"

    if not result["name"]:
        result["name"] = "Point"

    return result
