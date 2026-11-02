---
name: india-derivatives-analysis
description: Analyze Indian futures and options positioning, volatility, contract payoffs and risks using coherent timestamped contract data.
---

# Indian Derivatives Research

## Shared evidence

Before collecting or interpreting inputs, read
[evidence and freshness](../india-research-core/references/evidence.md) and
[data access](../india-research-core/references/data-access.md). All sibling skills
are distributed with this suite. Load other procedures only when the task needs
them; apply them in the current session without assuming additional agents exist.

1. Verify underlying, exchange, expiry, strike, option type, current lot size,
   settlement/exercise method, restrictions and costs from current specifications.
   Require synchronized chain/underlying data and inspect bid/ask depth, volume,
   OI units and delayed flags. Historical chains do not support live entries.
2. Evaluate futures basis/rollover and OI changes with price/volume context.
   Explain competing interpretations; OI/PCR/max pain cannot identify assured
   institutional intent or a pinning price.
3. Evaluate IV term structure/skew, realized volatility and event risk. Greeks
   require stated model assumptions, time, rate/dividends and pricing inputs;
   do not fabricate IV or Greeks from LTP alone.
4. For a requested strategy, show every leg, executable bid/ask assumptions,
   premium and lot units, expiration payoff, breakevens, maximum loss/profit where
   bounded, mark-to-market/assignment/settlement risks, costs and liquidity.
5. Compare stress scenarios including gaps, volatility changes and expiration.
   Unlimited/unbounded risks must remain explicit; a margin figure is not max loss.

Deliver research and conditional alternatives. Do not place orders or imply that
an account integration grants execution authorization. If no usable chain exists,
give a conceptual analysis with the missing inputs identified.
