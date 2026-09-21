"""Unadopted contact-layout feasibility trial for reachable intake travel.
Moves only collision housings and frame plates, plus full jaw subtrees. This is
not a coherent CAD assembly and MUST NOT replace production geometry directly.
Source gear alignment, drive shafts, supports and fasteners remain unresolved.
"""
from pathlib import Path
import xml.etree.ElementTree as X,json,numpy as np,mujoco as mj
P=Path(__file__).resolve().parents[1];src=P/'Unity/Assets/StreamingAssets/playground.xml';out=P/'work/v2/motion-layout-clear';out.mkdir(exist_ok=True);rows=[]
for setback in [63.5,76.2,88.9]:
 for forward in [25.4]:
  root=X.parse(src).getroot()
  for n in ['I_motor006','I_motor007']:
   g=root.find(f".//geom[@name='housing_{n}']");p=np.fromstring(g.get('pos','0 0 0'),sep=' ');p[1]+=setback/1000;g.set('pos',' '.join(map(str,p)))
  for side in ['L','R']:
   b=root.find(f".//body[@name='jaw{side}']");p=np.fromstring(b.get('pos'),sep=' ');p[1]-=forward/1000;b.set('pos',' '.join(map(str,p)))
  for n in ['I_motor11','I_motor003']:
   g=root.find(f".//geom[@name='housing_{n}']");p=np.fromstring(g.get('pos','0 0 0'),sep=' ');p[0]+=(1 if n=='I_motor11' else -1)*.0508;g.set('pos',' '.join(map(str,p)))
  for g in root.findall('.//geom'):
   name=g.get('name','')
   if name.startswith('cad_I_channel3_23_'):
    p=np.fromstring(g.get('pos'),sep=' ');p[1]+=.0508;g.set('pos',' '.join(map(str,p)))
   if name.startswith('cad_I_channel2_19_'):
    p=np.fromstring(g.get('pos'),sep=' ');p[2]+=.0508;g.set('pos',' '.join(map(str,p)))
  path=out/f'setback{setback}-forward{forward}.xml';X.ElementTree(root).write(path,encoding='unicode');m=mj.MjModel.from_xml_path(str(path));d=mj.MjData(m);bad={}
  for angle in [-.72,-.66,-.6,0,.0873]:
   for jaw in [.17453,.785398,1.3962634]:
    for n in ['lift','lower_parallel','rear_upright','upper_lift','upper_parallel','claw_upright','jawL','jawR']:d.qpos[m.joint(n).qposadr[0]]=jaw if n.startswith('jaw') else -angle if n=='rear_upright' else angle
    mj.mj_forward(m,d)
    for c in d.contact:
     if c.dist<-.000001 and all(m.geom_contype[g]==2 for g in c.geom):
      key=' | '.join(m.geom(int(g)).name for g in c.geom);bad[key]=max(bad.get(key,0),float(-c.dist*1000))
  rows.append(dict(model=str(path),setbackMm=setback,jawForwardMm=forward,penetrationsMm=bad));print(setback,forward,'pairs',len(bad),flush=True)
(P/'Evidence/v2/motion-layout-clear-trial.json').write_text(json.dumps(dict(scope='Collider feasibility only; lift motor transmissions/supports not moved in CAD. Jaw bodies translate together including rollers/gears; mounting not validated. Never adopt directly.',cases=rows),indent=2))
