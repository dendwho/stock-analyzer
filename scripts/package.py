#!/usr/bin/env python3
"""Build a deterministic suite ZIP excluding research, caches and credentials."""
import argparse
from pathlib import Path
import sys
import zipfile

ROOT = Path(__file__).resolve().parents[1]


def package(output):
    output = Path(output)
    if output.exists():
        raise ValueError('output already exists; choose a new archive name')
    files = [ROOT / name for name in ('README.md', 'AGENTS.md', 'THIRD_PARTY_NOTICES.md', 'skills-index.json', 'workflows.json')]
    for directory in ('skills', 'scripts', 'examples', 'tests'):
        files.extend(path for path in (ROOT / directory).rglob('*')
                     if path.is_file() and '__pycache__' not in path.parts and path.suffix != '.pyc')
    output.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(output, 'x', compression=zipfile.ZIP_DEFLATED) as archive:
        for path in sorted(set(files)):
            if path.is_symlink():
                raise ValueError(f'packaging symlinks is unsupported: {path}')
            info = zipfile.ZipInfo(path.relative_to(ROOT).as_posix(), date_time=(2026, 1, 1, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o100644 << 16
            archive.writestr(info, path.read_bytes())
    return output


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', required=True)
    args = parser.parse_args()
    try:
        print(package(args.output))
    except (ValueError, OSError) as exc:
        print(f'Packaging stopped: {exc}', file=sys.stderr)
        sys.exit(2)
