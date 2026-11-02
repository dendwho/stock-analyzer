---
name: india-trade-planning
description: Find valuation-aware stock entry zones, assess whether they could be reached in current market conditions, and size conditional plans when risk inputs are provided.
---

# Indian Entry and Trade Planning

## Shared evidence

Before collecting or interpreting inputs, read
[evidence and freshness](../india-research-core/references/evidence.md) and
[data access](../india-research-core/references/data-access.md). All sibling skills
are distributed with this suite. Load other procedures only when the task needs
them; apply them in the current session without assuming additional agents exist.

Always read [entry methods](../india-research-core/references/entry-methods.md)
and [calculations](../india-research-core/references/calculations.md).

1. Establish ownership versus tactical trade, investment horizon, entry window,
   verified price/time, valuation conclusions, numerical history, relevant
   market/sector conditions and upcoming events. Missing valuation means a technical
   plan only; missing price means conditional levels without a current entry call.
2. Derive applicable value/pullback/current/breakout alternatives. Include rationale,
   zone edges, confirmation, invalidation, distance, timing and expected scenario
   payoff. Do not invent a level just to fill a table or chase a missed entry.
3. Evaluate reachability using ATR-distance, drawdowns, historical excursions,
   breadth/sector/volatility, catalysts and liquidity. Use `reachability` helper
   when sufficient consistent OHLCV exists. Historical touch shares are descriptive,
   not probabilities; give sample/window/regime limitations and the change required
   for a deeper zone. State insufficient evidence when inputs are missing.
4. Separate “could reach entry” from “attractive after entry.” Compare prospective
   business returns and plausible downside for the specified horizon. Provide
   wait/no-valid-entry when expected reward is inadequate.
5. Quantities require account capital, explicit risk budget, cash budget, position
   and sector caps/current exposure, fees/slippage and lot. Use `position-size`;
   never invent a personalized risk tolerance. Staging must respect aggregate
   risk/exposure across all tranches and existing holdings.
6. Define thesis/technical invalidation distinctly, event review points and what
   would change the plan. Explain gaps/illiquidity can exceed modeled stop losses.

Deliver a conditional entry table with timeframe and reachability conclusion;
size only if inputs permit. A liked company still needs a price-sensitive verdict.
No broker execution or guaranteed fills are part of this workflow.
