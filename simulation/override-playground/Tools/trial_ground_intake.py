"""Simulation-only lower jaw-carrier mounting trial. Production assets remain unchanged.
Uses ordinary native commands after one initial fixture placement. This is a
feasibility screen, not mounting/adjacent-interface CAD validation or calibration.
"""
from pathlib import Path
import xml.etree.ElementTree as X
import ctypes as C,json,hashlib,math,argparse
from itertools import product
import numpy as np,mujoco as mj
from scipy.spatial.transform import Rotation
P=Path(__file__).resolve().parents[1];A=P/'Unity/Assets/StreamingAssets'
p=argparse.ArgumentParser();p.add_argument('--drops',nargs='+',type=float,default=[0,12.7,25.4,38.1]);p.add_argument('--model',default=str(A/'playground.xml'));p.add_argument('--native',default=str(P/'Unity/Assets/Plugins/liboverride.dylib'));p.add_argument('--lift-min',type=float,default=-.6);p.add_argument('--output',default='Evidence/v2/ground-intake-trials.json');p.add_argument('--target-y',nargs='+',type=float,default=[.685]);p.add_argument('--pieces',nargs='+',default=['pin0','cup0']);p.add_argument('--orientations',nargs='+',choices=['upright','side-long','side-cross'],default=['upright','side-long','side-cross']);p.add_argument('--intake-lift',action='store_true');p.add_argument('--close-drive',type=float,default=0);args=p.parse_args()
lib=C.CDLL(args.native);lib.pg_load.argtypes=[C.c_char_p,C.c_char_p,C.c_int];lib.pg_command.argtypes=[C.c_double]*5;lib.pg_poses.argtypes=[C.POINTER(C.c_double)];lib.pg_status.argtypes=[C.POINTER(C.c_double)];lib.pg_body.argtypes=[C.c_char_p]
rows=[];out=P/'work/v2/ground-intake-trials';out.mkdir(exist_ok=True)
def vec(v):return ' '.join(str(float(x)) for x in v)
for drop in args.drops:
 sweep=X.parse(args.model)
 for side in ['L','R']:
  body=sweep.getroot().find(f".//body[@name='jaw{side}']");pos=np.fromstring(body.get('pos'),sep=' ');pos[2]-=drop/1000;body.set('pos',vec(pos))
 path=out/f'drop-{drop}.xml';sweep.write(path,encoding='unicode')
 m=mj.MjModel.from_xml_path(str(path));d=mj.MjData(m);worst={}
 for angle in np.linspace(args.lift_min,.0873,31):
  for jaw in np.linspace(.17453,1.0472,5):
   for name in ['lift','lower_parallel','rear_upright','upper_lift','upper_parallel','claw_upright','jawL','jawR']:
    d.qpos[m.joint(name).qposadr[0]]=jaw if name.startswith('jaw') else -angle if name=='rear_upright' else angle
   mj.mj_forward(m,d)
   for c in d.contact:
    if c.dist<-.000001 and all(m.geom_contype[g]==2 for g in c.geom):
     key=' | '.join(m.geom(int(g)).name for g in c.geom);worst[key]=max(worst.get(key,0),float(-c.dist*1000))
 trials=[]
 for piece in args.pieces:
  shape=A/('ReusedPieces/pin-collision.json' if piece.startswith('pin') else 'StadiumPieces/cup-collision.json')
  vertices=np.concatenate([np.asarray(v['vertices']) for v in json.loads(shape.read_text())])
  for orientation,approach_y in product(args.orientations,args.target_y):
   rot=Rotation.identity() if orientation=='upright' else Rotation.from_euler('x' if orientation=='side-long' else 'y',90,degrees=True)
   v=rot.apply(vertices);center=rot.apply([0,0,.0825]);position=np.array([0,approach_y,.003])-np.array([center[0],center[1],v[:,2].min()]);q=rot.as_quat()
   root=X.fromstring(X.tostring(sweep.getroot()));b=root.find(f".//body[@name='{piece}']");b.set('pos',vec(position));b.set('quat',vec([q[3],*q[:3]]))
   if piece=='cup0':root.find(".//body[@name='pin0']").set('pos','-1.2 1.2 .003')
   fixture=out/'fixture.xml';X.ElementTree(root).write(fixture,encoding='unicode');err=C.create_string_buffer(4096);n=lib.pg_load(str(fixture).encode(),err,4096);assert n,err.value
   poses=(C.c_double*(n*7))();status=(C.c_double*12)();pid=lib.pg_body(piece.encode())
   def snap():
    lib.pg_poses(poses);lib.pg_status(status);assert np.isfinite(list(poses)).all() and status[8]==status[9]==0
    return list(poses[pid*7:pid*7+7])
   def extra():
    cid=lib.pg_body(b'claw');return dict(claw=list(poses[cid*7:cid*7+7]),robotOrigin=list(status)[5:8],lift=status[2],liftTarget=status[10],jaw=status[3],jawTarget=status[11])
   def step(seconds,f=0,t=0,l=0,j=0,r=0):lib.pg_command(f,t,l,j,r);lib.pg_step(round(seconds/.002))
   step(1);before=snap();before_extra=extra();step(1,f=args.close_drive,j=-1,r=1);closed=snap();closed_extra=extra();step(1.8,l=1,r=1 if args.intake_lift else 0);step(5);held=snap();held_extra=extra();step(2,j=1);step(2);released=snap();released_extra=extra()
   def center_z(p):return float(p[2]+Rotation.from_quat([*p[4:7],p[3]]).apply([0,0,.0825])[2])
   trial=dict(piece=piece,orientation=orientation,approachY=approach_y,before=before,closed=closed,held=held,released=released,states=dict(before=before_extra,closed=closed_extra,held=held_extra,released=released_extra),pickedUp=center_z(held)>center_z(before)+.15,releasedToFloor=center_z(released)<.15);trials.append(trial)
   print('drop',drop,piece,orientation,approach_y,'picked',trial['pickedUp'],'released',trial['releasedToFloor'],flush=True);lib.pg_close()
 rows.append(dict(dropMm=drop,nonexcludedStructuralPoseCount=155,worstStructuralPenetrationMm=worst,trials=trials))
 report=dict(scope=__doc__,intakeDuringLift=args.intake_lift,driveDuringClose=args.close_drive,originalModelSHA256=hashlib.sha256(Path(args.model).read_bytes()).hexdigest(),nativeSHA256=hashlib.sha256(Path(args.native).read_bytes()).hexdigest(),cases=rows)
 (P/args.output).write_text(json.dumps(report,indent=2)+'\n')
