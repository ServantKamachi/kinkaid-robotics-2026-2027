"""Read-only pose screen below the current lift stop; not authorization to change it.
Native structural contacts omit some detailed source interfaces. Exact CAD checks
and mounting validation remain required before extending physical travel.
"""
from pathlib import Path
import json,hashlib
import mujoco as mj,numpy as np
P=Path(__file__).resolve().parents[1];path=P/'Unity/Assets/StreamingAssets/playground.xml';m=mj.MjModel.from_xml_path(str(path));d=mj.MjData(m);rows=[]
rollers=[g for g in range(m.ngeom) if m.geom(g).name.startswith(('rollerL-','rollerR-'))]
assert rollers
for angle in np.linspace(-.60,-.65,51):
 worst=[];floor=[];bottoms=[]
 for jaw in [.17453,.6,1.0472]:
  for name in ['lift','lower_parallel','rear_upright','upper_lift','upper_parallel','claw_upright','jawL','jawR']:
   d.qpos[m.joint(name).qposadr[0]]=jaw if name.startswith('jaw') else -angle if name=='rear_upright' else angle
  mj.mj_forward(m,d)
  for g in rollers:
   axis=d.geom_xmat[g].reshape(3,3)[:,2];z=d.geom_xpos[g,2]-abs(axis[2])*m.geom_size[g,1]-np.sqrt(max(0,1-axis[2]**2))*m.geom_size[g,0];bottoms.append(float(z))
  for c in d.contact:
   if c.dist>=-1e-6:continue
   ids=list(map(int,c.geom));names=[m.geom(g).name for g in ids]
   record=dict(geoms=names,penetrationMm=float(-c.dist*1000),jaw=jaw)
   if all(m.geom_contype[g]==2 for g in ids):worst.append(record)
   if 'floor' in names and any(m.geom_contype[g]==2 for g in ids):floor.append(record)
 rows.append(dict(lift=float(angle),lowestRollerMm=min(bottoms)*1000,structuralContacts=worst,floorContacts=floor))
report=dict(scope=__doc__,modelSHA256=hashlib.sha256(path.read_bytes()).hexdigest(),poses=153,rows=rows)
(P/'Evidence/v2/ground-access-screen.json').write_text(json.dumps(report,indent=2));print(json.dumps([r for i,r in enumerate(rows) if i%10==0]))
