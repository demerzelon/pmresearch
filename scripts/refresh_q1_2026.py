#!/usr/bin/env python3
"""Refresh dataset to detect and add relevant Q1 2026 public-company KPI markets.

- Polymarket: uses Gamma API keyword searches.
- Kalshi: uses trade-api/v2/markets keyword searches.

Writes updated CSVs to both out/ and docs/ and recomputes aggregates.

NOTE: This is best-effort discovery (keyword-based), not a full catalog crawl.
"""

from __future__ import annotations

import csv
import json
import re
import ssl
from collections import Counter, defaultdict
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from urllib.parse import urlencode
from urllib.request import Request, urlopen


def http_json(url: str) -> Any:
    req = Request(url, headers={"User-Agent": "Mozilla/5.0 (pmresearch refresh)"})
    # Some local environments lack a working cert chain; this keeps the refresh usable.
    ctx = ssl._create_unverified_context()
    with urlopen(req, timeout=45, context=ctx) as r:
        return json.loads(r.read().decode("utf-8"))


def quarter_bounds(year: int, q: int) -> tuple[str, str]:
    m1 = (q - 1) * 3 + 1
    m3 = m1 + 2
    start = f"{year:04d}-{m1:02d}-01"
    if m3 in (1, 3, 5, 7, 8, 10, 12):
        d = 31
    elif m3 == 2:
        d = 29 if (year % 4 == 0 and (year % 100 != 0 or year % 400 == 0)) else 28
    else:
        d = 30
    end = f"{year:04d}-{m3:02d}-{d:02d}"
    return start, end


Q_YEAR, Q_NUM = 2026, 1
PERIOD_START, PERIOD_END = quarter_bounds(Q_YEAR, Q_NUM)
ASOF_UTC = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


PM_BASE = "https://gamma-api.polymarket.com/markets"
KALSHI_BASE = "https://api.elections.kalshi.com/trade-api/v2/markets"


COMPANY_ALIASES = {
    "Uber": ["uber"],
    "DoorDash": ["doordash", "door dash"],
    "Airbnb": ["airbnb"],
    "Netflix": ["netflix"],
    "Spotify": ["spotify"],
    "Meta": ["meta", "facebook"],
    "Pinterest": ["pinterest"],
    "Snap": ["snap"],
    "Tesla": ["tesla"],
}

KPI_PATTERNS: list[tuple[str, re.Pattern[str]]] = [
    ("Deliveries", re.compile(r"\bdeliver(y|ies)\b", re.I)),
    ("Orders", re.compile(r"\borders?\b", re.I)),
    ("Rides", re.compile(r"\brides?\b", re.I)),
    ("Trips", re.compile(r"\btrips?\b", re.I)),
    ("Nights and experiences booked", re.compile(r"\bnights?\b|experiences booked", re.I)),
    ("Gross bookings", re.compile(r"gross bookings|\bbookings\b", re.I)),
    ("Gross order value", re.compile(r"gross order value|\bgov\b", re.I)),
    ("Premium subscribers", re.compile(r"premium subscribers?", re.I)),
    ("Subscribers", re.compile(r"\bsubscribers?\b", re.I)),
    ("Daily active users", re.compile(r"daily active|\bdau\b", re.I)),
    ("Monthly active users", re.compile(r"monthly active|\bmau\b", re.I)),
    ("Revenue", re.compile(r"\brevenue\b", re.I)),
    ("EPS", re.compile(r"\beps\b", re.I)),
]


def detect_company(text: str) -> str:
    t = text.lower()
    for company, aliases in COMPANY_ALIASES.items():
        if any(a in t for a in aliases):
            return company
    return "Unknown"


def detect_kpi(text: str) -> str:
    for name, pat in KPI_PATTERNS:
        if pat.search(text):
            return name
    return "KPI"


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="") as f:
        return list(csv.DictReader(f))


def write_csv(path: Path, rows: list[dict[str, str]], fieldnames: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        for r in rows:
            w.writerow({k: r.get(k, "") for k in fieldnames})


FIELDS = [
    "venue",
    "market_id",
    "slug",
    "question/title",
    "company",
    "kpi",
    "period_start",
    "period_end",
    "resolution_date",
    "url",
    "volume",
    "polymarket_liquidity_current",
    "open_interest_current",
    "open_interest_at_resolution",
    "asof_utc",
    "data_source",
]


def gamma_search(term: str, limit: int = 100, max_pages: int = 5) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    for page in range(max_pages):
        offset = page * limit
        url = f"{PM_BASE}?{urlencode({'search': term, 'limit': limit, 'offset': offset})}"
        data = http_json(url)
        if not data:
            break
        out.extend(data)
        if len(data) < limit:
            break
    return out


def refresh_polymarket(existing: list[dict[str, str]]) -> tuple[list[dict[str, str]], int]:
    existing_ids = {r["market_id"] for r in existing}

    # Focused queries to reduce false positives.
    queries = [
        "q1 2026 uber rides",
        "q1 2026 uber trips",
        "q1 2026 uber gross bookings",
        "q1 2026 doordash deliveries",
        "q1 2026 doordash orders",
        "q1 2026 doordash gov",
        "q1 2026 airbnb nights",
        "q1 2026 netflix subscribers",
        "q1 2026 mau",
        "q1 2026 dau",
    ]

    cand: dict[str, dict[str, Any]] = {}
    for q in queries:
        for m in gamma_search(q, max_pages=3):
            mid = str(m.get("id") or "").strip()
            if not mid:
                continue
            cand[mid] = m

    # Keep only Q1 2026 KPI-ish markets.
    added = 0
    for mid, m in cand.items():
        text = f"{m.get('question','')} {m.get('slug','')}".lower()
        if "q1" not in text or "2026" not in text:
            continue
        if "report" not in text and "will" not in text:
            # weak heuristic, but helps avoid noise
            continue
        company = detect_company(text)
        kpi = detect_kpi(text)
        if company == "Unknown":
            continue

        if mid in existing_ids:
            continue

        slug = str(m.get("slug") or mid)
        url = f"https://polymarket.com/event/{slug}"
        end_date_iso = (m.get("endDateIso") or "")
        resolution_date = end_date_iso or (m.get("endDate") or "")[:10]

        row = {
            "venue": "Polymarket",
            "market_id": mid,
            "slug": slug,
            "question/title": m.get("question") or "",
            "company": company,
            "kpi": kpi,
            "period_start": PERIOD_START,
            "period_end": PERIOD_END,
            "resolution_date": resolution_date,
            "url": url,
            "volume": str(m.get("volume") or m.get("volumeNum") or ""),
            "polymarket_liquidity_current": str(m.get("liquidity") or m.get("liquidityNum") or ""),
            "open_interest_current": "",
            "open_interest_at_resolution": "",
            "asof_utc": ASOF_UTC,
            "data_source": f"{PM_BASE}?search={q}",
        }
        existing.append(row)
        existing_ids.add(mid)
        added += 1

    return existing, added


def kalshi_search(term: str, status: str, limit: int = 200, max_pages: int = 12) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    cursor: str | None = None
    for _ in range(max_pages):
        params = {"search_term": term, "status": status, "limit": limit}
        if cursor:
            params["cursor"] = cursor
        url = f"{KALSHI_BASE}?{urlencode(params)}"
        data = http_json(url)
        mkts = data.get("markets") or []
        out.extend(mkts)
        cursor = data.get("cursor")
        if not cursor or len(mkts) < limit:
            break
    return out


def refresh_kalshi(existing: list[dict[str, str]]) -> tuple[list[dict[str, str]], int]:
    existing_ids = {r["market_id"] for r in existing}

    # KPI-first search terms. Kalshi tickers often carry the period (e.g. 26Q1).
    terms = [
        "Uber",
        "DoorDash",
        "Airbnb",
        "Netflix",
        "Spotify",
        "Pinterest",
        "Snap",
        "deliveries",
        "rides",
        "bookings",
        "subscribers",
        "MAU",
        "DAU",
        "revenue",
        "EPS",
        "26Q1",
        "Q1 2026",
    ]

    cand: dict[str, dict[str, Any]] = {}
    for t in terms:
        for status in ["open", "settled"]:
            for m in kalshi_search(t, status=status):
                ticker = str(m.get("ticker") or "").strip()
                if not ticker:
                    continue
                cand[ticker] = m

    # Filter to Q1 2026 by ticker/title.
    added = 0
    for ticker, m in cand.items():
        hay = f"{ticker} {m.get('title','')} {m.get('subtitle','')}".lower()
        if "26q1" not in hay and "q1" not in hay:
            continue
        if "2026" not in hay and "26q1" in hay:
            # ok
            pass
        elif "2026" not in hay:
            continue

        company = detect_company(hay)
        kpi = detect_kpi(hay)
        if company == "Unknown":
            continue

        if ticker in existing_ids:
            continue

        event_ticker = m.get("event_ticker") or ""
        url = f"https://kalshi.com/markets/{event_ticker}/{ticker}" if event_ticker else ""

        # Prefer expiration_time, fallback close_time.
        res = (m.get("expiration_time") or m.get("close_time") or "")
        resolution_date = res[:10]

        row = {
            "venue": "Kalshi",
            "market_id": ticker,
            "slug": ticker,
            "question/title": m.get("title") or "",
            "company": company,
            "kpi": kpi,
            "period_start": PERIOD_START,
            "period_end": PERIOD_END,
            "resolution_date": resolution_date,
            "url": url,
            "volume": str(m.get("volume") or ""),
            "polymarket_liquidity_current": "",
            "open_interest_current": str(m.get("open_interest") or ""),
            "open_interest_at_resolution": "",
            "asof_utc": ASOF_UTC,
            "data_source": f"{KALSHI_BASE}?search_term={t}",
        }
        existing.append(row)
        existing_ids.add(ticker)
        added += 1

    return existing, added


def recompute_aggregates(pm_rows: list[dict[str, str]], k_rows: list[dict[str, str]]) -> tuple[list[dict[str, str]], list[dict[str, str]]]:
    def month_key(d: str) -> str:
        return d[:7]

    def quarter_key(d: str) -> str:
        y, m, _ = d.split("-")
        q = (int(m) - 1) // 3 + 1
        return f"{y}-Q{q}"

    all_rows = pm_rows + k_rows

    def agg(key_name: str, key_fn):
        grp = defaultdict(lambda: {"volume": 0.0, "count": 0})
        keys = set()
        for r in all_rows:
            k = key_fn(r["period_start"])
            keys.add(k)
            venue = r["venue"]
            grp[(k, venue)]["volume"] += float(r.get("volume") or 0)
            grp[(k, venue)]["count"] += 1

        out = []
        for k in sorted(keys):
            pm = grp.get((k, "Polymarket"), {"volume": 0, "count": 0})
            ka = grp.get((k, "Kalshi"), {"volume": 0, "count": 0})
            for venue, d in [
                ("Polymarket", pm),
                ("Kalshi", ka),
                ("Combined", {"volume": pm["volume"] + ka["volume"], "count": pm["count"] + ka["count"]}),
            ]:
                out.append(
                    {
                        key_name: k,
                        "venue": venue,
                        "market_count": str(d["count"]),
                        "total_volume": f"{d['volume']:.6f}".rstrip("0").rstrip("."),
                    }
                )
        return out

    by_month = agg("month", month_key)
    by_quarter = agg("quarter", quarter_key)
    return by_month, by_quarter


def main() -> None:
    out_pm = read_csv(Path("out/markets_polymarket.csv"))
    out_k = read_csv(Path("out/markets_kalshi.csv"))

    out_pm, pm_added = refresh_polymarket(out_pm)
    out_k, k_added = refresh_kalshi(out_k)

    # Keep deterministic ordering.
    def sort_key(r: dict[str, str]):
        return (r.get("period_start", ""), r.get("company", ""), r.get("kpi", ""), r.get("market_id", ""))

    out_pm.sort(key=sort_key)
    out_k.sort(key=sort_key)

    by_month, by_quarter = recompute_aggregates(out_pm, out_k)

    # Write to out/ and docs/
    for base in [Path("out"), Path("docs")]:
        write_csv(base / "markets_polymarket.csv", out_pm, FIELDS)
        write_csv(base / "markets_kalshi.csv", out_k, FIELDS)
        write_csv(base / "agg_by_month.csv", by_month, ["month", "venue", "market_count", "total_volume"])
        write_csv(base / "agg_by_quarter.csv", by_quarter, ["quarter", "venue", "market_count", "total_volume"])

    print(f"Q1 2026 refresh complete. Added: Polymarket={pm_added}, Kalshi={k_added}")


if __name__ == "__main__":
    main()
