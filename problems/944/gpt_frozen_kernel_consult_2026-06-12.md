# Consult sent 2026-06-12 to thread "Cold Review Adversarial Analysis" (c/6a29bd3c)

FROZEN-VERTEX KERNEL, proof round. Self-contained recap, then the sub-goal.

Definitions. R a finite connected simple graph, properly 3-colourable. For v in V(R)
with deg(v)=6, call v UNFROZEN if R-v admits a proper 3-colouring giving the six
neighbours of v the colour counts exactly (2,2,2); otherwise v is FROZEN. For the
shore application: H is a candidate shore of a 6-edge-cut in a 6-regular (4,1)-graph,
so H is connected, 3-colourable, max degree 6, and the total degree deficiency is
sum_v b(v) = 6 where b(v) = 6 - deg_H(v). Our filter [K] (boundary-shortfall, referee-
validated) requires: for EVERY v, some proper 3-colouring psi of H-v has
sum_i max(0, 2-cnt_i(psi, N_H(v))) <= b(v). For a full-degree vertex (b=0) this says
exactly: v is unfrozen.

Status you helped establish (all machine-verified by us):
- "unfrozen <= C" is FALSE: your 15-vertex B (6-regular, 3-colourable, lambda>=4,
  exactly one unfrozen vertex v=10) and the colour-compatible 2-edge-sum chain B^(m)
  with >= m unfrozen vertices. Mechanism: 2-edge cuts between blocks.
- Census n<=13 (all 50+849 connected 6-regular 3-colourable graphs): NO graph has all
  vertices unfrozen; max unfrozen = 2.
- Exhaustive shore searches: every candidate shore with 9 <= a <= 14 dies
  (119,236,283,370 candidates at a=14 alone, 0 survivors); the near-misses die
  exactly at [K], i.e. at a frozen full-degree vertex.
- Hence Theorem B: every 6-edge-cut in a 6-regular (4,1)-graph is a vertex star or
  has both shores >= 15; n <= 29 implies super-6-edge-connected.

THE SUB-GOAL (the single frontier lemma; would extend Theorem B to ALL shore sizes
at once and reduce Problem 5.2 to the star-cut endgame):

  (FK) Let H be connected, 3-colourable, max degree <= 6, with
       sum_{v in V(H)} (6 - deg_H(v)) = 6 and |V(H)| >= 9.
       Then H has a FROZEN vertex of degree 6.

Equivalently: H cannot have all its full-degree vertices unfrozen. Note B does NOT
contradict (FK): B has deficiency 0, not 6, and 14 of its 15 vertices are frozen.
The relevant frontier is deficiency exactly 6 with >= 9 vertices (sizes <= 8 are
excluded by your Turan-type counting; a <= 14 by exhaustive computation).

Questions, in order of value:
Q1. Prove (FK), or prove it under any additional hypothesis that exhaustive
    computation could plausibly discharge for small a (state the hypothesis
    precisely). Tools we trust: Kempe-component accounting in H-v (the parity
    6|K| = 2e(K) + m + t), discharging against the deficiency budget 6, the
    non-extendability of any (2,2,2) colouring at v, and the fact that an
    unfrozen vertex v needs a colouring of H-v in which all three colours hit
    N(v) twice -- a strong local symmetry.
Q2. If you cannot prove (FK), construct a counterexample candidate SHAPE (not
    necessarily explicit): what would a deficiency-6 graph with ALL full-degree
    vertices unfrozen have to look like? We will machine-search the shape at
    a = 15..18. Your B^(m) trick does not apply directly (it produces unfrozen
    vertices but also 2-edge cuts; a shore of a 6-regular (4,1)-graph inherits
    edge-connectivity constraints from lambda >= 6 of G -- you may assume H is
    2-edge-connected, and the 6-edge-connected variant is also of interest).
Q3. Name a FINITE certificate notion: a computer-checkable condition C(a_0) such
    that [C(a_0) verified by enumeration up to a_0] + [a clean induction/charge
    argument] => (FK) for all a. This is how we would close the gap rigorously.

Honest constraints: do not assume vertex-criticality of H (shores are not vertex-
critical); do not use [C]-type restrictions on colourings of H-v (we proved that
gap is real: H0 prism-blow-up is [C]-compliant yet all 12 vertices [K]-fail).
Answer with full proofs or explicit shapes; we audit line by line.
