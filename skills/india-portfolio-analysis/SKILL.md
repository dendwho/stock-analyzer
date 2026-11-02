---
name: india-portfolio-analysis
description: Evaluate Indian equity portfolio concentration, sector and factor exposures, liquidity, drawdowns, stress scenarios and proposed additions.
---

# Indian Portfolio Analysis

## Shared evidence

Before collecting or interpreting inputs, read
[evidence and freshness](../india-research-core/references/evidence.md) and
[data access](../india-research-core/references/data-access.md). All sibling skills
are distributed with this suite. Load other procedures only when the task needs
them; apply them in the current session without assuming additional agents exist.

1. Obtain holdings/quantities or portfolio weights, cash, price dates, currency,
   known constraints and investment horizon. Ask for risk/capital details only
   when needed for personalized sizing. Identify partial portfolios and cost basis
   gaps; never infer wealth from a holdings excerpt.
2. Normalize all positions to the same dated valuation and verify identities,
   funds/ETF look-through where available, corporate actions and duplicate exposure.
3. Quantify company/sector/group/factor concentration, liquidity and correlated
   economic exposures. Use the bundled `portfolio` helper for weight arithmetic.
4. For returns/correlation/drawdowns use aligned total-return series, sufficient
   common history and documented missing-date policy. Explain benchmark choice,
   price versus total returns and changing weights. No correlation estimates from
   company descriptions alone; no false time-weighted returns from cost basis.
5. Stress market/sector shocks, rate/FX/commodity changes and company-specific
   impairment; distinguish assumed shocks from calibrated models. Assess a proposed
   stock by incremental exposure as well as standalone attractiveness.
6. Present concentration, liquidity and scenario risks with conditional rebalance
   alternatives and costs/tax questions needing current verification. Use trade
   planning only with explicit user risk constraints; execute no orders.

Deliver exposure tables, data scope, stress assumptions and review priorities.
Portfolio “risk %” depends on its definition and is not a maximum possible loss.
