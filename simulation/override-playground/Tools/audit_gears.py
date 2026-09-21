"""Run in headless FreeCAD after audit_assembly.py; original CAD remains read-only."""
import FreeCAD as A,json,hashlib
from pathlib import Path
P=Path('/Users/kamachi/Documents/OverridePlayground')
D=A.openDocument(str(P/'CAD/RatchetingClaw-Simulation.FCStd'))
entries={e['name']:e for e in json.loads((P/'work/v2/cad-raw/manifest.json').read_text())['meshes']}
suffix='-interfaces'
rows=[]
for case in json.loads((P/('work/v2/solid-candidates'+suffix+'.json')).read_text()):
    if case['names'] not in [['I_gear60','I_gear36'],['I_gear017','I_gear016'],['I_gear016','I_gear018']]:continue
    print('CHECK',case['names'],flush=True)
    shapes=[]
    for name in case['names']:
        o=D.getObject(name);src=o.LinkedObject if o.TypeId=='App::Link' else o
        shape=src.Shape.copy();shape.Placement=A.Placement()
        e=entries[name];p=e['position'];q=e['rotation']
        local=A.Placement(A.Vector(p[0]*1000,p[2]*1000,p[1]*1000),A.Rotation(-q[0],-q[2],-q[1],q[3]))
        pose=case['poses'][e['body']];p=pose['position'];q=pose['quat']
        world=A.Placement(A.Vector(*[v*1000 for v in p]),A.Rotation(q[1],q[2],q[3],q[0]))
        shape.Placement=world.multiply(local);shapes.append(shape)
    axis=A.Vector(1,0,0) if case['names'][0]=='I_gear60' else A.Vector(0,0,1)
    ratio=60/36 if case['names'][0]=='I_gear60' else 1
    values=[]
    for step in range(13):
        phase=step*.5;a=shapes[0].copy();b=shapes[1].copy()
        a.rotate(a.BoundBox.Center,axis,phase);b.rotate(b.BoundBox.Center,axis,-phase*ratio)
        volume=a.common(b).Volume;values.append(dict(angleDegrees=phase,overlapMm3=volume))
    row=dict(names=case['names'],samples=values);rows.append(row);print(row,flush=True)
assert len(rows)==3, 'Missing representative gear pairs'
report=dict(status='PASS' if all(v['overlapMm3']<.01 for row in rows for v in row['samples']) else 'FAIL',scope='Representative drivetrain and claw tooth cycles at 0.5 degree steps',cadSHA256=hashlib.sha256((P/'CAD/RatchetingClaw-Simulation.FCStd').read_bytes()).hexdigest(),cases=rows)
(P/'Evidence/v2/gear-cycle.json').write_text(json.dumps(report,indent=2))
