import base64, pathlib, subprocess, sys
root=pathlib.Path(__file__).resolve().parent
files={name:base64.b64encode((root/name).read_bytes()).decode() for name in ('index.html','backend.py')}
remote=r'''import os,pathlib,base64,sys
os.umask(0o077)
base=pathlib.Path('/home/jeremiahai')
public=base/'www/nov-game/VVWK'
private=base/'.local/share/ancestale-vvwk'
for d in (public,private):
 if d.resolve()!=d: sys.exit('Symlink path refused')
 d.mkdir(parents=True,exist_ok=True)
private.chmod(0o700)
for target,encoded in [(public/'index.html',FILES['index.html']),(private/'backend.py',FILES['backend.py'])]:
 data=base64.b64decode(encoded)
 if target.is_symlink() or (target.exists() and target.read_bytes()!=data):sys.exit('Existing different file; review manually: '+str(target))
for target,encoded in [(public/'index.html',FILES['index.html']),(private/'backend.py',FILES['backend.py'])]:
 if not target.exists():
  with target.open('xb') as f:f.write(base64.b64decode(encoded))
 target.chmod(0o644 if target==public/'index.html' else 0o600)
public.chmod(0o755)
print('VVWK files installed. Existing HTTP service is unchanged. Integrate backend before enrolling.')
'''
code='FILES='+repr(files)+'\n'+remote
sys.exit(subprocess.run(['ssh','-T','jeremiahai-pi','python3 -'],input=code.encode()).returncode)
