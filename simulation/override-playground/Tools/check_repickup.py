"""Quick screening: same dropped piece, no reset or reposition between pickups.
Stationary second approach isolates whether lowering/reclosing can retrieve the drop.
A failure does not establish that driving/reorienting cannot recover the piece.
"""
from pathlib import Path
import ctypes as C,json,math,hashlib
P=Path(__file__).resolve().parents[1];lib=C.CDLL(str(P/'Unity/Assets/Plugins/liboverride.dylib'))
lib.pg_load.argtypes=[C.c_char_p,C.c_char_p,C.c_int];lib.pg_command.argtypes=[C.c_double]*5
lib.pg_place_piece.argtypes=[C.c_char_p,C.c_double,C.c_double,C.c_double];lib.pg_body.argtypes=[C.c_char_p];lib.pg_poses.argtypes=[C.POINTER(C.c_double)];lib.pg_status.argtypes=[C.POINTER(C.c_double)]
e=C.create_string_buffer(4096);n=lib.pg_load(str(P/'Unity/Assets/StreamingAssets/playground.xml').encode(),e,4096);assert n,e.value
poses=(C.c_double*(n*7))();s=(C.c_double*12)();rows=[]
def snap(piece):
 lib.pg_poses(poses);lib.pg_status(s);assert all(math.isfinite(x) for x in poses) and s[8]==s[9]==0
 b=lib.pg_body(piece.encode());return dict(position=list(poses[b*7:b*7+3]),quaternion=list(poses[b*7+3:b*7+7]))
def step(l,j,r,seconds):lib.pg_command(0,0,l,j,r);lib.pg_step(round(seconds/.002))
for piece in ['pin0','cup0']:
 lib.pg_reset(0)
 if piece=='cup0':lib.pg_place_piece(b'pin0',-1.2,1.2,.003)
 assert lib.pg_place_piece(piece.encode(),0,.685,.003)
 step(0,0,0,1)
 cycles=[]
 for cycle in range(3):
  before=snap(piece);step(0,-1,1,1);step(1,0,0,1.8);step(0,0,0,5);held=snap(piece)
  step(0,1,0,2);dropped=snap(piece);step(-1,0,0,2);step(0,0,0,1);resting=snap(piece)
  result=dict(cycle=cycle+1,before=before,held=held,dropped=dropped,resting=resting,pickedUp=held['position'][2]>before['position'][2]+.15);cycles.append(result);print(piece,cycle+1,result['pickedUp'],resting['position'],flush=True)
 rows.append(dict(piece=piece,cycles=cycles))
lib.pg_close();(P/'Evidence/v2/repickup-screen.json').write_text(json.dumps(dict(scope=__doc__,modelSHA256=hashlib.sha256((P/'Unity/Assets/StreamingAssets/playground.xml').read_bytes()).hexdigest(),cases=rows),indent=2))
