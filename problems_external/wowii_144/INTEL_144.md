# INTEL PACKET — WOWII Conjecture 144 (2026-07-18, post-recon)

## Target statement (FC-faithful)

For every finite simple **connected** graph `G` (n ≥ 2):

    tree(G) ≥ girth(G) − 1 + e(G)        (over ℝ; girth = 0 if acyclic)

where
- `tree(G)` = `largestInducedTreeSize` = max number of vertices of an induced subgraph that is a tree,
- `girth(G)` = length of a shortest cycle, **0 if acyclic** (junk value),
- `C` = `G.center` = set of vertices of minimum eccentricity `r` (radius),
- `e := ecc G C` = max over v ∉ C of `distToSet v C` (= max_v d(v, C); 0 if C = V).

Lean skeleton `conjecture142/144 skeletons` (problems_external/wowii_142/wave1/skeletons.lean, compiled):
**everything is closed except ONE branch: G cyclic and e ≥ 1.** That branch is THE task.

Useful elementary facts (all proved in the skeleton/API already, may be assumed):
- T1: t ≥ dist(u,v) + 1 for all u,v (geodesics induce trees); hence t ≥ D+1 (D = diam) and t ≥ r+1.
- T2: G cyclic ⟹ t ≥ g − 1 (shortest cycle minus a vertex).
- T3: every shortest cycle K is **chordless** and **isometric** (arcs of length ≤ ⌊g/2⌋ are geodesics).
- e ≤ r  (d(v,C) ≤ d(v,c₀) ≤ ecc(c₀) = r).
- If e ≥ 1 then C ≠ V, so some vertex has ecc ≥ r+1, so D ≥ r+1.

## Accepted tool: Lemma M (rigorous, easy — may be used freely)

For a shortest cycle K, define

    M(K) := max |F| : F ⊆ V∖V(K), G[F] is a forest, and ∃ z ∈ K such that
            EVERY connected component of G[F] sends EXACTLY ONE edge into K∖{z}
            (edges counted with multiplicity over pairs; edges into z itself are UNRESTRICTED,
             since z gets deleted; each component must have ≥ 1 edge into K∖{z}).

**Lemma M.** t ≥ (g − 1) + M(K) for every shortest cycle K.
*Proof.* K is chordless (T3), so G[K∖{z}] is an induced path with g−1 vertices and g−2 edges.
Components of the induced forest G[F] are pairwise non-adjacent; each attaches to the path by
exactly one edge. Vertex count (g−1)+|F|, edge count (g−2)+(|F|−c)+c = (g−1+|F|)−1, connected ⟹ tree. ∎

Exact reference implementation of M(K): `problems_external/wowii_144/wave2/lemma_e_tests.py` (`M_of_cycle`).

## THE open lemma (the whole remaining math of C144)

**Lemma E (exists-form).** G connected, cyclic, e ≥ 1 ⟹ **there exists** a shortest cycle K with e ≤ M(K).

Numeric status (exact arithmetic, seed 20260718):
- `E_exists`: **0 violations / 8219 graphs, min slack 0** (atlas n≤7 exhaustive + families + random + adversarial + traps + forced-girth; n − g ≤ 17). File: wave2/lemma_e_results.json.
- `E_forall` (min over K): TRUE on all tested graphs with **g ≥ 4**; **FALSE at g = 3** (F~AGO, n=7, e=2, M_min=0). So at g=3 the CHOICE of K matters.

## Verified-true auxiliary targets (tested, unproved — usable if you prove them)

- **P2 / Lemma A**: t ≥ D + ⌈g/2⌉ − 1 (equivalently t ≥ g−1+D−⌊g/2⌋). 0 violations / 12356+13455 graphs, min slack 0.
  If you prove P2, then the subcase e ≤ D − ⌊g/2⌋ of C144 closes via P2; only e > D − ⌊g/2⌋ remains for the M-route.
- Class-P proof of Lemma E (G = cycle + pendant trees) exists and its steps S1–S8 were mechanically
  verified on 4000 random class-P graphs: `wave2/verify_classP_proof.py` (READ ITS DOCSTRING — it is the
  core intuition: same-tree case; deep-tree case D_{T_c} ≥ r+1; c-on-K case with e = h_x + δ0, a window of
  2δ0−1 noncentral cycle positions, per-position witness trees with d_K(σ,ρ_j) ≥ r+1−D_j ("tent"), capacity
  count forcing Σ D_j ≥ δ0 over any cover).

## FALSIFIED — do NOT re-derive, do NOT silently "fix" (exact counterexamples on file)

- L3: e ≤ max(max_K max_x d(x,K), D − ⌊g/2⌋) — FALSE, min slack −4 (trapCascade, g=18). Deep single
  branches do NOT dominate e; multi-component witness families are genuinely needed.
- Single-tail CT (t ≥ g−1+d(x,K)) — FALSE at g=3 AND g=4 (double attachment; antipodal pair at g=4).
  Valid only for g ≥ 5.
- e ≤ Σ-branch-heights pure (no diam branch) — FALSE (girth-5 witness MA?OQO@@@CocOC?`?, e=3, σ=2).
- At g=4: e ≤ max(D−2, σ) — FALSE (7 CEs, e.g. FhELO n=7 D=3 e=2 σ=1). The g=4 endgame needs care:
  a g=4 component may attach to an ANTIPODAL PAIR of K; z-choice can kill one pair {0,2} but not both
  pairs {0,2},{1,3} simultaneously — handle multi-attach components explicitly.
  Tested-true g=4 candidates: "t = D+1 ⟹ e ≤ D−2" (T3plus, 0 viol) — but as a route this needs a
  companion for t ≥ D+2. E_exists itself is clean at g=4 (0 viol), and even E_forall holds at g≥4.
- At g=3: if a tail's last vertex q is adjacent to ≥ 2 triangle vertices, {q} ∪ (2 adjacent K-vertices)
  is ANOTHER shortest triangle — switching K is the standard repair at g=3.

## NEW (2026-07-18 late): σ*-distillation FALSIFIED — multi-tail-per-component is ESSENTIAL

The "one geodesic stem per branch component" distillation σ* (sum of branch heights, drop the smallest
when k ≥ g) is FALSE as an upper bound for e: graph6 `J?LcCHOC`C?` (n=11, g=6, D=4, r=3, e=3) has
σ* = 2 on every shortest cycle but M(K) = 4 on ALL THREE shortest cycles (E_exists holds with slack 1;
verified exactly 2026-07-18). Consequence for any general proof: the witness forest may need TWO OR MORE
tails drawn from the SAME component of G − K (attached at different K-positions); a per-component
"one stem" accounting CANNOT work. Any referee should test candidate proofs against this graph.
Also: class-P proof steps re-verified this session: 3342 class-P graphs with e ≥ 1, 0 failures.

## Sharp/tight instances the proof must respect (slack 0 in E_exists)

- C_g + path of length L ≤ ⌊g/2⌋ attached: e = L, M = L.
- cycleLegs(g; three legs of length 2 spread out), g = 10, 11: e = 5, r = 5, window arguments tight.
- Bipartite girth-4 blocks (FhELO-family): e = 2 achieved with M = 2 only via the right K / right F.

## Deliverable

A COMPLETE, rigorous, self-contained proof of **Lemma E (exists-form)** for all finite connected cyclic
graphs — every case (g=3, g=4, g≥5) closed, no "similarly", no unproved sub-bridges. If your route instead
proves C144's hard branch directly by another decomposition (e.g. P2 + partial-E), prove EVERY piece.
State every definition you use precisely (especially d_K, branch components of G−K, heights, witness sets).
The proof will next be formalized in Lean 4/Mathlib — prefer explicit constructions and exact counting over
compactness/extremal-choice arguments where possible; flag the steps you expect to be hardest in Lean.

Python env for any sanity checks you want to run: `python` (3.12, networkx installed);
exact bitmask invariant library: problems_external/wowii_141/oracle/invariants.py
(nx_to_bitadj, girth, all_pairs_dist, eccentricities, ecc_of_set, largest_induced_tree, dist_to_set).
Keep any runs ≤ 8 threads. Write scratch scripts to your own subfolder under problems_external/wowii_144/.
