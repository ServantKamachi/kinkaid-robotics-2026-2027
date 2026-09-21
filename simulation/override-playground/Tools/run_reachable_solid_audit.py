"""Bound exact OCCT checks for reachable-intake parts in isolated workers."""
from pathlib import Path
import subprocess, json, hashlib, argparse

P = Path(__file__).resolve().parents[1]
a = argparse.ArgumentParser()
a.add_argument('--timeout', type=int, default=30)
args = a.parse_args()
suffix = '-interfaces-expanded'
indices = [0, 7, 14, 15, 48, 49, 50, 51, 91, 92, 94, 95]
cases = json.loads((P / f'work/v2/solid-candidates{suffix}.json').read_text())
cad = hashlib.sha256((P / 'CAD/RatchetingClaw-Simulation.FCStd').read_bytes()).hexdigest()
folder = P / 'Evidence/v2/reachable-solid-batches' / cad
folder.mkdir(parents=True, exist_ok=True)
rows = []
for i in indices:
    expected = cases[i]['names']
    worker = P / 'work/v2' / f'reachable-solid-{i}.py'
    output_suffix = f'-reachable-{i}'
    report = P / f'Evidence/v2/assembly-solid-audit{suffix}{output_suffix}.json'
    worker.write_text(
        f"AUDIT_SUFFIX={suffix!r}\nAUDIT_INDICES=[{i}]\n"
        f"AUDIT_OUTPUT_SUFFIX={output_suffix!r}\n"
        f"exec(open({str(P / 'Tools/audit_assembly_solids.py')!r}).read())\n")
    try:
        result = subprocess.run(
            ['/opt/homebrew/bin/freecadcmd', '-c', str(worker)],
            stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True,
            timeout=args.timeout)
        if result.returncode or not report.exists():
            raise RuntimeError('worker failed')
        data = json.loads(report.read_text())
        measured = data['cases'][0]
        if data['cadSHA256'] != cad or measured['names'] != expected:
            raise RuntimeError('stale or mismatched result')
        row = dict(index=i, names=expected, status=(
            'PASS' if measured['meetsSampledClearanceTarget'] else 'FAIL'),
            overlapMm3=measured['overlapMm3'], distanceMm=measured['distanceMm'])
    except subprocess.TimeoutExpired:
        row = dict(index=i, names=expected, status='UNRESOLVED', reason=f'timeout after {args.timeout}s')
    except Exception as exc:
        row = dict(index=i, names=expected, status='UNRESOLVED', reason=str(exc))
    (folder / f'{i}.json').write_text(json.dumps(row, indent=2) + '\n')
    rows.append(row)
    print(i, expected, row['status'], flush=True)
report = dict(cadSHA256=cad, scope='Targeted exact solids for the coherent reachable-intake mounting and transmission changes; bounded workers preserve unresolved checks.', cases=rows,
              counts={s:sum(r['status']==s for r in rows) for s in ['PASS','FAIL','UNRESOLVED']})
(P / 'Evidence/v2/reachable-solid-audit.json').write_text(json.dumps(report, indent=2) + '\n')
print(json.dumps(report['counts']))
