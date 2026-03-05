# Work log — pmresearch (Polymarket + Kalshi public-company KPI markets)

This file documents what we did in this chat/session to build **pmresearch**: a small research repo + GitHub Pages site that catalogs **public-company KPI prediction markets** on **Polymarket** and **Kalshi**, with simple aggregates and visualizations.

Repo: https://github.com/demerzelon/pmresearch  
Pages: https://demerzelon.github.io/pmresearch/

> Notes on comparability: Polymarket and Kalshi volume/open-interest/liquidity units differ. The repo intentionally keeps venue-native fields and labels them clearly.

---

## 1) Goal (as stated)

- Find and install **Polymarket** and **Kalshi** skills.
- Research **public company KPI markets** (examples: DoorDash deliveries, Uber rides) across both venues.
- Estimate the size of this category and summarize **volume by month/quarter**.
- Publish results in a **new GitHub repo** with a **public GitHub Pages** landing page.
- Improve presentation with better **data visualization**.
- Add **open interest** (requested: current OI and OI at resolution).
- Re-check that the market list covers the category; add missing markets.

---

## 2) Skills discovery + install

### Polymarket
- Found multiple related skills on ClawHub (examples seen in search results): `polymarket-analysis`, `polymarket-agent`, `polymarket-api`, `polymarket-odds`, etc.
- Installed:
  - `polymarket-agent` → `~/.openclaw/skills/polymarket-agent`
  - `polymarket-analysis` → `~/.openclaw/skills/polymarket-analysis`
  - `polyedge` → `~/.openclaw/skills/polyedge`

### Kalshi
- Found skills on ClawHub: `kalshi`, `kalshi-cli-trading`, `kalshi-trading`.
- Installed:
  - `kalshi` → `~/.openclaw/skills/kalshi`
  - `kalshi-trading` → `~/.openclaw/skills/kalshi-trading`

### Attempted visualization skills
- Searched ClawHub for visualization/deploy skills (e.g. `data-visualization-2`, `chart-image`, `github-pages-auto-deploy`).
- Installs failed due to **ClawHub rate limiting** (“Rate limit exceeded”).
- Workaround: improve the site using CDN libraries instead of installing a visualization skill.

---

## 3) Research run (Codex)

### Constraint encountered
- A true isolated “sub-agent” session couldn’t be spawned via `sessions_spawn` (allowlist limited); instead, we ran **Codex CLI** in a background process.

### Codex outputs produced
Codex generated a set of reproducible scripts and outputs under a temp directory, then we copied them into the OpenClaw workspace.

The core deliverables created were:
- `out/markets_polymarket.csv`
- `out/markets_kalshi.csv`
- `out/agg_by_month.csv`
- `out/agg_by_quarter.csv`
- `out/README.md` (definition, taxonomy, methodology)
- `out/notes_gaps.md` (limitations)
- `scripts/fetch_markets.py` (candidate snapshot fetcher)
- `scripts/build_outputs.py` (initial builder)

### Data notes
- The initial dataset was a **curated slice** of KPI ladders/markets discovered via keyword searching, then normalized into consistent CSVs.
- The repo documents important gaps (e.g., unit mismatch; strike-ladder inflation; historical OI-at-resolution not available in the public snapshot pipeline).

---

## 4) Repo + GitHub Pages publication

### Repo creation
- Created a new public GitHub repo: **`demerzelon/pmresearch`**.
- Added a `docs/` folder with copies of the CSVs and Markdown files so GitHub Pages can serve them.
- Enabled GitHub Pages: source = `main`, path = `/docs`.

### Public URLs
- GitHub repo: https://github.com/demerzelon/pmresearch
- Pages: https://demerzelon.github.io/pmresearch/

---

## 5) Landing page redesign + visualization

Since installing dedicated visualization skills was rate-limited, we improved the Pages landing page directly.

### Implemented (client-side, no build step)
- Updated `docs/index.html` to load data from `docs/*.csv` and render charts.
- Libraries (CDN):
  - **PapaParse** for robust CSV parsing.
  - **Chart.js** for charts.

### Charts added
1. **Volume by quarter**
   - Dual-axis mode to avoid mixing units:
     - Polymarket (left axis)
     - Kalshi (right axis)
   - Toggle modes: dual / Polymarket-only / Kalshi-only
2. **Market count by quarter**
   - Bar chart with series for Combined / Polymarket / Kalshi
3. **Markets by company**
   - Bar chart (counts across both venues)

---

## 6) “Open interest” request (A and C)

Request: add (A) current open interest and (C) open interest at resolution.

### What we could do with public fields
- The original CSV had a combined column: `liquidity/open_interest`.
- We replaced this with explicit columns:
  - `polymarket_liquidity_current` — Polymarket Gamma `liquidity` (best public depth proxy available in this dataset).
  - `open_interest_current` — Kalshi open-interest-like value as present in the snapshot listing used.
  - `open_interest_at_resolution` — added as a column but **left blank** due to missing historical OI time series in the public snapshot pipeline.
  - `asof_utc` — regeneration timestamp.

We also updated `out/README.md` and `docs/README.md` to document these fields.

---

## 7) Coverage audit and missing-market additions

You asked to re-check whether we had *all relevant markets* for the original KPI category.

### Coverage check approach (best-effort)
- We ran additional keyword-based searches against:
  - Polymarket Gamma API (`https://gamma-api.polymarket.com/markets?search=...`)
  - Kalshi public API (`https://api.elections.kalshi.com/trade-api/v2/markets?...`)

### Findings
- We found **3 older Polymarket KPI markets** that matched the KPI+period+“report” pattern and were missing from our CSV.

### Added to the dataset
Added to `out/markets_polymarket.csv` and `docs/markets_polymarket.csv`:
- Tesla deliveries Q2 2021 — id `220931`
- Facebook Monthly Active People (MAP) Q2 2021 — id `221218`
- Spotify premium subscribers Q2 2021 — id `222376`

Then we recomputed `agg_by_month.csv` and `agg_by_quarter.csv` accordingly and pushed updates.

---

## 8) Current state of the repo

### Key files
- Data:
  - `out/markets_polymarket.csv`
  - `out/markets_kalshi.csv`
  - `out/agg_by_month.csv`
  - `out/agg_by_quarter.csv`
- Docs/Pages:
  - `docs/index.html`
  - `docs/*.csv` (copies of the above)
  - `docs/README.md`
  - `docs/notes_gaps.md`
- Repro scripts:
  - `scripts/fetch_markets.py`

### Known limitations (kept intentionally explicit)
- Polymarket: we store Gamma `liquidity` as a “depth-like” proxy; true “open interest” is not represented as a single public field in this dataset.
- Kalshi: to populate **OI at resolution** historically, we likely need a different API endpoint, authenticated access, or our own historical snapshot storage.
- Market discovery: keyword-based searches + curated inclusion are useful but not provably exhaustive; a full-catalog crawl would improve completeness.

---

## 9) Suggested next improvements (optional)

1. **Full-catalog Polymarket crawl** (paginate all markets; filter by KPI+period patterns; diff vs current list).
2. **Kalshi completeness pass**: crawl by series/ticker patterns rather than keyword only.
3. **Open interest at resolution**:
   - Start recording daily OI snapshots going forward; define “OI at resolution” as the last snapshot prior to market close.
4. Add filters to the Pages site (company/KPI/venue/period) and downloadable pre-filtered views.
