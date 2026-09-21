"""Bound each OCCT pair in a separate process; retain unresolved pairs explicitly."""
from pathlib import Path
import subprocess,json,hashlib,argparse,datetime,shutil
P=Path(__file__).resolve().parents[1];a=argparse.ArgumentParser();a.add_argument('--start',type=int,default=0);a.add_argument('--stop',type=int);a.add_argument('--timeout',type=int,default=90);a.add_argument('--retry-unresolved',action='store_true');args=a.parse_args()
cases=json.loads((P/'work/v2/solid-candidates-interfaces.json').read_text());cad=hashlib.sha256((P/'CAD/RatchetingClaw-Simulation.FCStd').read_bytes()).hexdigest();folder=P/'Evidence/v2/solid-batches'/cad;folder.mkdir(parents=True,exist_ok=True)
for i in range(args.start,min(args.stop or len(cases),len(cases))):
 out=folder/f'{i}.json'
 if out.exists():
  if not args.retry_unresolved or json.loads(out.read_text())['status']!='UNRESOLVED':continue
  history=folder/'history'/(datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%S%fZ')+f'-pair{i}')
  history.mkdir(parents=True)
  shutil.copy2(out,history/out.name)
  if (folder/f'{i}.log').exists():shutil.copy2(folder/f'{i}.log',history/f'{i}.log')
 script=folder/f'{i}.py';suffix=f'-batch-{i}'
 report=P/f'Evidence/v2/assembly-solid-audit-interfaces{suffix}.json'
 # A successful worker must create a fresh report, never reuse a stale result.
 if report.exists():
  archive=folder/'history';archive.mkdir(exist_ok=True)
  report.rename(archive/(datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%S%fZ')+'-'+report.name))
 script.write_text(f"AUDIT_SUFFIX='-interfaces'\nAUDIT_INDICES=[{i}]\nAUDIT_OUTPUT_SUFFIX={suffix!r}\nexec(open({str(P/'Tools/audit_assembly_solids.py')!r}).read())\n")
 try:
  with (folder/f'{i}.log').open('w') as log:
   r=subprocess.run(['/opt/homebrew/bin/freecadcmd','-c',f'exec(open({str(script)!r}).read())'],stdout=log,stderr=subprocess.STDOUT,timeout=args.timeout)
  if r.returncode or not report.exists():raise RuntimeError('Worker failed; inspect pair log')
  data=json.loads(report.read_text());assert data['cadSHA256']==cad
  assert len(data['cases'])==1 and data['cases'][0]['names']==cases[i]['names']
 except (subprocess.TimeoutExpired,RuntimeError,AssertionError) as e:
  data=dict(status='UNRESOLVED',reason=str(e),names=cases[i]['names'],cadSHA256=cad)
 data['timeoutSeconds']=args.timeout
 data['caseSHA256']=hashlib.sha256(json.dumps(cases[i],sort_keys=True).encode()).hexdigest()
 out.write_text(json.dumps(data,indent=2));print(i,cases[i]['names'],data['status'],data.get('sampledClearanceStatus',''),flush=True)
reports=[json.loads(p.read_text()) for p in folder.glob('*.json')]
summary=dict(cadSHA256=cad,totalPairs=len(cases),attemptedPairs=len(reports),completedPairs=sum(r['status']!='UNRESOLVED' for r in reports),failed=sum(r['status']=='FAIL' or r.get('sampledClearanceStatus')=='FAIL' for r in reports),unresolved=sum(r['status']=='UNRESOLVED' for r in reports),status='PASS' if len(reports)==len(cases) and all(r['status']=='PASS' and r.get('sampledClearanceStatus')=='PASS' for r in reports) else 'INCOMPLETE_OR_FAILED')
(folder/'summary.txt').write_text(json.dumps(summary,indent=2));print(summary)
