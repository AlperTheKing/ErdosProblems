import concurrent.futures
import json
import subprocess
import time
from pathlib import Path

root = Path(r'E:/Projects/ErdosProblems')
workdir = root / 'formal-conjectures'
files = sorted((root / 'problems/23/lean/Erdos23Delta0/Cert/BranchBData').glob('Shard*.lean'))

def run(path):
    rel = Path('..') / path.relative_to(root)
    t0 = time.time()
    proc = subprocess.run(['lake', 'env', 'lean', str(rel)], cwd=workdir, text=True, capture_output=True)
    return {
        'file': str(path.relative_to(root)),
        'returncode': proc.returncode,
        'seconds': round(time.time() - t0, 3),
        'stdout': proc.stdout[-2000:],
        'stderr': proc.stderr[-4000:],
    }

workers = 8
results = []
with concurrent.futures.ThreadPoolExecutor(max_workers=workers) as ex:
    futs = [ex.submit(run, p) for p in files]
    for fut in concurrent.futures.as_completed(futs):
        res = fut.result()
        results.append(res)
        print(f"{res['file']} rc={res['returncode']} sec={res['seconds']}", flush=True)

results.sort(key=lambda r: r['file'])
summary = {
    'schema': 'branchb_lean_all_shards_check_v1',
    'workers': workers,
    'count': len(results),
    'failures': [r for r in results if r['returncode'] != 0],
    'results': results,
}
out = root / 'tmp/branchb_lean_all_shards_v5_summary.json'
out.write_text(json.dumps(summary, indent=2), encoding='utf-8')
if summary['failures']:
    print(f"FAIL failures={len(summary['failures'])} summary={out}")
    raise SystemExit(1)
print(f"PASS shards={len(results)} summary={out}")
