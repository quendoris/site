#!/usr/bin/env python3
"""Exact-source B v0.6 checks. Builds into temp, compares against deployed tree.

Neither successful HTTP HEAD nor syntactic markup alone establishes that the
real page looks or works right. Browser acceptance remains a separate gate.
"""
from __future__ import annotations
import hashlib
import sys
from pathlib import Path
from tempfile import TemporaryDirectory

REPO=Path(__file__).resolve().parents[1]
SOURCE=REPO/'design/reference-b-v06'
sys.path.insert(0,str(SOURCE/'tools'))
from build_reference_b import build, page

LATIN='Quam multa fieri non posse prius quam sunt facta iudicantur?'
EXPECTED_PDF='6c4a941a71695cd96d7445ad6de601aeea5cbf59477812a9b0bfab899d215e47'
MARK_SHA='54c918920bffeac368c69015175abaa1d958cfba9cac4f34b0c56ee3bec3dcfd'

def sha(data:bytes)->str: return hashlib.sha256(data).hexdigest()
def check():
    errors=[]
    def require(cond,why):
        if not cond: errors.append(why)
    require(sha((SOURCE/'src/reference/mark.svg').read_bytes())==MARK_SHA, 'original emblem SVG digest changed')
    require((SOURCE/'src/reference/index.html').is_file(),'historical source homepage absent')
    paper=REPO/'dist/publications/constructive-million/v1.0.0/article.pdf'
    require(paper.is_file() and sha(paper.read_bytes())==EXPECTED_PDF,'published PDF changed')
    with TemporaryDirectory() as temp:
        generated=build(Path(temp))
        require(len(generated)==12,'expected exactly 5 B pages and 7 B assets')
        for path,digest in sorted(generated.items()):
            target=REPO/'dist'/path
            require(target.is_file() and sha(target.read_bytes())==digest,'source mismatch at dist/'+path)
    for source in ('index.html','publications/index.html','research/index.html','about/index.html','research/implicit-sliding-puzzles/index.html'):
        html=(REPO/'dist'/source).read_text(encoding='utf8')
        require('noindex' not in html,'unexpected noindex on '+source)
        require('b-reference-b.css' in html,'reference CSS absent on '+source)
        require('b-reference-atmosphere.js' in html,'theme controller absent on '+source)
        require('rel="canonical"' in html,'canonical URL absent on '+source)
    index=(REPO/'dist/index.html').read_text(encoding='utf8')
    require('<h1 id="hero-title" lang="la">'+LATIN+'</h1>' in index,'Latin Pliny heading altered')
    require('Как много вещей считают невозможными' in index,'translation absent')
    css=(REPO/'dist/assets/b-reference-atmosphere.css').read_text(encoding='utf8')
    require('Dark scene 01 intentionally has zero hero/font/layout overrides' in css,'scene 01 fidelity contract absent')
    js=(REPO/'dist/assets/b-reference-atmosphere.js').read_text(encoding='utf8')
    require('sessionStorage' in js and 'qtheme' in js,'session/scene behavior absent')
    require('fetch(' not in js and 'sendBeacon' not in js,'unexpected remote API in atmosphere script')
    for msg in errors: print('FAIL:',msg,file=sys.stderr)
    if errors: return 1
    print('OK: exact B source matches 12 distributed artifacts, original quote, all routes and pinned scientific PDF')
    return 0
if __name__=='__main__': raise SystemExit(check())
