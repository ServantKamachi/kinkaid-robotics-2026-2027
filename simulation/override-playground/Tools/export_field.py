from pathlib import Path
import mujoco as mj, numpy as np, json, struct, math
P=Path('/Users/kamachi/Documents/OverridePlayground/Unity/Assets/StreamingAssets');m=mj.MjModel.from_xml_path(str(P/'playground.xml'));out=P/'Field';out.mkdir(exist_ok=True)
manifest={'meshes':[]};buckets={}
def primitive(typ,s):
 if typ==6:
  vs=np.array([(x*s[0],y*s[1],z*s[2]) for x,y,z in [(-1,-1,-1),(1,-1,-1),(1,1,-1),(-1,1,-1),(-1,-1,1),(1,-1,1),(1,1,1),(-1,1,1)]])
  fs=np.array([(0,2,1),(0,3,2),(4,5,6),(4,6,7),(0,1,5),(0,5,4),(1,2,6),(1,6,5),(2,3,7),(2,7,6),(3,0,4),(3,4,7)])
  return vs,fs
 if typ==5:
  N=48;vs=[(s[0]*math.cos(i*2*math.pi/N),s[0]*math.sin(i*2*math.pi/N),z) for z in [-s[1],s[1]] for i in range(N)];vs.extend([(0,0,-s[1]),(0,0,s[1])]);fs=[]
  for i in range(N):j=(i+1)%N;fs.extend([(i,j,j+N),(i,j+N,i+N),(2*N,j,i),(2*N+1,i+N,j+N)])
  return np.array(vs),np.array(fs)
 raise Exception(typ)
for i in range(m.ngeom):
 b=int(m.geom_bodyid[i]);name=mj.mj_id2name(m,mj.mjtObj.mjOBJ_BODY,b) or 'world'
 if not(name=='world' or name.startswith('practiceGoal')):continue
 typ=int(m.geom_type[i]);rgba=m.geom_rgba[i];color=tuple(round(float(x),3) for x in rgba)
 if typ==7:
  mid=m.geom_dataid[i];v=m.mesh_vert[m.mesh_vertadr[mid]:m.mesh_vertadr[mid]+m.mesh_vertnum[mid]].copy();f=m.mesh_face[m.mesh_faceadr[mid]:m.mesh_faceadr[mid]+m.mesh_facenum[mid]].copy()
 else:v,f=primitive(typ,m.geom_size[i])
 mat=np.zeros(9);mj.mju_quat2Mat(mat,m.geom_quat[i]);v=v@mat.reshape(3,3).T+m.geom_pos[i];v=v[:,[0,2,1]];f=f[:,[0,2,1]]
 vv,ff=buckets.setdefault((name,color),([],[]));offset=len(vv);vv.extend(v.tolist());ff.extend((f+offset).tolist())
for idx,((body,rgba),(v,f)) in enumerate(buckets.items()):
 file=f'field{idx}.meshbin';v=np.array(v,dtype='<f4');f=np.array(f,dtype='<i4');(out/file).write_bytes(struct.pack('<ii',len(v),f.size)+v.tobytes()+f.tobytes());manifest['meshes'].append({'file':file,'body':body,'rgba':rgba,'vertices':len(v),'triangles':len(f)})
(out/'manifest.json').write_text(json.dumps(manifest,indent=2));print('Field meshes',len(buckets))
