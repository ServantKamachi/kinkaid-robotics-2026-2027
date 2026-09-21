"""Reuse Jerry Lum's GPL-3 Override meshes at their scene scale.
Pinned source and full license: Research/REUSE_AUDIT.md, Research/scoring-LICENSE.
Visual meshes retain the two source material groups. Pin contact hulls are
horizontal convex slices of the source surface, preserving the hex flange.
Cups retain the separately disclosed hollow approximate contact model.
"""
from pathlib import Path
import json, struct
import numpy as np
import trimesh
P=Path(__file__).resolve().parents[1]
out=P/'Unity/Assets/StreamingAssets/ReusedPieces';out.mkdir(exist_ok=True)
manifest={'meshes':[]}; collision=[]
for piece,file in [('pin','RedBluePin'),('cup','Cup')]:
 scene=trimesh.load(P/f'Research/Assets/V5RC-Override-H2H-_-{file}.glb')
 meshes=[]
 for node in scene.graph.nodes_geometry:
  tf,key=scene.graph[node];m=scene.geometry[key].copy();m.apply_transform(tf);meshes.append(m)
 bounds=scene.bounds; height=float(bounds[1,1]-bounds[0,1]);expected=.1651 if piece=='pin' else .1645
 assert abs(height-expected)<.0002,(piece,height)
 for group,m in enumerate(meshes):
  # Source scene Y-up; Unity also Y-up, reflection matches source Z -> MuJoCo Y.
  v=m.vertices.copy();v[:,1]-=bounds[0,1]
  f=m.faces.copy()
  name=f'{piece}{group}.meshbin';v=np.asarray(v,dtype='<f4');f=np.asarray(f,dtype='<i4')
  (out/name).write_bytes(struct.pack('<ii',len(v),f.size)+v.tobytes()+f.tobytes())
  rgba=(m.visual.material.main_color/255).tolist()
  for i in range(12 if piece=='pin' else 6):manifest['meshes'].append({'file':name,'body':f'{piece}{i}','rgba':rgba})
 if piece=='pin':
  whole=trimesh.util.concatenate(meshes)
  # Slice at every profile shoulder; convexity only within each narrow band.
  levels=[-.0825,-.065,-.010,-.005,0,.005,.010,.065,.0825]
  for k,(lo,hi) in enumerate(zip(levels,levels[1:])):
   cut=whole.slice_plane([0,lo-1e-8,0],[0,1,0]).slice_plane([0,hi+1e-8,0],[0,-1,0])
   hull=cut.convex_hull; v=hull.vertices[:,[0,2,1]];v[:,2]-=bounds[0,1]
   collision.append({'name':f'pin_slice{k}','vertices':v.tolist()})
(out/'manifest.json').write_text(json.dumps(manifest,indent=2))
(out/'pin-collision.json').write_text(json.dumps(collision))
(out/'SOURCE.txt').write_text('Geometry: JerryLum/vex-v5-scoring-practice-override\nCommit: 572085f57dcedb501d781db6c5485349beb887cf\nhttps://github.com/Jerrylum/vex-v5-scoring-practice-override\nLicense GPL-3.0; full text in COPYING.txt.\nScene transforms applied; pin contacts are sliced convex hull approximations. Cup wall contacts remain provisional.\n')
(out/'COPYING.txt').write_bytes((P/'Research/scoring-LICENSE').read_bytes())
print('Reusable pieces exported;',len(collision),'pin contact slices')
