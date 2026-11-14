#!/usr/bin/env bash
# AncesTale public Git cleanup. Does not delete local project content.
set -Eeuo pipefail
ROOT='/home/we6jbo/Projects/AncesTale'
EXPECTED='https://github.com/we6jbo/AncesTale.git'
LOGICAL_BRANCH='master'
cd "$ROOT" 2>/dev/null || { echo "ERROR: Project directory does not exist: $ROOT" >&2; exit 1; }
[[ -d .git && ! -L .git ]] || { echo 'ERROR: No ordinary .git directory in project root.' >&2; exit 1; }
[[ "$(pwd -P)" == "$ROOT" ]] || { echo 'ERROR: Project directory is a symlink or not canonical.' >&2; exit 1; }
[[ "$(git rev-parse --show-toplevel)" == "$ROOT" ]] || { echo 'ERROR: Unexpected repository root.' >&2; exit 1; }
[[ "$(git branch --show-current)" == "$LOGICAL_BRANCH" ]] || { echo 'ERROR: Switch to master before cleanup.' >&2; exit 1; }
origin=$(git remote get-url origin)
[[ "$origin" == "$EXPECTED" || "$origin" == 'git@github.com:we6jbo/AncesTale.git' || "$origin" == 'https://github.com/we6jbo/AncesTale' ]] || { echo "ERROR: Unexpected origin: $origin" >&2; exit 1; }
[[ -z "$(git diff --cached --name-only)" ]] || { echo 'ERROR: Existing staged changes. Unstage or commit them separately before cleanup.' >&2; exit 1; }
command -v curl >/dev/null || { echo 'ERROR: curl is required.' >&2; exit 1; }
command -v python3 >/dev/null || { echo 'ERROR: python3 is required.' >&2; exit 1; }
if command -v t14-finish >/dev/null; then t14-finish deadline || true; fi
printf '\nLocal project files will NOT be deleted. This operation changes Git tracking and pushes a commit.\n'
# Verify the current local history matches remote, preventing a blind overwrite.
git fetch origin "$LOGICAL_BRANCH"
remote_commit=$(git rev-parse "origin/$LOGICAL_BRANCH")
local_commit=$(git rev-parse HEAD)
[[ "$remote_commit" == "$local_commit" ]] || { echo 'ERROR: Local master differs from origin/master. Review/merge first; no push attempted.' >&2; exit 1; }
# Enumerate tracked paths and apply a narrowly scoped denylist. This also catches
# binaries/backups regardless of their location; does not track local untracked files.
mapfile -d '' tracked < <(git ls-files -z)
bad=()
for path in "${tracked[@]}"; do
  case "$path" in
    build/*|build-*/*|cmake-build-*/*|.hvza-build/*|.qtcreator/*|.git/*|.ancestale-backups/*|.ancestale-private/*|.ancestale-logs/*|.hvza-scripts/*|lib/*|certificate/*|records/*|hvza_pinned_cert.h|*.backup.*|*.db|*.db-*|*.sqlite|*.sqlite3|*.pem|*.key|*.p12|*.pfx|*.sig|*.so|*.so.*|*.o|*.a|*.bin|*.exe|*.out|*.user|*.user.*|*.log|*.zip|*.tar|*.gz|*.7z|*.png|*.jpg|*.jpeg|*.pdf)
      bad+=("$path") ;;
  esac
done
printf '\nTracked files to REMOVE from the public branch: %d\n' "${#bad[@]}"
for p in "${bad[@]}"; do printf '  %s\n' "$p"; done
if ((${#bad[@]} == 0)); then echo 'No denied files are currently tracked.'; fi
# Extend existing ignore rules, do not reset them.
python3 - <<'PY'
from pathlib import Path
p=Path('.gitignore')
existing=p.read_text() if p.exists() else ''
marker='# AncesTale private/generated files (GitHub privacy cleanup)'
append='''# AncesTale private/generated files (GitHub privacy cleanup)
/build/
/build-*/
/cmake-build-*/
/.hvza-build/
/.qtcreator/
/.ancestale-backups/
/.ancestale-private/
/.ancestale-logs/
/.hvza-scripts/
/lib/
/certificate/
/records/
/hvza_pinned_cert.h
*.backup.*
*.db
*.db-*
*.sqlite
*.sqlite3
*.pem
*.key
*.p12
*.pfx
*.sig
*.so
*.so.*
*.o
*.a
*.bin
*.exe
*.out
*.user
*.user.*
*.log
*.zip
*.tar
*.gz
*.7z
*.png
*.jpg
*.jpeg
*.pdf
'''
if marker not in existing:
    with p.open('a') as f:
        if existing and not existing.endswith('\n'):f.write('\n')
        f.write('\n'+append)
PY
if ((${#bad[@]})); then
  printf '%s\0' "${bad[@]}" | xargs -0 -r git rm --cached --ignore-unmatch --
fi
git add -- .gitignore
printf '\nStaged changes (review before confirmation):\n'
git diff --cached --stat
# Make sure no unrelated changes are staged.
mapfile -d '' staged < <(git diff --cached --name-only -z)
for p in "${staged[@]}"; do
  [[ "$p" == '.gitignore' ]] && continue
  found=false
  for b in "${bad[@]}"; do [[ "$p" == "$b" ]] && { found=true; break; }; done
  [[ "$found" == true ]] || { echo "ERROR: Unexpected staged change: $p" >&2; exit 1; }
done
if ((${#staged[@]} == 0)); then echo 'Nothing to commit; will still verify remote.'; else
  echo
  read -r -p 'Type CLEANUP to commit and PUSH these removals to public GitHub: ' answer
  [[ "$answer" == CLEANUP ]] || { echo 'Cancelled. Local files preserved; proposed changes remain staged.'; exit 2; }
  git commit -m 'Remove private and generated AncesTale files from public tracking'
  git push origin "HEAD:refs/heads/$LOGICAL_BRANCH"
fi
printf '\nWaiting 60 seconds before public verification...\n'
sleep 60
# Fetch authoritative remote tree and ensure none of the denied paths are present.
git fetch origin "$LOGICAL_BRANCH"
mapfile -d '' remote_paths < <(git ls-tree -r -z --name-only "origin/$LOGICAL_BRANCH")
remaining=()
for path in "${remote_paths[@]}"; do
  case "$path" in
    build/*|build-*/*|cmake-build-*/*|.hvza-build/*|.qtcreator/*|.git/*|.ancestale-backups/*|.ancestale-private/*|.ancestale-logs/*|.hvza-scripts/*|lib/*|certificate/*|records/*|hvza_pinned_cert.h|*.backup.*|*.db|*.db-*|*.sqlite|*.sqlite3|*.pem|*.key|*.p12|*.pfx|*.sig|*.so|*.so.*|*.o|*.a|*.bin|*.exe|*.out|*.user|*.user.*|*.log|*.zip|*.tar|*.gz|*.7z|*.png|*.jpg|*.jpeg|*.pdf)
      remaining+=("$path") ;;
  esac
done
if ((${#remaining[@]})); then
  printf 'FAIL: %d disallowed paths remain in origin/master:\n' "${#remaining[@]}"
  printf '  %s\n' "${remaining[@]}"
  exit 3
fi
printf 'PASS: Remote master tree has no files matching the protected-file rules.\n'
# Check representative formerly tracked URLs directly. The Git tree is the
# authoritative complete check; raw URLs can be cached so query cache-busting.
for path in 'main.cpp' 'lib/story.db' 'lib/libhvza.so' 'lib/story.db.sig' 'certificate/hvza-public.pem' '.hvza-scripts/resign_ancestale.sh' 'build/Desktop_Debug/AncesTale'; do
  url="https://raw.githubusercontent.com/we6jbo/AncesTale/refs/heads/master/$path?audit=$(date +%s)"
  code=$(curl -L -sS -o /dev/null -w '%{http_code}' --max-time 20 -H 'Cache-Control: no-cache' "$url") || { echo "WARNING: Unable to verify URL: $path"; continue; }
  case "$path" in
    main.cpp) [[ "$code" == 200 ]] && echo 'PASS: main.cpp remains publicly accessible' || echo "WARNING: main.cpp returned HTTP $code";;
    *) [[ "$code" == 404 ]] && echo "PASS: $path returned HTTP 404" || { echo "WARNING: $path returned HTTP $code (possible cache or incomplete removal)"; exit 4; };;
  esac
done
printf '\nCURRENT-BRANCH CLEANUP COMPLETE.\n'
printf 'NOTE: This does NOT erase previously published Git history, forks, clones, caches, or downloads.\n'
printf 'If private data were exposed, plan a separate history rewrite and key/credential rotation.\n'
