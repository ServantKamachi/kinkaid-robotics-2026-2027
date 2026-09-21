"""Rigid non-convex goal contact trial, isolated from production assets.

MuJoCo documents rigid flexes as non-convex triangle contacts:
https://mujoco.readthedocs.io/en/latest/modeling.html#deformable-objects
No deformable degrees of freedom or artificial attachment forces are added.
Surface thickness is 0.05 mm; containment and numerical tests remain required.
"""
from pathlib import Path
import argparse, hashlib, json, time
import xml.etree.ElementTree as X
import meshoptimizer as mo
import numpy as np
import trimesh

P = Path(__file__).resolve().parents[1]
a = argparse.ArgumentParser()
a.add_argument('--error-mm', type=float, default=.1)
a.add_argument('--tag', default='rigid-flex')
a.add_argument('--weld-digits', type=int, default=8,
               help='Trial vertex merge precision in meters; section audit must be rerun')
args = a.parse_args()
start = time.time()
source = P / 'work/v2/components/9.ply'
m = trimesh.load(source)
m.merge_vertices(digits_vertex=args.weld_digits)
m.update_faces(m.nondegenerate_faces())
m.update_faces(m.unique_faces())
m.remove_unreferenced_vertices()
b = m.bounds.copy()
m.vertices[:, :2] -= b.mean(axis=0)[:2]
m.vertices[:, 2] -= b[0, 2]
m.vertices[:, :2] *= .1425 / np.diff(b, axis=0)[0, :2]
m.vertices[:, 2] *= .0825 / np.ptp(m.vertices[:, 2])
vertices = np.asarray(m.vertices, np.float32)
indices = np.asarray(m.faces, np.uint32).reshape(-1)
result = np.empty_like(indices)
error = np.zeros(1, np.float32)
n = mo.simplify(result, indices, vertices, target_index_count=3,
                target_error=args.error_mm / 1000,
                options=mo.SIMPLIFY_ERROR_ABSOLUTE, result_error=error)
m = trimesh.Trimesh(vertices, result[:n].reshape(-1, 3), process=True)
m.update_faces(m.nondegenerate_faces())
m.remove_unreferenced_vertices()
mesh = P / f'work/v2/goal-{args.tag}.obj'
m.export(mesh)
root = X.parse(P / 'Unity/Assets/StreamingAssets/stadium.xml').getroot()
asset = root.find('asset')
for entry in list(asset):
    if entry.get('name', '').startswith('goal_shell'):
        asset.remove(entry)
count = 0
for body in root.findall('.//worldbody/body'):
    if not body.get('name', '').startswith('goal') or body.get('name', '').endswith('base'):
        continue
    for geom in list(body.findall('geom')):
        body.remove(geom)
    flex = X.SubElement(body, 'flexcomp', name=body.get('name') + '_surface',
                        type='mesh', file=str(mesh), rigid='true', radius='.000025')
    X.SubElement(flex, 'contact', selfcollide='none', internal='false',
                 friction='.65 .003 .0001', solref='.008 1',
                 solimp='.95 .99 .001', condim='4', margin='.0002')
    count += 1
assert count == 9
target = P / f'work/v2/stadium-{args.tag}.xml'
X.indent(root)
X.ElementTree(root).write(target, encoding='unicode')
report = dict(scope=__doc__, sourceSHA256=hashlib.sha256(source.read_bytes()).hexdigest(),
              weldDigits=args.weld_digits,
              model=str(target), mesh=str(mesh), goals=count, trianglesPerGoal=len(m.faces),
              verticesPerGoal=len(m.vertices), reportedSimplificationErrorMm=float(error[0]) * 1000,
              contactRadiusMm=.025, seconds=time.time() - start,
              status='UNADOPTED; contact evidence API must handle flex contacts before integration')
(P / f'Evidence/v2/goal-{args.tag}.json').write_text(json.dumps(report, indent=2))
print(json.dumps(report))
