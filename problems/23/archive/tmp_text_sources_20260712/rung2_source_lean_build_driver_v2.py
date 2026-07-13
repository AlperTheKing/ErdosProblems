import concurrent.futures
import json
import sys
from pathlib import Path

sys.path.append('problems/23/writeup')
import _codex_eq_odl1_rung2_lean_build as b

root = Path.cwd()
formal = (root / 'formal-conjectures').resolve()
src = (root / 'problems/23/lean').resolve()
build = (root / 'tmp/rung2_source_lean_o_v2').resolve()
build.mkdir(parents=True, exist_ok=True)

support = src / 'Erdos23Delta0/Cert/Rung2SourceSupport.lean'
shards = sorted((src / 'Erdos23Delta0/Cert/Rung2SourceData').glob('Shard*.lean'))
index = src / 'Erdos23Delta0/Cert/Rung2SourceData.lean'
results = []

res = b.run_lean(formal, src, build, support)
results.append(res)
print(f"{res['module']} rc={res['returncode']} sec={res['seconds']}", flush=True)

if res['returncode'] == 0:
    with concurrent.futures.ThreadPoolExecutor(max_workers=6) as ex:
        futs = [ex.submit(b.run_lean, formal, src, build, p) for p in shards]
        for fut in concurrent.futures.as_completed(futs):
            r = fut.result()
            results.append(r)
            print(f"{r['module']} rc={r['returncode']} sec={r['seconds']}", flush=True)

if all(r['returncode'] == 0 for r in results):
    r = b.run_lean(formal, src, build, index)
    results.append(r)
    print(f"{r['module']} rc={r['returncode']} sec={r['seconds']}", flush=True)

failures = [r for r in results if r['returncode'] != 0]
summary = {
    'schema': 'eq_odl1_rung2_source_lean_build_v1',
    'src_root': str(src),
    'build_root': str(build),
    'workers': 6,
    'recovery_policy': 'fresh_rerun_on_write_permission_error',
    'count': len(results),
    'shard_count': len(shards),
    'failures': failures,
    'results': sorted(results, key=lambda x: x['module']),
}
out = root / 'tmp/eq_odl1_rung2_source_lean_build_k5_G6_near_lexsmall_96prime_v2_summary.json'
out.write_text(json.dumps(summary, indent=2), encoding='utf-8')
print(('FAIL' if failures else 'PASS') + f' modules={len(results)} shards={len(shards)} summary={out}', flush=True)
raise SystemExit(1 if failures else 0)
