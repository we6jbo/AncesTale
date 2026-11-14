#!/usr/bin/env bash
set -euo pipefail
[[ $(id -un) == we6jbo ]] || { echo 'Run as we6jbo, without sudo.' >&2; exit 1; }
cd /home/we6jbo/Projects/AncesTale
exec python3 invitations/invite.py setup
