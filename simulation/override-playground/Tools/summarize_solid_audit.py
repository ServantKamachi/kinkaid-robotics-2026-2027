"""Summarize current-CAD exact checks without treating timeouts as passes."""
from pathlib import Path
import collections, hashlib, json

P = Path(__file__).resolve().parents[1]
cad = hashlib.sha256((P / 'CAD/RatchetingClaw-Simulation.FCStd').read_bytes()).hexdigest()
folder = P / 'Evidence/v2/solid-batches' / cad
cases = json.loads((P / 'work/v2/solid-candidates-interfaces.json').read_text())
entries = {e['name']: e for e in json.loads((P / 'work/v2/cad-raw/manifest.json').read_text())['meshes']}
rows = []
for i, case in enumerate(cases):
    file = folder / f'{i}.json'
    result = json.loads(file.read_text()) if file.exists() else {}
    if result:
        assert result['cadSHA256'] == cad, 'Stale CAD evidence'
    status = ('UNRESOLVED' if not result or result['status'] == 'UNRESOLVED'
              else 'FAIL' if result['status'] == 'FAIL' or result.get('sampledClearanceStatus') == 'FAIL'
              else 'PASS')
    row = dict(index=i, names=case['names'],
               bodies=[entries[n]['body'] for n in case['names']], status=status)
    if result.get('cases'):
        measured = result['cases'][0]
        assert measured['names'] == case['names']
        row.update(overlapMm3=measured['overlapMm3'], distanceMm=measured['distanceMm'],
                   lift=measured['lift'], jaw=measured['jaw'])
    rows.append(row)
counts = dict(collections.Counter(r['status'] for r in rows))
scope = ('Exact solids at the selected maximum bounding-box-overlap pose for each pair. '
         'This is not a continuous clearance certificate or a mounting-connectivity check. '
         'A failed clearance target can mean either intersection or less than 1 mm clearance.')
report = dict(cadSHA256=cad, scope=scope, counts=counts, cases=rows)
(P / 'Evidence/v2/solid-audit-summary.json').write_text(json.dumps(report, indent=2) + '\n')
lines = ['# Current assembly clearance findings', '', scope, '', f'CAD SHA256: `{cad}`', '',
         ', '.join(f'{n} {status.lower()}' for status, n in sorted(counts.items())) + '.', '',
         '## Failed checks by mechanism', '',
         '| Pair | Bodies | Parts | Intersection (mm³) | Minimum distance (mm) |',
         '|---|---|---|---:|---:|']
for r in sorted((x for x in rows if x['status'] == 'FAIL'), key=lambda x: (x['bodies'], x['index'])):
    distance = '≥1' if r['distanceMm'] is None else f"{r['distanceMm']:.4f}"
    lines.append(f"| {r['index']} | {' / '.join(r['bodies'])} | {' / '.join(r['names'])} | {r['overlapMm3']:.3f} | {distance} |")
lines += ['', '## Unresolved checks', '',
          ', '.join(str(r['index']) for r in rows if r['status'] == 'UNRESOLVED') or 'None.', '',
          'Retain the original CAD and tested app. Any part spacing correction must also update its '
          'shafts, bearings, ties and fasteners before adoption; moving an isolated collider does not fix an assembly.', '']
(P / 'CAD/CLEARANCE-STATUS.md').write_text('\n'.join(lines))
print(json.dumps(counts))
