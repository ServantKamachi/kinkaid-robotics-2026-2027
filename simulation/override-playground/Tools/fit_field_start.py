"""Resolve contact-fit z/radial offsets without altering drawing-backed cluster centers.
Not an official-CAD pose certification: the source drawings omit these free-object
resting offsets. Result explicitly retains that limitation for the release gate.
"""
from pathlib import Path
import mujoco,json,numpy as np
P=Path(__file__).resolve().parents[1];A=P/'Unity/Assets/StreamingAssets';path=A/'StadiumPieces/scenario.json';s=json.loads(path.read_text());m=mujoco.MjModel.from_xml_path(str(A/'stadium.xml'));d=mujoco.MjData(m)
# Only game piece placement is fitted, with the robot at its normal lowered pose.
for name,target in [('lift',-.6),('lower_parallel',-.6),('rear_upright',.6),('upper_lift',-.6),('upper_parallel',-.6),('claw_upright',-.6),('jawL',1.047),('jawR',1.047)]:d.qpos[m.joint(name).qposadr]=target
checks=[]
def penetration(bid):
 mujoco.mj_kinematics(m,d);mujoco.mj_collision(m,d);return max([0]+[-float(c.dist) for c in d.contact if bid in m.geom_bodyid[c.geom]])
for p in s['pieces']:
 if p['state']!='Field' or p['kind']=='cup':continue
 bid=m.body(p['id']).id;q=int(m.jnt_qposadr[m.body_jntadr[bid]]);initial=d.qpos[q:q+3].copy();horizontal=p['group']=='cross cluster'
 if horizontal:
  quat=d.qpos[q+3:q+7];mat=np.zeros(9);mujoco.mju_quat2Mat(mat,quat);direction=mat.reshape(3,3)[:,2]
 else:direction=np.array([0.,0,1])
 before=penetration(bid);offset=0.
 # Monotone outward escape search, then sub-0.1 mm bracket refinement.
 if before>.00005:
  low=0.;high=.080
  d.qpos[q:q+3]=initial+high*direction
  assert penetration(bid)<.00005,(p['id'],'No bounded escape')
  for _ in range(10):
   middle=(low+high)/2;d.qpos[q:q+3]=initial+middle*direction
   if penetration(bid)>.00005:low=middle
   else:high=middle
  offset=high;d.qpos[q:q+3]=initial+offset*direction
 after=penetration(bid);assert after<.0001,(p['id'],after,offset)
 p['position']=d.qpos[q:q+3].tolist();p['contactFitOffsetMeters']=round(offset,6);p['verticalStatus']='Contact-fitted development reset, exact official free-object resting pose still unverified'
 if horizontal:p['placementSource']='A12 cluster center; radial contact fit (NOT dimensioned individual-pin XY)'
 print(p['id'],round(offset*1000,2),flush=True)
 checks.append(dict(id=p['id'],initialPenetrationMm=before*1000,offsetMm=offset*1000,finalPenetrationMm=after*1000))
s['status']='Drawing-backed group centers with contact-fitted reset poses; exact free-object pose audit still pending';path.write_text(json.dumps(s,indent=2)+'\n');(P/'Evidence/v2/field-start-fit.json').write_text(json.dumps(dict(status='Contact-fit only, not official dimensional acceptance',pieces=checks),indent=2));print('FITTED',len(checks),'max offset mm',max(x['offsetMm'] for x in checks))
