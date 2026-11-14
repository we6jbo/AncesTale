#!/usr/bin/env python3
"""Local, read-only audio inventory plus private editable annotations; no Pi writes."""
import re, argparse,csv,datetime,fcntl,json,math,os,pathlib,shutil,stat,subprocess,sys,tempfile,unicodedata,urllib.parse
ROOT=pathlib.Path('/home/we6jbo/Projects/AncesTale/Music')
STATE=pathlib.Path.home()/'.ancestale-music'
EXT={'.mp3','.ogg','.oga','.wav','.flac','.opus','.m4a','.aac','.mid','.midi','.webm'}
ROLES={'Unassigned','Intro','Beginning','Middle','Outro','Other scene','Do not use'}
BASE='http://192.168.5.215:8081/nov-game/music/'
def private_dir():
    STATE.mkdir(mode=0o700,exist_ok=True)
    s=STATE.lstat()
    if not stat.S_ISDIR(s.st_mode) or s.st_uid!=os.getuid(): raise ValueError('Unsafe private directory')
    STATE.chmod(0o700)
def read(name,default):
    p=STATE/name
    if not p.exists() and not p.is_symlink(): return default
    s=p.lstat()
    if not stat.S_ISREG(s.st_mode) or s.st_uid!=os.getuid() or s.st_mode&0o077: raise ValueError('Unsafe private file: '+name)
    return json.loads(p.read_text(encoding='utf-8'))
def write(name,data):
    fd,tmp=tempfile.mkstemp(dir=STATE,prefix='.tmp-')
    try:
        with os.fdopen(fd,'w',encoding='utf-8') as f:
            json.dump(data,f,ensure_ascii=True,indent=2,allow_nan=False);f.write('\n');f.flush();os.fsync(f.fileno())
        os.replace(tmp,STATE/name)
    finally:
        if os.path.exists(tmp):os.unlink(tmp)
def probe(p):
    if not shutil.which('ffprobe'):return {'probe_status':'ffprobe unavailable','duration_seconds':None}
    try:
        r=subprocess.run(['ffprobe','-v','error','-show_format','-show_streams','-of','json',str(p)],capture_output=True,text=True,timeout=15,check=True)
        raw=json.loads(r.stdout);fmt=raw.get('format',{}); streams=[s for s in raw.get('streams',[]) if s.get('codec_type')=='audio'];dur=fmt.get('duration') or next((s.get('duration') for s in streams if s.get('duration')),None)
        try:dur=float(dur);dur=dur if math.isfinite(dur) and dur>0 else None
        except (TypeError,ValueError):dur=None
        return {'probe_status':'ok' if streams and dur else 'duration or audio stream unavailable','duration_seconds':dur,'format':fmt.get('format_name'),'bit_rate':fmt.get('bit_rate'),'tags':fmt.get('tags',{}),'audio_streams':[{k:s.get(k) for k in ('codec_name','sample_rate','channels','channel_layout','bit_rate','duration','tags') if k in s} for s in streams]}
    except (OSError,subprocess.SubprocessError,ValueError):return {'probe_status':'unsupported or probe failed','duration_seconds':None}
def read_index():
    p=ROOT/'index.csv'
    if not p.is_file() or p.is_symlink():return []
    if p.stat().st_size>2_000_000:raise ValueError('index.csv too large')
    with p.open(encoding='utf-8-sig',errors='replace',newline='') as f:return list(csv.reader(f))
def pi_inventory():
    script="import os,json,stat\np='/home/jeremiahai/www/nov-game/music'\nprint(json.dumps([{'filename': e.name,'size_bytes':e.stat(follow_symlinks=False).st_size} for e in os.scandir(p) if e.is_file(follow_symlinks=False)],ensure_ascii=True))"
    r=subprocess.run(['ssh','-o','BatchMode=yes','-o','ConnectTimeout=8','jeremiahai-pi','python3 -c '+__import__('shlex').quote(script)],capture_output=True,text=True,timeout=25,check=True)
    # A login banner may precede the actual JSON line.
    rows=json.loads(r.stdout.strip().splitlines()[-1]);return {'checked_at':now(),'files':rows}
def now():return datetime.datetime.now(datetime.timezone.utc).isoformat()
def normalized(s):return ''.join(c if c.isascii() else '?' for c in unicodedata.normalize('NFC',s))
def web_mapping(p,size,remote):
    candidates=[x for x in remote.get('files',[]) if x.get('size_bytes')==size and x.get('filename')==p.name]
    if not candidates:candidates=[x for x in remote.get('files',[]) if x.get('size_bytes')==size and normalized(x.get('filename',''))==normalized(p.name)]
    if len(candidates)==1:
        name=candidates[0]['filename'];return {'pi_filename':name,'web_url':BASE+urllib.parse.quote_from_bytes(os.fsencode(name),safe=''),'pi_match_status':'filename and size match; audio bytes and HTTP not verified'}
    return {'pi_filename':None,'web_url':None,'candidate_web_url':BASE+urllib.parse.quote_from_bytes(os.fsencode(p.name),safe=''),'pi_match_status':'unverified; check Pi filenames and HTTP before using'}
def key(name):
    return ''.join(c.casefold() for c in unicodedata.normalize('NFKD',name) if c.isalnum() and not unicodedata.combining(c))
def seed_records():
    p=ROOT/'annotations-20261114.json'
    if not p.is_file() or p.is_symlink():return []
    return json.loads(p.read_text(encoding='utf-8'))
def initial_annotation(filename, seed):
    aliases={'08kateorangevirusinstrumentalmp3':'kateorangevirusinstrumentalmp3'}
    k=key(filename);k=aliases.get(k,k)
    matches=[r for r in seed if key(r['title'])==k]
    if len(matches)==1:return dict(matches[0],import_status='CSV matched')
    return {'title':filename,'source_url':'','credit':'','notes':'','role':'Middle','days':'3-4','quarter':'2/4','repeat':'As appropriate','import_status':'No unique CSV match; default suggestion'}
def merge_annotations(notes,seed):
    for p in ROOT.iterdir():
        if p.is_symlink() or not p.is_file() or p.suffix.lower() not in EXT:continue
        base=initial_annotation(p.name,seed); existing=notes.get(p.name,{})
        if existing.get('schema_version')==2:
            for field in ('title','source_url','credit'):existing[field]=base[field]
            continue
        # Keep the CSV note and legacy edits, including distinctions in role.
        old_text=existing.get('notes','')
        if old_text and old_text!=base['notes']:
            base['notes']=(base['notes']+'\n\nExisting local notes: '+old_text).strip()
        if existing.get('role') not in (None,'Unassigned',base['role']):
            base['legacy_role']=existing['role']
            if existing['role']=='Do not use':base['role']='Do not use'
        base['schema_version']=2;notes[p.name]=base
    return notes
def timing_values(timing):
    a,b=timing.get('quarter2_percent',50),timing.get('quarter3_percent',75)
    if type(a)!=int or type(b)!=int or not 1<=a<b<=99:raise ValueError('Require 1 <= 2/4 < 3/4 <= 99')
    return {'quarter2_percent':a,'quarter3_percent':b}
def build(notes,remote,old,force=False,timing=None):
    if not ROOT.is_dir() or ROOT.is_symlink():raise ValueError('Music directory missing or symlink')
    cached={t['filename']:t for t in old.get('tracks',[])};tracks=[]
    for p in sorted(ROOT.iterdir(),key=lambda p:p.name.casefold()):
        if p.is_symlink() or not p.is_file() or p.suffix.lower() not in EXT:continue
        st=p.stat();old_t=cached.get(p.name,{});fingerprint=[st.st_size,st.st_mtime_ns]
        meta=old_t.get('metadata') if not force and old_t.get('fingerprint')==fingerprint else None
        if not isinstance(meta,dict):meta=probe(p)
        tracks.append({'filename':p.name,'local_path':str(p),'size_bytes':st.st_size,'fingerprint':fingerprint,'metadata':meta,'annotation':notes.get(p.name,{'role':'Unassigned','notes':''}),'rights_status':'not independently verified; inspect source index and recording rights',**web_mapping(p,st.st_size,remote)})
    warning='' if shutil.which('ffprobe') else 'ffprobe missing; duration and embedded metadata unavailable.'
    return {'schema':'AncesTale.music.catalog.v1','generated_at':now(),'pi_inventory_checked_at':remote.get('checked_at'),'warning':warning,'game_url':'http://192.168.5.215:8081/nov-game/','index_csv_rows':read_index(),'timing':timing_values(timing or {}),'tracks':tracks}
def main():
    a=argparse.ArgumentParser();a.add_argument('action',choices=['scan','save','check-pi','load','save-timing']);args=a.parse_args();os.umask(0o077);private_dir()
    lock=STATE/'catalog.lock';fd=os.open(lock,os.O_CREAT|os.O_RDWR|os.O_NOFOLLOW,0o600)
    with os.fdopen(fd,'w') as f:
        fcntl.flock(f,fcntl.LOCK_EX)
        notes=read('notes.json',{});remote=read('pi-inventory.json',{});old=read('catalog.json',{})
        seed=seed_records();notes=merge_annotations(notes,seed);timing=timing_values(read('timing.json',{}))
        if args.action=='save-timing':timing=timing_values(json.load(sys.stdin));write('timing.json',timing)
        if args.action=='check-pi':remote=pi_inventory();write('pi-inventory.json',remote)
        if args.action=='save':
            n=json.load(sys.stdin);name=n['filename'];role=n['role'];text=n['notes'];p=ROOT/name
            if pathlib.Path(name).name!=name or p.is_symlink() or not p.is_file() or p.suffix.lower() not in EXT or role not in ROLES or not isinstance(text,str) or len(text)>50000:raise ValueError('Invalid track or annotation')
            extra={k:n.get(k,'') for k in ('days','quarter','repeat')}
            if any(not isinstance(v,str) or len(v)>4000 for v in extra.values()) or extra['quarter'] not in ('Intro','1/4','2/4','3/4','Outro','Unassigned'):raise ValueError('Invalid scheduling fields')
            notes[name]={**notes.get(name,{}),**extra,'role':role,'notes':text,'updated_at':now(),'schema_version':2}
        write('notes.json',notes)
        result=build(notes,remote,old,force=args.action=='scan',timing=timing);write('catalog.json',result);print(json.dumps(result,ensure_ascii=True,allow_nan=False))
if __name__=='__main__':
    try:main()
    except Exception as e:print(str(e),file=sys.stderr);sys.exit(1)
