"""Native field reset/contact diagnostics. Reports failures instead of claiming fidelity."""
from pathlib import Path
import ctypes as C,json,time,math,hashlib
import mujoco,numpy as np
P=Path(__file__).resolve().parents[1];A=P/'Unity/Assets/StreamingAssets';path=A/'stadium.xml'
m=mujoco.MjModel.from_xml_path(str(path));d=mujoco.MjData(m);scenario=json.loads((A/'StadiumPieces/scenario.json').read_text());active=[p for p in scenario['pieces'] if p['state']=='Field']
for name,target in [('lift',-.6),('lower_parallel',-.6),('rear_upright',.6),('upper_lift',-.6),('upper_parallel',-.6),('claw_upright',-.6),('jawL',1.047),('jawR',1.047)]:d.qpos[m.joint(name).qposadr]=target
mujoco.mj_forward(m,d)
contacts=[]
for c in d.contact:
 if c.dist<-.001:
  names=[m.geom(int(g)).name for g in c.geom];contacts.append(dict(geoms=names,penetrationMm=float(-c.dist*1000)))
lib=C.CDLL(str(P/'Unity/Assets/Plugins/liboverride.dylib'));lib.pg_load.argtypes=[C.c_char_p,C.c_char_p,C.c_int];lib.pg_poses.argtypes=[C.POINTER(C.c_double)];lib.pg_status.argtypes=[C.POINTER(C.c_double)];e=C.create_string_buffer(4096);n=lib.pg_load(str(path).encode(),e,4096);assert n,e.value
poses=(C.c_double*(n*7))();s=(C.c_double*12)();samples=[];t=time.perf_counter()
for i in range(250):
 t0=time.perf_counter();lib.pg_step(10);samples.append((time.perf_counter()-t0)*1000)
 if i%50==0:lib.pg_status(s);print('time',s[0],'contacts',s[1],'warnings',list(s)[8:10],flush=True)
lib.pg_poses(poses);lib.pg_status(s);seconds=time.perf_counter()-t;finite=all(math.isfinite(x) for x in poses);lib.pg_close()
report=dict(scope=__doc__,modelSHA256=hashlib.sha256(path.read_bytes()).hexdigest(),inventory=dict(active=len(active),reserve=sum(p['state']=='Reserve' for p in scenario['pieces']),preloads=4),bodies=m.nbody,geoms=m.ngeom,initialPenetrationsOver1mm=sorted(contacts,key=lambda x:-x['penetrationMm']),finite=finite,badAcceleration=s[8],badPosition=s[9],simulationSeconds=s[0],wallSeconds=seconds,physics20msBatchP99=float(np.percentile(samples,99)),status='PASS' if finite and s[8]==s[9]==0 and not contacts else 'FAIL')
(P/'Evidence/v2/stadium-native.json').write_text(json.dumps(report,indent=2));print('RESULT',report['status'],'initial overlaps',len(contacts),'wall',seconds,'p99',report['physics20msBatchP99'])
