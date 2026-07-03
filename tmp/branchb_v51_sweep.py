import concurrent.futures as cf
import json
import subprocess
import time
from pathlib import Path

root = Path('E:/Projects/ErdosProblems')
fc = root / 'formal-conjectures'
paths = sorted((root / 'problems/23/lean/Erdos23Delta0/Cert/BranchBData').glob('Shard*.lean'))

def run(path):
    arg = '..\\' + str(path.relative_to(root)).replace('/', '\\')
    t0 = time.time()
    proc = subprocess.run(['lake', 'env', 'lean', arg], cwd=fc, text=True, capture_output=True)
    return {
        'file': str(path),
        'exit': proc.returncode,
        'seconds': round(time.time() - t0, 3),
        'stdout': proc.stdout[-2000:],
        'stderr': proc.stderr[-4000:],
    }

with cf.ThreadPoolExecutor(max_workers=8) as ex:
    results = list(ex.map(run, paths))
summary = {
    'schema': 'branchb_v51_selfcontained_all_shards_lean_sweep_v1',
    'workers': 8,
    'count': len(results),
    'failures': [r for r in results if r['exit'] != 0],
    'results': results,
}
out = root / 'tmp/branchb_v51_selfcontained_all_shards_summary.json'
out.write_text(json.dumps(summary, indent=2, sort_keys=True), encoding='utf-8')
print(json.dumps({'count': summary['count'], 'failures': len(summary['failures']), 'out': str(out)}, indent=2))
if summary['failures']:
    raise SystemExit(1)
