"""Validate the candidate's native/asset contracts before building. Not a physics acceptance test."""
from pathlib import Path
import argparse,hashlib,json,struct,ctypes,math
import numpy as np
import mujoco
P=Path(__file__).resolve().parents[1]
def check(root):
 root=Path(root);assets=root/'Unity/Assets/StreamingAssets';model=mujoco.MjModel.from_xml_path(str(assets/'playground.xml'));stadium=mujoco.MjModel.from_xml_path(str(assets/'stadium.xml'));files={};counts={}
 for folder in ['Robot','Field','ReusedPieces','Stadium','StadiumPieces']:
  active_model=stadium if folder=='StadiumPieces' else model
  base=assets/folder;manifest=json.loads((base/'manifest.json').read_text());checked={};entries=manifest['meshes']
  if not entries:raise ValueError(f'{folder}: no meshes')
  for e in entries:
   if e['body']!='world' and mujoco.mj_name2id(active_model,mujoco.mjtObj.mjOBJ_BODY,e['body'])<0:raise ValueError(f"Missing physical body: {e['body']}")
   for key,n in [('rgba',4),('position',3),('rotation',4)]:
    if key=='rgba' or key in e:
     a=e[key]
     if len(a)!=n or not all(math.isfinite(v) for v in a):raise ValueError(f'Invalid {key}: {e}')
   if 'rotation' in e and abs(sum(v*v for v in e['rotation'])-1)>.0001:raise ValueError('Non-unit quaternion')
   if e['file'] in checked:continue
   f=(base/e['file']).resolve()
   if not f.is_relative_to(base.resolve()):raise ValueError('Mesh path escapes asset folder')
   data=f.read_bytes()
   if len(data)<8:raise ValueError(f'Truncated mesh header: {f}')
   nv,ni=struct.unpack_from('<ii',data)
   if nv<=0 or ni<=0 or ni%3:raise ValueError(f'Invalid mesh counts: {f}')
   size=8+nv*12+ni*4
   if len(data) not in [size,size+nv*12]:raise ValueError(f'Truncated or surplus mesh data: {f}')
   v=np.frombuffer(data,'<f4',nv*3,8);idx=np.frombuffer(data,'<i4',ni,8+nv*12)
   if not np.isfinite(v).all() or idx.min()<0 or idx.max()>=nv:raise ValueError(f'Invalid mesh vertex/index: {f}')
   if len(data)>size and not np.isfinite(np.frombuffer(data,'<f4',nv*3,size)).all():raise ValueError(f'Invalid normals: {f}')
   files[str(f.relative_to(root))]=hashlib.sha256(data).hexdigest();checked[e['file']]=ni//3
  counts[folder]={'instances':len(entries),'uniqueMeshes':len(checked),'uniqueTriangles':sum(checked.values()),'instancedTriangles':sum(checked[e['file']] for e in entries)}
 for f in list(assets.rglob('*.json'))+list(assets.glob('*.xml')):
  files[str(f.relative_to(root))]=hashlib.sha256(f.read_bytes()).hexdigest()
 native=root/'Unity/Assets/Plugins/liboverride.dylib';lib=ctypes.CDLL(str(native));lib.pg_engine_version.restype=ctypes.c_int
 if lib.pg_engine_version()!=mujoco.mj_version():raise ValueError('Python/native MuJoCo versions differ')
 lib.pg_load.argtypes=[ctypes.c_char_p,ctypes.c_char_p,ctypes.c_int];buf=ctypes.create_string_buffer(4096)
 try:
  n=lib.pg_load(str(assets/'playground.xml').encode(),buf,4096)
  if not n:raise ValueError(buf.value.decode())
  if n!=model.nbody:raise ValueError('Native/Python model body mismatch')
 finally:lib.pg_close()
 return {'status':'PASS','scope':'Asset and native loading only; dynamics and graphics remain unvalidated','engine':mujoco.__version__,'bodies':model.nbody,'geoms':model.ngeom,'counts':counts,'assetSHA256':files}
if __name__=='__main__':
 ap=argparse.ArgumentParser();ap.add_argument('--output',default=str(P/'Evidence/v2/preflight.json'));args=ap.parse_args();report=check(P);Path(args.output).write_text(json.dumps(report,indent=2));print(json.dumps({k:v for k,v in report.items() if k!='assetSHA256'},indent=2))
