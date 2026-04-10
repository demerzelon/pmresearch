# pmresearch
Research into **public-company KPI prediction markets** across **Polymarket** and **Kalshi**.

- Rendered site (GitHub Pages): see repo Settings → Pages (enabled by automation below)
- Data + aggregates: [`out/`](./out)
- Repro scripts: [`scripts/`](./scripts)

## What are "public company KPI markets"?
Markets whose resolution is a **reported KPI** for a public company for a specific period (quarter/month/etc.), e.g. Uber rides, DoorDash deliveries, Airbnb nights booked, subscribers/DAU/MAU, revenue/EPS.

## Outputs
- `out/markets_polymarket.csv`, `out/markets_kalshi.csv`, `out/agg_by_month.csv`, `out/agg_by_quarter.csv`
- `docs/polymarket_liq_100k_500k_all_latest.csv`
- `docs/polymarket_liq_100k_500k_longtail_latest.csv`

Snapshot-specific files:
- `out/polymarket_liq_100k_500k_all_20260410_074706.csv`
- `out/polymarket_liq_100k_500k_longtail_20260410_074706.csv`

See `out/README.md` for the detailed methodology and caveats.