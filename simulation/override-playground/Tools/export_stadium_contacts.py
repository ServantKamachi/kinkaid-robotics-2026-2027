"""Source-surface contact partitions, with open interiors preserved.
These are quantified development approximations, NOT field-fidelity acceptance.
"""
from pathlib import Path
import json,math,argparse,numpy as np,trimesh
a=argparse.ArgumentParser();a.add_argument("--trial-shell",action="store_true");a.add_argument('--trial-radial',action='store_true');a.add_argument('--radial-step',type=float,default=0);args=a.parse_args()
from scipy.spatial import ConvexHull
P=Path(__file__).resolve().parents[1];A=P/'Unity/Assets/StreamingAssets';parts=[];bodies=[];audit=[]
rows=json.loads((P/'Evidence/v2/field-components.json').read_text())
def source(i):
 m=trimesh.load(P/f'work/v2/components/{i}.ply');m.update_faces(m.nondegenerate_faces());m.update_faces(m.unique_faces());m.remove_unreferenced_vertices();return m

def hull(m,name):
 if len(m.vertices)<4:return None
 v=np.unique(np.round(m.vertices,8),axis=0)
 try:h=ConvexHull(v)
 except Exception:return None
 vv=v[h.vertices];parts.append(dict(name=name,vertices=vv.tolist()));return name

def sectors(m,prefix,n=24,cuts=None):
 result=[];cuts=cuts or [m.bounds[0,2]-1e-6,m.bounds[1,2]+1e-6]
 for k in range(n):
  a=2*math.pi*k/n;b=2*math.pi*(k+1)/n
  sect=m.slice_plane([0,0,0],[-math.sin(a),math.cos(a),0]).slice_plane([0,0,0],[math.sin(b),-math.cos(b),0])
  if len(sect.vertices)<4:continue
  for j,(lo,hi) in enumerate(zip(cuts,cuts[1:])):
   band=sect.slice_plane([0,0,lo],[0,0,1]).slice_plane([0,0,hi],[0,0,-1])
   if args.trial_shell and prefix=='goal_shell':
    band.merge_vertices();patches=band.split(only_watertight=False)
   elif args.trial_radial and prefix=='goal_shell':
    normal=np.array([math.cos((a+b)/2),math.sin((a+b)/2),0]);patches=[]
    radii=np.arange(0,.090001,args.radial_step) if args.radial_step>0 else [0,.035,.05,.065,.09]
    for r0,r1 in zip(radii,radii[1:]):
     patch=band.slice_plane(normal*r0,normal).slice_plane(normal*r1,-normal)
     if len(patch.vertices)>=4:patches.append(patch)
   else:patches=[band]
   for c,patch in enumerate(patches):
    name=hull(patch,f'{prefix}_{k}_{j}_{c}' if (args.trial_shell or args.trial_radial) and prefix=='goal_shell' else f'{prefix}_{k}_{j}')
    if name:result.append(name)
 return result
# Normalize one source shell to Appendix A7 nominal base size/height.
m=source(9);bounds=m.bounds.copy();m.vertices[:,:2]-=bounds.mean(axis=0)[:2];m.vertices[:,2]-=bounds[0,2];m.vertices[:,:2]*=.1425/np.diff(bounds,axis=0)[0,:2];m.vertices[:,2]*=.0825/np.ptp(m.vertices[:,2])
cuts=[-1e-6,.01,.03,.05,.07,.082501]
if args.trial_shell or args.trial_radial:
 z=m.triangles[:,:,2];horizontal=np.ptp(z,axis=1)<1e-7
 levels=np.unique(np.round(z[horizontal].mean(axis=1),7))
 cuts=sorted(set(cuts+levels.tolist()))
shell=sectors(m,'goal_shell',24,cuts);audit.append(dict(component=9,method='24 angular sectors with source height planes and radial partitions' if args.trial_radial else '24 angular sectors with source height planes and connected patches' if args.trial_shell else '24 angular sectors x 5 height bands',parts=len(shell),nominalSizeCorrection=True,sourceBounds=bounds.tolist(),acceptance='PENDING source-distance and gameplay tests'))
baseMeshes={}
for i,key,h in [(7,'short',.064),(28,'tall',.1402)]:
 m=source(i);bounds=m.bounds.copy();m.vertices[:,:2]-=bounds.mean(axis=0)[:2];m.vertices[:,2]-=bounds[0,2];m.vertices[:,2]*=h/np.ptp(m.vertices[:,2]);baseMeshes[key]=sectors(m,'goal_base_'+key,24)
coords=json.loads((P/'Field/specification.json').read_text())['goalCentersFromAudienceLowerLeft']
for i,(X,Y) in enumerate(coords):
 alliance=i in [0,1,7,8];base=0 if alliance else .1402 if i==4 else .064
 center=[(X-1783.2)/1000,(1783.2-Y)/1000,base]
 bodies.append(dict(name=f'goal{i}',position=center,meshes=shell))
 if base:bodies.append(dict(name=f'goal{i}base',position=[*center[:2],0],meshes=baseMeshes['tall' if i==4 else 'short']))
# Loader transparent folded walls: partition into front/back/side regions without a solid central hull.
# Source left loaders were 7.79846 mm high relative to the right ones; use right assembly
# as the common source, mirrored for the left pair. Top=365 mm per A9.
m=source(322);bounds=m.bounds.copy();center=bounds.mean(axis=0);m.vertices[:,:2]-=center[:2];m.vertices[:,2]-=bounds[0,2];m.vertices[:,2]*=.365/np.ptp(m.vertices[:,2]);load=sectors(m,'loader_panel',24,[-1e-6,.0825,.30,.365001]);audit.append(dict(component=322,parts=len(load),acceptance='PENDING opening/visual alignment test; fixed bracket contacts not complete'))
for i,(sx,sy) in enumerate([(1,-1),(1,1),(-1,-1),(-1,1)]):
 # Center is source-derived; centerline Y is A10 290.6 mm from end wall.
 if sx==1:ids=load
 else:
  ids=[]
  for name in load:
   p=next(x for x in parts if x['name']==name);v=np.array(p['vertices']);v[:,0]*=-1;new=name+'_mirror';parts.append(dict(name=new,vertices=v.tolist()));ids.append(new)
  # Avoid duplicate named assets for second mirrored instance.
  if i==2:mirrored=ids
  else:
   parts=parts[:-len(ids)];ids=mirrored
 bodies.append(dict(name=f'loader{i}',position=[sx*abs(center[0]),sy*(1.7832-.2906),0],meshes=ids))
(P/'work/v2/contacts-radial-trial.json' if args.trial_radial else P/'work/v2/contacts-height-trial.json' if args.trial_shell else A/'Stadium/contacts.json').write_text(json.dumps(dict(meshes=parts,bodies=bodies),separators=(',',':')))
(P/'Evidence/v2/stadium-contact-radial-trial.json' if args.trial_radial else P/'Evidence/v2/stadium-contact-height-trial.json' if args.trial_shell else P/'Evidence/v2/stadium-contact-generation.json').write_text(json.dumps(dict(status='DEVELOPMENT; not full-fidelity acceptance',components=audit,meshes=len(parts),bodies=len(bodies),unresolved=['Source/hull surface-distance bound','Loader brackets and extended telescoping section','Toggle moving contacts and mounting slot','Dynamic manipulation and containment validation']),indent=2))
print('CONTACTS',len(parts),'shared convex assets',len(bodies),'field bodies',flush=True)
