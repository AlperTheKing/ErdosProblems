# GPT Pro — close the EXTREMAL high-p band-top (the genuine Step-1 wall)

STEP-1 FINITE ONLY (a(30)<=36). Setup: K=2,T=2 reroot; roots x,y; |C|=2 (c1,c2); A=N(x)\C (a),
B=N(y)\C (b), R=residual (q vtx, labels E/S1/S2/D); U=|S1|+|S2|+2|D|; p=#(A,B), M=#(A∪B,R),
e_R=#(R-internal); e=30-q+U+e_R+p+M; beta>=37; e in [112,143].

The U3(empty) cut p+e_R>=37 (beta<=p+e_R) closes all low-p cells. The REAL remaining obligations are
HIGH p, at the BAND TOP e=143: e.g. idx101 (0,2,2,7) a7b8 (forced K_{2,2} skeleton, e_R=4, D isolated),
e=143 => p+M=102; cells p=33..36 (M=69..66). These are EXTREMAL dense triangle-free graphs (e=143,
beta=37, just above 30^2/25=36).

STATUS of these extremal cells (closed by NEITHER tool):
(i) full second-shadow quotient (WBCL max-deg Delta<=11 at e=143, col-imbalance / full U3(W) family,
    degree-histograms with v_rjk consistency, 2nd-moment cuts) is FEASIBLE on them;
(ii) the exact 889-state CP-SAT state-count (quotient-cut-rounds=4, 32 workers) returns UNKNOWN after
    1812s (base solve doesn't even finish).

QUESTION: how to close these extremal high-p band-top cells? Assess:
(a) STABILITY: the extremal e=143 beta>=37 triangle-free graphs are near a known extremal structure
    (C5-blowup / Clebsch / near-bipartite); a stability/robustness argument excluding beta>=37 just
    above 36. Give the explicit inequality.
(b) Better/smaller EXACT ENCODING the CP-SAT can solve (889 states too big); a reduced band-top formulation.
(c) A new structural cut specific to the dense regime e in [140,143].
(d) Is this cell genuinely as hard as the full n^2/25 conjecture (fundamental obstruction), or finitely closable?
Give the explicit cut/argument/encoding; flag rigorous vs heuristic. Step-1 finite only.
