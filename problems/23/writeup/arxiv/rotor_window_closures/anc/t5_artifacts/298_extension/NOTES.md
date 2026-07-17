# TODO-6: independent replay of the #298 ambient maxcut-extension UNSAT

Date: 2026-07-17. Agent: TODO-6 replay session (workers capped at 8; all
arithmetic integer/Boolean; CP-SAT primary, CaDiCaL SAT replay; exit codes
checked on every step).

## What this directory certifies

For the printed #298 support graph
`Q??????wE_[?EGs?D_@A?C_B???` (18 vertices, classes 0-8 / 9-17, 24 edges),
a 25-atom support circuit with a covered rotating owner at (v,x0) = (0,17)
was rebuilt on the pinned graph, independently verified, and then shown to
admit **no** triangle-free row-preserving maximum-cut extension to at most
25 vertices: all eight added-vertex assignments (k = 0..7 new owner-class
vertices) are infeasible, in BOTH the primary lazy-separation run and the
independent SAT replay. This is the #298 analogue of the paper's
Proposition `prop:extension` (#264), with the same model, scripts and
dual-verification structure.

## Pipeline (exact commands, run from `anc/`)

1. `python rebuild_t5_local_classifier_hit.py --graph6 'Q??????wE_[?EGs?D_@A?C_B???' --left 9 --right 9 --owner 0 --active 17 --workers 8 --circuit-time 300 --output t5_artifacts/298_extension/hit_298_rebuilt.json`
   - New script (added by this task). It pins the printed graph6 string
     (asserts 18 vertices, 24 edges, connected, bipartite along 0-8/9-17,
     deg(0)=deg(1)=5, graph6 round-trip identical) and reruns the archived
     engine's own circuit stage (`choose_minimal_circuit` imported from
     `rooted_t5_support_cp_sat.py`, NOT re-implemented) with the production
     constraints: 25 atoms including the rotor atom {2,3}, owner bad degree
     5 at vertices 0 and 1, triangle-free bad graph, support multiplicity
     >= 2, all 25 deletion-SDR certificates, zero-vector local classifier
     pinned to active vertex 17. Engine's exact `verify_hit` layer passed.
   - Result: `circuitStatus OPTIMAL`, atom supply 32 (matches the paper's
     "32 pairs" for #298). Exit 0.
2. `python verify_t5_local_classifier_hit.py t5_artifacts/298_extension/hit_298_rebuilt.json --output t5_artifacts/298_extension/hit_298_rebuilt_verification.json`
   - Archived independent exact verifier (NetworkX + integer matching, no
     solver; script SHA-256 017d1e44..., matching the prefix printed in the
     paper). Verdict `PASS_TRIANGLE_FREE_ZERO_VECTOR_LOCAL_PROFILE`,
     classifier vector [0,0,0,0] at (0,17), owner dead (latent component
     {0,17}, no active bad atom), minimum displayed-cut sigma -20 at switch
     {4,5,6,7,8,12,14,15,16} — consistent with `prop:dead` and
     `rem:298maxcut`. Exit 0.
3. `python extend_t5_hit_maxcut.py t5_artifacts/298_extension/hit_298_rebuilt.json --workers 8 --iterations 200 --solve-time 20 --allow-existing-extra --output t5_artifacts/298_extension/extension_298.json`
   - PRIMARY run, unrestricted crossing-edge domain (as required by the
     replay verifier and as used for #264). All eight splits terminated
     `INFEASIBLE` (completed infeasibility proofs, no ITERATION_LIMIT, no
     time-outs); `hit: null`;
     verdict `NO_HIT_OR_INFEASIBLE_BY_RECORDED_SPLIT_STATUS`. Exit 0.
4. `python verify_t5_maxcut_extension_unsat.py t5_artifacts/298_extension/hit_298_rebuilt.json t5_artifacts/298_extension/extension_298.json`
   - INDEPENDENT SAT replay (CaDiCaL 1.9.5 via PySAT), rebuilt from the
     unrestricted domain: exact mixed-triangle clauses + per-witness-checked
     row-preservation clauses + totalizer cardinality encodings of the
     recorded switch inequalities. All eight splits UNSAT
     (512-966 CNF variables, 2810-5829 clauses per split);
     verdict `PASS_ALL_EIGHT_SPLITS_UNSAT`. Exit 0. Output:
     `extension_298_verification.json`.

## The finite obstruction (from the artifacts, exact)

The switch S = {4,5,6,7,8,12,14,15,16} is crossed by 24 of the 25 selected
atoms and by only 4 support edges ((2,14),(2,15),(3,12),(3,16)); sigma =
4 - 24 = -20, matching the "-20 switch" already cited in `rem:298maxcut`.
Every row-preserving maximum-cut extension must therefore add at least 20
crossing edges on the boundary of S. Unlike #264 (capacities
21,19,...,7), this demand alone kills no assignment here
(pre-path-closure capacities 35,34,33,32,31,30,29,28 for k=0..7): the
infeasibility is joint with the row-preservation clauses (28-35 forbidden
new geodesic rows per assignment) and, at k in {0,1}, a second recorded
switch (S plus all seven new vertices; pre-path-closure capacities 7 and 8
against the same demand of 20).

## Hashes

Canonical SHA-256 (embedded `canonicalSha256`, over the sorted compact JSON
without the marker — the convention of the paper's artifact prefixes):

- `hit_298_rebuilt.json`                 ff1c120948e914d5a2f1eaccc9b99ce626d43866e0a74a17550a3b567bf5b062
- `hit_298_rebuilt_verification.json`    e1e9fe43fb934783058099bffca703391a7f5986b72ab46765bb14668487405d
- `extension_298.json`                   2bf166b7fa6f3da5a6b4229e7bb1758256bf4d7a92a7d5a121eab78dcfd15311
- `extension_298_verification.json`      d176ce66d83c6206e33b88c3726cf9a6197c49fd61fd60f2cda5469af0e3443c

File SHA-256 (over the bytes on disk):

- `hit_298_rebuilt.json`                 13337608a8d3386d7ab85c99b91a6a293b5b4b5f1780900dc5483be840eef1be
- `hit_298_rebuilt_verification.json`    967a5956a4cd0cf35f05d9a1f8355e222a8956628705ca73d521021a11c78afe
- `extension_298.json`                   78666640e804e760f971a0cee560a44f5cd4eaebcf442b61ec93bfb9ef776138
- `extension_298_verification.json`      cfea5ff488600bb24a363cad5e44732784dcd5ac9bd0c0c1fea5db386cfd0695
- `../../rebuild_t5_local_classifier_hit.py` 34859ea68026b2f860115af71e66884685d834cbf10eb7d321f1ed4ee2a151a1
- `../../extend_t5_hit_maxcut.py`        b0e362ac457171eb16e01260cd9af868cdc25e2fa20cac6445730c74c09934a2 (unmodified)
- `../../verify_t5_maxcut_extension_unsat.py` ebbf48bfc7b7ad14fc5a594b92c9be5132cb7fbb015c0c1ad1880ba380c1128e (unmodified)
- `../../verify_t5_local_classifier_hit.py` 017d1e44e6dbacab39b82d99c451e9154afa7dfc560a0c478a28d8b778153aa6 (unmodified; prefix printed in the paper)
- `../../rooted_t5_support_cp_sat.py`    dfd060bd1955e7fda6982958f40fdb70a1504a49827a7dd1efaa77e89df03053 (unmodified; engine imported by the rebuild script)

The SHA chain is closed: `extension_298.json` embeds
`sourceCanonicalSha256 = ff1c1209...` and
`extension_298_verification.json` embeds both the source and the extension
canonical hashes; both replay scripts recompute and check these before
running.

Environment: Python 3.12.4 (Windows), NetworkX 3.6.1, OR-Tools CP-SAT,
PySAT/CaDiCaL195. Workers: 8 (both scripts hard-cap at 8).

## Caveat for the integrator (important)

The original #298 hit payload (paper prefix c1d474d7) was deleted from the
repository (review issue I1). The 25-atom set in `hit_298_rebuilt.json` is
therefore a REGENERATED witness on the pinned printed graph — a valid #298
circuit certified by the same independent verifier named in `prop:hits`,
but not guaranteed bit-identical to the deleted archived atom set. The
ambient-exclusion certificate in this directory applies to THIS recorded
circuit. If the prop:hits artifacts for #298 are regenerated separately
(review I1/I3 cleanup), either reuse `hit_298_rebuilt.json` as the #298
circuit record, or rerun steps 3-4 on the new payload so that the printed
prefixes and the SHA chain stay consistent. `prop:dead`'s #298 argument is
atom-set-independent (deg(17)=2), so it is unaffected.

`anc/SHA256SUMS` was NOT touched (integrator applies manifest changes).
