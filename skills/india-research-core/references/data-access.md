# Data access and fallback

Use available browsing/connected tools first. Prefer original documents to
unofficial endpoints. The URLs in `sources.json` are discovery pages, not promises
of stable programmatic APIs. Select the actual document before caching it.

| Need | Starting point | Fallback |
|---|---|---|
| Statements, announcements, shareholding, actions | NSE/BSE corporate filings and issuer IR | User-supplied filing or exchange download |
| IPO offer documents and amendments | SEBI public issues, exchanges, issuer/lead manager | Uploaded RHP/DRHP, explicitly versioned |
| Issue details and subscription | Exchange issue page, final offer, registrar | Timestamped downloaded issue data |
| Prices, volumes, delivery, deals, VIX | Exchange historical/daily reports | Documented provider export or CSV |
| Index returns, valuation, constituents | NSE Indices reports and methodology | Dated factsheet/export |
| Macro and monetary policy | RBI/DBIE, MoSPI, government releases | Original release downloaded by user |
| Flows | Exchange, NSDL/CDSL/AMFI disclosures as applicable | Dated official table/export |
| Company events | Original filing and issuer release; accessible reporting | Supplied document with provenance |
| GMP | Publisher quote, e.g. Investorgain/IPO Premium/Chittorgarh | Attributed screenshot with time, or unavailable |

NSE quote feeds, broker integrations, screener exports, consensus, and paid
historical data are optional capabilities. Inspect current documentation, coverage,
permissions, and terms before choosing an integration. A registered broker key
does not imply permission to place orders. Do not claim an unimplemented adapter.

## Collection helper

```bash
python3 skills/india-research-core/scripts/collect.py \
  --url 'https://www.sebi.gov.in/filings/public-issues.html' \
  --source-id sebi-issues --output-dir data/sources --max-age-hours 6
```

The helper stores bytes and a metadata sidecar keyed by URL hash. It preserves
the original retrieval time when using the cache. It sets publication/observation
times to unknown, to be established from content. A successful HTTP request is
not evidence that a JavaScript table has populated or the right document was
returned. Review content type, content, and issuer identity. The collector accepts
only public HTTPS destinations and checks redirects; it does not send credentials.

One normal request with a bounded timeout is sufficient. If access is blocked,
rate limited, paywalled, unavailable, or content is an anti-bot page, use another
authorized source or a supplied download. Do not bypass a CAPTCHA or access
control. Record failures and affected coverage. PDF table extraction requires
available PDF tools or direct visual inspection; manually reconcile totals.

## Normalized inputs

OHLCV CSV: ascending unique `date` (ISO YYYY-MM-DD), `open,high,low,close,volume`.
Use consistent raw or adjusted OHLC; specify `price_basis`. Splits/bonuses and
dividends need explicit treatment. Volume adjustment must also be documented.
Use the CSV normalizer with an explicit column mapping for provider exports;
it never guesses units, exchange timestamps, or adjustment methods.

Financial records: metric, value, currency, unit, period_start/end, annual/quarter,
consolidated/standalone, reported/restated, and source IDs. Do not infer missing
cash flows from earnings. Portfolio values use the same price date and currency.

Save completed Markdown reports under workspace-local `results/` by default,
following [saving results](saving-results.md), or a user-specified directory.
Preserve old reports
and ledger entries. No account credentials, holdings, or user documents belong in
the distributable skill package. Refresh only inputs needed for the question.
