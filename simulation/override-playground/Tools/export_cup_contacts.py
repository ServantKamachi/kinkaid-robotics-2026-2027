"""Replace provisional 2 mm wall with convex sectors of the actual licensed cup mesh.
Shared with field runtime; practice model stays unchanged until grip regression.
"""
from pathlib import Path
import json,numpy as np,trimesh
from scipy.spatial import ConvexHull
P=Path(__file__).resolve().parents[1];A=P/'Unity/Assets/StreamingAssets'
s=trimesh.load(P/'Research/Assets/V5RC-Override-H2H-_-Cup.glb');meshes=[]
for node in s.graph.nodes_geometry:
 tf,key=s.graph[node];m=s.geometry[key].copy();m.apply_transform(tf);v=m.vertices.copy();m.vertices=v[:,[0,2,1]];m.vertices[:,2]-=s.bounds[0,1];m.faces=m.faces[:,::-1];meshes.append(m)
m=trimesh.util.concatenate(meshes);parts=[]
for section,(z0,z1) in enumerate([(0,.008),(.008,.08225),(.08225,.1565),(.1565,.1645)]):
 band=m.slice_plane([0,0,z0-1e-7],[0,0,1]).slice_plane([0,0,z1+1e-7],[0,0,-1])
 for k in range(20):
  a=2*np.pi*k/20;b=2*np.pi*(k+1)/20;q=band.slice_plane([0,0,0],[-np.sin(a),np.cos(a),0]).slice_plane([0,0,0],[np.sin(b),-np.cos(b),0]);v=np.unique(q.vertices,axis=0);h=ConvexHull(v);parts.append(dict(name=f'cup_{section}_{k}',vertices=v[h.vertices].tolist()))
(A/'StadiumPieces/cup-collision.json').write_text(json.dumps(parts,separators=(',',':')));print('SOURCE_CUP_CONTACTS',len(parts))
