"""Finite-actuator lift tracking and stalled-target diagnostic using native bridge."""
import ctypes as C,json,hashlib,math
from pathlib import Path
P=Path(__file__).resolve().parents[1];lib=C.CDLL(str(P/'Unity/Assets/Plugins/liboverride.dylib'))
lib.pg_load.argtypes=[C.c_char_p,C.c_char_p,C.c_int];lib.pg_command.argtypes=[C.c_double]*5;lib.pg_status.argtypes=[C.POINTER(C.c_double)]
e=C.create_string_buffer(4096);assert lib.pg_load(str(P/'Unity/Assets/StreamingAssets/playground.xml').encode(),e,4096),e.value
s=(C.c_double*12)();rows=[]
for label,cmd,steps in [('settled',0,1500),('raised',1,1500),('held',0,2500),('lowered',-1,1500),('heldLow',0,2500)]:
 lib.pg_command(0,0,cmd,0,0);peak=0
 for _ in range(steps//10):
  lib.pg_step(10);lib.pg_status(s);peak=max(peak,abs(s[4]))
  assert all(math.isfinite(v) for v in s) and abs(s[4])<=22.000001 and s[8]==s[9]==0
 rows.append(dict(stage=label,angle=s[2],target=s[10],error=s[10]-s[2],torque=s[4],peakTorque=peak,badAcceleration=s[8],badPosition=s[9]));print(rows[-1],flush=True)
lib.pg_close();(P/'Evidence/v2/lift-control.json').write_text(json.dumps(dict(modelSHA256=hashlib.sha256((P/'Unity/Assets/StreamingAssets/playground.xml').read_bytes()).hexdigest(),nativeSHA256=hashlib.sha256((P/'Unity/Assets/Plugins/liboverride.dylib').read_bytes()).hexdigest(),cases=rows),indent=2))
assert all(abs(r['error'])<.015 and r['badAcceleration']==r['badPosition']==0 for r in rows), 'Lift tracking outside 0.015 rad diagnostic target'
