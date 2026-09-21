"""Native straight-line drive, braking and wall-impact comparison; limits remain estimated."""
from pathlib import Path
import ctypes as C,json,argparse,hashlib,math
import mujoco
import xml.etree.ElementTree as X
P=Path(__file__).resolve().parents[1];a=argparse.ArgumentParser();a.add_argument('--model',default='Unity/Assets/StreamingAssets/playground.xml');a.add_argument('--output',default='Evidence/v2/drive-response.json');a.add_argument('--lane-x',type=float,default=0);args=a.parse_args();path=P/args.model
lib=C.CDLL(str(P/'Unity/Assets/Plugins/liboverride.dylib'));lib.pg_load.argtypes=[C.c_char_p,C.c_char_p,C.c_int];lib.pg_command.argtypes=[C.c_double]*5;lib.pg_status.argtypes=[C.POINTER(C.c_double)];lib.pg_poses.argtypes=[C.POINTER(C.c_double)];lib.pg_place_piece.argtypes=[C.c_char_p,C.c_double,C.c_double,C.c_double]
root=X.parse(path);body=root.getroot().find(".//body[@name='robot']");pos=body.get('pos').split();pos[0]=str(args.lane_x);body.set('pos',' '.join(pos));fixture=P/'work/v2/drive-response-fixture.xml';root.write(fixture,encoding='unicode')
err=C.create_string_buffer(4096);n=lib.pg_load(str(fixture).encode(),err,4096);assert n,err.value;s=(C.c_double*12)();poses=(C.c_double*(n*7))();rows=[];model=mujoco.MjModel.from_xml_path(str(path));contacts=(C.c_double*(8192*6))();lib.pg_contact_evidence.argtypes=[C.POINTER(C.c_double),C.c_int]
def sample(t):
 lib.pg_status(s);lib.pg_poses(poses);assert all(math.isfinite(x) for x in poses) and s[8]==s[9]==0
 return dict(time=t,position=list(s)[5:8],contacts=s[1],lift=s[2],warnings=list(s)[8:10])
for power in [.4,1]:
 lib.pg_reset(0);lib.pg_place_piece(b'pin0',-1.2,1.2,.003);lib.pg_step(500);start=sample(0);trace=[start];wall_penetrations=[]
 for tick in range(300):
  lib.pg_command(power if tick<50 else 0 if tick<100 else 1,0,0,0,0);lib.pg_step(10);trace.append(sample((tick+1)*.02))
  if tick>=275:
   count=lib.pg_contact_evidence(contacts,8192);assert count<8192
   for i in range(count):
    names=[model.geom(int(contacts[6*i+k])).name for k in [0,1]]
    if any(name.startswith('wall') for name in names):wall_penetrations.append(max(0,-contacts[6*i+4]*1000))
 distance=math.dist(trace[50]['position'][:2],trace[0]['position'][:2]);brake=math.dist(trace[100]['position'][:2],trace[50]['position'][:2]);rows.append(dict(power=power,firstSecondDistanceMeters=distance,brakingDistanceMeters=brake,lastHalfSecondWallPenetrationMaxMm=max(wall_penetrations,default=0),wallContactObserved=bool(wall_penetrations),trace=trace));print(power,'1second distance',distance,'braking',brake,flush=True)
lib.pg_close();report=dict(scope=__doc__,fixtureLaneX=args.lane_x,fixtureSHA256=hashlib.sha256(fixture.read_bytes()).hexdigest(),modelSHA256=hashlib.sha256(path.read_bytes()).hexdigest(),nativeSHA256=hashlib.sha256((P/'Unity/Assets/Plugins/liboverride.dylib').read_bytes()).hexdigest(),cases=rows)
(P/args.output).write_text(json.dumps(report,indent=2)+'\n')
