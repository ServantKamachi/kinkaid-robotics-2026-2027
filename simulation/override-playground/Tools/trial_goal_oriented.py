"""Trial only: keep inner, outer and rib surfaces in separate contact hulls.

Partition source surfaces by local normal direction before connected-component
grouping. This prevents a hull bridging opposite sides of a hollow wall. Curved
patches still need the independent section audit; no production assets change.
"""
from pathlib import Path
import argparse, json, math, time
import numpy as np
import trimesh
from scipy.spatial import ConvexHull, QhullError

P = Path(__file__).resolve().parents[1]
a = argparse.ArgumentParser()
a.add_argument('--sectors', type=int, default=24)
a.add_argument('--bands', type=int, default=5)
a.add_argument('--tag', default='oriented-trial')
a.add_argument('--join', action='store_true', help='Trial merge of disconnected surfaces sharing a normal class')
a.add_argument('--simplify-mm', type=float, default=0)
a.add_argument('--repair-winding', action='store_true')
args = a.parse_args()
started = time.time()
m = trimesh.load(P / 'work/v2/components/9.ply')
m.merge_vertices()
m.update_faces(m.nondegenerate_faces())
m.update_faces(m.unique_faces())
m.remove_unreferenced_vertices()
if args.repair_winding:
    m.fix_normals(multibody=True)
bounds = m.bounds.copy()
m.vertices[:, :2] -= bounds.mean(axis=0)[:2]
m.vertices[:, 2] -= bounds[0, 2]
m.vertices[:, :2] *= .1425 / np.diff(bounds, axis=0)[0, :2]
m.vertices[:, 2] *= .0825 / np.ptp(m.vertices[:, 2])
if args.simplify_mm:
    import meshoptimizer as mo
    vertices = np.asarray(m.vertices, np.float32)
    indices = np.asarray(m.faces, np.uint32).reshape(-1)
    result = np.empty_like(indices)
    n = mo.simplify(result, indices, vertices, target_index_count=3,
                    target_error=args.simplify_mm / 1000,
                    options=mo.SIMPLIFY_ERROR_ABSOLUTE)
    m = trimesh.Trimesh(vertices, result[:n].reshape(-1, 3), process=True)
parts = []
for k in range(args.sectors):
    lo, hi = np.array([k, k + 1]) * 2 * math.pi / args.sectors
    sector = m.slice_plane([0, 0, 0], [-math.sin(lo), math.cos(lo), 0])
    sector = sector.slice_plane([0, 0, 0], [math.sin(hi), -math.cos(hi), 0])
    mid = (lo + hi) / 2
    basis = np.array([[math.cos(mid), math.sin(mid), 0],
                      [-math.sin(mid), math.cos(mid), 0], [0, 0, 1]])
    cuts = np.linspace(-.000001, .082501, args.bands + 1)
    for z0, z1 in zip(cuts, cuts[1:]):
        band = sector.slice_plane([0, 0, z0], [0, 0, 1])
        band = band.slice_plane([0, 0, z1], [0, 0, -1])
        if not len(band.faces):
            continue
        normals = band.face_normals @ basis.T
        axis = np.abs(normals).argmax(axis=1)
        labels = axis * 2 + (normals[np.arange(len(axis)), axis] < 0)
        for label in range(6):
            indices = np.where(labels == label)[0]
            if not len(indices):
                continue
            surfaces = band.submesh([indices], append=True)
            surfaces.merge_vertices()
            for patch in ([surfaces] if args.join else surfaces.split(only_watertight=False)):
                # Give zero-volume sheets 0.05 mm total thickness; do not
                # inflate the whole hull or introduce a broad collision skin.
                vertices = np.asarray(patch.vertices)
                if len(vertices) < 3:
                    continue
                _, singular, vectors = np.linalg.svd(vertices - vertices.mean(axis=0), full_matrices=False)
                if len(singular) < 3 or singular[-1] < 1e-8:
                    normal = vectors[-1]
                    vertices = np.concatenate([vertices + normal * .000025,
                                               vertices - normal * .000025])
                try:
                    hull = ConvexHull(vertices)
                except QhullError:
                    continue
                parts.append(dict(name=f'goal_shell_oriented_{len(parts)}',
                                  vertices=vertices[hull.vertices].tolist()))
data = json.loads((P / 'Unity/Assets/StreamingAssets/Stadium/contacts.json').read_text())
data['meshes'] = [p for p in data['meshes'] if not p['name'].startswith('goal_shell')] + parts
for body in data['bodies']:
    if body['name'].startswith('goal') and not body['name'].endswith('base'):
        body['meshes'] = [p['name'] for p in parts]
(P / f'work/v2/contacts-{args.tag}.json').write_text(json.dumps(data, separators=(',', ':')))
report = dict(scope=__doc__, sectors=args.sectors, bands=args.bands, joined=args.join,
              simplificationLimitMm=args.simplify_mm,
              repairedWinding=args.repair_winding,
              shellHulls=len(parts), seconds=time.time() - started,
              status='TRIAL ONLY; independent geometry and performance checks required')
(P / f'Evidence/v2/goal-{args.tag}.json').write_text(json.dumps(report, indent=2))
print(json.dumps(report))
