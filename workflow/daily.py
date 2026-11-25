#!/usr/bin/env python3
"""Guarded initial deployment; no AI, mail, Git or privilege changes."""
import argparse,base64,datetime,hashlib,json,os,pathlib,subprocess,sys,time,urllib.request
from zoneinfo import ZoneInfo
ROOT=pathlib.Path('/home/we6jbo/Projects/AncesTale')
PRIVATE=pathlib.Path.home()/'.ancestale'/ 'daily'
ZONE=ZoneInfo('America/Los_Angeles')
GAME='http://192.168.5.215:8081/nov-game/'
def main():
 p=argparse.ArgumentParser();p.add_argument('action',choices=['check','deploy']);p.add_argument('--apply',action='store_true');p.add_argument('--alpha',action='store_true');a=p.parse_args(); now=datetime.datetime.now(ZONE); day=now.date().isoformat()
 print('Pacific date:',day, 'time:',now.strftime('%H:%M:%S'))
 folder=PRIVATE/day; page=folder/'index.html'; review=folder/'review.json'
 for f in (ROOT/'lib/story.db',ROOT/'Music/index.csv',ROOT/'voice-clips/index.csv',ROOT/'voice/defaults.json',pathlib.Path.home()/'1/index.json'):
  print(('FOUND ' if f.is_file() else 'MISSING ')+str(f))
 for folder_ in (ROOT,pathlib.Path.home()/'1'):
  print('Film assignments:',[str(x) for x in folder_.glob('family_film_assignments.xlsx')])
 print('Initial page:',page,'present' if page.is_file() else 'missing');print('Review:',review,'present' if review.is_file() else 'missing')
 if a.action=='check':return
 if not a.apply or (day<'2026-11-21' and not(day=='2026-11-15' and a.alpha)):sys.exit('Not authorized: use explicit --apply and --alpha for Nov 15 test.')
 if not page.is_file() or not review.is_file() or page.resolve()!=page or review.resolve()!=review:sys.exit('Missing or unsafe reviewed page')
 raw=page.read_bytes(); digest=hashlib.sha256(raw).hexdigest(); meta=json.loads(review.read_text());
 if meta.get('sha256')!=digest or meta.get('date')!=day or meta.get('approved_for_lan') is not True:sys.exit('Owner review missing or content changed')
 if len(raw)>4_000_000:sys.exit('Page too large; use separate reviewed assets')
 for name in ('story.db','libhvza.so'):
  subprocess.run(['openssl','dgst','-sha256','-verify',str(ROOT/'lib/hvza-public.pem'),'-signature',str(ROOT/('lib/'+name+'.sig')),str(ROOT/('lib/'+name))],check=True,timeout=15)
 if hashlib.sha256((ROOT/'lib/hvza-public.pem').read_bytes()).hexdigest()!='ec4e4af5e84088f25fddbbd7098f362af2c67c299072ba9eca74166ffd057f5b':sys.exit('Certificate pin mismatch')
 code='PAYLOAD='+repr(base64.b64encode(raw).decode())+'\n'+"""import pathlib,os,sys,base64,tempfile,datetime,hashlib
base=pathlib.Path('/home/jeremiahai'); target=base/'www/nov-game/index.html'; backup=base/'.local/share/ancestale-vvwk'
if pathlib.Path.home()!=base or not target.is_file() or target.resolve()!=target or not backup.is_dir() or backup.resolve()!=backup:sys.exit('Unsafe remote path')
old=target.read_bytes(); new=base64.b64decode(PAYLOAD)
if old!=new:
 b=backup/('before-daily-'+datetime.datetime.now().strftime('%Y%m%d-%H%M%S-%f')+'.html')
 fd=os.open(b,os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600)
 with os.fdopen(fd,'wb') as f:f.write(old);f.flush();os.fsync(f.fileno())
 fd,t=tempfile.mkstemp(dir=target.parent)
 try:
  with os.fdopen(fd,'wb') as f:f.write(new);f.flush();os.fsync(f.fileno())
  os.chmod(t,0o644)
  if target.read_bytes()!=old:sys.exit('Concurrent update')
  os.replace(t,target)
 finally:
  if os.path.exists(t):os.unlink(t)
print(hashlib.sha256(target.read_bytes()).hexdigest())
"""
 r=subprocess.run(['ssh','-T','-o','BatchMode=yes','-o','ConnectTimeout=8','jeremiahai-pi','python3 -'],input=code,text=True,capture_output=True,timeout=45,check=True)
 if r.stdout.strip().splitlines()[-1]!=digest:sys.exit('Remote hash mismatch')
 with urllib.request.urlopen(GAME+'?verify='+str(time.time_ns()),timeout=10) as response: actual=response.read(4_000_001)
 if hashlib.sha256(actual).hexdigest()!=digest:sys.exit('HTTP content mismatch; investigate before inviting')
 print('Verified initial page:',GAME, 'Check root launch in player browser before inviting. No email sent.')
if __name__=='__main__':main()
