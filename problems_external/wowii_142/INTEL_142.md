# INTEL PACKET — WOWII Conjecture 142 (2026-07-18, post-recon)

## Target statement (FC-faithful)

For every finite simple **connected** graph `G` (n ≥ 2):

    tree(G) ≥ (2/3)·girth(G) + f(G)        (over ℝ; girth = 0 if acyclic)

where
- `tree(G)` = `largestInducedTreeSize` = max vertices of an induced tree,
- `girth(G)` = length of shortest cycle, **0 if acyclic**,
- `B` = `maxEccentricityVertices G` = periphery (vertices of maximum eccentricity = diameter D),
- `f := eccSet G B` = **max over ALL v** of `distToSet v B` (v ∈ B contributes 0).

Lean skeleton (problems_external/wowii_142/wave1/skeletons.lean, compiled): everything closed except
ONE branch: **G cyclic and f ≥ 1.** That branch is THE task.

Elementary facts already proved (usable):
- T1: t ≥ dist(u,v)+1; hence t ≥ D+1, t ≥ r+1.
- T2: cyclic ⟹ t ≥ g−1.
- T3: shortest cycles are chordless and isometric.
- f ≤ D (d(v,B) ≤ d(v,b₀) ≤ D for a diametral endpoint b₀ ∈ B).
- If d(b,w) = D = ecc(b) for some b, then ecc(w) = D too, so w ∈ B: BOTH ends of a diametral geodesic
  are peripheral. Hence f ≤ max_v d(v, {b, w}) for any diametral pair (b,w) — d to a 2-point subset of B.

## Accepted tool: Lemma M (rigorous — proof in ../wowii_144/INTEL_144.md)

M(K) := max |F|: F induced forest in G−V(K), ∃ z ∈ K, every component of G[F] sends exactly one edge
into K∖{z}. Then **t ≥ g−1+M(K)** for every shortest cycle K.

**Path-base variant (Lemma M-P, same one-line proof, no z needed):** for ANY induced path P
(e.g. a diametral geodesic), if F is an induced forest in G−V(P) whose every component sends exactly one
edge into P, then t ≥ |P| + |F| = D+1+M_P(P). This is rigorous — use it freely (but see Q4 falsifier below
for what canNOT be fed into it naively).

## Equality structure (exact oracle, 4665 graphs, 0 violations of C142)

113 equality cases (99 iso classes): **girth ∈ {3, 6} ONLY**, always t = f + 2g/3 (3 | g integrality is
real). Files: problems_external/wowii_142/oracle/{oracle142_results.json, equality_cases.json,
extremal_report.json}. Reverse-engineer these before proposing constants.

## FALSIFIED bridges — do NOT re-derive (counterexamples in oracle142_results.json / bridge files)

- Q3: ∃K,x: d(x,K) ≥ f − g/3 + 1 — FALSE (324 fails; min = bull graph Dx_).
- Q4 (naive double-tail): t ≥ D + 1 + max_x d(x, P) for a diametral geodesic P — FALSE at g=3,4
  (728 fails, all girth 3–4; already at Bw n=3). TRUE on all tested graphs with g ≥ 5.
  Failure mode: the tail's last vertex can attach to P at 2 close positions (triangle/C4), and at g≤4
  you cannot always prune to one edge without losing a vertex.
- Q5: d(x*, P_bw) ≥ (2/3)g + f − D − 1 — FALSE (79/124 fails).

## Facts from the 144 campaign you may combine (see ../wowii_144/INTEL_144.md for exact status)

- P2 (tested-true, UNPROVED): t ≥ D + ⌈g/2⌉ − 1 (0 viol / 25k+ graphs). If proved, then whenever
  f ≤ D − ⌈(2g/3 − g/2)⌉ + ... (do the arithmetic exactly) the bound closes; note (2/3)g − (⌈g/2⌉ − 1) =
  g/6 + 1-ish gap that f must cover.
- Lemma E (exists-form, 144's key: e ≤ max_K M(K), e = center-set eccentricity) — being proved in a
  parallel lane; if you want its statement as a black box, mark the dependency EXPLICITLY.

## Candidate routes (untested or partially tested — falsify FIRST, then prove)

1. Geodesic-base forest route: (2/3)g + f ≤ D + 1 + max_P M_P(P) over diametral geodesics P.
   (Rigorous consumer = Lemma M-P; the bridge itself must be oracle-tested before you invest.)
2. Cycle-base: (2/3)g + f ≤ g − 1 + max_K M(K), i.e. f ≤ g/3 − 1 + max_K M(K). Oracle-test.
3. Case split by comparing f with D and g: small-girth cases (g=3,4) may close from t ≥ D+1 alone
   plus integrality ((2/3)g + f ≤ D + 1 ⟺ f ≤ D + 1 − 2g/3; check exactly when this fails on the corpus
   — the failures are where real work lives).
4. Any completely different route — but every numeric claim must be exact-tested on the corpora below
   BEFORE being used (write a falsifier script; corpora generators: problems_external/wowii_141/oracle/
   sweep_families.py + wowii_144/wave2/route_b_tests.py have reusable generators).

## Deliverable

A COMPLETE rigorous proof of the hard branch (cyclic, f ≥ 1) of C142 — all girths, no unproved bridges;
each numeric bridge you introduce must come with an exact falsifier-test run (report the count and min
slack). Lean 4 formalization follows — prefer explicit constructions/counting; flag Lean-hard steps.

Python env: `python` (3.12, networkx); exact invariants: problems_external/wowii_141/oracle/invariants.py
(includes eccSet-faithful `ecc_of_set` and `dist_to_set`; `largest_induced_tree` exact ≤ 8 threads).
Write scratch to your own subfolder under problems_external/wowii_142/.
