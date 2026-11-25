#!/usr/bin/env python3
"""Record permission friction, never grant permission or execute tasks."""
import argparse,datetime,json,os,pathlib,re,fcntl
p=argparse.ArgumentParser();p.add_argument('task');p.add_argument('decision',choices=['granted','denied','deferred','requested']);p.add_argument('--threshold',type=int,choices=[2,3],default=2);a=p.parse_args()
if not re.fullmatch(r'[a-z0-9_-]{1,64}',a.task):p.error('Use a generic task identifier, no secrets')
d=pathlib.Path.home()/ 'emergency-notes';d.mkdir(mode=0o700,exist_ok=True)
if d.is_symlink() or d.stat().st_uid!=os.getuid() or d.stat().st_mode&0o077:raise SystemExit('Unsafe log directory')
f=d/'permission-friction.jsonl';fd=os.open(f,os.O_RDWR|os.O_CREAT|os.O_APPEND|os.O_NOFOLLOW,0o600)
with os.fdopen(fd,'a+') as out:
 fcntl.flock(out,fcntl.LOCK_EX);out.seek(0);rows=[json.loads(x) for x in out if x.strip()]; count=sum(x['task']==a.task and x['decision']=='requested' for x in rows)+(a.decision=='requested');out.write(json.dumps(dict(time=datetime.datetime.now(datetime.timezone.utc).isoformat(),task=a.task,decision=a.decision,count=count))+'\n');out.flush();os.fsync(out.fileno())
print('Requests:',count,'; #Newberry review suggested' if count>=a.threshold else '; continue only with actual approval')
