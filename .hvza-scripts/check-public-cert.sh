#!/usr/bin/env bash
set -euo pipefail
CERT='/home/we6jbo/Projects/AncesTale/certificate/hvza-public.pem'
LIBCERT='/home/we6jbo/Projects/AncesTale/lib/hvza-public.pem'
FLAG='/home/we6jbo/Projects/AncesTale/error-cert-does-not-match.txt'
PIN='ec4e4af5e84088f25fddbbd7098f362af2c67c299072ba9eca74166ffd057f5b'
if [[ ! -f "$CERT" || ! -f "$LIBCERT" ]] ||    [[ "$(sha256sum "$CERT" | awk '{print $1}')" != "$PIN" ]] ||    [[ "$(sha256sum "$LIBCERT" | awk '{print $1}')" != "$PIN" ]]; then
  printf 'ERROR: public certificate checksum differs from pinned value. Inspect trusted backup and verify source.\n' > "$FLAG"
  exit 1
fi
rm -f "$FLAG"
