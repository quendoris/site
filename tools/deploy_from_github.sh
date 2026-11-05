#!/usr/bin/env bash
# On trusted Arch workstation: fetch a particular GitHub commit and upload the exact static release.
set -euo pipefail

printf '\033[1;34m===== NEW ATOM — GITHUB PINNED SITE DEPLOY =====\033[0m\n'

COMMIT="${1:?Usage: tools/deploy_from_github.sh <40-hex Git commit> [Git repository URL]}"
REPO_URL="${2:-https://github.com/quendoris/site.git}"
SSH_KEY="${SSH_KEY:-$HOME/.ssh/id_ed25519_hp_research}"
VM_SSH="${VM_SSH:-vmadmin@10.218.10.187}"
SSH_JUMP="${SSH_JUMP:-hp}"
[[ "$COMMIT" =~ ^[0-9a-f]{40}$ ]] || { echo 'A full, immutable 40-character Git commit is required' >&2; exit 2; }
[[ -f "$SSH_KEY" ]] || { echo "Missing local SSH key: $SSH_KEY" >&2; exit 2; }

WORK="$(mktemp -d)"
cleanup() { rm -rf -- "$WORK"; }
trap cleanup EXIT

echo '=== FETCH EXACT GITHUB REVISION ==='
git clone -q --no-checkout "$REPO_URL" "$WORK/source"
git -C "$WORK/source" checkout -q --detach "$COMMIT"
FOUND="$(git -C "$WORK/source" rev-parse HEAD)"
[[ "$FOUND" == "$COMMIT" ]] || { echo 'Commit verification mismatch' >&2; exit 2; }

# Validate file integrity against the pinned Git tree.
echo '=== VERIFY SITE MANIFEST AND LINKS ==='
python3 "$WORK/source/tools/check_site.py" --root "$WORK/source"
(cd "$WORK/source" && sha256sum -c SHA256SUMS)

RELEASE_ID="v0.3-${COMMIT:0:12}"
mkdir -p "$WORK/release"
cp -a "$WORK/source/dist/." "$WORK/release/"
printf '%s\n' "$COMMIT" > "$WORK/release/SOURCE_COMMIT"
(
  cd "$WORK/release"
  find . -type f ! -name SHA256SUMS -print0 | LC_ALL=C sort -z | xargs -0 sha256sum > SHA256SUMS
  sha256sum -c SHA256SUMS
)
tar -cf "$WORK/release.tar" -C "$WORK/release" .
TAR_SHA="$(sha256sum "$WORK/release.tar" | cut -d' ' -f1)"

# The SSH jump uses the existing `Host hp` entry. Private key remains on Arch.
echo '=== RESERVE PRIVATE VM TEMP FILE ==='
REMOTE_TMP="$(ssh -J "$SSH_JUMP" -i "$SSH_KEY" "$VM_SSH" \
  'mktemp /tmp/quendoris-site-XXXXXXXX.tar')"
[[ "$REMOTE_TMP" =~ ^/tmp/quendoris-site-[A-Za-z0-9]+\.tar$ ]] || {
  echo "Unexpected remote temporary path: $REMOTE_TMP" >&2
  exit 3
}
echo '=== UPLOAD THROUGH SSH PROXYJUMP ==='
scp -q -J "$SSH_JUMP" -i "$SSH_KEY" "$WORK/release.tar" "$VM_SSH:$REMOTE_TMP"

echo '=== VERIFY AND ACTIVATE ROOT-OWNED RELEASE INSIDE VM ==='
ssh -J "$SSH_JUMP" -i "$SSH_KEY" "$VM_SSH" \
  "bash -s -- '$RELEASE_ID' '$TAR_SHA' '$REMOTE_TMP'" \
  < "$WORK/source/tools/activate_on_vm.sh"

echo '=== VERIFY FINAL HTTPS THROUGH HP (LAN) ==='
DOMAIN='quendoris1v7jcxzkgtd9geq7ran.duckdns.org'
curl --noproxy '*' --resolve "$DOMAIN:443:192.168.1.102" \
    --connect-timeout 4 --max-time 12 -fsS \
    -o /dev/null -w 'HTTPS status: %{http_code}\n' "https://$DOMAIN/"
echo "DEPLOYED_GIT_COMMIT=$COMMIT"
echo "DEPLOYED_RELEASE=$RELEASE_ID"
