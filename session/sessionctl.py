#!/usr/bin/env python3
"""Prepare local session artifacts; never SSH, publish, or modify signed assets."""
import argparse,csv,datetime as dt,hashlib,json,os,pathlib,re,tempfile
from zoneinfo import ZoneInfo
ROOT=pathlib.Path(__file__).resolve().parents[1]
LOCAL=ROOT/'.session-local'
ZONE=ZoneInfo('America/Los_Angeles')
def atomic(path,obj):
    path.parent.mkdir(mode=0o700,parents=True,exist_ok=True)
    fd,tmp=tempfile.mkstemp(dir=path.parent)
    try:
        with os.fdopen(fd,'w') as f: json.dump(obj,f,indent=2,ensure_ascii=False); f.write('\n'); f.flush(); os.fsync(f.fileno())
        os.replace(tmp,path)
    finally:
        if os.path.exists(tmp): os.unlink(tmp)
def log(s):
    LOCAL.mkdir(mode=0o700,exist_ok=True)
    with (LOCAL/'controller.log').open('a') as f: f.write(dt.datetime.now(ZONE).isoformat()+' '+s+'\n'); f.flush(); os.fsync(f.fileno())
def make(a):
    start=dt.datetime.combine(dt.date.fromisoformat(a.date),dt.time(15,20),ZONE)
    if start<=dt.datetime.now(ZONE): raise SystemExit('Refusing a past start time; choose a future session date.')
    with open(a.index,newline='',encoding='utf-8-sig') as f: rows=list(csv.DictReader(f))
    hits=[r for r in rows if r.get('file')==a.file]
    if len(hits)!=1: raise SystemExit('Track must occur exactly once in index: file,title,license,source_url,reviewed')
    r=hits[0]
    if r.get('license','').strip().upper() not in {'CC0','CC0-1.0','PUBLIC DOMAIN'} or r.get('reviewed','').lower()!='yes' or not r.get('source_url','').startswith('https://') or not r.get('title','').strip(): raise SystemExit('Track lacks approved public-domain/CC0 review and source.')
    if not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9_. -]{0,150}\.(mp3|ogg|wav|flac|m4a)',a.file,re.I) or '..' in a.file: raise SystemExit('Unsafe audio filename')
    p=ROOT/'Music'/a.file
    if not p.is_file() or p.is_symlink() or p.resolve().parent!=(ROOT/'Music').absolute(): raise SystemExit('Local audio missing or unsafe')
    digest=hashlib.sha256(p.read_bytes()).hexdigest()
    obj=dict(schema='ancestale.session.v1',id=start.strftime('%Y%m%d-1520'),start=start.isoformat(),draft_at=(start+dt.timedelta(minutes=2)).isoformat(),end=(start+dt.timedelta(minutes=10)).isoformat(),file=a.file,title=r['title'],license=r['license'],source_url=r['source_url'],sha256=digest)
    atomic(LOCAL/'ancestale-session.json',obj);log('Prepared '+obj['id']); print(LOCAL/'ancestale-session.json')
def draft(a):
    state=json.loads((LOCAL/'ancestale-session.json').read_text()); obj=json.loads(pathlib.Path(a.input).read_text())
    if obj.get('session_id')!=state['id']: raise SystemExit('Session mismatch')
    if dt.datetime.now(ZONE)<dt.datetime.fromisoformat(state['draft_at']): raise SystemExit('Draft not due yet')
    for k in ('title','blog','facebook','linkedin','speech','person','birthdate','record_id','story_url','source_url'):
        if not isinstance(obj.get(k),str) or not obj[k].strip(): raise SystemExit('Missing '+k)
    if len(obj['title'].split())!=4 or len(re.split(r'\n\s*\n',obj['blog'].strip()))!=2 or len(obj['speech'].split())>75: raise SystemExit('Title, blog or speech length invalid')
    if not obj['story_url'].startswith('http://192.168.5.215:8081/') or not obj['source_url'].startswith(('https://','http://')): raise SystemExit('Invalid evidence URL')
    for k in ('facebook','linkedin'):
        if 'https://j03.page/' not in obj[k] and '[BLOG_URL]' not in obj[k]: raise SystemExit('Missing blog link/placeholder')
    if len(obj['speech'].split())<10: raise SystemExit('Speech too short')
    atomic(LOCAL/'blog.json',obj);log('Draft saved '+state['id']);print('Draft shape checked; human evidence/privacy review still required.')
p=argparse.ArgumentParser();sub=p.add_subparsers(dest='cmd',required=True);m=sub.add_parser('prepare');m.add_argument('--date',required=True);m.add_argument('--index',required=True);m.add_argument('--file',required=True);m.set_defaults(fn=make);d=sub.add_parser('draft');d.add_argument('--input',required=True);d.set_defaults(fn=draft);a=p.parse_args();a.fn(a)
