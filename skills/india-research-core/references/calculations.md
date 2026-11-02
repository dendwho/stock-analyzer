# Calculation interface

Python 3.10+, standard library only. All operations except `normalize-csv` return
JSON; invalid inputs return exit 2. Output files use exclusive creation so prior
research is not overwritten. Use explicit timezone-bearing ISO timestamps.

```bash
python3 skills/india-research-core/scripts/research.py OPERATION --input inputs.json
python3 skills/india-research-core/scripts/research.py indicators --csv prices.csv
python3 skills/india-research-core/scripts/research.py reachability --csv prices.csv --input zone.json
```

Rates/fractions are decimals (`0.12` = 12%). Basis points are literal bps (`10` =
0.10%). Prices are ₹/share. Do not feed percentage points where fractions are used.
The helpers do not verify sources, adjustments, data freshness, assumptions or
appropriateness of a model; attach the source ledger and interpret the results.

## Valuation

`dcf`: JSON fields `fcff_crore` (nonempty annual forecast array), `wacc`,
`terminal_growth`, `shares_crore`, optionally `net_debt_crore`, `nci_crore`,
`nonoperating_assets_crore`. Forecasts are annual end-period FCFF; the terminal
base must be positive, WACC positive and above perpetual growth. Net cash is
negative net debt. The bridge subtracts NCI and adds nonoperating assets, avoiding
double counting assets already included in forecast cash flows. Fair value is
₹/share because both totals and shares use crore. No mid-year convention or
automatic forecast generation.

`multiple`: `kind` (`pe` or `ev-ebitda`), positive `metric_crore`, `multiple`,
`shares_crore`; EV mode also accepts the same debt/NCI/assets bridge. For P/E use
attributable normalized PAT; for EV use consistent EBITDA/leases. Invalid negative
earnings are rejected rather than yielding a meaningful-looking P/E.

`scenario-return`: `entry_price`, `exit_price` (zero allowed), `years`, optional
`cash_dividends` (cumulative, no reinvestment). Gross annualized terminal wealth
is not dividend-timed IRR and excludes fees/taxes.

## IPO and GMP

`ipo-capitalization`: `issue_price`, integer `pre_shares`, exactly one of integer
`fresh_shares` or `fresh_amount_rupees`, `attributable_pat_rupees`; optional
`additional_dilution_shares`, `ofs_shares`, `issuer_expenses_rupees`,
`pre_net_debt_rupees`, `non_debt_deployment_rupees`.
Shares are actual share counts, monetary fields ₹ (not crore). With fixed fresh
amount, shares are floored and unused budget is shown; reconcile actual counts
with the final offer. OFS adds no shares. Net debt after proceeds is pre-net-debt
minus net fresh proceeds plus non-debt deployment. Repaying debt from proceeds
does not require adding debt repayment back. Additional dilution assumes no cash
inflow; model any exercise proceeds explicitly outside the helper. PAT <= 0 gives
null P/E. This simplified EV bridge excludes NCI/nonoperating assets; add/reconcile
them explicitly in the research if relevant.

`gmp`: `issue_price`, explicit `price_basis` (e.g. upper band illustration),
`as_of`, optional `max_age_hours` (default 24), `quotes` array. Each quote:
`source`, optional `url`, `premium_rupees` (null means unavailable), `observed_at`
with timezone and `time_precision: timestamp`, or date-only `observed_at` with
`time_precision: date`. Unknown observation can be null. Quotes preserve source
fields and disagreement. Date-only observations are unverified intraday and must
use the same local calendar basis as `as_of`; normalize research cutoffs to IST
for Indian date-only quotes. The age limit is a diagnostic, not proof of market
freshness. Every quoted value needs source inspection for a newer update.

## Prices and reachability

`normalize-csv`: `--csv provider.csv --input mapping.json --output prices.csv`.
Mapping JSON: `{"column_mapping":{"date":"Date","open":"Open",...}}` for all
six canonical columns. Dates must already be ISO and values unformatted numeric;
normalize vendor-specific formats explicitly after checking their meaning.
No sorting/deduplication or adjustment is silently performed.

`indicators`: `--csv prices.csv`. Computes 20/50/200 SMA, 20 EMA, 14-period Wilder
RSI/ATR, 12/26/9 MACD, 20-period 2-population-SD Bollinger bands, log-return
volatility annualized at 252 sessions, volume ratio to prior 20 sessions, and
close-based maximum drawdown. EMA is SMA-seeded; ATR starts from changes after
the first bar. Insufficient history yields null, not a fabricated value; seed
effects need longer warm-up history. No automatic support-zone selection.

`reachability`: prices plus JSON `zone_low`, `zone_high`, `horizon_sessions`,
optional `nonoverlapping` (default true). Compares the current zone's relative
distance with fully observed subsequent daily ranges at historical starting
closes. Gives range-intersection share, complete sample size and excursion
percentiles, distance/ATR and history period. It never returns a forward
probability, guaranteed fill, or current-market conclusion. Use
[entry methods](entry-methods.md) for interpretation.

## Risk, screens and portfolio

`position-size`: `account_equity`, `entry`, `stop`, explicit `risk_fraction`,
`available_cash`, `max_position_fraction`; optional `lot_size` (default 1),
`round_trip_cost_bps`, `buy_cost_bps`, `adverse_slippage_per_share`,
`current_position_value`, `existing_planned_risk`; sector constraints require both
`max_sector_fraction` and `current_sector_value`.
All values ₹ except fractions/lot/bps. Round-trip risk costs include buy costs;
`buy_cost_bps` is also used separately for cash affordability. Position/sector caps
apply to notional; cash includes buy fees. Quantity is constrained by risk/cash/
exposure and rounded down to lots. Zero quantity is valid. Existing planned risk
allows aggregate tranche risk but does not model correlated gap losses.

`portfolio`: `holdings` array of unique `id`, `value` (common-date market ₹), optional
`sector`, plus optional `cash`. Calculates weights, sector aggregates and single-
name HHI on total portfolio. Unknown sector is retained. No return/correlation model.

`screen`: `rows` array of objects with unique `id` and numeric metrics; `rules`
array of `field`, `op` (`gt/gte/lt/lte`), `value`. Missing/null fields are excluded
as unknown and reported separately. No implicit ranking or live universe lookup.

## Backtest demonstration

`backtest-sma`: CSV plus `fast`, `slow`, `initial_cash`, `buy_cost_bps`,
`sell_cost_bps`, `slippage_bps`, `max_volume_fraction`; optional `lot_size`.
Fast must be below slow; first signal follows slow-period warmup and can fill only
at next open. Fully long when fast SMA > slow, otherwise cash. Integer lots,
side costs, adverse slippage and ex-post volume cap are applied. Partial entries
are not topped up; exits can span sessions while sell signal persists. This is
a documented toy engine for process validation, not a universal backtester.

Returns use final marked equity without forced liquidation; benchmark is a
costed/lot/volume-constrained one-shot buy-and-hold from the first executable open,
also marked without exit cost. Raw prices exclude dividends and require split
handling before use. Consistently adjusted OHLC needs compatible units/volumes
and should be labeled a modeled price-basis test. The engine cannot validate
opening liquidity, circuit-limit fills, historical universe bias or PIT financials.

## Saved-report validation

`validate-report`: JSON record matching `research.schema.json`. Checks required
verdict/timeframe/confidence, reference-price restrictions, source resolution,
entry fields and mandatory IPO GMP/listing conclusions. Full schema validation
is separate. Passing these structural/semantic checks does not verify research
truth or investment merit.
