#!/usr/bin/env bash
# Re-sign ONLY after the owner intentionally changes libhvza.so or story.db.
# Checking existing signatures in Qt does not use this script or any password.
set -Eeuo pipefail
PROJECT=/home/we6jbo/Projects/AncesTale
LIB="$PROJECT/lib"
PUB="$PROJECT/certificate/hvza-public.pem"
PIN_HEADER="$PROJECT/hvza_pinned_cert.h"
SIGN_USER=3R1xzBXK
PRIVATE=/home/3R1xzBXK/private
BACKUP=/opt/JSLib-dont-delete
[[ "$(id -un)" == we6jbo ]] || { echo 'Run as we6jbo' >&2; exit 1; }
[[ -s "$PUB" && -s "$PIN_HEADER" ]] || { echo 'Missing certificate or pinned checksum' >&2; exit 1; }
PIN=$(sed -n 's/^#define HVZA_PINNED_CERT_SHA256 "\([0-9a-f]\{64\}\)"$/\1/p' "$PIN_HEADER")
ACTUAL=$(sha256sum "$PUB" | awk '{print $1}')
[[ "$PIN" == "$ACTUAL" ]] || { echo 'ERROR: public certificate does not match pinned checksum; refusing to sign.' >&2; exit 1; }
[[ -s "$LIB/hvza-public.pem" ]] && cmp -s "$PUB" "$LIB/hvza-public.pem" || { echo 'ERROR: library public key is different; refusing to sign.' >&2; exit 1; }
[[ ! -e "$PROJECT/error-cert-does-not-match.txt" ]] || { echo 'Certificate tamper alert exists. Investigate before signing.' >&2; exit 1; }
for name in libhvza.so story.db; do
  file="$LIB/$name"
  [[ -s "$file" ]] || { echo "Missing $file" >&2; exit 1; }
  echo "Authorizing current $name with your private key. Enter its passphrase:"
  sudo install -m 600 -o "$SIGN_USER" -g "$SIGN_USER" "$file" "$PRIVATE/$name.sign-input"
  # Trap ensures staging input is deleted even if an incorrect passphrase stops the command.
  trap 'sudo rm -f "$PRIVATE/libhvza.so.sign-input" "$PRIVATE/story.db.sign-input" "$PRIVATE/libhvza.so.sig.tmp" "$PRIVATE/story.db.sig.tmp"' EXIT
  sudo -u "$SIGN_USER" openssl dgst -sha256 -sign "$PRIVATE/hvza-private.pem" \
      -out "$PRIVATE/$name.sig.tmp" "$PRIVATE/$name.sign-input"
  sudo install -m 600 -o we6jbo -g we6jbo "$PRIVATE/$name.sig.tmp" "$LIB/$name.sig.new"
  if ! openssl dgst -sha256 -verify "$PUB" -signature "$LIB/$name.sig.new" "$file"; then
    rm -f "$LIB/$name.sig.new"
    echo "Signature verification failed for $name" >&2; exit 1
  fi
  mv -f "$LIB/$name.sig.new" "$LIB/$name.sig"
  sudo rm -f "$PRIVATE/$name.sign-input" "$PRIVATE/$name.sig.tmp"
done
mkdir -p "$BACKUP"
cp -a "$LIB/libhvza.so" "$LIB/libhvza.so.sig" "$LIB/story.db" "$LIB/story.db.sig" "$LIB/hvza-public.pem" "$BACKUP/"
echo 'Signed files verified. Public verification remains passwordless.'
