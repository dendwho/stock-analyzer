#!/usr/bin/env python3
"""Save authored Markdown reports and optional JSON sidecars without replacing history."""
import argparse
from datetime import datetime, timedelta, timezone
import json
from pathlib import Path
import re
import sys
import unicodedata

IST = timezone(timedelta(hours=5, minutes=30))


def slug(value):
    value = unicodedata.normalize('NFKD', value).encode('ascii', 'ignore').decode()
    value = re.sub(r'[^a-z0-9]+', '-', value.lower()).strip('-')[:80].rstrip('-')
    if not value:
        raise ValueError('subject and kind need at least one letter or number')
    return value


def save_report(markdown, subject, kind, output_dir='results', sidecar=None):
    if not isinstance(markdown, str) or not markdown.strip():
        raise ValueError('Markdown report must not be empty')
    if sidecar is not None and not isinstance(sidecar, dict):
        raise ValueError('JSON sidecar must be an object')
    # Render before opening anything, so invalid JSON cannot leave half a report.
    rendered = json.dumps(sidecar, indent=2, ensure_ascii=False, allow_nan=False) + '\n' if sidecar is not None else None
    stem = f'{slug(subject)}_{slug(kind)}_{datetime.now(IST).strftime("%Y-%m-%d_%H%M%S_%f_IST")}'
    root = Path(output_dir).expanduser().resolve()
    root.mkdir(parents=True, exist_ok=True)
    for revision in range(1, 1001):
        name = stem if revision == 1 else f'{stem}_{revision}'
        md_path, json_path = root / f'{name}.md', root / f'{name}.json'
        if md_path.exists() or json_path.exists():
            continue
        created = []
        try:
            with md_path.open('x', encoding='utf-8') as handle:
                created.append(md_path)
                handle.write(markdown.rstrip() + '\n')
            if rendered is not None:
                with json_path.open('x', encoding='utf-8') as handle:
                    created.append(json_path)
                    handle.write(rendered)
        except FileExistsError:
            for path in created:
                path.unlink()
            continue
        except OSError:
            for path in created:
                path.unlink()
            raise
        return {'markdown': str(md_path), 'sidecar': str(json_path) if rendered is not None else None}
    raise ValueError('could not allocate a unique report filename')


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--subject', required=True)
    parser.add_argument('--kind', required=True, help='For example stock-analysis, ipo-analysis, market-roundup')
    parser.add_argument('--input', required=True, help='Authored Markdown file, or - for stdin')
    parser.add_argument('--output-dir', default='results', help='Relative to current workspace; defaults to results/')
    parser.add_argument('--sidecar', help='Optional prevalidated JSON record file')
    args = parser.parse_args(argv)
    try:
        content = sys.stdin.read() if args.input == '-' else Path(args.input).read_text(encoding='utf-8')
        sidecar = json.loads(Path(args.sidecar).read_text(encoding='utf-8')) if args.sidecar else None
        print(json.dumps(save_report(content, args.subject, args.kind, args.output_dir, sidecar), indent=2))
        return 0
    except (OSError, ValueError) as exc:
        print(f'Report was not saved: {exc}', file=sys.stderr)
        return 2


if __name__ == '__main__':
    raise SystemExit(main())
