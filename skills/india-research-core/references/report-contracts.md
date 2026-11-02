# Report contracts

Scale depth to the question. These are required information contracts, not a
requirement to produce a long report for every narrow follow-up. Open with the
answer, timeframe, as-of price and main uncertainty. Cite material claims near
their text, with a source ledger for detailed reports.

## Default delivery and saving

Apply [saving results](saving-results.md) to every completed analysis or report.
Write the full Markdown deliverable in the workspace's `results/` directory and
return its link with a concise answer. Do not wait for a separate save request.
Respect an explicit destination or chat-only preference. Short clarifications
need no report. Preserve earlier results instead of overwriting them.

## Complete stock report

1. **Decision:** permitted verdict from entry methods, current reference price
   and timestamp, investment horizon and why, business-quality assessment,
   valuation attractiveness, entry readiness, evidence confidence, strongest
   counterargument, and critical missing data. Never omit the verdict section.
2. **Business and economics:** segments, geography, customers, competitive
   position, management and capital allocation, sector-specific KPIs.
3. **Financials and quality:** comparable historical/quarterly table, cash flows,
   returns on capital, balance sheet, normalization, forensic flags, governance,
   promoter/ownership changes and material contingencies.
4. **Peers and sector:** justified peer set, comparable metrics, sector cycle,
   valuation history and competitive positioning.
5. **Valuation:** forecasts and sources/assumptions, appropriate methods, fully
   diluted capitalization, conservative/base/upside cases, sensitivities and
   reverse-implied expectations. Include dividends consistently if used.
6. **Market, technicals, news:** benchmark and sector conditions, breadth and
   liquidity where available, price structure and dated indicators, material
   company/sector/macro news, upcoming events and observed reaction.
7. **Entry plan:** zone/trigger/rationale/invalidation/reachability/horizon/source
   table. Even if user did not explicitly ask for entries, include this section.
   If no defensible entry exists, explain why and what would change that. A user
   expressing interest automatically receives the deeper entry assessment.
8. **Risks and monitoring:** downside scenarios, thesis breakers, review dates,
   evidence required to change verdict, source ledger and gaps.

## Complete IPO report

Open with distinct long-term verdict/horizon and listing-speculation assessment.
Include issue identity, latest prospectus version, terms/calendar, capital
structure, business/sector, restated financials, cash quality/governance, proceeds,
litigation/risks, peer valuation and bear/base/bull cases. Include timestamped
subscription by category and **GMP by default**, with nulls and availability
explanation when necessary. Treat pre-listing entry as an issue-price decision;
technical support levels require actual trading history. Close with conditions
for revising the conclusions and sources/pages.

## Market/news report

State trading session, cutoff and search window. Include indices/breadth/sector
leadership/valuation/volatility/flows as available and a ranked event table:
event date, publication date, source, what happened, affected exposures,
transmission mechanism, materiality, observed reaction, horizon, next evidence.
Deduplicate syndicated stories and separate developments from commentary.
No observed reaction is preferable to inventing causality. Include upcoming
official release/results calendar and coverage gaps. Daily and weekly reports
are generated on invocation unless a scheduler has explicitly been configured.

## Comparison / screening / portfolio

Comparisons explain peer selection, metric basis, ranks and tradeoffs. Screens
publish filters, data date, universe and exclusions; candidates are not completed
investment recommendations. Portfolio reports distinguish standalone company
attractiveness from incremental concentration and risk to the user's holdings.

## Structured sidecar

For complete stock/IPO reports, also save a matching JSON record following
`research.schema.json`, with the same conclusions as prose. Use ISO timestamps
with timezone and explicit precision; preserve report revisions instead of
overwriting research history. `python3 scripts/research.py validate-report ...`
checks key semantic fields and source references; it is not a financial audit.
Validate full JSON Schema with a compatible validator if one is already available.
