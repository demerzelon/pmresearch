#!/usr/bin/env python3
"""Fetch candidate KPI markets from public Polymarket + Kalshi endpoints.

This script is the reproducible fetch step. It does no final curation.
"""

import json
import urllib.parse
import urllib.request
from pathlib import Path

RAW = Path("out/raw")
RAW.mkdir(parents=True, exist_ok=True)

POLY_BASE = "https://gamma-api.polymarket.com/markets"
KALSHI_BASE = "https://api.elections.kalshi.com/trade-api/v2/markets"

KEYWORDS = [
    "uber",
    "doordash",
    "airbnb",
    "deliveries",
    "rides",
    "bookings",
    "subscribers",
    "mau",
    "dau",
    "revenue",
    "eps",
]


def get_json(url):
    with urllib.request.urlopen(url, timeout=30) as r:
        return json.loads(r.read().decode("utf-8"))


def fetch_polymarket():
    out = {}
    for kw in KEYWORDS:
        qs = urllib.parse.urlencode({"search": kw, "limit": 100, "offset": 0})
        url = f"{POLY_BASE}?{qs}"
        out[kw] = get_json(url)
    (RAW / "polymarket_candidates.json").write_text(json.dumps(out, indent=2))


def fetch_kalshi():
    out = {}
    for kw in KEYWORDS:
        for status in ["open", "settled"]:
            qs = urllib.parse.urlencode({"search_term": kw, "status": status, "limit": 100})
            url = f"{KALSHI_BASE}?{qs}"
            key = f"{kw}:{status}"
            out[key] = get_json(url)
    (RAW / "kalshi_candidates.json").write_text(json.dumps(out, indent=2))


def main():
    fetch_polymarket()
    fetch_kalshi()
    print("Wrote raw candidate snapshots to out/raw/")


if __name__ == "__main__":
    main()
