# CODEX BANK0 bench note, 2026-07-03

Scope: B1 final repair / BANK0 scalar theorem

Target under audit:

```text
Bank0: N^2 - 25 m >= 0
```

for connected-B, gamma-minimal maximum cuts in the all-bad-length-5 case.

## Exact component gate runs

Command:

```text
python -B _claude_bank0_component_gate.py --skip-census
```

Result:

```text
cuts=47, pure_l5_cuts=12
global_fails=0, local_fails=0, disj_fails=0
min_global_margin=21 on Grotzsch
VERDICT=PASS
```

Command:

```text
python -B _claude_bank0_component_gate.py --skip-named --min-n 8 --max-n 8
```

Result:

```text
cuts=280, pure_l5_cuts=268
global_fails=0, local_fails=0, disj_fails=0
min_global_margin=14
min_local_margin=0
VERDICT=PASS
```

Command:

```text
python -B _claude_bank0_component_gate.py --skip-named --min-n 9 --max-n 9
```

Result:

```text
cuts=1916, pure_l5_cuts=1818
global_fails=0, disj_fails=0
local_fails=8
min_global_margin=31
first_local_fail=('cen:H?AFBo]', '000111100', 2, 7)
VERDICT=FAIL because local_fails are included in this diagnostic script
```

Command:

```text
python -B _claude_bank0_component_gate.py --skip-named --min-n 10 --max-n 10
```

Result:

```text
cuts=16016, pure_l5_cuts=15503
global_fails=0, disj_fails=0
local_fails=119
min_global_margin=0 at cen:I?rFf_{N? with N=10,m=4
first_global_fail=None
VERDICT=FAIL because local_fails are included in this diagnostic script
```

Interpretation:

```text
Global Bank0 has 0 failures in these exact slices.
The naive local K-component inequality m_C <= |supp C|^2 / 25 is false.
The proof route must use ambient/global compensation, not per-component support summing.
```

## First local-bank witness

Command:

```text
python -B _claude_bank0_witness_dump.py
```

Witness:

```text
g6=H?AFBo], n=9, side=000111100
m=2, N^2-25m=31
component edges=((1,7),(2,7))
ells=[5,5]
m_C=2, |supp|=7, 25*m_C-|supp|^2=1
cyc[(1,7)] = [(1,6,8,3,7), (1,6,8,4,7)]
cyc[(2,7)] = [(2,6,8,3,7), (2,6,8,4,7)]
```

## Switch-cover replacement smoke

Command:

```text
python -B _claude_bank0_switchcover_lp.py
```

Result:

```text
[theta-witness] side=000111100 m=2 N^2=81 LP_OPT~50.0000 exact_cert=YES budget_ok=True
[C5[2]-tight] side=1111000000 m=4 N^2=100 LP_OPT~100.0000 exact_cert=YES budget_ok=True
[N10-worst] side=0000011110 m=2 N^2=100 LP_OPT~50.0000 exact_cert=YES budget_ok=True
```

Interpretation:

```text
The switch-cover mechanism handles the known local-bank failures and the C5[2] tight atom.
The next BANK0 proof target should be a formal exact switch-cover certificate or a
structural derivation of the same global cover, not the dead local component inequality.
```

## Row-monotone C5-hom probe

Script:

```text
python -B _codex_bank0_row_monotone_hom_probe.py
```

Definition checked:

```text
For every pure all-length-5 connected-B gamma-min cut:
  if any graph C5-hom lambda: V -> Z5 exists,
  then search for a hom such that every certified row P has labels
  lambda(P[j+1])-lambda(P[j]) constantly +1 or constantly -1 mod 5.
```

Named smoke:

```text
python -B _codex_bank0_row_monotone_hom_probe.py --skip-census
pure_l5_cuts=62
pure_hom_mono=50
pure_no_hom=12
counterexample=0
VERDICT=PASS
```

Census N=8..10:

```text
python -B _codex_bank0_row_monotone_hom_probe.py --skip-named --min-n 8 --max-n 10
pure_l5_cuts=17589
pure_hom_mono=15138
pure_no_hom=2451
counterexample=0
VERDICT=PASS
```

Census N=11:

```text
python -B _codex_bank0_row_monotone_hom_probe.py --skip-named --min-n 11 --max-n 11
pure_l5_cuts=167043
pure_hom_mono=130793
pure_no_hom=36250
counterexample=0
VERDICT=PASS
```

Interpretation:

```text
No N<=11 falsifier was found for:
  C5-hom exists but no row-monotone C5-hom exists.

The hom-positive pure-l5 branch supports the voltage/row-monotone lemma;
the no-hom cases remain the CROSS/OSC/corridor domain.
```

## Hom-branch bank-block trace emitter

Script:

```text
python -B _codex_bank0_hom_block_trace.py
```

For every pure all-length-5 connected-B gamma-min cut with a row-monotone C5 hom, the emitted trace checks:

```text
labels lambda : V -> Z5
class sizes n_i
edge-pair counts e_i between classes i and i+1
bad-edge count m
m <= e_i <= n_i*n_{i+1} for all i
N^2 - 25m >= 0
```

Named smoke:

```text
python -B _codex_bank0_hom_block_trace.py --skip-census --trace-limit 10 --output problems/tmp_bank0_hom_trace_named.json
hom_trace=50
pure_no_hom_or_no_mono_hom=12
first_hom_trace_fail=None
worst_template_margin=0 at C5[2]
worst_bank0_margin=0 at C5[2]
VERDICT=PASS
```

Census N=8..10:

```text
python -B _codex_bank0_hom_block_trace.py --skip-named --min-n 8 --max-n 10 --trace-limit 20 --output tmp/bank0_hom_trace_n8_10.json
hom_trace=15138
pure_no_hom_or_no_mono_hom=2451
first_hom_trace_fail=None
worst_template_margin=0
worst_bank0_margin=0 at C5[2]
VERDICT=PASS
```

Census N=11:

```text
python -B _codex_bank0_hom_block_trace.py --skip-named --min-n 11 --max-n 11 --trace-limit 20 --output tmp/bank0_hom_trace_n11.json
hom_trace=130793
pure_no_hom_or_no_mono_hom=36250
first_hom_trace_fail=None
worst_template_margin=0
worst_bank0_margin=21
VERDICT=PASS
```

Interpretation:

```text
The C5-hom positive branch now has machine-visible exact trace data for the AM-GM finish.
No emitted hom trace violates m <= e_i, e_i <= n_i*n_{i+1}, row-monotonicity, or Bank0.
No-hom cases are counted separately and remain the CROSS/OSC/corridor branch.
```

## Full JSONL hom-trace certificates and verifier

Emitter upgraded with:

```text
--jsonl-output <path>
```

Verifier:

```text
python -B _codex_bank0_hom_trace_verify.py <jsonl>
```

The verifier independently reconstructs each graph/cut and rechecks every `hom_trace` record:

```text
B connected
all bad edges have length 5
recorded labels are a C5 hom
all rows are label-monotone
class_sizes, edge_pair_counts, product_bounds, margins match recomputation
m <= e_i <= n_i*n_{i+1}
N^2 - 25m >= 0
```

Named JSONL smoke:

```text
python -B _codex_bank0_hom_block_trace.py --skip-census --trace-limit 5 --output tmp/bank0_hom_trace_named_summary_v3.json --jsonl-output tmp/bank0_hom_trace_named_v3.jsonl
python -B _codex_bank0_hom_trace_verify.py tmp/bank0_hom_trace_named_v3.jsonl
verified_hom_trace=50
routing_record=12
VERDICT=PASS
```

Census N=8..10 full JSONL:

```text
python -B _codex_bank0_hom_block_trace.py --skip-named --min-n 8 --max-n 10 --trace-limit 20 --output tmp/bank0_hom_trace_n8_10_summary_v2.json --jsonl-output tmp/bank0_hom_trace_n8_10_v2.jsonl
python -B _codex_bank0_hom_trace_verify.py tmp/bank0_hom_trace_n8_10_v2.jsonl
verified_hom_trace=15138
routing_record=2451
VERDICT=PASS
```

Census N=11 full JSONL:

```text
python -B _codex_bank0_hom_block_trace.py --skip-named --min-n 11 --max-n 11 --trace-limit 20 --output tmp/bank0_hom_trace_n11_summary_v2.json --jsonl-output tmp/bank0_hom_trace_n11_v2.jsonl
python -B _codex_bank0_hom_trace_verify.py tmp/bank0_hom_trace_n11_v2.jsonl
verified_hom_trace=130793
routing_record=36250
VERDICT=PASS
```

Artifacts:

```text
tmp/bank0_hom_trace_named_v3.jsonl
tmp/bank0_hom_trace_n8_10_v2.jsonl
tmp/bank0_hom_trace_n11_v2.jsonl
tmp/bank0_hom_trace_named_summary_v3.json
tmp/bank0_hom_trace_n8_10_summary_v2.json
tmp/bank0_hom_trace_n11_summary_v2.json
```

## B0-5 closure trace prototype (Codex)

Emitter: `problems/23/writeup/_codex_bank0_closure_trace_emit.py`.

Closure rules implemented for this gate:
- C1 row-interval closure.
- C2 oriented same-bad-edge / same-first-exit row-family closure.
- C3 blue-detour closure in the row-edge-deleted blue graph, with single-edge fallback for theta-style detours.
- C4 terminal-shadow completion, including nonterminal row intersections completed to both terminal shadows, then terminal-prefix closure.

Exact pressure: `Pi(U)=5*s(U)-N*|U|` with `s(v)=sum_f p_f(v)` as Fractions.

Results:
- N=8 census no-hom pure-l5: PASS, 30 records, 0 positive closed packets. Output `tmp/bank0_closure_trace_n8_v1.jsonl`.
- N=9 census no-hom pure-l5: initial C4 endpoint-only closure failed on singleton `{8}` in `cen:H?bB@qQ`, `Pi=1`; repaired C4 terminal-shadow completion. PASS after repair, 162 records, 0 positive closed packets. Output `tmp/bank0_closure_trace_n9_v2.jsonl`.
- N=10 census no-hom pure-l5: PASS, 2259 records, 0 positive closed packets. Output `tmp/bank0_closure_trace_n10_v1.jsonl`.

Status: B0-5 prototype is exact-clean through N=10. N=11 remains to scale or parallelize.

## B0-5 N=11 batched closure trace status (Codex)

Emitter updated:
- `--skip-records`, `--progress-every` for resumable shards.
- `--input-jsonl` to consume accepted `pure_no_hom_or_no_mono_hom` routing records directly from hom-trace JSONL and skip redundant C5-hom search.

Source: `tmp/bank0_hom_trace_n11_v2.jsonl`.
Total no-hom pure-l5 routing records: 36,250.

Checked shards:
- batch000 skip=0 limit=500: PASS, 500 records, 0 positive closed packets.
- batch001 skip=500 limit=500: PASS, 500 records, 0 positive closed packets.
- batch002 skip=1000 limit=500: PASS, 500 records, 0 positive closed packets.

Combined partial summary: `tmp/bank0_closure_trace_n11_batches_000_002_summary.json`.
Status: PASS_PARTIAL, 1,500 / 36,250 checked, 0 fails.

## B0-5 N=11 batched closure trace update 000-006 (Codex)

Additional checked shards:
- batch003 skip=1500 limit=500: PASS, 500 records, 0 positive closed packets.
- batch004 skip=2000 limit=500: PASS, 500 records, 0 positive closed packets.
- batch005 skip=2500 limit=500: PASS, 500 records, 0 positive closed packets.
- batch006 skip=3000 limit=500: PASS, 500 records, 0 positive closed packets.

Combined partial summary: `tmp/bank0_closure_trace_n11_batches_000_006_summary.json`.
Status: PASS_PARTIAL, 3,500 / 36,250 checked, 0 fails.

## B0-5 N=11 batched closure trace update 000-010 (Codex)

Additional checked shards:
- batch007 skip=3500 limit=500: PASS, 500 records, 0 positive closed packets.
- batch008 skip=4000 limit=500: PASS, 500 records, 0 positive closed packets.
- batch009 skip=4500 limit=500: PASS, 500 records, 0 positive closed packets.
- batch010 skip=5000 limit=500: PASS, 500 records, 0 positive closed packets.

Combined partial summary: `tmp/bank0_closure_trace_n11_batches_000_010_summary.json`.
Status: PASS_PARTIAL, 5,500 / 36,250 checked, 0 fails.

## B0-5 N=11 batched closure trace update 000-018 (Codex)

Added reproducible aggregator: `problems/23/writeup/_codex_bank0_closure_batch_summary.py`.

Additional checked shards:
- batch011 skip=5500 limit=500: PASS, 500 records, 0 positive closed packets.
- batch012 skip=6000 limit=500: PASS, 500 records, 0 positive closed packets.
- batch013 skip=6500 limit=500: PASS, 500 records, 0 positive closed packets.
- batch014 skip=7000 limit=500: PASS, 500 records, 0 positive closed packets.
- batch015 skip=7500 limit=500: PASS, 500 records, 0 positive closed packets.
- batch016 skip=8000 limit=500: PASS, 500 records, 0 positive closed packets.
- batch017 skip=8500 limit=500: PASS, 500 records, 0 positive closed packets.
- batch018 skip=9000 limit=500: PASS, 500 records, 0 positive closed packets.

Combined current summary: `tmp/bank0_closure_trace_n11_batches_all_current_v2_summary.json`.
Status: PASS_PARTIAL, 9,500 / 36,250 checked, 0 fails.
