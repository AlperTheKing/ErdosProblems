# Erdős #944 — STATEMENT (restricted target: Dirac k=4)
Source: erdosproblems.com/944 [Er89e]; Dirac 1970. Status: open; the ONLY remaining case is k=4
(all r). Formalised statement exists in formal-conjectures.

Full problem: for k ≥ 4, r ≥ 1, must there exist a graph G with χ(G) = k such that every vertex is
critical (χ(G−v) = k−1 for all v) yet every critical set of edges has size > r (χ(G−R) = k for all
R ⊆ E(G), |R| ≤ r)?

ACTIVE TARGET (the open case, r = 1, k = 4): does there exist a 4-chromatic graph G with
  (V) χ(G−v) = 3 for every vertex v (4-vertex-critical), and
  (E) χ(G−e) = 4 for every edge e (no critical edge)?
Either an explicit example (finite certificate: graph + per-vertex 3-colorings + non-3-colorability
of G and all G−e) or a nonexistence proof resolves the last case of Dirac's 1970 conjecture.

Quantifier notes: simple graphs; χ(G)=4 means not 3-colorable but 4-colorable; vertex-criticality
forces connectivity and δ(G) ≥ 3. k=4, r≥2 would follow from f_4(n) questions but r=1 is the gate.
