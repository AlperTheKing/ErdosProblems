# CODEX LIVE STATUS

Updated: 2026-06-23T05:35+03:00

Current target: Erdős #23 finite step, K=2/T=2 q=10 four-label frontier, support {E,D}, profile (4,0,0,6).

K2/T2 manifest scope:
- Safe manifest includes q=6..14 because the historical q14/t2 closure did
  not pass the independent-audit requirements for cap 143 without rejected
  proof rules.
- Manifest size is 387 profile-side instances.  q6-q9 are closed; q10 has
  only idx96-97 left; after V537-V540, q11-q14 have 263 profile-side instances
  not yet closed by recorded certificates.

Latest verified facts:
- q=9 four-label frontier closed through V516.
- q=10 all-D support {D}, idx53-55, closed through V515.
- q=10 {S1,S2,D} profile (0,2,2,6), idx56 (A,B)=(6,10), closed through V517: 45/45 INFEASIBLE.
- q=10 {S1,S2,D} profile (0,2,2,6), idx57 (A,B)=(7,9), closed through V518: 45/45 INFEASIBLE.
- q=10 {S1,S2,D} profile (0,2,2,6), idx58 (A,B)=(8,8), closed through V519: 45/45 INFEASIBLE.
- Full q=10 {S1,S2,D} profile (0,2,2,6) closed through V520.
- Full q=10 {S1,S2,D} profile (0,2,3,5), idx59-61, closed through V521: 254/254 INFEASIBLE.
- Full q=10 {S1,S2,D} profile (0,2,4,4), idx62-64, closed through V522: 299/299 INFEASIBLE.
- Full q=10 {S1,S2,D} profile (0,3,3,4), idx65-67, closed through V523: 780/780 covered by INFEASIBLE grids/partitions.
- Full q=10 {S1,S2,D} profile (0,3,4,3), idx68-70, closed through V524: 2767/2767 INFEASIBLE.
- Full q=10 {S1,S2,D} profile (0,4,4,2), idx71-73, closed through V525: 16321/16321 INFEASIBLE.
- Therefore q=10 support {S1,S2,D} is fully closed through V525.
- Full q=10 {E,D} profile (1,0,0,9), idx74-76, closed through V526: 1554/1554 INFEASIBLE.
- q=10 {E,D} profile (2,0,0,8), idx86 (A,B)=(6,10), closed through V527: 13805/13805 covered by INFEASIBLE rows plus exhaustive MA partition of the sole residual row.
- q=10 {E,D} profile (2,0,0,8), idx87 (A,B)=(7,9), closed through V528: 13805/13805 covered by INFEASIBLE rows, MA/MB partition, and defect-block label 0 closure.
- Full q=10 {E,D} profile (2,0,0,8), idx86-88, closed through V529: idx88 has 13805/13805 INFEASIBLE with projection cuts 0;3 plus defect-block label 0.
- Full q=10 {E,S1,S2,D} profile (1,2,2,5), idx77-79, closed through V530: 7398/7398 INFEASIBLE.
- Full q=10 {E,S1,S2,D} profile (1,2,3,4), idx80-82, closed through V531: 15759/15759 INFEASIBLE.
- Full q=10 {E,S1,S2,D} profile (1,3,3,3), idx83-85, closed through V532: 46347/46347 INFEASIBLE.
- Full q=10 {E,S1,S2,D} profile (2,2,2,4), idx89-91, closed through V533: 129828/129828 INFEASIBLE.
- q=10 {E,D} profile (3,0,0,7), idx92 (A,B)=(6,10), closed through V534: 186349/186349 INFEASIBLE.
- q=10 {E,D} profile (3,0,0,7), idx93 (A,B)=(7,9), closed through V535: 186349/186349 INFEASIBLE.
- Full q=10 {E,D} profile (3,0,0,7), idx92-94, closed through V536: 559047/559047 INFEASIBLE.
- All K2/T2 all-D support {D} instances with q>=11 are closed through V537
  by the scalar contradiction `p+e_R>=37` and `p<=113-7q<=36`; this closes
  idx98, idx99, idx150, idx151, idx234, and idx297 without solver output.
- Seven small no-empty `S1S2D` instances are closed through V538 by
  `p+e_R>=37`, the edge cap, and `e_R<=c1*c2`: idx235, idx236,
  idx298, idx299, idx300, idx301, and idx305.
- Reproducibility audit for V537-V538:
  `python search23/audit_k2_scalar_closures_v537_v538.py`, status PASS.
- V539 aggregate label-union MILP closure closes 13 more q11-q14 instances:
  idx120, idx121, idx182, idx183, idx255, idx271, idx302, idx303,
  idx304, idx324, idx325, idx326, and idx345.  Audit:
  `python search23/audit_k2_label_union_milp_v539.py`, status PASS.
- Frontier accounting audit:
  `python search23/audit_k2_t2_frontier_accounting.py`, status PASS.  It
  checks manifest size 387, q10 open indices `{96,97}`, and q11-q14 residual
  count 263 after V537-V539.

Current action:
- Closed filtered idx95 q10 {E,D} profile (4,0,0,6), (A,B)=(6,10),
  by V540 state-count audit.  Complete merged result:
  `search23/k2_idx95_q10ED4_a6b10_state_results_sidesum_merged_complete.tsv`.
  Full clean idx95 audit reports `results=599478`, `result_missing=0`,
  `result_extra=0`, and `bad_status=0`.
- Running filtered idx96 q10 {E,D} profile (4,0,0,6), (A,B)=(7,9), with
  the C++ fresh-process state-count runner at `64 x 1 = 64` worker threads.
  Active PID: 10566532.
  The earlier clean 13-worker partial is preserved as
  `search23/k2_idx96_q10ED4_a7b9_state_results_sidesum_part13x1_4940_20260623.tsv`;
  it has 4940 INFEASIBLE rows and allow-incomplete audit
  `result_extra=0`, `bad_status=0`.
  A 64x1 partial is preserved as
  `search23/k2_idx96_q10ED4_a7b9_state_results_sidesum_part64x1_6400_20260623.tsv`;
  it has 6400 INFEASIBLE rows and allow-incomplete audit
  `result_extra=0`, `bad_status=0`.  The 64x1 parent was stopped after it
  stalled at the 6400-row worker-recycle boundary.
  Later in-process partials were cleaned and merged after standalone retry of
  13 exception keys.  The first C++ remainder was stopped and audited at
  22642 rows, and a completed chunked test added another 6000 audited rows.
  Current merged partial:
  `search23/k2_idx96_q10ED4_a7b9_state_results_sidesum_merged_partial52131.tsv`,
  52131 INFEASIBLE rows, with allow-incomplete audit `result_extra=0` and
  `bad_status=0`.
  Live poll at 2026-06-23T05:35+03:00 reports the active remainder file at
  `94641/958184` rows, all INFEASIBLE.  A follow-up allow-incomplete audit at
  2026-06-23T05:30+03:00 reports `results=93740`, `result_missing=864444`,
  `result_extra=0`, and `bad_status=0`; the difference is normal growth while
  the runner writes.
  No FEASIBLE or UNKNOWN row has appeared.  Current compute cap is 64 worker
  threads; no second heavy batch should be launched while this PID is active.

Lightweight prep while idx96 runs:
- Added pure `S1+S2` residual task materializer
  `search23/make_k2_pure_s1s2_tasks.py`, using nauty `genbg -l -q -d2:2`
  instead of the old `2^(c1*c2)` brute skeleton enumerator.
- Added audit helper `search23/audit_k2_pure_s1s2_task_prep.py`.
- Prepared idx180 q12 pure `S1+S2`, `(A,B)=(6,8)`, `(c1,c2)=(6,6)`:
  `search23/k2_pure_s1s2_task_prep_idx180.tsv` audits PASS with
  `72014` skeletons and `11544817` state-task rows.  No solver has been
  launched for idx180.
- Added generic task-file slice tools:
  `search23/make_state_task_slice_manifest.py`,
  `search23/audit_state_task_slice_manifest.py`, and
  `search23/materialize_state_task_slice.py`.
  The idx180 slice manifest
  `search23/k2_idx180_q12S1S2_task_slice_manifest.tsv` audits PASS with
  116 slices covering `11544817` tasks.  Smoke materialization of slice 115
  wrote `44817/44817` rows, then the temporary slice file was removed.  No
  solver has been launched for any idx180 slice.
- Patched `search23/make_k2_pure_s1s2_tasks.py` with
  `--reuse-existing-skeletons` so repeated `(c1,c2)` families can share a
  canonical skeleton file.  Prepared idx181 q12 pure `S1+S2`, `(A,B)=(7,7)`,
  `(c1,c2)=(6,6)`, reusing the idx180 6x6 skeletons:
  `search23/k2_pure_s1s2_task_prep_idx181.tsv` audits PASS with `72014`
  skeletons and `11846739` state-task rows.  Slice manifest
  `search23/k2_idx181_q12S1S2_task_slice_manifest.tsv` audits PASS with 119
  slices covering all `11846739` tasks.  No solver has been launched for
  idx181.
- Added result-family audit helper
  `search23/audit_state_task_slice_result_family.py`.  Synthetic tests verify
  a complete slice result as PASS and `--require-complete` as FAIL when a
  result file is missing.  On current idx180/idx181 manifests it reports
  `completed=0`, `missing_files=116/119`, `bad_audits=0`, status PASS without
  `--require-complete`; this records that no slice-result certificate exists
  yet.
- Added pure `S1+S2` skeleton-slice tools
  `search23/make_k2_pure_s1s2_slice_manifest.py` and
  `search23/audit_k2_pure_s1s2_slice_manifest.py`.  `genbg` scale counts for
  the remaining pure `S1+S2` profiles are `(6,7)=706436`,
  `(6,8)=5917256`, and `(7,7)=14280402` canonical bipartite skeletons.
  Prepared idx254 q13 pure `S1+S2`, `(A,B)=(6,7)`, `(c1,c2)=(6,7)`:
  `search23/k2_pure_s1s2_slice_manifest_idx254.tsv` audits PASS with
  `706436` skeletons, 15 skeleton slices, and `293777388` state-task rows.
  No solver has been launched for idx254.
- Added raw/overcomplete scale estimator
  `search23/estimate_k2_es1s2_raw.py` for the three residual `E+S1+S2`
  instances idx270, idx344, and idx360.  Smoke tests:
  `python -m py_compile search23/estimate_k2_es1s2_raw.py` PASS and
  `idx270 --limit-skeletons 100` reports `raw_skeletons=6059`,
  `active_raw_skeletons=6059`, `tasks=2528739`.  This is a scale diagnostic
  only; no `E+S1+S2` certificate or solver run exists yet, and direct raw
  materialization appears too costly without a stronger quotient/canonical
  reduction.
- Built `tools/nauty2_8_9/labelg.exe` from the existing nauty source tree.
  `shortg.exe` failed to build on this Windows/Mingw toolchain because
  `shortg.c` requires `fork/pipe/wait`.  `labelg -f` was smoke-tested on
  three `6x6` bipartite graph6 rows and produced three canonical graph6 lines.
  Added `search23/smoke_k2_es1s2_labelg_quotient.py` to test this route on
  `E+S1+S2` raw candidates.  After fixing graph6 bit order, the idx270
  100-base-skeleton smoke reports `raw_graphs=6059`, `canonical_orbits=1651`,
  and `bad_partition_edges=0`.  With `--output`, it writes canonical compact
  mask samples; `search23/k2_idx270_es1s2_labelg_quotient_sample100.tsv` has
  `1651` unique masks, `raw_count_sum=6059`, and `bad_eR=0`.  This supports a
  future quotient generator, but no closure certificate has used it yet.
  Independent audit
  `python search23/audit_k2_es1s2_labelg_quotient_sample.py --sample search23/k2_idx270_es1s2_labelg_quotient_sample100.tsv --expect-rows 1651 --expect-raw-sum 6059`
  returns PASS.
  Added `search23/make_k2_es1s2_labelg_quotient_tasks.py` and
  `search23/audit_k2_es1s2_labelg_quotient_tasks.py`; the sample task grid
  `search23/k2_idx270_es1s2_labelg_quotient_sample100_tasks.tsv` has
  `695788` rows and audits PASS against the canonical sample TSV.
  Added `--max-raw-graphs` guard to the smoke tool.  A second guarded sample
  for idx344 using 10 `(6,7)` base skeletons reports `raw_graphs=2457`,
  `canonical_orbits=164`, and sample audit PASS.  Its task grid
  `search23/k2_idx344_es1s2_labelg_quotient_sample10_tasks.tsv` has `59287`
  rows and audits PASS.  The materializer now also emits prep manifests; the
  20k-slice manifest
  `search23/k2_idx344_es1s2_labelg_quotient_sample10_slice_manifest.tsv` has
  `3` slices and audits PASS.
  Added chunked generator
  `search23/make_k2_es1s2_labelg_quotient_skeletons.py`; on the same idx344
  sample with `--raw-chunk-size 300`, it reproduces the non-chunked `164`
  masks and raw counts exactly, with sample audit PASS.
  Added `--count-only` to the task materializer.  It reproduces the known
  idx344 sample task count `59287`, and reports `7046648` task rows for the
  idx270 1000-base-skeleton quotient sample without writing a large task TSV.
  Active remaining task grid:
  `search23/k2_idx96_q10ED4_a7b9_state_tasks_sidesum_remaining_after_52131.tsv`,
  958184 rows.  Active result file:
  `search23/k2_idx96_q10ED4_a7b9_state_results_sidesum_cpp64x1_after52131.tsv`.
  No idx97 batch is active.
- Chunked in-process helper
  `search23/run_state_count_6195_tasks_chunked_inproc.py` was tested on one
  6000-row chunk.  The chunk output is clean and merged, but worker recycling
  spawned more than the allowed process envelope, so the chunked runner was
  stopped.  The helper is now patched to set `CODEX_POOL_MAXTASKS` above the
  chunk size, but that fix has not been run-tested.  The safe active path is
  the C++ fresh-process runner above.

Diagnostic artifacts:
- Prepared all residual no-empty `S1+S2+D` profiles with `c1=2`, without
  starting a solver.  Local domination forces `R[S1,S2]=K_{2,c2}`, so each
  profile has one compact-mask skeleton.  The preparation covers 22
  profile-side instances and 1659 total `(p,M)` tasks: q11 has 8 instances
  and 865 tasks, q12 has 10 instances and 610 tasks, q13 has 4 instances and
  184 tasks.  Artifacts:
  `search23/make_k2_forced_s1s2d_tasks.py`,
  `search23/k2_forced_s1s2d_task_prep.tsv`, and
  `search23/k2_idx*_q*S1S2D_*_state_tasks.tsv` entries listed in the audit.
  Independent audit:
  `python search23/audit_k2_forced_s1s2d_task_prep.py`, status PASS.
- Prepared a broader audited no-empty `S1+S2+D` small-bit package using the
  compact-mask C++ skeleton generator
  `search23/k2_noempty_s1s2d_skeletons.cpp`.  For residual profiles with
  `c1*c2<=16`, the task prep covers 45 profile-side instances, 360 skeletons,
  and 44292 `(p,M)` tasks.  Distribution by q: q11 has 26434 tasks, q12 has
  14843, q13 has 2624, and q14 has 391.  Audit:
  `python search23/audit_k2_noempty_s1s2d_task_prep.py`, status PASS.
- Expanded the no-empty `S1+S2+D` task-prep package to `c1*c2<=20`:
  `search23/k2_noempty_s1s2d_task_prep_bits20.tsv` lists 55 profile-side
  instances, 1280 skeletons, and 222749 `(p,M)` tasks.  Distribution by q:
  q11 has 114663 tasks, q12 has 84001, q13 has 18888, and q14 has 5197.
  Audit:
  `python search23/audit_k2_noempty_s1s2d_task_prep.py --audit search23/k2_noempty_s1s2d_task_prep_bits20.tsv`,
  status PASS.
- Prepared the next no-empty `S1+S2+D` slice with `c1*c2=21`
  (`idx245` and `idx309`): 2 profile-side instances, 56 skeletons, and
  7380 `(p,M)` tasks.  Audit:
  `python search23/audit_k2_noempty_s1s2d_task_prep.py --audit search23/k2_noempty_s1s2d_task_prep_bits21_idx245_309.tsv`,
  status PASS.
- E+D residual preparation was attempted with `search23/make_k2_ed_tasks.py`,
  but broad and q11-only runs exceeded 60 seconds and were stopped without
  launching any solver.  E+D remains a preparation target needing a smaller
  profile split or optimized generator.
- Prepared the first two E+D residual side choices individually:
  `idx134` and `idx135`, both with `(c0,c1,c2,c3)=(2,0,0,9)`.  Artifacts:
  `search23/k2_ed_task_prep_idx134.tsv` and
  `search23/k2_ed_task_prep_idx135.tsv`.  Combined package has 220 skeletons
  and 36264 `(p,M)` tasks.  Audit:
  `python search23/audit_k2_ed_task_prep.py --audit ...`, status PASS for
  each file.
- Prepared the next two E+D residual side choices individually:
  `idx142` and `idx143`, both with `(c0,c1,c2,c3)=(3,0,0,8)`.  Artifacts:
  `search23/k2_ed_task_prep_idx142.tsv` and
  `search23/k2_ed_task_prep_idx143.tsv`.  Combined package has 2642 skeleton
  rows and 668462 `(p,M)` tasks.  Audit:
  `python search23/audit_k2_ed_task_prep.py --audit ...`, status PASS for
  each file.
- Prepared the next two E+D residual side choices individually:
  `idx146` and `idx147`, both with `(c0,c1,c2,c3)=(4,0,0,7)`.
  Artifacts: `search23/k2_ed_task_prep_idx146.tsv` and
  `search23/k2_ed_task_prep_idx147.tsv`, with 21656 combined skeleton rows
  and 7128779 combined `(p,M)` tasks.  Audit:
  `python search23/audit_k2_ed_task_prep.py --audit ...`, status PASS for
  each file.  No solver has been launched for these files.
- Added and audited a faster E+D skeleton generator:
  `search23/k2_ed_skeletons_fast.cpp`.  Orbit comparison against the old
  generator matches for `(c0,c3)=(3,8)` and `(4,7)`.  The fast generator
  handles `(c0,c3)=(5,6)` in 0.831 seconds with 35535 skeletons; the old
  generator exceeded 60 seconds on that profile and was stopped.
- Prepared the final two q11 E+D residual side choices individually:
  `idx148` and `idx149`, both with `(c0,c1,c2,c3)=(5,0,0,6)`.
  Artifacts: `search23/k2_ed_task_prep_idx148.tsv` and
  `search23/k2_ed_task_prep_idx149.tsv`, with 71070 combined skeleton rows
  and 28091014 combined `(p,M)` tasks.  Audit:
  `python search23/audit_k2_ed_task_prep.py --audit ...`, status PASS for
  each file.  No solver has been launched for these files.
- Therefore every q11 residual E+D profile-side instance is prepared and
  audited as task grids: idx134, idx135, idx142, idx143, idx146, idx147,
  idx148, and idx149.
- Prepared and audited the first six q12 residual E+D side choices:
  idx204, idx205, idx218, idx219, idx226, and idx227.  Combined package:
  70814 skeleton rows and 20617362 `(p,M)` tasks.  Audit:
  `python search23/audit_k2_ed_task_prep.py --audit ...`, status PASS for
  each file.  No solver has been launched for these files.
- Benchmarked q12 E+D `(c0,c3)=(5,7)` with the fast generator:
  224346 skeletons in 4.163 seconds.  Task prep for that profile should be
  split or compressed before generating full task grids.
- Added sliced task-maker `search23/k2_skeletons_make_state_tasks_slice.cpp`
  for large skeleton files.  Audit on idx204: two slices reproduce the full
  task-maker set exactly, `17138/17138` tasks.
- Added no-output task counter `search23/k2_skeletons_count_state_tasks.cpp`.
  Audit on idx204 returns 17138 tasks, matching the task-maker output.
- Counted the remaining large q12 E+D grids without writing full task files:
  idx230 has 81316201 tasks, idx231 has 81839608, idx232 has 195597390, and
  idx233 has 196935286.  These should be handled by skeleton slices or a
  compressed runner, not full monolithic task TSVs.
- Generated audited slice manifest for the same large q12 E+D grids:
  `search23/k2_ed_slice_manifest_q12_large_idx230_233.tsv`.  It has 30
  slice rows: idx230 and idx231 have 5 slices each, idx232 and idx233 have
  10 slices each.  Manifest task totals match the no-output counter values.
- Added reusable slice-manifest audit script
  `search23/audit_k2_ed_slice_manifest.py`; it returns PASS on
  `search23/k2_ed_slice_manifest_q12_large_idx230_233.tsv`.
- Added slice materialization helper `search23/materialize_k2_ed_slice.py`.
  Test on idx204 slice 0 produced `3267/3267` expected tasks.
- Added slice-result closure audit helper
  `search23/audit_k2_ed_slice_result_closure.py`.  Synthetic complete test on
  idx204 slice 0 reports `expected=3267`, `results=3267`, `missing=0`,
  `extra=0`, `bad_status=0`; allow-incomplete test reports `missing=1`.
- Added dry-run capable slice runner `search23/run_k2_ed_slice.py`.  Dry-run
  on idx230 slice 0 builds the materialize/run/audit commands with 60 x 1
  workers, `expected_tasks=15688432`, and standard K2 child arguments.
- Added family-level slice audit helper `search23/audit_k2_ed_slice_family.py`.
  Dry-run on the q12 large E+D manifest reports 4 instances, 30 slices, and
  30 missing result files.  Synthetic idx204 test audits one completed slice
  and reports two missing slice results, with zero failures.
- Added `--reuse-existing-skeletons` to `search23/make_k2_ed_slice_manifest.py`.
  Using the completed `(c0,c3)=(5,8)` skeleton file, generated and audited
  `search23/k2_ed_slice_manifest_idx293.tsv`: 23 slices, 1133993 skeletons,
  and 344494239 tasks.
- Added geng-backed E+D skeleton generator
  `search23/k2_ed_skeletons_geng.cpp` / `.exe` for `c0<=8`.  It uses
  `tools/nauty2_8_9/geng.exe -t` for the empty-label subgraph and was
  orbit-audited against the existing fast generator on the E-triangle-free
  subset: `(c0,c3)=(3,8)` gives `1317/1317` orbits and `(4,7)` gives
  `10763/10763` orbits.
- Built `tools/nauty2_8_9/genbg.exe` by direct `gcc` commands after the
  makefile path failed without `sh.exe`.  Smoke test:
  `genbg -u -d2:0 7 6` reports `945762` incidence graphs in 0.29 seconds.
- Added `search23/k2_ed_genbg_ee_stats.cpp` / `.exe`: incidence-first E+D
  scale audit.  Raw extension counts include `(7,6)=1774891`,
  `(8,6)=228320779`, `(7,7)=160727623`, `(6,8)=45373261`, and
  `(5,9)=4779693`.
- Added `search23/k2_ed_genbg_raw_skeletons_slice.cpp` / `.exe`: an
  overcomplete raw skeleton slice materializer.  Smoke tests:
  `(3,8)` slice 10 writes 10 skeletons and the existing counter reads 1034
  tasks; `(7,6)` slice 0 writes 1000 skeletons and the counter reads 372869
  tasks.
- Added `search23/audit_state_task_result_closure.py` and dry-run wrapper
  `search23/run_k2_ed_raw_slice.py`.  Synthetic audit closes 10/10 keys, and
  dry-run idx296 emits materialize/run/audit commands without launching a
  solver.
- Added raw-overcomplete manifest tooling:
  `search23/make_k2_ed_raw_slice_manifest.py` and
  `search23/audit_k2_ed_raw_slice_manifest.py`.  The remaining six E+D
  instances are planned in
  `search23/k2_ed_raw_slice_manifest_remaining.tsv`: 8880 slices covering
  443871224 raw skeleton-extension intervals, audit PASS.
- Added `search23/run_k2_ed_raw_manifest_slice.py`; dry-run on idx296 slice 0
  emits a 60 x 1 worker raw-slice command from the manifest without launching
  a solver.
- Added `search23/audit_k2_ed_raw_slice_family.py`.  On the new raw manifest
  it reports 8880 slices, 0 completed slices, 0 bad audits, and status PASS;
  `--require-complete` can be used after runs to enforce full closure.
- Added `search23/report_state_batch_progress.py`; it reports expected rows,
  written rows, missing rows, completion percent, and status counts for any
  task/result TSV pair.
- Current E+D residual accounting: 29 total profile-side instances; 23 now
  have prepared task grids or audited slice manifests.  Remaining E+D instances
  are idx295 `(6,7)`, idx296 `(7,6)`, idx379 `(5,9)`, idx383 `(6,8)`,
  idx385 `(7,7)`, and idx386 `(8,6)`.  The `c0>6` cases need a generator
  beyond the current fast E+D tool; the new geng-backed generator is correct
  on audited small cases but timed out at 30 seconds on `(7,6)`, so the current
  next candidate is the `genbg` incidence-first raw slice path.
- q11 all-D idx98 `(A,B)=(6,9)` task grid:
  `search23/k2_idx98_q11D_a6b9_state_tasks.tsv`, 186 cells.
- q11 all-D idx99 `(A,B)=(7,8)` task grid:
  `search23/k2_idx99_q11D_a7b8_state_tasks.tsv`, 215 cells.
  These are not solver obligations after V537; they are retained only to
  document the grid that the scalar closure supersedes.

Thread budget:
- Hard cap is 64 total hardware threads for Codex runs.  idx96 is running
  with the C++ fresh-process `64 x 1` pattern; do not launch idx97 while
  idx96 is active.

2026-06-23 09:03 +03 update:
- The prior idx96 C++ `64 x 1` process ended early after writing 246236 result
  rows: 246030 `INFEASIBLE`, 206 `NO_STATUS`, 711948 missing.
- Added `search23/make_state_remaining_from_results.py` and created
  `search23/k2_idx96_q10ED4_a7b9_state_tasks_sidesum_resume_after_cpp64_crash.tsv`.
  It contains 712154 tasks: all missing rows plus the 206 noncompleted rows.
- Clean completed rows are in
  `search23/k2_idx96_q10ED4_a7b9_state_results_sidesum_cpp64x1_after52131_clean.tsv`
  with 246030 rows.
- Relaunched idx96 resume with C++ fresh-process `64 x 1`; PID file:
  `search23/k2_idx96_q10ED4_a7b9_state_results_sidesum_resume_after_cpp64_crash_64x1.pid`
  and current PID `57764`.
- Output:
  `search23/k2_idx96_q10ED4_a7b9_state_results_sidesum_resume_after_cpp64_crash_64x1.tsv`.
  Initial log shows `done=730/712154`, `feasible=0`, `unknown=0`, `other=0`.

2026-06-23 09:07 +03 update:
- Latest idx96 resume poll:
  `search23/k2_idx96_q10ED4_a7b9_state_results_sidesum_resume_after_cpp64_crash_64x1.tsv`
  has `9948/712154` completed rows, all `INFEASIBLE`.
- Added `search23/summarize_k2_es1s2_quotient_samples.py`; `python -m py_compile`
  passes for it and `search23/make_state_remaining_from_results.py`.
- Scale summary:
  `search23/k2_es1s2_quotient_sample_scale_summary.tsv`.
  It estimates idx270 full E+S1+S2 task grid at `507457309` tasks from the
  1000-base sample, and idx344 at `4188247113` tasks from the very small
  10-base sample.  These branches should not be launched as direct full TSV
  grids before stronger quotient/count cuts.

2026-06-23 09:10 +03 update:
- Added `search23/finalize_k2_idx96.py`.  When the current resume completes,
  it merges:
  `search23/k2_idx96_q10ED4_a7b9_state_results_sidesum_merged_partial52131.tsv`,
  `search23/k2_idx96_q10ED4_a7b9_state_results_sidesum_cpp64x1_after52131_clean.tsv`,
  and the current resume output into
  `search23/k2_idx96_q10ED4_a7b9_state_results_sidesum_merged_complete.tsv`,
  then runs `search23/audit_k2_filtered_result_closure.py` for idx96.
- In incomplete mode it currently reports prefix `52131`, clean partial
  `246030`, and resume `17287/712154`, all `INFEASIBLE`.

2026-06-23 09:15 +03 update:
- Latest idx96 resume poll:
  `search23/k2_idx96_q10ED4_a7b9_state_results_sidesum_resume_after_cpp64_crash_64x1.tsv`
  has `25115/712154` completed rows, all `INFEASIBLE`.
- idx97 `(A,B)=(8,8)` is not launched while idx96 is active.  Its side-sum
  task file has `1157735` tasks, and
  `search23/audit_k2_sidesum_prefilter.py --skeletons search23/k2_q10_ED406_skeletons.tsv --original search23/k2_idx97_q10ED4_a8b8_state_tasks.tsv --filtered search23/k2_idx97_q10ED4_a8b8_state_tasks_sidesum.tsv --a 8 --b 8`
  reports `killed=0`, `missing=0`, `extra=0`.
- Added `search23/finalize_k2_idx97.py`; `python -m py_compile` passes and
  `--allow-missing` reports expected results file absent with `expected=1157735`.

2026-06-23 09:20 +03 update:
- Latest idx96 resume poll:
  `search23/k2_idx96_q10ED4_a7b9_state_results_sidesum_resume_after_cpp64_crash_64x1.tsv`
  has `31488/712154` completed rows, all `INFEASIBLE`.
- Added read-only q10 E+D frontier reporter:
  `search23/report_k2_q10_ed406_frontier.py`; `python -m py_compile` passes.
- Current live frontier table:
  `search23/k2_q10_ED406_frontier_live.tsv`.  It reports idx95 closed with
  `599478/599478`, idx96 known completed `330538/1010315` after combining
  prefix, clean partial, and live resume output, and idx97 pending with
  `1157735` tasks.

2026-06-23 09:24 +03 update:
- Latest idx96 resume poll:
  `search23/k2_idx96_q10ED4_a7b9_state_results_sidesum_resume_after_cpp64_crash_64x1.tsv`
  has `38544/712154` completed rows, all `INFEASIBLE`.
- Added guarded idx97 launcher:
  `search23/launch_k2_idx97_after_idx96.py`; `python -m py_compile` passes.
  Dry-run reports active PID `57764`, missing idx96 merged-complete certificate,
  `idx97_tasks=1157735`, and refuses to launch while idx96 is active.

2026-06-23 09:29 +03 update:
- Latest idx96 resume poll:
  `search23/k2_idx96_q10ED4_a7b9_state_results_sidesum_resume_after_cpp64_crash_64x1.tsv`
  has `44409/712154` completed rows, all `INFEASIBLE`.
- Added `search23/k2_q10_ED406_handoff.md` with the exact poll, finalize,
  guarded idx97 launch, and idx97 finalize commands.
- Refreshed `search23/k2_q10_ED406_frontier_live.tsv`: idx96 known completed
  `342687/1010315`, remaining `667628`; idx97 remains pending with `1157735`
  tasks.

2026-06-23 09:25 +03 update:
- Latest idx96 resume poll:
  `search23/k2_idx96_q10ED4_a7b9_state_results_sidesum_resume_after_cpp64_crash_64x1.tsv`
  has `59130/712154` completed rows, all `INFEASIBLE`.
- Active runner remains PID `57764`, command line contains `64` jobs and
  `1` worker per child; no second state-count solver was launched.
- Wrote the current E+S1+S2 structural-cut prompt to
  `GPT_PRO_QUESTION.md` and
  `gpt_pro_consultations/2026-06-23_k2_es1s2_residual_prompt.md`.
  The prompt covers exactly residual idx270, idx344, and idx360 and asks for
  safe quotient/skeleton cuts before direct full task materialization.
