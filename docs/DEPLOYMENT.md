# Quendoris B v0.6 — source-faithful deployment (2026-11-08)

The exact accepted B v0.2 source (original HTML, CSS, particles and logo) is
stored under `design/reference-b-v06/`; its generated five site pages and seven
assets reside in `dist/`. Dark scene 01 deliberately does not override B's
reference geometry. The recovered v0.3 web release remains available for
rollback. Preserve the historical scientific PDF digest.

The trusted Arch deployment workflow is unchanged except for the release label
`v0.6-<commit12>`; activate only from a pinned 40-character verified GitHub
commit. GitHub push/merge alone does not update the home server. On failure,
revert the current symlink to the previously read live release via
`tools/rollback_on_vm.sh`. A public GET of the actual homepage and B assets
must be checked, not just HTTP 200 or HEAD response.

---

# v0.4 upgrade: Pliny and the Quendoris atmospheric visual system

The original procedure below describes the historical v0.3 initial release. For a **v0.4** update, deploy a reviewed, merged, immutable GitHub commit using the existing trusted Arch workstation:

```bash
git clone https://github.com/quendoris/site.git
cd site
git checkout <full-approved-commit-sha>
python3 tools/check_site.py
python3 tools/check_atmosphere.py
sha256sum -c SHA256SUMS
bash tools/deploy_from_github.sh "$(git rev-parse HEAD)"
```

The upload still verifies every archived byte and published paper digest on both ends, stages in a root-owned directory, atomically changes the symlink, and verifies HTTP/HTTPS. The release label is `v0.4-<commit12>`. **Nothing deploys automatically from GitHub or a chat session.** The server is not accessible through the GitHub connector. Check the public URL from a phone after activation.

To rollback, supply `initial`, `v0.3-<commit12>`, or a known `v0.4-<commit12>` to `tools/rollback_on_vm.sh`. Do not delete previous releases.

---

# First publication on the HP server

## 1. GitHub is the independent public transport source

Create an **empty public** GitHub repository `quendoris/site` (do not auto-generate a README or license; both are included here). On Arch extract the release source archive and run:

```bash
cd /data/quendoris-site-github-v0.3
git init -b main
git add .
git commit -m 'site: initial verified Quendoris Research v0.3'
git remote add origin https://github.com/quendoris/site.git
git push -u origin main
```

If you have configured GitHub SSH authentication, you may instead use `git@github.com:quendoris/site.git` for the remote. Commit signing is optional; author authentication must be treated separately from hashes. The Git commit is the version identifier, not a Minisign signature.

Record the immutable full commit:

```bash
git rev-parse HEAD
```

## 2. Deploy from GitHub into VM

On Arch, from the same checkout:

```bash
bash tools/deploy_from_github.sh "$(git rev-parse HEAD)"
```

What the tool does:

1. Independently downloads the selected 40-character commit from **GitHub** to a temporary directory.
2. Validates checked-in SHA256SUMS, page links and the original PDF checksum.
3. Builds a self-contained tarball with source commit metadata and a fresh complete SHA256SUMS.
4. Uploads to the VM via SSH ProxyJump through the HP server, without storing the user's SSH private key on HP.
5. Validates the tarball digest and archive member safety, extracts into an unpublished root-owned staging directory, verifies **every file checksum** inside the VM.
6. Renames it to the unique release directory, atomically replaces `/srv/public-site/current`, and checks HTTP locally and HTTPS via the LAN proxy. If VM HTTP fails, the switch is reversed.

Files in `/srv/public-site/releases` are owned by root and readable by Nginx, but not writable by its worker. The guest has no Git nor default route, and the Arch signing keys remain local.

**Status:** manual, audited deployment; not an automatically signed complete-site release. A future independent host-side publisher must verify a site-signing key that is separately anchored, not trust a replacement public key arriving inside an unchecked tarball.

## 3. Verify what is live

On Arch:

```bash
curl --noproxy '*' --resolve quendoris1v7jcxzkgtd9geq7ran.duckdns.org:443:192.168.1.102 \
  -fsSI https://quendoris1v7jcxzkgtd9geq7ran.duckdns.org/
```

On HP host:

```bash
ssh hp 'sudo virsh domiflist public-web'
```

The site remains **LAN-tested** until router WAN port forwarding and ingress firewall rules are independently configured and externally verified. The site URL being in DNS is not proof of external reachability.

## 4. Rollback

A previous release is **retained** on the guest. To revert to the original technical landing page:

```bash
ssh -J hp -i ~/.ssh/id_ed25519_hp_research vmadmin@10.218.10.187 \
  'bash -s -- initial' < tools/rollback_on_vm.sh
```

Or pass an existing `v0.3-<commit12>` id instead of `initial`. The rollback updates the symlink atomically, then tests HTTP from inside the VM. No Git, restart, or network access is required.

Do not delete `/srv/public-site/releases/initial` until the entire end-to-end recovery procedure has been tested separately.
