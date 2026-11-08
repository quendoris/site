#!/usr/bin/env python3
"""Build canonical static Quendoris pages FROM the exact reviewed B v0.2 source.

No screenshot re-synthesis. Original b.css/base.css/particles-b.svg and content are
versioned under src/reference. Only URL routing, public metadata, status stamp,
and an optional tiny light-mode control are adapted.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / 'src/reference'
ASSETS = ROOT / 'src/atmosphere'
ROUTES = {
    'index.html': 'index.html',
    'about.html': 'about/index.html',
    'publications.html': 'publications/index.html',
    'research.html': 'research/index.html',
    'study.html': 'research/implicit-sliding-puzzles/index.html',
}
CANONICAL = 'https://quendoris1v7jcxzkgtd9geq7ran.duckdns.org'
PATHS = {
    'href="index.html"': 'href="/"',
    'href="publications.html"': 'href="/publications/"',
    'href="research.html"': 'href="/research/"',
    'href="about.html"': 'href="/about/"',
    'href="study.html"': 'href="/research/implicit-sliding-puzzles/"',
    'href="../assets/base.css"': 'href="/assets/b-reference-base.css"',
    'href="../assets/b.css"': 'href="/assets/b-reference-b.css"',
    'href="../assets/mark.svg"': 'href="/assets/b-reference-mark.svg"',
    'src="../assets/particles-b.svg"': 'src="/assets/b-reference-particles.svg"',
    'src="../assets/implicit-field.svg"': 'src="/assets/b-reference-field.svg"',
}
CONTROLS = '''<details class="atmo-switch"><summary aria-label="Параметры света Quendoris">Свет <span>◈</span></summary><div class="atmo-menu"><label for="qnd-mode">ОСВЕЩЕНИЕ</label><select id="qnd-mode" aria-label="Режим освещения"><option value="clock">По часам</option><option value="system">Тема устройства</option><option value="light">Светлая</option><option value="dark">Тёмная</option></select><div><button type="button" id="qnd-next">Другой свет</button><button type="button" id="qnd-copy">Ссылка</button></div><p>День: 07–19 · Ночь: 19–07<br>Сцена сохраняется в этой вкладке.</p></div></details>'''
META = {
    'index.html': ('Независимые исследования Quendoris: математика, алгоритмы, доказательства и проверяемые результаты.', '/'),
    'about.html': ('Принципы независимого исследовательского архива Quendoris.', '/about/'),
    'publications.html': ('Публикации Quendoris, исходные материалы и воспроизводимые проверки.', '/publications/'),
    'research.html': ('Исследовательские направления Quendoris: алгоритмы, математика, архитектура.', '/research/'),
    'study.html': ('Implicit Sliding Puzzles: конструктивные алгоритмы и ограничения применимости.', '/research/implicit-sliding-puzzles/'),
}
ASSET_MAP = {
    'base.css':'b-reference-base.css',
    'b.css':'b-reference-b.css',
    'particles-b.svg':'b-reference-particles.svg',
    'mark.svg':'b-reference-mark.svg',
    'implicit-field.svg':'b-reference-field.svg',
}

def page(filename: str) -> str:
    html=(SRC/filename).read_text(encoding='utf-8')
    assert '<body class="variant variant-b">' in html
    assert '<meta name="robots" content="noindex,nofollow">' in html
    assert '<a class="lab-jump" href="../index.html"' in html
    assert '<link rel="stylesheet" href="../assets/base.css">' in html
    assert '<link rel="stylesheet" href="../assets/b.css">' in html
    html=html.replace('<meta name="robots" content="noindex,nofollow">', '')
    desc,route=META[filename]
    html=html.replace('<meta name="description" content="Независимая экспериментальная визуальная реконструкция Quendoris, вариант B">',
        '<meta name="description" content="'+desc+'"><link rel="canonical" href="'+CANONICAL+route+'">')
    html=html.replace('<meta name="color-scheme" content="dark">', '<meta name="color-scheme" content="light dark">')
    html=html.replace('<title>Главная · Quendoris / B · прототип</title>', '<title>Quendoris — Независимые исследования</title>')
    html=html.replace(' · Quendoris / B · прототип</title>', ' · Quendoris</title>')
    for a,b in PATHS.items(): html=html.replace(a,b)
    start=html.index('<a class="lab-jump" href="../index.html"')
    end=html.index('</a>',start)+len('</a>')
    html=html[:start]+CONTROLS+html[end:]
    html=html.replace('VISUAL STUDY / B<br>2026.11.08 · НЕ ПУБЛИКАЦИЯ', 'QUENDORIS / RESEARCH<br>2026')
    html=html.replace('</head>', '<link rel="stylesheet" href="/assets/b-reference-atmosphere.css"><script src="/assets/b-reference-atmosphere.js"></script></head>',1)
    # Scene meter is visually passive and uses the source reference's position/stamp typography.
    html=html.replace('<span class="figure-stamp">Q / 01 — INVERSION FIELD</span>',
                      '<span class="figure-stamp">Q / 01 — INVERSION FIELD <span id="qnd-scene" aria-hidden="true"></span></span>')
    if filename=='index.html':
        assert '<h1 id="hero-title" lang="la">Quam multa fieri non posse prius quam sunt facta iudicantur?</h1>' in html
        assert '<section class="post-quote">' in html and '<section class="pledge">' in html
    assert 'noindex' not in html
    assert 'href="../' not in html and 'src="../' not in html
    return html

def build(destination: Path) -> dict:
    destination=destination.resolve()
    result={}
    for original,target in ROUTES.items():
        out=destination/target
        out.parent.mkdir(parents=True,exist_ok=True)
        out.write_text(page(original),encoding='utf-8')
        result[target]=hashlib.sha256(out.read_bytes()).hexdigest()
    for a,b in ASSET_MAP.items():
        out=destination/'assets'/b
        out.parent.mkdir(parents=True,exist_ok=True)
        out.write_bytes((SRC/a).read_bytes())
        result['assets/'+b]=hashlib.sha256(out.read_bytes()).hexdigest()
    for a,b in [('b-atmosphere.css','b-reference-atmosphere.css'),('b-atmosphere.js','b-reference-atmosphere.js')]:
        out=destination/'assets'/b
        out.write_bytes((ASSETS/a).read_bytes())
        result['assets/'+b]=hashlib.sha256(out.read_bytes()).hexdigest()
    return result

def main() -> int:
    p=argparse.ArgumentParser()
    p.add_argument('--output',type=Path,default=ROOT/'preview')
    args=p.parse_args()
    manifest=build(args.output)
    print('BUILT',len(manifest),'reference B pages and assets at',args.output)
    print(json.dumps(manifest,ensure_ascii=False,indent=2,sort_keys=True))
    return 0
if __name__=='__main__': raise SystemExit(main())
