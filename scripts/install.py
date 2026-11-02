#!/usr/bin/env python3
"""Install the complete sibling skill suite into an explicitly chosen destination."""
import argparse
import json
from pathlib import Path
import shutil
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]


def install(destination, dry_run=False):
    destination = Path(destination).expanduser().resolve()
    catalog = json.loads((ROOT / 'skills-index.json').read_text())['skills']
    names = [entry['id'] for entry in catalog]
    if destination == (ROOT / 'skills').resolve() or (ROOT / 'skills').resolve() in destination.parents:
        raise ValueError('choose an installation destination outside the source skills directory')
    for name in names:
        if not (ROOT / 'skills' / name / 'SKILL.md').is_file():
            raise ValueError(f'incomplete source suite: {name}')
        if (destination / name).exists() or (destination / name).is_symlink():
            raise ValueError(f'refusing to replace existing skill: {destination / name}')
    if dry_run:
        return {'dry_run': True, 'destination': str(destination), 'skills': names}
    destination.mkdir(parents=True, exist_ok=True)
    # Stage and verify the complete copy before moving any skill into discovery.
    with tempfile.TemporaryDirectory(prefix='.india-skills-', dir=destination) as staging:
        for name in names:
            shutil.copytree(ROOT / 'skills' / name, Path(staging) / name,
                            ignore=shutil.ignore_patterns('__pycache__', '*.pyc'))
        moved = []
        try:
            for name in names:
                target = destination / name
                # Recheck in case another process installed while staging.
                if target.exists() or target.is_symlink():
                    raise ValueError(f'installation target appeared: {target}')
                (Path(staging) / name).rename(target)
                moved.append(target)
        except Exception:
            for target in moved:
                shutil.rmtree(target)
            raise
    notice = ROOT / 'THIRD_PARTY_NOTICES.md'
    # Preserve attribution within the installed skill set as well as the archive.
    shutil.copyfile(notice, destination / 'india-research-core' / 'THIRD_PARTY_NOTICES.md')
    return {'installed': len(names), 'destination': str(destination),
            'next': 'Reload your skill host; see india-stock-research and india-ipo-analysis'}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--dest', required=True)
    parser.add_argument('--dry-run', action='store_true')
    args = parser.parse_args()
    try:
        print(json.dumps(install(args.dest, args.dry_run), indent=2))
        return 0
    except (ValueError, OSError) as exc:
        print(f'Installation stopped: {exc}', file=sys.stderr)
        return 2


if __name__ == '__main__':
    raise SystemExit(main())
