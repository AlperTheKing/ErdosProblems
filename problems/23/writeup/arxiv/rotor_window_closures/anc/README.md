# Ancillary files for "Balanced deficiency rotors in shortest-support Hall systems of triangle-free maximum cuts"

All hashes: see `SHA256SUMS` (SHA-256, lowercase hex, relative paths).

## Eight-vertex rotor (Section: An eight-vertex neutral square rotor)

- `_claude_r39_8vtx_rotor_gate.py` — exhaustive verifier for every numbered
  statement of the rotor section except the automorphism.
  Run: `python _claude_r39_8vtx_rotor_gate.py`.
  Expected output ends with `CLAUDE-GATE=PASS (exhaustive)`.
- `verify_rotor8_automorphism.py` — stdlib-only exhaustive checker for the
  automorphism proposition (adjacency preservation, order four, shore swap,
  BFS recomputation of d_B = 4, geodesic/state re-enumeration, transitive
  4-cycle action). Run: `python verify_rotor8_automorphism.py`.
  Expected output ends with `PASS_ROTOR8_AUTOMORPHISM`, exit 0.

## Sixteen-atom closure (t = 4)

Primary enumeration (requires `geng` from nauty/Traces and Python 3 with
NetworkX for the verifiers):

- `enumerate_t4_support_graphs.py`, `enumerate_t4_atom_circuits.py`,
  `enumerate_t4_profile_transitions.py` — the census pipeline; emits the
  canonical JSON artifacts whose SHA-256 hashes are printed in the paper.

Independent verifiers (second acceptance path):

- `verify_t4_support_census.py`, `verify_t4_atom_census.py`,
  `verify_t4_profile_exclusion.py`, `verify_t4_cross_outer_exclusion.py`.

Abstract support-only survivor (Remark "Why geometry is load-bearing"):

- `search_t4_support_circuit.py` (search harness; hits at seed 0, step 0),
  `verify_t4_support_circuit.py` (independent recheck).

The five canonical JSON artifacts of the census are shipped in
`t4_artifacts/` (the paper prints their embedded `canonicalSha256` values;
`SHA256SUMS` lists the whole-file hashes, which differ). The `verify_t4_*.py`
scripts expect the artifacts in the same directory as the scripts, so copy
`t4_artifacts/*.json` beside them before running; `verify_t4_support_census.py`
additionally resolves `geng` at `tools/nauty2_8_9/geng.exe` three directory
levels above its own location (`HERE.parents[2]/tools/nauty2_8_9/geng.exe`).
Provenance and verifier verdicts: `NOTES_TODO7_t4_artifacts.md`.

## Twenty-five atoms (t = 5)

- `rooted_t5_support_cp_sat.py` — OR-Tools CP-SAT model for the support
  relaxation (R1)-(R7); produced the order 15/16/17 split certificates.
- `verify_t5_local_classifier_hit.py` — independent exact verification of the
  two order-18 circuit hits (#298, #264).
- `verify_t5_active_scope_unsat.py`, `verify_t5_tail_blanket_unsat.py` —
  dead-owner / tail-blanket certificates (CaDiCaL via PySAT).
- `extend_t5_hit_maxcut.py`, `verify_t5_maxcut_extension_unsat.py` — ambient
  maximum-cut extension exclusion of #264 and #298.
- `rebuild_t5_local_classifier_hit.py` — pins a printed graph6 support graph
  and reruns the archived engine's own circuit stage
  (`choose_minimal_circuit`, imported from `rooted_t5_support_cp_sat.py`) at
  the recorded (owner, active) pair; used to regenerate both circuit hits.
- `check_t5_active_scope_profile.py` — CP-SAT all-row dead-owner gate
  (copied verbatim from the source archive).

The regenerated t = 5 certificate artifacts are shipped in `t5_artifacts/`
(regeneration record: `t5_artifacts/NOTES_t5_regeneration.md`). The twelve
split-infeasibility certificates regenerate bit-exactly to the canonical
hashes cited in the paper; the circuit-level artifacts were rebuilt on the
two printed support graphs at the recorded (v, x0) pairs with identical
verdicts. The #298 ambient extension chain (rebuilt hit, primary extension
run, independent SAT replay, `PASS_ALL_EIGHT_SPLITS_UNSAT`) is in
`t5_artifacts/298_extension/` with its own `NOTES.md`. The paper's printed
prefixes are prefixes of each artifact's embedded `canonicalSha256` payload
hash, not of the file bytes; `SHA256SUMS` lists whole-file hashes.

## Lean modules (`lean/`)

Production sources of the Lean 4 development `Erdos23Delta0` cited by the
paper, included verbatim for hash comparison:
`SingletonPairSigma.lean`, `CutTightStarPigeonhole.lean`,
`R43SupportIncidence.lean`, `BadStarCoverFreeness.lean`,
`K33BadStarPairCountZero.lean`, `CutTightActiveRotorIncidence.lean`,
`SaturatedRotorSupportPersistence.lean`, `R44K2TailOverlap.lean`,
`LiveMiddleSwapCrossOuter.lean`.
These files import the surrounding development (in particular
`Erdos23Delta0.CertGraph`) and are not buildable stand-alone from this
directory; their SHA-256 hashes match the values printed in the paper.

## Lean axiom probe (`lean_axiom_probe/`)

Fresh rebuild-and-probe record (2026-07-17) for
`LiveMiddleSwapCrossOuter.lean`: `rebuild_and_probe.ps1` compiles the
five-module import chain out-of-tree against a formal-conjectures Mathlib
olean cache (Lean 4.27.0) and runs the kernel `#print axioms` probe
(`probe_live_middle_swap.lean`). Result: axioms exactly
`[propext, Quot.sound]`, verdict `PASS_AXIOM_PROBE`; full transcript in
`probe_transcript_2026-07-17.txt`. Requires a formal-conjectures checkout
with its Mathlib olean cache; not runnable from this directory alone.
