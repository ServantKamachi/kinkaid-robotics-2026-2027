"""Continuous manipulation diagnostic using only ordinary drive/lift/jaw/roller commands.
Initial fixture placement occurs once. Subsequent approach targets use observed piece
centers; no resets, attachments or pose edits occur between cycles. This is a test
controller, not a user-facing autonomous feature or general recovery guarantee.
"""
from pathlib import Path
import ctypes as C,json,math,hashlib,argparse
import numpy as np
from scipy.spatial.transform import Rotation
P=Path(__file__).resolve().parents[1]
a=argparse.ArgumentParser();a.add_argument('--cycles',type=int,default=10);a.add_argument('--pieces',nargs='+',default=['pin0','cup0']);a.add_argument('--release-mode',choices=['drop','lower','place'],default='drop');a.add_argument('--output',default='Evidence/v2/reapproach-screen.json');a.add_argument('--alternate-carry',action='store_true');args=a.parse_args()
lib=C.CDLL(str(P/'Unity/Assets/Plugins/liboverride.dylib'))
lib.pg_load.argtypes=[C.c_char_p,C.c_char_p,C.c_int];lib.pg_command.argtypes=[C.c_double]*5
lib.pg_place_piece.argtypes=[C.c_char_p,C.c_double,C.c_double,C.c_double];lib.pg_body.argtypes=[C.c_char_p];lib.pg_poses.argtypes=[C.POINTER(C.c_double)];lib.pg_status.argtypes=[C.POINTER(C.c_double)]
e=C.create_string_buffer(4096);n=lib.pg_load(str(P/'Unity/Assets/StreamingAssets/playground.xml').encode(),e,4096);assert n,e.value
poses=(C.c_double*(n*7))();status=(C.c_double*12)();rows=[]
def snap(piece):
 lib.pg_poses(poses);lib.pg_status(status);assert all(math.isfinite(x) for x in poses) and status[8]==status[9]==0
 return {name:list(poses[lib.pg_body(name.encode())*7:lib.pg_body(name.encode())*7+7]) for name in [piece,'robot','claw']}
def step(seconds,f=0,t=0,l=0,j=0,r=0):lib.pg_command(f,t,l,j,r);lib.pg_step(round(seconds/.002))
def rotation(p):return Rotation.from_quat([*p[4:7],p[3]])
def center(p):return np.array(p[:3])+rotation(p).apply([0,0,.0825])
def approach(piece):
 trace=[];settled=0
 for tick in range(250):
  s=snap(piece);robot=s['robot'];delta=center(s[piece])[:2]-np.array(robot[:2]);forward=rotation(robot).apply([0,-1,0])[:2]
  error=math.atan2(forward[0]*delta[1]-forward[1]*delta[0],float(np.dot(forward,delta)))
  distance=float(np.linalg.norm(delta));f=(math.copysign(max(.24,min(.4,abs(distance-.215)*4)),distance-.215) if abs(distance-.215)>.004 and abs(error)<.2 else 0);t=(math.copysign(max(.24,min(.4,abs(error))),error) if abs(error)>.025 else 0)
  if abs(distance-.215)<.004 and abs(error)<.025:settled+=1
  else:settled=0
  if tick%10==0:trace.append(dict(seconds=tick*.04,distance=distance,headingError=error,forward=float(f),turn=float(t)))
  if settled>=5:break
  step(.04,f=float(f),t=float(t))
 step(.5)
 return dict(aligned=settled>=5,trace=trace,final=snap(piece))
for piece in args.pieces:
 shape_file=P/('Unity/Assets/StreamingAssets/StadiumPieces/cup-collision.json' if piece.startswith('cup') else 'Unity/Assets/StreamingAssets/ReusedPieces/pin-collision.json')
 vertices=np.concatenate([np.asarray(x['vertices']) for x in json.loads(shape_file.read_text())])
 lib.pg_reset(0)
 if piece=='cup0':assert lib.pg_place_piece(b'pin0',-1.2,1.2,.003)
 assert lib.pg_place_piece(piece.encode(),0,.685,.003)
 step(1);cycles=[]
 for cycle in range(args.cycles):
  app=approach(piece) if cycle else None;before=snap(piece)
  step(1,j=-1,r=1);step(1.8,l=1);step(2);raised=snap(piece)
  step(.6,f=.4 if args.alternate_carry and cycle%2 else -.4);step(2);held=snap(piece)
  picked=center(held[piece])[2]>center(before[piece])[2]+.15
  if args.release_mode=='place':
   for tick in range(600):
    pose=snap(piece)[piece];bottom=(rotation(pose).apply(vertices)+np.array(pose[:3]))[:,2].min()
    if bottom<=.012:break
    step(.01,l=-1)
   step(.4);step(2,j=1);step(2,l=-1);step(1)
  elif args.release_mode=='lower':
   step(2,l=-1);step(1);step(2,j=1);step(1)
  else:step(2,j=1);step(2,l=-1);step(1)
  resting=snap(piece)
  row=dict(cycle=cycle+1,approach=app,before=before,raised=raised,held=held,resting=resting,pickedUp=bool(picked),carriedDistanceMeters=float(np.linalg.norm(np.array(held[piece][:2])-np.array(raised[piece][:2]))),pickedUpAndCarried=bool(picked and np.linalg.norm(np.array(held[piece][:2])-np.array(raised[piece][:2]))>.02),releasedToFloor=bool(center(resting[piece])[2]<.15))
  cycles.append(row);print(piece,cycle+1,picked,'resting center',center(resting[piece]).round(4),flush=True)
  if not picked:break
 rows.append(dict(piece=piece,cycles=cycles,passed=len(cycles)==args.cycles and all(c['pickedUpAndCarried'] and c['releasedToFloor'] for c in cycles)))
lib.pg_close()
report=dict(scope=__doc__,requestedCycles=args.cycles,releaseMode=args.release_mode,alternateCarry=args.alternate_carry,modelSHA256=hashlib.sha256((P/'Unity/Assets/StreamingAssets/playground.xml').read_bytes()).hexdigest(),nativeSHA256=hashlib.sha256((P/'Unity/Assets/Plugins/liboverride.dylib').read_bytes()).hexdigest(),cases=rows)
(P/args.output).write_text(json.dumps(report,indent=2)+'\n')
