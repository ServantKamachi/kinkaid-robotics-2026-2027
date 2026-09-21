"""Run in headless FreeCAD after audit_assembly.py; original CAD remains read-only."""
import FreeCAD as A,json,hashlib
from pathlib import Path
P=Path('/Users/kamachi/Documents/OverridePlayground')
D=A.openDocument(str(P/'CAD/RatchetingClaw-Simulation.FCStd'))
entries={e['name']:e for e in json.loads((P/'work/v2/cad-raw/manifest.json').read_text())['meshes']}
suffix=globals().get('AUDIT_SUFFIX','')
rows=[]
cases=json.loads((P/('work/v2/solid-candidates'+suffix+'.json')).read_text())
selection=globals().get('AUDIT_INDICES')
if selection is not None:cases=[cases[i] for i in selection]
output_suffix=suffix+globals().get('AUDIT_OUTPUT_SUFFIX','')
for case in cases:
    print('CHECK',case['names'],flush=True)
    shapes=[]
    for name in case['names']:
        o=D.getObject(name);src=o.LinkedObject if o.TypeId=='App::Link' else o
        shape=src.Shape.copy();shape.Placement=A.Placement()
        e=entries[name];p=e['position'];q=e['rotation']
        local=A.Placement(A.Vector(p[0]*1000,p[2]*1000,p[1]*1000),A.Rotation(-q[0],-q[2],-q[1],q[3]))
        # Trial-only per-part offsets in the native body frame (millimeters).
        # Keep the rest of that body and the original CAD unchanged.
        offset=case.get('partOffsetsMm',{}).get(name,[0,0,0])
        local.Base=local.Base+A.Vector(*offset)
        pose=case['poses'][e['body']];p=pose['position'];q=pose['quat']
        world=A.Placement(A.Vector(*[v*1000 for v in p]),A.Rotation(q[1],q[2],q[3],q[0]))
        shape.Placement=world.multiply(local);shapes.append(shape)
    volume=0.0;distance=1e9;checked=0
    for sa in shapes[0].Solids:
        for sb in shapes[1].Solids:
            ba,bb=sa.BoundBox,sb.BoundBox
            # Only skip when an axis proves at least the 1 mm design clearance.
            gap_lower=max(ba.XMin-bb.XMax,bb.XMin-ba.XMax,ba.YMin-bb.YMax,bb.YMin-ba.YMax,ba.ZMin-bb.ZMax,bb.ZMin-ba.ZMax,0)
            if gap_lower>=1:continue
            gap=sa.distToShape(sb)[0];distance=min(distance,gap)
            if gap<1e-6:
                volume+=sa.common(sb).Volume
            checked+=1
            if volume>.01:break
        if volume>.01:break
    if distance==1e9:distance=None
    row=dict(names=case['names'],lift=case['lift'],jaw=case['jaw'],overlapMm3=volume,distanceMm=distance,clearanceAtLeastMm=1.0 if distance is None else min(distance,1.0))
    if case.get('partOffsetsMm'):row['partOffsetsMm']=case['partOffsetsMm']
    names=set(case['names'])
    gear_contact=names in [set(pair) for pair in [('I_gear60','I_gear36'),('I_gear001','I_gear002'),('I_gear003','I_gear004'),('I_gear005','I_gear006'),('I_gear007','I_gear008'),('I_gear009','I_gear010'),('I_gear017','I_gear016'),('I_gear016','I_gear018'),('I_gear019','I_gear018')]]
    shaft_bore=bool(names & {'Detail034','Detail041'}) and any(n.startswith('I_channel2_') for n in names)
    spacer_seat=names in [set(['ClawDetail003','I_channel2_019']),set(['ClawDetail011','I_channel2_021'])]
    row['interfaceClass']='meshing gears' if gear_contact else 'shaft clearance bore' if shaft_bore else 'spacer seat' if spacer_seat else 'non-contact'
    row['meetsSampledClearanceTarget']=row['overlapMm3']<.01 and (row['interfaceClass']!='non-contact' or row['clearanceAtLeastMm']>=1)
    rows.append(row);print(row,flush=True)
    (P/('Evidence/v2/assembly-solid-audit'+output_suffix+'-partial.json')).write_text(json.dumps(rows,indent=2))
report=dict(cadSHA256=hashlib.sha256((P/'CAD/RatchetingClaw-Simulation.FCStd').read_bytes()).hexdigest(),status='PASS' if all(r['overlapMm3']<.01 for r in rows) else 'FAIL',sampledClearanceStatus='PASS' if all(r['meetsSampledClearanceTarget'] for r in rows) else 'FAIL',scope='Exact OCCT solids at maximum sampled bounding-box overlap for selected detailed part pairs; adjacency included when requested; not exhaustive continuous proof',cases=rows)
(P/('Evidence/v2/assembly-solid-audit'+output_suffix+'.json')).write_text(json.dumps(report,indent=2)+'\n')
