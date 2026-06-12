# GPT Pro Digest: Domination/Synchronisation Follow-up

Date: 2026-06-11 Europe/Istanbul

Question:
prove or refute the reduced domination/synchronisation lemma for #944.  The
lemma would convert high third-colour multiplicity in a support-critical mate
Kempe component into either a comparable same-colour nonedge or a failure of
one of the required one-deletion terminal list-colourabilities.

GPT Pro verdict:

- No proof of the domination/synchronisation lemma.
- No genuine obstruction satisfying all target-level local conditions,
  especially the full condition:
  `H-y` is `L_x`-colourable for every terminal `x` and every `y in V(H)`.
- The remaining smaller target is a trace-domination lemma over the cut
  `(K,H-K)`.

Useful reductions:

- Parity tightening:
  if `K` is a two-colour Kempe component and
  `m = e_H(K,C)`, `t = |K cap N(v)|`, then
  `6|K| = 2e(K) + m + t`, so `m+t` is even.
  Therefore the bad thresholds are really:
  type `(1,1)`: `e_H(K,C) >= 6`;
  type `(2,2)`: `e_H(K,C) >= 4`.

- Trace formulation:
  for `W=H-K`, deletion `z in W`, and an exterior `L`-colouring `theta` of
  `W-z`, the trace list on `K` is
  `T_{theta,z}(u) = L(u) \ { theta(w) : w in N_H(u) cap (W-z) }`.
  Then `H-z` is `L`-colourable iff some exterior `theta` makes `K`
  colourable from this trace.

Proposed smaller lemma:

- Type `(1,1)` trace-domination:
  if `K` is support-critical for the two opposite terminal assignments and
  `e_H(K,C) >= 6`, then some `z in N_H(K) cap C` and one of those lists
  has every exterior trace uncolourable, hence `H-z` is not `L`-colourable.

- Type `(2,2)` trace-domination:
  if `K` is support-critical for all four relevant terminal assignments and
  `e_H(K,C) >= 4`, then some third-colour boundary deletion and one of those
  lists has every exterior trace uncolourable.

Verification of GPT's proposed 22-vertex diagnostic graph:

- Added verifier:
  `experiments/sixreg/verify_gpt_21_obstruction.cpp`.
- The supplied graph6 string is:
  ```text
  U@`d`z{A?C@O???FoIo?o?F`?BzGSa?uaSCWuo??
  ```
- Verified from graph6:
  `n=22`, all vertices degree `6`,
  `G` is not 3-colourable,
  `G-v` is 3-colourable,
  no edge deletion is 3-colourable,
  and the only 3-colourable vertex deletion is `v`.
- However, the detailed vertex-order/partition/list claims did **not** verify:
  under the claimed order, `H` is not tripartite in the displayed
  `A/B/C` partition;
  `L_a` is colourable on `H`;
  the claimed small `(A,B)` component is not recovered.
- Therefore the graph6 diagnostic cannot be used as a certified Kempe/list
  obstruction in the claimed labelled form.  Treat it only as evidence that
  6-regular 4-chromatic no-critical-edge non-vertex-critical graphs exist,
  not as proof of any support-to-multiplicity claim.

Status:

- No complete #944 proof.
- The remaining route requires a new trace-domination/synchronisation theorem.
- If no new idea for that theorem appears, #944 should be parked as hard.
