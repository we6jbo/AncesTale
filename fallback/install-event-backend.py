#!/usr/bin/env python3
"""Optional event-log backend update. Owner runs manually; no service restart."""
import argparse,base64,pathlib,subprocess,sys
p=argparse.ArgumentParser();p.add_argument('--approved',action='store_true');a=p.parse_args()
if not a.approved:p.error('Explicit owner --approved required')
root=pathlib.Path(__file__).resolve().parents[1]
if root!=pathlib.Path('/home/we6jbo/Projects/AncesTale'):sys.exit('Wrong project root')
code='PAYLOAD='+repr(base64.b64encode((root/'vvwk/backend.py').read_bytes()).decode())+'\n'+r'''
import os,sys,pathlib,base64,tempfile,datetime,shutil
root=pathlib.Path('/home/jeremiahai/.local/share/ancestale-vvwk');p=root/'backend.py'
if pathlib.Path.home()!=pathlib.Path('/home/jeremiahai') or p.resolve()!=p or not p.is_file() or 'Closed enrollment.' not in p.read_text():sys.exit('Unexpected remote backend; review first')
raw=base64.b64decode(PAYLOAD);compile(raw,'backend.py','exec')
b=root/('backend-before-events-'+datetime.datetime.now().strftime('%Y%m%d-%H%M%S-%f')+'.bak');shutil.copy2(p,b);os.chmod(b,0o600)
fd,t=tempfile.mkstemp(dir=root,prefix='.backend-')
try:
 with os.fdopen(fd,'wb') as f:f.write(raw);f.flush();os.fsync(f.fileno())
 os.replace(t,p)
finally:
 if os.path.exists(t):os.unlink(t)
print('Private event backend installed; existing enrollments unchanged. Restart only the existing VVWK process separately. Backup:',b)
'''
sys.exit(subprocess.run(['ssh','-T','-o','ConnectTimeout=8','jeremiahai-pi','python3 -'],input=code,text=True).returncode)
