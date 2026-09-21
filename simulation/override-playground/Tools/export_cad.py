import FreeCAD as A, Part, MeshPart, math, json, os, struct
from FreeCAD import Vector as V
out='/Users/kamachi/Documents/OverridePlayground/Unity/Assets/StreamingAssets/Robot'
D=A.openDocument('/Users/kamachi/Downloads/RatchetingClaw.FCStd')
# Recover the neutral link arrangement, independently of the saved viewing pose.
for g in [D.LowerStage,D.UpperStage]:
 for o in g.Group:
  if 'NeutralPlacement' in o.PropertiesList:o.Placement=o.NeutralPlacement
D.LowerStage.Placement=A.Placement(V(0,-127,355.6),A.Rotation())
D.RearCoupler.Placement=A.Placement(V(0,203.2,355.6),A.Rotation())
D.UpperStage.Placement=A.Placement(V(0,203.2,533.4),A.Rotation(V(0,0,1),180))
D.Claw.Placement=A.Placement(V(0,-127,533.4),A.Rotation())
D.ClawControls.OpeningAngle=0;D.ClawControls.RollerAngle=0
D.recompute()
colors={'metal':[.54,.60,.65,1],'black':[.045,.055,.07,1],'gear':[.18,.20,.23,1],'red':[.75,.07,.08,1],'white':[.78,.81,.82,1],'rubber':[.10,.115,.13,1],'glass':[.24,.40,.46,.22]}
buckets={};cache={}; count=0; skipped=[]
refs={'robot':A.Placement(), 'lower0':D.LowerStage.Placement, 'lower1':A.Placement(V(0,-127,444.5),A.Rotation()),'rear':D.RearCoupler.Placement,'upper0':D.UpperStage.Placement,'upper1':A.Placement(V(0,203.2,622.3),A.Rotation(V(0,0,1),180)),'claw':D.Claw.Placement}
for n,b in [('LeftJaw','jawL'),('RightJaw','jawR'),('LeftWheelStack','rollerL'),('RightWheelStack','rollerR')]:refs[b]=D.getObject(n).getGlobalPlacement()
def walk(g,body):
 global count
 for o in g.Group:
  if o.TypeId=='App::Part':
   b={'LeftJaw':'jawL','RightJaw':'jawR','LeftWheelStack':'rollerL','RightWheelStack':'rollerR'}.get(o.Name,body)
   if 'ClawGear' in o.Name:continue
   walk(o,b);continue
  if not hasattr(o,'Shape') or o.Shape.isNull():continue
  label=o.Label.lower()
  if any(t in label for t in ['screw','shaft collar','pivot screw']):skipped.append(o.Name);continue
  b=body
  if g.Name in ['LowerStage','UpperStage']:b=('lower' if g.Name=='LowerStage' else 'upper')+('1' if getattr(o,'ParallelOffset',0)>1 else '0')
  if 'omni wheel' in label:
   p=o.Placement.Base;b='wheel'+str(0 if p.x<0 else 1)+str(int(round((p.y+165.1)/165.1)))
   refs[b]=A.Placement(V(p.x,p.y,p.z),A.Rotation())
  col='metal'
  if any(t in label for t in ['gear','bearing','shaft','pawl']):col='gear'
  if any(t in label for t in ['motor','brain','battery','radio','tubing','cable']):col='black'
  if any(t in label for t in ['wheel','tire','shoe']):col='rubber'
  if 'team plate' in label:col='red'
  if any(t in label for t in ['lettering','nylon']):col='white'
  if 'polycarbonate' in label:col='glass'
  if o.TypeId=='App::Link':
   src=o.LinkedObject;key=src.Name;shape=src.Shape.copy();shape.Placement=A.Placement();pl=g.getGlobalPlacement().multiply(o.Placement)
  else:
   key=o.Name;shape=o.Shape.copy();shape.Placement=A.Placement();pl=g.getGlobalPlacement().multiply(o.Placement)
  if key not in cache:
   mesh=MeshPart.meshFromShape(Shape=shape,LinearDeflection=0.65,AngularDeflection=0.4,Relative=False)
   cache[key]=mesh.Topology
  vv,ff=cache[key];tf=refs[b].inverse().multiply(pl)
  key2=(b,col);verts,faces=buckets.setdefault(key2,([],[]));start=len(verts)
  for v in vv:
   p=tf.multVec(v);verts.append((p.x*.001,p.z*.001,p.y*.001))
  faces.extend((start+f[0],start+f[2],start+f[1]) for f in ff)
  count+=1
for n,b in [('Chassis','robot'),('Tower','robot'),('Electronics','robot'),('LowerStage','lower0'),('RearCoupler','rear'),('UpperStage','upper0'),('Claw','claw')]:walk(D.getObject(n),b)
meta={'source':'RatchetingClaw.FCStd','units':'meters','axis':'Unity x,z,y from CAD x,y,z','parts':count,'omittedFasteners':len(skipped),'meshes':[]}
for (b,c),(vs,fs) in buckets.items():
 name=b+'_'+c+'.meshbin'
 with open(out+'/'+name,'wb') as f:
  f.write(struct.pack('<ii',len(vs),len(fs)*3))
  for v in vs:f.write(struct.pack('<fff',*v))
  for face in fs:f.write(struct.pack('<iii',*face))
 meta['meshes'].append({'file':name,'body':b,'rgba':colors[c],'vertices':len(vs),'triangles':len(fs)})
with open(out+'/manifest.json','w') as f:json.dump(meta,f,indent=2)
print('EXPORTED',count,'parts',len(buckets),'meshes',sum(len(f) for v,f in buckets.values()),'triangles')
print('REFERENCE FRAMES',[(b,str(p)) for b,p in refs.items()])
