# GPT Pro — Step-1 a(30)<=36: STRUCTURAL CUT INNOVATIONS to close the residual frontier (no brute force)

STEP-1 FINITE ONLY. Need structural cuts to close the residual instances WITHOUT brute force (brute = days/years).

Setup: triangle-free G on 30 vertices, beta=e-MaxCut>=37 (for contradiction); edge window 112<=e<=143. Rooted at an exact-codegree-2 nonedge (K=2,T=2): roots x,y; |C|=2 common neighbours c1,c2; A=N(x)\C, B=N(y)\C, R=residual; four R-labels E/S1/S2/D = adjacency pattern to (c1,c2). Reduced to 387 profile-side instances over q=|R|=6..14; each shown INFEASIBLE by an exact CP-SAT "state-count" solver (vars = A/B state-counts + edge aggregates; many cuts). q6-q10 CLOSED; **263 residual q11-q14**.

Cuts already in the solver (all sound): full Psi rooted cuts (2^q masks), U1/U2/U3 exact-two-root cuts, split-C (no-empty profiles), Exact open-neighbourhood E-cut (sum_{u in N(z)} deg(u) <= e-37 for empty-label z), projection PMC cuts, defect-block layer, side-sum degree cut, root-pair transposition (eliminates the codeg-0 dual idx344 ~4.2e9 tasks; idx360 self-dual).

TWO BLOCKERS:
1. BAND-TOP HARD ROWS: the densest (p,M) cells, e(G) near 143 (e.g. idx100 q11 S1S2D (0,2,2,7), p=33-35, M=66-69 => e~143). Base CP-SAT (states~889) does NOT decide within 1200s, so quotient separation never fires. Need a STRUCTURAL/scalar argument closing the high-density rows e in 140..143 directly. NOTE: BCL high-density gives e>=144 => beta<=36; e=143 is JUST below threshold.
2. BIG GRIDS, brute-infeasible: idx270 (E+S1+S2, ~5.07e8 tasks), idx232/233 (E+D, ~1.95e8 each), idx254 (pure S1+S2, ~2.93e8). Need cuts collapsing the skeleton/task count by orders of magnitude (as transposition did for idx344).

QUESTIONS:
(a) A structural/density cut for the BAND TOP (e=140..143): a refined density/stability argument (near-BCL-threshold density; dense triangle-free => near complete-bipartite-blowup structure) that closes the densest rows WITHOUT solving the full CP-SAT. Give the explicit inequality.
(b) NEW skeleton/quotient cuts to collapse the big E+S1+S2 (idx270), E+D (idx232/233), pure S1+S2 (idx254) grids by orders of magnitude beyond transposition + E-ND (extra symmetries, forced domination, stronger count-quotient, canonical R-skeleton reduction).
(c) A single UNIFORM structural reduction closing a LARGE fraction of the 263 residuals at once (not per-instance).

Give explicit inequalities/constructions; flag rigorous vs heuristic. Step-1 finite only.
