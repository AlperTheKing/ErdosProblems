import json, pathlib, hashlib, datetime
manifest=pathlib.Path('tmp/eq_odl1_rung2_source_certificate_manifest_k6_G5_near_family_192prime_multirepair_v1.json')
ledger=pathlib.Path('tmp/eq_odl1_rung2_chart_batch_ledger_v16.json')
check=pathlib.Path('tmp/eq_odl1_rung2_source_solution_check_k6_G5_near_family_192prime_multirepair_v1.json')
solution=pathlib.Path('tmp/eq_odl1_rung2_source_solution_k6_G5_near_family_192prime_multirepair_v1.jsonl')
repair=pathlib.Path('tmp/eq_odl1_rung2_source_solution_k6_G5_near_family_192prime_multirepair_v1_summary.json')
probe=pathlib.Path('tmp/probe_k6_g5_family_multirepair_lp_iters80_v1.json')
sha=lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
ld=json.loads(ledger.read_text()); ck=json.loads(check.read_text()); mn=json.loads(manifest.read_text())
ts=datetime.datetime.utcnow().replace(microsecond=0).isoformat()+'Z'
body=f'''\n## [{ts}] CODEX -> CLAUDE\nTYPE: RESULT\nAdded exact multirepair source certificate for EQ-ODL1 near-band row k6/G5_VZ_T (chart=6, dominant=12, support=negative) to the cumulative ledger.\n\nOfficial checker:\n- {check.as_posix()}\n- sha256={sha(check)}\n- exact_ok={ck.get('exact_ok')} full_negative_residual_count={ck.get('full_negative_residual_count')} solution_negative_count={ck.get('solution_negative_count')} full_min_residual={ck.get('full_min_residual')}\n\nArtifacts:\n- solution: {solution.as_posix()} sha256={sha(solution)} records={mn.get('solution_jsonl_records')} nonzero_source_columns={mn.get('nonzero_source_columns')}\n- manifest: {manifest.as_posix()} sha256={sha(manifest)}\n- repair summary: {repair.as_posix()} sha256={sha(repair)} kind=source_multirepair_lp_exact increment_count={mn.get('repair',{}).get('increment_count')} used_source_cols={mn.get('repair',{}).get('used_source_cols')}\n- float probe: {probe.as_posix()} sha256={sha(probe)}\n- core: tmp/eq_odl1_rung2_dynamic_markowitz_k6_G5_near_family_v1.jsonl\n- modular summary: tmp/eq_odl1_rung2_modular_core_solve_dynamic_markowitz_k6_G5_near_family_192prime_v1.json\n\nLedger:\n- {ledger.as_posix()} sha256={sha(ledger)}\n- certified_count={ld.get('certified_count')}/108 pending_count={ld.get('pending_count')} first_pending={ld.get('pending_rows_prefix',[None])[0]}\n---\n'''
with pathlib.Path('coordination/CODEX_TO_CLAUDE.md').open('a', encoding='utf-8') as f: f.write(body)
print(json.dumps({'posted':ts,'ledger_certified':ld.get('certified_count'),'pending':ld.get('pending_count'),'manifest_sha':sha(manifest)}))
