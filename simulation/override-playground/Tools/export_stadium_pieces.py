"""Export licensed source piece variants with shared native geometry coordinates."""
from pathlib import Path
import json,struct,numpy as np,trimesh
P=Path(__file__).resolve().parents[1];out=P/'Unity/Assets/StreamingAssets/StadiumPieces';entries=[];audit=[]
scenario=json.loads((out/'scenario.json').read_text())
for kind,stem in [('redBlue','RedBluePin'),('redYellow','RedYellowPin'),('blueYellow','BlueYellowPin'),('yellowYellow','YellowYellowPin'),('cup','Cup')]:
 scene=trimesh.load(P/f'Research/Assets/V5RC-Override-H2H-_-{stem}.glb')
 for i,node in enumerate(scene.graph.nodes_geometry):
  tf,key=scene.graph[node];m=scene.geometry[key].copy();m.apply_transform(tf);material=m.visual.material;rgba=(material.main_color/255).tolist();material_name=material.name
  # Blue/red pin is rotated half a turn relative to the other source pin exports.
  # Normalize polygonal flange coordinates to the shared pin contact template.
  if kind in ['redYellow','blueYellow','yellowYellow']:m.vertices[:,[0,2]]*=-1
  m.vertices[:,1]-=scene.bounds[0,1];m.merge_vertices();m=trimesh.graph.smooth_shade(m,angle=np.radians(35))
  v=np.asarray(m.vertices,dtype='<f4');f=np.asarray(m.faces,dtype='<i4');norm=np.asarray(m.vertex_normals,dtype='<f4');name=f'{kind}-{i}.meshbin';(out/name).write_bytes(struct.pack('<ii',len(v),f.size)+v.tobytes()+f.tobytes()+norm.tobytes())
  if 'clear' in material_name.lower():rgba[3]=.35
  audit.append(dict(kind=kind,material=material_name,bounds=m.bounds.tolist()))
  for p in scenario['pieces']:
   if p['state']=='Field' and p['kind']==kind:entries.append(dict(file=name,body=p['id'],rgba=rgba))
(out/'manifest.json').write_text(json.dumps(dict(meshes=entries),indent=2))
(out/'COPYING.txt').write_bytes((P/'Research/scoring-LICENSE').read_bytes());(out/'SOURCE.txt').write_text('GPL-3.0 geometry from JerryLum/vex-v5-scoring-practice-override commit 572085f57dcedb501d781db6c5485349beb887cf. Original material groups and geometry, normalized local transforms, shared mesh binary format.\n')
(P/'Evidence/v2/stadium-piece-materials.json').write_text(json.dumps(audit,indent=2));print('Piece render instances',len(entries))
