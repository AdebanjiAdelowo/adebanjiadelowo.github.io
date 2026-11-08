"""Audit every link and asset reference in the generated site.

Modes (combine as needed):
  python3 scripts/check_links.py                 offline checks (always run)
  python3 scripts/check_links.py --external      also request every external URL
  python3 scripts/check_links.py --live BASE_URL also check the deployed site at BASE_URL

Offline checks: local href/src/srcset/CSS url() targets exist with exact filename
case, required CV downloads exist and are valid files, compatibility copies
match their canonical files, and no link points into a known private repository.

External and live checks use plain unauthenticated requests, the same view an
ordinary visitor has. Results are classified as:
  broken       confirmed failure (404/410, or a GitHub page hidden from the public) -> exit 1
  transient    timeout, connection error or 5xx after retries                       -> warning
  unverifiable the site refuses automated clients (401/403/429/999)                 -> warning
"""
import argparse
import concurrent.futures as cf
import hashlib
import re
import socket
import sys
import time
import urllib.error
import urllib.request
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urljoin, urlsplit

ROOT = Path(__file__).resolve().parents[1]

# Prefer IPv4: without an IPv6 route, urllib tries each IPv6 address in turn and
# waits a full timeout on each, unlike browsers and curl.
_getaddrinfo = socket.getaddrinfo
def _ipv4_first(*args, **kwargs):
    results = _getaddrinfo(*args, **kwargs)
    return [r for r in results if r[0] == socket.AF_INET] or results
socket.getaddrinfo = _ipv4_first
UA = 'Mozilla/5.0 (compatible; site-link-check/1.0)'

# Files every visitor must be able to download.
REQUIRED_DOWNLOADS = {
    'downloads/cv/Academic_CV_Adelowo.pdf': 'pdf',
    'downloads/cv/Academic_CV_Adelowo.tex': 'tex',
    'downloads/cv/Adebanji_Adelowo_CV_ML_Data_Science.pdf': 'pdf',
}
# Older public URLs kept working; each must stay byte-identical to its canonical file.
COMPAT_COPIES = {
    'cv.pdf': 'downloads/cv/Adebanji_Adelowo_CV_ML_Data_Science.pdf',
    'downloads/Adebanji_Adelowo_CV_ML_Data_Science.pdf': 'downloads/cv/Adebanji_Adelowo_CV_ML_Data_Science.pdf',
    'downloads/Academic_CV_Adelowo.pdf': 'downloads/cv/Academic_CV_Adelowo.pdf',
}
# Repositories known to be private: links into them fail for visitors. If one is
# made public, remove it here before linking to it again.
PRIVATE_REPOS = [f'AdebanjiAdelowo/{name}' for name in (
    'selected-projects-scientific-audit', 'multimodal-visual-rag', 'legal-research-rag',
    'fem-topology-optimization', 'course-learning-portal', 'ai-projects-portfolio')]


class Refs(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.refs = []

    def handle_starttag(self, tag, attrs):
        for key, value in attrs:
            if value is None:
                continue
            if key in ('href', 'src', 'poster', 'data-src'):
                self.refs.append(value.strip())
            elif key in ('srcset', 'imagesrcset'):
                self.refs.extend(part.strip().split()[0] for part in value.split(',') if part.strip())
            elif key == 'content' and value.startswith(('http://', 'https://', './', '../', '/')) and dict(attrs).get('property', dict(attrs).get('name', '')).endswith(('image', 'url')):
                self.refs.append(value.strip())


def pages():
    return sorted(list(ROOT.glob('*.html')) + list((ROOT / 'projects').glob('*.html')))


def collect():
    """Return {ref: set of source files} for HTML pages, CSS files and the sitemap."""
    found = {}
    def add(ref, src):
        found.setdefault(ref, set()).add(str(src.relative_to(ROOT)))
    for page in pages():
        parser = Refs()
        parser.feed(page.read_text())
        for ref in parser.refs:
            add((page, ref), page)
    for css in ROOT.glob('assets/**/*.css'):
        for ref in re.findall(r'url\(\s*[\'"]?([^\'")]+)', css.read_text()):
            add((css, ref.strip()), css)
    return found


def exact_case_exists(path):
    """True only if every path component matches the filesystem with exact case."""
    root = ROOT.resolve()
    try:
        rel = path.resolve().relative_to(root)
    except ValueError:
        return False
    current = root
    for part in rel.parts:
        if not current.is_dir() or part not in {p.name for p in current.iterdir()}:
            return False
        current = current / part
    return True


def valid_file(path, kind):
    data = path.read_bytes()
    if kind == 'pdf':
        return len(data) > 1024 and data.startswith(b'%PDF-') and b'%%EOF' in data[-2048:]
    if kind == 'tex':
        text = data.decode('utf-8', 'replace')
        # A literal backslash-n that does not begin a command such as \noindent is an
        # escaped newline pasted into the source; after a % it silently comments
        # out everything that follows on the line.
        escaped_newline = re.search(r'\\n(?![A-Za-z])', text)
        return ('\\documentclass' in text and '\\begin{document}' in text
                and '\\end{document}' in text and not escaped_newline)
    return len(data) > 0


def offline(refs):
    errors, external = [], {}
    for (src, ref), sources in sorted(refs.items(), key=lambda kv: (str(kv[0][0]), kv[0][1])):
        where = ', '.join(sorted(sources))
        url = urlsplit(ref)
        if url.scheme in ('mailto', 'tel'):
            if url.scheme == 'mailto' and not re.fullmatch(r'[^@\s]+@[^@\s]+\.[^@\s]+', unquote(url.path)):
                errors.append(f'{where}: malformed email link {ref}')
            continue
        if url.scheme in ('http', 'https'):
            for repo in PRIVATE_REPOS:
                if repo.lower() in ref.lower():
                    errors.append(f'{where}: link into private repository {repo}: {ref}')
            external.setdefault(ref.split('#')[0], set()).update(sources)
            continue
        if url.scheme or url.netloc:
            errors.append(f'{where}: unsupported link scheme {ref}')
            continue
        if not url.path:
            continue  # same-page anchor, checked by check_site.py
        if url.path.startswith('/'):
            errors.append(f'{where}: root-relative path breaks on a project site, use a relative path: {ref}')
            continue
        target = src.parent / unquote(url.path)
        if target.is_dir():
            target = target / 'index.html'
        if not target.exists():
            errors.append(f'{where}: missing local target {ref}')
        elif not exact_case_exists(target):
            errors.append(f'{where}: filename case differs from the file on disk (breaks on GitHub Pages): {ref}')
    for rel, kind in REQUIRED_DOWNLOADS.items():
        path = ROOT / rel
        if not path.exists() or not exact_case_exists(path):
            errors.append(f'required download missing: {rel}')
        elif not valid_file(path, kind):
            errors.append(f'required download is not a valid {kind} file: {rel}')
    for copy, canonical in COMPAT_COPIES.items():
        a, b = ROOT / copy, ROOT / canonical
        if not a.exists() or not b.exists() or a.read_bytes() != b.read_bytes():
            errors.append(f'compatibility copy {copy} differs from {canonical}')
    return errors, external


def fetch(url):
    """GET the first 4 KB with no credentials, following redirects."""
    req = urllib.request.Request(url, headers={'User-Agent': UA, 'Accept': '*/*'})
    with urllib.request.urlopen(req, timeout=15) as resp:
        return resp.status, resp.geturl(), resp.headers.get('Content-Type', ''), resp.read(4096)


def classify(url):
    """Return (status, detail, content_type, first bytes)."""
    last = 'no response'
    for attempt in range(3):
        try:
            code, final, ctype, body = fetch(url)
            if 'github.com/login' in final:
                return 'broken', f'redirects to GitHub sign-in ({final})', ctype, body
            return 'ok', str(code), ctype, body
        except urllib.error.HTTPError as e:
            if e.code in (404, 410):
                return 'broken', f'HTTP {e.code}', '', b''
            if e.code in (401, 403, 429, 999):
                return 'unverifiable', f'HTTP {e.code} (refuses automated clients)', '', b''
            last = f'HTTP {e.code}'
        except Exception as e:  # timeouts, DNS, TLS, resets
            last = f'{type(e).__name__}: {e}'
        time.sleep(2 * (attempt + 1))
    return 'transient', last, '', b''


def external_check(urls):
    results = {}
    with cf.ThreadPoolExecutor(max_workers=8) as pool:
        futures = {pool.submit(classify, u): u for u in urls}
        for fut in cf.as_completed(futures):
            results[futures[fut]] = fut.result()
    return results


def live_check(base, refs):
    base = base.rstrip('/') + '/'
    targets = {'', 'sitemap.xml', 'robots.txt'}
    for (src, ref) in refs:
        url = urlsplit(ref)
        if url.scheme or url.netloc or not url.path or url.path.startswith('/'):
            continue
        rel = (src.parent / unquote(url.path)).resolve().relative_to(ROOT.resolve()).as_posix()
        targets.add(rel)
    for page in pages():
        targets.add(page.relative_to(ROOT).as_posix())
    targets.update(REQUIRED_DOWNLOADS)
    targets.update(COMPAT_COPIES)
    errors, warnings = [], []
    def one(rel):
        return rel, classify(urljoin(base, rel))
    with cf.ThreadPoolExecutor(max_workers=8) as pool:
        for rel, (status, detail, ctype, body) in pool.map(one, sorted(targets)):
            if status != 'ok':
                (errors if status == 'broken' else warnings).append(f'{base}{rel}: {status}: {detail}')
            elif rel.endswith('.pdf') and not body.startswith(b'%PDF-'):
                errors.append(f'{base}{rel}: not a PDF (Content-Type {ctype})')
            elif rel.endswith('.tex') and b'\\documentclass' not in body:
                errors.append(f'{base}{rel}: not LaTeX source (Content-Type {ctype})')
    return len(targets), errors, warnings


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--external', action='store_true', help='request every external URL without credentials')
    ap.add_argument('--live', metavar='BASE_URL', help='check the deployed site at BASE_URL')
    args = ap.parse_args()
    refs = collect()
    errors, external = offline(refs)
    warnings = []
    local = sum(1 for (_, r) in refs if not urlsplit(r).scheme)
    print(f'Offline: {len(refs)} references ({local} local, {len(external)} unique external URLs) in {len(pages())} pages and CSS')
    if args.external:
        results = external_check(sorted(external))
        counts = {}
        for url, (status, detail, _, _) in sorted(results.items()):
            counts[status] = counts.get(status, 0) + 1
            if status == 'ok':
                continue
            line = f'{url}: {status}: {detail} [in {", ".join(sorted(external[url]))}]'
            (errors if status == 'broken' else warnings).append(line)
        print('External: ' + ', '.join(f'{k}={v}' for k, v in sorted(counts.items())))
    if args.live:
        n, live_errors, live_warnings = live_check(args.live, refs)
        errors += live_errors
        warnings += live_warnings
        print(f'Live: {n} URLs under {args.live}')
    for w in warnings:
        print('WARNING ' + w)
    if errors:
        for e in errors:
            print('ERROR ' + e)
        sys.exit(f'FAIL: {len(errors)} link problem(s)')
    print('PASS: link audit' + (f' ({len(warnings)} warning(s), none confirmed broken)' if warnings else ''))


if __name__ == '__main__':
    main()
