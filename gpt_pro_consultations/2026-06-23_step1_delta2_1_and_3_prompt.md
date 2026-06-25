# GPT Pro follow-up — Step-1 a(30)<=36: establish delta(G)>=8 in the delta_2=1 and delta_2=3 branches

STEP-1 FINITE ONLY (a(30)<=36; do NOT address all-n). Continuation of the r=4,5,6,7 / delta>=8 analysis.

Setup: medium window 112<=e(G)<=143, beta(G)>=37, G triangle-free on 30 vtx, WLOG edge-maximal.
The proof roots at a MINIMUM nonedge-codegree pair, splitting by
  delta_2(G) := min over nonedges xy of |N(x) ∩ N(y)|.
- delta_2 >= 4 => G homomorphic to C5 => beta small => done.
- so delta_2 in {1,2,3}; each branch then enumerates min-degree root r0 in {8,9}.
Hence delta(G) >= 8 (ruling out min-degree r=4,5,6,7) must hold in EACH branch delta_2 in {1,2,3}.

Already done (delta_2 = 2): root at a min-degree vertex v, A=N(v), B=V\N[v], state S_x=N(x)∩A.
Since every nonedge has codeg>=2, |S_x|>=2; then r=4 => beta<=25, r=5 => beta<=33 (both <37),
and r=6,7 reduce to a small exact cut-certificate. These crucially used |S_x|>=2.

QUESTION — handle the other two branches rigorously:

(1) delta_2 = 3: every nonedge has codeg >= 3, so |S_x| >= 3 for x in B.
    Does this make r=4,5,6,7 EASIER? (e.g. r=4: only states of size 3 or 4; a size-3 state has a
    unique disjoint... etc.) Give the explicit bounds / show delta>=8 follows, or identify the hard case.

(2) delta_2 = 1: some nonedge has codeg exactly 1. The min-degree vertex v (deg r in {4,5,6,7}) MAY
    have a non-neighbor x with codeg(v,x)=1, giving |S_x|=1, so the |S_x|>=2 argument fails.
    Close r=4,5,6,7 here. Assess: (a) is "the minimum-degree vertex has minimum-codegree >= 2 with all
    its non-neighbors" forceable (so the delta_2=2 lemma applies to v regardless of global delta_2)?
    (b) root instead at the codeg-1 nonedge and argue there; (c) a separate finite certificate.

Give the cleanest RIGOROUS route to establish delta(G)>=8 in BOTH delta_2=1 and delta_2=3 (or show one
is trivial). Flag every step as rigorous vs heuristic. Keep it Step-1 finite.
