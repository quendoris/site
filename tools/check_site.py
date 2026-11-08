#!/usr/bin/env python3
"""Validate the site-only release tree and its pinned transport checksums.

This verifier is stdlib-only. Git hashes and SHA256SUMS alone do not provide
independent proof of authorship. Check an externally pinned commit/signature.
"""
from __future__ import annotations
import hashlib
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlsplit
import argparse
import re
import sys

PDF_SHA = "6c4a941a71695cd96d7445ad6de601aeea5cbf59477812a9b0bfab899d215e47"
PDF_PATH = "dist/publications/constructive-million/v1.0.0/article.pdf"
LINE = re.compile(r"^([0-9a-f]{64})  (dist/[A-Za-z0-9_./-]+)$")

class LinkExtractor(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.links: list[str] = []
    def handle_starttag(self, tag, attrs):
        kv = dict(attrs)
        for key in ("href", "src"):
            val = kv.get(key)
            if isinstance(val, str) and val:
                self.links.append(val)

def checksum(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as file:
        for chunk in iter(lambda: file.read(1048576), b""):
            h.update(chunk)
    return h.hexdigest()

def check(root: Path) -> int:
    root = root.resolve()
    dist = root / "dist"
    if not dist.is_dir() or dist.is_symlink():
        raise ValueError("missing or symlinked dist directory")
    manifest = (root / "SHA256SUMS").read_text(encoding="utf-8")
    expected: dict[str,str] = {}
    for line in manifest.splitlines():
        m = LINE.fullmatch(line)
        if not m:
            raise ValueError(f"invalid checksum line: {line!r}")
        digest, name = m.groups()
        segments = Path(name).parts
        if ".." in segments or "." in segments or name in expected:
            raise ValueError(f"unsafe/duplicate path: {name}")
        expected[name] = digest
    actual = {}
    for file in sorted(dist.rglob("*")):
        if file.is_symlink():
            raise ValueError(f"symlinks prohibited: {file}")
        if file.is_file():
            actual[file.relative_to(root).as_posix()] = checksum(file)
    if expected != actual:
        extras = set(actual) - set(expected)
        missing = set(expected) - set(actual)
        modified = [x for x in expected.keys() & actual.keys() if expected[x] != actual[x]]
        raise ValueError(f"SHA256 mismatch: missing={sorted(missing)}, extra={sorted(extras)}, modified={sorted(modified)}")
    if actual.get(PDF_PATH) != PDF_SHA:
        raise ValueError("signed-paper PDF digest changed")
    if not (dist / "index.html").is_file():
        raise ValueError("index.html missing")
    checked_links = 0
    for html in sorted(dist.rglob("*.html")):
        parser = LinkExtractor()
        parser.feed(html.read_text(encoding="utf-8"))
        for raw in parser.links:
            uri = urlsplit(raw)
            if uri.scheme or uri.netloc or raw.startswith("#"):
                continue
            path = unquote(uri.path)
            if not path:
                continue
            if path.startswith("/"):
                target = dist / path.lstrip("/")
            else:
                target = html.parent / path
            try:
                target = target.resolve(strict=False)
                target.relative_to(dist)
            except ValueError as exc:
                raise ValueError(f"out-of-root link: {html}: {raw}") from exc
            if target.is_dir():
                target = target / "index.html"
            if not target.is_file():
                raise ValueError(f"broken local link: {html}: {raw}")
            checked_links += 1
    # Editorial/brand regression gates: this quotation is a literal primary-source witness.
    # These assertions check the intended HTML text, not universal historical authenticity.
    from xml.etree import ElementTree as ET
    original = "Quam multa fieri non posse prius quam sunt facta iudicantur?"
    translation = "Как много вещей считают невозможными, пока они не осуществлены?"
    home = (dist / "index.html").read_text(encoding="utf-8")
    if f'<h1 class="hero-quote" lang="la">{original}</h1>' not in home:
        raise ValueError("verified Pliny Latin homepage heading changed or missing")
    for exact in (f'<p class="hero-translation" lang="ru">{translation}</p>',
                  "Плиний Старший", "Naturalis Historia", "книга VII, § 6",
                  "I век н. э.",
                  "https://penelope.uchicago.edu/thayer/l/roman/texts/pliny_the_elder/7%2A.html"):
        if exact not in home:
            raise ValueError("Pliny source attribution or translation missing: " + exact)
    original_shape = ("M 35 35 L 386 35 L 386 246 L 316 246 L 316 386 "
                      "L 245 386 L 245 316 L 176 316 L 176 386 "
                      "L 105 386 L 105 246 L 35 246 Z "
                      "M 106 106 L 175 106 L 175 175 L 106 175 Z "
                      "M 246 106 L 315 106 L 315 175 L 246 175 Z")
    for asset in ("favicon.svg", "quendoris-mark.svg", "quendoris-inversion.svg"):
        root_svg = ET.fromstring((dist / "assets" / asset).read_text(encoding="utf-8"))
        if root_svg.get("viewBox") != "0 0 420 420":
            raise ValueError("changed Quendoris SVG viewBox: " + asset)
        paths = root_svg.findall("{http://www.w3.org/2000/svg}path")
        if len(paths) != 1 or paths[0].get("d") != original_shape or paths[0].get("fill-rule") != "evenodd":
            raise ValueError("changed original Quendoris silhouette: " + asset)
    for page in sorted(dist.rglob("*.html")):
        if 'src="/assets/quendoris-mark.svg"' not in page.read_text(encoding="utf-8"):
            raise ValueError("original emblem absent from navigation: " + page.as_posix())

    print(f"OK: {len(actual)} files, {checked_links} internal references, PDF SHA-256 verified")
    return len(actual)

if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    args = p.parse_args()
    try:
        check(args.root)
    except (ValueError, OSError, UnicodeError) as e:
        print(f"REJECTED: {e}", file=sys.stderr)
        sys.exit(1)
