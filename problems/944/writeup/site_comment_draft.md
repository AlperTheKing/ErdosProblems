# erdosproblems.com #944 sayfa yorumu — GÖNDERİME HAZIR (arXiv:2606.18462)

Some verified computational and structural progress on the 6-regular case isolated by
Skottova and Steiner (arXiv:2508.08703, Problem 5.2):

(1) There is no 6-regular 4-vertex-critical graph on n ≤ 15 vertices, except a unique
one (up to isomorphism) on n = 13 (graph6 L?bFFbw~B{FwFw) whose 13 critical edges form a
Hamilton cycle. Hence any 6-regular (4,1)-graph has at least 16 vertices. (Exhaustive
nauty/geng enumeration with generator-side completeness guards; the n=14 and n=15 totals
match the known counts of 6-regular graphs.)

(2) In any 6-regular (4,1)-graph, every 6-edge-cut is either the edge star of a vertex or
has both shores of size ≥ 15; consequently every such graph on ≤ 29 vertices is
super-6-edge-connected. The proof combines an exact classification of the 6-cut matrices
(21 matrices, 5 types up to row/column permutation) with a "boundary-shortfall" lemma;
the only near-miss shore is K_{3,3,3} minus a rainbow 3-matching, excluded by the
shortfall lemma.

(3) No shore of a nontrivial 6-edge-cut in a 6-regular (4,1)-graph induces a bipartite
graph; more generally, a shore whose deficiency is concentrated on two vertices forces
them to receive equal colours in every proper 3-colouring. (This is sharp: the incidence
graph of PG(2,5) gives deficiency-6 candidates that pass all the one-sided counting
filters.)

These do not resolve Problem 5.2 — a target could still be a super-6-edge-connected
6-regular graph on n ≥ 16 — but they pin down the small-order behaviour exactly. Full
details, code, certificates, and machine-checked (Lean 4 / Mathlib) cores of the key
lemmas: arXiv:2606.18462 (https://arxiv.org/abs/2606.18462). Lean cores are also at
google-deepmind/formal-conjectures PR #4237.
