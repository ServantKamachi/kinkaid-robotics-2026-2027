"""Cross-section audit of source shell versus the union of physical convex hulls.
Finite sampled heights, not a whole-surface error certificate. Source triangle-plane segments are used directly because source sections contain open paths; source solid area is not inferred. Internal hull seams
are removed by planar union; a solid hull filling the bore is therefore detected.
"""
from pathlib import Path
import json, hashlib, argparse
import numpy as np
import trimesh
from scipy.spatial import ConvexHull
from shapely.geometry import Polygon, MultiLineString
from shapely.ops import unary_union
P=Path(__file__).resolve().parents[1]
A=P/'Unity/Assets/StreamingAssets'

def prepare_hull(vertices):
    v=np.asarray(vertices);h=ConvexHull(v)
    edges=set(tuple(sorted((int(a),int(b)))) for f in h.simplices for a,b in zip(f,np.roll(f,1)))
    return v,edges

def hull_section(vertices,z,prepared=None):
    v,edges=prepared if prepared is not None else prepare_hull(vertices)
    if z<=v[:,2].min() or z>=v[:,2].max():return Polygon()
    points=[]
    for a,b in edges:
        lo,hi=v[a],v[b]
        if (lo[2]-z)*(hi[2]-z)<0:
            points.append((lo+(hi-lo)*(z-lo[2])/(hi[2]-lo[2]))[:2])
    if len(points)<3:return Polygon()
    points=np.unique(np.round(points,12),axis=0)
    if len(points)<3:return Polygon()
    return Polygon(points[ConvexHull(points).vertices])

def source_section(mesh,z):
    segments=trimesh.intersections.mesh_plane(mesh,plane_normal=[0,0,1],plane_origin=[0,0,z])
    return MultiLineString(segments[:,:,:2].tolist())

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--contacts',default='Unity/Assets/StreamingAssets/Stadium/contacts.json');parser.add_argument('--output',default='Evidence/v2/goal-contact-sections.json');args=parser.parse_args()
    source=P/'work/v2/components/9.ply';mesh=trimesh.load(source)
    mesh.merge_vertices();mesh.update_faces(mesh.nondegenerate_faces());mesh.update_faces(mesh.unique_faces());mesh.remove_unreferenced_vertices()
    bounds=mesh.bounds.copy();mesh.vertices[:,:2]-=bounds.mean(axis=0)[:2];mesh.vertices[:,2]-=bounds[0,2]
    mesh.vertices[:,:2]*=.1425/np.diff(bounds,axis=0)[0,:2];mesh.vertices[:,2]*=.0825/np.ptp(mesh.vertices[:,2])
    contact=P/args.contacts;data=json.loads(contact.read_text());parts=[e for e in data['meshes'] if e['name'].startswith('goal_shell_')]
    prepared=[prepare_hull(p['vertices']) for p in parts]
    rows=[]
    for z in np.linspace(.00025,.08225,83):
        reference=source_section(mesh,z);physical=unary_union([hull_section(None,z,q) for q in prepared])
        if reference.is_empty or physical.is_empty:raise ValueError(f'Missing section at {z}')
        rows.append(dict(heightMm=float(z*1000),boundaryHausdorffMm=float(reference.hausdorff_distance(physical.boundary)*1000),physicalAreaMm2=float(physical.area*1e6)))
    report=dict(scope=__doc__,sourceSHA256=hashlib.sha256(source.read_bytes()).hexdigest(),contactSHA256=hashlib.sha256(contact.read_bytes()).hexdigest(),normalization='Same nominal goal-shell normalization as contact exporter; source mesh is not official CAD',sections=rows,maxSampledBoundaryErrorMm=max(r['boundaryHausdorffMm'] for r in rows),status='MEASURED_ONLY; official source fidelity and unsampled surfaces remain unvalidated')
    (P/args.output).write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps({k:v for k,v in report.items() if k!='sections'}))
