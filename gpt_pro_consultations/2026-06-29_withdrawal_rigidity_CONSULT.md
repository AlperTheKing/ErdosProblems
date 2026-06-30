# GPT-Pro consult 2026-06-29 — PREFIX-LOAD-PSC withdrawal/rigidity half

## Question sent

Setup. G is a finite triangle-free graph on N vertices with a chosen MAXIMUM cut (S, S-bar). Call an edge "bad" if both endpoints lie on the same side; let M be the set of bad edges and beta=|M|. (Note beta = |E| - maxcut(G); the open conjecture I am attacking asserts beta <= N^2/25.) Because G is triangle-free and the cut is maximum, every bad edge f lies on a shortest alternating closed walk whose non-f edges are all cut edges, of length >= 5; let ell(f) >= 5 be its number of vertices and cyc(f) the set of such shortest geodesics. Define a load function T: V -> Q>=0 by

   T(v) = sum_{f in M} ( ell(f)/|cyc(f)| ) * #{ geodesics in cyc(f) through v },

so that sum_v T(v) = Gamma := sum_{f in M} ell(f)^2. For a threshold s let H_s = { v : T(v) > s }, and write delta_B(H_s), delta_M(H_s) for the number of cut-edges resp. bad-edges in the boundary of H_s. Maximum-cut optimality gives, for every s, delta_M(H_s) <= delta_B(H_s).

What I have proven EXACTLY (rational arithmetic) over ~190,000 triangle-free maximum-cut configurations, including iterated Mycielskians up to N=23 and glued multi-component graphs:

   (PREFIX)  G(tau) := integral_0^tau [ (N^2 - 25 beta + 25 N - 50 s) * |H_s|  -  5 N * ( delta_B(H_s) - delta_M(H_s) ) ] ds  >= 0   for every tau >= 0,

with equality (and G(infinity)=0) exactly at the balanced blow-up of C5 (T == N, beta = N^2/25). The full integral G(infinity) >= 0 is equivalent to the target beta <= N^2/25 (via sum_v T = Gamma and a PSD / Cauchy-Schwarz step that uses ell >= 5). The |H_s|-coefficient (N^2 - 25 beta + 25 N - 50 s) is positive for s < (N^2 - 25 beta + 25 N)/50 and negative beyond. Empirically the integrand is termwise >= 0 for s <= N/2 ("deposit"), and only goes negative for s > N/2 ("withdrawal"), yet the running integral G(tau) never dips below 0. I have also verified the deposit half termwise: for every superlevel interval lying entirely in {s <= N/2}, the integrand is >= 0.

Crucial constraint (already refuted, so please do NOT propose these): the withdrawal bound is NOT local in the superlevel set. There is NO per-superlevel isoperimetric inequality that pays the withdrawal from the CURRENT boundary alone. Specifically, both of these fail on explicit small examples: (i) the cut-pressure flux carried across the boundary of H can be 0 while sigma(H) = delta_B(H) - delta_M(H) = 2 > 0; (ii) 2*t_j <= N does not imply the band is a deposit (a band straddling s = N/2 can already be a withdrawal). So whatever bounds the withdrawal at levels s > N/2 must draw on the ACCUMULATED surplus deposited by LOW-LOAD vertices at levels s < N/2 -- it is a non-local, running-balance / potential-function phenomenon, not a single-superlevel inequality.

QUESTION. Given that constraint, what is the right NON-LOCAL mechanism that makes the running integral G(tau) monotone-enough to stay >= 0? My working hypothesis is a rigidity/stability principle -- "beta near N^2/25 forces T near-uniform (about N), so {T > N} has small measure, so the withdrawal is small." Which of these is the sharp route, and how is it set up:

 (b) a single GLOBAL Cauchy-Schwarz / SOS certificate writing the full functional sum_v T(T-N) + (N/5)(TV_cut(T) - TV_bad(T)) - Gamma(N^2/25 - beta) as a sum of squares against the maximum-cut Laplacian, such that the coarea/threshold partial sums are automatically >= 0 (this would give PREFIX for free);
 (c) a spectral / Cheeger bound tying sum_v T(T-N) to the cut-pressure sum_{cut uv}|T_u - T_v| via the second eigenvalue of the maximum-cut quotient, giving the near-uniform rigidity directly;
 (d) a transport plan IN THE LEVEL VARIABLE: match each unit of withdrawal at a level s > N/2 to banked deposit at a level s' < N/2 belonging to the SAME or a NESTED superlevel (so the matching respects the H_s filtration), with a per-unit cost bound from ell >= 5;
 or (e) something else.

Please pick the single most promising route and outline the proof in enough detail that I can verify it on exact examples. If route (b), give the explicit SOS / Gram decomposition (which vectors, indexed by what -- vertices, bad edges, geodesics?). If (c), give the precise eigenvalue inequality and why max-cut + triangle-free forces it. If (d), give the matching and the per-unit cost bound. The key fact I can feed any route: ell(f) >= 5 for every bad edge, sum_v T = Gamma = sum_f ell(f)^2, and delta_M(H_s) <= delta_B(H_s) for all s.

## Answer (GPT-Pro, model Kapsamlı Pro, 2026-06-29) — 1-line: ROUTE (d) causal level-transport

PICK: route (d) level-variable transport ("banked coarea"); REJECTS (c) [glued islands make spectral gap
arbitrarily small while prefix stays sharp componentwise -> rigidity is a COROLLARY not input] and (b)
[any SOS must contain the level param s and becomes the dual of (d), Gram atoms (v,j),(e,j),(f,Q,j)].

BANK FORM. eta:=N^2/25-beta. N^2-25beta+25N = 25(N+eta). Integrand I(s)=25(N+eta-2s)h(s)-5N*sigma(s),
h=|H_s|, sigma=delta_B-delta_M>=0. Sign change at theta=(N+eta)/2 (NOT N/2; my N/2 split was a conservative
subset since 2t_{j+1}<=N => t_j+t_{j+1}<=N<=N+eta). PREFIX <=> Debt(tau)<=Bank_+(tau) for all tau, where
Bank_+ = int_0^tau 25(N+eta-2s)_+ h ds, Debt = int_0^tau [25(2s-N-eta)_+ h + 5N sigma] ds.

FINITE BANDS. levels 0=t_0<...<t_m (distinct positive loads, + theta). band J_j=(t_j,t_{j+1}), Delta_j=width,
h_j=|{T>t_j}|, sigma_j. alpha_j:=25(N+eta-(t_j+t_{j+1})). band signed contribution
  b_j = Delta_j[ alpha_j h_j - 5N sigma_j ].  PREFIX: sum_{j<k} b_j >= 0 for all k.

REFINED CAUSAL TRANSPORT (the proof object). Atoms per band j:
  SOURCE (v,j) for v in H_{t_j} when alpha_j>0 : capacity Delta_j*25(N+eta-(t_j+t_{j+1}))_+.
  VOLUME SINK (v,j) for v in H_{t_j} when alpha_j<0 : demand Delta_j*25(t_j+t_{j+1}-N-eta)_+.
  PRESSURE SINK (e,j) for e in boundary(H_{t_j}) : demand 5N*Delta_j  [net 5N*sigma_j; bad-boundary edges credit].
Admissible arcs UPWARD only (i<=j): source(u,i)->volsink(v,j) iff u=v OR u,v on a common shortest B-geodesic
cycle of some bad edge; source(u,i)->presssink(xy,j) iff xy in boundary(H_{t_j}) and u on a shortest geodesic
crossing the threshold through xy. If this transport exists for every tau, PREFIX follows by summing capacities.

FIVE-SLOT LEMMA (where ell>=5 enters): one unit of pressure debt at level s charges to 5 earlier vertical
source slots on the SAME odd cycle. 5N = N copies of the 5-slot payment; 25 = 5^2 = C5 geometry. Extremal
C5[t]: all five slots used with equality, zero spare bank, T==N.

L-HALL: nu(D)<=mu(Back(D)) for every sink set D; conjecturally suffices to test UPPER IDEALS {sinks level>=k}
(1-param family) since H_s nested. (UH) form given.

STEP-10 EXACT VERIFICATION (what I must run): build sources/volsinks/presssinks + causal same-geodesic arcs
as a rational max-flow; check feasibility for every prefix tau=t_k on the battery. Feasible => proof skeleton;
infeasible => the failed min-cut names the missing admissible arc type. Expectation: only 3 arc types needed
(vertical self, same-geodesic volume, same-geodesic pressure).

## My verification plan
Implement the refined causal max-flow (exact Fraction / cleared-denominator integer Dinic) and test per-prefix
feasibility on the curated HARD set first (C5[t] t=1..4 must be TIGHT, C7[t], two-lane, k-lane, Grotzsch,
Myc(Grotzsch) N=23, glued islands), then sample census. File _level_transport.py.
