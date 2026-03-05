# Gaps / Limits

1. Volume unit mismatch across venues.
- Polymarket `volume` is USD-style notional.
- Kalshi `volume` is contract count.
- Combined totals are useful for within-venue trends, not apples-to-apples cross-venue liquidity comparison.

2. Lifetime volume semantics differ.
- Public endpoints do not provide a single normalized lifetime-dollar metric across both venues.
- This study uses each venue's best public `volume` field as-is.

3. Category coverage is best-effort keyword + manual curation.
- KPI markets with unusual naming may be missed.
- Some search windows return only top results; deeper pagination can add additional strikes/contracts.

4. Strike-ladder inflation.
- Many Kalshi events are represented as multiple strike contracts for one KPI release (e.g., Uber bookings thresholds).
- Market counts therefore represent tradable contracts, not unique KPI events.

5. Period normalization assumptions.
- Quarter boundaries are normalized to calendar quarter start/end based on market text.
- Exact company fiscal-calendar nuances are not modeled.

6. Network/environment constraint during build.
- Local shell DNS/network was unavailable in this run, so API retrieval was performed via web-access tooling and encoded into reproducible scripts + curated outputs.
