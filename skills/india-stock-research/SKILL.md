---
name: india-stock-research
description: Produce a complete Indian listed-company investment report with a current-price verdict, timeframe, valuation, entries and reachability; also handle interest in a stock and where to enter.
---

# Indian Stock Research

## Shared evidence

Before collecting or interpreting inputs, read
[evidence and freshness](../india-research-core/references/evidence.md) and
[data access](../india-research-core/references/data-access.md). All sibling skills
are distributed with this suite. Load other procedures only when the task needs
them; apply them in the current session without assuming additional agents exist.

Turn a company question into an evidence-backed investment decision. Read the
[report contract](../india-research-core/references/report-contracts.md),
[entry methods](../india-research-core/references/entry-methods.md), and relevant
[sector playbook](../india-research-core/references/sector-playbooks.md).

## Workflow

1. Resolve issuer/security and research cutoff. Use the user's investment horizon;
   otherwise disclose a provisional 3–5 year ownership horizon and 1–3 month entry
   window. Ask only if identity or a genuinely necessary constraint is unresolved.
2. Gather latest filed financials, annual report/notes, results and calls,
   ownership/pledges, material announcements, price history, sector/market evidence,
   and material news. Reuse verified cached inputs, refreshing time-sensitive ones.
3. Read and apply sibling `india-fundamental-analysis`, `india-forensic-analysis`,
   `india-earnings-analysis`, `india-peer-comparison`, and `india-sector-analysis`
   SKILL.md files to their actual inputs. Use their procedures within this run;
   no separate agent or proprietary tool is required.
4. Apply `india-stock-valuation` to explicit forecasts and reconcile capital units.
   Apply `india-macro-analysis`, `india-market-analysis`, `india-technical-analysis`,
   and the news skills to the exposures that materially affect this company. Skip
   unrelated detail with a reason; missing critical inputs remain visible.
5. Synthesize business quality, sustainable earnings, governance, valuation,
   catalysts and market conditions. State whether it is attractive at the cited
   price: attractive-now, attractive-below, watchlist, avoid, or insufficient-evidence.
   Justify the timeframe and give sourced bear/base/bull assumptions and downside.
6. Always apply `india-trade-planning` and entry methods to provide entry zones,
   current-price distance, triggers/invalidation, and conditional reachability.
   A user saying “I like it” triggers the deeper plan automatically. Quantities
   require capital/risk/exposure inputs; an investment verdict does not.
7. Review contrary evidence, scenario consistency, freshness and missing data.
   Deliver the full stock contract; save the Markdown report and matching JSON
   sidecar in workspace-local `results/` by default and return the Markdown link.

If price is stale/unverified, withhold a current-price verdict and give conditional
valuation thresholds. If only technicals are available, do not imply complete
fundamental research. For an unlisted IPO, use `india-ipo-analysis` instead.

## Follow-ups

Reuse the source ledger for peer comparisons or sensitivity questions, refresh
affected evidence, and show what changed. On a request to save/track, use
`india-research-journal` or `india-watchlist-monitor`; invocation alone starts no
background job.
