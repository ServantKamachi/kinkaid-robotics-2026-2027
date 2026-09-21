"""Dense compiled-model sweep plus CAD solid-check candidate generation."""
import json,itertools,argparse,hashlib
parser=argparse.ArgumentParser();parser.add_argument("--interfaces",action="store_true");parser.add_argument("--expanded",action="store_true");args=parser.parse_args()
suffix=("-interfaces" if args.interfaces else "")+("-expanded" if args.expanded else "")
from pathlib import Path
import mujoco as mj,numpy as np
from scipy.spatial.transform import Rotation
P=Path(__file__).resolve().parents[1]
x=mj.MjModel.from_xml_path(str(P/'Unity/Assets/StreamingAssets/playground.xml'));d=mj.MjData(x)
manifest=json.loads((P/'work/v2/cad-raw/manifest.json').read_text())
parts=[]
for e in manifest['meshes']:
    if not any(t in e['label'].lower() for t in ['arm','channel','upright','cross','brace','panel','plate','motor','gear','lever','jaw','wheel','roller','battery','brain','pneumatic']):continue
    if any(t in e['label'].lower() for t in ['screw','bearing']):continue
    with open(P/'work/v2/cad-raw'/e['file'],'rb') as f:
        nv,ni=np.frombuffer(f.read(8),dtype='<i4');v=np.frombuffer(f.read(int(nv)*12),dtype='<f4').reshape(-1,3)[:,[0,2,1]]
    q=e['rotation'];rot=Rotation.from_quat([-q[0],-q[2],-q[1],q[3]]).as_matrix();pos=np.array(e['position'])[[0,2,1]]
    corners=np.array(list(itertools.product(*zip(v.min(0),v.max(0)))))@rot.T+pos
    parts.append((e,corners,x.body(e['body']).id))
worst={};solid_candidates={};count=0
angles=np.linspace(-.72 if args.expanded else -.60,.0873,181 if args.expanded else 151)
jaws=np.linspace(.17453,1.3962634 if args.expanded else 1.0472,15 if args.expanded else 11)
for ai,angle in enumerate(angles):
 for ji,jaw in enumerate(jaws):
    for k in ['lift','lower_parallel','rear_upright','upper_lift','upper_parallel','claw_upright','jawL','jawR']:
        d.qpos[x.joint(k).qposadr[0]]=jaw if k.startswith('jaw') else -angle if k=='rear_upright' else angle
    for sign,side in [(-1,'L'),(1,'R')]:d.qpos[x.joint('gearSun'+side).qposadr[0]]=0
    mj.mj_forward(x,d);count+=1
    for c in d.contact:
        if c.dist<-.000001 and all(x.geom_contype[g]==2 for g in c.geom):
            pair=' | '.join(x.geom(int(g)).name for g in c.geom)
            if pair not in worst or c.dist<worst[pair]['distance']:worst[pair]=dict(distance=float(c.dist),lift=float(angle),jaw=float(jaw))
    if ai%10 or ji not in [0,5,10]:continue
    bounds=[]
    for e,corners,b in parts:
        world=corners@d.xmat[b].reshape(3,3).T+d.xpos[b];bounds.append((world.min(0),world.max(0)))
    for a,b in itertools.combinations(range(len(parts)),2):
        ea,_,ba=parts[a];eb,_,bb=parts[b]
        if ba==bb:continue
        # Connected link interfaces require a separate assembly check; retain nonadjacent pairs here.
        if not args.interfaces and (x.body_parentid[ba]==bb or x.body_parentid[bb]==ba):continue
        overlap=np.minimum(bounds[a][1],bounds[b][1])-np.maximum(bounds[a][0],bounds[b][0])
        if np.any(overlap<=-.001):continue
        key=ea['name']+' | '+eb['name'];volume=float(np.prod(overlap+.001))
        if key not in solid_candidates or volume>solid_candidates[key]['bboxOverlap']:
            solid_candidates[key]=dict(names=[ea['name'],eb['name']],lift=float(angle),jaw=float(jaw),bboxOverlap=volume,
                poses={e['body']:dict(position=d.xpos[bid].tolist(),quat=d.xquat[bid].tolist()) for e,_,bid in [parts[a],parts[b]]})
report=dict(modelSHA256=hashlib.sha256((P/'Unity/Assets/StreamingAssets/playground.xml').read_bytes()).hexdigest(),cadSHA256=hashlib.sha256((P/'CAD/RatchetingClaw-Simulation.FCStd').read_bytes()).hexdigest(),status='PASS' if not worst else 'FAIL',scope='Native non-excluded structural colliders only; solid and joint-interface checks separate',poseCount=count,liftRange=[float(angles[0]),float(angles[-1])],jawRange=[float(jaws[0]),float(jaws[-1])],worstContacts=worst,solidCandidateCount=len(solid_candidates))
(P/('Evidence/v2/assembly-collider-sweep'+suffix+'.json')).write_text(json.dumps(report,indent=2)+'\n')
(P/('work/v2/solid-candidates'+suffix+'.json')).write_text(json.dumps(list(solid_candidates.values()),indent=2))
print(json.dumps(report,indent=2))

assert not worst, "Structural contact sweep failed; inspect saved report before downstream tests"
