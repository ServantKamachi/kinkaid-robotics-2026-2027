"""Reusable GPL field presentation; presentation with drawing-audited nominal measurements.
Pinned provenance: Research/REUSE_AUDIT.md. Meshoptimizer absolute simplification error <=0.15mm.
"""
from pathlib import Path
import json,struct,hashlib,numpy as np,trimesh,meshoptimizer as mo
from scipy.spatial.transform import Rotation
P=Path(__file__).resolve().parents[1];out=P/'Unity/Assets/StreamingAssets/Stadium';out.mkdir(exist_ok=True);entries=[];stats=[]
def save(mesh,name):
 mesh.merge_vertices();mesh.update_faces(mesh.nondegenerate_faces());mesh.update_faces(mesh.unique_faces());mesh.remove_unreferenced_vertices()
 v=np.asarray(mesh.vertices,dtype=np.float32);idx=np.asarray(mesh.faces,dtype=np.uint32).reshape(-1);dest=np.empty_like(idx);err=np.zeros(1,np.float32)
 n=mo.simplify(dest,idx,v,target_index_count=max(3,int(len(idx)*.12)//3*3),target_error=.00015,options=mo.SIMPLIFY_ERROR_ABSOLUTE|mo.SIMPLIFY_LOCK_BORDER,result_error=err)
 m=trimesh.Trimesh(v,dest[:n].reshape(-1,3),process=False);m.remove_unreferenced_vertices();m=trimesh.graph.smooth_shade(m,angle=np.radians(35))
 v=np.asarray(m.vertices,dtype='<f4');f=np.asarray(m.faces,dtype='<i4');norm=np.asarray(m.vertex_normals,dtype='<f4');file=name+'.meshbin';(out/file).write_bytes(struct.pack('<ii',len(v),f.size)+v.tobytes()+f.tobytes()+norm.tobytes());stats.append(dict(file=file,inputTriangles=len(idx)//3,triangles=n//3,errorMeters=float(err[0])));return file
for stem in ['FieldPerimeter','Override-H2H-_-FieldElements','Override-H2H-_-Toggle']:
 source=P/'Research/Assets'/('V5RC-'+stem+'.glb');s=trimesh.load(source)
 for i,node in enumerate(s.graph.nodes_geometry):
  tf,key=s.graph[node];m=s.geometry[key].copy();m.apply_transform(tf);rgba=(m.visual.material.main_color/255).tolist()
  if 'clear' in m.visual.material.name.lower():rgba[3]=.38
  if stem!='Override-H2H-_-Toggle':
   v=m.vertices.copy()
   # Two reused red loader shells sit 7.79846 mm above the corresponding blue shells.
   # Correct only those colored/acrylic moving panels; fixed bracket audit is separate.
   if stem=='Override-H2H-_-FieldElements' and m.visual.material.name in ['Acrylic_(Clear)','Opaque(213,0,50)']:
    mask=(v[:,0]<-1.65)&(np.abs(v[:,1])>1.35);v[mask,2]-=.00779846
   m.vertices=np.column_stack([v[:,0],v[:,2]+.2943392,-v[:,1]])
   file=save(m,stem+str(i));entries.append(dict(file=file,body='world',rgba=rgba))
  else:
   file=save(m,'toggle'+str(i))
   for x,z,yaw in [(0,-1.8148,0),(1.8148,0,-90),(0,1.8148,180),(-1.8148,0,90)]:
    rot=Rotation.from_euler('y',yaw,degrees=True)*Rotation.from_euler('x',30,degrees=True)
    entries.append(dict(file=file,body='world',rgba=rgba,position=[x,.3353,z],rotation=rot.as_quat().tolist()))
 print(stem,'exported',flush=True)
(out/'manifest.json').write_text(json.dumps(dict(meshes=entries,scope='Drawing-audited stadium presentation; full dimensional/contact acceptance pending',sourceCommit='572085f57dcedb501d781db6c5485349beb887cf'),indent=2));(out/'COPYING.txt').write_bytes((P/'Research/scoring-LICENSE').read_bytes());(out/'SOURCE.txt').write_text('Reused from https://github.com/Jerrylum/vex-v5-scoring-practice-override at 572085f57dcedb501d781db6c5485349beb887cf. GPL-3.0. Modified coordinate transforms, bounded-error simplification and mesh format.\n')
(P/'Evidence/v2/stadium-export.json').write_text(json.dumps(dict(meshes=stats,instances=len(entries),triangles=sum(next(s['triangles'] for s in stats if s['file']==e['file']) for e in entries)),indent=2))
