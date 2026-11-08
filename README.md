# Quendoris Research — static site

Publication-ready static website for the Quendoris research archive. This repository holds the **site bytes and source-controlled deployment tooling**. Scientific papers retain independent provenance in [quendoris/papers](https://github.com/quendoris/papers) and algorithm implementations in their own research repositories.

- **Version:** v0.4 — Pliny / Quendoris Atmosphere redesign (v0.3 remains available for rollback).
- **No external runtime dependencies:** static HTML, CSS, SVG, PDF and a small local JavaScript for optional day/night theme and atmosphere controls; no remote JS, fonts, CDN or trackers.
- **Runtime:** Nginx serving a read-only, root-owned release directory on an isolated Debian VM.
- **Transport:** GitHub → trusted Arch workstation → SSH ProxyJump through HP → `public-web` VM.
- **Releases:** `/srv/public-site/releases/v0.4-<commit12>` (earlier v0.3 retained); active `/srv/public-site/current` symlink.

## Visual system and day/night behavior

The original 420×420 Quendoris mark is reproduced exactly; the homepage presents Pliny the Elder's authenticated Latin line from *Naturalis Historia* VII.6, with a quieter Russian translation and a direct source link. Site identity stays stable while the light field shifts between six scene variations for each day/night regime. The default clock mode uses local hours, not actual astronomical sunrise/sunset. The current visit is stable across navigation. No geolocation or telemetry is used.

The design assets are split between `src/design/` (readable source) and `dist/assets/` (verified release bytes); see [design and accessibility notes](src/design/README.md).

## Verify this release

```bash
python3 tools/check_site.py
python3 tools/check_atmosphere.py
sha256sum -c SHA256SUMS
```

The PDF at `dist/publications/constructive-million/v1.0.0/article.pdf` must have SHA-256:

`6c4a941a71695cd96d7445ad6de601aeea5cbf59477812a9b0bfab899d215e47`

The original PDF is separately signed through the papers publication pipeline. **This site ZIP/repository is not itself a Minisign-signed site release.** Pin the exact Git commit when deploying; that identifies the code and bytes but does not independently attest author identity without a trusted signature or other anchor.

## Deploy the exact GitHub revision (trusted Arch workstation only)

From the trusted Arch Linux workstation (requires `git`, `ssh`, `scp`, `tar`, `python3`):

```bash
bash tools/deploy_from_github.sh "$(git rev-parse HEAD)"
```

The script **clones GitHub by a full commit SHA**, checks every checked-in site file against the SHA-256 manifest and the PDF digest, uploads only a tar archive via `ssh -J hp` and verifies it again inside the guest before an atomic symlink switch. It keeps the previous release for rollback and tests HTTPS via the HP proxy after activation. It neither runs Git on HP nor connects the guest to the Internet.

Assumptions (from deployed infrastructure):

- Arch `~/.ssh/config` contains the `hp` alias for host `192.168.1.102`.
- Arch SSH key: `~/.ssh/id_ed25519_hp_research`.
- Guest: `vmadmin@10.218.10.187`, reachable via `-J hp`.
- `vmadmin` has `sudo -n` privileges for initial deployment. **This is temporary bootstrap privilege; reduce it after setting up a dedicated narrowly-scoped publisher.**
- Guest Nginx root: `/srv/public-site/current`; listens on `10.218.10.187:80`.
- Host Nginx handles public TLS on `192.168.1.102:443`.

Do not run GitHub Actions as a push-based publisher into home infrastructure. Keep management SSH and private signing keys outside public Internet exposure. See [docs/DEPLOYMENT.md](docs/DEPLOYMENT.md) for the publication and rollback steps.

## Licensing

Original site design, explanatory text and figures: **CC BY 4.0** (`LICENSE-CONTENT`).
Software/scripts/CI: **Apache-2.0** (`LICENSE-CODE`).
Embedded paper: its own author attribution and **CC BY 4.0**, unchanged. Third-party sources retain their original rights.
