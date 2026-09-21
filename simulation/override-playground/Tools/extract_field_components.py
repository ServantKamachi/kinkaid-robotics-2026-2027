"""Extract connected CAD components from the reused GPL field, without rebuilding each tiny fastener."""
import trimesh,numpy as np,json
from scipy.sparse import coo_matrix
from scipy.sparse.csgraph import connected_components
from pathlib import Path
P=Path(__file__).resolve().parents[1];out=P/'work/v2/components';out.mkdir(exist_ok=True);rows=[]
s=trimesh.load(P/'Research/Assets/V5RC-Override-H2H-_-FieldElements.glb')
for node in s.graph.nodes_geometry:
 tf,key=s.graph[node];m=s.geometry[key].copy();m.apply_transform(tf);v=m.vertices.copy();v[:,1]*=-1;v[:,2]+=.2943392;f=m.faces[:,::-1].copy()
 edges=np.concatenate([f[:,[0,1]],f[:,[1,2]],f[:,[2,0]]]);graph=coo_matrix((np.ones(len(edges)),(edges[:,0],edges[:,1])),shape=(len(v),len(v))).tocsr();n,lab=connected_components(graph,directed=False)
 fl=lab[f[:,0]];order=np.argsort(fl);cuts=np.flatnonzero(np.diff(fl[order]))+1
 for inds in np.split(order,cuts):
  faces=f[inds];used=np.unique(faces);vv=v[used];bounds=np.array([vv.min(axis=0),vv.max(axis=0)]);ext=bounds[1]-bounds[0]
  if max(ext)<.04 or np.prod(ext)<1e-6:continue
  mesh=trimesh.Trimesh(vv,np.searchsorted(used,faces),process=False);i=len(rows);mesh.export(out/f'{i}.ply');rows.append(dict(i=i,material=m.visual.material.name,color=m.visual.material.main_color.tolist(),bounds=bounds.tolist(),faces=len(faces)))
 print(key,n,'components',len(rows),'retained',flush=True)
(P/'Evidence/v2/field-components.json').write_text(json.dumps(rows,indent=2))
