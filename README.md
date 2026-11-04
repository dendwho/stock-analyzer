# Indian Stock Research Skills

A coordinated suite for researching Indian listed companies, sectors, market
conditions, news, IPOs, entries, and portfolios. These are executable assistant
workflows with shared Python calculation and data helpers, not a market-data feed.

## What it can do for you

| Need | What you get |
|---|---|
| Complete stock analysis | Business, financials, management, risks and valuation, with a verdict at the cited price, an investment timeframe and an entry plan. |
| IPO analysis | Offer-document review, proceeds, dilution, valuation, subscription, anchors and GMP, with separate long-term ownership and listing assessments. |
| Find potential investments | A shortlist from an available stock dataset using explicit quality, growth, value, dividend or technical filters, with coverage and exclusions stated. |
| Compare companies | Comparisons of profitability, growth, debt, cash generation, valuation and risks across economically relevant peers. |
| Plan entries and position sizes | Valuation and technical entry zones, triggers, invalidation conditions and reachability; position sizing when you provide capital and risk limits. |
| Review your portfolio | Concentration, sector exposure, overlapping risks and the effect of adding a proposed investment, based on your holdings or weights. |
| Check financial red flags | Reviews of cash versus reported profits, receivables, inventory, related-party dealings, promoter pledges and accounting changes. |
| Understand quarterly results | Comparable earnings reviews, explanations of material changes and an assessment of whether the investment thesis has improved or weakened. |
| Technical analysis | Trends, momentum, volume, volatility and support/resistance using available price history. |
| Market, sector and news research | Market and macro context, sector prospects, news roundups and scenarios for how specific events could affect an investment. |
| Futures and options research | Positioning, volatility, strategy payoffs, breakevens and risks when suitable timestamped contract data is available. |
| Test strategies | Historical evaluation of explicit trading rules with stated costs, execution assumptions, benchmarks and limitations. |
| Review watchlists and past decisions | Dated stock and IPO updates, changes since earlier research, upcoming catalysts, thesis records and research postmortems. |

Choose a complete report or a focused question. The available workflows and their
inputs are listed in [the skill catalog](skills-index.json).

## Use it

Open this workspace in your skill-enabled assistant and ask:

- “Analyze Infosys completely. Is it attractive at the current price, for what
  timeframe, and where could I enter?”
- “I like this stock. Find entry zones and assess whether they could be reached
  over the next three months.”
- “Analyze this IPO, including GMP, subscription, valuation, and long-term versus
  listing-day prospects.”
- “Compare ICICI Bank, HDFC Bank, and Axis Bank.”
- “Review my holdings and identify my biggest concentration and sector risks.”
- “Screen this stock dataset for profitable companies with low debt and positive
  operating cash flow, and explain the filters.”
- “Check this company's annual report for accounting and governance red flags.”
- “Review these quarterly results and explain what changed in the investment
  thesis.”
- “Update my watchlist against the previous reports and flag material changes.”
- “Test a moving-average strategy on this price-history CSV, including costs.”
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

Broad screening and historical strategy tests need adequate datasets; a few
researched examples do not establish coverage of the entire market. The bundled
`backtest-sma` helper is a basic single-security, long-only moving-average
demonstration with next-open execution and supplied costs. Broader portfolio or
derivatives backtests require suitable data and an appropriate implementation.

Default stock reports include investment attractiveness, timeframe, scenarios,
entry zones, and reachability. IPO reports always include a GMP section; missing
GMP is not treated as zero. Alerts and watchlist reviews run when invoked; no
background monitoring is configured by installation.

The suite supports research and planning. Broker orders, IPO applications,
external messages, paid subscriptions and scheduled jobs are separate actions
requiring your explicit instruction and suitable tools; they are not configured
by this repository.

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
