# Worked examples — synthetic data only

All files here use fictional inputs. They establish calculation behavior and
missing-evidence handling; they are not current market data or recommendations.
`synthetic-prices.csv` is a deterministic 1,000-observation weekday series, ignoring
exchange holidays. It is not any actual security or an Indian trading calendar.

Run commands from the repository root:

```bash
python3 skills/india-research-core/scripts/research.py dcf --input examples/dcf.json
python3 skills/india-research-core/scripts/research.py ipo-capitalization --input examples/ipo-capitalization.json
python3 skills/india-research-core/scripts/research.py gmp --input examples/gmp.json
python3 skills/india-research-core/scripts/research.py position-size --input examples/position-size.json
python3 skills/india-research-core/scripts/research.py indicators --csv examples/synthetic-prices.csv
python3 skills/india-research-core/scripts/research.py reachability --csv examples/synthetic-prices.csv --input examples/reachability.json
python3 skills/india-research-core/scripts/research.py screen --input examples/screen.json
python3 skills/india-research-core/scripts/research.py backtest-sma --csv examples/synthetic-prices.csv --input examples/backtest.json
python3 skills/india-research-core/scripts/research.py validate-report --input examples/stock-report.json
python3 skills/india-research-core/scripts/research.py validate-report --input examples/ipo-report.json
```

Key checks:

- The IPO has 1.2 crore post-issue shares and ₹120 crore market cap. Its one million
  OFS shares add no dilution. Net fresh proceeds are ₹19 crore; after ₹5 crore
  non-debt deployment, net debt becomes minus ₹4 crore. Pro forma EPS is ₹5, P/E 20.
- GMP source A quotes +15%, source B -5% and is stale, and source C is unavailable.
  No averaged quote is produced. These publishers are fictional.
- The position example allows 699 shares after buy fees and the remaining sector
  cap, even though the standalone risk budget would allow more.
- The screen returns only SYNTHETIC-QUALITY; an unknown ROE is excluded explicitly.
- The report examples deliberately withhold recommendations without evidence.

For a real analysis, ask your assistant to use the corresponding skill and gather
the latest evidence. Saved JSON supplements a sourced prose report; a structurally
valid record alone does not constitute complete research.
