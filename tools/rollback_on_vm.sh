#!/usr/bin/env bash
# Invoke from Arch over SSH ProxyJump after choosing a known previously deployed version.
set -euo pipefail
TARGET="${1:?Usage: rollback_on_vm.sh initial|v0.3-<commit12>|v0.4-<commit12>}"
[[ "$TARGET" == initial || "$TARGET" =~ ^v0\.(3|4)-[0-9a-f]{12}$ ]] || { echo 'Invalid release id' >&2; exit 2; }
ROOT=/srv/public-site
DIR="$ROOT/releases/$TARGET"
sudo -n test -d "$DIR" || { echo 'Unknown release' >&2; exit 3; }
sudo -n test -f "$DIR/index.html" || { echo 'Missing index.html' >&2; exit 3; }
NEXT="$ROOT/.rollback-${TARGET}-$$"
sudo -n ln -s "releases/$TARGET" "$NEXT"
sudo -n mv -Tf "$NEXT" "$ROOT/current"
curl --noproxy '*' -fsS --connect-timeout 2 --max-time 7 -o /dev/null \
  http://10.218.10.187/
echo "RESTORED_RELEASE=$TARGET"
