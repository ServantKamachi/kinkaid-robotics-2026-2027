"""Bounded-error meshoptimizer simplification, sharp-edge normals, shared CAD instances."""
from pathlib import Path
import struct,json,numpy as np,trimesh,meshoptimizer as mo
P=Path(__file__).resolve().parents[1];src=P/'work/v2/cad-raw';out=P/'Unity/Assets/StreamingAssets/Robot';out.mkdir(exist_ok=True)
m=json.loads((src/'manifest.json').read_text());stats={}
for file in dict.fromkeys(e['file'] for e in m['meshes']):
 a=(src/file).read_bytes();nv,ni=struct.unpack_from('<ii',a);v=np.frombuffer(a,np.float32,nv*3,8).reshape(-1,3).copy();idx=np.frombuffer(a,np.uint32,ni,8+nv*12).copy();dest=np.empty_like(idx);err=np.zeros(1,np.float32)
 n=mo.simplify(dest,idx,v,target_index_count=int(ni*.10)//3*3,target_error=.00012,options=mo.SIMPLIFY_ERROR_ABSOLUTE|mo.SIMPLIFY_LOCK_BORDER,result_error=err)
 mesh=trimesh.Trimesh(v,dest[:n].reshape(-1,3),process=False);mesh.remove_unreferenced_vertices();mesh=trimesh.graph.smooth_shade(mesh,angle=np.radians(35))
 vv=np.asarray(mesh.vertices,dtype='<f4');ff=np.asarray(mesh.faces,dtype='<i4');norm=np.asarray(mesh.vertex_normals,dtype='<f4')
 (out/file).write_bytes(struct.pack('<ii',len(vv),ff.size)+vv.tobytes()+ff.tobytes()+norm.tobytes());stats[file]={'inputTriangles':ni//3,'triangles':n//3,'vertices':len(vv),'maximumErrorMeters':float(err[0])}
for e in m['meshes']:e.update(stats[e['file']])
m['optimization']='meshoptimizer 0.2.30a0, 0.12 mm absolute geometric error limit, locked borders, 35 degree sharp-edge normals'
(out/'manifest.json').write_text(json.dumps(m,indent=2));(P/'Evidence/v2/cad-optimization.json').write_text(json.dumps(stats,indent=2))
print(len(stats),'meshes',len(m['meshes']),'parts',sum(e['triangles'] for e in m['meshes']),'instanced triangles')
