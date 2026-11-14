#!/usr/bin/env python3
import base64,pathlib,subprocess,sys
root=pathlib.Path(__file__).resolve().parent
files={n:base64.b64encode((root/n).read_bytes()).decode() for n in ('backend.py','index.html','presence.js')}
remote=r'''import os,pathlib,base64,sys,datetime,shutil,tempfile,subprocess
os.umask(0o077)
base=pathlib.Path('/home/jeremiahai'); private=base/'.local/share/ancestale-vvwk'; public=base/'www/nov-game/VVWK'; game=public.parent/'index.html'
if pathlib.Path.home()!=base:sys.exit('Wrong SSH account')
for p in (private,public,private/'backend.py',private/'server.py',private/'enrollments.json',public/'index.html'):
 if not p.exists() or p.resolve()!=p:sys.exit('Missing or unsafe path: '+str(p))
if 'TTL=90*86400' not in (private/'backend.py').read_text() and 'Closed enrollment.' not in (private/'backend.py').read_text():sys.exit('Unexpected backend; review before replacing')
compile(base64.b64decode(FILES['backend.py']), 'backend.py','exec')
backup=private/('backup-player-'+datetime.datetime.now().strftime('%Y%m%d-%H%M%S-%f'));backup.mkdir(mode=0o700)
changes=[(private/'backend.py',base64.b64decode(FILES['backend.py']),0o600),(public/'index.html',base64.b64decode(FILES['index.html']),0o644),(public/'presence.js',base64.b64decode(FILES['presence.js']),0o644)]
# Only the existing game entry page is patched; other actual game pages need the same script tag.
if game.is_file() and game.resolve()==game:
 raw=game.read_bytes();tag=b'<script defer src="/nov-game/VVWK/presence.js"></script>'
 if tag not in raw:
  if b'</body>' in raw:raw=raw.replace(b'</body>',tag+b'\n</body>',1)
  else:raw+=b'\n'+tag+b'\n'
  changes.append((game,raw,game.stat().st_mode&0o777))
else:print('Game index.html not found; add presence script to the actual game page manually.')
for i,(p,data,mode) in enumerate(changes):
 if p.resolve()!=p:sys.exit('Unsafe path: '+str(p))
 if p.exists():shutil.copy2(p,backup/str(i))
for p,data,mode in changes:
 fd,tmp=tempfile.mkstemp(dir=p.parent,prefix='.vvwk-');os.fchmod(fd,mode)
 with os.fdopen(fd,'wb') as f:f.write(data);f.flush();os.fsync(f.fileno())
 os.replace(tmp,p)
print('Files installed; existing enrollments untouched. Backup:',backup)
print('RESTART the existing VVWK server now; old process still accepts enrollment until restarted.')
'''
code='FILES='+repr(files)+'\n'+remote
sys.exit(subprocess.run(['ssh','-T','jeremiahai-pi','python3 -'],input=code.encode()).returncode)
