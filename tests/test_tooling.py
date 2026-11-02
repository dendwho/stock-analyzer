from datetime import datetime, timezone
import hashlib
import importlib.util
import json
from pathlib import Path
import re
import socket
import tempfile
import unittest
from unittest.mock import MagicMock, patch
import zipfile

ROOT = Path(__file__).resolve().parents[1]


def module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    result = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(result)
    return result


collector = module('collector', ROOT / 'skills/india-research-core/scripts/collect.py')
installer = module('installer', ROOT / 'scripts/install.py')
packager = module('packager', ROOT / 'scripts/package.py')
saver = module('saver', ROOT / 'skills/india-research-core/scripts/save_report.py')


class ReportSavingTests(unittest.TestCase):
    def test_markdown_and_matching_sidecar(self):
        with tempfile.TemporaryDirectory() as temp:
            result = saver.save_report('# Research\n\nEvidence and conclusion.', 'Infosys', 'Stock Analysis', temp, {'schema_version': 1})
            markdown, sidecar = Path(result['markdown']), Path(result['sidecar'])
            self.assertEqual(markdown.stem, sidecar.stem)
            self.assertIn('infosys_stock-analysis_', markdown.name)
            self.assertIn('_IST.md', markdown.name)
            self.assertEqual(markdown.read_text(), '# Research\n\nEvidence and conclusion.\n')
            self.assertEqual(json.loads(sidecar.read_text()), {'schema_version': 1})

    def test_repeated_saves_preserve_history_even_with_same_timestamp(self):
        with tempfile.TemporaryDirectory() as temp:
            with patch.object(saver, 'datetime') as clock:
                clock.now.return_value.strftime.return_value = '2026-11-02_173015_123456_IST'
                first = saver.save_report('First report', 'INFY', 'stock-analysis', temp)
                second = saver.save_report('Updated report', 'INFY', 'stock-analysis', temp)
            self.assertNotEqual(first['markdown'], second['markdown'])
            self.assertEqual(Path(first['markdown']).read_text(), 'First report\n')
            self.assertEqual(Path(second['markdown']).read_text(), 'Updated report\n')

    def test_subject_cannot_escape_results_directory(self):
        with tempfile.TemporaryDirectory() as temp:
            result = saver.save_report('Report', '../../Company/name', 'IPO analysis', temp)
            self.assertEqual(Path(result['markdown']).parent, Path(temp).resolve())
            self.assertTrue(Path(result['markdown']).name.startswith('company-name_ipo-analysis_'))

    def test_invalid_content_creates_no_files(self):
        with tempfile.TemporaryDirectory() as temp:
            for content, sidecar in (('', None), ('Report', []), ('Report', {'bad': float('nan')})):
                with self.assertRaises(ValueError):
                    saver.save_report(content, 'subject', 'analysis', temp, sidecar)
            self.assertEqual(list(Path(temp).iterdir()), [])


class CollectionTests(unittest.TestCase):
    def test_private_or_insecure_url_rejected(self):
        for url in ('http://example.com/a', 'https://user:pass@example.com/a',
                    'https://example.com:444/a', 'https://example.com/a#fragment'):
            with self.assertRaises(ValueError):
                collector.public_https(url)
        with patch.object(collector.socket, 'getaddrinfo', return_value=[(socket.AF_INET, socket.SOCK_STREAM, 6, '', ('127.0.0.1', 443))]):
            with self.assertRaisesRegex(ValueError, 'private'):
                collector.public_https('https://localhost/a')

    def test_cache_hit_preserves_retrieval_time_and_does_not_require_network(self):
        with tempfile.TemporaryDirectory() as temp:
            url = 'https://example.com/filing.pdf'
            key = hashlib.sha256(url.encode()).hexdigest()
            body = b'synthetic filing'
            artifact = Path(temp) / 'document.bin'
            artifact.write_bytes(body)
            retrieved = datetime.now(timezone.utc).isoformat()
            meta = {'id': 'old', 'url': url, 'retrieved_at': retrieved,
                    'artifact_name': artifact.name, 'sha256': hashlib.sha256(body).hexdigest()}
            (Path(temp) / f'{key}.json').write_text(json.dumps(meta))
            with patch.object(collector.socket, 'getaddrinfo', side_effect=AssertionError('network should not be used')):
                result = collector.collect(url, 'new', temp, max_age_hours=1)
            self.assertTrue(result['cache_hit'])
            self.assertEqual(result['retrieved_at'], retrieved)
            self.assertEqual(result['id'], 'new')

    def test_fetch_stores_hash_without_inventing_observation_time(self):
        response = MagicMock()
        response.__enter__.return_value = response
        response.read.return_value = b'fake public document'
        response.headers = {'Content-Type': 'application/pdf'}
        response.geturl.return_value = 'https://example.com/doc'
        opener = MagicMock()
        opener.open.return_value = response
        with tempfile.TemporaryDirectory() as temp:
            with patch.object(collector, 'public_https', side_effect=lambda url: url), patch.object(collector.urllib.request, 'build_opener', return_value=opener):
                result = collector.collect('https://example.com/doc', 'filing', temp)
            self.assertFalse(result['cache_hit'])
            self.assertEqual(Path(result['artifact']).read_bytes(), b'fake public document')
            self.assertIsNone(result['published_at'])
            self.assertIsNone(result['observed_at'])
            self.assertEqual(result['sha256'], hashlib.sha256(b'fake public document').hexdigest())
            self.assertEqual(opener.open.call_args.kwargs['timeout'], 20)

    def test_large_fetch_is_bounded(self):
        response = MagicMock()
        response.__enter__.return_value = response
        response.read.return_value = b'123456'
        opener = MagicMock()
        opener.open.return_value = response
        with tempfile.TemporaryDirectory() as temp:
            with patch.object(collector, 'public_https', side_effect=lambda url: url), patch.object(collector.urllib.request, 'build_opener', return_value=opener):
                with self.assertRaisesRegex(ValueError, 'max-bytes'):
                    collector.collect('https://example.com/doc', 'filing', temp, max_bytes=5)
            self.assertFalse(list(Path(temp).iterdir()))


class DistributionTests(unittest.TestCase):
    def test_dry_run_changes_no_destination(self):
        with tempfile.TemporaryDirectory() as temp:
            dest = Path(temp) / 'absent'
            result = installer.install(dest, dry_run=True)
            self.assertEqual(len(result['skills']), 22)
            self.assertFalse(dest.exists())

    def test_install_keeps_all_shared_references_and_license(self):
        with tempfile.TemporaryDirectory() as temp:
            dest = Path(temp) / 'skills'
            result = installer.install(dest)
            self.assertEqual(result['installed'], 22)
            self.assertTrue((dest / 'india-research-core/THIRD_PARTY_NOTICES.md').is_file())
            for skill in dest.glob('*/SKILL.md'):
                for target in re.findall(r'\[[^\]]*\]\(([^)]+)\)', skill.read_text()):
                    self.assertTrue((skill.parent / target).exists(), f'{skill}: {target}')
            with self.assertRaisesRegex(ValueError, 'replace'):
                installer.install(dest)

    def test_partial_conflict_does_not_install_anything(self):
        with tempfile.TemporaryDirectory() as temp:
            dest = Path(temp)
            (dest / 'india-ipo-analysis').mkdir()
            with self.assertRaises(ValueError):
                installer.install(dest)
            self.assertEqual(len(list(dest.iterdir())), 1)

    def test_package_deterministic_and_omits_private_directories(self):
        with tempfile.TemporaryDirectory() as temp:
            a, b = Path(temp) / 'a.zip', Path(temp) / 'b.zip'
            packager.package(a)
            packager.package(b)
            self.assertEqual(hashlib.sha256(a.read_bytes()).hexdigest(), hashlib.sha256(b.read_bytes()).hexdigest())
            with zipfile.ZipFile(a) as archive:
                names = archive.namelist()
                self.assertIn('skills/india-ipo-analysis/SKILL.md', names)
                self.assertIn('THIRD_PARTY_NOTICES.md', names)
                self.assertFalse(any(n.startswith(('data/', 'reports/', 'results/', '.env', '.git/')) or '__pycache__' in n for n in names))
            with self.assertRaises(ValueError):
                packager.package(a)

    def test_suite_metadata_and_links(self):
        validator = module('validator', ROOT / 'scripts/validate.py')
        self.assertIn('Validated 22 skills', validator.validate())


if __name__ == '__main__':
    unittest.main()
