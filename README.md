# Indian Stock Research Skills

A coordinated suite for researching Indian listed companies, sectors, market
conditions, news, IPOs, entries, and portfolios. These are executable assistant
workflows with shared Python calculation and data helpers, not a market-data feed.

## Use it

Open this workspace in your skill-enabled assistant and ask:

- “Analyze Infosys completely. Is it attractive at the current price, for what
  timeframe, and where could I enter?”
- “I like this stock. Find entry zones and assess whether they could be reached
  over the next three months.”
- “Analyze this IPO, including GMP, subscription, valuation, and long-term versus
  listing-day prospects.”
- “Compare ICICI Bank, HDFC Bank, and Axis Bank.”
- “Give me today's Indian market and news roundup.”

`AGENTS.md` routes requests in this workspace. Explicit skill invocation, once
installed in a compatible host, uses `$india-stock-research`, `$india-ipo-analysis`,
or another name in [the catalog](skills-index.json). Natural-language selection
depends on the host; all skills permit automatic discovery.

## Install or package

Python 3.10+ is required for the helpers. Copy the whole suite, retaining sibling
directories. Preview installation without changing files:

```bash
python3 scripts/install.py --dest /path/to/your/skills --dry-run
python3 scripts/install.py --dest /path/to/your/skills
python3 scripts/package.py --output dist/india-stock-research.zip
```

The installer refuses to replace existing skill directories. Use an empty target
or review and remove an older copy yourself. For Codex, an example user-level
destination is `~/.codex/skills`; installation there is a separate local action.
This repository does not write outside the chosen destination or configure an
assistant, broker, scheduler, or paid provider. Restart/reload your host as needed.

## Data and capabilities

The assistant uses its browsing or connected tools to locate current evidence.
Public filings and uploaded documents/CSVs support the basic path. The bundled
collector can cache accessible public HTTPS documents and JSON; it does not bypass
access controls or extract arbitrary PDF tables automatically. See
[data access](skills/india-research-core/references/data-access.md).

Prices, GMP, subscription, ownership, and filings carry their own observation
times. Live feeds, historical point-in-time universes, reliable consensus, and
intraday derivatives data may require a suitable provider. If unavailable, reports
state the limitation and withhold conclusions that depend on missing evidence.

Default stock reports include investment attractiveness, timeframe, scenarios,
entry zones, and reachability. IPO reports always include a GMP section; missing
GMP is not treated as zero. Alerts and watchlist reviews run when invoked; no
background monitoring is configured by installation.

Completed analyses are saved automatically as Markdown in the workspace's
`results/` directory, with a link returned in the response. Filenames include the
subject, report type and IST timestamp; earlier reports are preserved. Complete
stock/IPO reports also get a matching JSON sidecar. You can request a different
directory or a chat-only answer. For example:
`results/infosys_stock-analysis_2026-11-02_173015_123456_IST.md`.
See [saving results](skills/india-research-core/references/saving-results.md).

## Helpers and checks

```bash
python3 skills/india-research-core/scripts/research.py --help
python3 skills/india-research-core/scripts/collect.py --help
python3 scripts/validate.py
python3 -m unittest discover -s tests -v
```

The validation command requires PyYAML (`python3 -m pip install PyYAML`). Runtime
calculation and collection helpers have no third-party Python dependencies.
See [worked examples](examples/README.md) and
[acceptance scenarios](tests/acceptance.md) for reproducible checks and realistic
assistant evaluations. Synthetic examples are explicitly labeled.

The workflows draw on reviewed ideas from TraderMonty's `claude-trading-skills`;
details and retained license terms are in [the attribution](THIRD_PARTY_NOTICES.md).
# stock-analyzer
# stock-analyzer
