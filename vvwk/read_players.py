#!/usr/bin/env python3
"""Private read-only SSH summary; never return bearer cookie values."""
import subprocess,sys,json
remote=r'''import json,time,hashlib,pathlib,datetime
p=pathlib.Path.home()/'.local/share/ancestale-vvwk/enrollments.json'
now=time.time()
def fmt(x):return datetime.datetime.fromtimestamp(x,datetime.timezone.utc).isoformat() if x else 'Never observed'
rows=[]
for token,r in json.loads(p.read_text()).items():
 if r['expires']<=now:continue
 last=r.get('last_seen',0)
 rows.append({'name':r['name'],'ip':r.get('last_ip',r['ip']),'player_id':hashlib.sha256(token.encode()).hexdigest()[:16],'page':r.get('last_page','Not observed on game page'),'last_seen':fmt(last),'status':('Unknown — no game heartbeat' if not last else 'Recently connected' if 0<=now-last<=90 else 'Offline or inactive'),'expires':fmt(r['expires']),'sort':last})
rows.sort(key=lambda x:x.pop('sort'),reverse=True)
print(json.dumps({'schema':'ancestale.players.v1','players':rows},ensure_ascii=False))'''
r=subprocess.run(['ssh','-T','-o','BatchMode=yes','-o','ConnectTimeout=5','jeremiahai-pi','python3 -'],input=remote,text=True,capture_output=True,timeout=15)
if r.returncode:sys.exit('SSH query failed; verify authentication in terminal')
for line in reversed(r.stdout.splitlines()):
 try:
  data=json.loads(line)
  if data.get('schema')=='ancestale.players.v1':print(json.dumps(data,ensure_ascii=False));sys.exit(0)
 except (ValueError,AttributeError):pass
sys.exit('No valid player summary returned')
