import json, pathlib, subprocess, sys
prev = json.loads(pathlib.Path('tmp/eq_odl1_rung2_chart_batch_ledger_v13.json').read_text())
manifests = [r['manifest'] for r in prev['certified_rows']]
new = 'tmp\\eq_odl1_rung2_source_certificate_manifest_k8_F4_near_lexlarge_192prime_v1.json'
if new not in manifests:
    manifests.append(new)
cmd = [sys.executable, '-B', 'problems/23/writeup/_codex_eq_odl1_rung2_batch_ledger.py']
for m in manifests:
    cmd += ['--manifest', m]
cmd += ['--pending-prefix', '20', '--out', 'tmp/eq_odl1_rung2_chart_batch_ledger_v14.json']
print('manifest_count', len(manifests))
subprocess.run(cmd, check=True)
