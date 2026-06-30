# GPT-Pro consult 2026-06-30 — the core anti-concentration: ROWSUM-O / <u_f,T> <= N

## Question sent

This is the single open inequality the whole problem (Erdos #23, delta=0) reduces to. I have proven the reduction
and validated the inequality exactly on ~190k triangle-free max-cut configs (census N<=11, blow-ups to N=49, the
N=22 sandwich-killer, Grotzsch, iterated Mycielskians to N=23, random to N=24, glued multi-component graphs).
I need the proof.

SETUP. G triangle-free, N vertices, a MAXIMUM cut; B = cut edges (connected bipartite), M = bad (monochromatic)
edges, beta=|M|. Triangle-free + max cut => each bad edge f=(a,b) closes an odd cycle of length ell(f)=d_B(a,b)+1
>= 5 (d_B = distance in B). For a bad edge f, p_f(v) = fraction of shortest a-b B-geodesics through v (so
p_f(v) in [0,1], sum_v p_f(v)=ell(f)). P = V x M matrix P[v,f]=p_f(v). Load T(v)=sum_g ell(g) p_g(v); incidence
S(v)=sum_g p_g(v). Gram O=P^T P (M x M), O_{fg}=<p_f,p_g>=sum_v p_f(v)p_g(v) >= 0. K=PP^T (V x V),
K_{vw}=sum_f p_f(v)p_f(w). Gamma=sum_f ell(f)^2.

THE OPEN INEQUALITY (ROWSUM-O). For every bad edge f:
   (O.1)_f = sum_g O_{fg} = sum_v p_f(v) S(v)  <=  N.
[Equivalent per-edge "load" form: the betweenness-weighted average load along f's geodesic bundle,
  <u_f, T> <= N + eta,  u_f = p_f/ell(f)^2 normalized (sum_v u_f=1), eta=N^2/25-beta.]
WHY IT FINISHES: ROWSUM-O + (O symmetric nonneg) => rho(O) <= max row sum <= N (Gershgorin/Perron). O PSD Gram
=> sum_v T(v)^2 = ell^T O ell <= rho(O)*||ell||^2 = N*Gamma. Cauchy-Schwarz: sum_v T^2 >= (sum_v T)^2/N =
Gamma^2/N (since sum_v T = Gamma). So Gamma^2/N <= N Gamma => Gamma <= N^2 => beta <= Gamma/25 <= N^2/25 (ell>=5).
Tight exactly at the balanced C_{2k+1}[t] blow-up (T == N, constant Perron vector of K).

PROVEN STRUCTURAL FACTS available:
 - Layer-uniformity: with layers I_i(f)={v: d_B(a,v)=i, d_B(v,b)=ell-1-i}, sum_{v in I_i(f)} p_f(v) = 1 for each
   i=0..ell-1. So <u_f,T> = (1/ell(f)) sum_i (p_f-weighted average of T over layer I_i(f)).
 - Betweenness factorization: p_f(v) = sigma_a(v) sigma_b(v)/sigma_ab (Brandes).
 - Diagonal bound: O_{ff} = ||p_f||^2 <= ell(f) <= N.
 - K row sums: K.1 = T; B := diag(T) - K is a PSD, zero-row-sum (Laplacian-type) matrix; rho(O)=rho(K).
   rho(K)=N EXACTLY iff T == N (the constant vector is the Perron eigenvector of K at the extremal).
 - Incidence <= load/5: S(v) <= T(v)/5.

APPROACHES ALREADY REFUTED (exact witnesses; please do NOT propose these):
 - Cut-metric / Crofton LP endpoint-separation: separating-cut multiplicity inflates the bound; cuts cannot see
   the vertex overlap <p_f,p_g>.
 - Combinatorial charging / double-counting; geodesic flow / Menger / incidence LP-dual (collapse to layer-cover
   which overshoots N, or circular); overlap-packing LP (circular, dual mu_g=O_fg uses no cut).
 - Norm bounds ||P||^2 <= ||P||_1 ||P||_inf ~ 0.27 N^2 (lossy); per-cycle sum_{v in C} S(v) <= N is FALSE
   (up to 1.067 N); per-layer / symmetric-pair / vertex-Gershgorin.
 - Vertex-SOS N I - K = sum_f [diag(N p_f/S) - p_f p_f^T] is CIRCULAR (f-block PSD <=> ROWSUM-O(f)).
 - Spectral V2=sum(T-N)^2 <= K Gamma budget: constant unbounded ~N. Per-bad-edge induction with constant budget
   (N+eta)ell_f^2: FALSE (fails at C5[5]).

QUESTION. The two live directions are (1) a NON-CIRCULAR SOS split N*I - K = L + R, L a graph Laplacian (e.g. the
B-distance or cut Laplacian) and R manifestly PSD via the betweenness factorization; (2) a spectral comparison
K <= M (in PSD order or via quadratic forms) for an explicit odd-cycle / circulant MODEL operator M with rho(M)=N,
the comparison forced by triangle-freeness + odd-girth >= 5. Which is the right one, and what EXACTLY is L and R
(resp. M)? In particular: is there a Laplacian L on the cut-graph B such that N*I - K - L is PSD by a LOCAL
(per-layer or per-geodesic) betweenness identity that does NOT reduce back to ROWSUM-O? The crux is the
cross-terms <p_f,p_g> for overlapping geodesics; the layer-uniformity (sum_{I_i}p_f=1) and the odd length >=5
must bound how much two bad-edge geodesics can co-travel. Please give the construction in enough detail to verify
on exact examples (I can test any proposed L, R, or M, and any per-layer/per-geodesic inequality, in exact
rational arithmetic on the full battery).

## Answer
(pending)

## Per-cycle circulant identity (GPT-Pro plain-ASCII, 2026-06-30) -- LOCAL, MINIMALITY-FREE
Single-geodesic bad edge f, chordless odd cycle C_f length ell, p_f = indicator (1 on ell cycle vertices):
  a_f = ell/(2+2cos(pi/ell))  [sharp];  a_f_bar = ell^3/(4(ell^2-2))  [rational, <= a_f].
  L_f = cycle Laplacian (2I - A_cycle) on the ell cycle verts, 0 outside.  D_f = ell*diag(p_f).
  IDENTITY:  R_f := ell*diag(p_f) - p_f p_f^T - a_f L_f  is PSD.
  C5 check (a_f=1.382): R_f eigenvalues {0 (const mode), 3.09, 3.09, 0, 0} -- PSD, tight on const + top-L_f modes.
PROVEN analytically (circulant Fourier): const mode 0; mode k -> ell - a_f(2-2cos(2pi k/ell)) >= ell - a_f(2+2cos(pi/ell)) = 0.
ASSEMBLY: sum_f R_f >= 0 and sum_f ell_f diag(p_f) = diag(T), sum_f p_f p_f^T = K  =>  diag(T)-K-R_cyc >= 0,
R_cyc = sum_f a_f L_f. i.e. B := diag(T)-K >= R_cyc >= 0 (min-free Laplacian lower bound on B). To close
N*I-K>=0 still need B >= diag(T-N) on the overload directions = the GLOBAL minimality-dependent positivity.
