# EQ-ODL1 O14 ASSEMBLY THEOREM — GPT-Pro (main thread), extracted 2026-07-04

Source: main thread https://chatgpt.com/c/6a450f06-be68-83eb-b6f4-5b855434e550 (reply to the
O14 assembly-theorem consult; 12,677 chars). Verbatim-as-rendered (KaTeX subscripts flattened
by innerText; math reconstructed inline where unambiguous). Extraction: offset-stitch, 14 slices,
reverse ZZEQZZ/ZZPLUSZZ transform.

STATUS: architecture ARCHIVED. O14 remains CERT-PENDING until all 300 regions + stratum are
certified or routed (section 8, all-or-nothing).

KEY POINTS (my summary; full text below):
- Target: P_EQ1(w) = D_EQ(w)·[eta25(w) − 25(I_EQ(w) − N(w))] ≥ 0 with D_EQ > 0 ⟹ I_EQ − N ≤ eta.
- Coverage chain: height reduction (h = min w_i) → 10 height charts (HCover) → compactification
  s = 1/S, z_i = x_i/S bijective onto open simplex face s>0; s=0 = projective infinity, certified
  only to close the Bernstein cert → homogenization P_k(s,z) = s^11 · P_EQ1(z/s) (Phat) →
  15 generators F1-F7, G1-G8 (G6 = U_A = A²−9T, G7 = U_B = B²−4T, G8 = B0 = eta25 − 25) with
  corrected degree-2 lifts G# = H_G·Λ^(2−deg G), Λ = s + Σz (Λ=1 on simplex) → equality stratum
  = seed ray, P_EQ1(t) = 25t⁶(t+2)(t²+2t+2) ≥ 375 (Stratum) → dominance charts D_{k,a} for a
  maximizing G#_a (Dominance) → bands B_near: 2s−1 ≥ 0, B_inf: 1−2s ≥ 0 → ChartCover:
  H_k = Stratum ∪ ⋃_a (D_{k,a} ∩ B_near) ∪ ⋃_a (D_{k,a} ∩ B_inf).
- Cert object: EQODL1CoverCert { stratumCert; regions : Fin 10 → GeneratorLabel(15) → BandLabel(2)
  → RegionCert }; RegionCert = direct | skip | empty. 300 region labels + 1 stratum cert.
- Direct cert (Direct): P_k = P_0 + Σ_G G#_G P_G + Σ_b Δ_{a,b} P_{a,b} + B_β P_β, all multipliers
  Bernstein-positive on the simplex; checkEq + Bernstein-coefficient nonneg blocks.
- Empty cert (Empty): Positivstellensatz −1 = P_0 + Σ G# P_G + Σ Δ P + B_β P_β + S_Δ P_Δ ⟹ region
  vacuous.
- Skip cert — CORRECTION vs the earlier radmono sweep protocol: bare dominance-based skips are
  REJECTED. Two accepted modes:
  * Mode A (global-band): ∓∂_s P_k ≥ 0 on the WHOLE band 0 ≤ s ≤ 1/2 with NO dominance deltas —
    dominance irrelevant; one cert covers all 15 generator regions of chart k in that band.
  * Mode B (radial-hull): monotonicity on RadHull(k,a,β) = radial closure of the dominance
    region; requires an explicit RadialHullCert that the derivative cert's domain contains the
    whole radial path.
  Skip soundness: decreasing ⟹ P_k(s,u) ≥ P_k(1/2,u) on [0,1/2] (boundary cert at s=1/2);
  increasing ⟹ P_k(s,u) ≥ P_k(0,u) (s=0 FaceCert). EQRadialSkipCert = { sign; derivCert
  (BernsteinConeCert); radialDomainCert; boundaryCert (s=0 face | s=1/2 boundary) }.
- Pullback (Lemma 4.1): P_k(s,z) ≥ 0, s>0 ⟹ P_EQ1(w̄) = P_k/s^11 ≥ 0.
- Height-1 theorem (5.1): stratum cert + all 300 regions certified ⟹ P_EQ1(w̄) ≥ 0 for all
  w̄_i ≥ 1 with min w̄_i = 1 (Height1P).
- All heights (6): H(w) := I_EQ(w) − N(w); H(h·w̄) = h·H(w̄), eta(h·w̄) = h²·eta(w̄);
  EQ-CERT1 gives eta(w̄) ≥ 1 > 0; so H(w) = h·H(w̄) ≤ h·eta(w̄) ≤ h²·eta(w̄) = eta(w) — EQ-ODL1.
- Passive AM (7): EQ-ODL1 + EQ-AM ⟹ EQ branch ODL (consumer edge).
- Failure accounting (8): ALL-OR-NOTHING — one uncertified region ⟹ no global conclusion, no
  partial credit in the ODL ledger.
- Lean shapes (9): BandLabel, RegionCert, EQODL1CoverCert; checkEQStratumCert / checkRegionCert /
  checkEQODL1CoverCert; DirectChartCert.sound, EmptyRegionCert.sound (→ False),
  RadialSkipCert.sound, RegionCert.sound (cases); eq_chart_cover (stratum ∨ ∃ a band, dominance ∧
  inBand — max generator + band split); EQODL1CoverCert.sound_height1; EQODL1_of_cover (all
  heights); EQBranchODL (with EQPassiveAM).
- Checker obligations (10): stratum cert; 300 region certs; direct = target identity + generator
  list + dominance deltas + band generator + Bernstein nonneg; skip = deriv + radial-domain +
  boundary certs; empty = contradiction ConeCert; all checks true ⟹ EQ-ODL1 globally.

---- FULL TEXT (verbatim-as-rendered) ----

O14 EQ-ODL1 assembly theorem

Target: P_EQ1(w) = D_EQ(w)[eta_25(w) − 25(I_EQ(w) − N(w))] ≥ 0.
Since D_EQ > 0, this proves I_EQ(w) − N(w) ≤ eta(w).

1. Domain coverage theorem

1.1 Height reduction
For any w_i ≥ 1, let h := min_i w_i. Then h ≥ 1, and w̄_i := w_i/h satisfies w̄_i ≥ 1,
min_i w̄_i = 1. Therefore w̄ belongs to at least one height chart H_k : w̄_k = 1, w̄_i ≥ 1.
The ten height charts cover the normalized domain:
{w̄ : w̄_i ≥ 1, min_i w̄_i = 1} = ⋃_{k=0}^{9} H_k.   (HCover)

1.2 Compactification of a height chart
On chart k, set w̄_k = 1, w̄_i = 1 + x_i, x_i ≥ 0 (i ≠ k). Let S := 1 + Σ_{i≠k} x_i,
s := 1/S, z_i := x_i/S. Then s > 0, z_i ≥ 0, s + Σ_{i≠k} z_i = 1. Conversely, for s > 0,
z_i ≥ 0, s + Σ z_i = 1, recover x_i = z_i/s, and hence w̄_i = 1 + z_i/s. Thus the
compactification is a bijection between the original chart and the open simplex face s > 0.
The closed face s = 0 is the projective boundary at infinity. It has no finite w-preimage,
but certifying nonnegativity on the closed simplex is harmless and useful for Bernstein
positivity.

1.3 Homogenized target
Let D := 11. Define P_k(s,z) := s^11 · P_EQ1^(k)(z/s).   (Phat)
For s > 0, P_k(s,z) = s^11 · P_EQ1(w̄). Since s^11 > 0, P_k(s,z) ≥ 0 ⟺ P_EQ1(w̄) ≥ 0.

1.4 Generator set and equality stratum
Let the generator set be G = {F_1,…,F_7, G_1,…,G_8}, where
G_1 = UV−T, G_2 = UZ−T, G_3 = XY−T, G_4 = VZ−XY, G_5 = VZ−T,
G_6 = U_A = A²−9T, G_7 = U_B = B²−4T, G_8 = B_0 = eta_25 − 25.
Every generator is nonnegative on the EQ cone.
Use the corrected degree-2 lifted generators: G#_k(s,z) = H_{G,k}(s,z)·Λ(s,z)^{2−deg G},
Λ = s + Σ z_i. On the simplex, Λ = 1. Thus G# represents the same nonnegative generator but
has uniform degree 2 without losing linear-generator information on s = 0.
If G#_k(s,z) = 0 ∀ G ∈ G, then the point lies on the CERT-1 equality stratum.
The equality stratum is the seed ray: w_0 = w_1 = w_2 = w_3 = w_4 = 1,
w_5 = w_6 = w_7 = w_8 = w_9 = t, t ≥ 1. On this ray,
P_EQ1(t) = 25t⁶(t+2)(t²+2t+2) ≥ 375.   (Stratum)
So the equality stratum is certified separately.

1.5 Dominance charts
If not all generators vanish, at least one generator is positive. Choose a generator a ∈ G
maximizing G#_{a,k}. Then the point lies in the dominance chart
D_{k,a} : G#_{a,k} ≥ G#_{b,k} ∀ b ∈ G.   (Dominance)
Write Δ_{a,b,k} := G#_{a,k} − G#_{b,k}. Thus the dominance charts cover all non-stratum points.

1.6 Band cover
For every compactified chart point, 0 ≤ s ≤ 1. The two bands are:
B_near : 2s − 1 ≥ 0   (Near)   and   B_inf : 1 − 2s ≥ 0.   (Inf)
They cover the whole closed simplex: [0,1] = [0,1/2] ∪ [1/2,1]. Therefore the full chart
coverage is: H_k = Stratum ∪ ⋃_{a∈G} (D_{k,a} ∩ B_near) ∪ ⋃_{a∈G} (D_{k,a} ∩ B_inf).   (ChartCover)

2. ChartCoverCert object
structure EQODL1CoverCert where
  stratumCert : EQStratumCert
  regionCerts : Fin 10 → GeneratorLabel → BandLabel → EQRegionCert
inductive BandLabel | near | infinity
GeneratorLabel ranges over the 15 generators. So there are 10×15×2 = 300 region labels,
plus one stratum certificate.
inductive EQRegionCert
| direct (cert : EQDirectChartCert)
| skip   (cert : EQRadialSkipCert)
| empty  (cert : EQEmptyRegionCert)

3. Per-region certificate soundness

3.1 Direct chart certificate
A direct region certificate proves P_k(s,z) ≥ 0 on the region
Δ_k ∩ {G#_{a,k} ≥ G#_{b,k} ∀b} ∩ B_β. The certificate identity is:
P_k = P_0 + Σ_{G∈G} G#_{G,k} P_G + Σ_{b∈G} Δ_{a,b,k} P_{a,b} + B_β P_β,   (Direct)
where B_near = 2s−1; B_inf = 1−2s; all multipliers are Bernstein-positive on the simplex.
The checker verifies the polynomial identity by checkEq, and verifies nonnegativity of all
Bernstein coefficient blocks. Then soundness is immediate because every generator in the
identity is nonnegative on the region.

3.2 Empty-region certificate
An empty-region certificate proves the region constraints are inconsistent. It may be
encoded as a Positivstellensatz-style ConeCert:
−1 = P_0 + Σ_G G#_{G,k} P_G + Σ_b Δ_{a,b,k} P_{a,b} + B_β P_β + S_Δ P_Δ,   (Empty)
with all right-hand generators nonnegative on the region. This proves no point satisfies
the region constraints. The checker returns that the region is vacuous.

3.3 Radial skip certificate
A radial skip certificate is sound only if it certifies monotonicity on the whole radial
path from the point to the boundary used. This is important: a dominance condition at one s
need not remain true along the radial path. Therefore there are two accepted skip modes.
Mode A: global-band skip. Certify monotonicity on the whole band, without dominance deltas:
−∂_s P_k(s,u) ≥ 0 on 0 ≤ s ≤ 1/2, or +∂_s P_k(s,u) ≥ 0 on 0 ≤ s ≤ 1/2. Then dominance is
irrelevant.
Mode B: radial-hull skip. Certify monotonicity on the radial hull of the dominance region:
RadHull(k,a,β) = {(s′,u) : ∃ s in the region, s′ lies between s and the boundary}. The
checker must verify a RadialHullCert showing the derivative certificate's domain contains
this whole path. If no radial-hull certificate is supplied, dominance-based skip is REJECTED.

3.4 Skip soundness
For infinity-band decreasing skip: −∂_s P_k ≥ 0 on the relevant radial domain implies
P_k(s,u) ≥ P_k(1/2,u) for 0 ≤ s ≤ 1/2. Thus a boundary certificate at s = 1/2 proves the
whole skipped region. For increasing skip: +∂_s P_k ≥ 0 implies P_k(s,u) ≥ P_k(0,u). Thus
an s = 0 face certificate proves the skipped region. A skip certificate must therefore
contain:
structure EQRadialSkipCert where
  sign : MonotoneSign  -- decreasing or increasing
  derivCert : BernsteinConeCert
  radialDomainCert : RadialDomainCert
  boundaryCert : EQBoundaryCert
where boundaryCert is either: a face certificate at s = 0; or a boundary certificate at
s = 1/2.

4. Pullback from chart to original domain
Lemma 4.1 — chart soundness. If P_k(s,z) ≥ 0 for a compactified point with s > 0, then
P_EQ1(w̄) ≥ 0 for the corresponding original chart point.
Proof: By definition, P_k(s,z) = s^11 · P_EQ1(w̄). Since s > 0, s^11 > 0. Therefore
P_EQ1(w̄) = P_k(s,z)/s^11 ≥ 0. ∎
The s = 0 boundary has no finite w-preimage. Its certification is only used to make the
closed Bernstein certificate valid.

5. Final height-1 theorem
Theorem 5.1 — chart certificates imply height-1 EQ-ODL1. Assume: the stratum certificate
proves P_EQ1 ≥ 0 on the equality stratum; every one of the 300 labelled chart regions has a
direct, skip, or empty certificate; all region certificates are sound. Then for every
w̄_i ≥ 1, min_i w̄_i = 1, we have P_EQ1(w̄) ≥ 0.   (Height1P)
Proof: Choose k with w̄_k = 1. Compactify w̄ to (s,z) with s > 0. If all generators G#_{b,k}
vanish, use the equality-stratum certificate. Otherwise choose a maximizing generator a.
Then (s,z) lies in D_{k,a}. If s ≥ 1/2, it lies in the near band. If s ≤ 1/2, it lies in
the infinity band. The corresponding region certificate proves P_k(s,z) ≥ 0. By chart
soundness, P_EQ1(w̄) ≥ 0. ∎

6. From height 1 to all heights
Let arbitrary w_i ≥ 1. Let h = min_i w_i, w̄ = w/h. Then h ≥ 1, min_i w̄_i = 1. Height-1
theorem gives: I_EQ(w̄) − N(w̄) ≤ eta(w̄). Let H(w) := I_EQ(w) − N(w). The height lemma
gives: H(h·w̄) = h·H(w̄), eta(h·w̄) = h²·eta(w̄). EQ-CERT1 gives: eta(w̄) ≥ 1 > 0. Thus:
H(w) = h·H(w̄) ≤ h·eta(w̄) ≤ h²·eta(w̄) = eta(w). Therefore I_EQ(w) − N(w) ≤ eta(w) for all
w_i ≥ 1. This is EQ-ODL1.

7. Passive AM propagation
If passive attachments are added, EQ-AM proves I_ext(R) − N_ext ≤ I_seed(Q*) − N_seed.
Since EQ-ODL1 gives I_seed(Q*) − N_seed ≤ eta_ambient, the passive extension satisfies ODL:
I_ext(R) ≤ N_ext + eta_ambient. Thus: EQ-ODL1 + EQ-AM ⟹ EQ branch ODL.

8. Failure accounting
The chart coverage theorem is all-or-nothing. If even one labelled region (k,a,β) is
uncertified and not proven empty or skipped, then the coverage theorem cannot conclude
global EQ-ODL1. A partially certified region set proves only P_EQ1 ≥ 0 on the certified
subset of the compactified domain. That has no usable partial-credit interpretation in the
ODL ledger, because an arbitrary EQ quotient could lie in the missing region. Thus: O14
remains CERT-PENDING until all 300 regions plus stratum are certified or routed.

9. Lean statement shapes
9.1 Basic structures
inductive BandLabel | near | infinity
inductive RegionCert
| direct (cert : DirectChartCert)
| skip   (cert : RadialSkipCert)
| empty  (cert : EmptyRegionCert)
structure EQODL1CoverCert where
  stratumCert : EQStratumCert
  regions : Fin 10 → Fin 15 → BandLabel → RegionCert
9.2 Check functions
def checkEQStratumCert (cert : EQStratumCert) : Bool := ...
def checkRegionCert (k : Fin 10) (a : Fin 15) (band : BandLabel) (cert : RegionCert) : Bool := ...
def checkEQODL1CoverCert (cert : EQODL1CoverCert) : Bool :=
  checkEQStratumCert cert.stratumCert &&
  Fin.all (fun k =>
    Fin.all (fun a =>
      checkRegionCert k a BandLabel.near (cert.regions k a BandLabel.near) &&
      checkRegionCert k a BandLabel.infinity (cert.regions k a BandLabel.infinity)))
9.3 DirectChartCert.sound
  (hcheck : checkDirectChartCert k a band cert = true) (hSimplex : simplex s z)
  (hCone : EQConePoint k s z) (hDom : dominance k a s z) (hBand : inBand band s) :
  0 ≤ Phat k s z
This theorem uses the ConeCert/BernsteinCube checker.
9.4 EmptyRegionCert.sound (same hypotheses) : False
9.5 RadialSkipCert.sound (same hypotheses) : 0 ≤ Phat k s z — internally uses: derivative
certificate; radial-domain certificate; boundary certificate.
9.6 RegionCert.sound (same hypotheses) : 0 ≤ Phat k s z — by cases on cert.
9.7 Coverage theorem
theorem eq_chart_cover (hSimplex : simplex s z) (hCone : EQConePoint k s z) :
  EqualityStratum k s z ∨ ∃ a band, dominance k a s z ∧ inBand band s
Proof: if all generators zero, equality stratum; else choose a finite maximizer a; choose
band by s ≤ 1/2 or s ≥ 1/2.
9.8 EQODL1CoverCert.sound_height1
  (hcheck : checkEQODL1CoverCert cert = true) (w : Fin 10 → ℚ) (hw : ∀ i, 1 ≤ w i)
  (hmin : ∃ k, w k = 1) (hCone : EQSevenCone w) : 0 ≤ P_EQ1 w
Proof: choose chart k; compactify to s,z; use eq_chart_cover; stratum or region
certificate; pull back via P = s^11 P.
9.9 EQODL1_of_cover
  (hcheck : checkEQODL1CoverCert cert = true) (w : Fin 10 → ℚ) (hw : ∀ i, 1 ≤ w i)
  (hCone : EQSevenCone w) : I_EQ w - N_EQ w ≤ eta_EQ w
Proof: set h = min_i w_i; define normalized w̄ = w/h; apply sound_height1; use EQ height
lemma and EQ-CERT1 to scale back.
9.10 EQBranchODL (hODL1 : EQODL1_of_cover ...) (hAM : EQPassiveAM ...) : EQBranchODLStatement
This theorem is the consumer edge for O14.

10. Checker obligations summary
A valid O14 artifact must provide: EQStratumCert; 300 region certificates (10×15×2). For
each direct cert: target identity; generator list; dominance deltas; band generator;
Bernstein nonnegativity. For each skip cert: derivative certificate; radial-domain
certificate; boundary certificate. For each empty cert: contradiction ConeCert. All check
functions return true. Then O14 proves EQ-ODL1 globally.

This completes the O14 formal architecture.


# ===== FOLLOW-UP: FLOOR-BUFFER DIAGNOSIS + SKIP-MODE POLICY (main thread, 2026-07-04) =====

Q1 FLOOR-BUFFER (theta_max=0 diagnosis): NOT decisive on the negative-support column set —
artifact of restricted support (loses balancing columns) + pessimistic uniform buffer
(n_i^- sums negatives over ALL support columns incl. inactive ones).
RANKED POLICY:
 1A full cap support for BufferLP; or 1B ACTIVE-SET support J_act = {j : lambda_j^num > 1e-9}
    from a feasible full-support numerical point, with n^-(J_act) — much less pessimistic.
 2  Full-support theta_max=0 => chart is BOUNDARY-FEASIBLE (not infeasible): hybrid = binding
    rows (r*_i <= eps_bind(1+||p||_inf)) by exact repair (small Markowitz/modular subsystem),
    nonbinding rows by buffer theta on n_F^- only.
 3  k0 hard dominants (B0, G6=U_A, G7=U_B): after ONE failed full/active buffer attempt,
    Markowitz-plus-repair is the default exact route (k0/B0/near already closed that way).
    k5-9: floor-buffer first (likely true interior margin).
 4  Improved Stage-1 = ACTIVE-BUFFER LP: n_i^-(J) over active support only; Stage-2
    min sum c_j lambda_j at theta_0 = theta_max/2; floor-round only J coefficients.
 5  RepairLP after floor: V = {i : b_i < 0}, J_rep = {j : exists i in V, A_ij < 0}; solve
    A_{V,J_rep} mu <= b_V, mu >= 0 (optional buffer on V); lambda_final = lambda^(Q) + mu;
    exact-check b_final = p - A lambda_final >= 0.
 ConeCert compatibility: UNCHANGED — base := p - A lambda >= 0 exact; target = base +
 sum lambda_j slack_j; checkEq contract untouched.
 DECISION TREE per chart: active-buffer floor rounding (full cap if tractable else active set)
 -> theta>0: round + exact-check -> theta=0: mark boundary-feasible -> Markowitz+repair /
 binding-row repair. NEVER conclude infeasibility from theta=0.

Q2 SKIP MODES (default + canonical Mode B):
 DEFAULT: Mode A first, per chart k, WHOLE inf band. Radial parametrization z = (1-s)u,
 Ptilde_k(s,u) = P_k(s,(1-s)u). (A-): -d/ds Ptilde_k >= 0 on [0,1/2] x Delta => inf band
 covered by s=1/2 boundary/near cert. (A+): +d/ds >= 0 => covered by s=0 FaceCert.
 NO dominance deltas. One Mode-A cert kills all 15 inf regions of chart k.
 MODE B CANONICAL FORM (path domain — now UNBLOCKED for emission): variables (s0, lambda, u),
 path point s1 = (1-lambda)s0 + lambda*b (b = 1/2 decreasing, b = 0 increasing); target
 -+d/ds Ptilde_k(s1,u) >= 0; allowed generators: simplex(u), band (s0 >= 0, 1/2 - s0 >= 0),
 path (lambda >= 0, 1 - lambda >= 0), dominance deltas AT s0 (G^rad_a(s0,u) - G^rad_b(s0,u));
 multipliers Bernstein-positive on box-simplex [0,1/2] x [0,1] x Delta. Soundness: derivative
 sign at every path point + integration along the path; checker needs NO geometric projection
 proof (cert already lives over path variables). Mode B NOT default — only when Mode A fails,
 sign valid on hull, and full InfCert much heavier.
 IMPLEMENTATION ORDER per chart: numeric Mode-A sweep on whole inf band -> one surviving sign
 => attempt Mode-A cert -> success => all 15 regions covered -> fail => full InfCert per
 region; Mode B for a small hard subset only.
 CAUTION (unsound form): +-d/ds >= 0 certified only on the dominance region at the SAME s is
 UNSOUND (path may leave the region). Dominance-local skips are sound ONLY in the Mode-B
 path-domain form.
