"""Source-faithful instanced CAD export; original FCStd remains read-only.
Reuse FreeCAD's OCCT/MeshPart tessellator and saved GUI material data.
Correct accumulated parallel-arm pose offsets before assigning rigid links.
"""
import FreeCAD as A,MeshPart,json,struct,zipfile,xml.etree.ElementTree as ET,os
from FreeCAD import Vector as V
P='/Users/kamachi/Documents/OverridePlayground';out=P+'/work/v2/cad-raw';os.makedirs(out,exist_ok=True)
source='/Users/kamachi/Downloads/RatchetingClaw.FCStd';D=A.openDocument(source)
archive=zipfile.ZipFile(source);gui=ET.fromstring(archive.read('GuiDocument.xml'))
views={v.attrib['name']:v for v in gui.findall('.//ViewProvider')}
def rgba(o):
 n=o.LinkedObject.Name if o.TypeId=='App::Link' else o.Name
 v=views.get(n);color=[.72,.75,.78,1]
 if v is not None:
  m=v.find('./Properties/Property[@name="ShapeAppearance"]/MaterialList')
  if m is not None and m.attrib.get('file'):
   data=archive.read(m.attrib['file']);c=struct.unpack_from('<I',data,8)[0];color=[((c>>24)&255)/255,((c>>16)&255)/255,((c>>8)&255)/255,1-struct.unpack_from('<f',data,24)[0]]
 return color
# Recover upper parallel link origin from corresponding lower link, not a saved posed offset.
corrections={}
for g in [D.LowerStage,D.UpperStage]:
 arms=[o for o in g.Group if 'parallel lift arm' in o.Label.lower()]
 base=next(o for o in arms if o.ParallelOffset==0);high=next(o for o in arms if o.ParallelOffset>0)
 delta=V(0,0,float(high.ParallelOffset))-(high.NeutralPlacement.Base-base.NeutralPlacement.Base)
 corrections[g.Name]=[delta.x,delta.y,delta.z]
 for o in g.Group:
  if 'NeutralPlacement' in o.PropertiesList:
   pl=A.Placement(o.NeutralPlacement)
   if o.ParallelOffset>0:pl.Base=pl.Base+delta
   o.Placement=pl
D.LowerStage.Placement=A.Placement(V(0,-127,355.6),A.Rotation())
D.RearCoupler.Placement=A.Placement(V(0,203.2,355.6),A.Rotation())
D.UpperStage.Placement=A.Placement(V(0,203.2,533.4),A.Rotation(V(0,0,1),180))
D.Claw.Placement=A.Placement(V(0,-127,533.4),A.Rotation())
D.ClawControls.OpeningAngle=0;D.ClawControls.RollerAngle=-1;D.recompute()
refs={'robot':A.Placement(),'lower0':D.LowerStage.Placement,'lower1':A.Placement(V(0,-127,444.5),A.Rotation()),'rear':D.RearCoupler.Placement,'upper0':D.UpperStage.Placement,'upper1':A.Placement(V(0,203.2,622.3),A.Rotation(V(0,0,1),180)),'claw':D.Claw.Placement}
# User-authorized corrections are shared by CAD, rendering and collider export.
import sys
sys.path.insert(0,P+'/Tools')
from correct_assembly import apply
assembly_corrections=apply(D)
for n,b in [('LeftJaw','jawL'),('RightJaw','jawR'),('LeftWheelStack','rollerL'),('RightWheelStack','rollerR')]:refs[b]=D.getObject(n).getGlobalPlacement()
os.makedirs(P+'/CAD',exist_ok=True)
D.saveAs(P+'/CAD/RatchetingClaw-Simulation.FCStd')
json.dump(dict(status='candidate; dense solid validation pending',original=source,
               simulationCopy=P+'/CAD/RatchetingClaw-Simulation.FCStd',changes=assembly_corrections),
          open(P+'/CAD/assembly-corrections.json','w'),indent=2)
for n,b in [('LeftClawGear','gearSunL'),('RightClawGear','gearSunR')]:refs[b]=D.getObject(n).getGlobalPlacement()
drive_gears={'I_gear36':'motorGear00','I_gear002':'motorGear01','I_gear004':'motorGear02','I_gear006':'motorGear10','I_gear008':'motorGear11','I_gear010':'motorGear12'}
for n,b in drive_gears.items():refs[b]=A.Placement(D.Chassis.getGlobalPlacement().multiply(D.getObject(n).Placement).Base,A.Rotation())
cache={};entries=[];collisions=[]
def walk(g,b):
 for o in g.Group:
  if o.TypeId=='App::Part':walk(o,{'LeftJaw':'jawL','RightJaw':'jawR','LeftWheelStack':'rollerL','RightWheelStack':'rollerR'}.get(o.Name,drive_gears.get(o.Name,b)));continue
  if not hasattr(o,'Shape') or o.Shape.isNull():continue
  label=o.Label.lower();body={'I_gear016':'gearSunL','I_gear018':'gearSunR','I_gear60':'wheel00','I_gear001':'wheel01','I_gear003':'wheel02','I_gear005':'wheel10','I_gear007':'wheel11','I_gear009':'wheel12'}.get(o.Name,drive_gears.get(o.Name,b))
  if g.Name in ['LowerStage','UpperStage']:body=('lower' if g.Name=='LowerStage' else 'upper')+('1' if getattr(o,'ParallelOffset',0)>1 else '0')
  if 'omni wheel' in label:
   p=o.Placement.Base;body='wheel'+str(0 if p.x<0 else 1)+str(int(round((p.y+165.1)/165.1)));refs[body]=A.Placement(V(p.x,p.y,p.z),A.Rotation())
  src=o.LinkedObject if o.TypeId=='App::Link' else o
  key=src.Name;shape=src.Shape.copy();shape.Placement=A.Placement()
  tf=refs[body].inverse().multiply(g.getGlobalPlacement().multiply(o.Placement));q=tf.Rotation.Q
  if key not in cache:
   mesh=MeshPart.meshFromShape(Shape=shape,LinearDeflection=.20,AngularDeflection=.25,Relative=False)
   vv,ff=mesh.Topology
   with open(out+'/'+key+'.meshbin','wb') as f:
    f.write(struct.pack('<ii',len(vv),len(ff)*3))
    for v in vv:f.write(struct.pack('<fff',v.x*.001,v.z*.001,v.y*.001))
    for face in ff:f.write(struct.pack('<iii',face[0],face[2],face[1]))
   cache[key]={'vertices':len(vv),'triangles':len(ff)}
  entry=dict(file=key+'.meshbin',body=body,rgba=rgba(o),position=[tf.Base.x*.001,tf.Base.z*.001,tf.Base.y*.001],rotation=[-q[0],-q[2],-q[1],q[3]],name=o.Name,label=o.Label,**cache[key]);entries.append(entry)
  # Structure uses CAD-local envelopes, never decimated render geometry.
  if 'channel' in src.Name.lower() or any(w in label for w in ['diagonal brace','polycarbonate','toggle shoe','simulation mounting plate']):
   bb=shape.BoundBox;center=V((bb.XMin+bb.XMax)/2,(bb.YMin+bb.YMax)/2,(bb.ZMin+bb.ZMax)/2);c=tf.multVec(center)
   collisions.append(dict(name=o.Name,body=body,pos=[c.x*.001,c.y*.001,c.z*.001],quat=[q[3],q[0],q[1],q[2]],size=[bb.XLength*.0005,bb.YLength*.0005,bb.ZLength*.0005],label=o.Label))
for n,b in [('Chassis','robot'),('Tower','robot'),('Electronics','robot'),('LowerStage','lower0'),('RearCoupler','rear'),('UpperStage','upper0'),('Claw','claw')]:walk(D.getObject(n),b)
json.dump(dict(source=source,bodyFrames={n:{'position':[p.Base.x*.001,p.Base.y*.001,p.Base.z*.001]} for n,p in refs.items()},parts=len(entries),meshes=entries,correctionsMillimeters=corrections,uniqueGeometry=len(cache)),open(out+'/manifest.json','w'),indent=2)
json.dump(collisions,open(out+'/collisions.json','w'),indent=2)
print('EXPORT',len(entries),'parts',len(cache),'unique meshes',sum(c['triangles'] for c in cache.values()),'unique triangles',sum(e['triangles'] for e in entries),'instanced triangles',flush=True)
print('PARALLEL CORRECTIONS',corrections,flush=True)
