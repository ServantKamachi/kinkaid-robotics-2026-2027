from pathlib import Path
import xml.etree.ElementTree as X, math, json, struct
import numpy as np
from scipy.spatial import ConvexHull
P=Path('/Users/kamachi/Documents/OverridePlayground/Unity/Assets/StreamingAssets')
def el(p,t,**a):return X.SubElement(p,t,{k:str(v) for k,v in a.items()})
def vec(v):return ' '.join(f'{x:.8g}' for x in v)
r=X.Element('mujoco',model='169C Override full playground')
el(r,'compiler',angle='radian',autolimits='true',inertiafromgeom='auto')
opt=el(r,'option',timestep='.002',integrator='implicitfast',solver='Newton',iterations='40',tolerance='1e-8',cone='elliptic',gravity='0 0 -9.81')
el(opt,'flag',sleep='enable');el(r,'size',memory='128M')
d=el(r,'default');el(d,'joint',damping='.025',armature='.001');el(d,'geom',friction='.65 .003 .0001',solref='.008 1',solimp='.95 .99 .001',condim='4',margin='.0002')
a=el(r,'asset');w=el(r,'worldbody');eq=el(r,'equality');act=el(r,'actuator')
def body(p,name,pos=(0,0,0),**kw):return el(p,'body',name=name,pos=vec(pos),**kw)
def box(p,name,pos,size,**kw):return el(p,'geom',name=name,type='box',pos=vec(pos),size=vec(size),**kw)
def mass(b,m,pos=(0,0,0),diag=(.002,.002,.002)):el(b,'inertial',mass=m,pos=vec(pos),diaginertia=vec(diag))
def joint(b,n,axis=(1,0,0),**kw):el(b,'joint',name=n,axis=vec(axis),**kw)
def coupled(n,source='lift',ratio=1):el(eq,'joint',joint1=n,joint2=source,polycoef=f'0 {ratio} 0 0 0',solref='.004 1')
def mesh(name,verts):el(a,'mesh',name=name,vertex=vec([q for v in verts for q in v]))
def frustum(name,z0,z1,r0,r1,N=24):
 verts=[(rad*math.cos(2*math.pi*i/N),rad*math.sin(2*math.pi*i/N),z) for z,rad in [(z0,r0),(z1,r1)] for i in range(N)];mesh(name,verts)
pin_shapes=json.loads((P/'ReusedPieces/pin-collision.json').read_text())
for shape in pin_shapes:mesh(shape['name'],shape['vertices'])
# Source-derived cup sectors shared with stadium; no invented uniform wall thickness.
N=20
for shape in json.loads((P/'StadiumPieces/cup-collision.json').read_text()):
 mesh(shape['name'],shape['vertices'])
# Drawing-backed portable inside span; practice layouts are deliberately separate from match setup.
box(w,'floor',(0,0,-.025),(1.7832,1.7832,.025),rgba='.32 .36 .39 1',friction='.85 .002 .0001')
for s in [-1,1]:
 box(w,f'wallX{s}',(s*1.8032,0,.10),(.02,1.8232,.10),rgba='.12 .16 .2 1')
 box(w,f'wallY{s}',(0,s*1.8032,.10),(1.7832,.02,.10),rgba='.12 .16 .2 1')
robot=body(w,'robot',(0,.90,.006));el(robot,'freejoint',name='root');mass(robot,5.5,(0,.025,.13),(.16,.15,.19))
# Drive losses/braking are handled by the finite motor model. Do not inherit
# the generic .025 Nm/(rad/s) structural damping on wheel and meshing gear joints.
for side,s in enumerate([-1,1]):
 for j,y in enumerate([-.1651,0,.1651]):
  n=f'wheel{side}{j}';b=body(robot,n,(s*.1905,y,.04165));joint(b,n,damping='0');mass(b,.14,diag=(.00012,.00007,.00007))
  el(act,'motor',name=n,joint=n,ctrllimited='true',ctrlrange='-.63 .63')
  # Physical free-spinning rollers allow transverse slip at every robot heading.
  for k in range(10):
   t=2*math.pi*k/10;axis=(0,math.cos(t),-math.sin(t));pos=(0,.033775*math.sin(t),.033775*math.cos(t))
   roll=body(b,f'{n}roller{k}',pos);joint(roll,f'{n}r{k}',axis,damping='.000002',armature='.0000001');
   end=[.008*q for q in axis]
   el(roll,'geom',name=f'{n}contact{k}',type='capsule',fromto=vec([-q for q in end]+end),size='.0075',mass='.005',friction='.9 .0001 .00001',contype='2',conaffinity='1',condim='3')
for side,sign in enumerate([-1,1]):
 for j,y in enumerate([-.1143,.0508,.1143]):
  n=f'motorGear{side}{j}';frame=json.loads((P.parents[2]/'work/v2/cad-raw/manifest.json').read_text())['bodyFrames'][n];gear=body(robot,n,frame['position']);joint(gear,n,damping='0');mass(gear,.015,diag=(.000003,.000002,.000002));coupled(n,f'wheel{side}{j}',-60/36)
def arms(b,width):pass
lo=body(robot,'lower0',(0,-.127,.3556));joint(lo,'lift',limited='true',range='-.721 .10');mass(lo,.55,(0,.1651,0),(.010,.019,.028));arms(lo,.1778)
lo1=body(robot,'lower1',(0,-.127,.4445));joint(lo1,'lower_parallel');mass(lo1,.65,(0,.1651,0),(.011,.021,.031));arms(lo1,.1778);coupled('lower_parallel')
rear=body(lo,'rear',(0,.3302,0));joint(rear,'rear_upright');mass(rear,.7,(0,0,.13),(.010,.02,.012));coupled('rear_upright',ratio=-1)

up=body(rear,'upper0',(0,0,.1778),quat='0 0 0 1');joint(up,'upper_lift');mass(up,.45,(0,.1651,0),(.01,.012,.02));arms(up,.13335);coupled('upper_lift')
up1=body(rear,'upper1',(0,0,.2667),quat='0 0 0 1');joint(up1,'upper_parallel');mass(up1,.65,(0,.1651,0),(.015,.019,.025));arms(up1,.13335);coupled('upper_parallel')
cl=body(up,'claw',(0,.3302,0),quat='0 0 0 1');joint(cl,'claw_upright');mass(cl,.65,(0,0,.025),(.005,.008,.006));coupled('claw_upright')

for s,side in [(-1,'L'),(1,'R')]:
 jaw=body(cl,'jaw'+side,(s*.03175,-.0508,0));joint(jaw,'jaw'+side,(0,0,s),limited='true',range='.17453 1.3962634');mass(jaw,.12,(0,-.03,0),(.0006,.0005,.0004))

 el(act,'motor',name='jaw'+side,joint='jaw'+side,ctrllimited='true',ctrlrange='-1.2 1.2')
 roll=body(jaw,'roller'+side,(0,-.0635011811,0));joint(roll,'roller'+side,(0,0,1),damping='.003',armature='.00005');mass(roll,.20,(0,0,.009),(.0006,.0006,.00012))
 for z in [-.06,-.021,.017,.1004]:el(roll,'geom',name=f'roller{side}{z}',type='cylinder',pos=f'0 0 {z}',size=f'{.0357 if z in [-.021,.017] else .034925} .0095',friction='1.0 .003 .0001',contype='2',conaffinity='1')
 el(act,'motor',name='roller'+side,joint='roller'+side,ctrllimited='true',ctrlrange='-.12 .12')
for sign,side in [(-1,'L'),(1,'R')]:
 carrier=next(b for b in cl.iter('body') if b.get('name')=='jaw'+side)
 sun=body(carrier,'gearSun'+side,(0,0,.042));joint(sun,'gearSun'+side,(0,0,1),damping='.0001',armature='.00001');mass(sun,.02,diag=(.00001,.00001,.00002))
 coupled('gearSun'+side,'roller'+side,-1)
# Explicit symmetric geared approximation; pneumatic ratchet locking remains uncalibrated.
coupled('jawR','jawL',1);coupled('rollerR','rollerL',-1)
el(act,'motor',name='lift',joint='lift',ctrllimited='true',ctrlrange='-22 22')
# Three thin plates preserve the open C-channel cross-section; screw holes are omitted.
bodies={b.attrib['name']:b for b in w.iter('body')}
contact=el(r,'contact')
for parent,child in [('robot','lower1'),('lower1','rear'),('rear','upper1'),('upper1','claw'),('claw','rollerL'),('claw','rollerR')]:
 el(contact,'exclude',body1=parent,body2=child)
for side in range(2):
 for j in range(3):
  for k in range(10):el(contact,'exclude',body1='robot',body2=f'wheel{side}{j}roller{k}')
def rotate(q,v):
 w,x,y,z=q;a,b,c=v
 return ((1-2*(y*y+z*z))*a+2*(x*y-z*w)*b+2*(x*z+y*w)*c,2*(x*y+z*w)*a+(1-2*(x*x+z*z))*b+2*(y*z-x*w)*c,2*(x*z-y*w)*a+2*(y*z+x*w)*b+(1-2*(x*x+y*y))*c)
for c in json.loads((P.parents[2]/'work/v2/cad-raw/collisions.json').read_text()):
 hx,hy,hz=c['size'];parts=[([0,0,0],c['size'])]
 if 'channel' in c['name']:
  t=.0016
  parts=[([0,0,-hz+t/2],[hx,hy,t/2]),([0,-hy+t/2,0],[hx,t/2,hz]),([0,hy-t/2,0],[hx,t/2,hz])]
 # These solid braces are convex (hull/source volume agreement checked at export).
 # Use their CAD hull, not the bounding box that fills empty space beside a diagonal.
 if 'diagonal brace' in c['label'].lower():
  rawdir=P.parents[2]/'work/v2/cad-raw'
  entry=next(e for e in json.loads((rawdir/'manifest.json').read_text())['meshes'] if e['name']==c['name'])
  data=(rawdir/entry['file']).read_bytes();nv,ni=struct.unpack_from('<ii',data)
  vertices=np.frombuffer(data,np.float32,nv*3,8).reshape(-1,3)[:,[0,2,1]]
  hull=ConvexHull(vertices);name='brace_'+c['name'];mesh(name,vertices[hull.vertices])
  q=entry['rotation'];pos=entry['position']
  el(bodies[c['body']],'geom',name=name,type='mesh',mesh=name,pos=vec([pos[0],pos[2],pos[1]]),quat=vec([q[3],-q[0],-q[2],-q[1]]),contype='2',conaffinity='3')
  continue
 for k,(offset,size) in enumerate(parts):
  off=rotate(c['quat'],offset);pos=[c['pos'][i]+off[i] for i in range(3)]
  box(bodies[c['body']], 'cad_'+c['name']+'_'+str(k),pos,size,quat=vec(c['quat']),contype='2',conaffinity='3')
# External housing hulls from CAD: eight motors, brain and battery.
# Hulls conservatively fill small housing recesses; shaft/fastener detail remains visual.
rawdir=P.parents[2]/'work/v2/cad-raw'
housing_entries=[e for e in json.loads((rawdir/'manifest.json').read_text())['meshes'] if e['name'].startswith('I_motor') or e['name'] in ['I_brain','I_battery']]
assert len(housing_entries)==10, 'Housing inventory changed; review collision coverage'
for entry in housing_entries:
 data=(rawdir/entry['file']).read_bytes();nv,ni=struct.unpack_from('<ii',data)
 vertices=np.frombuffer(data,np.float32,nv*3,8).reshape(-1,3)[:,[0,2,1]]
 hull=ConvexHull(vertices);name='housing_'+entry['name'];mesh(name,vertices[hull.vertices])
 q=entry['rotation'];pos=entry['position']
 el(bodies[entry['body']],'geom',name=name,type='mesh',mesh=name,pos=vec([pos[0],pos[2],pos[1]]),quat=vec([q[3],-q[0],-q[2],-q[1]]),contype='2',conaffinity='3')
# Reconfigurable practice objects: each is a free rigid body with actual contact surfaces.
for i in range(12):
 x,y=[(0,.685),(.30,.35),(-.30,.35),(.60,.15),(-.60,.15),(.32,-.2),(-.32,-.2),(.85,-.5),(-.85,-.5),(0,-.4),(.45,-.9),(-.45,-.9)][i]
 b=body(w,f'pin{i}',(x,y,.003));el(b,'freejoint',name=f'pin{i}free');mass(b,.073,(0,0,.08255),(.00014,.00014,.000032))
 for shape in pin_shapes:el(b,'geom',name=f"pin{i}_{shape['name']}",type='mesh',mesh=shape['name'],rgba=('.92 .16 .18 1' if (i%3)==0 else '.12 .43 .92 1' if i%3==1 else '.95 .73 .08 1'),friction='.45 .002 .0001')
for i in range(6):
 b=body(w,f'cup{i}',(-.70+i*.28,-.65,.003));el(b,'freejoint',name=f'cup{i}free');mass(b,.078,(0,0,.08225),(.00017,.00017,.000065))
 for section in range(4):
  for k in range(N):el(b,'geom',name=f'cup{i}_{section}_{k}',type='mesh',mesh=f'cup_{section}_{k}',rgba=('.12 .15 .19 1' if section>=2 else '.58 .66 .7 .45'),friction='.45 .002 .0001')
# Three practice pegs, not a claim of complete official goal assemblies.
for i,h in enumerate([.0825,.1465,.2227]):
 b=body(w,f'practiceGoal{i}',(-.60+i*.60,-1.30,0));el(b,'geom',name=f'goalbase{i}',type='cylinder',size='.11 .012',pos='0 0 .012',rgba='.10 .14 .18 1');el(b,'geom',name=f'goalpost{i}',type='cylinder',size=f'.0127 {h/2}',pos=f'0 0 {h/2+.024}',rgba='.80 .82 .84 1')
X.indent(r);X.ElementTree(r).write(P/'playground.xml',encoding='unicode')
print(P/'playground.xml')
