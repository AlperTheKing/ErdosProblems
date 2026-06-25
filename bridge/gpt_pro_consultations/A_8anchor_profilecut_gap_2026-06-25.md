# GPT Pro path (A) to close Step-2: the ORDER-10 EIGHT-ANCHOR PROFILE-CUT GAP on the witness

chat 6a3b5aba. User overrode (c)-stop -> push to closure. GPT picks (A): diagnose the separating constraint from
the exact witness via an 8-anchor (k=8) local cutting rule -- "the first objective-specific order-10 constraint
the new q actually makes available" (the order-9 cert used k<=7 profile cuts; k=7 already cut the gap ~150x).

## Construction
Witness q = order-10 extension distribution (12172 tri-free 10-vertex graphs), d_mono claim m* = 2/25 + 6.0e-5.
For a sign rule sigma_R : 2^[8] -> {-1,+1} (per 8-vertex root graph R), the monochromatic-edge density of J:
  c_sigma(J) = (1/10!) sum_{pi in S10} 1{pi(9)pi(10) in E(J)} * 1{ sigma_{R_pi}(A_pi) = sigma_{R_pi}(B_pi) }
where R_pi = graph induced by the first 8 permuted vertices, A_pi=N(pi9) cap [8], B_pi=N(pi10) cap [8] are the two
profiles. (Leave-2-out: for each ordered edge (i,j) of J, the OTHER 8 vertices are the anchors R=J-{i,j};
i,j get sides sigma_R(prof_i), sigma_R(prof_j); the edge is monochromatic iff those signs agree.)
NOTE: w_R(A,B) = 0 unless A,B are INDEPENDENT in R and A cap B = empty (triangle-free forces this).

U_8(q) = min_sigma  sum_J q_J c_sigma(J).  Per canonical R this DECOUPLES into a MaxCut on R's PROFILE GRAPH
(nodes = profiles A = independent sets of R; edge {A,B} weight w_R(A,B) = q-weight of edges with that anchor-graph
R and profiles A,B; self-loops A=B are ALWAYS monochromatic): min monochromatic_R = totalweight_R - MaxCut_R.
U_8(q) = sum_R min_monochromatic_R, in edge-density units (same as m*: both are e - cut).

## What to test FIRST
Delta_8(q) = m* - U_8(q).
 - Delta_8 > 0  => witness VIOLATES the valid graphon inequality d_mono <= U_8. Extract the minimizing sigma_R,
   add it as an exact cut, reoptimize eta, repeat (cutting-plane loop).
 - U_8(q) <= 2/25  => the FIRST cut already eliminates the witness at the threshold => band CLOSES.
 - Delta_8 <= 0  => witness survives every 8-anchor cut; next = 9 anchors (selective 10->11 marginal lift, not a
   full order-11 SDP).

## MY IMPLEMENTATION PLAN (compute_U8.py)
1. Load witness.npz (q over T_10). For each J with q_J>0, each ORDERED edge (i,j): R=J-{i,j} (8 vtx); CANONICAL-
   relabel R; map A=prof_i,B=prof_j to canonical anchor coords; accumulate w_R(A,B) += q_J/(10*9).
2. Per canonical R: build profile graph; MaxCut (exact small / good heuristic for an UPPER bound on monochromatic
   = valid cut). For a VALID violation test the sigma must be SHARED across all J with the same R (graphon cut) =>
   canonicalization is REQUIRED (per-J-optimal under-estimates U_8). monochromatic_R = total - MaxCut_R.
3. U_8 = sum_R monochromatic_R (edge-density units; sanity: t(K2,q)=sum q_J*orderededges/90 must match x@dedge~0.297).
4. Delta_8 = m* - U_8; compare U_8 to 2/25.
AUDIT: any closure (U_8<=2/25) needs the EXACT rational U_8 (exact MaxCut) + the cut verified valid for ALL real
band graphons (brute tri-free n<=12), per all-or-nothing + 8 false closures averted. A heuristic cut beating m*
is a SUFFICIENT (one-sided) confirmation of Delta_8>0 (U_8 <= heuristic_monochromatic < m*).
