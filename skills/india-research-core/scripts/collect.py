#!/usr/bin/env python3
"""Cache accessible public HTTPS evidence with retrieval metadata, not inferred freshness."""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import ipaddress
import json
import math
from pathlib import Path
import socket
import sys
import urllib.error
import urllib.parse
import urllib.request


def public_https(url):
    parsed = urllib.parse.urlsplit(url)
    if parsed.scheme != 'https' or not parsed.hostname or parsed.username or parsed.password:
        raise ValueError('use a public HTTPS URL without credentials')
    if parsed.port not in (None, 443):
        raise ValueError('only the standard HTTPS port is supported')
    if parsed.fragment:
        raise ValueError('remove the URL fragment before collecting a document')
    for item in socket.getaddrinfo(parsed.hostname, 443, type=socket.SOCK_STREAM):
        if not ipaddress.ip_address(item[4][0]).is_global:
            raise ValueError('local/private destinations are not supported')
    return url


class PublicRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        public_https(newurl)
        return super().redirect_request(req, fp, code, msg, headers, newurl)


def collect(url, source_id, output_dir, max_age_hours=0, max_bytes=20_000_000):
    if not source_id.strip():
        raise ValueError('source ID is required')
    if not math.isfinite(max_age_hours) or max_age_hours < 0:
        raise ValueError('max-age-hours must be finite and nonnegative')
    if max_bytes <= 0:
        raise ValueError('max-bytes must be positive')
    # Validate URL structure even when offline cache is used; do not require DNS
    # for a valid cache hit, so evidence remains usable during an outage.
    parts = urllib.parse.urlsplit(url)
    if parts.scheme != 'https' or not parts.hostname or parts.username or parts.password or parts.fragment or parts.port not in (None, 443):
        raise ValueError('use a standard public HTTPS document URL without credentials/fragments')
    key = hashlib.sha256(url.encode()).hexdigest()
    root = Path(output_dir)
    meta_path = root / f'{key}.json'
    now = datetime.now(timezone.utc)
    if meta_path.exists() and max_age_hours > 0:
        meta = json.loads(meta_path.read_text())
        retrieved = datetime.fromisoformat(meta['retrieved_at'])
        if retrieved.tzinfo is None:
            raise ValueError('cache retrieval timestamp is missing timezone')
        age = (now - retrieved).total_seconds() / 3600
        artifact = root / meta['artifact_name']
        if artifact.parent.resolve() != root.resolve():
            raise ValueError('invalid cache artifact path')
        if 0 <= age <= max_age_hours and artifact.exists():
            if hashlib.sha256(artifact.read_bytes()).hexdigest() == meta['sha256']:
                return {**meta, 'id': source_id, 'artifact': str(artifact), 'cache_hit': True,
                        'accessed_at': now.isoformat()}
    public_https(url)
    request = urllib.request.Request(url, headers={'User-Agent': 'IndianResearchSkills/1.0 (public research document retrieval)'})
    opener = urllib.request.build_opener(PublicRedirect())
    with opener.open(request, timeout=20) as response:
        body = response.read(max_bytes + 1)
        if len(body) > max_bytes:
            raise ValueError('document exceeds max-bytes; use an authorized manual download')
        content_type = response.headers.get('Content-Type', 'application/octet-stream')
        final_url = response.geturl()
        public_https(final_url)
        headers = {key: response.headers.get(key) for key in ('ETag', 'Last-Modified')}
    content_hash = hashlib.sha256(body).hexdigest()
    artifact_name = f'{key}-{content_hash}.bin'
    artifact = root / artifact_name
    root.mkdir(parents=True, exist_ok=True)
    if not artifact.exists():
        with artifact.open('xb') as handle:
            handle.write(body)
    meta = {'id': source_id, 'url': url, 'final_url': final_url,
            'retrieved_at': datetime.now(timezone.utc).isoformat(),
            'published_at': None, 'observed_at': None,
            'content_type': content_type, 'byte_count': len(body),
            'sha256': content_hash, 'artifact_name': artifact_name,
            'http_headers': headers,
            'limitations': 'Content, document identity, publication time and observation period require inspection'}
    # Versioned evidence bytes are retained; pointer replacement is atomic.
    temp = meta_path.with_suffix('.json.tmp')
    temp.write_text(json.dumps(meta, indent=2) + '\n')
    temp.replace(meta_path)
    return {**meta, 'artifact': str(artifact), 'cache_hit': False}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--url', required=True)
    parser.add_argument('--source-id', required=True)
    parser.add_argument('--output-dir', required=True)
    parser.add_argument('--max-age-hours', type=float, default=0)
    parser.add_argument('--max-bytes', type=int, default=20_000_000)
    args = parser.parse_args(argv)
    try:
        result = collect(args.url, args.source_id, args.output_dir, args.max_age_hours, args.max_bytes)
        print(json.dumps(result, indent=2))
        return 0
    except (ValueError, OSError, KeyError, urllib.error.URLError) as exc:
        print(f'Collection unavailable: {exc}. Use another authorized source or a supplied document.', file=sys.stderr)
        return 2


if __name__ == '__main__':
    raise SystemExit(main())
