"""Sequential candidate graphics checks. Run without builds or CAD audit workloads."""
from pathlib import Path
import argparse,json,subprocess,hashlib,platform,datetime
P=Path(__file__).resolve().parents[1]
a=argparse.ArgumentParser();a.add_argument('--scenes',type=int,nargs='+',default=[0,1,2]);a.add_argument('--stadium',action='store_true');a.add_argument('--duration',type=float,default=65);args=a.parse_args()
if not 65<=args.duration<=3600:a.error('Duration must be between65 and3600seconds')
run_suffix='' if args.duration==65 else '-'+format(args.duration,'g')+'s'
b=json.loads((P/'Evidence/v2/latest-candidate.json').read_text());app=Path(b['application']);results=[]
for scene in ([0] if args.stadium else args.scenes):
 out=P/'Evidence/v2'/('performance-'+b['buildId'])/(('stadium' if args.stadium else str(scene))+run_suffix);out.mkdir(parents=True,exist_ok=True)
 subprocess.run([str(app/'Contents/MacOS/Override Playground'),'-screen-fullscreen','0','-screen-width','1280','-screen-height','820','--benchmark','--view','0' if args.stadium else '1','--scene',str(scene),'--duration',str(args.duration),'--evidence',str(out),'-logFile',str(out/'player.log')]+(['--stadium'] if args.stadium else []),stdout=subprocess.DEVNULL,stderr=subprocess.STDOUT,check=True,timeout=args.duration+85)
 f=max(out.glob('metrics-*.json'),key=lambda p:p.stat().st_mtime);m=json.loads(f.read_text())
 m['meetsBudget']=(m.get('benchmark') is True and m.get('scriptedCommands') is True and m['stadium']==args.stadium and m['frameP99ms']<=25 and m['framesOver50ms']==0 and m['physicsP99ms']<=6 and m['badAcceleration']==m['badPosition']==0 and m['simulationSeconds']/m['measuredWallSeconds']>=.98 and m['pixelWidth']==1280 and m['pixelHeight']==820 and m['frames']>3000)
 results.append(m);print(json.dumps(m),flush=True)
report=dict(buildId=b['buildId'],application=str(app),scope='Stadium scripted motion; not manipulation or fidelity acceptance' if args.stadium else 'Selected practice scenarios; not full-field release validation',machine=platform.platform(),recordedAt=datetime.datetime.now(datetime.timezone.utc).isoformat(),packagedBuildInfoSHA256=hashlib.sha256((app/'Contents/Resources/Data/StreamingAssets/build-info.json').read_bytes()).hexdigest(),cases=results)
(P/'Evidence/v2'/('performance-'+b['buildId'])/(('stadium-summary' if args.stadium else 'summary')+run_suffix+'.json')).write_text(json.dumps(report,indent=2))
assert all(r['meetsBudget'] for r in results),'Candidate misses performance gate'
