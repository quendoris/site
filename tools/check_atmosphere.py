#!/usr/bin/env python3
"""Offline Quendoris Atmosphere v0.4 checks. No browsers, networks or Python dependencies."""
from pathlib import Path
from html.parser import HTMLParser
import re
import sys

ROOT=Path(__file__).resolve().parents[1]
LATIN="Quam multa fieri non posse prius quam sunt facta iudicantur?"
RUSSIAN="Как много вещей считают невозможными, пока они не осуществлены?"
PATH='M35 35H386V246H316V386H245V316H176V386H105V246H35Z M106 106H175V175H106Z M246 106H315V175H246Z'
PAGES=[
 'dist/index.html',
 'dist/about/index.html',
 'dist/publications/index.html',
 'dist/research/index.html',
 'dist/research/implicit-sliding-puzzles/index.html',
]
def main():
 errors=[]
 def ok(condition,message):
  if not condition:errors.append(message)
 logo=(ROOT/'dist/assets/quendoris-mark.svg').read_text(encoding="utf-8")
 ok(PATH in logo,"exact logo outline differs")
 ok('fill-rule="evenodd"' in logo,"eyes are not protected by evenodd rule")
 ok((ROOT/'src/design/quendoris-mark.svg').read_text(encoding="utf-8")==logo,
    "mark source/build diverged")
 for name in ['atmosphere.css','atmosphere.js']:
  a=(ROOT/'dist/assets'/name).read_bytes()
  b=(ROOT/'src/design'/name).read_bytes()
  ok(a==b,"source/dist divergence: "+name)
 js=(ROOT/'dist/assets/atmosphere.js').read_text(encoding="utf-8")
 ok('getHours()' in js and 'h>=7&&h<19' in js,"clock boundaries absent")
 ok('qscene' in js and 'sessionStorage' in js and 'localStorage' in js,"visit/session control absent")
 ok('navigator.clipboard' in js,"explicit sharing feature absent")
 ok('fetch(' not in js and 'XMLHttpRequest' not in js and 'sendBeacon' not in js,
    "unexpected network function in theme controller")
 for p in PAGES:
  content=(ROOT/p).read_text(encoding="utf-8")
  ok(content.count('src="/assets/atmosphere.js"')==1,"theme controller missing or duplicated: "+p)
  ok(content.count('href="/assets/atmosphere.css"')==1,"theme style missing or duplicated: "+p)
  ok(content.count('src="/assets/quendoris-mark.svg"')==2,"header/footer logo mismatch: "+p)
  ok(content.count('id="qnd-mode"')==1,"theme selector missing or duplicated: "+p)
  ok('noindex' not in content and 'прототип' not in content.lower(),"experimental marker in public HTML: "+p)
  ok('<link rel="canonical"' in content,"canonical absent: "+p)
 h=(ROOT/'dist/index.html').read_text(encoding="utf-8")
 ok('<h1 lang="la">'+LATIN+'</h1>' in h,"Latin hero quote differs")
 ok(RUSSIAN in h,"subordinate Russian translation differs")
 ok("Плиний Старший" in h and "Naturalis Historia" in h and "§ 6" in h,
    "source attribution missing")
 ok('class="qnd-afterword"' in h,"project's own statement must follow historical quote")
 pdf=(ROOT/'dist/publications/constructive-million/v1.0.0/article.pdf').read_bytes()
 import hashlib
 ok(hashlib.sha256(pdf).hexdigest()=="6c4a941a71695cd96d7445ad6de601aeea5cbf59477812a9b0bfab899d215e47",
    "historic published PDF digest changed")
 for err in errors:print("FAIL:",err,file=sys.stderr)
 if errors:return 1
 print("OK: Pliny original, exact mark, 5 routes, atmosphere source, offline constraints, PDF preserved")
 return 0
if __name__=="__main__":raise SystemExit(main())
