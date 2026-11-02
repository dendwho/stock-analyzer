---
name: india-ipo-analysis
description: Research Indian mainboard and SME IPOs with prospectus due diligence, valuation, subscription and GMP included by default, plus separate long-term and listing assessments.
---

# Indian IPO Analysis

## Shared evidence

Before collecting or interpreting inputs, read
[evidence and freshness](../india-research-core/references/evidence.md) and
[data access](../india-research-core/references/data-access.md). All sibling skills
are distributed with this suite. Load other procedures only when the task needs
them; apply them in the current session without assuming additional agents exist.

Always read [IPO methods](../india-research-core/references/ipo-methods.md),
[report contracts](../india-research-core/references/report-contracts.md), and the
relevant [sector playbook](../india-research-core/references/sector-playbooks.md).

## Workflow

1. Resolve issuer, platform, issue status/cutoff and latest applicable RHP/final
   offer plus amendments. DRHP-only analysis is preliminary. Record direct links
   and document pages for material disclosures.
2. Reconcile issue terms, price band, calendar, categories, lot, fresh issue/OFS,
   selling holders, post-issue dilution, expenses, net proceeds, uses and lock-ins.
3. Apply fundamental/forensic/sector/peer procedures to restated annual and interim
   accounts, concentration, governance, litigation, management and issue risks.
4. Calculate post-issue valuation at applicable prices with diluted shares and
   proceeds treatment; compare economic peers and construct bear/base/bull cases.
5. Obtain timestamped category subscriptions and anchors, explaining denominators
   and provisional/final status. Do not sum overlapping exchange data.
6. **Fetch and report GMP without waiting for the user to request it.** Seek two
   attributable sources where available. Show ₹, %, selected price basis,
   observation/retrieval dates, freshness/history and conflicts. Use the `gmp`
   helper for arithmetic. Missing/undated/stale quotes stay visible; unavailable
   is not zero. Preserve negative GMP and keep it out of fundamental valuation.
7. Give separate long-term ownership verdict/timeframe and listing-speculation
   assessment, supported by valuation, risks, demand quality and market conditions.
   SME issues require specific liquidity, concentration and trading-rule review.
8. Deliver the complete IPO contract, including a GMP section even if unavailable.
   Entry before listing is the issue-price decision; after listing route actual
   trading levels to stock research. Save the Markdown report and matching JSON
   sidecar in workspace-local `results/` by default and return the Markdown link.

Do not equate SEBI filing, oversubscription or positive GMP with investment merit.
Do not submit an application or claim certain allotment/listing gains.
