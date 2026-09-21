"""Experimental thin source-surface contacts. Writes only work/; not production.
Bounded simplification and +/-0.025mm surface thickness avoid filling cavities.
Source tessellation error and fast-motion tunneling still require separate tests.
"""
from pathlib import Path
import json,numpy as np,trimesh,meshoptimizer as mo
P=Path(__file__).resolve().parents[1]
m=trimesh.load(P/'work/v2/components/9.ply');m.merge_vertices();m.update_faces(m.nondegenerate_faces());m.update_faces(m.unique_faces());m.remove_unreferenced_vertices()
b=m.bounds.copy();m.vertices[:,:2]-=b.mean(axis=0)[:2];m.vertices[:,2]-=b[0,2];m.vertices[:,:2]*=.1425/np.diff(b,axis=0)[0,:2];m.vertices[:,2]*=.0825/np.ptp(m.vertices[:,2])
v=np.asarray(m.vertices,np.float32);idx=np.asarray(m.faces,np.uint32).reshape(-1);dest=np.empty_like(idx);err=np.zeros(1,np.float32)
n=mo.simplify(dest,idx,v,target_index_count=3,target_error=.0001,options=mo.SIMPLIFY_ERROR_ABSOLUTE,result_error=err)
m=trimesh.Trimesh(v,dest[:n].reshape(-1,3),process=False);m.update_faces(m.nondegenerate_faces());m.remove_unreferenced_vertices()
data=json.loads((P/'Unity/Assets/StreamingAssets/Stadium/contacts.json').read_text());data['meshes']=[e for e in data['meshes'] if not e['name'].startswith('goal_shell')];ids=[]
for i,(tri,normal) in enumerate(zip(m.triangles,m.face_normals)):
 name=f'goal_shell_surface_{i}';ids.append(name);vertices=np.concatenate([tri+normal*.000025,tri-normal*.000025]);data['meshes'].append(dict(name=name,vertices=vertices.tolist()))
for body in data['bodies']:
 if body['name'].startswith('goal') and not body['name'].endswith('base'):body['meshes']=ids
(P/'work/v2/contacts-surface-trial.json').write_text(json.dumps(data,separators=(',',':')))
report=dict(scope=__doc__,sourceTriangles=len(idx)//3,contactTriangles=len(ids),simplificationReportedErrorMeters=float(err[0]),thicknessMeters=.00005)
(P/'Evidence/v2/goal-surface-trial.json').write_text(json.dumps(report,indent=2));print(report,flush=True)
