# Public-Company KPI Prediction Markets (Kalshi + Polymarket)

## Definition
A market is included if the underlying resolves to a **public company KPI for a specific reporting period** (quarterly in this dataset), e.g. rides, deliveries, nights booked, bookings/GOV, subscribers, DAU/MAU, revenue, EPS.

Excluded: non-KPI company markets (price direction, valuation multiples, implied vol, M&A, regulation).

## Taxonomy
- Operational KPIs: rides/trips, deliveries/orders, nights booked, gross bookings/GOV.
- User metrics: subscribers, DAU/MAU.
- Financial KPIs: revenue/EPS/EBITDA (included when represented as KPI contracts).

## Findings Summary
- Curated KPI markets captured:
  - Polymarket: **22**
  - Kalshi: **49**
  - Combined: **71**
- Volume totals (best available from public APIs):
  - Polymarket `volume` (USD notionals): **825,718.19**
  - Kalshi `volume` (contracts): **713,375**
- Important comparability note: Kalshi and Polymarket volume units are not directly comparable (contracts vs USD notional).
- This category is concentrated in recurring quarterly earnings-adjacent KPI ladders for a small set of companies (Uber, DoorDash, Airbnb; plus some subscriber/MAU names).

## Methodology
1. Pulled candidate markets from public endpoints, no credentials:
   - Polymarket Gamma: `GET https://gamma-api.polymarket.com/markets?search=<keyword>&limit=100&offset=0`
   - Kalshi: `GET https://api.elections.kalshi.com/trade-api/v2/markets?search_term=<keyword>&status=<open|settled>&limit=...`
2. Used keyword discovery: `uber`, `doordash`, `airbnb`, `rides`, `deliveries`, `bookings`, `subscribers`, `mau`, `dau`, `revenue`, `eps`.
3. Manually curated to KPI-only contracts and normalized:
   - `company`, `kpi`, and reporting period (`period_start`, `period_end` from quarter text)
   - `resolution_date` from market end/expiration metadata
4. Aggregated by month and quarter using `period_start`.

## Reproducibility
- Fetch candidates: `python3 scripts/fetch_markets.py` (writes `out/raw/*.json`)
- Build curated outputs used in this run: `python3 scripts/build_outputs.py`

Outputs:
- `out/markets_polymarket.csv`
- `out/markets_kalshi.csv`
- `out/agg_by_month.csv`
- `out/agg_by_quarter.csv`
- `out/notes_gaps.md`
## Open interest / liquidity fields
- `polymarket_liquidity_current`: Polymarket Gamma `liquidity` (best public proxy for depth / OI-like).
- `open_interest_current`: Kalshi open-interest-like field as available in the public market listing snapshots used here.
- `open_interest_at_resolution`: **not available from the public snapshots used in this repo** (would require historical OI time series or per-market history). Left blank for now.
- `asof_utc`: when the CSV was last regenerated.

