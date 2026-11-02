#!/usr/bin/env python3
"""Validate skill discovery, shared references, workflows and example reports."""
import json
from pathlib import Path
import re
import sys

try:
    import yaml
except ImportError:
    sys.exit('Skill validation requires PyYAML: python3 -m pip install PyYAML')

ROOT = Path(__file__).resolve().parents[1]


def validate(root=ROOT):
    errors = []
    index = json.loads((root / 'skills-index.json').read_text())
    entries = index['skills']
    names = {item['id'] for item in entries}
    if len(names) != len(entries):
        errors.append('duplicate catalog IDs')
    actual = {p.name for p in (root / 'skills').iterdir() if p.is_dir()}
    if actual != names:
        errors.append(f'catalog/directory mismatch: {actual ^ names}')
    for item in entries:
        path = root / item['path']
        text = path.read_text()
        if not text.startswith('---\n') or '\n---\n' not in text[4:]:
            errors.append(f'{path}: missing frontmatter')
            continue
        metadata = yaml.safe_load(text.split('---', 2)[1])
        if metadata.get('name') != item['id'] or not re.fullmatch(r'[a-z0-9-]{1,63}', item['id']):
            errors.append(f'{path}: invalid name')
        if not isinstance(metadata.get('description'), str) or not metadata['description'].strip():
            errors.append(f'{path}: missing description')
        if 'TODO' in text or '[TODO' in text:
            errors.append(f'{path}: unfinished scaffold')
        if not set(item['requires']) <= names:
            errors.append(f'{path}: missing dependency')
        ui = yaml.safe_load((path.parent / 'agents/openai.yaml').read_text())
        interface = ui['interface']
        if not 25 <= len(interface['short_description']) <= 64:
            errors.append(f'{path}: UI subtitle length')
        if f'${item["id"]}' not in interface['default_prompt']:
            errors.append(f'{path}: UI prompt does not invoke skill')
        if ui.get('policy', {}).get('allow_implicit_invocation') is False:
            errors.append(f'{path}: unintended explicit-only policy')
    for path in root.rglob('*.md'):
        if any(part in ('data', 'reports', 'results', 'dist', '.git', '.venv') for part in path.relative_to(root).parts):
            continue
        for target in re.findall(r'\[[^\]]*\]\(([^)]+)\)', path.read_text()):
            if re.match(r'^[a-z][a-z0-9+.-]*:', target) or target.startswith('#'):
                continue
            linked = (path.parent / target.split('#')[0]).resolve()
            if not linked.exists():
                errors.append(f'{path.relative_to(root)}: broken link {target}')
    workflows = json.loads((root / 'workflows.json').read_text())['workflows']
    ids = []
    for workflow in workflows:
        ids.append(workflow['id'])
        if workflow['entry_skill'] not in names or not set(workflow['skills']) <= names:
            errors.append(f'{workflow["id"]}: unresolved skills')
        if not workflow['gates'] or not workflow['required_outputs']:
            errors.append(f'{workflow["id"]}: missing contracts')
    if len(ids) != len(set(ids)):
        errors.append('duplicate workflows')
    # Syntax-parse every JSON resource; scripts are exercised by unit tests.
    for path in [*(root / 'skills').rglob('*.json'), *(root / 'examples').glob('*.json')]:
        try:
            json.loads(path.read_text())
        except ValueError as exc:
            errors.append(f'{path}: invalid JSON: {exc}')
    if errors:
        raise ValueError('\n'.join(errors))
    return f'Validated {len(names)} skills, {len(workflows)} workflows, UI metadata and local references.'


if __name__ == '__main__':
    try:
        print(validate())
    except (ValueError, KeyError, OSError) as exc:
        print(exc, file=sys.stderr)
        sys.exit(1)
