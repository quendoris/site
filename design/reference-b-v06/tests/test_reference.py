from __future__ import annotations
import hashlib
import tempfile
import unittest
import sys
from pathlib import Path
from html.parser import HTMLParser
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools'))
from build_reference_b import build,page,ROUTES,SRC

EXPECTED={
 'base.css':'9d78b4ce8f943f2c1ba739b0c4a67b6f24f58169e2bbf508cdce14112ba11501',
 'b.css':'2d0c16cc1a5e192535783833fab0708cf625319480a6f7a388071aef5d9cde5c',
 'particles-b.svg':'aa20cc865490a064cf88c668b7600052eca69752e0122eafe75f68f00b589a6e',
 'mark.svg':'54c918920bffeac368c69015175abaa1d958cfba9cac4f34b0c56ee3bec3dcfd',
 'index.html':'9fab07a01fc2ae260ea1a582072dbd1fd893f55d6d9ae0ced59a398fd61ddd4c',
}

class Check(HTMLParser):
    def __init__(self):super().__init__();self.stack=[];self.errors=[];self.links=[]
    def handle_starttag(self,tag,attrs):
        if tag not in ('meta','link','img','input','br','hr','source','wbr','embed','area'):
            self.stack.append(tag)
        for k,v in attrs:
            if k in ('href','src') and v:self.links.append(v)
    def handle_endtag(self,tag):
        if not self.stack or self.stack[-1]!=tag:self.errors.append((tag,self.stack[-1] if self.stack else None))
        else:self.stack.pop()

class ReferenceBTests(unittest.TestCase):
    def test_original_assets_cryptographically_fixed(self):
        for file,digest in EXPECTED.items():
            with self.subTest(file=file):self.assertEqual(hashlib.sha256((SRC/file).read_bytes()).hexdigest(),digest)
    def test_primary_heading_and_exact_publication_modules(self):
        h=page('index.html')
        self.assertIn('<h1 id="hero-title" lang="la">Quam multa fieri non posse prius quam sunt facta iudicantur?</h1>',h)
        for cls in ('home-hero historic-hero','hero-rail','post-quote','publication-feature','number-ledger','research-index','pledge'):
            self.assertIn(cls,h)
        for k in ('10¹²','678 347','Fmax','I.A.M.','Книга VII, § 6'):
            self.assertIn(k,h)
    def test_reference_field_original_dots_and_symbol_not_rewritten(self):
        original=(SRC/'index.html').read_text(encoding='utf-8')
        rendered=page('index.html')
        a=original[original.index('<div class="identity-field '):original.index('<div class="hero-rail"')]
        b=rendered[rendered.index('<div class="identity-field '):rendered.index('<div class="hero-rail"')]
        for snippet in ('<svg class="mark-hero"', 'viewBox="0 0 420 420"',
                        '<div class="field-orbit orbit-one"', '<div class="field-orbit orbit-two"',
                        '<span class="axis axis-x"', '<span class="axis axis-y"'):
            self.assertIn(snippet,a);self.assertIn(snippet,b)
        self.assertIn('src="/assets/b-reference-particles.svg"',b)
        self.assertIn('stop-color="#f4f5d2"',b)
        self.assertIn('stop-color="#698a72"',b)
    def test_dark_scene_one_additive_css_has_no_layout_overrides(self):
        css=(ROOT/'src/atmosphere/b-atmosphere.css').read_text()
        self.assertIn('Dark scene 01 intentionally has zero hero/font/layout overrides',css)
        self.assertNotIn('html[data-qtheme="dark"][data-qscene="1"] .identity-field',css)
        self.assertNotIn('html[data-qtheme="dark"][data-qscene="1"] .hero-main',css)
        self.assertNotIn('html[data-qtheme="dark"][data-qscene="1"] .home-hero',css)
    def test_canonical_routes_html_balance_and_links(self):
        for src in ROUTES:
            with self.subTest(file=src):
                h=page(src);p=Check();p.feed(h)
                self.assertEqual(p.errors,[]);self.assertEqual(p.stack,[])
                self.assertNotIn('noindex,nofollow',h)
                self.assertIn('rel="canonical"',h)
                self.assertIn('href="/assets/b-reference-base.css"',h)
                self.assertIn('href="/assets/b-reference-b.css"',h)
                self.assertNotIn('../index.html',h)
    def test_byte_identical_repeated_builds(self):
        with tempfile.TemporaryDirectory() as aa,tempfile.TemporaryDirectory() as bb:
            a=build(Path(aa));b=build(Path(bb))
            self.assertEqual(a,b)
            self.assertEqual(len(a),12)
    def test_logo_pixel_exact_mask(self):
        try:
            import io,cairosvg,numpy as np
            from PIL import Image
        except ImportError:
            self.skipTest('Pillow/CairoSVG/numpy optional for raster test')
        ref=np.array(Image.open(SRC/'mark-original.png').convert('RGB'))
        svg=np.array(Image.open(io.BytesIO(cairosvg.svg2png(url=str(SRC/'mark.svg'),output_width=420,output_height=420))).convert('RGBA'))
        rm=np.all(ref==[211,224,139],axis=2);sm=svg[:,:,3]>0
        self.assertEqual(int(rm.sum()),89249)
        self.assertEqual(int(np.count_nonzero(rm!=sm)),0)
    def test_no_remote_runtime_assets(self):
        for p in ('src/atmosphere/b-atmosphere.js','src/atmosphere/b-atmosphere.css'):
            s=(ROOT/p).read_text();self.assertNotIn('https://',s);self.assertNotIn('fetch(',s)

if __name__=='__main__':unittest.main()
