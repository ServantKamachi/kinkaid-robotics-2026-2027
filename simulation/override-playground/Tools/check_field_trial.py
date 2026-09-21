"""Native field trial timing/finite-state screen; not containment or full release acceptance."""
from pathlib import Path
import ctypes as C,json,time,numpy as np,sys
P=Path(__file__).resolve().parents[1];path=Path(sys.argv[1]);lib=C.CDLL(str(P/'Unity/Assets/Plugins/liboverride.dylib'));lib.pg_load.argtypes=[C.c_char_p,C.c_char_p,C.c_int];lib.pg_status.argtypes=[C.POINTER(C.c_double)];lib.pg_command.argtypes=[C.c_double]*5;lib.pg_poses.argtypes=[C.POINTER(C.c_double)]
error=C.create_string_buffer(4096);t=time.perf_counter();n=lib.pg_load(str(path).encode(),error,4096);assert n,error.value;load=time.perf_counter()-t
status=(C.c_double*12)();samples=[];t=time.perf_counter()
for i in range(1500):
 lib.pg_command(.35 if i%400<200 else -.35,.2 if i%200<100 else -.2,1 if i%400<200 else -1,-1,1)
 t0=time.perf_counter();lib.pg_step(10);cost=(time.perf_counter()-t0)*1000
 if i>=250:samples.append(cost)
 if i%250==0:lib.pg_status(status);print('seconds',status[0],'contacts',status[1],'batchms',cost,flush=True)
lib.pg_status(status);poses=(C.c_double*(n*7))();lib.pg_poses(poses);assert np.isfinite(list(poses)).all();r=dict(path=str(path),bodies=n,loadSeconds=load,wallSeconds=time.perf_counter()-t,simSeconds=status[0],physics20msP99=float(np.percentile(samples,99)),physics20msMedian=float(np.median(samples)),warnings=list(status)[8:10]);lib.pg_close();print(json.dumps(r));(P/f'Evidence/v2/{path.stem}-native.json').write_text(json.dumps(r,indent=2))
