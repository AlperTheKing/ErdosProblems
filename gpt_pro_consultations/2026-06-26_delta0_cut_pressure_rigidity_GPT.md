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

---

## STEP 2 (2026-06-26, same thread c/6a3b8a74): whole-class ensemble fix + E-FLAT REFUTED

Step-1 asked GPT-Pro to (a) confirm/repair the whole-class graphon optimal-cut ensemble (my
finite-vs-graphon caveat: C5[2] gets class-splitting optimal cuts, maxdev 0.133) and (b) PROVE
the E-flat sub-lemma (P=alpha constant on the whole edge support {W>0}). GPT answer (11640 chars)
AUDITED + EXACT-VERIFIED (problems/23/writeup/verify_eflat_refutation.py).

### (a) Whole-class ensemble — REPAIRED (rigorous, adopted)
Use the graphon/quotient optimal-cut supergradient P = conv{K_chi : chi in C*(W)} (whole-atom
optimal cuts), NOT the uniform measure on raw finite max-cuts of a blow-up. WHY class-splitting
cuts add no new off-diagonal supergradient: round a fractional optimal graphon cut x in [0,1]^m
by independent Bernoulli(x_i). Then E[M_W(chi)] = M_W(x) = d_mono(W), but every whole-atom cut has
M_W(chi) >= d_mono(W); so every whole-atom cut with positive rounding probability is itself optimal
=> the split cut's off-diagonal kernel is a convex combo of whole-atom optimal kernels. => my
caveat is resolved: fractional class-splitting optimal cuts contribute nothing new off-diagonal.

### (b) E-FLAT — NOT a consequence of KKT (honest refutation; sub-lemma killed)
The box normal cone N_[0,1](W) gives, with C_ij=0 on edge support (triangle-free W*C_W=0):
  0 < W_ij < 1, C_ij=0  =>  P_ij = alpha     (FRACTIONAL edges: equality)
  W_ij = 1,    C_ij=0   =>  P_ij >= alpha     (SATURATED edges: ONE-SIDED only -> slack allowed)
E-flat asserted P_ij=alpha on ALL of {W>0} incl. W=1 -- KKT proves it only on fractional edges.
EXACT WITNESS (verified by Fractions): weighted C5-blowup w=(.54,.06,.20,.10,.10), edges between
consecutive classes => d_edge=321/1250=0.2568 (IN BAND), unique min-product edge 3-4 (=1/100),
maxcut leaves 3-4 monochromatic, d_mono=1/50 (band-slack). The optimal cut's same-side kernel P
has P_{34}=1 on the SATURATED edge 3-4 while P=0 on the other 4 saturated cyclic edges -> P is
NOT constant on edge support. So a saturated edge carries strict pressure slack (P>alpha) and
E-flat is false from KKT alone. (Edge-relocation cannot fix it: see clone note below.)

### Replacement (adopted) -- bang-bang / pressure-threshold lemma
What KKT REALLY says: inside the zero-common-neighbor graph Z={(i,j):C_ij=0}, supp(W) is a
THRESHOLD set for the pressure P:  P>alpha => W=1 ;  P<alpha => W=0 ;  P=alpha => 0<=W<=1.

### The real remaining hard lemma -- "High-F no-slack"
For a fixed-density maximizer with d_mono(W) >= 2/25: NO saturated edge has strict pressure slack,
i.e. W_ij=1, C_ij=0 => P_ij=alpha. GPT: strictly stronger than KKT; NOT provable by edge-relocation
or clone-refinement alone (splitting atoms can't desaturate a complete edge: averaging 1's stays 1).
Must use one of: atom-WEIGHT variation (shift measure toward high-pressure endpoints at fixed
density), clone-weight rebalancing, a global optimal-cut metric (hypermetric/pentagonal) inequality,
or a classification of pressure-threshold triangle-free supports. The balanced C5 equalizes all
edge pressures (=> the P=1/5 anchor); an UNbalanced weighted C5 does not -- so the no-slack lemma
is exactly a fixed-density weight-extremality statement on weighted-C5-type supports.

### Step-1 audit verdict
SOUND + HONEST. The ensemble repair is rigorous (Bernoulli rounding) and resolves my caveat; the
E-flat refutation is a correct subdifferential-calculus fact (one-sided normal cone at W=1), backed
by an exact in-band witness; the bang-bang restatement is precisely the KKT content; the High-F
no-slack lemma is the sharply-stated open core (delta=0 is hard -- expected). NET: killed a wrong
sub-lemma BEFORE it could cause a false closure, and narrowed the route to one weight-extremality
lemma. Convergence with Step-2: their "tight Gamma=N^2 => C5[q], obstructions only at Gamma<N^2"
finite rigidity == this "no saturated-edge pressure slack at high F" graphon rigidity (PROGRESS
2026-06-26T19:55). RELAYED to user for Step-2.
