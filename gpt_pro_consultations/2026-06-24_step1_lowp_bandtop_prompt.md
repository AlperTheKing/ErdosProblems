# GPT Pro — Step-1: cut for the LOW-p / HIGH-M band-top (the remaining quotient gap)

STEP-1 FINITE ONLY (a(30)<=36; do NOT address all-n). Setup: K=2,T=2 reroot; roots x,y; |C|=2 common
nbrs c1,c2; A=N(x)\C (|A|=a), B=N(y)\C (|B|=b), R=residual (q vtx, labels E/S1/S2/D); U=|S1|+|S2|+2|D|;
p=#(A,B edges), M=#(A∪B, R edges), e_R=#(R-internal edges); e=30-q+U+e_R+p+M; beta>=37; e in [112,143].

Your second-shadow quotient — col-imbalance cut (40), A/B degree-histograms with v_rjk consistency
(33-35), WBCL max-degree (Delta<=11 at e=143), 2nd-moment cuts (36-38) — is IMPLEMENTED and verified
SOUND (I re-derived (40): 70=2*37-4; audited WBCL via blow-up density margin). It CLOSES the band-top
(e=140-143) cells with HIGH p: e.g. idx100 (0,2,2,7) a6b9, e=143, p=33..36 all INFEASIBLE in 0.02s
(these had timed out the 889-state CP-SAT at 1200s).

PROBLEM: the quotient leaves OPEN the band-top cells with LOW p / HIGH M. Example: idx101 (0,2,2,7)
a7b8 (forced skeleton R[S1,S2]=K_{2,2}, e_R=4, D isolated), e=143 => p+M=102; the cells p=4..11
(M=98..91) remain FEASIBLE in the full quotient (~31 open cells per e across e=140..143). These are
dense in A/B-R incidences (M~93 spread over q=11 R-vertices, so R-degrees near the cap 11) with FEW
A-B edges (p small). Intuitively a near-bipartite (A∪B | R)-dense graph.

QUESTION: what additional SOUND structural cut closes the LOW-p / HIGH-M band-top cells? Assess:
(i) class-weight 37-knapsack separator (a.6) — does a weighting exist whose Q_37>1/25 forces W>rho for these cells?
(ii) the A-A / B-B codegree 2nd-moment cuts (37)(38) sharpened with the histogram at high M;
(iii) a WBCL weighting concentrating mass on R (since R-degrees are near the cap and M is large);
(iv) an independent-set cut using A∪{y} or B∪{x} (size a+1, b+1) or D plus disjoint A/B;
(v) a cut on the A/B-R bipartite incidence structure when M is near maximal.
Give the EXPLICIT inequality that closes low-p/high-M band-top, rigorous vs heuristic. Step-1 finite only.
