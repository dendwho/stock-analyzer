---
name: india-stock-valuation
description: Value Indian listed companies with sector-appropriate forecasts, DCF, reverse valuation, peers and scenario ranges, including attractiveness at a cited price.
---

# Indian Stock Valuation

## Shared evidence

Before collecting or interpreting inputs, read
[evidence and freshness](../india-research-core/references/evidence.md) and
[data access](../india-research-core/references/data-access.md). All sibling skills
are distributed with this suite. Load other procedures only when the task needs
them; apply them in the current session without assuming additional agents exist.

Read [sector methods](../india-research-core/references/sector-playbooks.md),
[entry methods](../india-research-core/references/entry-methods.md), and
[calculations](../india-research-core/references/calculations.md).

## Workflow

1. Establish price/time, current diluted capital, debt, cash, non-controlling
   interests, investments, leases and current earnings/cash-flow basis. Reconcile
   share/crore units and corporate actions before calculating per-share values.
2. Forecast from revenue drivers, margins, taxes, reinvestment, working capital
   and financing. Label management guidance, outside estimates and own assumptions
   separately; never invent consensus. Reconcile cash flows to the forecast.
3. Choose appropriate methods: FCFF/WACC for suitable non-financial businesses;
   FCFE/residual income/PB-ROE for lenders; embedded-value economics for relevant
   insurers; SOTP/project NAV/cycle-normalized models where appropriate.
4. Show bear/base/bull operating and multiple assumptions, horizon, sensitivity to
   discount/growth/margins and terminal-value contribution. Require discount rate
   above perpetual growth and justify both from current evidence. Reverse DCF
   should solve and show the expectations required by price, using a bounded
   numerical search if needed; disclose model non-uniqueness.
5. Cross-check on economic peers and the company's valuation history. Do not use
   P/E for negative earnings or call a peak-cycle low P/E cheap without normalization.
6. Conclude attractiveness at cited price, justified horizon, scenario returns,
   required-return buy thresholds, uncertainty and what would change the result.
   Provide fair-value ranges rather than a falsely precise single target.

Use the bundled `dcf`, `multiple`, `scenario-return` and `ipo-capitalization`
calculations when relevant. Do not mechanically apply a fixed margin of safety
or assert a target will be achieved by the horizon.
