"""Contact trial using convex planar source patches with 0.05 mm sheet thickness.
Writes only work/: source fidelity and physical containment require independent tests.
Triangles are projected within a recorded plane tolerance, then merge only when their planar union remains convex (area checked).
"""
from pathlib import Path
import json,hashlib,time,argparse
import numpy as np,trimesh,meshoptimizer as mo
from shapely.geometry import Polygon
from shapely.ops import unary_union
from scipy.spatial import ConvexHull
P=Path(__file__).resolve().parents[1];start=time.time()
parser=argparse.ArgumentParser();parser.add_argument('--error-mm',type=float,default=.1);parser.add_argument('--tag',default='facet-trial');parser.add_argument('--grow',action='store_true');args=parser.parse_args()
source=P/'work/v2/components/9.ply';m=trimesh.load(source)
m.merge_vertices();m.update_faces(m.nondegenerate_faces());m.update_faces(m.unique_faces());m.remove_unreferenced_vertices()
b=m.bounds.copy();m.vertices[:,:2]-=b.mean(axis=0)[:2];m.vertices[:,2]-=b[0,2];m.vertices[:,:2]*=.1425/np.diff(b,axis=0)[0,:2];m.vertices[:,2]*=.0825/np.ptp(m.vertices[:,2])
input_triangles=len(m.faces)
v=np.asarray(m.vertices,np.float32);idx=np.asarray(m.faces,np.uint32).reshape(-1);dest=np.empty_like(idx);simplify_error=np.zeros(1,np.float32)
n=mo.simplify(dest,idx,v,target_index_count=3,target_error=args.error_mm/1000,options=mo.SIMPLIFY_ERROR_ABSOLUTE,result_error=simplify_error)
m=trimesh.Trimesh(v,dest[:n].reshape(-1,3),process=True);m.update_faces(m.nondegenerate_faces());m.remove_unreferenced_vertices()
facets=list(m.facets);covered=set(int(i) for f in facets for i in f);facets.extend(np.array([i]) for i in range(len(m.faces)) if i not in covered)
if args.grow:
 adjacency=[[] for _ in m.faces]
 for a,b in m.face_adjacency:adjacency[a].append(b);adjacency[b].append(a)
 assigned=set();facets=[]
 for seed in np.argsort(-m.area_faces):
  if seed in assigned:continue
  normal=m.face_normals[seed];origin=m.triangles[seed,0];patch=[seed];assigned.add(seed);queue=[seed]
  while queue:
   for neighbor in adjacency[queue.pop()]:
    if neighbor in assigned:continue
    if np.dot(normal,m.face_normals[neighbor])<np.cos(np.radians(20)):continue
    if abs((m.triangles[neighbor]-origin)@normal).max()>.0001:continue
    patch.append(neighbor);assigned.add(neighbor);queue.append(neighbor)
  facets.append(np.array(patch))
plane_tolerance=.0001 if args.grow else .000025
refined=[]
for f in facets:
 error=abs((m.triangles[f]-m.triangles[f[0],0])@m.face_normals[f[0]]).max()
 refined.extend([f] if error<=plane_tolerance else [np.array([i]) for i in f])
facets=refined
parts=[];max_plane_error=0.
for facet in facets:
 normal=m.face_normals[facet[0]];origin=m.triangles[facet[0],0];axis=m.triangles[facet[0],1]-origin;axis/=np.linalg.norm(axis);other=np.cross(normal,axis);basis=np.array([axis,other])
 triangles=m.triangles[facet];err=float(abs((triangles-origin)@normal).max());max_plane_error=max(max_plane_error,err)
 # Flattening error is bounded separately from the contact sheet thickness.
 assert err<=plane_tolerance,err
 polygons={i:Polygon((tri-origin)@basis.T) for i,tri in enumerate(triangles)}
 changed=True
 while changed:
  changed=False;edges={};neighbors=set()
  for i,p in polygons.items():
   coords=np.array(p.exterior.coords)[:-1]
   for a,b in zip(coords,np.roll(coords,-1,axis=0)):
    key=tuple(sorted((tuple(np.round(a,9)),tuple(np.round(b,9)))))
    if key in edges:neighbors.add(tuple(sorted((i,edges[key]))))
    else:edges[key]=i
  for a,b in sorted(neighbors):
   if a not in polygons or b not in polygons:continue
   x,y=polygons[a],polygons[b];joined=unary_union([x,y]);h=joined.convex_hull
   if joined.geom_type=='Polygon' and h.area-joined.area<1e-12:
    polygons[a]=h;del polygons[b];changed=True
 for p in polygons.values():
  xy=np.asarray(p.exterior.coords)[:-1];vertices=origin+xy@basis
  vv=np.concatenate([vertices+normal*.000025,vertices-normal*.000025])
  parts.append(dict(name=f'goal_shell_facet_{len(parts)}',vertices=vv.tolist()))
data=json.loads((P/'Unity/Assets/StreamingAssets/Stadium/contacts.json').read_text());data['meshes']=[e for e in data['meshes'] if not e['name'].startswith('goal_shell')]+parts
for body in data['bodies']:
 if body['name'].startswith('goal') and not body['name'].endswith('base'):body['meshes']=[p['name'] for p in parts]
(P/f'work/v2/contacts-{args.tag}.json').write_text(json.dumps(data,separators=(',',':')))
report=dict(scope=__doc__,sourceSHA256=hashlib.sha256(source.read_bytes()).hexdigest(),sourceTriangles=input_triangles,simplifiedTriangles=len(m.faces),grown=args.grow,planeToleranceMm=plane_tolerance*1000,facets=len(facets),contactPatches=len(parts),maxPlaneErrorMm=max_plane_error*1000,thicknessMm=.05,simplificationReportedErrorMm=float(simplify_error[0])*1000,seconds=time.time()-start)
(P/f'Evidence/v2/goal-{args.tag}.json').write_text(json.dumps(report,indent=2));print(json.dumps(report))
