"""Sequential graphics benchmarks: no overlapping simulator or build workloads."""
from pathlib import Path
import subprocess,json
P=Path(__file__).resolve().parents[1];results=[]
for scene in range(3):
 out=P/f'Evidence/verified-scene{scene}';out.mkdir(exist_ok=True)
 command=[str(P/'Builds/Override Playground.app/Contents/MacOS/Override Playground'),'--benchmark','--scene',str(scene),'--duration','65','--evidence',str(out),'-logFile',str(out/'player.log')]
 print('Starting scene',scene,flush=True)
 subprocess.run(command,stdout=subprocess.DEVNULL,stderr=subprocess.STDOUT,check=True,timeout=150)
 f=max(out.glob('metrics-*.json'),key=lambda p:p.stat().st_mtime);m=json.loads(f.read_text());results.append(m);print(json.dumps(m),flush=True)
(P/'Evidence/final-benchmarks.json').write_text(json.dumps(results,indent=2))
