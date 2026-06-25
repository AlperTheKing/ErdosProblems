# Codex Status for Step 2

Last updated: 2026-06-23T05:35+03:00.

Current Step-1 audit note: K2/T2 q10 idx95 is closed by V540.  The complete
clean merged result has 599478/599478 filtered rows, all INFEASIBLE, with
`filter_missing=0`, `filter_extra=0`, `result_missing=0`, `result_extra=0`,
and `bad_status=0`.  idx96 is active under PID 10566532 using the C++ fresh-
process state-count runner with `64 x 1 = 64` worker threads.  Clean partials
are merged in
`search23/k2_idx96_q10ED4_a7b9_state_results_sidesum_merged_partial52131.tsv`,
with 52131 INFEASIBLE rows and audit `result_extra=0`, `bad_status=0`.
The active C++ remainder file currently shows 94641/958184 rows by live poll,
all INFEASIBLE; a follow-up allow-incomplete audit saw 93740 rows with
`result_missing=864444`, `result_extra=0`, and `bad_status=0`.  No idx97 batch
is active.  Earlier
duplicate/stale idx96 outputs were renamed or stopped and are not certificate
evidence until explicitly merged and audited.  Do not launch idx97 while idx96
is active.
Latest live poll at 2026-06-23T05:35+03:00 shows the active idx96 remainder
at 94641/958184 rows, all INFEASIBLE; the 05:30 audit saw 93740 rows.  Count
differences are expected because the active writer keeps moving while audits
read the file.  Current Codex compute cap is 64 worker threads while this PID
is active.
Codex added `search23/estimate_k2_es1s2_raw.py` as a scale diagnostic for
residual `E+S1+S2` instances idx270, idx344, and idx360.  A 100-skeleton
idx270 smoke estimate reports `raw_skeletons=6059` and `tasks=2528739`, so
direct raw materialization is likely too costly without a quotient/canonical
reduction.  This diagnostic is not a closure certificate.
Codex also built `tools/nauty2_8_9/labelg.exe` and added
`search23/smoke_k2_es1s2_labelg_quotient.py`.  The idx270 100-skeleton smoke
reports `raw_graphs=6059`, `canonical_orbits=1651`, `bad_partition_edges=0`,
and sample TSV `search23/k2_idx270_es1s2_labelg_quotient_sample100.tsv` with
`1651` unique masks.  Independent audit
`search23/audit_k2_es1s2_labelg_quotient_sample.py` returns PASS on that
sample.  `search23/make_k2_es1s2_labelg_quotient_tasks.py` materializes a
sample task grid with `695788` rows, and
`search23/audit_k2_es1s2_labelg_quotient_tasks.py` audits it PASS; no closure
certificate uses this quotient path yet.
The smoke tool now has a `--max-raw-graphs` guard.  A guarded idx344 sample
using 10 `(6,7)` base skeletons has `2457` raw graphs, `164` canonical masks,
and a `59287`-row task grid audited PASS.  The sample slice manifest has `3`
slices and audits PASS.
The chunked generator `search23/make_k2_es1s2_labelg_quotient_skeletons.py`
reproduces the same idx344 sample masks and raw counts with `--raw-chunk-size
300`; this is preparation for larger `E+S1+S2` quotient generation.
The task materializer has `--count-only`; it reports `7046648` task rows for
the idx270 1000-base-skeleton quotient sample without materializing that grid.
Codex also prepared `search23/run_state_count_6195_tasks_chunked_inproc.py`,
a warm-runner wrapper.  One 6000-row chunk was clean and merged, but the runner
spawned beyond the allowed process envelope via worker recycling, so it was
stopped.  The helper is now patched to set `CODEX_POOL_MAXTASKS` above the
chunk size, but that fix has not been run-tested.
q6-q9 are closed; q10 has only idx96-97
left; after V537-V539, q11-q14 have 263 profile-side instances not yet closed
by recorded certificates.  Accounting audit
`python search23/audit_k2_t2_frontier_accounting.py` returns PASS for these
counts.
The single raw resume4 EXCEPTION key has standalone retry evidence in
`search23/k2_idx95_q10ED4_a6b10_state_results_sidesum_resume4_exception_fix.tsv`
and is included in the clean complete merge as INFEASIBLE.

Prepared next Step-1 handoff: all residual no-empty S1+S2+D profiles with
`c1=2` have forced `R[S1,S2]=K_{2,c2}` compact-mask skeletons.  Audit
`search23/k2_forced_s1s2d_task_prep.tsv` lists 22 profile-side instances and
1659 total state-task rows.  Independent audit
`python search23/audit_k2_forced_s1s2d_task_prep.py` returns PASS.  No solver
has been launched for these files.

Broader Step-1 handoff: compact C++ skeleton generator
`search23/k2_noempty_s1s2d_skeletons.cpp` prepares all residual no-empty
S1+S2+D instances with `c1*c2<=16`: 45 profile-side instances, 360 skeletons,
44292 state-task rows.  Independent audit
`python search23/audit_k2_noempty_s1s2d_task_prep.py` returns PASS.  No solver
has been launched for these files.

Expanded no-empty S1+S2+D handoff: `c1*c2<=20` now has
`search23/k2_noempty_s1s2d_task_prep_bits20.tsv` with 55 profile-side
instances, 1280 skeletons, and 222749 state-task rows.  Independent audit
with `--audit search23/k2_noempty_s1s2d_task_prep_bits20.tsv` returns PASS.
No solver has been launched for these files.

Next no-empty S1+S2+D slice: `c1*c2=21` (`idx245`, `idx309`) has
`search23/k2_noempty_s1s2d_task_prep_bits21_idx245_309.tsv` with 2
profile-side instances, 56 skeletons, and 7380 state-task rows.  Independent
audit returns PASS.  No solver has been launched for these files.

Pure S1+S2 prep: added `search23/make_k2_pure_s1s2_tasks.py`, which uses
nauty `genbg -l -q -d2:2` for canonical bipartite skeletons, plus
`search23/audit_k2_pure_s1s2_task_prep.py`.  Prepared idx180 q12 pure
S1+S2 `(c1,c2)=(6,6)`, `(A,B)=(6,8)`: audit
`search23/k2_pure_s1s2_task_prep_idx180.tsv` returns PASS with 72014
skeletons and 11544817 state-task rows.  No solver has been launched for
idx180.
Added generic task-file slice helpers
`search23/make_state_task_slice_manifest.py`,
`search23/audit_state_task_slice_manifest.py`, and
`search23/materialize_state_task_slice.py`.  The idx180 slice manifest
`search23/k2_idx180_q12S1S2_task_slice_manifest.tsv` returns PASS with 116
slices covering 11544817 tasks; slice 115 materialized 44817/44817 rows in a
smoke test, and the temporary slice file was removed.
Patched the pure S1+S2 materializer with `--reuse-existing-skeletons` and
prepared idx181 q12 pure S1+S2 `(c1,c2)=(6,6)`, `(A,B)=(7,7)` from the same
6x6 skeleton file.  Audit `search23/k2_pure_s1s2_task_prep_idx181.tsv`
returns PASS with 72014 skeletons and 11846739 state-task rows.  Slice
manifest `search23/k2_idx181_q12S1S2_task_slice_manifest.tsv` returns PASS
with 119 slices.  No solver has been launched for idx181.
Added `search23/audit_state_task_slice_result_family.py` for future slice
result certificate audits.  Synthetic tests cover PASS and require-complete
FAIL behavior.  Current idx180/idx181 manifests report zero completed result
files, all expected result files missing, and zero bad audits in non-complete
mode.
Added pure S1+S2 skeleton-slice manifest tooling:
`search23/make_k2_pure_s1s2_slice_manifest.py` and
`search23/audit_k2_pure_s1s2_slice_manifest.py`.  Remaining pure S1+S2 scale
counts are `(6,7)=706436`, `(6,8)=5917256`, `(7,7)=14280402` skeletons.
Prepared idx254 q13 pure S1+S2 `(c1,c2)=(6,7)`, `(A,B)=(6,7)`:
`search23/k2_pure_s1s2_slice_manifest_idx254.tsv` returns PASS with 15 slices
and 293777388 state-task rows.  No solver has been launched for idx254.

E+D preparation note: `search23/make_k2_ed_tasks.py` exists, but broad and
q11-only residual E+D task-prep runs exceeded 60 seconds and were stopped.
No solver was launched for those files; E+D needs a smaller split or generator
optimization.

E+D individual prep: `idx134` and `idx135`, both `(2,0,0,9)`, are prepared
with `search23/k2_ed_task_prep_idx134.tsv` and
`search23/k2_ed_task_prep_idx135.tsv`; together they have 220 skeletons and
36264 state-task rows.  `search23/audit_k2_ed_task_prep.py` returns PASS on
both.  No solver has been launched for these files.

E+D individual prep: `idx142` and `idx143`, both `(3,0,0,8)`, are prepared
with `search23/k2_ed_task_prep_idx142.tsv` and
`search23/k2_ed_task_prep_idx143.tsv`; together they have 2642 skeleton rows
and 668462 state-task rows.  `search23/audit_k2_ed_task_prep.py` returns PASS
on both.  No solver has been launched for these files.

E+D individual prep: `idx146` and `idx147`, both `(4,0,0,7)`, are prepared
with `search23/k2_ed_task_prep_idx146.tsv` and
`search23/k2_ed_task_prep_idx147.tsv`; together they have 21656 skeleton rows
and 7128779 state-task rows.  `search23/audit_k2_ed_task_prep.py` returns PASS
on both.  No solver has been launched for these files.

E+D generator note: `search23/k2_ed_skeletons_fast.cpp` was added.  Its orbit
sets match the old generator on `(3,8)` and `(4,7)`.  It generates the
`(5,6)` E+D skeletons in 0.831 seconds; the old generator exceeded 60 seconds.

E+D individual prep: `idx148` and `idx149`, both `(5,0,0,6)`, are prepared
with `search23/k2_ed_task_prep_idx148.tsv` and
`search23/k2_ed_task_prep_idx149.tsv`; together they have 71070 skeleton rows
and 28091014 state-task rows.  `search23/audit_k2_ed_task_prep.py` returns
PASS on both.  No solver has been launched for these files.

All q11 residual E+D side choices are now prepared and audited as task grids:
idx134, idx135, idx142, idx143, idx146, idx147, idx148, and idx149.

q12 residual E+D prep has started: idx204, idx205, idx218, idx219, idx226,
and idx227 are prepared and audited as task grids.  Combined package has 70814
skeleton rows and 20617362 state-task rows.  No solver has been launched for
these files.  The next q12 E+D profile `(5,7)` has 224346 skeletons by the
fast generator and should be split or compressed before full task prep.

Large-grid support: `search23/k2_skeletons_make_state_tasks_slice.cpp` was
added and audited on idx204; two slices reproduce the full task-maker output,
`17138/17138` tasks.

Large-grid sizing: `search23/k2_skeletons_count_state_tasks.cpp` was added and
audited on idx204.  Remaining q12 E+D large grids are counted without full TSV
materialization: idx230=81316201 tasks, idx231=81839608, idx232=195597390,
idx233=196935286.  These require skeleton slices or a compressed runner.

q12 large E+D slice manifest exists at
`search23/k2_ed_slice_manifest_q12_large_idx230_233.tsv`: 30 slice rows total,
with 5 slices for idx230, 5 for idx231, 10 for idx232, and 10 for idx233.
Manifest task totals match the no-output counter values.

Reusable q12 large E+D helpers:
`search23/audit_k2_ed_slice_manifest.py` audits the slice manifest and returns
PASS on `search23/k2_ed_slice_manifest_q12_large_idx230_233.tsv`.
`search23/materialize_k2_ed_slice.py` materializes one slice; idx204 slice 0
test produced `3267/3267` expected tasks.
`search23/audit_k2_ed_slice_result_closure.py` audits one slice result file
against manifest+skeleton expected keys.  Synthetic complete idx204 slice 0
test reports `missing=0`, `extra=0`, `bad_status=0`; allow-incomplete test
reports `missing=1`.
`search23/run_k2_ed_slice.py` is a dry-run capable wrapper that materializes,
runs, and audits one manifest slice.  Dry-run on idx230 slice 0 produces a
60 x 1 worker command with `expected_tasks=15688432` and standard K2 child
arguments.
`search23/audit_k2_ed_slice_family.py` audits all result files for a manifest
family.  Dry-run on the q12 large E+D manifest reports 4 instances, 30 slices,
and 30 missing result files.  Synthetic idx204 test audits one completed slice
with zero failures.
`search23/make_k2_ed_slice_manifest.py` now has `--reuse-existing-skeletons`.
Using the completed `(5,8)` skeleton file, idx293 now has an audited slice
manifest: 23 slices, 1133993 skeletons, 344494239 tasks.

E+D generator update: `search23/k2_ed_skeletons_geng.cpp` / `.exe` was added
for `c0<=8`.  It uses `tools/nauty2_8_9/geng.exe -t` for the empty-label
subgraph and was orbit-audited against the existing fast generator on the
E-triangle-free subset: `(3,8)` gives `1317/1317` orbits and `(4,7)` gives
`10763/10763` orbits.
`tools/nauty2_8_9/genbg.exe` was also built by direct `gcc` commands after
the makefile path failed without `sh.exe`; smoke test `genbg -u -d2:0 7 6`
reports `945762` incidence graphs in 0.29 seconds.
`search23/k2_ed_genbg_ee_stats.cpp` / `.exe` now audits incidence-first raw
E-E extension scale: `(7,6)=1774891`, `(8,6)=228320779`, `(7,7)=160727623`,
`(6,8)=45373261`, `(5,9)=4779693`.
`search23/k2_ed_genbg_raw_skeletons_slice.cpp` / `.exe` materializes
overcomplete raw E+D skeleton slices; smoke test `(7,6)` slice 0 writes 1000
skeletons and the existing task counter reads 372869 tasks.
`search23/audit_state_task_result_closure.py` and
`search23/run_k2_ed_raw_slice.py` are added; the synthetic audit closes 10/10
keys and idx296 dry-run emits commands without launching a solver.
Raw-overcomplete manifest tooling is also added:
`search23/make_k2_ed_raw_slice_manifest.py`,
`search23/audit_k2_ed_raw_slice_manifest.py`, and
`search23/k2_ed_raw_slice_manifest_remaining.tsv`; audit PASS covers 6
remaining E+D instances, 8880 slices, and 443871224 raw intervals.
`search23/run_k2_ed_raw_manifest_slice.py` dry-runs idx296 slice 0 into a
60 x 1 worker raw-slice command without launching a solver.
`search23/audit_k2_ed_raw_slice_family.py` audits result coverage for the raw
manifest; current dry audit reports 8880 missing result files, 0 bad audits,
and PASS without `--require-complete`.
`search23/report_state_batch_progress.py` reports expected/done/missing,
completion percent, and status counts for long state-count batches.
`search23/k2_idx96_idx97_launch_commands.txt` contains older launch notes; the
current active idx96 command is the C++ fresh-process `64 x 1` runner under PID
10566532.

E+D residual accounting: 29 total profile-side instances; 23 have prepared
task grids or audited slice manifests.  Remaining E+D instances are idx295
`(6,7)`, idx296 `(7,6)`, idx379 `(5,9)`, idx383 `(6,8)`, idx385 `(7,7)`,
and idx386 `(8,6)`.  The geng-backed generator is correct on audited small
cases but timed out at 30 seconds on `(7,6)`, so the current next candidate is
a `genbg` incidence-first raw slice path.

## H1: `a(30) <= 36`

Status: IN PROGRESS pending global Step-1 audit.  The active `6195, e_R=16`
frontier is closed, but Codex has not yet re-audited every H1 dependency.

Do not mark H1 proved from this file alone.  The next Codex action is to audit
the Step-1 proof state for any remaining open families or missing certificate
handoff items.

Current audit blocker: the BCL density theorem itself still has to be cited and
accepted, but its "sufficiently large n" hypothesis is no longer a finite-n
blocker for Step 1.  Uniform blow-ups transfer BCL's density ranges back to
`n=30`, closing `e<=111` and `e>=144`.  The direct rooted
`109<=e<=139` campaign was audited and is not a certificate: it has
`149/149` `INCONCLUSIVE` rows.  H1 still needs a finite closure of the full
remaining window `112<=e<=143`.

Audit note 2026-06-20T03:25+03:00: the old q13/r0=8/t=2 `a6b7` remainder
table is not a valid `n=30` branch.  Its rooted partition has
`2 + k + na + nb + q = 2 + 3 + 6 + 7 + 13 = 31`.  The previous `218`/`214`
row estimates for that `a6b7` universe are superseded; Codex must audit valid
`q=13,k=3` branches with `na+nb=12` instead.  Separately,
`bridge/NEEDED_FROM_STEP1.md` flags a search-space completeness issue: BCL
density reductions are asymptotic and cannot by themselves justify the
finite `109 <= e <= 139` edge window at `n=30`.

Valid q13 follow-up: the visible `q=13,k=3,t=3,r8` profile artifacts with
`na+nb=12` are closed at the profile level:
`q13_t3_r8_a5b7_profile_cpsat_0_256.tsv` has `257/257` `INFEASIBLE`;
`q13_t3_r8_a6b6_profile_cpsat_0_255.tsv` has `249/256` `INFEASIBLE`, and
`q13_t3_r8_a6b6_profile_hard_300.tsv` closes the remaining `7/7`;
`q13_t3_r8_a7b5_profile_cpsat_0_255.tsv` has `256/256` `INFEASIBLE`.
The visible `q=13,k=3,t=3,r9,na=6,nb=6` branch is also closed:
`q13_t3_r9_profile_cpsat_0_93.tsv` has `93/94` `INFEASIBLE`, and the one
hard profile `74088` is closed by `q13_t3_r9_profile_74088_rerun_sym.txt`.

Finite density update: the BCL density ranges transfer to `n=30` by uniform
blow-up.  If `m<=111`, then `m/450<0.2486`; if `m>=144`, then
`m/450>0.3197`.  Since `beta(G[t])=t^2 beta(G)`, either case contradicts the
BCL bound `beta(G[t])<=(30t)^2/25` for large enough `t`.  Thus only
`112<=e<=143` is outside the density transfer.  The earlier finite deletion and
AES audits remain valid independent checks for subranges, but are superseded by
this broader transfer.  The rooted campaign
`campaign_rooted_r4_9_e109_139_w100_c20k_20260618_233808` does not close this
gap: `summary.tsv` reports `INCONCLUSIVE 149`.

Valid q13 T2 frontier update: the old `q13/r0=8/t=2/a6b7` artifacts are
invalid because they describe `31` vertices.  For valid
`q=13,k=3,t=2,r0=8,na+nb=12`, the cap-143 scalar prefilters currently have
`576607`, `556394`, and `493254` surviving rows for `(na,nb)=(5,7),(6,6),(7,5)`.
No trusted closure for this valid T2 frontier is visible yet.  Codex added a
summary inventory at `search23/q13_t2_r8_cap143_profile_summary.tsv` and
`search23/q13_t2_r8_cap143_bucket_summary.tsv`.  A tiny sample subcase is now
closed: valid `a6b6` profile `idx=66649`, count vector
`4,0,0,3,3,0,0,3`, at `eR=14`; the row split has `23/24` `INFEASIBLE`, and
the remaining `p=23,M=58..70` row is `INFEASIBLE` in
`search23/q13_t2_valid_top_a6b6_66649_eR14_p23_strong.tsv`.

Current verified Step-1 facts for this frontier:

- `6195, e_R=12`: closed by state-count/C6 projection certificate.
- `6195, e_R=13`: high-p rows closed by projected typewise certificate.
- `6195, e_R=14`: 135 tasks closed, all `INFEASIBLE`.
- `6195, e_R=15`: 23446 tasks closed, all `INFEASIBLE`.
- `6195, e_R=16`: full clean union closed, `59823/59823` tasks
  `INFEASIBLE`.
- Density transfer: `e<=111` and `e>=144` closed by BCL plus uniform blow-up.
- Remaining density gap after transfer: `112<=e<=143`.
- Rooted `109<=e<=139` campaign audit: `149/149` `INCONCLUSIVE`; not a
  certificate.
- Cap-143 low-codegree delta audit: the conservative cap143-minus-cap139
  shape delta has 61 rows, but generic scalar filtering leaves only six new
  scalar-surviving shapes, all in `r0=8,k=t=1,q=8` with
  `(a,b)=(7,12)..(12,7)`.  Artifact:
  `search23/lowcodegree_scalar_r8_t1_q8_cap143_survivor_rows.tsv`.
- The R-skeleton universe for that new `k=1,q=8` delta has only 60 canonical
  orbits: `c0=0` gives 1, `c0=1` gives 7, and `c0=2` gives 52.  Artifact:
  `search23/k1_q8_skeleton_manifest.tsv`.
- Codex closed the full `k=1,q=8,c0=0,c1=8,(a,b)=(7,12)` state-count group:
  `420/420 INFEASIBLE` across
  `search23/k1_q8_a7b12_c0_first40_w16.tsv` and
  `search23/k1_q8_a7b12_c0_remaining_w16.tsv`.  This is a subfrontier
  closure only; the remaining `k=1,q=8` side choices and `c0=1,2` skeleton
  families remain open.
- K2 reroot compression audit: q14 cannot yet be excluded because the old
  q14/t2 closure contains terminal-touch/terminal-degree dependencies that are
  no longer accepted.  Codex generated the safe q6..q14 four-label manifest:
  `search23/k2_four_label_profile_instances.tsv` with `387` instances.
- K2 P-free master result: `search23/k2_pfree_master_results.tsv` has
  `387/387 OPTIMAL`.  The paired-cut/aggregate layer is validated as a
  necessary filter, but it closes no K2 profile; next layer must be exact
  A/B state-count quotient or weighted quotient-cut separation.
- K2 exact state-count first closure: the `q=6`, support `{D}` family is
  closed by fixed-empty-R skeleton quotient.  Artifacts
  `search23/k2_idx{0..4}_q6D_*_state_results.tsv` contain
  `5200/5200 INFEASIBLE` and no accepted survivor.
- K2 exact state-count second closure: the `q=7`, support `{D}` family is
  also closed by the same quotient.  Artifacts
  `search23/k2_idx{5..8}_q7D_*_state_results.tsv` contain
  `3392/3392 INFEASIBLE` and no accepted survivor.
- Valid `q=13,k=3,t=2,na+nb=12` frontier remains open pending a structural or
  quotient certificate.
- Sample valid T2 subcase closed: `a6b6 idx=66649 eR=14`; this is diagnostic
  only and not a global T2 closure.
- New cap-143 delta interface smoke: `state_count_6195_cpsat.py --k 1`
  closes `cnt=0,8`, `(a,b)=(7,12)`, `p=19`, `M=95`, `mask=0` as
  `INFEASIBLE`; the full `k=1,q=8` frontier is still open.

Latest closed computation:

- Target: `6195, e_R=16`, total `2601 * 23 = 59823` `(mask,p,M)` tasks.
- Clean union artifact:
  `search23/state_count_6195_er16_clean_infeasible_union.tsv`.
- Final clean union verifier output:
  `expected=59823 rows_read=63867 unique_infeasible=59823 missing=0 noninf_keys=0 duplicate_inf_rows=4044 malformed=0`.
- Latest completed chunks include
  `search23/state_count_6195_er16_chunkA_defect24.tsv`,
  `search23/state_count_6195_er16_chunkB_defect24.tsv`,
  `search23/state_count_6195_er16_chunkC_defect24.tsv`, and
  `search23/state_count_6195_er16_chunkD2_defect24.tsv`,
  `search23/state_count_6195_er16_chunkE2_defect24.tsv`,
  `search23/state_count_6195_er16_chunkH_defect24.tsv`,
  `search23/state_count_6195_er16_chunkI_defect24.tsv`,
  `search23/state_count_6195_er16_chunkJ_defect24.tsv`,
  `search23/state_count_6195_er16_chunkK_defect24.tsv`,
  `search23/state_count_6195_er16_chunkL_defect24.tsv`,
  `search23/state_count_6195_er16_chunkM_defect24.tsv`, and
  `search23/state_count_6195_er16_chunkN_defect24.tsv`,
  `search23/state_count_6195_er16_chunkO_defect24.tsv`, and
  `search23/state_count_6195_er16_chunkP_defect24.tsv`; `chunkN` and
  `chunkO` have `2000` `INFEASIBLE` rows each, and `chunkP` has `2104`.
- Recent chunks `chunkN`, `chunkO`, and `chunkP` used `25 jobs * 2 solver
  workers`.
- Codex added `search23/verify_state_count_union.cpp`; use the clean union
  artifact above for final `e_R=16` status.
- No `FEASIBLE` result has been accepted. `NO_STATUS` rows are not counted as
  closed and are rerun.
- Abandoned file `search23/state_count_6195_er16_chunkD_defect24.tsv` is not
  part of the trusted union because a duplicate launch polluted it with
  `NO_STATUS`/blank status rows.
- Stopped file `search23/state_count_6195_er16_chunkF_defect24.tsv` is not
  part of the trusted union because it was launched with `20 jobs * 3 solver
  workers`, outside the conservative Step-1 cap policy.
- q13/r0=8/t=2 terminal-touch/`terminal_closure` equalities are not accepted
  as proof rules.
- All `search23/q13_t2_r8_a6b7_*` runs are now diagnostic only.  They use
  `na=6, nb=7`, hence describe `31` vertices under the q13 rooted partition.
  Codex patched the q13 verifier and runner to reject any
  `2 + k + na + nb + q != n` invocation.
- The visible valid `q=13,k=3,t=3,r8` artifacts are closed at the profile
  level, including the seven hard `a6b6` reruns.  H1 still needs a global
  inventory proving that no other valid q13 branch remains.
- The visible valid `q=13,k=3,t=3,r9` artifact is closed at the profile level,
  including the single hard rerun for profile `74088`.

## Step-2 Request Answers

- Claim boundary: Codex is currently working only on H1, namely the finite
  `a(30) <= 36` certificate.  H1 by itself should not be advertised as a full
  solution of Erdős Problem #23 unless the separate Step-2 reduction from a
  general counterexample to the 30-vertex H1 obstruction is independently
  proved and audited.
- Exact extremal census at beta `36`: not produced yet. Current pipeline is
  focused on excluding beta `>=37`, not enumerating all beta `36` extremals.
- `a(29)` / no 29-vertex beta-threshold statement: not currently proved by
  this Step-1 run. No dependency should assume it.
- Audit checklist in `NEEDED_FROM_STEP1.md`: not yet satisfied. The final H1
  handoff must include search-space completeness, triangle-free enforcement,
  beta/maxcut encoding match, rooting/branching soundness, and reproducible
  zero-UNKNOWN certificate totals.

## Interface Notes

The state-count outputs are useful as finite certificates only after:

1. status counts sum to the declared task universe;
2. every status is `INFEASIBLE`;
3. duplicate partial rows are unioned by `(mask,p,M)`;
4. `NO_STATUS`, `UNKNOWN`, `FEASIBLE`, and missing rows are rerun or separately
   explained;
5. the certificate constraints are stated in the write-up and checked by an
   independent verifier where practical.

## K2 Safe Manifest Updates

- `K=2,T=2,q=6`, support `{D}`: closed by state-count quotient,
  `5200/5200 INFEASIBLE`; artifacts
  `search23/k2_idx0_q6D_a6b14_state_results.tsv` through
  `search23/k2_idx4_q6D_a10b10_state_results.tsv`.
- `K=2,T=2,q=7`, support `{D}`: closed by state-count quotient,
  `3392/3392 INFEASIBLE`; artifacts
  `search23/k2_idx5_q7D_a6b13_state_results.tsv` through
  `search23/k2_idx8_q7D_a9b10_state_results.tsv`.
- `K=2,T=2,q=7`, support `{E,D}`: closed by state-count quotient,
  `19520/19520 INFEASIBLE`; artifacts
  `search23/k2_idx9_q7ED_a6b13_state_results.tsv` through
  `search23/k2_idx12_q7ED_a9b10_state_results.tsv`.
- The `{E,D}` runs used `--disable-anti-tightness`; H14/anti-tightness remains
  disabled until the full cap-143 `q=14,T=2` dependency is independently
  audited.
- `K=2,T=2,q=8`, support `{D}`, side `(a,b)=(6,12)`: closed by state-count
  quotient after hard-row rerun, union `592/592 INFEASIBLE`.
- `K=2,T=2,q=8`, support `{D}`, side `(a,b)=(7,11)`: closed by state-count
  quotient.  The trusted union has `656/656 INFEASIBLE`, with no missing
  key.  Superseded early files contain `52` non-INFEASIBLE rows, all closed by
  later hard/tail/remaining artifacts.
- Added safe all-D low-`p` parity lemma:
  `problems/23/k2_allD_minimal_p_parity_2026-06-20.md`.
  It closes the `p=22` and `p=23` rows for q8 all-D `(a,b)=(7,11)` without H14
  or terminal equalities.  Machine artifacts:
  `search23/k2_idx14_q8D_a7b11_p22_parity_results.tsv`,
  `search23/k2_idx14_q8D_a7b11_p22_tail_results.tsv`, and
  `search23/k2_idx14_q8D_a7b11_p23_parity_results.tsv`.
- Closed the full `p=24` band for q8 all-D `(a,b)=(7,11)`:
  `search23/k2_idx14_q8D_a7b11_p24_results.tsv` plus hard-tail artifact
  `search23/k2_idx14_q8D_a7b11_p24_hard_results.tsv`, union
  `32/32 INFEASIBLE`.
- Closed the full `p=25` band for q8 all-D `(a,b)=(7,11)`:
  `search23/k2_idx14_q8D_a7b11_p25_results.tsv` plus hard-tail artifact
  `search23/k2_idx14_q8D_a7b11_p25_hard_results.tsv`, union
  `32/32 INFEASIBLE`.
- Closed the full `p=26` band for q8 all-D `(a,b)=(7,11)`:
  `search23/k2_idx14_q8D_a7b11_p26_results.tsv` plus hard-tail artifact
  `search23/k2_idx14_q8D_a7b11_p26_hard_results.tsv`, union
  `32/32 INFEASIBLE`.
- Closed the full `p=27` band for q8 all-D `(a,b)=(7,11)`:
  `search23/k2_idx14_q8D_a7b11_p27_results.tsv` plus hard-tail artifact
  `search23/k2_idx14_q8D_a7b11_p27_hard_results.tsv`, union
  `31/31 INFEASIBLE`.
- Closed the full `p=28` band for q8 all-D `(a,b)=(7,11)`:
  `search23/k2_idx14_q8D_a7b11_p28_results.tsv` plus hard-tail artifact
  `search23/k2_idx14_q8D_a7b11_p28_hard_results.tsv`, union
  `30/30 INFEASIBLE`; runs used the current 64-worker cap.
- Closed the full `p=29` band for q8 all-D `(a,b)=(7,11)`:
  `search23/k2_idx14_q8D_a7b11_p29_results.tsv` plus hard-tail artifact
  `search23/k2_idx14_q8D_a7b11_p29_hard_results.tsv`, union
  `29/29 INFEASIBLE`; runs used the current 64-worker cap.
- Closed the full `p=30` band for q8 all-D `(a,b)=(7,11)`:
  `search23/k2_idx14_q8D_a7b11_p30_results.tsv` plus hard-tail artifact
  `search23/k2_idx14_q8D_a7b11_p30_hard_results.tsv`, union
  `28/28 INFEASIBLE`; runs used the current 64-worker cap.
- Closed the full `p=31` band for q8 all-D `(a,b)=(7,11)`:
  `search23/k2_idx14_q8D_a7b11_p31_results.tsv` plus hard-tail artifact
  `search23/k2_idx14_q8D_a7b11_p31_hard_results.tsv`, union
  `27/27 INFEASIBLE`; runs used the current 64-worker cap.
- Closed the full `p=32` band for q8 all-D `(a,b)=(7,11)`:
  `search23/k2_idx14_q8D_a7b11_p32_results.tsv`, union
  `26/26 INFEASIBLE`; run used the current 64-worker cap.
- Closed the full `p=33` band for q8 all-D `(a,b)=(7,11)`:
  `search23/k2_idx14_q8D_a7b11_p33_results.tsv`, union
  `25/25 INFEASIBLE`; run used the current 64-worker cap.
- Closed the full `p=34` band for q8 all-D `(a,b)=(7,11)`:
  `search23/k2_idx14_q8D_a7b11_p34_results.tsv`, union
  `24/24 INFEASIBLE`; run used the current 64-worker cap.
- Closed the full `p=35` band for q8 all-D `(a,b)=(7,11)`:
  `search23/k2_idx14_q8D_a7b11_p35_results.tsv`, union
  `23/23 INFEASIBLE`; run used the current 64-worker cap.
- Closed the full `p=36` band for q8 all-D `(a,b)=(7,11)`:
  `search23/k2_idx14_q8D_a7b11_p36_results.tsv`, union
  `22/22 INFEASIBLE`; run used the current 64-worker cap.
- Closed the full `p=37` band for q8 all-D `(a,b)=(7,11)`:
  `search23/k2_idx14_q8D_a7b11_p37_results.tsv`, union
  `21/21 INFEASIBLE`; run used the current 64-worker cap.
- Closed the full `p=38` band for q8 all-D `(a,b)=(7,11)`:
  `search23/k2_idx14_q8D_a7b11_p38_results.tsv`, union
  `20/20 INFEASIBLE`; run used the current 64-worker cap.
- Closed the full `p=39` band for q8 all-D `(a,b)=(7,11)`:
  `search23/k2_idx14_q8D_a7b11_p39_results.tsv`, union
  `19/19 INFEASIBLE`; run used the current 64-worker cap.
- Closed the full `p=40` band for q8 all-D `(a,b)=(7,11)`:
  `search23/k2_idx14_q8D_a7b11_p40_results.tsv`, union
  `18/18 INFEASIBLE`; run used the current 64-worker cap.
- Closed all remaining rows for q8 all-D `(a,b)=(7,11)` after `p=40`:
  `search23/k2_idx14_q8D_a7b11_remaining_after_p40_results.tsv`, union
  `153/153 INFEASIBLE`; run used the current 64-worker cap.
- `K=2,T=2,q=8`, support `{D}`, side `(a,b)=(8,10)`: started by
  state-count quotient.  The `p=20` band is closed by
  `search23/k2_idx15_q8D_a8b10_p20_results.tsv` plus hard-tail artifact
  `search23/k2_idx15_q8D_a8b10_p20_hard_results.tsv`, union
  `32/32 INFEASIBLE`; the hard tail used timeout `600s` and the current
  64-worker cap.
- The `p=21` band for q8 all-D `(a,b)=(8,10)` is also closed by
  `search23/k2_idx15_q8D_a8b10_p21_results.tsv` plus hard-tail artifact
  `search23/k2_idx15_q8D_a8b10_p21_hard_results.tsv`, union
  `32/32 INFEASIBLE`; the hard tail used timeout `600s` and the current
  64-worker cap.
- The `p=22` band for q8 all-D `(a,b)=(8,10)` is closed by
  `search23/k2_idx15_q8D_a8b10_p22_results.tsv`, hard-tail artifact
  `search23/k2_idx15_q8D_a8b10_p22_hard_results.tsv`, and focused-tail
  artifact `search23/k2_idx15_q8D_a8b10_p22_hard2_results.tsv`, union
  `32/32 INFEASIBLE`; the focused tail used `2 jobs x 32 workers`, timeout
  `1200s`, under the current 64-worker cap.
- The `p=23` band for q8 all-D `(a,b)=(8,10)` is closed by
  `search23/k2_idx15_q8D_a8b10_p23_results.tsv`, hard-tail artifact
  `search23/k2_idx15_q8D_a8b10_p23_hard_results.tsv`, and focused-tail
  artifact `search23/k2_idx15_q8D_a8b10_p23_hard2_results.tsv`, union
  `32/32 INFEASIBLE`; the focused tail used `2 jobs x 32 workers`, timeout
  `1200s`, under the current 64-worker cap.
- The `p=24` band for q8 all-D `(a,b)=(8,10)` is closed by
  `search23/k2_idx15_q8D_a8b10_p24_results.tsv`, hard-tail artifact
  `search23/k2_idx15_q8D_a8b10_p24_hard_results.tsv`, and focused-tail
  artifact `search23/k2_idx15_q8D_a8b10_p24_hard2_results.tsv`, union
  `32/32 INFEASIBLE`; the focused tail used `2 jobs x 32 workers`, timeout
  `1200s`, under the current 64-worker cap.
- The `p=25` band for q8 all-D `(a,b)=(8,10)` is closed by
  `search23/k2_idx15_q8D_a8b10_p25_results.tsv`, hard-tail artifact
  `search23/k2_idx15_q8D_a8b10_p25_hard_results.tsv`, and focused-tail
  artifact `search23/k2_idx15_q8D_a8b10_p25_hard2_results.tsv`, union
  `32/32 INFEASIBLE`; the focused tail used `2 jobs x 32 workers`, timeout
  `1200s`, under the current 64-worker cap.
- The `p=26` band for q8 all-D `(a,b)=(8,10)` is closed by
  `search23/k2_idx15_q8D_a8b10_p26_results.tsv`, hard-tail artifact
  `search23/k2_idx15_q8D_a8b10_p26_hard_results.tsv`, and focused-tail
  artifact `search23/k2_idx15_q8D_a8b10_p26_hard2_results.tsv`, union
  `32/32 INFEASIBLE`; the focused tail used `2 jobs x 32 workers`, timeout
  `1200s`, under the current 64-worker cap.
- The `p=27` band for q8 all-D `(a,b)=(8,10)` is closed by
  `search23/k2_idx15_q8D_a8b10_p27_results.tsv`, hard-tail artifact
  `search23/k2_idx15_q8D_a8b10_p27_hard_results.tsv`, and focused-tail
  artifact `search23/k2_idx15_q8D_a8b10_p27_hard2_results.tsv`, union
  `31/31 INFEASIBLE`; the focused tail used `1 job x 32 workers`, timeout
  `1200s`, under the current 64-worker cap.
- The `p=28` band for q8 all-D `(a,b)=(8,10)` is closed by
  `search23/k2_idx15_q8D_a8b10_p28_results.tsv` plus hard-tail artifact
  `search23/k2_idx15_q8D_a8b10_p28_hard_results.tsv`, union
  `30/30 INFEASIBLE`; the hard tail used `4 jobs x 16 workers`, timeout
  `600s`, under the current 64-worker cap.
- The `p=29` band for q8 all-D `(a,b)=(8,10)` is closed by
  `search23/k2_idx15_q8D_a8b10_p29_results.tsv` plus hard-tail artifact
  `search23/k2_idx15_q8D_a8b10_p29_hard_results.tsv`, union
  `29/29 INFEASIBLE`; the hard tail used `4 jobs x 16 workers`, timeout
  `600s`, under the current 64-worker cap.
- The `p=30` band for q8 all-D `(a,b)=(8,10)` is closed by
  `search23/k2_idx15_q8D_a8b10_p30_results.tsv` plus hard-tail artifact
  `search23/k2_idx15_q8D_a8b10_p30_hard_results.tsv`, union
  `28/28 INFEASIBLE`; the hard tail used `4 jobs x 16 workers`, timeout
  `600s`, under the current 64-worker cap.
- The `p=31` band for q8 all-D `(a,b)=(8,10)` is closed by
  `search23/k2_idx15_q8D_a8b10_p31_results.tsv` plus hard-tail artifact
  `search23/k2_idx15_q8D_a8b10_p31_hard_results.tsv`, union
  `27/27 INFEASIBLE`; the hard tail used `4 jobs x 16 workers`, timeout
  `600s`, under the current 64-worker cap.
- The `p=32` band for q8 all-D `(a,b)=(8,10)` is closed by
  `search23/k2_idx15_q8D_a8b10_p32_results.tsv` plus hard-tail artifact
  `search23/k2_idx15_q8D_a8b10_p32_hard_results.tsv`, union
  `26/26 INFEASIBLE`; the hard tail used `4 jobs x 16 workers`, timeout
  `600s`, under the current 64-worker cap.
- The `p=33` band for q8 all-D `(a,b)=(8,10)` is closed by
  `search23/k2_idx15_q8D_a8b10_p33_results.tsv` plus hard-tail artifact
  `search23/k2_idx15_q8D_a8b10_p33_hard_results.tsv`, union
  `25/25 INFEASIBLE`; the hard tail used `3 jobs x 16 workers`, timeout
  `600s`, under the current 64-worker cap.
- The `p=34` band for q8 all-D `(a,b)=(8,10)` is closed by
  `search23/k2_idx15_q8D_a8b10_p34_results.tsv` plus hard-tail artifact
  `search23/k2_idx15_q8D_a8b10_p34_hard_results.tsv`, union
  `24/24 INFEASIBLE`; the hard tail used `2 jobs x 16 workers`, timeout
  `600s`, under the current 64-worker cap.
- The `p=35` band for q8 all-D `(a,b)=(8,10)` is closed by
  `search23/k2_idx15_q8D_a8b10_p35_results.tsv` plus hard-tail artifact
  `search23/k2_idx15_q8D_a8b10_p35_hard_results.tsv`, union
  `23/23 INFEASIBLE`; the hard tail used `1 job x 32 workers`, timeout
  `600s`, under the current 64-worker cap.
- The `p=36` band for q8 all-D `(a,b)=(8,10)` is closed by
  `search23/k2_idx15_q8D_a8b10_p36_results.tsv`, union
  `22/22 INFEASIBLE`; the run used `4 jobs x 16 workers`, timeout `120s`,
  under the current 64-worker cap.
- The `p=37` band for q8 all-D `(a,b)=(8,10)` is closed by
  `search23/k2_idx15_q8D_a8b10_p37_results.tsv`, union
  `21/21 INFEASIBLE`; the run used `4 jobs x 16 workers`, timeout `120s`,
  under the current 64-worker cap.
- The `p=38` band for q8 all-D `(a,b)=(8,10)` is closed by
  `search23/k2_idx15_q8D_a8b10_p38_results.tsv`, union
  `20/20 INFEASIBLE`; the run used `4 jobs x 16 workers`, timeout `120s`,
  under the current 64-worker cap.
- The `p=39` band for q8 all-D `(a,b)=(8,10)` is closed by
  `search23/k2_idx15_q8D_a8b10_p39_results.tsv`, union
  `19/19 INFEASIBLE`; the run used `4 jobs x 16 workers`, timeout `120s`,
  under the current 64-worker cap.
- The `p=40` band for q8 all-D `(a,b)=(8,10)` is closed by
  `search23/k2_idx15_q8D_a8b10_p40_results.tsv`, union
  `18/18 INFEASIBLE`; the run used `4 jobs x 16 workers`, timeout `120s`,
  under the current 64-worker cap.
- The `p=41` band for q8 all-D `(a,b)=(8,10)` is closed by
  `search23/k2_idx15_q8D_a8b10_p41_results.tsv`, union
  `17/17 INFEASIBLE`; the run used `4 jobs x 16 workers`, timeout `120s`,
  under the current 64-worker cap.
- The `p=42` band for q8 all-D `(a,b)=(8,10)` is closed by
  `search23/k2_idx15_q8D_a8b10_p42_results.tsv`, union
  `16/16 INFEASIBLE`; the run used `4 jobs x 16 workers`, timeout `120s`,
  under the current 64-worker cap.
- The `p=43` band for q8 all-D `(a,b)=(8,10)` is closed by
  `search23/k2_idx15_q8D_a8b10_p43_results.tsv`, union
  `15/15 INFEASIBLE`; the run used `4 jobs x 16 workers`, timeout `120s`,
  under the current 64-worker cap.
- The `p=44` band for q8 all-D `(a,b)=(8,10)` is closed by
  `search23/k2_idx15_q8D_a8b10_p44_results.tsv`, union
  `14/14 INFEASIBLE`; the run used `4 jobs x 16 workers`, timeout `120s`,
  under the current 64-worker cap.
- The `p=45` band for q8 all-D `(a,b)=(8,10)` is closed by
  `search23/k2_idx15_q8D_a8b10_p45_results.tsv`, union
  `13/13 INFEASIBLE`; the run used `4 jobs x 16 workers`, timeout `120s`,
  under the current 64-worker cap.
- The `p=46` band for q8 all-D `(a,b)=(8,10)` is closed by
  `search23/k2_idx15_q8D_a8b10_p46_results.tsv`, union
  `12/12 INFEASIBLE`; the run used `4 jobs x 16 workers`, timeout `120s`,
  under the current 64-worker cap.
- The `p=47` band for q8 all-D `(a,b)=(8,10)` is closed by
  `search23/k2_idx15_q8D_a8b10_p47_results.tsv`, union
  `11/11 INFEASIBLE`; the run used `4 jobs x 16 workers`, timeout `120s`,
  under the current 64-worker cap.
- The `p=48` band for q8 all-D `(a,b)=(8,10)` is closed by
  `search23/k2_idx15_q8D_a8b10_p48_results.tsv`, union
  `10/10 INFEASIBLE`; the run used `4 jobs x 16 workers`, timeout `120s`,
  under the current 64-worker cap.
- The `p=49` band for q8 all-D `(a,b)=(8,10)` is closed by
  `search23/k2_idx15_q8D_a8b10_p49_results.tsv`, union
  `9/9 INFEASIBLE`; the run used `4 jobs x 16 workers`, timeout `120s`,
  under the current 64-worker cap.
- The `p=50` band for q8 all-D `(a,b)=(8,10)` is closed by
  `search23/k2_idx15_q8D_a8b10_p50_results.tsv`, union
  `8/8 INFEASIBLE`; the run used `4 jobs x 16 workers`, timeout `120s`,
  under the current 64-worker cap.
- The `p=51` band for q8 all-D `(a,b)=(8,10)` is closed by
  `search23/k2_idx15_q8D_a8b10_p51_results.tsv`, union
  `7/7 INFEASIBLE`; the run used `4 jobs x 16 workers`, timeout `120s`,
  under the current 64-worker cap.
- The `p=52` band for q8 all-D `(a,b)=(8,10)` is closed by
  `search23/k2_idx15_q8D_a8b10_p52_results.tsv`, union
  `6/6 INFEASIBLE`; the run used `4 jobs x 16 workers`, timeout `120s`,
  under the current 64-worker cap.
- The `p=53` band for q8 all-D `(a,b)=(8,10)` is closed by
  `search23/k2_idx15_q8D_a8b10_p53_results.tsv`, union
  `5/5 INFEASIBLE`; the run used `4 jobs x 16 workers`, timeout `120s`,
  under the current 64-worker cap.
- The `p=54` band for q8 all-D `(a,b)=(8,10)` is closed by
  `search23/k2_idx15_q8D_a8b10_p54_results.tsv`, union
  `4/4 INFEASIBLE`; the run used `4 jobs x 16 workers`, timeout `120s`,
  under the current 64-worker cap.
- The `p=55` band for q8 all-D `(a,b)=(8,10)` is closed by
  `search23/k2_idx15_q8D_a8b10_p55_results.tsv`, union
  `3/3 INFEASIBLE`; the run used `3 jobs x 16 workers`, timeout `120s`,
  under the current 64-worker cap.
- The `p=56` band for q8 all-D `(a,b)=(8,10)` is closed by
  `search23/k2_idx15_q8D_a8b10_p56_results.tsv`, union
  `2/2 INFEASIBLE`; the run used `2 jobs x 16 workers`, timeout `120s`,
  under the current 64-worker cap.
- The final `p=57` row for q8 all-D `(a,b)=(8,10)` is closed by
  `search23/k2_idx15_q8D_a8b10_p57_results.tsv`, union
  `1/1 INFEASIBLE`; the full side manifest
  `search23/k2_idx15_q8D_a8b10_state_tasks.tsv` is now union-audited as
  `720/720 INFEASIBLE`, missing `0`.
- `K=2,T=2,q=8`, support `{D}`, final side `(a,b)=(9,9)` is started by
  state-count quotient.  The `p=18` band is closed by
  `search23/k2_idx16_q8D_a9b9_p18_results.tsv`, union
  `32/32 INFEASIBLE`; the run used `4 jobs x 16 workers`, timeout `120s`,
  under the current 64-worker cap.
- The `p=19` band for q8 all-D `(a,b)=(9,9)` is closed by
  `search23/k2_idx16_q8D_a9b9_p19_results.tsv`, union
  `32/32 INFEASIBLE`; the run used `4 jobs x 16 workers`, timeout `120s`,
  under the current 64-worker cap.
- The `p=20` band for q8 all-D `(a,b)=(9,9)` is closed by the union of
  `search23/k2_idx16_q8D_a9b9_p20_results.tsv`,
  `search23/k2_idx16_q8D_a9b9_p20_hard_results.tsv`, and
  `search23/k2_idx16_q8D_a9b9_p20_hard2_results.tsv`; union
  `32/32 INFEASIBLE`, missing `0`.  The focused tail used `2 jobs x 32
  workers`, timeout `1800s`, under the current 64-worker cap.
- The `p=21` band for q8 all-D `(a,b)=(9,9)` is closed by the union of
  `search23/k2_idx16_q8D_a9b9_p21_results.tsv`,
  `search23/k2_idx16_q8D_a9b9_p21_hard_results.tsv`, and
  `search23/k2_idx16_q8D_a9b9_p21_hard2_results.tsv`; union
  `32/32 INFEASIBLE`, missing `0`.  The focused tail used `2 jobs x 32
  workers`, timeout `1800s`, under the current 64-worker cap.
- The `p=22` band for q8 all-D `(a,b)=(9,9)` is closed by the union of
  `search23/k2_idx16_q8D_a9b9_p22_results.tsv`,
  `search23/k2_idx16_q8D_a9b9_p22_hard_results.tsv`, and
  `search23/k2_idx16_q8D_a9b9_p22_hard2_results.tsv`; union
  `32/32 INFEASIBLE`, missing `0`.  The focused tail used `2 jobs x 32
  workers`, timeout `1800s`, under the current 64-worker cap.
- The `p=23` band for q8 all-D `(a,b)=(9,9)` is closed by the union of
  `search23/k2_idx16_q8D_a9b9_p23_results.tsv`,
  `search23/k2_idx16_q8D_a9b9_p23_hard_results.tsv`, and
  `search23/k2_idx16_q8D_a9b9_p23_hard2_results.tsv`; union
  `32/32 INFEASIBLE`, missing `0`.  The focused tail used `2 jobs x 32
  workers`, timeout `1800s`, under the current 64-worker cap.
- The `p=24` band for q8 all-D `(a,b)=(9,9)` is closed by the union of
  `search23/k2_idx16_q8D_a9b9_p24_results.tsv`,
  `search23/k2_idx16_q8D_a9b9_p24_hard_results.tsv`, and
  `search23/k2_idx16_q8D_a9b9_p24_hard2_results.tsv`; union
  `32/32 INFEASIBLE`, missing `0`.  The focused tail used `2 jobs x 32
  workers`, timeout `1800s`, under the current 64-worker cap.
- The `p=25` band for q8 all-D `(a,b)=(9,9)` is closed by the union of
  `search23/k2_idx16_q8D_a9b9_p25_results.tsv`,
  `search23/k2_idx16_q8D_a9b9_p25_hard_results.tsv`, and
  `search23/k2_idx16_q8D_a9b9_p25_hard2_results.tsv`; union
  `32/32 INFEASIBLE`, missing `0`.  The focused tail used `2 jobs x 32
  workers`, timeout `1800s`, under the current 64-worker cap.
- The `p=26` band for q8 all-D `(a,b)=(9,9)` is closed by the union of
  `search23/k2_idx16_q8D_a9b9_p26_results.tsv`,
  `search23/k2_idx16_q8D_a9b9_p26_hard_results.tsv`, and
  `search23/k2_idx16_q8D_a9b9_p26_hard2_results.tsv`; union
  `32/32 INFEASIBLE`, missing `0`.  The focused tail used `2 jobs x 32
  workers`, timeout `1800s`, under the current 64-worker cap.
- The `p=27` band for q8 all-D `(a,b)=(9,9)` is closed by the union of
  `search23/k2_idx16_q8D_a9b9_p27_results.tsv`,
  `search23/k2_idx16_q8D_a9b9_p27_hard_results.tsv`, and
  `search23/k2_idx16_q8D_a9b9_p27_hard2_results.tsv`; union
  `31/31 INFEASIBLE`, missing `0`.  The focused tail used `2 jobs x 32
  workers`, timeout `1800s`, under the current 64-worker cap.
- The `p=28` band for q8 all-D `(a,b)=(9,9)` is closed by the union of
  `search23/k2_idx16_q8D_a9b9_p28_results.tsv`,
  `search23/k2_idx16_q8D_a9b9_p28_hard_results.tsv`, and
  `search23/k2_idx16_q8D_a9b9_p28_hard2_results.tsv`; union
  `30/30 INFEASIBLE`, missing `0`.  The focused tail used `1 job x 32
  workers`, timeout `1800s`, under the current 64-worker cap.
- The `p=29` band for q8 all-D `(a,b)=(9,9)` is closed by the union of
  `search23/k2_idx16_q8D_a9b9_p29_results.tsv` and
  `search23/k2_idx16_q8D_a9b9_p29_hard_results.tsv`; union
  `29/29 INFEASIBLE`, missing `0`.  The hard tail used `4 jobs x 16
  workers`, timeout `600s`, under the current 64-worker cap.
- The `p=30` band for q8 all-D `(a,b)=(9,9)` is closed by the union of
  `search23/k2_idx16_q8D_a9b9_p30_results.tsv` and
  `search23/k2_idx16_q8D_a9b9_p30_hard_results.tsv`; union
  `28/28 INFEASIBLE`, missing `0`.  The hard tail used `4 jobs x 16
  workers`, timeout `600s`, under the current 64-worker cap.
- The `p=31` band for q8 all-D `(a,b)=(9,9)` is closed by the union of
  `search23/k2_idx16_q8D_a9b9_p31_results.tsv` and
  `search23/k2_idx16_q8D_a9b9_p31_hard_results.tsv`; union
  `27/27 INFEASIBLE`, missing `0`.  The hard tail used `4 jobs x 16
  workers`, timeout `600s`, under the current 64-worker cap.
- The `p=32` band for q8 all-D `(a,b)=(9,9)` is closed by the union of
  `search23/k2_idx16_q8D_a9b9_p32_results.tsv` and
  `search23/k2_idx16_q8D_a9b9_p32_hard_results.tsv`; union
  `26/26 INFEASIBLE`, missing `0`.  The hard tail used `4 jobs x 16
  workers`, timeout `600s`, under the current 64-worker cap.
- The `p=33` band for q8 all-D `(a,b)=(9,9)` is closed by the union of
  `search23/k2_idx16_q8D_a9b9_p33_results.tsv` and
  `search23/k2_idx16_q8D_a9b9_p33_hard_results.tsv`; union
  `25/25 INFEASIBLE`, missing `0`.  The hard tail used `3 jobs x 16
  workers`, timeout `600s`, under the current 64-worker cap.
- The `p=34` band for q8 all-D `(a,b)=(9,9)` is closed by the union of
  `search23/k2_idx16_q8D_a9b9_p34_results.tsv` and
  `search23/k2_idx16_q8D_a9b9_p34_hard_results.tsv`; union
  `24/24 INFEASIBLE`, missing `0`.  The hard tail used `2 jobs x 16
  workers`, timeout `600s`, under the current 64-worker cap.
- The `p=35` band for q8 all-D `(a,b)=(9,9)` is closed by the union of
  `search23/k2_idx16_q8D_a9b9_p35_results.tsv` and
  `search23/k2_idx16_q8D_a9b9_p35_hard_results.tsv`; union
  `23/23 INFEASIBLE`, missing `0`.  The hard tail used `1 job x 64
  workers`, timeout `600s`, under the current 64-worker cap.
- The `p=36` band for q8 all-D `(a,b)=(9,9)` is closed by
  `search23/k2_idx16_q8D_a9b9_p36_results.tsv`; union
  `22/22 INFEASIBLE`, missing `0`.  The run used `4 jobs x 16 workers`,
  timeout `120s`, under the current 64-worker cap.
- The `p=37` band for q8 all-D `(a,b)=(9,9)` is closed by
  `search23/k2_idx16_q8D_a9b9_p37_results.tsv`; union
  `21/21 INFEASIBLE`, missing `0`.  The run used `4 jobs x 16 workers`,
  timeout `120s`, under the current 64-worker cap.
- The `p=38` band for q8 all-D `(a,b)=(9,9)` is closed by
  `search23/k2_idx16_q8D_a9b9_p38_results.tsv`; union
  `20/20 INFEASIBLE`, missing `0`.  The run used `4 jobs x 16 workers`,
  timeout `120s`, under the current 64-worker cap.
- The `p=39` band for q8 all-D `(a,b)=(9,9)` is closed by
  `search23/k2_idx16_q8D_a9b9_p39_results.tsv`; union
  `19/19 INFEASIBLE`, missing `0`.  The run used `4 jobs x 16 workers`,
  timeout `120s`, under the current 64-worker cap.
- The `p=40` band for q8 all-D `(a,b)=(9,9)` is closed by
  `search23/k2_idx16_q8D_a9b9_p40_results.tsv`; union
  `18/18 INFEASIBLE`, missing `0`.  The run used `4 jobs x 16 workers`,
  timeout `120s`, under the current 64-worker cap.
- All remaining rows after `p=40` for q8 all-D `(a,b)=(9,9)` are closed by
  `search23/k2_idx16_q8D_a9b9_remaining_after_p40_results.tsv`; union
  `153/153 INFEASIBLE`, missing `0`.  Full side audit over all
  `k2_idx16_q8D_a9b9*_results.tsv` artifacts gives `784/784 INFEASIBLE`,
  missing `0`; the whole q8 all-D `(9,9)` side is closed.
- The whole q8 all-D support is closed: `(7,11)` audited `656/656`,
  `(8,10)` audited `720/720`, and `(9,9)` audited `784/784`, all with
  missing `0`, using exact state-count quotient artifacts with anti-tightness
  disabled.
- Correction/addendum: q8 all-D has four side choices.  The remaining
  `(6,12)` side is closed after rerunning the two old UNKNOWN rows in
  `search23/k2_idx13_q8D_a6b12_missing2_results.tsv`; the four-side audit is
  `(6,12) 592/592`, `(7,11) 656/656`, `(8,10) 720/720`, `(9,9) 784/784`,
  all missing `0`.
- In the separate `k=1,q=8` cap-143 delta, the `c0=0,c1=8,(a,b)=(8,11)`
  side is now closed by `search23/k1_q8_a8b11_c0_w16_300.tsv`:
  `420/420 INFEASIBLE`, `UNKNOWN=0`, `FEASIBLE=0`.  Together with the prior
  `(7,12)` closure, two of six `c0=0` side choices are closed.
- The central `k=1,q=8,c0=0,c1=8,(a,b)=(9,10)` side is now closed by
  `search23/k1_q8_a9b10_c0_w16_300.tsv`: manifest audit gives `420/420`
  `INFEASIBLE`, `UNKNOWN=0`, `FEASIBLE=0`, missing `0`.
- The full `k=1,q=8,c0=0,c1=8` six-side family is closed: direct closures
  exist for `(7,12)`, `(8,11)`, `(9,10)`, and the root-swap symmetry
  `(A,B)<->(B,A)` closes `(12,7)`, `(11,8)`, `(10,9)`; see PROOF_STATE V479.
- The first `k=1,q=8,c0=1,c1=7` side is closed: `(a,b)=(7,12)` audited over
  `search23/k1_q8_state_count_tasks/a7_b12_c01_c17.tasks.tsv`; unique
  manifest keys `4809/4809` are covered by
  `search23/k1_q8_a7b12_c1_w16_300.tsv` and
  `search23/k1_q8_a7b12_c1_w2x32_300_part2.tsv`, all `INFEASIBLE`, missing
  `0`, `UNKNOWN=0`; see PROOF_STATE V480.
- Its A/B root-swap mate `(a,b)=(12,7)` is also closed: the `(7,12)` and
  `(12,7)` manifests have identical unique `(mask,p,M)` key sets
  (`4809/4809`, symmetric difference `0`), and V479 audits the model symmetry;
  see PROOF_STATE V481.
- The second direct `k=1,q=8,c0=1,c1=7` side is closed:
  `(a,b)=(8,11)` audited over
  `search23/k1_q8_state_count_tasks/a8_b11_c01_c17.tasks.tsv`; unique
  manifest keys `4809/4809` are covered by
  `search23/k1_q8_a8b11_c1_unique_w2x32_300.tsv`, all `INFEASIBLE`,
  missing `0`, `UNKNOWN=0`; see PROOF_STATE V482.
- Its A/B root-swap mate `(a,b)=(11,8)` is also closed: the `(8,11)` and
  `(11,8)` manifests have identical unique `(mask,p,M)` key sets
  (`4809/4809`, symmetric difference `0`), and V479 audits the model symmetry;
  see PROOF_STATE V483.
- The central direct `k=1,q=8,c0=1,c1=7` side is closed:
  `(a,b)=(9,10)` audited over
  `search23/k1_q8_state_count_tasks/a9_b10_c01_c17.tasks.tsv`; unique
  manifest keys `4809/4809` are covered by
  `search23/k1_q8_a9b10_c1_unique_w2x32_300.tsv`, all `INFEASIBLE`,
  missing `0`, `UNKNOWN=0`; see PROOF_STATE V484.
- Its A/B root-swap mate `(a,b)=(10,9)` is also closed: the `(9,10)` and
  `(10,9)` manifests have identical unique `(mask,p,M)` key sets
  (`4809/4809`, symmetric difference `0`), and V479 audits the model symmetry;
  see PROOF_STATE V485.
- Therefore the full `k=1,q=8,c0=1,c1=7` six-side family is closed: direct
  closures `(7,12)`, `(8,11)`, `(9,10)` plus root-swap closures `(12,7)`,
  `(11,8)`, `(10,9)`; see PROOF_STATE V486.
- The first `k=1,q=8,c0=2,c1=6` side is closed: `(a,b)=(7,12)` audited over
  `search23/k1_q8_state_count_tasks/a7_b12_c02_c16.tasks.tsv`; unique
  manifest keys `47424/47424` are covered by
  `search23/k1_q8_a7b12_c2_unique_w2x32_300.tsv`, all `INFEASIBLE`, missing
  `0`, `UNKNOWN=0`; see PROOF_STATE V487.
- Its A/B root-swap mate `(a,b)=(12,7)` is also closed: the `(7,12)` and
  `(12,7)` manifests have identical unique `(mask,p,M)` key sets
  (`47424/47424`, symmetric difference `0`), and V479 audits the model
  symmetry; see PROOF_STATE V488.
- The second direct `k=1,q=8,c0=2,c1=6` side is closed:
  `(a,b)=(8,11)` audited over
  `search23/k1_q8_state_count_tasks/a8_b11_c02_c16.tasks.tsv`; unique
  manifest keys `48048/48048` are covered by
  `search23/k1_q8_a8b11_c2_unique_w2x32_300.tsv`, all `INFEASIBLE`,
  missing `0`, `UNKNOWN=0`; see PROOF_STATE V489.
- Its A/B root-swap mate `(a,b)=(11,8)` is also closed: the `(8,11)` and
  `(11,8)` manifests have identical unique `(mask,p,M)` key sets
  (`48048/48048`, symmetric difference `0`), and V479 audits the model
  symmetry; see PROOF_STATE V490.
- The central direct `k=1,q=8,c0=2,c1=6` side is closed:
  `(a,b)=(9,10)` audited over
  `search23/k1_q8_state_count_tasks/a9_b10_c02_c16.tasks.tsv`; unique
  manifest keys `48048/48048` are covered by
  `search23/k1_q8_a9b10_c2_unique_w2x32_300.tsv`, all `INFEASIBLE`,
  missing `0`, `UNKNOWN=0`; see PROOF_STATE V491.
- Its A/B root-swap mate `(a,b)=(10,9)` is also closed: the `(9,10)` and
  `(10,9)` manifests have identical unique `(mask,p,M)` key sets
  (`48048/48048`, symmetric difference `0`), and V479 audits the model
  symmetry; see PROOF_STATE V492.
- Therefore the full `k=1,q=8,c0=2,c1=6` six-side family is closed: direct
  closures `(7,12)`, `(8,11)`, `(9,10)` plus root-swap closures `(12,7)`,
  `(11,8)`, `(10,9)`; see PROOF_STATE V493.
- Therefore the full new cap-143 `k=1,q=8` delta frontier isolated in
  PROOF_STATE V384/V385 is closed: `(c0,c1)=(0,8)` by V479, `(1,7)` by V486,
  and `(2,6)` by V493; see PROOF_STATE V494.
- The next `K=2,T=2,q=8` support `{S1,S2,D}` is closed: local domination
  forces `R[S1,S2]=K_{2,2}` and `D` isolated, and exact fixed-`R` state-count
  grids for idx17-20 give `3264/3264 INFEASIBLE`, missing `0`, `UNKNOWN=0`;
  see PROOF_STATE V495.
- The next `K=2,T=2,q=8` support `{E,D}` is closed: canonical `E-D` star
  masks `k=2..7` for idx21-24 give `19968/19968 INFEASIBLE`, missing `0`,
  `UNKNOWN=0`; see PROOF_STATE V496.
- The next two-empty `K=2,T=2,q=8` support `{E,D}` family is closed:
  canonical masks under `S2 x S6` give `36` masks; idx25 `(a,b)=(6,12)`
  gives `29536/29536 INFEASIBLE`, idx26 `(a,b)=(7,11)` gives
  `31840/31840 INFEASIBLE`, idx27 `(a,b)=(8,10)` gives
  `34144/34144 INFEASIBLE`, and idx28 `(a,b)=(9,9)` gives
  `36448/36448 INFEASIBLE`; total `131968/131968 INFEASIBLE`, all missing
  `0`, `UNKNOWN=0`; see PROOF_STATE V497-V500.
- Therefore the full `K=2,T=2,q=8` four-label frontier is closed: the
  manifest `search23/k2_four_label_profile_instances.tsv` has exactly
  idx13-28 for `q=8`; idx13-16 are V476, idx17-20 are V495, idx21-24 are
  V496, and idx25-28 are V497-V500.  See PROOF_STATE V501.
- The next `K=2,T=2,q=9` all-doubleton support is closed by scalar unpaired
  exact-two-root cuts: idx29-31 have `e_R=0`, `U=18`, `root_edges=21`, so
  edge upper gives `p+M<=104`, while `W=empty` cuts give `p>=37` and
  `M>=70`; contradiction.  See PROOF_STATE V502.
- The next `K=2,T=2,q=9` support `{S1,S2,D}` profile `(c0,c1,c2,c3)=(0,2,2,5)`
  is closed: local domination fixes `R[S1,S2]=K2,2`, `D` isolated, mask
  `0xf`; idx32-34 state-count grids plus targeted reruns give
  `165/165 INFEASIBLE`, missing `0`, `UNKNOWN=0`.  See PROOF_STATE V503.
- The next `K=2,T=2,q=9` support `{S1,S2,D}` profile `(0,2,3,4)` is closed:
  local domination fixes `R[S1,S2]=K2,3`, `D` isolated, mask `0x3f`; idx35-37
  grids give `360/360 INFEASIBLE`, missing `0`, `UNKNOWN=0`.  See PROOF_STATE
  V504.
- The final `K=2,T=2,q=9` support `{S1,S2,D}` profile `(0,3,3,3)` is closed:
  the `3 x 3` core complement is a matching of size `0..3`; idx38-40 grids
  plus a two-row quotient rerun give `2142/2142 INFEASIBLE`.  See PROOF_STATE
  V505.
- Therefore the full `K=2,T=2,q=9` support `{S1,S2,D}` is closed:
  idx32-34 by V503, idx35-37 by V504, and idx38-40 by V505.  See PROOF_STATE
  V506.
- The next `K=2,T=2,q=9` support `{E,D}` one-empty star family is closed:
  local domination gives `E-D` star masks `k=2..8`; idx41-43 grids give
  `1263/1263 INFEASIBLE`, missing `0`, `UNKNOWN=0`.  See PROOF_STATE V507.
- The next `K=2,T=2,q=9` support `{E,S1,S2,D}` profile `(1,2,2,4)` is
  closed: canonical empty-neighbour masks give 15 skeleton cases per side,
  and idx44-46 grids give `8841/8841 INFEASIBLE`, missing `0`, `UNKNOWN=0`.
  See PROOF_STATE V508.
- The next `K=2,T=2,q=9` support `{E,D}` profile `(2,0,0,7)` has idx47
  closed for side `(6,11)`: 55 canonical skeleton masks, `8029/8029
  INFEASIBLE` after a targeted three-row rerun.  See PROOF_STATE V509.
- The same `{E,D}` profile has idx48 closed for side `(7,10)`: continuation
  plus targeted rerun gives `8029/8029 INFEASIBLE`.  See PROOF_STATE V510.
- The same `{E,D}` profile is now fully closed: idx47-49 give `24087/24087
  INFEASIBLE` after targeted reruns.  See PROOF_STATE V511.
- The next `K=2,T=2,q=9` support `{E,D}` profile `(3,0,0,6)` has idx50
  closed for side `(6,11)`: `300` canonical skeleton masks, `69087/69087`
  original task keys covered by `INFEASIBLE` rows after recovery/hidden
  continuation, missing `0`, `UNKNOWN=0`.  See PROOF_STATE V512.
- The same `{E,D}` profile has idx51 closed for side `(7,10)`:
  first pass gave `69077 INFEASIBLE, 10 UNKNOWN`; the targeted ten-row
  rerun closed `10/10`, so `69087/69087` original task keys are covered,
  missing `0`, `UNKNOWN=0`.  See PROOF_STATE V513.
- The same `{E,D}` profile is fully closed: idx52 `(8,9)` also has
  `69087/69087` original task keys covered after recovery and a ten-row
  targeted rerun.  Thus idx50-52 give `207261/207261 INFEASIBLE`, missing
  `0`, `UNKNOWN=0`.  See PROOF_STATE V514.
- The next `K=2,T=2,q=10` all-doubleton support `{D}` is closed by scalar
  unpaired exact-two-root cuts: fixed edges are `40`, so edge upper gives
  `p+M<=103`, while `p>=37` and `M>=70` give `p+M>=107`.  Thus idx53-55
  are infeasible.  See PROOF_STATE V515.
- The next `K=2,T=2,q=10` support `{S1,S2,D}`, profile `(0,2,2,6)`, has
  fixed skeleton `R[S1,S2]=K2,2` with six isolated `D` vertices.  Its first
  side idx56 `(A,B)=(6,10)` is closed: 45/45 `(p,M)` rows are infeasible,
  using state-count rows, the side-sum prefilter, and the labelled exact
  A/B verifier for the last 12 rows.  See PROOF_STATE V517.
- The same q10 `{S1,S2,D}` profile has idx57 `(A,B)=(7,9)` closed:
  45/45 `(p,M)` rows are infeasible, using state-count rows, labelled exact
  A/B verification, split-C retries, and the full `(p,M)=(33,70)` MA/MB branch
  family.  See PROOF_STATE V518.
- The same q10 `{S1,S2,D}` profile has idx58 `(A,B)=(8,8)` closed:
  45/45 `(p,M)` rows are infeasible after labelled exact A/B verification,
  D-state bounds, symmetric MA/MB branching, and 64-worker deep branch reruns.
  Thus the full q10 profile `(0,2,2,6)` is closed.  See PROOF_STATE V519-V520.
- The next q10 `{S1,S2,D}` profile `(0,2,3,5)` is closed: local domination
  fixes `R[S1,S2]=K2,3` with five isolated `D` vertices, and labelled exact
  A/B grids close idx59 `(6,10)` 50/50, idx60 `(7,9)` 99/99, and idx61 `(8,8)`
  105/105.  See PROOF_STATE V521.
- The next q10 `{S1,S2,D}` profile `(0,2,4,4)` is closed: local domination
  fixes `R[S1,S2]=K2,4` with four isolated `D` vertices, and labelled exact
  A/B grids close idx62 `(6,10)` 65/65, idx63 `(7,9)` 114/114, and idx64 `(8,8)`
  120/120.  See PROOF_STATE V522.
- The next q10 `{S1,S2,D}` profile `(0,3,3,4)` is closed: `R[S1,S2]` is
  `K3,3` minus a matching of size `0..3`; labelled exact A/B grids close
  idx65 `(6,10)` 260/260 and idx66 `(7,9)` 260/260, while idx67 `(8,8)` closes
  after MA/MB partitioning of its 8 frontier p/M rows and a 100-worker deep
  rerun of the last 33 branches.  See PROOF_STATE V523.
- The next q10 `{S1,S2,D}` profile `(0,3,4,3)` is closed: eight canonical
  `3 x 4` singleton-core orbits are covered by labelled exact A/B grids;
  idx68 `(6,10)` is 648/648 INFEASIBLE, idx69 `(7,9)` is 1039/1039
  INFEASIBLE, and idx70 `(8,8)` is 1080/1080 INFEASIBLE.  See PROOF_STATE
  V524.
- The next q10 `{S1,S2,D}` profile `(0,4,4,2)` is closed: 42 canonical
  `4 x 4` singleton-core orbits are covered by labelled exact A/B grids;
  idx71 `(6,10)` is 4113/4113 INFEASIBLE, idx72 `(7,9)` is 6038/6038
  INFEASIBLE, and idx73 `(8,8)` is 6170/6170 INFEASIBLE.  Thus the full
  q10 support `{S1,S2,D}` is closed through V525.  See PROOF_STATE V525.
- The next q10 `{E,D}` profile `(1,0,0,9)` is closed: the 8 canonical
  star masks `e_R=2..9` are covered by state-count p/M grids; idx74 `(6,10)`,
  idx75 `(7,9)`, and idx76 `(8,8)` are each 518/518 INFEASIBLE, for
  1554/1554 total.  See PROOF_STATE V526.
- The next q10 `{E,D}` profile `(2,0,0,8)` now has idx86 `(A,B)=(6,10)`
  closed: the full 13,805-task state-count grid left 8 UNKNOWN at 180s;
  a targeted 900s rerun closed 7/8, and the final row
  `mask=0x18180,p=33,M=70` is closed by the exhaustive side-total partition
  `MA=31,32,33`.  Thus idx86 has 13,805/13,805 covered.  See PROOF_STATE V527.
- The same q10 `{E,D}` profile has idx87 `(A,B)=(7,9)` closed: the full
  13,805-task grid left 17 UNKNOWN, a targeted rerun reduced this to 6 cells,
  MA/MB branching produced 19 residual leaves, and the projected defect-block
  layer `--defect-block-labels 0` closed all 19.  Thus idx87 has
  13,805/13,805 covered.  See PROOF_STATE V528.
- The same q10 `{E,D}` profile is now fully closed: idx88 `(A,B)=(8,8)`
  closes in one full state-count pass with projection cuts `0;3` and
  `--defect-block-labels 0`, giving `13805/13805 INFEASIBLE`.  Thus idx86-88
  close profile `(2,0,0,8)`.  See PROOF_STATE V529.
- The next q10 `{E,S1,S2,D}` profile `(1,2,2,5)` is closed: local domination
  fixes `R[S1,S2]=K2,2`, the unique empty-label vertex gives 12 canonical
  skeleton masks, and state-count p/M grids close idx77 `(6,10)`,
  idx78 `(7,9)`, and idx79 `(8,8)` with `2466/2466 INFEASIBLE` each.  Thus
  idx77-79 give `7398/7398 INFEASIBLE`.  See PROOF_STATE V530.
- The next q10 `{E,S1,S2,D}` profile `(1,2,3,4)` is closed: the generic
  `{E,S1,S2,D}` generator gives 18 canonical skeleton masks, and state-count
  p/M grids with projection cuts `0;3`, defect-block label `0`, and
  anti-tightness disabled close idx80 `(6,10)`, idx81 `(7,9)`, and idx82
  `(8,8)` with `5253/5253 INFEASIBLE` each.  Thus idx80-82 give
  `15759/15759 INFEASIBLE`.  See PROOF_STATE V531.
- The next q10 `{E,S1,S2,D}` profile `(1,3,3,3)` is closed: the generic
  `{E,S1,S2,D}` generator gives 49 canonical skeleton masks, and state-count
  p/M grids with projection cuts `0;3`, defect-block label `0`, and
  anti-tightness disabled close idx83 `(6,10)`, idx84 `(7,9)`, and idx85
  `(8,8)` with `15449/15449 INFEASIBLE` each.  Thus idx83-85 give
  `46347/46347 INFEASIBLE`.  See PROOF_STATE V532.
- The next q10 `{E,S1,S2,D}` profile `(2,2,2,4)` is closed: the generalized
  generator gives 123 canonical skeleton masks, and state-count p/M grids with
  projection cuts `0;3`, defect-block label `0`, and anti-tightness disabled
  close idx89 `(6,10)`, idx90 `(7,9)`, and idx91 `(8,8)` with
  `43276/43276 INFEASIBLE` each.  Thus idx89-91 give
  `129828/129828 INFEASIBLE`.  See PROOF_STATE V533.
- The next q10 `{E,D}` profile `(3,0,0,7)` now has idx92 `(A,B)=(6,10)`
  closed: the 186349-task state-count grid is covered by a 36706-row partial
  batch plus a 149643-row remaining batch, both all INFEASIBLE, with
  `UNKNOWN=0` and `FEASIBLE=0`.  See PROOF_STATE V534.
- The same q10 `{E,D}` profile now has idx93 `(A,B)=(7,9)` closed:
  the full 186349-task state-count grid is all INFEASIBLE, with `UNKNOWN=0`
  and `FEASIBLE=0`.  See PROOF_STATE V535.
- The same q10 `{E,D}` profile `(3,0,0,7)` is now fully closed:
  idx92-94 give `559047/559047 INFEASIBLE`, with `UNKNOWN=0` and
  `FEASIBLE=0`.  See PROOF_STATE V536.
- All K2/T2 all-D support `{D}` instances with `q>=11` are closed by the
  scalar cut `p+e_R>=37` together with `p<=113-7q<=36`.  This closes
  idx98, idx99, idx150, idx151, idx234, and idx297.  See PROOF_STATE V537.
- Seven small no-empty `S1S2D` instances are closed by the scalar cut
  `p+e_R>=37`, the edge cap, and `e_R<=c1*c2`: idx235, idx236, idx298,
  idx299, idx300, idx301, and idx305.  See PROOF_STATE V538.
- Audit script `search23/audit_k2_scalar_closures_v537_v538.py` reproduces
  the V537/V538 index sets and returns PASS.
- V539 aggregate label-union MILP closure closes 13 more q11-q14 instances:
  idx120, idx121, idx182, idx183, idx255, idx271, idx302, idx303,
  idx304, idx324, idx325, idx326, and idx345.  Audit script
  `search23/audit_k2_label_union_milp_v539.py` returns PASS.
- Current STEP-1 frontier: q10 `{E,D}` profile `(4,0,0,6)`, idx95
  `(A,B)=(6,10)` is closed by V540.  Side-sum prefilter removes 558117 rows;
  complete audited count is `599478/599478 INFEASIBLE`.  Audit:
  `search23/k2_q10_ED406_sidesum_prefilter_audit.tsv`; checker
  `search23/audit_k2_sidesum_prefilter.py` verifies idx95-97 with
  `missing=0`, `extra=0`.  Closure checker
  `search23/audit_k2_filtered_result_closure.py` currently reports
  `filter_missing=0`, `filter_extra=0`, `bad_status=0`, `result_extra=0`,
  and `result_missing=0` for complete idx95.
- K2/T2 manifest size is 387 profile-side instances with q14 included for
  safety; q6-q9 are closed, q10 has only idx96-97 left, and after V537
  through V540 q11-q14 have 263 profile-side instances not yet closed by recorded
  certificates.
- A one-worker q11 idx98 side batch was stopped because visible top-level
  thread count reached 66; `_aborted_threads66` outputs are not counted.
- q11 all-D task grids for idx98 and idx99 are retained as diagnostic
  artifacts only; V537 closes those instances without solver output.
- Answer to `NEEDED_FROM_STEP1` r<=3 audit: current recorded V5 proof still
  uses BCL global at n=29 (`beta(G-v)<=floor(29^2/23.5)=35`).  I have not
  found a direct finite r=0..3 certificate in `PROOF_STATE.md`; treat this
  as an H1 audit dependency, not closed by the active q10 run.  A sufficient
  finite replacement would be `a(29)<=35`: deleting a degree-r vertex loses at
  most `floor(r/2)` beta, so r=0,1 leave beta>=37 and r=2,3 leave beta>=36.
- Answer to `NEEDED_FROM_STEP1` a25 request: not started in this STEP-1 run.
  Priority remains a(30)<=36 medium-window closure; a25 transfer/certificate
  is a separate requested audit item.
- The full `K=2,T=2,q=9` four-label frontier is closed: the manifest has
  exactly idx29-52 for q9, and V502-V514 close all of them.  See PROOF_STATE
  V516.

2026-06-23 09:03 +03 update:
- STEP-1 active compute remains q10 `{E,D}` `(4,0,0,6)`, idx96 `(A,B)=(7,9)`.
- Previous C++ `64 x 1` run ended early at 246236 rows: 246030 `INFEASIBLE`,
  206 `NO_STATUS`, 711948 missing.
- `search23/make_state_remaining_from_results.py` produced a 712154-row resume
  task file and a 246030-row clean result file.
- Relaunched idx96 with C++ `64 x 1`, PID `57764`, output
  `search23/k2_idx96_q10ED4_a7b9_state_results_sidesum_resume_after_cpp64_crash_64x1.tsv`.
- Initial live log: `done=730/712154`, `feasible=0`, `unknown=0`, `other=0`.

2026-06-23 09:07 +03 update:
- idx96 resume poll: `9948/712154` rows completed, all `INFEASIBLE`.
- Added scale summary
  `search23/k2_es1s2_quotient_sample_scale_summary.tsv`.
  Current estimates: idx270 E+S1+S2 direct grid `507457309` tasks; idx344
  small-sample estimate `4188247113` tasks.  Treat these as evidence that the
  residual E+S1+S2 branches need stronger quotient/count cuts before full
  task materialization.

2026-06-23 09:10 +03 update:
- Added `search23/finalize_k2_idx96.py`; incomplete-mode check reports
  prefix `52131`, cleaned partial `246030`, and resume `17287/712154`, all
  `INFEASIBLE`.
- After the 64-worker resume completes, this helper will merge all idx96 result
  pieces into `search23/k2_idx96_q10ED4_a7b9_state_results_sidesum_merged_complete.tsv`
  and run the independent idx96 filtered-result closure audit.

2026-06-23 09:15 +03 update:
- idx96 resume poll: `25115/712154` completed rows, all `INFEASIBLE`.
- idx97 is prepared but not running: side-sum task file has `1157735` tasks,
  side-sum prefilter kills `0`, and no result file exists yet.
- Added `search23/finalize_k2_idx97.py`; it will audit idx97 after a future
  result file `search23/k2_idx97_q10ED4_a8b8_state_results_sidesum_64x1.tsv`
  exists and has all rows `INFEASIBLE`.

2026-06-23 09:20 +03 update:
- idx96 resume poll: `31488/712154` completed rows, all `INFEASIBLE`.
- Added `search23/report_k2_q10_ed406_frontier.py` and wrote
  `search23/k2_q10_ED406_frontier_live.tsv`.
- Live q10 E+D state: idx95 closed; idx96 known completed `330538/1010315`
  after prefix + clean partial + live resume; idx97 pending with `1157735`
  tasks and no result file.

2026-06-23 09:24 +03 update:
- idx96 resume poll: `38544/712154` completed rows, all `INFEASIBLE`.
- Added guarded launcher `search23/launch_k2_idx97_after_idx96.py`.  Dry-run
  refuses to launch idx97 while active PID `57764` exists and the idx96 merged
  complete certificate is absent; intended idx97 command uses `64 x 1`.

2026-06-23 09:29 +03 update:
- idx96 resume poll: `44409/712154` completed rows, all `INFEASIBLE`.
- Added handoff note `search23/k2_q10_ED406_handoff.md`.
- Refreshed `search23/k2_q10_ED406_frontier_live.tsv`: idx95 closed; idx96
  known completed `342687/1010315`, remaining `667628`; idx97 pending with
  `1157735` tasks.

2026-06-23 09:25 +03 update:
- idx96 resume poll: `59130/712154` completed rows, all `INFEASIBLE`; active
  command uses `64 x 1`, PID `57764`.
- Saved current GPT Pro consultation prompt for the K2/T2 E+S1+S2 residual:
  `gpt_pro_consultations/2026-06-23_k2_es1s2_residual_prompt.md`.
- The E+S1+S2 residual consists exactly of idx270 `(q,A,B,cnt)=(13,6,7,1,6,6,0)`,
  idx344 `(14,6,6,1,6,7,0)`, and idx360 `(14,6,6,2,6,6,0)`.

2026-06-23 09:39 +03 update:
- idx96 resume poll: `98464/712154` completed rows, all `INFEASIBLE`; active
  command remains PID `57764` with `64 x 1`, respecting the 64-thread cap.
- GPT Pro E+S1+S2 consultation is still pending; no completed answer has been
  saved or trusted.
- Audited `state_count_6195_cpsat.py`: A/B legal states already enforce
  root-colour visibility by rejecting states with fewer than `T-1` vertices in
  any root-colour support.  This is not a missing cut.
- Added a new static no-D split-C empty-label cut to
  `search23/verify_k2_pfree_master.py`; proof note:
  `search23/k2_es1s2_splitC_cut_note.md`.  This is not yet a closure; it must
  be tested on idx270/344/360 after the current 64-worker idx96 batch frees
  thread budget.

2026-06-23 09:48 +03 update:
- idx96 resume poll: `113051/712154` completed rows, all `INFEASIBLE`.
- GPT Pro E+S1+S2 response is still pending; only the prompt and an incomplete
  opening sentence are visible.
- Re-audited the no-D split-C cut implementation against
  `search23/k2_es1s2_splitC_cut_note.md`; the code terms match both written
  cut formulas.  No closure run was launched because idx96 already occupies
  the full 64-thread allocation.

2026-06-23 09:56 +03 update:
- idx96 resume poll: `118168/712154` completed rows, all `INFEASIBLE`.
- The exact state-count verifier already has the old no-empty-label D-split
  cut; the new no-D E-split version is documented but intentionally not
  inserted into `state_count_6195_cpsat.py` while active PID `57764` is using
  that file for child processes.

2026-06-23 10:04 +03 update:
- idx96 resume poll: `123550/712154` completed rows, all `INFEASIBLE`.
- GPT Pro E+S1+S2 response remains incomplete; it has started mentioning a
  possible D=0 symmetry but no finished answer has been saved or trusted.
- `search23/k2_es1s2_splitC_cut_note.md` now includes a deferred insertion
  recipe for adding the no-D E-split cut to `state_count_6195_cpsat.py` after
  the active batch is finalized.

2026-06-23 10:18 +03 update:
- idx96 active command remains PID `57764` with `64 x 1`; process tree shows
  `64` child `cmd.exe` workers plus wrapper/conhost/pwsh, respecting the
  64-thread cap.
- Latest live stderr poll: about `138805/712154` resume rows completed, all
  `INFEASIBLE`; no `FEASIBLE`, `UNKNOWN`, or other status has appeared.
- GPT Pro E+S1+S2 consultation is still in `Pro thinking` / `Stop answering`;
  no complete answer has been saved or trusted.
- Manifest re-check confirms the residual E+S1+S2 rows are exactly idx270
  `q=13,(A,B)=(6,7),(c0,c1,c2,c3)=(1,6,6,0)`, idx344
  `q=14,(6,6),(1,6,7,0)`, and idx360 `q=14,(6,6),(2,6,6,0)`.
  The incomplete Pro claim of an idx270/idx344 symmetry is not accepted
  without an explicit reroot map because the current root parameters differ.

2026-06-23 10:25 +03 update:
- idx96 remains active at PID `57764` with `64 x 1`; latest live stderr poll:
  about `146550/712154` resume rows completed, all `INFEASIBLE`, with no
  `FEASIBLE`, `UNKNOWN`, or other status.
- Readiness audit: `search23/finalize_k2_idx96.py` refuses to merge until the
  resume result count equals the resume task count and all statuses are
  `INFEASIBLE`; `search23/launch_k2_idx97_after_idx96.py` refuses to launch
  while an active state-count process exists or the idx96 merged certificate is
  absent.
- GPT Pro E+S1+S2 consultation is still in `Finalizing answer` / `Stop
  answering`; no completed answer has been saved or trusted.

2026-06-23 10:31 +03 update:
- idx96 remains active at PID `57764` with `64 x 1`; latest frontier reporter
  saw resume `154355` rows with `154354 INFEASIBLE` and one `NO_STATUS`.
- The `NO_STATUS` row is unique in the resume task file:
  `(mask,p,M)=(0x303b89c0,46,53)`, result line `ERROR: child exit 1`.
  Do not count idx96 closed until this row is independently retried and merged
  with all other resume rows.

2026-06-23 10:38 +03 update:
- GPT Pro E+S1+S2 answer completed and was saved at
  `gpt_pro_consultations/2026-06-23_k2_es1s2_residual_answer.md`.
- Initial Codex audit: the open-neighbourhood lemma
  `sum_{u in N(v)} deg(u) <= e(G)-37` is safe from triangle-freeness and
  `beta>=37`; the projected `8 deg(v) <= e(G)-37` additionally uses the
  current `delta(G)>=8` reduction.
- For an empty-label vertex `z`, this gives a safe skeleton/generator filter
  `alpha_z + beta_z + d_R(z) <= 13`, hence `d_R(z) <= 9` because
  `alpha_z,beta_z>=2`.  Pro also proposed an exact count-quotient
  `Exact-E-ND` cut that does not use the `delta>=8` projection; this is not yet
  implemented.
- Pro's idx270/idx344 transposition claim remains conditional pending an audit
  of the exact root-selection semantics; do not use it as a closure yet.

2026-06-23 10:45 +03 update:
- idx96 still active with `64 x 1`.  Latest direct result scan:
  `169212 INFEASIBLE` and one `NO_STATUS`, same key
  `(0x303b89c0,46,53)`.
- `search23/finalize_k2_idx96.py` was updated and syntax-checked so that,
  after the resume completes, it can take `--extra-results <retry.tsv>`, clean
  non-`INFEASIBLE` rows out of the resume file, require retry TSVs to cover
  exactly those keys, and then run the normal merged closure audit.
- `python search23/finalize_k2_idx96.py --allow-incomplete` currently reports
  `175386 INFEASIBLE + 1 NO_STATUS` in the still-incomplete resume and does
  not merge.

2026-06-23 10:53 +03 update:
- idx96 remains active with `64 x 1`.  Latest frontier reporter:
  resume `179086` rows with `179085 INFEASIBLE` and one `NO_STATUS`; full idx96
  known completed `477246/1010315`, leaving `533069`.
- The only non-`INFEASIBLE` row remains `(0x303b89c0,46,53)`.  Prepared retry
  task file:
  `search23/k2_idx96_q10ED4_a7b9_state_tasks_resume_no_status_retry.tsv`.
  Do not launch it until the active 64-worker resume batch finishes, unless
  the active batch is intentionally stopped.

2026-06-23 10:59 +03 update:
- idx96 still active with `64 x 1`; latest direct TSV scan:
  `184071 INFEASIBLE` and one `NO_STATUS`, same key `(0x303b89c0,46,53)`.
- Added the projected open-neighbourhood ND8 cut to the P-free master
  `search23/verify_k2_pfree_master.py`:
  `8*(alpha[r]+beta[r]+dR[r]+label_size[r]) <= total_edges-37` for every R
  vertex.  This uses triangle-freeness, `beta>=37`, and the current
  minimum-degree-eight reduction.  Syntax check passed; no solver run was
  launched while idx96 occupies the 64-thread allocation.
- The exact count-quotient `Exact-E-ND` cut for `state_count_6195_cpsat.py`
  remains deferred until the active batch no longer spawns that verifier.

2026-06-23 11:06 +03 update:
- idx96 still active with `64 x 1`.  Latest frontier reporter:
  resume `190528` rows with `190527 INFEASIBLE` and one `NO_STATUS`; full idx96
  known completed `488688/1010315`, leaving `521627`.
- Added standalone proof note `search23/open_neighbourhood_cut_note.md` for
  the safe cut `sum_{u in N(v)} deg(u) <= e(G)-37` and its projected
  minimum-degree-eight form used in the P-free master.

2026-06-23 current poll update:
- idx96 remains active at PID `57764` with the intended `64 x 1` process shape.
  Latest direct TSV scan: `198659 INFEASIBLE` and one `NO_STATUS`, still the
  same key `(0x303b89c0,46,53)`.
- Latest stderr tail reports about `198830/712154` active resume rows, with
  `FEASIBLE=0`, `UNKNOWN=0`, and `other=1`.
- No additional state-count solver was launched; the 64-thread allocation is
  still occupied by idx96.

2026-06-23 D=0 transposition update:
- Accepted and recorded the manifest-level K2/T2 no-doubleton root-pair
  transposition in `search23/k2_d0_root_transposition_note.md`.
- Audit command `python search23/audit_k2_d0_transposition.py` returns
  `checked_d0_instances=8`, `failures=0`, `idx270->idx344`,
  `idx344->idx270`, and `idx360->idx360`.
- Consequence: idx344 is redundant with idx270, while idx360 is self-dual.
  This is not a closure of idx270 or idx360.
- Accounting check: `search23/k2_q11_q14_residual_after_v539.tsv` still has
  263 residual rows, but after V541 only 262 separate search targets remain if
  idx270 is retained, because idx344 is represented by idx270.
- The post-V541 manifest generator
  `python search23/make_k2_residual_after_v541.py` writes
  `search23/k2_q11_q14_residual_after_v541.tsv` and dependency file
  `search23/k2_q11_q14_residual_after_v541_dependencies.tsv`; it reports
  `kept=262`, `removed=1`, `removed_idx=344`.
- Independent audit `python search23/audit_k2_residual_after_v541.py` reports
  `v539=263`, `v541=262`, `dependencies=1`, `missing_kept=0`,
  `extra_kept=0`, `wrong_deps=0`, and `bad_dep_fields=0`.

2026-06-23 V541 / idx96 update:
- Recorded the no-doubleton transposition reduction as
  `problems/23/PROOF_STATE.md` V541 with status `VERIFIED MANIFEST REDUCTION`.
- Latest idx96 poll: active PID `57764`, stderr around `217545/712154`, with
  `FEASIBLE=0`, `UNKNOWN=0`, and the same single `NO_STATUS` key
  `(0x303b89c0,46,53)`.
- The 64-thread allocation remains occupied by idx96; no additional solver was
  launched.

2026-06-23 q10 ED406 current frontier:
- `python search23/report_k2_q10_ed406_frontier.py` was saved to
  `search23/k2_q10_ED406_frontier_live.tsv`.
- Latest snapshot: idx95 closed by V540; idx96 active with
  `known_completed=548691` and `remaining_to_full=461624`; idx97 prepared but
  not launched.
- idx96 active resume status in that snapshot:
  `INFEASIBLE:250530,NO_STATUS:1`; the same retry key remains pending until the
  active resume reaches `712154/712154`.

2026-06-23 64-worker cap poll:
- Active idx96 PID `57764` still runs with command-line worker count `64`.
- Refreshed `search23/k2_q10_ED406_frontier_live.tsv`: idx96 now has
  `known_completed=563127`, `remaining_to_full=447188`, and active resume
  `INFEASIBLE:264966,NO_STATUS:1`.
- The only non-`INFEASIBLE` key remains `(0x303b89c0,46,53)`; retry is deferred
  until the active resume finishes.

2026-06-23 idx96 poll:
- Active idx96 PID `57764` remains running under the 64-worker cap.
- Refreshed `search23/k2_q10_ED406_frontier_live.tsv`: idx96 now has
  `known_completed=570433`, `remaining_to_full=439882`, and active resume
  `INFEASIBLE:272272,NO_STATUS:1`.
- Read-only audit of `search23/state_count_6195_cpsat.py` found root-opposite,
  typewise A/R, B/R, A/A, B/B, R/R, unpaired cuts, quotient cuts, and split-C
  cuts present; `Exact-E-ND` remains deferred until active batch no longer
  spawns that verifier.

2026-06-23 idx96 active poll:
- Active idx96 PID `57764` remains running under the 64-worker cap.
- Refreshed `search23/k2_q10_ED406_frontier_live.tsv`: idx96 now has
  `known_completed=573756`, `remaining_to_full=436559`, and active resume
  `INFEASIBLE:275595,NO_STATUS:1`.
- Direct result scan before the refresh showed the same single non-`INFEASIBLE`
  key `(0x303b89c0,46,53)`; retry remains deferred until resume completion.

2026-06-23 idx96 active poll:
- Active idx96 PID `57764` remains running under the 64-worker cap.
- Refreshed `search23/k2_q10_ED406_frontier_live.tsv`: idx96 now has
  `known_completed=579068`, `remaining_to_full=431247`, and active resume
  `INFEASIBLE:280907,NO_STATUS:1`.
- Direct result scan showed `280152 INFEASIBLE` plus the same single
  `NO_STATUS` key `(0x303b89c0,46,53)`.

2026-06-23 idx96 active poll:
- Active idx96 PID `57764` remains running under the 64-worker cap.
- Direct result scan showed `284781 INFEASIBLE` plus the same single
  `NO_STATUS` key `(0x303b89c0,46,53)`.
- Refreshed `search23/k2_q10_ED406_frontier_live.tsv`: idx96 now has
  `known_completed=583903`, `remaining_to_full=426412`, and active resume
  `INFEASIBLE:285742,NO_STATUS:1`.
- `python search23/launch_k2_idx97_after_idx96.py --dry-run` refused launch
  because active state-count PID `57764` is still present; idx97 task count is
  `1157735`.

2026-06-23 idx96 active poll:
- Active idx96 PID `57764` remains running under the 64-worker cap.
- Direct result scan showed `289540 INFEASIBLE` plus the same single
  `NO_STATUS` key `(0x303b89c0,46,53)`.
- Refreshed `search23/k2_q10_ED406_frontier_live.tsv`: idx96 now has
  `known_completed=588655`, `remaining_to_full=421660`, and active resume
  `INFEASIBLE:290494,NO_STATUS:1`.

2026-06-23 idx96 active poll:
- Active idx96 PID `57764` remains running under the 64-worker cap.
- Refreshed `search23/k2_q10_ED406_frontier_live.tsv`: idx96 now has
  `known_completed=594359`, `remaining_to_full=415956`, and active resume
  `INFEASIBLE:296198,NO_STATUS:2`.
- Direct scan found two retry keys:
  `(0x303b89c0,46,53)` and `(0x30b09bd8,35,53)`.
- Updated `search23/k2_idx96_q10ED4_a7b9_state_tasks_resume_no_status_retry.tsv`
  so it now covers exactly those two keys; retry remains deferred until active
  resume completion.

2026-06-23 Exact-E-ND audit:
- Added `search23/audit_exact_e_nd_formula.py`, a standalone checker for the
  deferred exact open-neighbourhood formula for empty-label `R` vertices in the
  state-count quotient.
- Command `python search23/audit_exact_e_nd_formula.py --trials 2000 --seed 230623`
  returned `checked_instances=2000`, `checked_empty_vertices=4779`, and
  `failures=0`.
- This does not edit the active verifier; insertion into
  `search23/state_count_6195_cpsat.py` remains deferred until active idx96 no
  longer spawns it.

2026-06-23 idx96 active poll:
- Active idx96 PID `57764` remains running under the 64-worker cap.
- Direct result scan showed `309539 INFEASIBLE` plus two `NO_STATUS` keys:
  `(0x303b89c0,46,53)` and `(0x30b09bd8,35,53)`.
- Retry manifest
  `search23/k2_idx96_q10ED4_a7b9_state_tasks_resume_no_status_retry.tsv`
  matches exactly those two keys.
- Refreshed `search23/k2_q10_ED406_frontier_live.tsv`: idx96 now has
  `known_completed=611025`, `remaining_to_full=399290`, and active resume
  `INFEASIBLE:312864,NO_STATUS:2`.

2026-06-23 idx96 active poll:
- Active idx96 PID `57764` remains running under the 64-worker cap.
- Direct result scan showed `317770 INFEASIBLE` plus the same two
  `NO_STATUS` keys `(0x303b89c0,46,53)` and `(0x30b09bd8,35,53)`.
- Refreshed `search23/k2_q10_ED406_frontier_live.tsv`: idx96 now has
  `known_completed=616838`, `remaining_to_full=393477`, and active resume
  `INFEASIBLE:318677,NO_STATUS:2`.

2026-06-23 Exact-E-ND preview:
- Created preview-only verifier copy
  `search23/state_count_6195_cpsat_exact_e_nd_preview.py` with the deferred
  exact open-neighbourhood cut inserted.
- `python -m py_compile search23/state_count_6195_cpsat_exact_e_nd_preview.py`
  and `python search23/state_count_6195_cpsat_exact_e_nd_preview.py --help`
  both succeeded.
- The active verifier `search23/state_count_6195_cpsat.py` remains untouched
  while idx96 PID `57764` is still spawning it.

2026-06-23 idx96 active poll:
- Active idx96 PID `57764` remains running under the 64-worker cap.
- Direct result scan showed `325929 INFEASIBLE` plus the same two
  `NO_STATUS` keys `(0x303b89c0,46,53)` and `(0x30b09bd8,35,53)`.
- Refreshed `search23/k2_q10_ED406_frontier_live.tsv`: idx96 now has
  `known_completed=625015`, `remaining_to_full=385300`, and active resume
  `INFEASIBLE:326854,NO_STATUS:2`.

2026-06-23 idx96 active poll:
- Active idx96 PID `57764` remains running under the 64-worker cap.
- Direct result scan showed `330514 INFEASIBLE` plus the same two
  `NO_STATUS` keys `(0x303b89c0,46,53)` and `(0x30b09bd8,35,53)`.
- Refreshed `search23/k2_q10_ED406_frontier_live.tsv`: idx96 now has
  `known_completed=629848`, `remaining_to_full=380467`, and active resume
  `INFEASIBLE:331687,NO_STATUS:2`.

2026-06-23 idx96 active poll:
- Active idx96 PID `57764` remains running under the 64-worker cap.
- Direct result scan showed `335293 INFEASIBLE` plus the same two
  `NO_STATUS` keys `(0x303b89c0,46,53)` and `(0x30b09bd8,35,53)`.
- Refreshed `search23/k2_q10_ED406_frontier_live.tsv`: idx96 now has
  `known_completed=634323`, `remaining_to_full=375992`, and active resume
  `INFEASIBLE:336162,NO_STATUS:2`.

2026-06-23 idx96 active poll:
- Active idx96 PID `57764` remains running under the 64-worker cap.
- Direct result scan showed `340063 INFEASIBLE` plus the same two
  `NO_STATUS` keys `(0x303b89c0,46,53)` and `(0x30b09bd8,35,53)`.
- Refreshed `search23/k2_q10_ED406_frontier_live.tsv`: idx96 now has
  `known_completed=639080`, `remaining_to_full=371235`, and active resume
  `INFEASIBLE:340919,NO_STATUS:2`.

2026-06-23 idx96 active poll:
- Active idx96 PID `57764` remains running under the 64-worker cap.
- `search23/k2_q10_ED406_frontier_live.tsv` now has idx96
  `known_completed=653415`, `remaining_to_full=356900`, and active resume
  `INFEASIBLE:355254,NO_STATUS:2`.
- The only non-`INFEASIBLE` keys are still `(0x303b89c0,46,53)` and
  `(0x30b09bd8,35,53)`, both `ERROR: child exit 1`.
- No retry/finalize yet; active resume has not finished.

2026-06-23 idx96 active poll:
- Active idx96 PID `57764` remains running under the 64-worker cap.
- `search23/k2_q10_ED406_frontier_live.tsv` now has idx96
  `known_completed=665640`, `remaining_to_full=344675`, and active resume
  `INFEASIBLE:367479,NO_STATUS:2`.
- Stderr tail reports `done=367490/712154`, `feasible=0`, `unknown=0`,
  `other=2`, and `eta_s=7566`.
- No retry/finalize yet; active resume has not finished.

2026-06-23 idx96 active poll:
- Active idx96 PID `57764` remains running under the 64-worker cap.
- `search23/k2_q10_ED406_frontier_live.tsv` now has idx96
  `known_completed=669992`, `remaining_to_full=340323`, and active resume
  `INFEASIBLE:371831,NO_STATUS:2`.
- Stderr tail reports `done=371845/712154`, `feasible=0`, `unknown=0`,
  `other=2`, and `eta_s=7467`.
- Resource poll: `python=64`, private memory about `58.25 GB`.
- No retry/finalize yet; active resume has not finished.

2026-06-23 idx96 active poll:
- Active idx96 PID `57764` remains running under the 64-worker cap.
- `search23/k2_q10_ED406_frontier_live.tsv` now has idx96
  `known_completed=810395`, `remaining_to_full=199920`, and active resume
  `INFEASIBLE:512234,NO_STATUS:2`.
- Stderr tail reports `done=512245/712154`, `feasible=0`, `unknown=0`,
  `other=2`, and `eta_s=4340`.
- Resource poll: `python=62`, private memory about `42.68 GB`.
- No retry/finalize yet; active resume has not finished.

2026-06-23 idx96 finalized and idx97 launched:
- `idx96` is now closed by
  `search23/k2_idx96_q10ED4_a7b9_state_results_sidesum_merged_complete.tsv`.
- Finalizer audit for idx96: `rows=1010315`, `filter_missing=0`,
  `filter_extra=0`, `result_missing=0`, `result_extra=0`, `bad_status=0`.
- The two active-resume `NO_STATUS` keys reran as `INFEASIBLE` in
  `search23/k2_idx96_q10ED4_a7b9_state_results_resume_no_status_retry_1x1.tsv`.
- The audited Exact-E-ND cut is now inserted in
  `search23/state_count_6195_cpsat.py`; `py_compile` and `--help` succeeded.
- `idx97` launched as PID `64344` with 64 workers. Initial live frontier:
  `result_rows=3796`, `result_status=INFEASIBLE:3796`.

2026-06-23 idx97 active poll and next q11 target:
- `idx97` remains active under the 64-worker Exact-E-ND verifier.
- Live frontier: `result_rows=14207`, `result_status=INFEASIBLE:14207`,
  `remaining_to_full=1143528`; stderr reports `feasible=0`, `unknown=0`,
  `other=0`.
- Post-q10 residual manifest:
  `search23/k2_q11_q14_residual_after_v541.tsv` has `262` rows.
- First prepared q11 target after idx97 is `idx100`, with one skeleton and
  `36` state-count tasks in
  `search23/k2_idx100_q11S1S2D_0_2_2_7_a6b9_state_tasks.tsv`.

2026-06-23 idx97 active poll:
- `idx97` remains active as PID `64344` under the 64-worker Exact-E-ND verifier.
- Live frontier now has `result_rows=31030`, `result_status=INFEASIBLE:31030`,
  `remaining_to_full=1126705`; stderr showed `feasible=0`, `unknown=0`,
  `other=0`.
- `idx100` is prepared but not launched while idx97 is active: one skeleton,
  `36` tasks, `p=33..40`, `M=62..69`.

2026-06-23 idx100 helper preparation:
- Added `search23/launch_k2_idx100_after_idx97.py` and
  `search23/finalize_k2_idx100.py`.
- Both helpers passed `py_compile`; launcher dry-run refused to start while
  idx97 PID `64344` is active and while idx97 is incomplete.
- Intended idx100 launch after q10 closure: `36` jobs, one worker per job,
  same K2/T2 state-count verifier flags, no anti-tightness.

2026-06-23 forced S1+S2+D prep audit:
- `search23/k2_forced_s1s2d_task_prep.tsv` was audited against
  `search23/k2_q11_q14_residual_after_v541.tsv`: `status=PASS`.
- Coverage: `22` forced `S1+S2+D` residual instances, `1659` tasks total
  (`q=11:865`, `q=12:610`, `q=13:184`).

2026-06-23 forced S1+S2+D live reporter:
- Added `search23/report_k2_forced_s1s2d_frontier.py`; `py_compile` passed.
- Live report file: `search23/k2_forced_s1s2d_frontier_live.tsv`.
- Current forced-slice status: `22` prepared instances, `1659` tasks,
  `1659` remaining, no result files yet.

2026-06-23 forced S1+S2+D batch helpers:
- Added `search23/launch_k2_forced_s1s2d_next.py` and
  `search23/finalize_k2_forced_s1s2d_slice.py`; both passed `py_compile`.
- Launcher dry-run selected `idx100` and refused to start because idx97 PID
  `64344` is active.
- Finalizer dry-run mode reported `1659` tasks, `22` missing result files,
  `0` bad rows, before any forced-slice run.

2026-06-23 q10 E+D aggregate closure helper:
- Added `search23/finalize_k2_q10_ed406.py`; `py_compile` passed.
- In incomplete mode it verifies idx95 and idx96 complete all-`INFEASIBLE`.
- The only open q10 E+D item is still idx97; aggregate dry-run:
  `expected=2767528`, `done=1671592`, `bad=1`.

2026-06-23 q11-q14 prep coverage report:
- Added `search23/report_k2_residual_prep_coverage.py`; `py_compile` passed.
- Live report file: `search23/k2_q11_q14_prep_coverage_live.tsv`.
- Prepared residual coverage: `73/262` indices have at least one task-prep
  manifest.
- By support: `E+D 14/29`, `E+S1+S2 0/2`, `E+S1+S2+D 0/145`,
  `S1+S2 2/5`, `S1+S2+D 57/81`.

2026-06-23 missing prep plan:
- Added `search23/plan_k2_missing_prep.py`; `py_compile` passed.
- Live plan file: `search23/k2_missing_prep_plan_live.tsv`.
- First missing rows: `idx118`, `idx119`, no-empty `S1+S2+D` with
  `c1*c2=25`, requiring `--max-bits 0` prep after the worker pool is free.
- Next missing family starts at `idx122`: `E+S1+S2+D`, requiring a dedicated
  quotient task-prep pipeline.

2026-06-23 E+S1+S2+D compact prep dry-run:
- Added `search23/make_k2_es1s2d_compact_tasks.py`; `py_compile` passed.
- Dry-run for `idx122`/`idx123` shows compact allowed-edge `bits=14` and
  planned compact skeleton/task file names; no generation or solver launch.
- Prep coverage reporter now ignores `dry_run=1` rows and missing task files.
- Refreshed coverage is unchanged at `73/262`; `idx122` remains correctly
  marked unprepared.

2026-06-23 active poll / Step-2 dependency answers:
- Active 64-worker run remains `idx97` q10 `E+D` `(q,A,B;c0,c1,c2,c3)=(10,8,8;4,0,0,6)`.
  Latest stderr read: `done=100070/1157735`, `infeasible=100070`, `feasible=0`,
  `unknown=0`, `other=0`, `eta_s=26142`.  Process tree shows 64 direct
  `cmd.exe` workers under PID `64344`; no new solver is launched while this
  run is active.
- Current H1 status remains incomplete.  q10 `E+D` has idx95 closed by V540,
  idx96 closed by V542 finalization, and idx97 active; q11-q14 residual after
  V541 has `262` profile-side rows, with `73/262` prepared for task generation.
- Answer to `NEEDED_FROM_STEP1` r<=3 audit: current recorded proof still rests
  on PROOF_STATE V5, which uses BCL global at `n=29`:
  `beta(G-v)<=floor(29^2/23.5)=35`.  A direct finite r=0..3 replacement was
  not found in the current files.  The standalone L29 CEGAR route is explicitly
  recorded in PROOF_STATE as abandoned/inconclusive (`253/740` slices completed,
  `39` UNSAT, `214` INCONCLUSIVE).  Treat r<=3 as needing either an exact finite
  replacement or a write-up dependency, not as closed by current K2/T2 frontier.
- Answer to `NEEDED_FROM_STEP1` a25 request: this Step-1 run has not produced an
  exact `a(25)<=25` certificate.  Bridge audit/ledger indicate the BCL
  finite-n issue is resolved for density tails by uniform blow-up, leaving the
  finite medium window `78<=e<=99`; no Codex N=25 enumeration/certificate has
  been run here.  Priority remains the `a(30)<=36` medium-window closure.

2026-06-23 active poll / next-frontier note:
- `idx97` q10 `E+D` remains active as PID `64344` under the 64-worker cap.
  Latest stderr read: `done=113555/1157735`, `infeasible=113555`,
  `feasible=0`, `unknown=0`, `other=0`, `eta_s=25594`.  Process tree poll
  showed `64` direct `cmd.exe` workers and `64` `python.exe` grandchildren.
  No q10 finalization or q11 launch is allowed until this run exits.
- Current q10 reporter hygiene: `search23/report_k2_q10_ed406_frontier.py`
  now reports `idx96` as `closed by V542` when the merged-complete file exists,
  suppressing the historical crash-resume artefact.  Latest reporter snapshot:
  idx95 closed, idx96 closed, idx97 `109782` all-`INFEASIBLE`.
- Next post-q10 compute target remains `idx100` in the forced `S1+S2+D`
  slice: `36` tasks, no result file yet.  The forced-slice frontier has `22`
  prepared instances and `1659` pending tasks.
- First prep gaps after the prepared forced slice are `idx118/idx119`
  no-empty `S1+S2+D` high-bit rows, then `idx122+` `E+S1+S2+D`, which needs
  the compact ES1S2D task-prep pipeline before solver launch.

2026-06-23 launcher cap-guard update:
- Added explicit `jobs * workers_per_job <= 64` guards to
  `search23/launch_k2_idx100_after_idx97.py` and
  `search23/launch_k2_forced_s1s2d_next.py`.
- `py_compile` passed for both launchers.  Dry-run tests with
  `--workers-per-job 2` reported `workers_exceed_cap=72` and did not launch
  compute; active solver PID `64344` remained the only running state-count
  batch.
- During the dry-run guard test, idx97 was read at `idx97_done=120545`,
  status `{'INFEASIBLE': 120545}`.

2026-06-23 q10 finalizer readiness:
- `search23/finalize_k2_idx97.py` and `search23/finalize_k2_q10_ed406.py`
  passed `py_compile`.
- `python search23/finalize_k2_idx97.py --allow-incomplete` was run while
  idx97 remained active; it reported `expected=1157735`, `done=126065`,
  `status={'INFEASIBLE': 126065}` and did not audit/finalize because the result
  is incomplete.
- When PID `64344` exits, next commands are:
  `python search23/finalize_k2_idx97.py`, then
  `python search23/finalize_k2_q10_ed406.py`.  If either reports a non-
  `INFEASIBLE` status or missing row, stop and inspect before launching q11.

2026-06-23 ES1S2D prep hardening / active poll:
- `search23/make_k2_es1s2d_compact_tasks.py` now resolves default relative
  paths against the repository root and invokes `k2_skeletons_make_state_tasks`
  with `cwd=E:\Projects\ErdosProblems`, so future prep calls are not dependent
  on the caller's current directory.
- `py_compile` passed.  A repo-external dry-run for `idx122`/`idx123` wrote
  `search23/k2_es1s2d_compact_task_prep_dryrun_pathcheck.tsv` with absolute
  skeleton/task paths and no skeleton generation or solver launch.
- Active `idx97` remains PID `64344` under the 64-worker cap.  Latest stderr
  read: `done=145080/1157735`, `infeasible=145080`, `feasible=0`,
  `unknown=0`, `other=0`, `eta_s=24465`.

2026-06-23 ES1S2D compact audit readiness:
- Added `search23/audit_k2_es1s2d_compact_task_prep.py` to audit future
  compact `E+S1+S2+D` prep manifests.  It checks residual row agreement,
  compact allowed-edge bit counts, canonical skeleton masks, triangle-freeness,
  local domination, degree/M_floor columns, skeleton row counts, and task row
  counts; dry-run rows are skipped.
- `py_compile` passed.  Running it on
  `search23/k2_es1s2d_compact_task_prep_dryrun_pathcheck.tsv` reported
  `instances=0`, `skipped_dry_run=2`, `status=PASS`.
- Active `idx97` remains PID `64344`.  Latest stderr read:
  `done=153970/1157735`, `infeasible=153970`, `feasible=0`, `unknown=0`,
  `other=0`, `eta_s=24145`.

2026-06-23 q10/q11 gate check:
- `python search23/finalize_k2_idx97.py --allow-incomplete` reported
  `expected=1157735`, `done=158062`, `status={'INFEASIBLE': 158062}`.
  The run is still incomplete, so no q10 finalization was performed.
- `python search23/launch_k2_idx100_after_idx97.py --dry-run` reported
  `refusing_launch_active_solver=1`, `active_state_count_pids=64344`, and
  `idx100_tasks=36`; it did not launch compute.
- Active `idx97` remains PID `64344`.  Latest stderr read:
  `done=158840/1157735`, `infeasible=158840`, `feasible=0`, `unknown=0`,
  `other=0`, `eta_s=23959`.

2026-06-23 q10 ED406 reporter refresh:
- `python search23/report_k2_q10_ed406_frontier.py` reports `idx95` closed by
  V540 and `idx96` closed by V542.  Active `idx97` now has
  `result_rows=164575`, `result_status=INFEASIBLE:164575`,
  `remaining_to_full=993160`.
- No q10 finalization or q11 launch was performed.  Final live stderr read:
  `done=165515/1157735`, `infeasible=165515`, `feasible=0`, `unknown=0`,
  `other=0`, `eta_s=23764`; PID `64344` remains active.

2026-06-23 guarded q10-to-q11 advance helper:
- Added `search23/advance_k2_q10_to_idx100.py`.  By default it runs
  `finalize_k2_idx97.py`, `finalize_k2_q10_ed406.py`, and then the idx100
  launcher in dry-run mode; it only starts q11 compute if called with `--launch`.
- `py_compile` passed.  A current guard run stopped at `finalize_idx97` with
  incomplete `idx97`: `done=170669/1157735`, `status={'INFEASIBLE': 170669}`;
  it did not reach the q11 launcher.
- Active `idx97` remains PID `64344`.  Latest stderr read:
  `done=171115/1157735`, `infeasible=171115`, `feasible=0`, `unknown=0`,
  `other=0`, `eta_s=23616`.

2026-06-23 idx97 partial-result integrity check:
- A direct TSV scan of
  `search23/k2_idx97_q10ED4_a8b8_state_results_sidesum_64x1.tsv` found
  `rows=175790`, `status=INFEASIBLE:175790`, and duplicate
  `(mask,p,M,line)` keys `0`.
- The live writer continued during the scan.  Latest stderr after the scan:
  `done=176445/1157735`, `infeasible=176445`, `feasible=0`, `unknown=0`,
  `other=0`, `eta_s=23470`; PID `64344` remains active.

2026-06-23 idx97 lightweight monitor:
- Added `search23/monitor_k2_idx97.py`, a file-based monitor that reports
  expected task rows, current result status counts, remaining result rows, and
  the latest `done=...` stderr line.  Optional `--check-duplicates` checks
  duplicate `(mask,p,M,line)` keys.
- `py_compile` passed.  A duplicate-check run reported
  `result_rows=182508`, `result_status=INFEASIBLE:182508`,
  `duplicate_keys=0`, `remaining_by_results=975227`, and stderr
  `done=182510/1157735`, `unknown=0`, `other=0`, `eta_s=23301`.
- PID `64344` remains active under the 64-worker cap.

2026-06-23 idx97 monitor checkpoint:
- `python search23/monitor_k2_idx97.py` reported `expected=1157735`,
  `result_rows=185119`, `result_status=INFEASIBLE:185119`,
  `remaining_by_results=972616`; latest stderr line was
  `done=185115/1157735`, `feasible=0`, `unknown=0`, `other=0`,
  `eta_s=23225`.
- PID `64344` remains active; no q10 finalization or q11 launch was performed.
