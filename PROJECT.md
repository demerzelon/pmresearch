# Project Documentation — Public-Company KPI Prediction Markets

## Overview
This project gathers information about public-company KPI prediction markets on Polymarket and Kalshi for potential research and analysis.

### Goals
1. Identify and catalog public-company KPI prediction markets on Polymarket and Kalshi.
2. Analyze and aggregate data to quantify the category with respect to volume and market count quarter over quarter.
3. Create a public repository and GitHub Pages for transparent data access.
4. Ensure the data is continually refreshed and expanded to reflect changes and new entries.

## Key Files
- `markets_polymarket.csv`: Detailed market data from Polymarket.
- `markets_kalshi.csv`: Detailed market data from Kalshi.
- `agg_by_month.csv`: Aggregated volume and market count data by month.
- `agg_by_quarter.csv`: Aggregated volume and market count data by quarter.
- `scripts/refresh_q1_2026.py`: Python script to refresh and check for new markets as of Q1 2026.
- `WORKLOG.md`: Detailed work log documenting steps, decisions, and actions taken during the project.

## Methodology
### Data Collection
Data was gathered using public APIs provided by Polymarket Gamma and Kalshi. Specific keywords relating to the companies and KPIs were used to search the available markets.

### Data Cleaning and Analysis
Data was normalized and cleaned to ensure consistent terminology and formats across data sources. Analysis focused on volume, market count, and open interest.

## Results
The project successfully identified categories and potential markets for the mentioned KPIs, capturing relevant data fields such as volume, liquidity, and market changes over time.

## Challenges
1. Rate limits on API access delayed some processes.
2. Integration of all markets was limited due to API constraints, particularly around historical open interest.
3. Expanding searches to cover all relevant KPIs and market changes.

## Future Work
Explore additional data fields and period evaluations to include. Broaden search methodologies and evaluate automated daily polling for data freshness.

## Repository
GitHub: [pmresearch](https://github.com/demerzelon/pmresearch)
GitHub Pages: [Public-Company KPI Prediction Markets](https://demerzelon.github.io/pmresearch/)
