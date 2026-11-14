#!/usr/bin/env python3
"""Private, read-only collection. No network, deployment, or source writes."""
import argparse, datetime, hashlib, json, os, pathlib, sqlite3, tempfile
P=pathlib.Path
ROOT=P('/home/we6jbo/Projects/AncesTaleextended')
OUT=P.home()/'.ancestale'/'extended'
EXPECTED='7d48a3f3e046c1fc1d4683e52ea20cdc'
def atomic(p,obj):
    fd,t=tempfile.mkstemp(dir=p.parent,prefix='.bridge-')
    try:
        with os.fdopen(fd,'w') as f: json.dump(obj,f,ensure_ascii=False,indent=2); f.flush(); os.fsync(f.fileno())
        os.replace(t,p)
    finally:
        if os.path.exists(t): os.unlink(t)
def collect(root,out,screens):
    if out.is_symlink() or out.parent.is_symlink(): raise ValueError('Unsafe output')
    out.mkdir(parents=True,exist_ok=True,mode=0o700); os.chmod(out,0o700)
    errors=[]; research={}; groups=[]; notes=[]; music=[]; shots=[]; relationships=[]; digest=None
    def read(p):
        if p.is_symlink() or not p.is_file(): raise ValueError('Missing or unsafe input: '+p.name)
        return json.loads(p.read_text())
    try:
        research=read(root/'missing_family_records.json')
        if not isinstance(research,dict) or not isinstance(research.get('people'),list): raise ValueError('Unexpected research schema')
    except Exception as e: errors.append('Research: '+str(e)); research={}
    try:
        db=root/'family_groups.db'
        if db.is_symlink() or not db.is_file(): raise ValueError('Missing or unsafe database')
        digest=hashlib.md5(db.read_bytes()).hexdigest()
        if digest!=EXPECTED: errors.append('Family DB differs from owner supplied MD5; review current snapshot before using its facts (legitimate additions may change it).')
        with sqlite3.connect(db.as_uri()+'?mode=ro',uri=True) as c:
            c.row_factory=sqlite3.Row; c.execute('PRAGMA query_only=ON'); c.execute('BEGIN')
            groups=[dict(r) for r in c.execute('SELECT * FROM family_groups')]; notes=[dict(r) for r in c.execute('SELECT * FROM record_notes')]
        roles=('person','father','mother','spouse','child')
        for g in groups:
            names={r:' '.join(str(g.get(r+'_'+k) or '').strip() for k in ('first_name','last_name')).strip() for r in roles}
            for a,b,rel in [('father','person','father_of'),('mother','person','mother_of'),('person','spouse','spouse_of'),('person','child','parent_of')]:
                if names[a] and names[b]: relationships.append(dict(group_id=g['id'],subject=names[a],relation=rel,object=names[b],status='recorded_not_independently_verified'))
            if names['spouse'] and names['child']: relationships.append(dict(group_id=g['id'],subject=names['spouse'],relation='possible_co_parent',object=names['child'],status='unresolved_do_not_assert'))
    except Exception as e: errors.append('Family groups: '+str(e)); groups=[]; notes=[]; relationships=[]
    for m in sorted((root/'Music').glob('*/metadata.json')):
        try:
            if m.parent.is_symlink(): raise ValueError('Symlink recording directory')
            data=read(m); files=[str(f) for f in m.parent.iterdir() if f.is_file() and not f.is_symlink() and f.suffix.lower() in {'.ogg','.oga','.mp3','.wav','.flac','.opus','.m4a','.webm'}]
            music.append(dict(metadata_file=str(m),metadata=data,local_audio=files,status='rights_review_required'))
        except Exception as e: errors.append('Music: '+str(e))
    if screens.is_dir() and not screens.is_symlink():
        shots=[dict(path=str(f),status='unreviewed_local_only') for f in sorted(screens.iterdir()) if f.is_file() and not f.is_symlink() and f.suffix.lower() in {'.png','.jpg','.jpeg','.webp'}]
    now=datetime.datetime.now(datetime.timezone.utc).isoformat()
    result=dict(schema='AncesTale.extended.private.v1',created_at=now,classification='private_local_only',research=research,family_groups=groups,record_notes=notes,relationship_candidates=relationships,family_db_md5=digest,expected_family_db_md5=EXPECTED,music=music,screenshots=shots,issues=errors)
    atomic(out/'snapshot.json',result)
    summary=dict(created_at=now,counts=dict(people=len(research.get('people',[])),groups=len(groups),notes=len(notes),relationships=len(relationships),music=len(music),screenshots=len(shots)),issues=errors,snapshot=str(out/'snapshot.json'),routes={'Vibe':'private snapshot; evidence review and relationship reconciliation','Pi':'only approved scene facts and rights-cleared media; no raw snapshot','Blog':'four-word title, two paragraphs, verified screenshot/audio and credits','Facebook':'reviewed summary and actual blog URL','LinkedIn':'reviewed summary and actual blog URL','Speech':'reviewed historical name/date, <=40 seconds','Local only':'unresolved relationships, private records, raw metadata, unreviewed screenshots and errors'})
    atomic(out/'summary.json',summary); return summary
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--root',type=P,default=ROOT);p.add_argument('--out',type=P,default=OUT);p.add_argument('--screens',type=P,default=P.home()/'.38bTqEvQc/ancestaleextended');a=p.parse_args();print(json.dumps(collect(a.root.resolve(),a.out,a.screens),indent=2,ensure_ascii=False))
