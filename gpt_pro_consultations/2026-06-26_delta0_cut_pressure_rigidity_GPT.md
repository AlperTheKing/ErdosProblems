# GPT-Pro fresh delta=0 route: variational "cut-pressure rigidity" (2026-06-26)

Thread "Erdos Problem 23 Closure" (c/6a3b8a74), model Kapsamlı Pro. Step-1 drove the browser, asked for a
COMPLEMENTARY route to the band bound d_mono(W)<=2/25 (delta=0), distinct from Step-2's geodesic-peel/Gamma route
and from the walled flag-SDP / local-cert / scalar routes. GPT picked a variational/stability ("cut-pressure
rigidity") route. AUDITED + KEY CLAIMS INDEPENDENTLY VERIFIED.

## KEY REFRAMING (GPT correction, verified)
C5-blow-up is NOT a band maximizer: d_edge(C5[1/5]) = 2*5/25 = 2/5 = 0.4 > 0.3197, i.e. C5 is in the HIGH TAIL,
not the medium band. (Verified: in-band d_mono is strictly < 2/25 with slack; that's why the brute in-band max was
~0.0556.) So the correct variational target is NOT "C5 = unique band maximizer" but:
  ** any triangle-free graphon with d_mono >= 2/25 must satisfy C5-type stationarity, hence d_edge >= 2/5. **
Since 0.3197 < 2/5, this CLOSES the band (no band graphon can have d_mono >= 2/25).

## The functional and the Euler-Lagrange / KKT condition
F(W) := d_mono(W) = inf_S <W, K_S>, K_S(x,y)=1_S(x)1_S(y)+1_{S^c}(x)1_{S^c}(y) (same-side kernel). F is CONCAVE
(inf of linear functionals). Supergradients = convex combos of same-side kernels of OPTIMAL cuts. For an
optimal-cut ensemble nu, the CUT-PRESSURE kernel P_nu(x,y) = Pr_{S~nu}[x,y same side]; 0<=P<=1, <W,P_nu>=F(W).
Common-neighbour kernel C_W(x,y)=int W(x,z)W(y,z)dz; triangle-free => W*C_W=0 a.e.; D t(K3,W)[Z]=3 int Z C_W.

FIRST LEMMA (concrete, finite-step = finite-dim nonsmooth KKT, CODE-AUDITABLE): a fixed-density maximizer of F
over {0<=W<=1, t(K3,W)=0, int W=d_0} satisfies, for multipliers alpha in R, lambda>=0,
  P - alpha - 3 lambda C_W  in  N_{[0,1]}(W)   (box normal cone), i.e.
  W=1 => P >= alpha+3 lambda C_W ;  0<W<1 => P = alpha+3 lambda C_W ;  W=0 => P <= alpha+3 lambda C_W.
Existence: F usc + constraint set weak-* compact => maximizer exists; optimal-cut attainment via closed convex
hull of eps-optimal cut kernels (handles measurable selection).

## C5 ANCHOR -- VERIFIED EXACTLY (Step-1, by enumerating C5's 10 optimal cuts)
P = 1/5 + 2 C_W on ALL pairs of C5: adjacent (W=1) P=1/5, C_W=0; dist-2 (W=0) P=3/5, C_W=1/5; same-class (W=0)
P=1, C_W=2/5. So C5 satisfies KKT EXACTLY with alpha=1/5, lambda=2/3, all box relations equalities.
(verify: a one-off enumeration confirmed P=0.2/0.6/1.0 vs 1/5+2C_W = 0.2/0.6/1.0.)

## HARD STEP -- the Pressure-Rigidity Lemma (OPEN, the real content)
F(W) >= 2/25  =>  P = 1/5 + 2 C_W a.e.  =>  C_W takes only C5-values {0,1/5,2/5} (mod twins)  =>  W is a
weighted C5-blow-up  =>  d_edge(W) = 2 sum w_i w_{i+1} >= 2/5. Closes the band.
GPT's 3 attack tools: (1) EDGE-AVERAGE identity <W,P>=F => a band counterexample has F/d_edge >= (2/25)/0.3197
~ 0.2502 vs C5's exactly 1/5 ("too much edge pressure"); (2) triangle-free complementarity W*C_W=0 forces P flat
(=alpha) on edge support (the "E-flat" target), unstable under edge relocation otherwise; (3) R:=1-P is an L1 CUT
METRIC => satisfies hypermetric/PENTAGONAL inequalities, saturated by the C5 optimal-cut metric; integrate the
pentagonal inequality against a W-/C_W-biased 5-point distribution. Target inequality schema:
F(W)-2/25 <= A(d_edge-2/5) + B*R(W) with R(W)<=0 for triangle-free (hypermetric), equality forcing the C5 metric.

## Step-1 audit verdict
SOUND + GENUINELY FRESH. Distinct from peel/Gamma (Step-2), the self-tight flag-SDP, the refuted local certs, and
spectral/electrical (GPT notes that's ~Gamma in disguise and weakens the squared quantity). The functional/KKT is
standard nonsmooth convex analysis; the C5 stationarity anchor is verified exact; the first (KKT) lemma is concrete
and code-auditable on weighted blow-ups (Grotzsch/Petersen/Clebsch/Mycielski/C7/C9/C5). The pressure-rigidity lemma
is the hard open core (as expected -- delta=0 is hard), but it is sharply targeted + FALSIFIABLE: compute P, C_W on
Grotzsch/Mycielski blow-ups and check where P-1/5-2C_W fails (should fail GLOBALLY). RELAYED to Step-2 as a
complementary line to their peel route (co-develop; do NOT duplicate their flag-SDP/live-run files).
