#!/usr/bin/env python3
"""Inspect owner-staged media; never download, publish or modify source media."""
import argparse, json, pathlib, hashlib, subprocess, re, os, tempfile
ROOT=pathlib.Path('/home/we6jbo/1')
def inside(root, rel):
 p=root/rel
 if pathlib.Path(rel).is_absolute() or not p.resolve().is_relative_to(root.resolve()) or p.resolve()!=p.absolute():raise ValueError('unsafe media path')
 return p
def scan(root):
 data=json.loads((root/'index.json').read_text()); results=[];seen=set()
 if data.get('schema')!='ancestale-media-v1':raise ValueError('unsupported index')
 for item in data['items']:
  r={**item,'ready':False,'issues':[]}; e=r['issues']; results.append(r)
  try:
   ident=item['id'];kind=item['kind']
   if not re.fullmatch(r'[a-zA-Z0-9_-]+',ident) or ident in seen:raise ValueError('invalid or duplicate ID')
   seen.add(ident);p=inside(root,item['path'])
   if not p.is_file():e.append('missing file');continue
   for k in ('title','creator','source_url','license','license_url','credit','rights_notes'):
    if not isinstance(item.get(k),str) or not item[k].strip():e.append('missing '+k)
   for k in ('source_url','license_url'):
    if not str(item.get(k,'')).startswith(('https://','http://')):e.append('invalid '+k)
   if item.get('approved_for_lan') is not True:e.append('owner rights review pending')
   if kind=='movie':
    info=json.loads(subprocess.check_output(['ffprobe','-v','error','-show_streams','-show_format','-of','json',str(p)],timeout=15));duration=float(info['format']['duration']);r['duration_seconds']=duration
    if not 600<=duration<=2700:e.append('duration outside 10–45 minutes')
    if not any(x.get('codec_type')=='video' for x in info['streams']):e.append('no video stream')
    if not any(x.get('codec_type')=='video' and x.get('codec_name')=='h264' for x in info['streams']):e.append('H.264 conversion/review required')
    if p.suffix.lower()!='.mp4':e.append('MP4 required')
   elif kind=='voice':
    for key in ('config','model_card'):
     if not inside(root,item[key]).is_file():e.append('missing '+key)
    if p.suffix!='.onnx':e.append('ONNX required')
   elif kind=='artwork':
    if p.suffix.lower() not in ('.png','.jpg','.jpeg','.webp'):e.append('unsupported image type')
   else:e.append('unknown kind')
   if not e:
    with p.open('rb') as f:r['sha256']=hashlib.file_digest(f,'sha256').hexdigest()
    r['ready']=True
  except Exception as exc:e.append(str(exc))
 return {'schema':'ancestale-media-review-v1','items':results,'ready':sum(i['ready'] for i in results),'total':len(results)}
if __name__=='__main__':
 a=argparse.ArgumentParser();a.add_argument('--root',type=pathlib.Path,default=ROOT);a.add_argument('--json',action='store_true');v=a.parse_args();result=scan(v.root.absolute());print(json.dumps(result,indent=2) if v.json else '\n'.join([f"{i['id']}: "+('READY (owner reviewed)' if i['ready'] else '; '.join(i['issues'])) for i in result['items']]+[f"{result['ready']}/{result['total']} ready"]))
