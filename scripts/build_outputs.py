#!/usr/bin/env python3
import csv
from collections import defaultdict
from datetime import datetime
from pathlib import Path

OUT = Path("out")
OUT.mkdir(exist_ok=True)


def q_start_end(q):
    y, qn = q.split("-Q")
    y = int(y)
    qn = int(qn)
    m1 = (qn - 1) * 3 + 1
    m3 = m1 + 2
    start = f"{y:04d}-{m1:02d}-01"
    if m3 in (1, 3, 5, 7, 8, 10, 12):
        d = 31
    elif m3 == 2:
        d = 29 if (y % 4 == 0 and (y % 100 != 0 or y % 400 == 0)) else 28
    else:
        d = 30
    end = f"{y:04d}-{m3:02d}-{d:02d}"
    return start, end

polymarket_rows = [
    # Uber
    ("359476", "q4-2025-uber-gross-bookings-between-44b-and-45b", "How much gross bookings will Uber report for Q4 of 2025?", "Uber", "Gross bookings", "2025-Q4", "2026-02-10", "https://polymarket.com/event/q4-2025-uber-gross-bookings-between-44b-and-45b", 83920.666214, 22928.560177),
    ("350159", "q4-2025-uber-rides-between-3b-and-3-2b", "How many rides will Uber report for Q4 of 2025?", "Uber", "Rides", "2025-Q4", "2026-02-05", "https://polymarket.com/event/q4-2025-uber-rides-between-3b-and-3-2b", 17123.286927, 5891.669108),
    ("334365", "q3-2025-uber-trips-between-3-2b-and-3-35b", "How many trips will Uber report for Q3 of 2025?", "Uber", "Trips", "2025-Q3", "2025-11-05", "https://polymarket.com/event/q3-2025-uber-trips-between-3-2b-and-3-35b", 17487.200061, 11914.468111),
    ("320709", "q2-2025-uber-rides-between-3-1b-and-3-2b", "How many rides will Uber report for Q2 of 2025?", "Uber", "Rides", "2025-Q2", "2025-08-06", "https://polymarket.com/event/q2-2025-uber-rides-between-3-1b-and-3-2b", 21288.443531, 5100.506937),
    ("294062", "q1-2025-uber-rides-between-2-95b-and-3-05b", "How many rides will Uber report for Q1 of 2025?", "Uber", "Rides", "2025-Q1", "2025-05-07", "https://polymarket.com/event/q1-2025-uber-rides-between-2-95b-and-3-05b", 71720.825683, 12528.93833),
    ("268404", "q4-2024-uber-rides-between-2-95b-and-3-05b", "How many rides will Uber report for Q4 of 2024?", "Uber", "Rides", "2024-Q4", "2025-02-05", "https://polymarket.com/event/q4-2024-uber-rides-between-2-95b-and-3-05b", 194410.670274, 20133.55458),
    ("248180", "q3-2024-uber-rides-between-2-8b-and-2-95b", "How many rides will Uber report for Q3 of 2024?", "Uber", "Rides", "2024-Q3", "2024-11-06", "https://polymarket.com/event/q3-2024-uber-rides-between-2-8b-and-2-95b", 49276.150645, 22067.281536),
    # DoorDash
    ("359477", "q4-2025-doordash-deliveries-between-794m-and-810m", "How many deliveries will DoorDash report for Q4 of 2025?", "DoorDash", "Deliveries", "2025-Q4", "2026-02-10", "https://polymarket.com/event/q4-2025-doordash-deliveries-between-794m-and-810m", 3047.162434, 2112.257626),
    ("359479", "q4-2025-doordash-gov-between-23b-and-23-5b", "How much gross order value will DoorDash report for Q4 of 2025?", "DoorDash", "Gross order value", "2025-Q4", "2026-02-10", "https://polymarket.com/event/q4-2025-doordash-gov-between-23b-and-23-5b", 3007.108834, 2109.242037),
    ("334366", "q3-2025-doordash-deliveries-between-710m-and-730m", "How many deliveries will DoorDash report for Q3 of 2025?", "DoorDash", "Deliveries", "2025-Q3", "2025-11-05", "https://polymarket.com/event/q3-2025-doordash-deliveries-between-710m-and-730m", 2143.338978, 1692.044494),
    ("320710", "q2-2025-doordash-deliveries-between-690m-and-710m", "How many deliveries will DoorDash report for Q2 of 2025?", "DoorDash", "Deliveries", "2025-Q2", "2025-08-06", "https://polymarket.com/event/q2-2025-doordash-deliveries-between-690m-and-710m", 3116.266595, 2017.322146),
    ("294063", "q1-2025-doordash-deliveries-between-670m-and-685m", "How many deliveries will DoorDash report for Q1 of 2025?", "DoorDash", "Deliveries", "2025-Q1", "2025-05-07", "https://polymarket.com/event/q1-2025-doordash-deliveries-between-670m-and-685m", 6878.995093, 3115.443962),
    ("268405", "q4-2024-doordash-orders-between-670m-and-690m", "How many orders will DoorDash report for Q4 of 2024?", "DoorDash", "Orders", "2024-Q4", "2025-02-05", "https://polymarket.com/event/q4-2024-doordash-orders-between-670m-and-690m", 34754.164482, 8171.509068),
    ("248181", "q3-2024-doordash-orders-between-640m-and-655m", "How many orders will DoorDash report for Q3 of 2024?", "DoorDash", "Orders", "2024-Q3", "2024-11-06", "https://polymarket.com/event/q3-2024-doordash-orders-between-640m-and-655m", 47229.28355, 6601.58861),
    # Airbnb
    ("359481", "q4-2025-airbnb-nights-booked-between-120m-and-130m", "How many nights and experiences booked will Airbnb report for Q4 of 2025?", "Airbnb", "Nights and experiences booked", "2025-Q4", "2026-02-10", "https://polymarket.com/event/q4-2025-airbnb-nights-booked-between-120m-and-130m", 1948.514618, 1628.422841),
    ("334368", "q3-2025-airbnb-nights-booked-between-115m-and-120m", "How many nights and experiences booked will Airbnb report for Q3 of 2025?", "Airbnb", "Nights and experiences booked", "2025-Q3", "2025-11-05", "https://polymarket.com/event/q3-2025-airbnb-nights-booked-between-115m-and-120m", 1555.780152, 1443.516177),
    ("320712", "q2-2025-airbnb-nights-booked-between-130m-and-140m", "How many nights and experiences booked will Airbnb report for Q2 of 2025?", "Airbnb", "Nights and experiences booked", "2025-Q2", "2025-08-06", "https://polymarket.com/event/q2-2025-airbnb-nights-booked-between-130m-and-140m", 3349.577465, 1809.942231),
    ("294065", "q1-2025-airbnb-nights-between-140m-and-145m", "How many nights and experiences booked will Airbnb report for Q1 of 2025?", "Airbnb", "Nights and experiences booked", "2025-Q1", "2025-05-07", "https://polymarket.com/event/q1-2025-airbnb-nights-between-140m-and-145m", 11292.847306, 4052.772971),
    ("268407", "q4-2024-airbnb-nights-between-110m-and-120m", "How many nights and experiences booked will Airbnb report for Q4 of 2024?", "Airbnb", "Nights and experiences booked", "2024-Q4", "2025-02-05", "https://polymarket.com/event/q4-2024-airbnb-nights-between-110m-and-120m", 28769.496109, 4668.624523),
    ("248183", "q3-2024-airbnb-nights-between-120m-and-130m", "How many nights and experiences booked will Airbnb report for Q3 of 2024?", "Airbnb", "Nights and experiences booked", "2024-Q3", "2024-11-06", "https://polymarket.com/event/q3-2024-airbnb-nights-between-120m-and-130m", 32203.317564, 6064.693059),
    ("225019", "q2-2024-airbnb-nights-between-120m-and-130m", "How many nights and experiences booked will Airbnb report for Q2 of 2024?", "Airbnb", "Nights and experiences booked", "2024-Q2", "2024-08-07", "https://polymarket.com/event/q2-2024-airbnb-nights-between-120m-and-130m", 115515.721521, 6886.457153),
    ("202350", "q1-2024-airbnb-nights-between-130m-and-140m", "How many nights and experiences booked will Airbnb report for Q1 of 2024?", "Airbnb", "Nights and experiences booked", "2024-Q1", "2024-05-08", "https://polymarket.com/event/q1-2024-airbnb-nights-between-130m-and-140m", 75679.372592, 8009.32695),
]

kalshi_rows = [
    # Uber bookings open/settled
    ("KXUBERBOOKINGS-25Q4-T44.9", "How many gross bookings will Uber report in Q4 of 2025?", "Uber", "Gross bookings", "2025-Q4", "2026-02-10", "KXUBERBOOKINGS", 1362, 1494),
    ("KXUBERBOOKINGS-25Q4-T45.4", "How many gross bookings will Uber report in Q4 of 2025?", "Uber", "Gross bookings", "2025-Q4", "2026-02-10", "KXUBERBOOKINGS", 332, 392),
    ("KXUBERBOOKINGS-25Q4-T44.4", "How many gross bookings will Uber report in Q4 of 2025?", "Uber", "Gross bookings", "2025-Q4", "2026-02-10", "KXUBERBOOKINGS", 264, 302),
    ("KXUBERBOOKINGS-25Q4-T45.9", "How many gross bookings will Uber report in Q4 of 2025?", "Uber", "Gross bookings", "2025-Q4", "2026-02-10", "KXUBERBOOKINGS", 188, 253),
    ("KXUBERBOOKINGS-25Q4-T46.4", "How many gross bookings will Uber report in Q4 of 2025?", "Uber", "Gross bookings", "2025-Q4", "2026-02-10", "KXUBERBOOKINGS", 175, 183),
    ("KXUBERBOOKINGS-25Q3-T40.0", "How many gross bookings will Uber report in Q3 of 2025?", "Uber", "Gross bookings", "2025-Q3", "2025-11-05", "KXUBERBOOKINGS", 80165, 0),
    ("KXUBERBOOKINGS-25Q3-T39.5", "How many gross bookings will Uber report in Q3 of 2025?", "Uber", "Gross bookings", "2025-Q3", "2025-11-05", "KXUBERBOOKINGS", 73089, 0),
    ("KXUBERBOOKINGS-25Q3-BT39.0", "How many gross bookings will Uber report in Q3 of 2025?", "Uber", "Gross bookings", "2025-Q3", "2025-11-05", "KXUBERBOOKINGS", 49300, 0),
    ("KXUBERBOOKINGS-25Q3-T40.5", "How many gross bookings will Uber report in Q3 of 2025?", "Uber", "Gross bookings", "2025-Q3", "2025-11-05", "KXUBERBOOKINGS", 36914, 0),
    ("KXUBERBOOKINGS-25Q3-T41.0", "How many gross bookings will Uber report in Q3 of 2025?", "Uber", "Gross bookings", "2025-Q3", "2025-11-05", "KXUBERBOOKINGS", 16607, 0),
    ("KXUBERBOOKINGS-25Q2-T39.9", "How many gross bookings will Uber report in Q2 of 2025?", "Uber", "Gross bookings", "2025-Q2", "2025-08-06", "KXUBERBOOKINGS", 52573, 0),
    ("KXUBERBOOKINGS-25Q2-T39.4", "How many gross bookings will Uber report in Q2 of 2025?", "Uber", "Gross bookings", "2025-Q2", "2025-08-06", "KXUBERBOOKINGS", 39824, 0),
    ("KXUBERBOOKINGS-25Q2-T40.4", "How many gross bookings will Uber report in Q2 of 2025?", "Uber", "Gross bookings", "2025-Q2", "2025-08-06", "KXUBERBOOKINGS", 26300, 0),
    ("KXUBERBOOKINGS-25Q2-BT38.9", "How many gross bookings will Uber report in Q2 of 2025?", "Uber", "Gross bookings", "2025-Q2", "2025-08-06", "KXUBERBOOKINGS", 24510, 0),
    ("KXUBERBOOKINGS-25Q2-T40.9", "How many gross bookings will Uber report in Q2 of 2025?", "Uber", "Gross bookings", "2025-Q2", "2025-08-06", "KXUBERBOOKINGS", 12297, 0),
    ("KXUBERBOOKINGS-25Q1-T37.5", "How many gross bookings will Uber report in Q1 of 2025?", "Uber", "Gross bookings", "2025-Q1", "2025-05-07", "KXUBERBOOKINGS", 116449, 0),
    ("KXUBERBOOKINGS-25Q1-BT37.0", "How many gross bookings will Uber report in Q1 of 2025?", "Uber", "Gross bookings", "2025-Q1", "2025-05-07", "KXUBERBOOKINGS", 70503, 0),
    ("KXUBERBOOKINGS-25Q1-T38.0", "How many gross bookings will Uber report in Q1 of 2025?", "Uber", "Gross bookings", "2025-Q1", "2025-05-07", "KXUBERBOOKINGS", 59357, 0),
    # DoorDash deliveries (open + settled)
    ("KXDASHGOV-25Q4-T23.2", "How much gross order value will DoorDash report in Q4 of 2025?", "DoorDash", "Gross order value", "2025-Q4", "2026-02-10", "KXDASHGOV", 108, 154),
    ("KXDASHGOV-25Q4-T23.7", "How much gross order value will DoorDash report in Q4 of 2025?", "DoorDash", "Gross order value", "2025-Q4", "2026-02-10", "KXDASHGOV", 42, 60),
    ("KXDASHGOV-25Q4-T22.7", "How much gross order value will DoorDash report in Q4 of 2025?", "DoorDash", "Gross order value", "2025-Q4", "2026-02-10", "KXDASHGOV", 18, 24),
    ("KXDASHGOV-25Q4-T24.2", "How much gross order value will DoorDash report in Q4 of 2025?", "DoorDash", "Gross order value", "2025-Q4", "2026-02-10", "KXDASHGOV", 8, 8),
    ("KXDASHGOV-25Q4-T22.2", "How much gross order value will DoorDash report in Q4 of 2025?", "DoorDash", "Gross order value", "2025-Q4", "2026-02-10", "KXDASHGOV", 7, 8),
    ("KXDASHDELIV-25Q3-T720", "How many deliveries will DoorDash report in Q3 of 2025?", "DoorDash", "Deliveries", "2025-Q3", "2025-11-05", "KXDASHDELIV", 5321, 0),
    ("KXDASHDELIV-25Q3-T715", "How many deliveries will DoorDash report in Q3 of 2025?", "DoorDash", "Deliveries", "2025-Q3", "2025-11-05", "KXDASHDELIV", 4142, 0),
    ("KXDASHDELIV-25Q3-T710", "How many deliveries will DoorDash report in Q3 of 2025?", "DoorDash", "Deliveries", "2025-Q3", "2025-11-05", "KXDASHDELIV", 3707, 0),
    ("KXDASHDELIV-25Q3-BT705", "How many deliveries will DoorDash report in Q3 of 2025?", "DoorDash", "Deliveries", "2025-Q3", "2025-11-05", "KXDASHDELIV", 1965, 0),
    ("KXDASHDELIV-25Q3-T725", "How many deliveries will DoorDash report in Q3 of 2025?", "DoorDash", "Deliveries", "2025-Q3", "2025-11-05", "KXDASHDELIV", 1893, 0),
    ("KXDASHDELIV-25Q2-T700", "How many deliveries will DoorDash report in Q2 of 2025?", "DoorDash", "Deliveries", "2025-Q2", "2025-08-06", "KXDASHDELIV", 10536, 0),
    ("KXDASHDELIV-25Q2-BT695", "How many deliveries will DoorDash report in Q2 of 2025?", "DoorDash", "Deliveries", "2025-Q2", "2025-08-06", "KXDASHDELIV", 7707, 0),
    ("KXDASHDELIV-25Q2-T705", "How many deliveries will DoorDash report in Q2 of 2025?", "DoorDash", "Deliveries", "2025-Q2", "2025-08-06", "KXDASHDELIV", 7575, 0),
    ("KXDASHDELIV-25Q2-T710", "How many deliveries will DoorDash report in Q2 of 2025?", "DoorDash", "Deliveries", "2025-Q2", "2025-08-06", "KXDASHDELIV", 2430, 0),
    ("KXDASHDELIV-25Q2-T715", "How many deliveries will DoorDash report in Q2 of 2025?", "DoorDash", "Deliveries", "2025-Q2", "2025-08-06", "KXDASHDELIV", 948, 0),
    # Airbnb nights
    ("KXABNBNIGHTS-25Q4-T122.5", "How many nights and experiences booked will Airbnb report in Q4 of 2025?", "Airbnb", "Nights and experiences booked", "2025-Q4", "2026-02-10", "KXABNBNIGHTS", 95, 126),
    ("KXABNBNIGHTS-25Q4-BT117.5", "How many nights and experiences booked will Airbnb report in Q4 of 2025?", "Airbnb", "Nights and experiences booked", "2025-Q4", "2026-02-10", "KXABNBNIGHTS", 63, 80),
    ("KXABNBNIGHTS-25Q4-T127.5", "How many nights and experiences booked will Airbnb report in Q4 of 2025?", "Airbnb", "Nights and experiences booked", "2025-Q4", "2026-02-10", "KXABNBNIGHTS", 44, 62),
    ("KXABNBNIGHTS-25Q4-T132.5", "How many nights and experiences booked will Airbnb report in Q4 of 2025?", "Airbnb", "Nights and experiences booked", "2025-Q4", "2026-02-10", "KXABNBNIGHTS", 20, 32),
    ("KXABNBNIGHTS-25Q4-BT112.5", "How many nights and experiences booked will Airbnb report in Q4 of 2025?", "Airbnb", "Nights and experiences booked", "2025-Q4", "2026-02-10", "KXABNBNIGHTS", 19, 24),
    ("KXABNBNIGHTS-25Q3-T115", "How many nights and experiences booked will Airbnb report in Q3 of 2025?", "Airbnb", "Nights and experiences booked", "2025-Q3", "2025-11-05", "KXABNBNIGHTS", 2757, 0),
    ("KXABNBNIGHTS-25Q3-T117.5", "How many nights and experiences booked will Airbnb report in Q3 of 2025?", "Airbnb", "Nights and experiences booked", "2025-Q3", "2025-11-05", "KXABNBNIGHTS", 1774, 0),
    ("KXABNBNIGHTS-25Q3-T120", "How many nights and experiences booked will Airbnb report in Q3 of 2025?", "Airbnb", "Nights and experiences booked", "2025-Q3", "2025-11-05", "KXABNBNIGHTS", 916, 0),
    ("KXABNBNIGHTS-25Q3-BT112.5", "How many nights and experiences booked will Airbnb report in Q3 of 2025?", "Airbnb", "Nights and experiences booked", "2025-Q3", "2025-11-05", "KXABNBNIGHTS", 542, 0),
    ("KXABNBNIGHTS-25Q3-BT110", "How many nights and experiences booked will Airbnb report in Q3 of 2025?", "Airbnb", "Nights and experiences booked", "2025-Q3", "2025-11-05", "KXABNBNIGHTS", 219, 0),
    # Subscriber / MAU KPI
    ("KXNETFLXSUBS-25Q4-T4.7", "How many global paid subscribers will Netflix report in Q4 of 2025?", "Netflix", "Global paid subscribers", "2025-Q4", "2026-01-20", "KXNETFLXSUBS", 170, 274),
    ("KXNETFLXSUBS-25Q4-T4.8", "How many global paid subscribers will Netflix report in Q4 of 2025?", "Netflix", "Global paid subscribers", "2025-Q4", "2026-01-20", "KXNETFLXSUBS", 42, 81),
    ("KXNETFLXSUBS-25Q4-T4.9", "How many global paid subscribers will Netflix report in Q4 of 2025?", "Netflix", "Global paid subscribers", "2025-Q4", "2026-01-20", "KXNETFLXSUBS", 13, 26),
    ("KXSNAPMAU-25Q4-T920", "How many daily active users will Snap report in Q4 of 2025?", "Snap", "Daily active users", "2025-Q4", "2026-02-05", "KXSNAPMAU", 44, 73),
    ("KXSNAPMAU-25Q4-T970", "How many daily active users will Snap report in Q4 of 2025?", "Snap", "Daily active users", "2025-Q4", "2026-02-05", "KXSNAPMAU", 13, 21),
    ("KXPINSMAU-25Q4-T582", "How many monthly active users will Pinterest report in Q4 of 2025?", "Pinterest", "Monthly active users", "2025-Q4", "2026-02-05", "KXPINSMAU", 28, 36),
]

poly_out = []
for mid, slug, title, company, kpi, q, resolution_date, url, vol, liq in polymarket_rows:
    ps, pe = q_start_end(q)
    poly_out.append({
        "venue": "Polymarket",
        "market_id": mid,
        "slug": slug,
        "question/title": title,
        "company": company,
        "kpi": kpi,
        "period_start": ps,
        "period_end": pe,
        "resolution_date": resolution_date,
        "url": url,
        "volume": vol,
        "liquidity/open_interest": liq,
        "data_source": "https://gamma-api.polymarket.com/markets?search=<keyword>&limit=100&offset=0",
    })

kalshi_out = []
for ticker, title, company, kpi, q, resolution_date, event_ticker, vol, oi in kalshi_rows:
    ps, pe = q_start_end(q)
    kalshi_out.append({
        "venue": "Kalshi",
        "market_id": ticker,
        "slug": ticker,
        "question/title": title,
        "company": company,
        "kpi": kpi,
        "period_start": ps,
        "period_end": pe,
        "resolution_date": resolution_date,
        "url": f"https://kalshi.com/markets/{event_ticker}/{ticker}",
        "volume": vol,
        "liquidity/open_interest": oi,
        "data_source": "https://api.elections.kalshi.com/trade-api/v2/markets?search_term=<keyword>&status=<open|settled>&limit=10",
    })


def write_csv(path, rows):
    fields = [
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
        "liquidity/open_interest",
        "data_source",
    ]
    with path.open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        w.writerows(rows)


def month_key(d):
    return d[:7]


def quarter_key(d):
    dt = datetime.strptime(d, "%Y-%m-%d")
    q = (dt.month - 1) // 3 + 1
    return f"{dt.year}-Q{q}"


def build_agg(rows, key_name, key_fn):
    grp = defaultdict(lambda: {"volume": 0.0, "count": 0})
    for r in rows:
        k = key_fn(r["period_start"])
        grp[(k, r["venue"])]["volume"] += float(r["volume"] or 0)
        grp[(k, r["venue"])]["count"] += 1

    all_keys = sorted({k for k, _ in grp.keys()})
    out = []
    for k in all_keys:
        p_vol = grp.get((k, "Polymarket"), {"volume": 0, "count": 0})
        k_vol = grp.get((k, "Kalshi"), {"volume": 0, "count": 0})
        for venue, v in [("Polymarket", p_vol), ("Kalshi", k_vol), ("Combined", {"volume": p_vol["volume"] + k_vol["volume"], "count": p_vol["count"] + k_vol["count"]})]:
            out.append({
                key_name: k,
                "venue": venue,
                "market_count": v["count"],
                "total_volume": round(v["volume"], 6),
            })
    return out


def write_agg(path, rows, key_name):
    with path.open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=[key_name, "venue", "market_count", "total_volume"])
        w.writeheader()
        w.writerows(rows)


write_csv(OUT / "markets_polymarket.csv", poly_out)
write_csv(OUT / "markets_kalshi.csv", kalshi_out)
all_rows = poly_out + kalshi_out
write_agg(OUT / "agg_by_month.csv", build_agg(all_rows, "month", month_key), "month")
write_agg(OUT / "agg_by_quarter.csv", build_agg(all_rows, "quarter", quarter_key), "quarter")
print("Wrote CSV outputs to out/")
