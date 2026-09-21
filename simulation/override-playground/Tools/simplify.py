import json,struct,numpy as np,fast_simplification as fs,pathlib
p=pathlib.Path('/Users/kamachi/Documents/OverridePlayground/Unity/Assets/StreamingAssets/Robot');m=json.loads((p/'manifest.json').read_text())
for e in m['meshes']:
 f=p/e['file'];data=f.read_bytes();nv,ni=struct.unpack_from('<ii',data);v=np.frombuffer(data,dtype='<f4',count=nv*3,offset=8).reshape(-1,3);t=np.frombuffer(data,dtype='<i4',count=ni,offset=8+nv*12).reshape(-1,3)
 target=min(len(t),max(100,int(len(t)*.14)))
 if len(t)==e["triangles"] and target<len(t):v,t=fs.simplify(v.astype(np.float64).copy(),t.copy(),target_count=target,agg=5)
 f.write_bytes(struct.pack('<ii',len(v),t.size)+np.asarray(v,dtype='<f4').tobytes()+np.asarray(t,dtype='<i4').tobytes());e['vertices']=len(v);e['triangles']=len(t)
(p/'manifest.json').write_text(json.dumps(m,indent=2));print('Visual triangles:',sum(e['triangles'] for e in m['meshes']))
