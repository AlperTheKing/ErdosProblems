import json, pathlib, subprocess, sys
v11 = json.loads(pathlib.Path('tmp/eq_odl1_rung2_chart_batch_ledger_v11.json').read_text())
manifests = [r['manifest'] for r in v11['certified_rows']]
new = 'tmp\\eq_odl1_rung2_source_certificate_manifest_k5_G5_near_family_192prime_highspy_basis_margin_rows_soft_exact_v1.json'
if new not in manifests:
    manifests.append(new)
cmd = [sys.executable, '-B', 'problems/23/writeup/_codex_eq_odl1_rung2_batch_ledger.py']
for m in manifests:
    cmd += ['--manifest', m]
cmd += ['--pending-prefix', '20', '--out', 'tmp/eq_odl1_rung2_chart_batch_ledger_v12.json']
print('manifest_count', len(manifests))
subprocess.run(cmd, check=True)
