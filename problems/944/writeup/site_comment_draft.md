# erdosproblems.com #944 sayfa yorumu — TASLAK (arXiv ID çıkınca [ARXIV] doldurulup gönderilecek)

Some verified computational and structural progress on the 6-regular case isolated by
Skottová–Steiner (arXiv:2508.08703, Problem 5.2):

(1) There is no 6-regular 4-vertex-critical graph on n ≤ 12 or n = 14 vertices; on
n = 13 there is exactly one (graph6 L?bFFbw~B{FwFw), and its 13 critical edges form a
Hamilton cycle. Hence any 6-regular (4,1)-graph has at least 15 vertices. (Exhaustive,
double-verified: nauty geng + two independent classifiers; the n=14 total 21,609,301
matches the known count of 6-regular graphs.)

(2) In any 6-regular (4,1)-graph, every 6-edge-cut is either a vertex star or has both
shores of size ≥ 14; consequently every such graph on ≤ 27 vertices is
super-6-edge-connected. The proof combines an exact classification of the 6-cut
matrices (21 matrices, 5 types) with a "boundary-shortfall" lemma; the only
near-miss shore is K_{3,3,3} minus a rainbow perfect matching, excluded by the
shortfall lemma.

Full details, code, certificates and machine-checked (Lean 4) cores: [ARXIV].
