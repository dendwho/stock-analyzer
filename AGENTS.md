# Indian market research workspace

This repository contains an India-focused research skill suite. For a complete stock
request, open `skills/india-stock-research/SKILL.md`; for an IPO, open
`skills/india-ipo-analysis/SKILL.md`. For narrower requests, select the matching skill
from `skills-index.json`. Follow that skill's linked shared references. These paths
also support use directly from this workspace without global installation.

Every complete stock report must answer whether the investment is attractive **at
the cited price**, provide a justified timeframe, and assess entry zones and their
reachability. Every IPO report must include GMP by default, even when the result
is explicitly unavailable. Respect source timestamps and distinguish facts,
calculations, assumptions, and interpretation. Never fill gaps with invented data.

Save every completed analysis, comparison, roundup, screen and review as Markdown
in the workspace's `results/` directory by default. Use the shared
`skills/india-research-core/references/saving-results.md` procedure. Preserve prior
files and return a clickable link to the saved report. Save complete stock/IPO
JSON sidecars alongside the Markdown. Honor a user-specified destination or
explicit chat-only request. Brief clarifications do not need separate reports.

The suite is for research and planning. Broker execution, IPO applications,
external messages, paid subscriptions, and scheduled jobs are separate actions
requiring the user's instruction. Do not claim monitoring is running unless it is.

Keep common methods in `skills/india-research-core`; specialist skills link there.
All skills must be distributed together so these relative links remain valid.
Do not introduce requirements for specific proprietary services when files or
public documents suffice. Preserve attribution in `THIRD_PARTY_NOTICES.md`.

Run `python3 scripts/validate.py` and
`python3 -m unittest discover -s tests -v` after substantive changes. Python helper
scripts use the standard library. Skill validation requires PyYAML only.
