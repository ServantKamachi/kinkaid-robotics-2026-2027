"""Native integration checks with the same bridge and model as the app."""
import ctypes as C,json,time,math
from pathlib import Path
P=Path(__file__).resolve().parents[1]
lib=C.CDLL(str(P/'Unity/Assets/Plugins/liboverride.dylib'))
lib.pg_load.argtypes=[C.c_char_p,C.c_char_p,C.c_int];lib.pg_command.argtypes=[C.c_double]*5
lib.pg_status.argtypes=[C.POINTER(C.c_double)];lib.pg_poses.argtypes=[C.POINTER(C.c_double)];lib.pg_body.argtypes=[C.c_char_p]
err=C.create_string_buffer(4096);n=lib.pg_load(str(P/'Unity/Assets/StreamingAssets/playground.xml').encode(),err,4096);assert n,err.value
s=(C.c_double*12)();p=(C.c_double*(n*7))()
def snap():
 lib.pg_status(s);lib.pg_poses(p);assert all(math.isfinite(x) for x in p);assert s[8]==s[9]==0
 return list(s)
def body(name):
 i=lib.pg_body(name.encode());assert i>=0;return list(p[i*7:i*7+7])
report={'scenarios':[]}
for scene in range(3):
 lib.pg_reset(scene);start=time.perf_counter();max_contacts=0
 for second in range(30):
  lib.pg_step(500);ss=snap();max_contacts=max(max_contacts,ss[1])
 report['scenarios'].append({'scene':scene,'simSeconds':ss[0],'wallSeconds':time.perf_counter()-start,'maxContacts':max_contacts,'status':ss,'pin0':body('pin0'),'cup0':body('cup0')})
 print('scene',scene,report['scenarios'][-1],flush=True)
for sign in [1,-1]:
 lib.pg_reset(0);lib.pg_step(500);before=snap();lib.pg_command(sign,0,0,0,0);lib.pg_step(500);after=snap();dy=after[6]-before[6];assert dy*sign<-.05,(sign,dy)
 report[f'drive_{sign}']={'deltaY':dy,'before':before,'after':after}
lib.pg_reset(0);lib.pg_step(500);before=snap();low=body('claw');lib.pg_command(0,0,1,-1,0);lib.pg_step(1200);after=snap();raised=body('claw');assert raised[2]>low[2]+.1;assert after[3]<before[3]-.2
report['liftJaw']={'before':before,'after':after,'lowClaw':low,'raisedClaw':raised}
(P/'Evidence/native-validation.json').write_text(json.dumps(report,indent=2));lib.pg_close();print('PASS native stability, forward/reverse, raise and jaw close')
