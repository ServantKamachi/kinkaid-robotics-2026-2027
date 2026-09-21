"""Build a candidate without overwriting the preserved prototype. Run with .venv/bin/python."""
from pathlib import Path
import subprocess,sys,json,hashlib,datetime,os
from preflight import check
P=Path(__file__).resolve().parents[1];E=P/'Evidence/v2';E.mkdir(exist_ok=True)
UNITY=Path('/Applications/Unity/Hub/Editor/6000.6.2f1/Unity.app/Contents/MacOS/Unity')
if not UNITY.is_file():raise SystemExit('Required Unity editor missing: '+str(UNITY))
base=json.loads((P/'Evidence/baseline-preservation/checkpoint.json').read_text())
if hashlib.sha256(Path(base['originalCAD']).read_bytes()).hexdigest()!=base['originalCADSHA256']:raise SystemExit('Original robot CAD changed; stop and investigate before building.')
subprocess.run(['zsh',str(P/'Tools/build_native.sh')],cwd=P,check=True)
report=check(P);(E/'preflight.json').write_text(json.dumps(report,indent=2))
ident=datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%SZ');dest=P/'Builds/Candidates'/ident/'Override Playground.app';dest.parent.mkdir(parents=True,exist_ok=True);log=E/f'build-{ident}.log'
version={'buildId':ident,'sourceCommit':subprocess.check_output(['git','rev-parse','HEAD'],cwd=P,text=True).strip(),'engine':report['engine'],'originalCADSHA256':base['originalCADSHA256'],'status':'development candidate; release validation required','sourceFiles':{str(f.relative_to(P)):hashlib.sha256(f.read_bytes()).hexdigest() for folder in ['Tools','Unity/Assets/Scripts','Unity/Assets/Editor','Unity/Packages','Unity/ProjectSettings'] for f in (P/folder).rglob('*') if f.is_file() and '__pycache__' not in str(f)},'assetSHA256':report['assetSHA256']}
(P/'Unity/Assets/StreamingAssets/build-info.json').write_text(json.dumps(version,indent=2));env=os.environ.copy();env['OVERRIDE_BUILD_OUTPUT']=str(dest)
r=subprocess.run([str(UNITY),'-batchmode','-nographics','-projectPath',str(P/'Unity'),'-executeMethod','BuildPlayground.Build','-quit','-logFile',str(log)],env=env,cwd=P)
if r.returncode or not dest.exists() or 'PLAYGROUND_BUILD_SUCCESS' not in log.read_text():raise SystemExit('Candidate build failed; inspect '+str(log))
version.update(application=str(dest),log=str(log));(E/'latest-candidate.json').write_text(json.dumps(version,indent=2));print('CANDIDATE_BUILD_SUCCESS '+str(dest),flush=True)
