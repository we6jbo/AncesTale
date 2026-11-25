#!/usr/bin/env python3
"""Regenerate hosted narration WAVs on the T14 (never on the Pi).

Reads the raw narration lines (voice/narration-lines.json), normalizes each
line for speech with speaktext.speak_text (strips TG codes, speaks dates in
full, numbers as words), writes the spoken lines back to the lines file
(idempotent), renders one Piper WAV per line into the output directory named
<sha256(wav)>.wav, and writes index.json LAST (atomically) mapping the exact
spoken text to its WAV. Deploy the output directory to /nov-game/narration/
with index.json last, never partial.

Usage:
  python3 voice/gen_narration.py [--lines voice/narration-lines.json] \
      [--out /tmp/narration2] [--piper ~/.local/piperenv/bin/piper] \
      [--model /home/we6jbo/1/voices/narrator/voice.onnx] \
      [--config /home/we6jbo/1/voices/narrator/voice.onnx.json]
"""
import argparse, hashlib, json, os, pathlib, subprocess, sys, tempfile, wave

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from speaktext import speak_text

CREDIT = 'Piper en_US-lessac-low (rhasspy/piper-voices), LAN use, rights review pending'
LICENSE = 'review pending'


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--lines', type=pathlib.Path, default=HERE / 'narration-lines.json')
    p.add_argument('--out', type=pathlib.Path, default=pathlib.Path('/tmp/narration2'))
    p.add_argument('--piper', default=os.path.expanduser('~/.local/piperenv/bin/piper'))
    p.add_argument('--model', default='/home/we6jbo/1/voices/narrator/voice.onnx')
    p.add_argument('--config', default='/home/we6jbo/1/voices/narrator/voice.onnx.json')
    a = p.parse_args()

    lines_path = a.lines.absolute()
    raw = json.loads(lines_path.read_text())
    spoken = [speak_text(x) for x in raw]
    if len(set(spoken)) != len(spoken):
        dupes = sorted({s for s in spoken if spoken.count(s) > 1})
        raise SystemExit('duplicate spoken lines after normalization: %r' % dupes[:3])

    out = a.out.absolute()
    out.mkdir(mode=0o700, parents=True, exist_ok=True)
    manifest = {}
    for text in spoken:
        if not text:
            continue
        fd, tmp = tempfile.mkstemp(suffix='.wav', dir=out)
        os.close(fd)
        try:
            subprocess.run([a.piper, '--model', a.model, '--config', a.config,
                            '--output_file', tmp], input=text, text=True, check=True, timeout=180)
            with wave.open(tmp) as w:
                if not w.getnframes():
                    raise ValueError('empty audio for: %r' % text[:60])
            data = pathlib.Path(tmp).read_bytes()
            name = hashlib.sha256(data).hexdigest() + '.wav'
            dest = out / name
            if not dest.exists():
                os.replace(tmp, dest)
            else:
                os.unlink(tmp)
        finally:
            if os.path.exists(tmp):
                os.unlink(tmp)
        manifest[text] = {'file': name, 'voice': 'narrator', 'credit': CREDIT, 'license': LICENSE}
        print('wav', name[:12], '<-', text[:70])

    fd, tmp = tempfile.mkstemp(dir=out)
    os.close(fd)
    pathlib.Path(tmp).write_text(json.dumps(manifest, ensure_ascii=False, indent=1))
    os.replace(tmp, out / 'index.json')

    fd, tmp = tempfile.mkstemp(dir=lines_path.parent)
    os.close(fd)
    pathlib.Path(tmp).write_text(json.dumps(spoken, ensure_ascii=False, indent=1))
    os.chmod(tmp, 0o600)
    os.replace(tmp, lines_path)
    print('Generated %d narration entries in %s; spoken lines written to %s'
          % (len(manifest), out, lines_path))


if __name__ == '__main__':
    main()
