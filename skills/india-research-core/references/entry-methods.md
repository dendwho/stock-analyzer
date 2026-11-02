# Investment verdict, entry zones, and reachability

## Verdict and horizon

Answer whether the security is attractive at the cited price. Allowed verdicts:
`attractive-now`, `attractive-below`, `watchlist`, `avoid`, `insufficient-evidence`.
Support the verdict with business economics, valuation, balance-sheet/governance
risk, catalysts, and market context; explain the strongest contrary case. A user
liking a company is a reason to investigate entries, not evidence of attractiveness.

Use the user's horizon. If unspecified, adopt a stated provisional 3–5 year
business-ownership horizon, adjusting it when the thesis has a different economic
duration; separately assess entry reachability over 1–3 months. Short trades need
their own catalyst/price thesis and days/weeks horizon. Never present a technical
trade as a long-term valuation conclusion. Explain why earnings development,
capacity ramp, cycle normalization, or a catalyst could take the stated time.

Build bear/base/bull outcomes with explicit earnings/cash-flow and valuation
assumptions, dates or horizon, dividend treatment, and price/total-return basis.
Show downside as prominently as upside. Annualize multi-year scenario returns
when useful. Do not label discretionary scenario weights as statistical
probabilities. No target is guaranteed to occur or mature on schedule.

## Entry construction

1. Establish identity, current price/as-of, liquidity, upcoming results/events,
   corporate actions, current market/sector state, and usable OHLCV history.
2. Derive a fundamental buy range from conservative fair values, required return,
   and an explicitly justified margin of safety. Reverse-DCF assumptions help
   expose what the current price already requires. No universal fixed discount.
3. Find relevant weekly/daily structure: repeated support/resistance zones, prior
   bases and gaps, volume confirmation, trend and relative strength. Moving
   averages are context, not automatic buy signals. Numerical indicators require
   numerical data; chart-only levels are approximate and labeled as such.
4. Reconcile valuation with technical structure. Label a support zone that is
   still expensive as a tactical level, not a value entry. Do not force overlap.
5. Return only applicable alternatives: initial entry now, pullback accumulation,
   deeper value, breakout after confirmation, or wait/no valid entry. Each row
   needs a price zone, rationale, trigger, invalidation, distance from price,
   reachability horizon and assessment, catalyst sensitivity, and evidence IDs.
6. Staged allocation is optional and depends on risk budget and existing exposure.
   Without portfolio information, describe conditions and omit personalized
   quantities. For long-term ownership, distinguish thesis invalidation from a
   trading stop. A stop cannot cap gap or illiquidity losses.

## Reachability

Assess whether the *entry zone could be visited*, separately from whether an
investment would succeed afterwards. Compute current distance to both edges,
distance/ATR when available, realized volatility, typical pullbacks, drawdown,
and historical excursions over the chosen number of sessions. Put those in
current breadth, sector momentum, market valuation, flows, event, and liquidity
context. If market evidence is missing, state this dependency; don't manufacture
a current-regime conclusion.

The `reachability` helper summarizes backward-looking high/low excursions from
historical closes, optionally using nonoverlapping windows. Its touch share is a
sample description, never a forward probability. Daily OHLC cannot establish
intraday ordering or that a quoted level was fillable. Report sample size, period,
window length, overlap, adjustments, and regime mismatch. Exclude windows not
fully observed as of the cutoff. At least 20 complete windows are a useful
diagnostic floor, not proof of calibration. Do not invent a probability from ATR.

Use reasoned labels:

- **Plausible in an ordinary pullback:** supported by observed excursions and
  current conditions; explain what could prevent it.
- **Needs a broader correction or catalyst:** ordinary variation offers limited
  support; identify the required change.
- **Requires breakout confirmation:** a conditional upward entry, not a forecast.
- **Insufficient evidence:** missing history, stale price, incompatible adjusted
  series, or unusable market context.

Avoid “will reach,” false precision, and uncalibrated odds. A zone can be
reachable and a poor investment, or attractive and unlikely to be visited soon.

## Exit and review

Set review points around results/catalysts and thesis changes. Explain whether a
price rise has consumed the margin of safety. Define what evidence would justify
holding, reducing, waiting, or redoing research. Do not convert a missed entry
into a higher buy price without revisiting prospective returns.
