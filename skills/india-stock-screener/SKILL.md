---
name: india-stock-screener
description: Screen Indian equities for quality, value, growth, dividends, turnaround or technical setups using explicit filters, universe and data dates.
---

# Indian Stock Screening

## Shared evidence

Before collecting or interpreting inputs, read
[evidence and freshness](../india-research-core/references/evidence.md) and
[data access](../india-research-core/references/data-access.md). All sibling skills
are distributed with this suite. Load other procedures only when the task needs
them; apply them in the current session without assuming additional agents exist.

1. Translate the request into measurable filters and a declared exchange/security
   universe. Explain thresholds, market cap/liquidity minimums and exclusions.
   If the user is broad, choose stated provisional criteria rather than silently
   optimize until desirable names appear.
2. Verify dataset coverage, as-of dates, consolidation, corporate actions and
   available financial/technical fields. Current snapshots cannot support historical
   point-in-time screening. No invented universe-wide search from a few examples.
3. Use sector-specific definitions and separate banks/insurers when general debt,
   FCF or ROCE filters do not apply. Missing metrics are unknown, not zeros.
4. Apply filters reproducibly to available exports/connected screener data; record
   names excluded for missing/stale fields and survivorship limitations. For small
   provided datasets, use the bundled `screen` helper with explicit numeric rules.
5. Rank on stated criteria and explain tradeoffs, governance/liquidity flags and
   what deeper research is needed. For dividends distinguish recurring capacity
   from temporary high yield; for turnarounds require evidence of change.

Deliver filter specification, universe/coverage, candidate table, exclusions and
next research steps. A screen is a shortlist; use `india-stock-research` before
making a current-price investment conclusion.
