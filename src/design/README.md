# Quendoris Atmosphere v0.4 — production site design

**Status:** proposed exact-commit static release; deployed site remains unchanged until a trusted Arch workstation runs the existing SSH deployment command.

## Design contract

- Exact original Quendoris **420×420** angular mark: eyes and lower notch preserved (source `src/design/quendoris-mark.svg`, distributed at `dist/assets/quendoris-mark.svg`). Pixel-equivalence checked against the user-provided original: 89,249 foreground pixels, 0 differences.
- Home headline is the unabridged and sourced Latin quotation from **Pliny the Elder**, `Naturalis Historia` VII.6 (first century CE); the Russian translation is subordinate and Quendoris's own statement follows the quotation.
- Day/night: local device time, **07:00–18:59 light; 19:00–06:59 dark**. These are clock hours, not astronomical sunrise/sunset; no geolocation used.
- A new browser session rotates through six *restrained* atmosphere states in each regime. Pages visited in the same tab retain one field; refresh does not scramble it.
- Explicit modes: local clock, device theme, always light, always dark. Manual choice persists only on the current device. The share control pins the number of the scene in a URL.
- No analytics, cookies, external fonts/CDNs/APIs or background services. On disabled JavaScript, semantic text and links remain visible, with a CSS device-theme fallback. LocalStorage/sessionStorage are used solely for user visual preferences and the scene counter.
- The five canonical HTML routes and the independently signed article PDF path stay intact.

## Code split

- `dist/` is the exact static public release tree, directly served by Nginx. It does **not** include the experimental 12-scene gallery or any `noindex` markers.
- `dist/assets/site.css` remains the archived v0.3 base; `dist/assets/atmosphere.css` supplies the v0.4 override, including mobile and reduced-motion styles.
- `dist/assets/atmosphere.js` implements deterministic field states and local preferences.
- `src/design/` has byte-identical readable copies of the mark, CSS and JS; verification requires that these copies match distributed files.
- `tools/check_site.py` validates the exact whole `dist/` inventory and links, including the archived PDF digest; `tools/check_atmosphere.py` checks this visual-language upgrade.
- `.github/workflows/site-check.yml` checks repository changes; it does **not** deploy into home infrastructure.

## Run locally

```bash
python3 tools/check_site.py
python3 tools/check_atmosphere.py
sha256sum -c SHA256SUMS
python3 -m http.server 8765 --bind 127.0.0.1 --directory dist
```

Then open http://127.0.0.1:8765/ in your browser. Test both http://127.0.0.1:8765/?qscene=1&qtheme=light and http://127.0.0.1:8765/?qscene=1&qtheme=dark. The public site uses fixed canonical links; local development tests do not constitute a public deployment.

## Trusted release process

On the **trusted Arch workstation** (with configured SSH `hp`, correct SSH key and access to the VM):

```bash
git clone https://github.com/quendoris/site.git
cd site
git checkout <exact-merged-commit-sha>
python3 tools/check_site.py
python3 tools/check_atmosphere.py
bash tools/deploy_from_github.sh "$(git rev-parse HEAD)"
```

The deployment utility independently clones the exact Git revision, audits the release, uploads through the existing ProxyJump, validates on the VM, atomically changes the `current` symlink and checks local HTTPS. Older releases remain available for rollback. No background auto-publisher or remote signing key is introduced.

**Warning:** repository commits alone do *not* update the physical web server. Never claim the public site is updated without the VM activation and external phone/HTTPS checks. See [deployment instructions](../../docs/DEPLOYMENT.md).
