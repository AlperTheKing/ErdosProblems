# Audit - K2/T2 E+S1+S2 Residual Consultation

Date: 2026-06-23

Prompt:

`gpt_pro_consultations/2026-06-23_k2_es1s2_residual_prompt.md`

Submission:

The prompt was submitted through the in-app ChatGPT Pro Extended tab at
`https://chatgpt.com/c/6a3a2748-cf48-83ed-b332-91a58aaac9c7`.

Current response status:

At the last poll the page was still in `Stop answering` / `Pro thinking`
state.  No complete answer has been saved or trusted yet.

Residual profile-side instances:

```
idx  q   A  B  c0 c1 c2 c3  support
270  13  6  7  1  6  6  0   E+S1+S2
344  14  6  6  1  6  7  0   E+S1+S2
360  14  6  6  2  6  6  0   E+S1+S2
```

Scale evidence:

`search23/k2_es1s2_quotient_sample_scale_summary.tsv` estimates:

```
idx270: 507457309 tasks from 1000-base sample
idx344: 4188247113 tasks from 10-base sample
```

Independent audit before receiving Pro answer:

1. The E-neighbour rectangle condition is already present in the
   `E+S1+S2` generator.  `search23/estimate_k2_es1s2_raw.py` only enumerates
   empty-label states `(P,Q)` with `P x Q` disjoint from the fixed
   `S1-S2` graph, and `search23/make_k2_es1s2_labelg_quotient_skeletons.py`
   canonicalizes the resulting R-skeletons with `labelg`.

2. The old P-free master table does not close these instances.  Existing
   survivor rows in `search23/k2_pfree_master_results.tsv` are:

```
idx  p   eR  M   MA  MB  edges
270  37  17  58  27  31  141
344  25  25  53  17  36  132
360  26  24  58  16  42  136
```

3. Therefore a pure scalar/profile contradiction is unlikely with the current
   master constraints.  The next useful answer must add either a new skeleton
   filter, a stronger count-quotient cut, or a smaller exact branch
   decomposition before full task-grid materialization.

4. Do not use terminal-touch degree equality or C-tight endpoint degree
   equality.  H14 anti-tightness remains conditional and is disabled in the
   safe K2 reroot runs.

5. Root-colour visibility for A/B state types is already enforced in
   `search23/state_count_6195_cpsat.py`: `legal_states()` builds each root
   colour support and rejects every state with
   `popcount(state & support) < T-1`.  The active 64-worker batch invokes this
   Python verifier through `search23/run_state_count_6195_tasks_batch.exe`, so
   this is not a missing E+S1+S2 strengthening.

6. Added a new static P-free no-D split-C cut to
   `search23/verify_k2_pfree_master.py`, with proof note
   `search23/k2_es1s2_splitC_cut_note.md`.  It applies to `E+S1+S2`
   profiles by splitting the empty-label vertices across the two C-split
   patterns.  It has passed `python -m py_compile`; no CP-SAT closure run has
   been launched while the 64-worker idx96 batch is active.

7. Manifest re-check:

```
idx  q   A  B  c0 c1 c2 c3  support
270  13  6  7  1  6  6  0   E+S1+S2
344  14  6  6  1  6  7  0   E+S1+S2
360  14  6  6  2  6  6  0   E+S1+S2
```

The only visible incomplete Pro claim so far mentions a possible D=0
symmetry between idx270 and idx344 and self-duality of idx360.  This is not
accepted as evidence while the answer is incomplete: idx270 and idx344 have
different current root parameters (`q=13,A+B=13` versus `q=14,A+B=12`), so
any equivalence would need an explicit reroot map and invariant audit.

Completed answer:

`gpt_pro_consultations/2026-06-23_k2_es1s2_residual_answer.md`

Initial audit of the completed answer:

1. **Root-pair transposition.**  Pro proposes rerooting at the two original
   common neighbours `c1,c2` when `D=empty`, giving
   `(q,A,B;c0,c1,c2,0) -> (A+B+c0,c1,c2;c0,A,B,0)`.  This would map idx270 to
   idx344 and make idx360 self-dual.  This remains conditional until audited
   against the exact K2/T2 manifest semantics: the branch must be existential
   over exact-codegree-two root pairs and must not depend on a distinguished
   root-selection predicate or on an unaudited q14 closure.

2. **Open-neighbourhood cut.**  The lemma is safe:
   for every vertex `v`, triangle-freeness makes `N(v)` independent, so the
   cut `N(v) | V\\N(v)` leaves exactly
   `e(G) - sum_{u in N(v)} deg(u)` monochromatic edges.  Since `beta>=37`,
   `sum_{u in N(v)} deg(u) <= e(G)-37`.

3. **Projected ND8 cut.**  The cheap form `8 deg(v) <= e(G)-37` uses the
   already-audited current reduction `delta(G)>=8`.  In the active K2 runs
   this matches `--r0 8`, but the proof write-up must cite the minimum-degree
   reduction before using the projection.

4. **E-vertex specialization.**  For `z in E`, the projection gives
   `alpha_z + beta_z + d_R(z) <= 13`, hence
   `d_R(z) <= 9` because root-to-R side codegrees force
   `alpha_z,beta_z>=2`.  This looks like a strong skeleton/generator filter
   for idx270/344/360.  It is not yet implemented.

5. **Exact-E-ND quotient cut.**  Pro gives a linear count-quotient inequality
   summing the degrees of all neighbours of an empty-label vertex `z`.  This
   does not require the `delta>=8` projection and appears strictly safer.  A
   search of `state_count_6195_cpsat.py` found no existing `Exact-E-ND` style
   cut.  Do not patch that verifier while active idx96 PID `57764` is still
   spawning children from it.

6. **Implemented safe projected master cut.**  Added the projected ND8 cut to
   `search23/verify_k2_pfree_master.py`:

```
8 * (alpha[r] + beta[r] + dR[r] + label_size[r]) <= total_edges - 37
```

   for every R vertex.  This is a P-free necessary condition using the
   already-present minimum-degree-eight reduction in that master.  It passed
   `python -m py_compile search23/verify_k2_pfree_master.py`.  No CP-SAT solve
   was launched while the active 64-worker idx96 batch was running.

7. **D=0 root-pair transposition accepted at manifest level.**  The proof is
   recorded in `search23/k2_d0_root_transposition_note.md`.  The independent
   manifest audit

```
python search23/audit_k2_d0_transposition.py
```

   returns:

```
checked_d0_instances=8
failures=0
idx270->idx344
idx344->idx270
idx360->idx360
```

   Therefore idx344 is redundant with idx270 under the exact K2/T2 four-label
   manifest semantics, and idx360 is self-dual.  This does not close idx270 or
   idx360; it only removes a separate idx344 search once idx270 is closed.
