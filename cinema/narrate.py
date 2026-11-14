#!/usr/bin/env python3
"""Generate reviewed dialogue offline on the T14, not on the Pi."""
import argparse, pathlib, json, hashlib, subprocess, tempfile, os, wave, shutil
from media import scan,inside,ROOT
p=argparse.ArgumentParser();p.add_argument('scenes',type=pathlib.Path);p.add_argument('output',type=pathlib.Path);p.add_argument('--piper',default='piper');p.add_argument('--root',type=pathlib.Path,default=ROOT);a=p.parse_args()
root=a.root.absolute();voices={i['id']:i for i in scan(root)['items'] if i['kind']=='voice' and i['ready']};out=a.output.absolute();out.mkdir(mode=0o700,parents=True,exist_ok=True);manifest={};exe=shutil.which(a.piper)
if not exe:raise SystemExit('Piper unavailable; install locally and run --help before generating')
for scene in json.loads(a.scenes.read_text()):
 text=scene['text'].strip();voice=voices.get(scene['voice']);
 if not text or len(text)>12000 or not voice:raise SystemExit('Invalid text or voice not reviewed')
 model=inside(root,voice['path']);config=inside(root,voice['config']);digest=hashlib.sha256((voice['sha256']+hashlib.sha256(config.read_bytes()).hexdigest()+text).encode()).hexdigest();name=digest+'.wav';dest=out/name
 if not dest.exists():
  fd,tmp=tempfile.mkstemp(suffix='.wav',dir=out);os.close(fd)
  try:
   subprocess.run([exe,'--model',str(model),'--config',str(config),'--output_file',tmp],input=text,text=True,check=True,timeout=180)
   with wave.open(tmp) as w:
    if not w.getnframes():raise ValueError('empty audio')
   os.replace(tmp,dest)
  finally:
   if os.path.exists(tmp):os.unlink(tmp)
 manifest[text]={'file':name,'voice':voice['id'],'credit':voice['credit'],'license':voice['license']}
fd,tmp=tempfile.mkstemp(dir=out);os.close(fd);pathlib.Path(tmp).write_text(json.dumps(manifest,ensure_ascii=False,indent=2));os.replace(tmp,out/'index.json');print('Generated or reused',len(manifest),'narration entries; local only')
