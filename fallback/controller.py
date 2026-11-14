#!/usr/bin/env python3
"""Owner-armed fallback for Nov 21–29 only. No email, Git, sudo or service changes."""
import argparse, datetime as dt, fcntl, hashlib, html, json, os, pathlib, stat, subprocess, tempfile, time, urllib.request
from zoneinfo import ZoneInfo
ROOT=pathlib.Path(__file__).resolve().parents[1]
ZONE=ZoneInfo('America/Los_Angeles')
PRIVATE=pathlib.Path.home()/'emergency-notes'
STATE=ROOT/'.fallback-local'
HERE=ROOT/'fallback'
GAME='http://192.168.5.215:8081/nov-game/'

def secure_dir(p):
    p.mkdir(mode=0o700,exist_ok=True)
    s=p.lstat()
    if not stat.S_ISDIR(s.st_mode) or s.st_uid!=os.getuid() or s.st_mode&0o077:raise RuntimeError('Private directory must be owned by current user, mode 700: '+str(p))

def atomic(p,obj):
    if p.is_symlink():raise RuntimeError('Unsafe symlink')
    fd,t=tempfile.mkstemp(dir=p.parent,prefix='.tmp-')
    try:
        with os.fdopen(fd,'w') as f:json.dump(obj,f,ensure_ascii=False,indent=2);f.write('\n');f.flush();os.fsync(f.fileno())
        os.replace(t,p)
    finally:
        if os.path.exists(t):os.unlink(t)

def read(p):
    if p.is_symlink():raise RuntimeError('Unsafe symlink')
    return json.loads(p.read_text()) if p.exists() else {}

def log(day,event,**fields):
    p=PRIVATE/(day+'.jsonl')
    fd=os.open(p,os.O_WRONLY|os.O_CREAT|os.O_APPEND|os.O_NOFOLLOW,0o600)
    with os.fdopen(fd,'a') as f:
        f.write(json.dumps(dict(time=dt.datetime.now(dt.timezone.utc).isoformat(),event=event,**fields),ensure_ascii=False)+'\n');f.flush();os.fsync(f.fileno())

def remote(code):
    r=subprocess.run(['ssh','-T','-o','BatchMode=yes','-o','ConnectTimeout=8','jeremiahai-pi','python3 -'],input=code,text=True,capture_output=True,timeout=45)
    if r.returncode:raise RuntimeError('SSH operation failed (check authorized alias and Pi availability)')
    return r.stdout

def activate(day,mode):
    # Same file for every date: the browser itself date-gates operation.
    raw=(HERE/'index.html').read_bytes(); expected=hashlib.sha256(raw).hexdigest()
    import base64
    code='PAYLOAD='+repr(base64.b64encode(raw).decode())+'\n'+r'''
import base64,datetime,hashlib,os,pathlib,shutil,tempfile,sys
base=pathlib.Path('/home/jeremiahai'); p=base/'www/nov-game/index.html'; private=base/'.local/share/ancestale-vvwk'
if pathlib.Path.home()!=base or not p.is_file() or p.resolve()!=p or private.resolve()!=private or not private.is_dir():sys.exit('Wrong account or unsafe paths')
old=p.read_bytes(); new=base64.b64decode(PAYLOAD)
if old!=new:
 b=private/('game-before-fallback-'+datetime.datetime.now().strftime('%Y%m%d-%H%M%S-%f')+'.html')
 fd=os.open(b,os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW,0o600)
 with os.fdopen(fd,'wb') as f:f.write(old);f.flush();os.fsync(f.fileno())
 fd,t=tempfile.mkstemp(dir=p.parent,prefix='.recovery-');os.fchmod(fd,0o644)
 try:
  with os.fdopen(fd,'wb') as f:f.write(new);f.flush();os.fsync(f.fileno())
  if p.read_bytes()!=old:sys.exit('Concurrent site change; refusing takeover')
  os.replace(t,p)
 finally:
  if os.path.exists(t):os.unlink(t)
print(hashlib.sha256(p.read_bytes()).hexdigest())
'''
    # Mark pending BEFORE writing; Vibe is required to stop if pending/taken over.
    atomic(STATE/'taken-over.json',dict(date=day['date'],mode=mode,status='pending',sha256=expected))
    log(day['date'],'takeover_requested',mode=mode)
    if remote(code).strip().splitlines()[-1]!=expected:raise RuntimeError('Remote file hash mismatch')
    req=urllib.request.Request(GAME+'?fallback_verify='+str(time.time_ns()),headers={'Cache-Control':'no-cache'})
    with urllib.request.urlopen(req,timeout=10) as r: body=r.read(2_000_000)
    if hashlib.sha256(body).hexdigest()!=expected:raise RuntimeError('HTTP verification failed; inspect live page and backup before retry')
    atomic(STATE/'taken-over.json',dict(date=day['date'],mode=mode,status='verified',sha256=expected))
    log(day['date'],'fallback_verified',mode=mode,person=day['name'],tg=day['tg'],birth=day['birth'],source=day['source'],art='Original procedural vector illustration',sha256=expected)
    print('Emergency adventure verified on '+GAME)

def collect(day):
    # Only event log, never enrollment file or reusable cookie.
    code=r'''import pathlib
p=pathlib.Path.home()/'.local/share/ancestale-vvwk/game-events.jsonl'
if p.is_file() and not p.is_symlink():
 with p.open('rb') as f:
  f.seek(max(0,p.stat().st_size-1000000)); data=f.read()
  print(data.decode('utf-8','replace'))
'''
    events=[]
    import re
    for line in remote(code).splitlines():
        try:
            e=json.loads(line); stamp=dt.datetime.fromtimestamp(float(e['time']),ZONE)
            if stamp.date().isoformat()==day['date'] and e['event'] in ('scene','choice','music_started','music_failed','chime_started','session_end','heartbeat') and re.fullmatch(r'[A-Za-z0-9_-]{1,60}',e['detail']):events.append(e)
        except (ValueError,KeyError,TypeError,OverflowError):continue
    p=PRIVATE/(day['date']+'-browser-events.json');atomic(p,events)
    log(day['date'],'browser_events_collected',count=len(events))
    print('Collected',len(events),'browser-reported events (not proof of audible sound).')
    return events

def draft(day,events):
    takeover=read(STATE/'taken-over.json'); verified=takeover.get('date')==day['date'] and takeover.get('status')=='verified'
    observed=any(e['event']=='scene' for e in events)
    starts={e['detail'] for e in events if e['event']=='music_started'}
    tracks=[t for cue,t in zip(('intro','middle','outro'),day['tracks']) if cue in starts]
    title='Discovering Our Family Branches'
    body=f'<p>According to the signed local family record, {html.escape(day["name"])} was born {html.escape(day["birth"])} in {html.escape(day["place"])}. AncesTale prepared an illustrated adventure chapter based on this record, separating genealogical claims from imaginative scenery. The birth details have not been independently confirmed.</p>\n'
    desc='The emergency page was verified on the game server.' if verified else 'The emergency chapter was prepared, but deployment has not been verified.'
    desc+=' A browser reported visiting a scene.' if observed else ' No player visit was confirmed in the recovered event log.'
    if tracks:desc+=' The browser reported starting '+', '.join(t['title'] for t in tracks)+'. Audible playback was not independently verified.'
    else:desc+=' No music playback was confirmed in the recovered event log.'
    body+='<p>'+html.escape(desc)+' Artwork is an original procedural illustration. A screenshot and music embed should be added only after the actual media are reviewed and their public URLs verified.</p>'
    obj=dict(session_id='backup-'+day['date'],date=day['date'],title=title,blog=body,facebook='AncesTale family history: '+day['name']+'. Read more: [BLOG_URL]',linkedin='AncesTale combines genealogy with interactive storytelling. Read the development update: [BLOG_URL]',speech=day['speech'],person=day['name'],birthdate=day['birth'],record_id=day['tg'],source_url=day['source'],evidence='Emergency draft; review before publication.')
    path=PRIVATE/(day['date']+'-draft.json')
    if not path.exists():atomic(path,obj);log(day['date'],'emergency_draft_created')
    print('Emergency draft available:',path)

def main():
    ap=argparse.ArgumentParser();ap.add_argument('command',choices=['arm','disarm','lease','check','takeover','collect','draft']);a=ap.parse_args()
    if ROOT!=pathlib.Path('/home/we6jbo/Projects/AncesTale') or ROOT.resolve()!=ROOT:raise SystemExit('Run only from authorized T14 project root')
    # Passive monitor does not create state until armed or explicitly used.
    if a.command=='check' and not STATE.is_dir():return
    os.umask(0o077);secure_dir(STATE);secure_dir(PRIVATE)
    fd=os.open(STATE/'lock',os.O_CREAT|os.O_RDWR|os.O_NOFOLLOW,0o600)
    with os.fdopen(fd,'w') as lock:
        fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
        now=dt.datetime.now(ZONE); day=next((d for d in json.loads((HERE/'days.json').read_text()) if d['date']==now.date().isoformat()),None)
        if a.command=='disarm':atomic(STATE/'armed.json',{});print('Fallback monitor disarmed.');return
        if not day:
            if a.command!='check':print('Outside Nov 21–29 recovery period; no action.')
            return
        date=day['date']; taken=read(STATE/'taken-over.json');armed=read(STATE/'armed.json');lease=read(STATE/'lease.json')
        active=dt.datetime.fromisoformat(day['start'])<=now<dt.datetime.fromisoformat(day['end'])
        if a.command=='collect':collect(day);return
        if a.command=='draft':draft(day,collect(day));return
        if a.command=='lease':
            if taken.get('date')==date:raise SystemExit('Fallback takeover pending or active; Vibe must stop site writes.')
            if not active:raise SystemExit('Outside game session.')
            atomic(STATE/'lease.json',dict(date=date,time=time.time()));print('Vibe lease renewed.');return
        if a.command=='arm':
            if now>=dt.datetime.fromisoformat(day['end']):raise SystemExit('Session ended')
            atomic(STATE/'armed.json',dict(date=date,time=time.time()));log(date,'monitor_armed');print('Armed today. Keep AncesTale running. Vibe must renew lease every 60s.');return
        if a.command=='check':
            if taken.get('date')==date:
                if taken.get('status')=='verified' and now>=dt.datetime.fromisoformat(day['end']) and not (PRIVATE/(date+'-draft.json')).exists():draft(day,collect(day))
                return
            if not active or armed.get('date')!=date:return
            if lease.get('date')!=date:return # explicit manual takeover if Vibe failed before initial lease
            if time.time()-max(lease['time'],armed['time'])<300:return
            activate(day,'owner-armed-stale-lease');return
        if a.command=='takeover':
            if not active:raise SystemExit('Outside today’s scheduled game window')
            activate(day,'manual');return
if __name__=='__main__':
    try:main()
    except Exception as e:print('Recovery blocked:',e);raise SystemExit(1)
