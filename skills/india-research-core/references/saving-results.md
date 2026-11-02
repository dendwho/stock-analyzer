# Saving research results

Save every completed analysis, comparison, news roundup, screening report,
portfolio review, entry plan and watchlist review as UTF-8 Markdown in `results/`
relative to the user's active workspace. Create the directory if needed. An
explicit destination or chat-only request takes precedence. Brief clarifications
and status replies do not need separate files.

The saved Markdown is the full researched deliverable, including sources,
timestamps, assumptions, material gaps and limitations, rather than only the
conversational summary. Complete stock reports retain verdict/timeframe/entry
sections; IPO reports retain GMP even when unavailable.

Use a filesystem-safe subject and report type plus an IST creation timestamp:
`infosys_stock-analysis_2026-11-02_173015_123456_IST.md`. Creation time in the name
is separate from the research cutoff and observation times in the content.
Preserve older files. Corrections and updates produce a new report that links
back to the previous one and explains material changes.

The bundled helper accepts an authored Markdown file or stdin. Run from the
user's workspace (the path to the helper may be absolute when installed):

```bash
python3 skills/india-research-core/scripts/save_report.py \
  --subject infosys --kind stock-analysis --input /tmp/research-draft.md
```

For complete stock/IPO research, create and validate the structured record using
`research.py validate-report`, then pass `--sidecar /tmp/research-record.json`.
The helper gives both files the same basename. It saves supplied content, not
generated investment conclusions, and does not replace report validation.
Other report types do not require a JSON sidecar. Use `--output-dir` only for a
user-specified alternative destination.

Return a concise assessment and a clickable “Full analysis” link to the actual
saved `.md` file, using the absolute path returned by the helper.
Do not claim a save succeeded until the write succeeds. If saving
fails, retain the analysis in chat and explain the actual filesystem limitation.

Results can contain portfolio information. Keep them out of skill distribution
archives. The repository ignores result contents in version control and packages
only the skill suite and its explicitly synthetic examples.
