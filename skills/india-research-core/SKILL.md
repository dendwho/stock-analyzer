---
name: india-research-core
description: Resolve Indian market data, evidence, units, and reusable calculations when supporting the Indian research suite or diagnosing its data inputs.
---

# Indian research core

Use this common foundation when a specialist needs evidence rules, normalized
inputs, calculations, or document collection. The user-facing entry points for
complete reports are the sibling stock and IPO skills.

1. Read [evidence rules](references/evidence.md) and
   [data access](references/data-access.md) before gathering inputs.
2. Load [sector playbooks](references/sector-playbooks.md) only for a relevant
   business; [entry methods](references/entry-methods.md) for entry requests;
   [IPO methods](references/ipo-methods.md) for issues; and
   [report contracts](references/report-contracts.md) for complete deliverables.
3. Use [the calculation interface](references/calculations.md) to avoid
   reimplementing standard calculations. Run `python3 scripts/research.py --help`
   relative to this skill directory. Inspect the required units before execution.
4. For repeatable collection, `scripts/collect.py` caches public HTTPS documents
   with a content hash and retrieval metadata. Browsing and manually supplied
   documents are valid fallbacks. Read the exact filing and relevant PDF pages;
   search snippets are discovery aids, not financial evidence.
5. Maintain a source ledger using the structure in
   [the schema](references/research.schema.json). Source IDs in report claims and
   calculated inputs must resolve to actual documents or provided artifacts.

Capability boundaries: helpers calculate from supplied inputs; they do not
establish data truth, select investments automatically, or supply live feeds.
No execution, application submission, subscription, message, or scheduler is
authorized merely by invoking a research skill.

For every completed deliverable, follow [saving results](references/saving-results.md).
Save Markdown in workspace-local `results/` by default and return its link.
