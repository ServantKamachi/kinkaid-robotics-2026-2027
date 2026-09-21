"""Validate read-only native contact export against independently loaded MuJoCo contact fixture."""
from pathlib import Path
import ctypes as C
import hashlib,json
import mujoco
import numpy as np
P=Path(__file__).resolve().parents[1]
xml=P/'Unity/Assets/StreamingAssets/playground.xml'
libpath=P/'Unity/Assets/Plugins/liboverride.dylib'
lib=C.CDLL(str(libpath));lib.pg_load.argtypes=[C.c_char_p,C.c_char_p,C.c_int]
lib.pg_contact_evidence.argtypes=[C.POINTER(C.c_double),C.c_int]
m=mujoco.MjModel.from_xml_path(str(xml));d=mujoco.MjData(m)
for name,value in [('lift',-.60),('lower_parallel',-.60),('rear_upright',.60),('upper_lift',-.60),('upper_parallel',-.60),('claw_upright',-.60),('jawL',1.047),('jawR',1.047)]:
 d.qpos[m.joint(name).qposadr[0]]=value
d.qpos[m.joint('pin0free').qposadr[0]:m.joint('pin0free').qposadr[0]+7]=[0,.685,-.001,1,0,0,0]
mujoco.mj_forward(m,d)
err=C.create_string_buffer(4096);assert lib.pg_load(str(xml).encode(),err,4096)>0,err.value
lib.pg_place_piece.argtypes=[C.c_char_p,C.c_double,C.c_double,C.c_double]
assert lib.pg_place_piece(b'pin0',0,.685,-.001)
out=(C.c_double*(6*(d.ncon+10)))();n=lib.pg_contact_evidence(out,d.ncon+10);assert n==d.ncon and n>0, (n,d.ncon,mujoco.__version__)
max_distance_error=0.;max_force_error=0.
for i in range(n):
 c=d.contact[i];record=list(out[i*6:i*6+6]);force=np.zeros(6);mujoco.mj_contactForce(m,d,i,force)
 assert record[:4]==[int(c.geom[0]),int(c.geom[1]),int(m.geom_bodyid[c.geom[0]]),int(m.geom_bodyid[c.geom[1]])]
 max_distance_error=max(max_distance_error,abs(record[4]-c.dist));max_force_error=max(max_force_error,abs(record[5]-force[0]))
assert max_distance_error<1e-9 and max_force_error<1e-6
assert lib.pg_contact_evidence(out,1)==1
assert lib.pg_contact_evidence(out,0)==0
assert lib.pg_contact_evidence(None,10)==0
lib.pg_close();assert lib.pg_contact_evidence(out,10)==0
report=dict(passed=True,scope=__doc__,contacts=n,maxDistanceErrorMeters=max_distance_error,maxForceErrorNewtons=max_force_error,modelSHA256=hashlib.sha256(xml.read_bytes()).hexdigest(),nativeSHA256=hashlib.sha256(libpath.read_bytes()).hexdigest())
(P/'Evidence/v2/contact-api.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report))
