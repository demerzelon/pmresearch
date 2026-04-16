#!/usr/bin/env python3
"""Build a live snapshot of Polymarket + Kalshi markets closing in the next 24h.

Filters:
- close/finality time in [now, now+24h]
- implied probability in [0.20, 0.80] (non-edge)
"""

from __future__ import annotations

import csv
import json
import urllib.parse
import urllib.request
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

OUT = Path("out")
DOCS = Path("docs")
OUT.mkdir(exist_ok=True)
DOCS.mkdir(exist_ok=True)

PM_BASE = "https://gamma-api.polymarket.com/markets"
KALSHI_BASE = "https://api.elections.kalshi.com/trade-api/v2/markets"

HEADERS = {"User-Agent": "Mozilla/5.0"}


def get_json(url: str) -> Any:
    last_err = None
    for _ in range(3):
        try:
            req = urllib.request.Request(url, headers=HEADERS)
            with urllib.request.urlopen(req, timeout=20) as r:
                return json.loads(r.read().decode("utf-8"))
        except Exception as e:
            last_err = e
    if last_err:
        raise last_err
    raise RuntimeError("unreachable")


def parse_iso(ts: Optional[str]) -> Optional[datetime]:
    if not ts:
        return None
    try:
        if ts.endswith("Z"):
            ts = ts[:-1] + "+00:00"
        return datetime.fromisoformat(ts).astimezone(timezone.utc)
    except Exception:
        return None


def pct(v: Optional[float]) -> str:
    if v is None:
        return ""
    return f"{v*100:.2f}"


def fetch_polymarket(now: datetime, until: datetime) -> List[Dict[str, Any]]:
    rows: List[Dict[str, Any]] = []
    seen = set()
    offset = 0
    limit = 500
    max_pages = 12  # up to 6k markets

    for _ in range(max_pages):
        qs = urllib.parse.urlencode({"limit": limit, "offset": offset})
        data = get_json(f"{PM_BASE}?{qs}")
        if not isinstance(data, list) or not data:
            break

        for m in data:
            mid = str(m.get("id", ""))
            if not mid or mid in seen:
                continue
            seen.add(mid)

            end_dt = parse_iso(m.get("endDate"))
            if not end_dt or not (now <= end_dt <= until):
                continue

            if bool(m.get("closed")):
                continue

            prices = m.get("outcomePrices") or []
            yes_p = None
            if isinstance(prices, list) and prices:
                try:
                    yes_p = float(prices[0])
                except Exception:
                    yes_p = None
            if yes_p is None:
                continue

            if not (0.20 <= yes_p <= 0.80):
                continue

            rows.append(
                {
                    "venue": "Polymarket",
                    "market_id": mid,
                    "title": (m.get("question") or "").strip(),
                    "url": f"https://polymarket.com/event/{m.get('slug','')}",
                    "close_time_utc": end_dt.isoformat().replace("+00:00", "Z"),
                    "hours_to_close": round((end_dt - now).total_seconds() / 3600, 2),
                    "prob_yes_pct": pct(yes_p),
                    "band": "20-80",
                    "volume": m.get("volume", ""),
                    "liquidity_or_oi": m.get("liquidity", ""),
                }
            )

        if len(data) < limit:
            break
        offset += limit

    return rows


def kalshi_prob(m: Dict[str, Any]) -> Optional[float]:
    for a, b in (("yes_bid_dollars", "yes_ask_dollars"),):
        bid = m.get(a)
        ask = m.get(b)
        if bid is not None and ask is not None:
            try:
                return (float(bid) + float(ask)) / 2.0
            except Exception:
                pass
    for k in ("last_price_dollars", "yes_ask_dollars", "yes_bid_dollars"):
        v = m.get(k)
        if v is not None:
            try:
                return float(v)
            except Exception:
                continue
    return None


def fetch_kalshi(now: datetime, until: datetime) -> List[Dict[str, Any]]:
    rows: List[Dict[str, Any]] = []
    cursor = None
    pages = 0

    while pages < 40:
        params = {"status": "open", "limit": 1000}
        if cursor:
            params["cursor"] = cursor
        qs = urllib.parse.urlencode(params)
        payload = get_json(f"{KALSHI_BASE}?{qs}")
        markets = payload.get("markets") or []
        if not markets:
            break

        for m in markets:
            close_dt = parse_iso(m.get("close_time") or m.get("expiration_time") or m.get("expected_expiration_time"))
            if not close_dt or not (now <= close_dt <= until):
                continue

            p = kalshi_prob(m)
            if p is None or not (0.20 <= p <= 0.80):
                continue

            ticker = m.get("ticker", "")
            event_ticker = m.get("event_ticker", "")
            url = f"https://kalshi.com/markets/{event_ticker}/{ticker}" if event_ticker and ticker else ""

            rows.append(
                {
                    "venue": "Kalshi",
                    "market_id": ticker,
                    "title": (m.get("title") or "").strip(),
                    "url": url,
                    "close_time_utc": close_dt.isoformat().replace("+00:00", "Z"),
                    "hours_to_close": round((close_dt - now).total_seconds() / 3600, 2),
                    "prob_yes_pct": pct(p),
                    "band": "20-80",
                    "volume": m.get("volume_24h_fp", ""),
                    "liquidity_or_oi": m.get("open_interest_fp", ""),
                }
            )

        cursor = payload.get("cursor")
        pages += 1
        if not cursor:
            break

    return rows


def write_csv(path: Path, rows: List[Dict[str, Any]]) -> None:
    fields = [
        "venue",
        "market_id",
        "title",
        "url",
        "close_time_utc",
        "hours_to_close",
        "prob_yes_pct",
        "band",
        "volume",
        "liquidity_or_oi",
    ]
    with path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        w.writerows(rows)


def main() -> None:
    now = datetime.now(timezone.utc)
    until = now + timedelta(hours=24)

    rows = fetch_polymarket(now, until) + fetch_kalshi(now, until)
    rows.sort(key=lambda r: (r["close_time_utc"], r["venue"]))

    out_name = f"markets_closing_24h_{now.strftime('%Y%m%d_%H%M%S')}.csv"
    out_path = OUT / out_name
    docs_path = DOCS / "markets_closing_24h_latest.csv"

    write_csv(out_path, rows)
    write_csv(docs_path, rows)

    print(json.dumps({
        "snapshot_utc": now.isoformat().replace("+00:00", "Z"),
        "count": len(rows),
        "snapshot_file": str(out_path),
        "latest_file": str(docs_path),
    }, indent=2))


if __name__ == "__main__":
    main()
