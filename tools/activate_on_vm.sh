#!/usr/bin/env bash
# Executed by deploy_from_github.sh on VM via SSH. No Git, Internet or private key on VM.
set -euo pipefail

RELEASE_ID="${1:?release id required}"
EXPECTED_SHA="${2:?tar sha required}"
TAR_PATH="${3:?uploaded tar path required}"

[[ "$RELEASE_ID" =~ ^v0\.(3|4)-[0-9a-f]{12}$ ]] || { echo 'Invalid release id' >&2; exit 2; }
[[ "$EXPECTED_SHA" =~ ^[0-9a-f]{64}$ ]] || { echo 'Invalid tar checksum' >&2; exit 2; }
[[ "$TAR_PATH" =~ ^/tmp/quendoris-site-[A-Za-z0-9]+\.tar$ ]] || { echo 'Unexpected tar path' >&2; exit 2; }
[[ -f "$TAR_PATH" && ! -L "$TAR_PATH" ]] || { echo 'Missing tar archive' >&2; exit 2; }

printf '%s  %s\n' "$EXPECTED_SHA" "$TAR_PATH" | sha256sum -c --status

# Independently reject links, devices, absolute/traversal paths, duplicate entries,
# and oversized archives before asking root to extract anything.
python3 - "$TAR_PATH" <<'PY'
from pathlib import PurePosixPath
import sys, tarfile
p = sys.argv[1]
names=set()
size=0
with tarfile.open(p, 'r:') as t:
    members=t.getmembers()
    if not (10 <= len(members) <= 200):
        raise SystemExit('Invalid number of tar entries')
    for m in members:
        raw=m.name
        path=PurePosixPath(raw)
        if raw.startswith('/') or '..' in path.parts or not (m.isfile() or m.isdir()):
            raise SystemExit('Forbidden tar member: '+raw)
        normalized='/'.join(x for x in path.parts if x not in ('.', ''))
        if normalized in names and normalized:
            raise SystemExit('Duplicate tar member: '+raw)
        names.add(normalized)
        size+=m.size
    if size > 60*1024*1024 or 'index.html' not in names or 'SHA256SUMS' not in names:
        raise SystemExit('Invalid archive content or total size')
PY

ROOT=/srv/public-site
RELEASE="$ROOT/releases/$RELEASE_ID"
sudo -n install -d -o root -g root -m 0755 "$ROOT" "$ROOT/releases"
if sudo -n test -e "$RELEASE"; then
    echo "Release already exists; refusing overwrite: $RELEASE" >&2
    exit 3
fi
STAGING="$(sudo -n mktemp -d "$ROOT/releases/.staging-${RELEASE_ID}.XXXXXXXX")"
cleanup() { sudo -n rm -rf -- "$STAGING" 2>/dev/null || :; }
trap cleanup EXIT
sudo -n tar -xf "$TAR_PATH" -C "$STAGING" --no-same-owner --no-same-permissions
sudo -n sh -c 'cd "$1" && sha256sum -c SHA256SUMS' sh "$STAGING"
sudo -n test -f "$STAGING/index.html"
sudo -n find "$STAGING" -type d -exec chmod 0755 '{}' +
sudo -n find "$STAGING" -type f -exec chmod 0644 '{}' +
sudo -n chown -R root:root "$STAGING"
sudo -n mv -T -- "$STAGING" "$RELEASE"
STAGING=''
trap - EXIT

if ! sudo -n test -L "$ROOT/current"; then
    echo 'Expected existing current symlink missing; release staged but not activated' >&2
    exit 4
fi
PREVIOUS="$(sudo -n readlink "$ROOT/current")"
NEWLINK="$ROOT/.current-${RELEASE_ID}-$$"
sudo -n ln -s "releases/$RELEASE_ID" "$NEWLINK"
sudo -n mv -Tf -- "$NEWLINK" "$ROOT/current"
if ! curl --noproxy '*' -fsS --connect-timeout 2 --max-time 7 -o /dev/null \
    http://10.218.10.187/; then
    echo 'HTTP check failed, rolling back symlink' >&2
    ROLLBACK="$ROOT/.rollback-${RELEASE_ID}-$$"
    sudo -n ln -s "$PREVIOUS" "$ROLLBACK"
    sudo -n mv -Tf "$ROLLBACK" "$ROOT/current"
    exit 5
fi
rm -f -- "$TAR_PATH"
echo "ACTIVE_RELEASE=$RELEASE_ID"
echo "SOURCE_COMMIT=$(sudo -n cat "$RELEASE/SOURCE_COMMIT")"
echo "PREVIOUS_RELEASE=$PREVIOUS"
echo 'GUEST_HTTP_OK=1'
