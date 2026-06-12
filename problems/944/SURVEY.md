# Erdős #944 — SURVEY / FRONTIER (2026-06-10)
- Dirac 1970 conjecture (r=1): k-vertex-critical graphs with no critical edge exist for all k ≥ 4.
- Brown 1992 [Br92, "A vertex critical graph without critical edges", Discrete Math]: k=5 example.
- Lattanzio 2002 [La02]: all k with k−1 composite. Jensen 2002 [Je02]: alternative construction, all k ≥ 5.
- Martinsson–Steiner 2023/25 [arXiv:2310.12891, CPC]: for every r, all sufficiently large k (partial
  answer to Erdős's all-r form).
- Skottova–Steiner 2025 [arXiv:2508.08703]: all k ≥ 5, all r; quantitative: (1/k)n^{1/3} ≪ f_k(n) ≪
  n/(log n)^c for k ≥ 5 (page comment by Zach Hunter refines constants). Methods: modification of
  Jensen's construction + gluing operation. Abstract states k=4 remains open (all r).
- THE FRONTIER: k=4 entirely open (even r=1). 55 years, all known construction machinery (Brown/
  Lattanzio/Jensen/MaSt/SkSt) fails at k=4. No computational search results located anywhere
  (papers, page, forum — forum has only a constants comment).
- Novelty target: an explicit 4-vertex-critical graph with no critical edge (finite, Lean-checkable
  certificate ⟹ full resolution of the last Dirac case, strong even as "special case explicitly
  noted as open"), OR a nonexistence proof, OR (fallback partial) a verified exhaustive lower bound
  "no such graph on ≤ N vertices" with structural analysis.
- Scoop watch: Steiner's group active (2025); re-scan every ~10 iterations.

## Novelty sweep update (2026-06-10 late)

- Erdős Problems #944 page still lists the problem as OPEN, says the case `k=4,r=1` remains open, and
  records no partial or complete solution in comments.
- Skottova-Steiner 2025 arXiv:2508.08703 states that Dirac/Erdős remains open only for `k=4`, proves the
  broad problem for `k >= 5`, and in Section 5 asks Problem 5.2: whether a 6-regular `(4,1)` graph exists.
- Their Proposition 5.1 contains the general random-permutation lower edge-connectivity argument; the broad
  `|delta(S)| >= 6` fact is therefore KNOWN and must be cited, not claimed as new.
- Web searches found no prior small-order enumeration for 6-regular `(4,1)` graphs, no published unique
  `n=13` 6-regular 4-vertex-critical graph statement, and no occurrence of the exact Kempe-tether/small
  6-cut shore package:
  `"6-regular" "(4,1)-graph"`, `"6-regular" "4-vertex-critical"`, `"Kempe chain" "vertex-critical"
  "critical edge"`, `"6-edge-cut" "vertex-critical" "critical edge"`.
- Current novelty posture: the package is plausibly new as a secondary contribution, but final PR requires
  one more citation-graph / problem-history sweep immediately before submission.

## Structural facts (derived, T1)
1. Any edge-minimal 4-chromatic subgraph H of a 4-vertex-critical G spans G's vertex set (else
   χ(G−v) = 4 for uncovered v). Hence G = H(spanning 4-edge-critical) ∪ S (extra edges).
2. Every e ∈ S is automatically non-critical (G−e ⊇ H keeps χ=4). Only edges of H need
   de-criticalizing: ∀e ∈ E(H): (H−e) ∪ S must be 4-chromatic.
3. Vertex condition: ∀v: (H ∪ S) − v 3-colorable (adding S can break H's vertex-criticality).
4. δ(G) ≥ 3; G connected; |E| moderate (4-chromatic on n vertices).

## Attack vectors
A. Catalog+CEGAR: enumerate 4-edge-critical H (small n; generate with SMS/geng+filters or known
   catalogs), then search S ⊆ co-edges: SAT side = per-vertex 3-colorings of (H∪S)−v (polynomial
   witnesses); coNP side = ∀e∈H: (H−e)∪S not 3-colorable, handled by CEGAR with blocking clauses
   from violating colorings. Outcome: example (resolution!) or exhaustive small-n nonexistence.
B. Understand WHY constructions fail at k=4 (fetch full texts of Je02/SkSt25 §k=4 remarks; GPT
   consult) → adapt or prove an obstruction (possible NO-direction theorem for k=4).
C. Local search/SA over (H, S) at larger n guided by patterns from A.
