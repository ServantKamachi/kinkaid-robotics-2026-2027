"""Official H2H identities and drawing-backed XY placement; no active reserve bodies.
Appendix A12 and FO-2; native +y points toward the audience. Vertical nested
placement and four horizontal-pin clusters are separately subject to contact tests.
"""
from pathlib import Path
import json,math,collections
import numpy as np
from scipy.spatial.transform import Rotation
P=Path(__file__).resolve().parents[1];A=P/'Unity/Assets/StreamingAssets';out=A/'StadiumPieces';out.mkdir(exist_ok=True)
pieces=[]
def add(kind,n,side,state,clear=False):
 for _ in range(n):pieces.append(dict(id=f'piece-{len(pieces):03}',kind=kind,alliance=side,state=state,clearSideUp=clear))
add('redBlue',4,'neutral','Field')
for side in ['red','blue']:
 add(side+'Yellow',8,side,'Field');add(side+'Yellow',2,side,'Preload');add(side+'Yellow',10,side,'Reserve');add('yellowYellow',1,side,'Reserve');add('cup',10,side,'Reserve')
add('yellowYellow',17,'neutral','Field');add('cup',24,'neutral','Field');add('cup',12,'neutral','Field',True)
used=set()
def take(kind,clear=False):
 p=next(p for p in pieces if p['state']=='Field' and p['kind']==kind and p['clearSideUp']==clear and p['id'] not in used);used.add(p['id']);return p

def place(kind,X,Y,z,clear=False,axis=None,flip=False,group='',verticalStatus='Contact settling required'):
 p=take(kind,clear);q=np.array([1.,0,0,0])
 if axis is not None:
  rot=Rotation.align_vectors([axis],[[0,0,1]])[0];v=rot.as_quat();q=np.array([v[3],*v[:3]])
 elif flip:q=np.array([0.,1,0,0])
 # Canonical body origin is at bottom end of source upright asset.
 p.update(position=[round((X-1783.2)/1000,7),round((1783.2-Y)/1000,7),z],quaternion=q.tolist(),group=group,placementSource='Appendix A12 / FO-2',verticalStatus=verticalStatus)
 return p
# Source cup has opaque upper half. Clear-up cups are inverted, origin at top.
def cup(X,Y,clear,group):return place('cup',X,Y,.1645 if clear else 0.,clear=clear,flip=clear,group=group)
# Eight groups against the perimeter, three opaque-up cups and a nested YY pin.
for X in [1185.1,2381.3]:
 for Y in [40.1,3526.3]:
  for dx in [-80.4,0,80.4]:cup(X+dx,Y,False,'perimeter')
  place('yellowYellow',X,Y,.08225,group='perimeter')
for X in [40.1,3526.3]:
 for Y in [1185.1,2381.3]:
  for dy in [-80.4,0,80.4]:cup(X,Y+dy,False,'perimeter')
  place('yellowYellow',X,Y,.08225,group='perimeter')
# Clear-up cups on the alternate diagonal and at each midfield diamond point.
for X,Y in [(587.1,587.1),(1185.1,1185.1),(2381.3,2381.3),(2979.3,2979.3)]:
 cup(X,Y,True,'diagonal');place('yellowYellow',X,Y,.08225,group='diagonal')
# RedBlue source has red upper and blue lower; lower/west points red-up.
for X,Y,redUp in [(1783.2,2381.3,False),(2381.3,1783.2,False),(1185.1,1783.2,True),(1783.2,1185.1,True)]:
 cup(X,Y,True,'midfield boundary');place('redBlue',X,Y,.08225 if redUp else .24725,flip=not redUp,group='midfield boundary')
# Five neutral-goal starting pins. Source goal center bore seating is validated separately.
for X,Y,top in [(587.1,2381.3,.1465),(1185.1,2979.3,.1465),(2381.3,587.1,.1465),(2979.3,1185.1,.1465),(1783.2,1783.2,.2227)]:
 place('yellowYellow',X,Y,top-.0825,group='neutral goal')
# Four clusters: upright clear-up cup surrounded by horizontal colored-out pins.
# A12 gives XY centers; z and roll must pass native collision/settling checks.
for X,Y in [(587.1,2979.3),(1185.1,2381.3),(2381.3,1185.1),(2979.3,587.1)]:
 cup(X,Y,True,'cross cluster')
 for dx,dy,kind in [(-80.4,0,'redYellow'),(0,-80.4,'redYellow'),(80.4,0,'blueYellow'),(0,80.4,'blueYellow')]:
  # Body +z points toward the colored end; source color halves verified on export.
  axis=np.array([dx,-dy,0.]);axis/=np.linalg.norm(axis)
  center=np.array([(X+dx-1783.2)/1000,(1783.2-Y-dy)/1000,.04015])
  p=place(kind,X+dx,Y+dy,.04015,axis=axis,group='cross cluster',verticalStatus='UNVALIDATED: source drawing gives XY only; ground and cup clearance test required')
  p['position']=(center-axis*.0825).tolist()
assert len(used)==73 and len(pieces)==119
scenario=dict(mode='Head-to-head practice',source='Override manual v2 FO-2, A12; assembly pp150-164',coordinates='Native SI x-right/y-toward-audience/z-up',status='XY/identity manifest; final settling and exact vertical pose checks pending',pieces=pieces,robotPosition=[-1.45,0,.006])
(out/'scenario.json').write_text(json.dumps(scenario,indent=2)+'\n')
print('SCENARIO',dict(collections.Counter(p['state'] for p in pieces)))
