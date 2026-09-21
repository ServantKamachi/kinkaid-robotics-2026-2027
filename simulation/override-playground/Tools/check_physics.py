import ctypes as C, time,json,math,pathlib
p=pathlib.Path('/Users/kamachi/Documents/OverridePlayground');lib=C.CDLL(str(p/'Unity/Assets/Plugins/liboverride.dylib'));lib.pg_load.argtypes=[C.c_char_p,C.c_char_p,C.c_int];lib.pg_command.argtypes=[C.c_double]*5;lib.pg_poses.argtypes=[C.POINTER(C.c_double)];lib.pg_status.argtypes=[C.POINTER(C.c_double)];lib.pg_body.argtypes=[C.c_char_p]
err=C.create_string_buffer(4096);n=lib.pg_load(str(p/'Unity/Assets/StreamingAssets/playground.xml').encode(),err,4096)
assert n,err.value
poses=(C.c_double*(n*7))();status=(C.c_double*12)()
def snap():
 lib.pg_poses(poses);lib.pg_status(status);return list(status)
def pos(name):i=lib.pg_body(name.encode());return list(poses)[i*7:i*7+3]
report=[]
for scene in range(3):
 lib.pg_reset(scene);t=time.perf_counter();lib.pg_step(1500);wall=time.perf_counter()-t;s=snap();print('SCENE',scene,'3s cost',wall,'status',s,flush=True);report.append({'scene':scene,'simSeconds':3,'wallSeconds':wall,'status':s,'pin0':pos('pin0'),'cup0':pos('cup0')})
lib.pg_reset(0);lib.pg_step(500);before=snap();lib.pg_command(1,0,0,0,0);t=time.perf_counter();lib.pg_step(1000);after=snap();print('DRIVE',before,after,'wall',time.perf_counter()-t,flush=True);report.append({'driveBefore':before,'driveAfter':after})
lib.pg_command(0,0,1,0,0);lib.pg_step(1000);s=snap();print('LIFT',s,'claw',pos('claw'),flush=True);report.append({'raised':s,'clawPosition':pos('claw')})
(p/'Evidence/physics-initial.json').write_text(json.dumps(report,indent=2));lib.pg_close()
