"""Contact-only pickup/hold/release checks; fixture placement ends before stepping."""
import ctypes as C,json,math,hashlib,argparse
from pathlib import Path
parser=argparse.ArgumentParser();parser.add_argument('--output',default='Evidence/v2/grip-validation.json');parser.add_argument('--repeats',type=int,default=3);args=parser.parse_args()
assert args.repeats>0
P=Path(__file__).resolve().parents[1];lib=C.CDLL(str(P/'Unity/Assets/Plugins/liboverride.dylib'))
lib.pg_load.argtypes=[C.c_char_p,C.c_char_p,C.c_int];lib.pg_command.argtypes=[C.c_double]*5;lib.pg_poses.argtypes=[C.POINTER(C.c_double)];lib.pg_body.argtypes=[C.c_char_p];lib.pg_place_piece.argtypes=[C.c_char_p,C.c_double,C.c_double,C.c_double]
lib.pg_status.argtypes=[C.POINTER(C.c_double)]
e=C.create_string_buffer(4096);n=lib.pg_load(str(P/'Unity/Assets/StreamingAssets/playground.xml').encode(),e,4096);assert n,e.value
p=(C.c_double*(n*7))();status=(C.c_double*12)();reports=[]
for trial,(piece,offset) in enumerate([(p,o) for p in ['pin0','cup0'] for o in [0,.01,-.01]]*args.repeats):
 report={'trial':trial,'piece':piece,'lateralOffsetMeters':offset,'holdSeconds':5,'rollersDuringClose':1}
 def snap():
  lib.pg_poses(p);lib.pg_status(status);assert all(math.isfinite(x) for x in p);assert status[8]==status[9]==0
  return {name:list(p[lib.pg_body(name.encode())*7:lib.pg_body(name.encode())*7+7]) for name in [piece,'claw']}
 lib.pg_reset(0)
 if piece=="cup0":assert lib.pg_place_piece(b"pin0",-1.2,1.2,.003)
 assert lib.pg_place_piece(piece.encode(),offset,.685,.003);lib.pg_step(500);report['settled']=snap()
 lib.pg_command(0,0,0,-1,1);lib.pg_step(500);report['closed']=snap()
 lib.pg_command(0,0,1,0,0);lib.pg_step(900);report['raised']=snap()
 lib.pg_command(0,0,0,0,0);lib.pg_step(2500);report['held']=snap()
 lib.pg_command(0,0,0,1,0);lib.pg_step(1000);report['released']=snap()
 report['pickedUp']=report['held'][piece][2]>report['settled'][piece][2]+.15
 report['releasedToFloor']=report['released'][piece][2]<.10
 reports.append(report);print(piece,offset,report['pickedUp'],report['releasedToFloor'],flush=True)
output=P/args.output;output.parent.mkdir(parents=True,exist_ok=True)
output.write_text(json.dumps({'nativeSHA256':hashlib.sha256((P/'Unity/Assets/Plugins/liboverride.dylib').read_bytes()).hexdigest(),'modelSHA256':hashlib.sha256((P/'Unity/Assets/StreamingAssets/playground.xml').read_bytes()).hexdigest(),'cases':reports},indent=2));lib.pg_close()
assert all(r['pickedUp'] and r['releasedToFloor'] for r in reports),'Pickup/hold/release case failed; inspect '+str(output)
