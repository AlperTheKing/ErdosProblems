# Workflow (12-agent) synthesis on the P5-chord lemma -- corroborates GPT + adds electrical-flow lead

STATUS: reduced to one clean sub-claim (the SHARP CONGESTION / COAREA LEMMA = GPT's (Sync)).

PROVED (citable):
 (L1) BLOCK CASE: M = one complete-bipartite block U x V, 5 pairwise-disjoint shells U,A,W,D,V. The four
   CD flips give q<=a, p<=d, pq<=aw, pq<=dw; disjointness gives N>=p+q+a+w+d; AM-GM case-split on w yields
   N>=5 sqrt(pq) => pq=|M|<=N^2/25. Sharp at C5[n] (C5[2]: N=10, |M|=4=N^2/25, all d_B=4). [matches GPT]
 (L2) Integrated CD / coarea: for all f:V->R, sum_{uv in M}|f(u)-f(v)| <= sum_{uv in B}|f(u)-f(v)|
   (layer-cake of CD; no alignment). But LINEAR -> only 4|M|<=|B|; CANNOT reach 25|M|<=N^2. [= GPT's coarea gap]

THE GAP (block -> general), sharpened:
 - The block step N>=p+q+|A|+|W|+|D| needs the 5 layers GLOBALLY pairwise-disjoint <=> a graph hom G->C5.
   Triangle-free + CD + all-d_B=4 do NOT supply one: Petersen and an odd-cycle bad graph M are CD-valid,
   all-distance-4, triangle-free, yet have NO C5-hom. Non-block instances are the MAJORITY (5123 vs 3567
   block at N=10). Naive per-block summing double-counts shared vertices and is FALSE.
 - Every SCALAR foliation (single potential f) is provably linear (4|M|<=|B|) -- the dead ceiling.
 - The quadratic constant 25 needs a sharp CONGESTION/coarea estimate: a canonical fractional B-routing of
   the |M| bad demands + a dual potential whose sublevel sets feed CD + no congestion exceeds CD's per-level
   capacity, reproducing 25 WITHOUT alignment.

CONCRETE NEXT ACTION (Workflow, conf 0.82) -- electrical-flow / multicommodity LP-duality, NOT single coarea:
 (1) each bad edge's demand = a unit ELECTRICAL CURRENT in B between its endpoints (split over all length-4
     geodesics / electrical flow);
 (2) bound total energy / congestion by N using CD applied to the level sets of the ELECTRICAL POTENTIAL
     (NOT the integer BFS-distance potential, which is the proven-too-weak L2);
 (3) NUMERICALLY TEST on the two witnesses (odd-cycle bad-M, Petersen) that the electrical-potential level
     sets give a per-level CD margin >= the routed congestion, BEFORE the general proof. If it fails there,
     that pins the next obstruction precisely.
Lean-ready: NO (the gap is genuine open math).
