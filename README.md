# Quendoris Research — static site

Publication-ready static website for the Quendoris research archive. This repository holds the **site bytes and source-controlled deployment tooling**. Scientific papers retain independent provenance in [quendoris/papers](https://github.com/quendoris/papers) and algorithm implementations in their own research repositories.

- **Version:** v0.3 — initial site release candidate.
- **No runtime dependencies:** HTML, CSS, SVG, PDF; no external JS/fonts/CDN/trackers.
- **Runtime:** Nginx serving a read-only, root-owned release directory on an isolated Debian VM.
- **Transport:** GitHub → trusted Arch workstation → SSH ProxyJump through HP → `public-web` VM.
- **Releases:** `/srv/public-site/releases/v0.3-<commit12>`; active `/srv/public-site/current` symlink.

## Verify this release

```bash
python3 tools/check_site.py
sha256sum -c SHA256SUMS
```

The PDF at `dist/publications/constructive-million/v1.0.0/article.pdf` must have SHA-256:

`6c4a941a71695cd96d7445ad6de601aeea5cbf59477812a9b0bfab899d215e47`

The original PDF is separately signed through the papers publication pipeline. **This site ZIP/repository is not itself a Minisign-signed site release.** Pin the exact Git commit when deploying; that identifies the code and bytes but does not independently attest author identity without a trusted signature or other anchor.

## Deploy the exact GitHub revision

From the trusted Arch Linux workstation (requires `git`, `ssh`, `scp`, `tar`, `python3`):

```bash
bash tools/deploy_from_github.sh "$(git rev-parse HEAD)"
```

The script **clones GitHub by a full commit SHA**, checks all 12 site files and the PDF digest, uploads only a tar archive via `ssh -J hp` and verifies it again inside the guest before an atomic symlink switch. It keeps the previous release for rollback and tests HTTPS via the HP proxy after activation. It neither runs Git on HP nor connects the guest to the Internet.

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
