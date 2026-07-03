# GPT-Pro Attempt-9: Attachment Monotonicity (AM) Theorem — with gate results

Source: thread 6a450f06, 2026-07-02. Full text held by user/Claude; this records the
operative content + Claude's exact-gate results.

## Statement (AM)
Passive attachment := positive-flow bag outside the seed core, in one of the 3 blue interior
C5-classes, incident ONLY with blue/cut edges, creating NO new bad door. (Bad-door-creating
attachments must first be absorbed into the seed core — see §5 caveat below.)
For seed S ∈ {EQ, SIB} with positive bag weights w_0..w_9 satisfying its seven max-cut
inequalities, active overfull rows Q*_EQ=(7,5,8,6,9), Q*_SIB=(1,6,8,4,9); H = S + any finite
family of passive attachments. Then for every shortest row Q of an original seed bad door:
    I_H(Q) − N_H ≤ I_S(Q*) − N_S.                                   (AM)

## Proof skeleton
1. UNIVERSAL-BAG DOMINATION: the 3 interior active-row bags have full adjacent-layer
   neighborhoods, so every passive attachment's neighborhood is contained in the corresponding
   universal bag's; attachment rows are dominated row types.
2. Exact path-partition formula: s_H(r) = Σ_{ab∈M_S} w_a w_b · D_ab^{(r)}(z) / (W_r · D_ab(z)),
   endpoints s_H(a)=Σ w_b. Row excess E_H(Q)=I_H(Q)−N_H is an explicit rational function.
3. M-cert: 𝒟_{S,Q}·Δ_{S,Q} = P⁺ + Σ_{j=1..7} F_j·P_j + E_S(Q*)·P_8, all P's coefficient-
   nonnegative after w_i=1+x_i, z_σ=y_σ ≥ 0. F_j = the seven seed max-cut inequalities.
   FINITE LIST: 3 layers × (2²−1)² = 27 passive signatures per seed; row types: EQ 3+3+5=11,
   SIB 5+5+3=13. Simultaneous certificate: 27 attachment variables per seed.
4. Attachment-on-row case: covered by the same list via the 1/W_Z representative factor.
5. ABSORPTION (non-passive attachments): new-bad-edge bags absorbed into core; then either
   contracts to EQ/SIB, or ≥4 effective bad doors ⟹ "cannot be overfull" via PROPER-MASK
   inequalities (two disjoint proper terminal masks active; summing flip inequalities).
6. ODL chain: AM + seed certs (I_S−N_S ≤ (2/3)η_S) + m_G=m_S + η_G≥η_S ⟹ ODL for all N.
7. H_3⁺ check: 33/80 < 2 < η_G ✓ (matches Claude's exact verification).

## CLAUDE GATE RESULTS (2026-07-02)
- §1 EQ: VERIFIED EXACT. Classes V0={1,7},V1={3,5},V2={0,8},V3={4,6},V4={2,9} valid
  (all edges consecutive); bags 5,8,6 all FULL adjacent-layer neighborhoods. EQ M-cert grind
  (27 signatures × 11 rows) can proceed.
- §1 SIB: **VERIFIED (after correction, 2026-07-02 06:43Z).** My earlier "refutation" used a
  SHELL-MANGLED graph6 string (backtick corruption in powershell→python -c; the decoded list had
  triangles — impossible for census). With the correct string ('I?'+chr(96)+'FAo]]?'): 16 edges,
  0 triangles, GPT-Pro's classes V0={1,2},V1={5,6},V2={0,8},V3={3,4},V4={7,9} have 0 violations,
  and ALL universal bags FULL: bag6 {0,1,2,8}, bag8 {3,4,5,6}, bag4 {0,7,8,9}. AM §1 holds on
  BOTH seeds; SIB M-cert grind (27×13) UNBLOCKED. ⚠ Tooling rule: build graph6 strings with
  chr()/files in shell contexts, never inline backticks.
- §5 DEPENDENCY FLAG: the absorption argument USES the PROPER-MASK LIFT (A1) — the dependency
  graph is ODL ⟸ AM + seed certs + absorption(⟸ A1 + "≥4 doors not overfull"). The ≥4-door
  claim is battery-consistent (census: all overloaded components have m_C=3) but the summed-
  flip-inequality argument is a sketch needing exact form.
- Empirical AM spot-gate (EQ 3-blowup): pure overload 2 → z(V2) 33/80 → bag2(V2) −202/187 →
  z(V3) 6/11, all monotone-OK; V1-attachment variant breaks max-cut (out-of-family). ✓

## ADDENDUM (2026-07-04): AM-§5 ABSORPTION + C5-RS ASSEMBLY TREE (GPT-Pro)
ATTACHMENT TAXONOMY: passive = interior class (V1/V2/V3) + all-blue incident + no bad door +
one-layer signature (= AM-§1 scope, proven). TYPE A (new-bad-door attachment): absorb the
door into the bad-door core (bookkeeping only — G, cut, s_i, m, N, eta unchanged);
re-saturate; 3-door saturated core → EQ/SIB seed branch; >=4-door → AM-§5 A1-absorption
theorem (X(A) mask inequality covers the extra doors; algebra ⟹ ODL). TYPE B (boundary
class V0/V4 attachment): positive-flow boundary bag is necessarily an endpoint of a bad
door ⟹ Type A. C5-RS ASSEMBLY (§8): P = {i: s_i > tau}; P proper ⟹ A1-soft branch
(needs beta_P <= 1 or PMTS residual); P = Z5 ⟹ ODL branch: I(Q) <= N immediate, else
overfull C5-hom → saturate doors → {3-door: seed certificates (EQ: height+CERT-1 proven+
CERT-2 LP; SIB: S7 program) + AM-passive | >=4-door: A1 absorption}. CAVEAT (tail): the
absorption threshold needs A1 pair-residual UNIFORMLY or a finite gate for N <= 50.
STATUS TREE: A1 (PMTS-LP spec ready, battery queued) + ODL (seeds: EQ 2/3 done, SIB S7
in progress; AM-§1 proven; AM-§5 = this addendum, absorption algebra stated) ⟹ C5-RS ⟹
net-DW' ⟹ GERSH_{L=5}.

## ADDENDUM 2 (2026-07-03): (A1-5mask) — PAIR RESIDUAL ELIMINATED, N<=50 GATE GONE
My exact gate: N>=9 closes (5/4)(25/N+7/30) <= 1+25/N; saturated 4-door forces N>=10
(cyclic prefix ineqs n_i n_{i+1} >= m_C (max-cut prefix flips, e(V_i,V_{i+1}) >= m_C) =>
prod n_i >= m_C^{5/2}, AM-GM N >= 5 sqrt(m_C) >= 10; exhaustive small check 0 cex).
THEOREM (uniform 4-door absorption): saturated C5-hom all-l5 core, >=4 effective doors =>
X(Omega) = I(Q)-N+25\bar\eta/N; five 4-masks A_i = Z5\{i}; A1-4: X(A_i) <= (25/N+7/30)\bar\eta;
sum = 4X(Omega) <= 5(25/N+7/30)\bar\eta => X(Omega) <= (1+25/N)\bar\eta = ODL-X => ODL.
ELIMINATES: N<=50 finite gate, pair-separation residual lemma, complementary-pair route.
REMAINING AM-5 CERT FAMILY: exactly the five 4-mask PMTS certificates per core shape,
(25/N+7/30)\bar\eta - X(Z5\{i}) in PMTSCone(Z5\{i}), residuals >= 0. Codex battery scope
SHRINKS to 4-masks with the uniform 7/30 coefficient.
