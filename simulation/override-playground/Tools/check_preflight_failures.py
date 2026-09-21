"""Exercise damaged-package failures in an isolated copy, never production assets."""
from pathlib import Path
import tempfile,shutil,json,sys
from preflight import check,P
reports=[]
with tempfile.TemporaryDirectory(prefix='preflight-',dir=P/'work') as name:
 root=Path(name);assets=root/'Unity/Assets';assets.mkdir(parents=True)
 shutil.copytree(P/'Unity/Assets/StreamingAssets',assets/'StreamingAssets');(assets/'Plugins').symlink_to(P/'Unity/Assets/Plugins',target_is_directory=True)
 manifest=assets/'StreamingAssets/Field/manifest.json';original=manifest.read_bytes();source=json.loads(original);mesh=assets/'StreamingAssets/Field'/source['meshes'][0]['file'];mesh_original=mesh.read_bytes()
 for case in ['missing-file','truncated-mesh','missing-body','bad-transform','escaping-path']:
  data=json.loads(original)
  if case=='missing-file':data['meshes'][0]['file']='missing.meshbin'
  elif case=='truncated-mesh':mesh.write_bytes(mesh_original[:7])
  elif case=='missing-body':data['meshes'][0]['body']='unavailable-body'
  elif case=='bad-transform':data['meshes'][0]['rotation']=[0,0,0,0]
  elif case=='escaping-path':data['meshes'][0]['file']='../Robot/Part_channel2_35.meshbin'
  manifest.write_text(json.dumps(data))
  try:check(root)
  except (ValueError,FileNotFoundError) as ex:reports.append({'case':case,'status':'PASS','detected':str(ex)})
  else:raise AssertionError('Damaged package passed: '+case)
  finally:manifest.write_bytes(original);mesh.write_bytes(mesh_original)
 report=check(root);assert report['status']=='PASS';reports.append({'case':'restored-package','status':'PASS'})
(P/'Evidence/v2/preflight-failures.json').write_text(json.dumps(reports,indent=2));print(json.dumps(reports,indent=2))
