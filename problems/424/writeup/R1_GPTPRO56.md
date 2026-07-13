# R1 (GPT-5.6 Pro, 2026-07-13, 18,315 ch) — ROUTE R-A fully mapped; best broader route = G0·G2 bilinear
## [CLAUDE GATE HEADER — literature to verify: Bettin–Koukoulopoulos–Sanna (density-1 products; smooth/rough
## estimates), Ford multiplication-table exponent 0.086071…; all reductions exact by inspection]

- SETUP: S = G ∩ 3N = 3T (1 ∈ T); T^(2) = {uv : u,v ∈ T, u≠v}; m ∈ T^(2) ⟹ 9m−1 ∈ G; d(G) ≥ d(T^(2))/9.
- **PRIME OBSTRUCTION (exact)**: p prime ⟹ p ∈ T^(2) ⟺ p ∈ T (only 1·p). For p ≡ 1 (mod 3):
  9p−1 ∈ G ⟺ 3p ∈ G (pairs (1,9p),(9,p) killed by 1 ∉ G and G1) ⟹ EVENTUAL-ALL class-8 requires
  "3p ∈ G for all large primes p ≡ 1 mod 3" — a new prime theorem. Almost-all NOT obstructed (primes = density 0).
- **DENSITY THRESHOLDS USELESS**: BKS: d1 × d1 ⟹ product density 1; NO c < 1 suffices — idempotent
  countermodels A(q,k) = {n : v_q(n) ≡ 0 mod k}, A·A = A. NUMERICAL TWIN: d(A(2,6)) = 32/63 ≈ 0.5079,
  S0 = 3·A(2,6) has d ≈ 0.1693 ≈ our observed 0.17 — "the density 0.17 by itself is completely silent."
  Even d(T) = 1 does not give cofinite ({1} ∪ composites misses all primes). Conversely density-0 sets CAN
  be multiplicative bases (prime-partition M0·M1 = N minus {1}) ⟹ the invariant is canonical factorization
  structure, not density.
- **FORD**: balanced dyadic products cover o(X) (multiplication-table exponent) ⟹ any proof MUST use
  growing scales with highly UNBALANCED factors — both still → ∞: with u = (loglogX)^(1/2),
  y = exp((logX)^(1/2)), z = y^(1/u), L = exp((logz)^(1/2)): a.e. m = s·r, L ≤ s ≤ y smooth, r > z rough
  (ambient supply PROVED). Missing piece = MEMBERSHIP of s and r in T.
- **CENTRAL FINITE CERTIFICATE (21)**: |T^(2) ∩ [1,X]| ≥ X − E0(smooth part > y) − Es(smooth part ∉ T)
  − Er(smooth ∈ T, rough ∉ T) − 1. (54): E0+Es+Er = o(X) ⟹ d(T^(2)) = 1. (24)-(25): errors ≤ (1−β)X ⟹
  d(G) ≥ β/9. Sufficient gates: (31) sum over z-smooth s ≤ y with s ∉ T of 1/s = o(log z);
  (32) H_z(y) · sup rough-miss-rate = o(1). Works even if d(T) = 0.
- **HONEST DOUBLE COUNTING**: d(G) ≥ d(T)/3 + d(T^(2))/9 (disjoint classes, (36)-(37)); new-products
  metric P_new = T^(2) minus T (38); baseline-safe (39): d(G) ≥ d(B) + (1/9)·d{m ∈ T^(2) : 9m−1 ∉ B}.
  The finite census value 0.519 is NOT an asymptotic baseline.
- **GATES**: (40) membership recursion — n ∈ G ⟺ some divisor pair of n+1 lies in G×G (both cofactors
  < n) — EXACT census with no truncation (supersedes G0 algorithmically); (41)-(42) divisor-cover count;
  **(43)-(46) GLOBAL MODULAR FALSIFIER**: R_M = closure of {2,3} in Z/M under rs−1 (equal residues
  allowed ⟹ over-approximation of G mod M); U_q = {u : 3u mod 3q ∈ R_3q}; if U_q·U_q ≠ Z/q for ANY q ⟹
  density-one/cofinite R-A globally impossible (fail = complete falsifier; pass proves nothing);
  (47) smooth-rough positive certificate; **(48)-(51) ENERGY GATE**: disjoint U,V ⊆ T, all uv ≤ X,
  E×(U,V) ≤ κ·|U|²|V|²/X ⟹ d(T^(2)) ≥ α/κ — "probably the cleanest finite gate"; Ford: a single balanced
  block cannot satisfy it; **(52)-(53) TOWER THINNESS**: B(X) ≤ C·X^θ, θ < 1 ⟹ |B·B ∩ [1,X]| ≪ X^θ logX
  = o(X) ⟹ the affine tower CANNOT be the covering core (the killer is the polynomial upper bound).
- **(56) SHARPEST CLASS-8 IDENTITY**: 9m−1 ∈ G ⟺ m ∈ T^(2) ∪ T9·V, where T9 = {u : 9u ∈ G},
  V = G ∩ {2 mod 3} (second channel 9u × v, auto-distinct; includes 17 = 9·2−1 which pure R-A misses).
- **(58)-(60) ROUTE R-C (BEST BROADER)**: G0 = G ∩ 3N, G2 = G ∩ {2 mod 3}: a ∈ G0, b ∈ G2 ⟹
  AUTO-distinct and ab−1 ∈ G2 ⟹ G0·G2 − 1 ⊆ G, disjoint from G0 ⟹ d(G) ≥ d(G0) + d(G0·G2 − 1).
  ENOUGH: d(G0·G2) > 0 via variable-scale energy for disjoint reservoirs U_X ⊆ G0, V_X ⊆ G2 — no 1/9
  loss, no distinctness correction, consistent with ALL SIX sprint obstructions.
- **FRONTIER (61)**: eventual-all/two-unbounded = impossible (primes); eventual-all-with-3 = new prime
  theorem; almost-all / positive fraction = viable ONLY via unbounded smooth-rough membership or low
  multiplicative energy; best enlargement = T^(2) ∪ T9·V; best broad route = scale-dependent expansion
  of G0·G2.
