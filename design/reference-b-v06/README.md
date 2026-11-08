# Quendoris B v0.6 — faithful source port, not a redesign

**Status:** local reproduction/review package. **NOT deployed, NOT merged to main.** The public server remains on the restored v0.3 release until a separate reviewed publication.

## What changed in our engineering approach

Earlier v0.4/v0.5 approximations recreated the look with unrelated CSS. This file instead includes original B v0.2 page HTML, `base.css`, `b.css`, `particles-b.svg` and the true Quendoris mark from the accepted source archive. Those source bytes are pinned by tests and are not rewritten. The five canonical site routes are built through minimal, auditable URL/metadata adaptation.

Dark **scene 01** deliberately uses the original `base.css` + `b.css` + original `particles-b.svg`, including their original full-bleed hero, three-line headline at the desktop reference viewport, historical citation rail, research data ledger, 3-row catalogue and lime publication principle band. Only the experiment's noindex/gallery links and footer stamp are removed; the header's last small utility link becomes the compact `Свет` switch. Dark scenes 02–06 vary only the light field/particle intensity, preserving geometry. Light mode has a distinct paper palette with the same layout.

## Proof of fidelity

We reproduced the archived `quendoris_pliny_B_desktop_v02.png` in actual Chromium (1440 × 2778 px) by inlining the archived HTML/CSS/SVG directly into a browser document, rather than opening blocked file:// or localhost URLs. **Archived image vs rerendered original: 0 changed pixels, RGB MAE 0.0.** Comparing the archived B render with the new B v0.6 dark scene 01: same 1440×2778 dimensions, same key element positions and sizes, RGB MAE 0.0845 / 255; only 0.0908% of pixels differ by more than 4 channel units. The differences correspond to the small utility-label/footer modifications.

This is a controlled browser rendering test of the exact static source, not a claim that the public Nginx deployment was tested. Local HTTP navigation and caching still require review on Arch.

### Test results

- 8 Python tests (original file hashes, exact quote, source markup/data, markup balance, URL canonicalisation, byte-reproducible compilation, logo exact mask of 89,249 foreground pixels, negative accidental remote runtime dependencies).
- Node.js `--check` on the theme controller.
- Browser `set_content` test exercising selection of light and changing scene (no JavaScript exceptions).
- Four additional Chromium viewport/theme samples: light 1440, light 390, dark 390 and dark 320 px; no horizontal overflow, no runtime page exceptions. Real network navigation not covered.

## Local preview — no daemon, no SSH

```bash
python3 -m unittest discover -s tests -v
node --check src/atmosphere/b-atmosphere.js
python3 tools/build_reference_b.py --output preview
python3 -m http.server 8765 --bind 127.0.0.1 --directory preview
```

Use your desktop Firefox at:

- `http://127.0.0.1:8765/?qtheme=dark&qscene=1` — pixel-matching B reference mode
- `http://127.0.0.1:8765/?qtheme=light&qscene=1` — paper mode
- `http://127.0.0.1:8765/?qtheme=dark&qscene=2` — next night field

Press Ctrl+C to terminate the single foreground server. There is no installation, autostart, persistent daemon or modification of OS/network/browser settings.

## Optional production repository overlay, for review only

`tools/install_into_site.py` preflights a local checkout pinned at exact v0.4 main SHA `fa82eb5e39deea32f00b91d8b52a90c4a908ba6f`. A clean checkout and unmodified signed-paper PDF are mandatory. By default it is read-only. Only `--apply` writes five canonical HTML pages and exact reference assets to that checkout, then regenerates and validates the full dist SHA256SUMS. It **does not commit, push or deploy**.

```bash
python3 tools/install_into_site.py --repo /path/to/site
# after independent code and browser review, and only in a disposable clean worktree:
python3 tools/install_into_site.py --repo /path/to/site --apply
```

Source names in the repo remain clearly isolated under `src/reference/` and `src/atmosphere/`, the public copy is under `dist/assets/b-reference-*` and the historical PDF digest remains unchanged. The existing site's other unused assets remain untouched until explicit cleanup in a later release.

**Never redeploy previous v0.4 or v0.5:** the user experienced a failed v0.4 release despite successful file/HTTP checks; the currently recovered production v0.3 is kept unchanged. Visual sign-off and on-device integration checks must precede any new production release.
