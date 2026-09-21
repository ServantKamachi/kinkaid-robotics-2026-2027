"""Build independent full-field physics from the stable robot and audited field assets.
No off-field reserve bodies are compiled. Stadium-specific uncertainties remain in
Field/specification.json and Evidence/v2/stadium-contact-generation.json.
"""
from pathlib import Path
import xml.etree.ElementTree as X,json,copy,numpy as np,argparse
P=Path(__file__).resolve().parents[1];A=P/'Unity/Assets/StreamingAssets'
parser=argparse.ArgumentParser();parser.add_argument('--contacts',default=str(A/'Stadium/contacts.json'));parser.add_argument('--output',default=str(A/'stadium.xml'));args=parser.parse_args()
def vec(v):return ' '.join(f'{float(x):.9g}' for x in v)
def el(p,t,**a):return X.SubElement(p,t,{k:str(v) for k,v in a.items()})
r=X.parse(A/'playground.xml').getroot();r.set('model','Override full field development');w=r.find('worldbody');asset=r.find('asset')
for b in list(w.findall('body')):
 if b.get('name','').startswith(('pin','cup','practiceGoal')):w.remove(b)
spec=json.loads((P/'Field/specification.json').read_text());per=spec['portablePerimeter'];half=per['insideSpan']/2000;thick=per['wallWidth']/2000;height=per['wallHeight']/2000
for g in w.findall('geom'):
 name=g.get('name','')
 if name.startswith('wall'):
  sign=-1 if name.endswith('-1') else 1
  if name.startswith('wallX'):g.set('pos',vec([sign*(half+thick),0,height]));g.set('size',vec([thick,half+2*thick,height]))
  else:g.set('pos',vec([0,sign*(half+thick),height]));g.set('size',vec([half,thick,height]))
scenario=json.loads((A/'StadiumPieces/scenario.json').read_text());w.find("body[@name='robot']").set('pos',vec(scenario['robotPosition']))
for shape in json.loads((A/'StadiumPieces/cup-collision.json').read_text()):
 asset.find("mesh[@name='"+shape['name']+"']").set('vertex',vec(np.array(shape['vertices']).reshape(-1)))
pin_shapes=json.loads((A/'ReusedPieces/pin-collision.json').read_text())
for p in scenario['pieces']:
 if p['state']!='Field':continue
 name=p['id'];cup=p['kind']=='cup';b=el(w,'body',name=name,pos=vec(p['position']),quat=vec(p['quaternion']));el(b,'freejoint',name=name+'free')
 el(b,'inertial',mass='.078' if cup else '.073',pos='0 0 .08225' if cup else '0 0 .0825',diaginertia='.00017 .00017 .000065' if cup else '.00014 .00014 .000032')
 shapes=[f'cup_{section}_{k}' for section in range(4) for k in range(20)] if cup else [s['name'] for s in pin_shapes]
 for i,shape in enumerate(shapes):el(b,'geom',name=f'{name}_{i}',type='mesh',mesh=shape,friction='.45 .002 .0001',rgba='.7 .7 .7 1')
contacts_path=Path(args.contacts)
if contacts_path.exists():
 contacts=json.loads(contacts_path.read_text())
 for entry in contacts['meshes']:el(asset,'mesh',inertia='shell',name=entry['name'],vertex=vec(np.array(entry['vertices']).reshape(-1)))
 for entry in contacts['bodies']:
  b=el(w,'body',name=entry['name'],pos=vec(entry.get('position',[0,0,0])))
  for i,mesh in enumerate(entry['meshes']):el(b,'geom',name=f"{entry['name']}_{i}",type='mesh',mesh=mesh,rgba='.3 .3 .3 1')
X.indent(r);X.ElementTree(r).write(args.output,encoding='unicode');print('STADIUM_MODEL',len(scenario['pieces']),'ledger entries,',len([p for p in scenario['pieces'] if p['state']=='Field']),'physical pieces; contacts',contacts_path.exists())
