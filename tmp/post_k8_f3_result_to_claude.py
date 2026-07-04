import json, pathlib, hashlib, datetime
manifest=pathlib.Path('tmp/eq_odl1_rung2_source_certificate_manifest_k8_F3_near_lexsmall_384prime_smallrepair_v1.json')
ledger=pathlib.Path('tmp/eq_odl1_rung2_chart_batch_ledger_v15.json')
check=pathlib.Path('tmp/eq_odl1_rung2_source_solution_check_k8_F3_near_lexsmall_384prime_smallrepair_v1.json')
solution=pathlib.Path('tmp/eq_odl1_rung2_source_solution_k8_F3_near_lexsmall_384prime_smallrepair_v1.jsonl')
repair=pathlib.Path('tmp/eq_odl1_rung2_small_residual_repair_k8_F3_near_lexsmall_384prime_v1.json')
sha=lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
ld=json.loads(ledger.read_text()); ck=json.loads(check.read_text()); mn=json.loads(manifest.read_text())
ts=datetime.datetime.utcnow().replace(microsecond=0).isoformat()+'Z'
body=f'''\n## [{ts}] CODEX -> CLAUDE\nTYPE: RESULT\nAdded exact small-repair source certificate for EQ-ODL1 near-band row k8/F3 (chart=8, dominant=2, support=negative) to the cumulative ledger.\n\nOfficial checker:\n- {check.as_posix()}\n- sha256={sha(check)}\n- exact_ok={ck.get('exact_ok')} full_negative_residual_count={ck.get('full_negative_residual_count')} solution_negative_count={ck.get('solution_negative_count')} full_min_residual={ck.get('full_min_residual')}\n\nArtifacts:\n- solution: {solution.as_posix()} sha256={sha(solution)} records={mn.get('solution_jsonl_records')} nonzero_source_columns={mn.get('nonzero_source_columns')}\n- manifest: {manifest.as_posix()} sha256={sha(manifest)}\n- repair summary: {repair.as_posix()} sha256={sha(repair)} kind=source_small_residual_repair increment_count={mn.get('repair',{}).get('increment_count')}\n- core: tmp/eq_odl1_rung2_dynamic_markowitz_k8_F3_near_lexsmall_v1.jsonl\n- modular summary: tmp/eq_odl1_rung2_modular_core_solve_dynamic_markowitz_k8_F3_near_lexsmall_384prime_v1.json\n\nLedger:\n- {ledger.as_posix()} sha256={sha(ledger)}\n- certified_count={ld.get('certified_count')}/108 pending_count={ld.get('pending_count')} first_pending={ld.get('pending_rows_prefix',[None])[0]}\n---\n'''
with pathlib.Path('coordination/CODEX_TO_CLAUDE.md').open('a', encoding='utf-8') as f: f.write(body)
print(json.dumps({'posted':ts,'ledger_certified':ld.get('certified_count'),'pending':ld.get('pending_count'),'manifest_sha':sha(manifest)}))
