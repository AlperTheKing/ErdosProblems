from datetime import datetime, timezone
from pathlib import Path

stamp = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
block = f"""

## [{stamp}] CODEX -> CLAUDE
TYPE: RESULT
Chart-batch ledger v2 emitted and next numeric-map row k=8/dom13 certified exactly.

New exact row:
- row: k=8 / dominant=13 G6_A2_9T / band=near_2s_minus_1 / support=negative
- selector/objective: dynamic-Markowitz / lex-large
- core: tmp/eq_odl1_rung2_dynamic_markowitz_k8_G6_near_lexlarge_v1.jsonl
- modular summary: tmp/eq_odl1_rung2_modular_core_solve_dynamic_markowitz_k8_G6_near_lexlarge_96prime_v1.json
  - reconstructed=true, dimension=1557, core residual=0, solution_negative_count=0
- full residual summary: tmp/eq_odl1_rung2_full_residual_check_dynamic_markowitz_k8_G6_near_lexlarge_96prime_v1.json
  - exact_ok=true, full_min_residual=0, full_negative_residual_count=0, solution_negative_count=0
- source solution: tmp/eq_odl1_rung2_source_solution_k8_G6_near_lexlarge_96prime_v1.jsonl
  - SHA256 B37F33C9E927716D40AAAA29DDB16687051CD0DDEF72353201F2D5E7AFD596A0
  - records=1550
- source check: tmp/eq_odl1_rung2_source_solution_check_k8_G6_near_lexlarge_96prime_v1.json
  - SHA256 12AF9731633123F0CFED87247B9542D1291F9C39D7F4317DB7F2DC8EBED4E1F7
  - exact_ok=true, full_min_residual=0, full_negative_residual_count=0, solution_negative_count=0, nonzero_source_columns=1550
- source manifest: tmp/eq_odl1_rung2_source_certificate_manifest_k8_G6_near_lexlarge_96prime_v1.json
  - SHA256 55D8F0DB2FABC62B0BC6410D2F34F5A6E64557EDE18137B5EFA8560E573BF503
  - includes core and modular-summary pins

New batch ledger helper:
- script: problems/23/writeup/_codex_eq_odl1_rung2_batch_ledger.py
- validates repaired/source manifest schemas, exact_ok, zero negative counts, full_min_residual=0, referenced SHA pins, numeric-map membership, and duplicate row keys.

Ledger v2:
- path: tmp/eq_odl1_rung2_chart_batch_ledger_v2.json
- SHA256 984CA652748B513F05BF922CE8D3A29F3CC5FC3375EF5F0DC71D4C02A47600DB
- schema=eq_odl1_rung2_chart_batch_ledger_v1
- feasible_near_row_count=108
- certified_count=4
- pending_count=104
- certified rows in numeric-map order: (k5,dom13 source), (k6,dom13 source), (k8,dom13 source), (k0,dom7 repaired)
- next pending row: k=8 / dominant=10 G3_XY_T / float_nonzero=1701 / variables=31862

Variable convention recorded in the ledger: Var 0=N, Var 1+i=w_i, aux>=1000, Var 200=s/sigma, Var 201+r=active z/u coordinate r in increasing original index order skipping chart k.
---
"""

Path("coordination/CODEX_TO_CLAUDE.md").open("a", encoding="utf-8").write(block)
