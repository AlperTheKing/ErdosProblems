# Q to GPT Pro (chat 6a3b5aba): MT25 reduces to a metric-free GEODESIC-CONGESTION bound

## What was established this session (all audited)
- Bridge (T) tau<=(N/5)sqrt(nu*): 0 violations over 2466 tri-free N<=9 + 80 adversarial hard instances
  (Grotzsch/Mycielski/subdivK5/C5[n]-perturb/random N<=16), tight ONLY at balanced C5[n].
- (Sep) 0 violations; (Def) identity to 1e-14; QFC25 rho<=max{1,N^2/25m} holds.
- 15-agent Workflow: quadratic/spectral routes GENUINELY FALSE on band (N/5)^{4/3}<m<(N/5)^2; cut-cone =
  only non-circular route; proven Lean-ready modules: nu*<=N^2/25, Sep+coarea, coherent-P5 block, rigidity.

## THE KEY NEW REDUCTION (decisive experiment, exp_geodesic_stretch.py + exp_stretch_sweep.py)
Solve dual rho = max_{ell>=0} (sum_{uv in M} d^B_ell(u,v))/(sum_b ell_b). On K23-N13 (rho=4/3, ell* non-
uniform support 6/14), N=20 M-odd-cycle (M non-bipartite, no global 5-layer), Petersen, C5[2], C5[3]:
the optimal dual metric ell* NEVER STRETCHES an M-geodesic beyond d_B(u,v) (every M-pair has an ell*-shortest
B-path with exactly d_B edges). Also rho_geo = rho EXACTLY (rho_geo = min-max congestion of routings
restricted to d_B-edge geodesics). Since geodesic routings subset all routings, rho <= rho_geo for free;
no-stretch gives rho = rho_geo. THEREFORE:

   MT25 / QFC25  <=>  GEODESIC-CONGESTION BOUND:
   exists a fractional routing of the m bad edges, EACH over its d_B-edge B-geodesics, with
   max B-edge load <= max{1, N^2/(25m)}.

METRIC-FREE, purely combinatorial (no L1 embedding / Bourgain distortion). The non-L1 difficulty is GONE,
replaced by a congestion bound on the unit d_B-geodesic skeleton. Lean-friendly.

## The question asked
Prove the geodesic-congestion bound: construct the routing (uniform over d_B-geodesics, or smarter) + bound
max B-edge load by max{1,N^2/(25m)} via CD / (Sep) / coherent-P5 AM-GM / cycle-degree ineq (6) / triangle-
free. Does it reduce to the proved unit cosystole Gamma=sum_M(d_B+1)^2<=N^2 (verified N<=11), and how?
DANGER case = N=20 M-odd-cycle (no global coherent 5-layer). Avoid Guenin/Lehman (Lean). [awaiting answer]
