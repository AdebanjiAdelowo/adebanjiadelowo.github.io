"""Offline tests for check_links.py: each defect class must be detected.

Run: python3 scripts/test_check_links.py
"""
import shutil
import sys
import tempfile
import unittest
import urllib.error
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parent))
import check_links  # noqa: E402

PDF = b'%PDF-1.5\n' + b'0' * 2000 + b'\n%%EOF\n'
TEX = b'\\documentclass{article}\\begin{document}x\\end{document}\n'


class SiteFixture(unittest.TestCase):
    def setUp(self):
        self.root = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, self.root)
        (self.root / 'downloads/cv').mkdir(parents=True)
        (self.root / 'projects').mkdir()
        (self.root / 'assets/css').mkdir(parents=True)
        (self.root / 'images').mkdir()
        (self.root / 'images/Photo.png').write_bytes(b'png')
        for rel, kind in check_links.REQUIRED_DOWNLOADS.items():
            (self.root / rel).write_bytes(PDF if kind == 'pdf' else TEX)
        for copy, canonical in check_links.COMPAT_COPIES.items():
            (self.root / copy).write_bytes((self.root / canonical).read_bytes())
        (self.root / 'assets/css/site.css').write_text('body{background:url("../../images/Photo.png")}')
        self.page('<a href="./downloads/cv/Academic_CV_Adelowo.pdf">cv</a><img src="./images/Photo.png">'
                  '<a href="mailto:someone@example.org">mail</a><a href="https://example.org/">x</a>')
        patcher = mock.patch.object(check_links, 'ROOT', self.root)
        patcher.start()
        self.addCleanup(patcher.stop)

    def page(self, body, name='index.html'):
        (self.root / name).write_text(f'<html><body>{body}</body></html>')

    def errors(self):
        return check_links.offline(check_links.collect())[0]

    def test_clean_site_passes(self):
        errors, external = check_links.offline(check_links.collect())
        self.assertEqual(errors, [])
        self.assertEqual(set(external), {'https://example.org/'})

    def test_missing_local_target(self):
        self.page('<a href="./missing.html">x</a>', 'other.html')
        self.assertTrue(any('missing local target ./missing.html' in e for e in self.errors()))

    def test_case_mismatch_is_detected(self):
        self.page('<img src="./images/photo.png">', 'other.html')
        found = self.errors()
        # On a case-insensitive filesystem the file "exists"; either way it must be reported.
        self.assertTrue(any('photo.png' in e for e in found), found)

    def test_css_url_is_checked(self):
        (self.root / 'assets/css/site.css').write_text('body{background:url(../../images/gone.png)}')
        self.assertTrue(any('gone.png' in e for e in self.errors()))

    def test_private_repository_link(self):
        self.page('<a href="https://raw.githubusercontent.com/AdebanjiAdelowo/selected-projects-scientific-audit/main/x.pdf">x</a>', 'other.html')
        self.assertTrue(any('private repository' in e for e in self.errors()))

    def test_root_relative_path(self):
        self.page('<a href="/cv.html">x</a>', 'other.html')
        self.assertTrue(any('root-relative' in e for e in self.errors()))

    def test_invalid_required_download(self):
        (self.root / 'downloads/cv/Academic_CV_Adelowo.pdf').write_text('<html>Sign in</html>')
        found = self.errors()
        self.assertTrue(any('not a valid pdf' in e for e in found), found)

    def test_missing_tex_source(self):
        (self.root / 'downloads/cv/Academic_CV_Adelowo.tex').unlink()
        self.assertTrue(any('required download missing' in e for e in self.errors()))

    def test_compat_copy_drift(self):
        (self.root / 'cv.pdf').write_bytes(PDF + b'changed')
        self.assertTrue(any('compatibility copy cv.pdf' in e for e in self.errors()))

    def test_malformed_mailto(self):
        self.page('<a href="mailto:not-an-address">x</a>', 'other.html')
        self.assertTrue(any('malformed email' in e for e in self.errors()))


class Classification(unittest.TestCase):
    def run_with(self, effect):
        with mock.patch.object(check_links, 'fetch', side_effect=effect), mock.patch.object(check_links.time, 'sleep'):
            return check_links.classify('https://example.org/x')[:2]

    def http(self, code):
        return urllib.error.HTTPError('https://example.org/x', code, 'x', None, None)

    def test_404_is_broken(self):
        self.assertEqual(self.run_with(self.http(404))[0], 'broken')

    def test_github_login_redirect_is_broken(self):
        result = self.run_with(lambda url: (200, 'https://github.com/login?return_to=x', 'text/html', b''))
        self.assertEqual(result[0], 'broken')

    def test_403_is_unverifiable(self):
        self.assertEqual(self.run_with(self.http(403))[0], 'unverifiable')

    def test_timeout_is_transient_after_retries(self):
        self.assertEqual(self.run_with(TimeoutError('timed out'))[0], 'transient')

    def test_503_is_transient(self):
        self.assertEqual(self.run_with(self.http(503))[0], 'transient')

    def test_recovers_after_one_transient_failure(self):
        responses = iter([TimeoutError('t'), (200, 'https://example.org/x', 'text/html', b'')])
        def effect(url):
            r = next(responses)
            if isinstance(r, Exception):
                raise r
            return r
        self.assertEqual(self.run_with(effect)[0], 'ok')


if __name__ == '__main__':
    unittest.main(verbosity=1)
