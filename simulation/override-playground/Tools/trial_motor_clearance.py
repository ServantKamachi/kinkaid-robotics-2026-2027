"""Recompiled collider-only feasibility search for lower lift travel.
Moves inferred motor housings in trial XML only. Does not certify gears, shafts,
mountings, mass distribution or source solids; production geometry is unchanged.
"""
from pathlib import Path
import xml.etree.ElementTree as X,json,hashlib
import mujoco as mj,numpy as np
P=Path(__file__).resolve().parents[1];source=P/'Unity/Assets/StreamingAssets/playground.xml';out=P/'work/v2/motor-clearance';out.mkdir(exist_ok=True);results=[]
drive=['I_motor11','I_motor001','I_motor002','I_motor003','I_motor004','I_motor005'];lift=['I_motor006','I_motor007']
for inset in [0,12.7,25.4,38.1,50.8]:
 for setback in [0,12.7,25.4,38.1]:
  root=X.parse(source).getroot()
  for i,name in enumerate(drive):
   g=root.find(f".//geom[@name='housing_{name}']");pos=np.fromstring(g.get('pos','0 0 0'),sep=' ');pos[0]+=(1 if i<3 else -1)*inset/1000;g.set('pos',' '.join(map(str,pos)))
  for name in lift:
   g=root.find(f".//geom[@name='housing_{name}']");pos=np.fromstring(g.get('pos','0 0 0'),sep=' ');pos[1]+=setback/1000;g.set('pos',' '.join(map(str,pos)))
  path=out/f'inset{inset}-setback{setback}.xml';X.ElementTree(root).write(path,encoding='unicode');m=mj.MjModel.from_xml_path(str(path));d=mj.MjData(m);rows=[]
  for angle in np.linspace(-.6,-.68,17):
   worst={}
   for jaw in [.17453,.6,1.0472]:
    for name in ['lift','lower_parallel','rear_upright','upper_lift','upper_parallel','claw_upright','jawL','jawR']:
     d.qpos[m.joint(name).qposadr[0]]=jaw if name.startswith('jaw') else -angle if name=='rear_upright' else angle
    mj.mj_forward(m,d)
    for c in d.contact:
     if c.dist<-.000001 and all(m.geom_contype[g]==2 for g in c.geom):
      key=' | '.join(m.geom(int(g)).name for g in c.geom);worst[key]=max(worst.get(key,0),float(-c.dist*1000))
   rows.append(dict(lift=float(angle),worst=worst))
  clear=[r['lift'] for r in rows if not r['worst']];result=dict(insetMm=inset,setbackMm=setback,lowestSampledClearAngle=min(clear) if clear else None,rows=rows);results.append(result)
  print(inset,setback,'clear',result['lowestSampledClearAngle'],flush=True)
report=dict(scope=__doc__,modelSHA256=hashlib.sha256(source.read_bytes()).hexdigest(),cases=results);(P/'Evidence/v2/motor-clearance-trial.json').write_text(json.dumps(report,indent=2)+'\n')
