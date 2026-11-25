# AncesTale session runbook — created 2026-11-15 (for repeatability, esp. Sat 2026-11-21)

The Pi is NOT deconstructed; everything below is redeployable from T14 project sources.
Pi facts: `pi@192.168.5.215` SSH key `~/.ssh/t14_to_pi`; `pi` has passwordless sudo.
Port 8081 vhost = `/home/lockedgames/www` (only `/nov-game/` is proxied to 8080, docroot `/home/jeremiahai/www`).
Web: `http://192.168.5.215:8081/` launch page (iframe -> /nov-game/), game at `/nov-game/`, quiz `/quiz.html`, zork `/zork.html`.

## Source of truth on T14 (all deployed files live here)
- `site/nov-game-index.html` — game page (sha256 abbde4e2... at creation)
- `site/quiz.html`, `site/zork.html` — root-level pages served from /home/lockedgames/www
- `session/web/scene3d.js` (Three.js journey world; needs `three.module.js` r160 MIT alongside)
- `session/web/zorklike.js`, `session/web/voice-setup.js`, `session/web/narration.js`, `session/web/session.js`, `session/web/cinema.js`
- `session/sessionctl.py` — `prepare --date --index --file` (hardcodes 15:20 PT start, 10-min window, PD/CC0+reviewed only)
- `Music/` catalog + `annotations-20261114.json`; voice clips `voice-clips/` + `voice/clips.json` + `voice/defaults.json`
- `.session-local/` — private state (ancestale-session.json, controller.log, blog.json); never commit

## Deploy recipe (as done 2026-11-15)
1. Game dir: `ssh pi` then `sudo install -o jeremiahai -g jeremiahai -m 644 <local> /home/jeremiahai/www/nov-game/<name>`; backup first: `sudo cp -p index.html index.html.pre-<tag>-20261115.bak`. State JSON placed last, atomic (tmp+mv).
2. Root pages: `sudo install -o lockedgames -g lockedgames -m 644 <local> /home/lockedgames/www/<name>`
3. Transfer files via `ssh ... "cat > /tmp/x.new" < local` (scp/sftp was flaky); keep SSH connections sparse (MaxStartups throttling caused refused bursts).
4. Verify: `curl -s -o /dev/null -w "%{http_code}" http://192.168.5.215:8081/<path>` for every asset; compare sha256 T14 vs served.

## Session flow (per begin.md / session/VIBE.md)
- prepare state -> deploy session.js + chime + state + page tag -> arm browser ("Enable session sound") -> play at start -> draft at +2min -> (end chime was REMOVED from session.js 2026-11-15, backup session.js.pre-noend-20261115.bak)
- invites: `python3 invitations/invite.py send --game-ready --entry-root` (root verified as launch page); one batch/Pacific day; ledger consumed 2026-11-15
- quiz at end auto-redirects /nov-game/ -> /quiz.html -> (both activities correct) /zork.html
- "Explore the next branch" button on all pages except root links to `/`

## 2026-11-21 (Saturday) specifics
- Nov 21-29 recovery window: hold `python3 fallback/controller.py lease` before site work, renew every 60 s; sessions 09:00-15:30 PT
- prepare >=20 scenes, >=30 narrated lines, >=5 activities, >=3 destinations, film + alternative; 9 daily backup chapters
- media: fill `/home/we6jbo/1/index.json` (title/creator/source_url/license/license_url/credit/rights_notes) and set approved_for_lan/ready only after rights review; deploy reviewed MP4s to /nov-game/movies/<id>.mp4; voices into /home/we6jbo/1/voices/<name>/ (voice.onnx + voice.onnx.json + MODEL_CARD, same revision)
- Piper: durable venv `~/.local/piperenv` (`python3 -m venv ~/.local/piperenv && ~/.local/piperenv/bin/pip install piper-tts`); generate on T14 only: `~/.local/piperenv/bin/piper -m MODEL -c CONFIG -f OUT.wav` or `python3 cinema/narrate.py SCENES.json OUT`; deploy WAVs+index.json to /nov-game/narration/ (never replace active audio with incomplete index)
- Tested 2026-11-15: en_US-lessac-low (rhasspy/piper-voices) staged in /home/we6jbo/1/voices/narrator/ (voice.onnx, voice.onnx.json, MODEL_CARD.txt); approved_for_lan remains false pending owner rights review
- Hosted narration: 63 WAVs served at /nov-game/narration/ (index.json maps exact spoken text -> <sha256(wav)>.wav). Regenerate/extend: edit lines, run `python3 /tmp/gen_narration.py` (reads SCENES from site/nov-game-index.html + ZSTR from session/web/zorklike.js + quiz strings; writes voice/narration-lines.json + /tmp/narration2), then tar-deploy /tmp/narration2 to /nov-game/narration/ (index.json LAST, never partial)
- Pages speaking hosted narration: /nov-game/ (scenes + end via AncesTaleVoice.scene), /quiz.html (intro/labels/verdicts), /zork.html (every line via out()); all load /nov-game/narration.js. Zork is button-driven (no textbox) via zbtns in zorklike.js
- Chromebook needs NOTHING installed: WebGL2 renders scene3d.js, WAVs/mp3s play via <audio>; LAN only
- Git: nothing commits/pushes before 2026-11-18 Pacific (test4 marker contract)

## Backups on Pi (nov-game/)
index.html.pre-alpha-20261114.bak, .pre-alpha2-*.bak, .pre-nextbranch-20261114.bak, .pre-session-20261115.bak, .pre-voicesetup-20261115.bak, .pre-orev-20261115.bak, .pre-activities-20261115.bak, .pre-3d-20261115.bak, .pre-journey-20261115.bak, .pre-walk-20261115.bak, .pre-fullscreen-20261115.bak, .pre-hint-20261115.bak, .pre-topleft-20261115.bak; session.js.pre-noend-20261115.bak
