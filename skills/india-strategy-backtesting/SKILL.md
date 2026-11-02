---
name: india-strategy-backtesting
description: Evaluate Indian equity trading strategies with point-in-time inputs, explicit timing, corporate-action handling, transaction costs and out-of-sample checks.
---

# Indian Strategy Backtesting

## Shared evidence

Before collecting or interpreting inputs, read
[evidence and freshness](../india-research-core/references/evidence.md) and
[data access](../india-research-core/references/data-access.md). All sibling skills
are distributed with this suite. Load other procedures only when the task needs
them; apply them in the current session without assuming additional agents exist.

Read [calculation conventions](../india-research-core/references/calculations.md).

1. Freeze strategy rules, horizon, universe, dates, rebalancing, sizing, benchmark
   and execution assumptions before examining outcomes. Separate research tuning
   from an untouched evaluation period. Define success and failure criteria.
2. Verify point-in-time financial publication dates, historical constituents,
   delisted securities, survivorship and corporate actions. Explain unavailable
   data. Price-based single-security demonstrations cannot validate a broad screen.
3. Align signal time with the earliest feasible fill; no same-close fill from a
   close-derived signal. Model gaps, spreads, liquidity, lots, partial/unfilled
   orders where material, side-specific costs, turnover and current verified tax/
   fee assumptions. Disclose every simplified fill assumption.
4. Use a suitable reproducible engine. The bundled `backtest-sma` is a bounded
   single-security long-only illustration using next-open execution, volume
   participation, integer lots and supplied side costs. It is not a general
   portfolio/derivatives engine or a total-return backtest on raw prices.
5. Report net and benchmark return on a consistent basis, drawdown, exposure,
   trades, turnover, costs, sensitivity, sample size and out-of-sample performance
   when feasible. Separate open holdings from realized trades and review failures.
6. State selection/tuning bias, missing regime coverage and implementation limits.
   Historical performance does not establish a forward win probability. Archive
   configuration and source hashes so a result can be reproduced.

Deliver a research report with assumptions and limitations. If evidence cannot
support a meaningful backtest, provide a test design and identify missing inputs
rather than inventing an equity curve.
