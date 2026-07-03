# Bank-L: Complete Proof modulo the Low-Length Lane Coarea Lemma (GPT-Pro, 2026-07-03)

## PROVEN THIS REPLY
**Lemma 1 (row-neighbor spacing)**: on p=1,h=0 rows every x ∈ R has k_x ≤ 2 row-neighbors;
k_x=2 ⟹ A(x) = {q_i, q_{i+2}} exactly. Proof: all Q→R edges blue ⟹ A(x) one parity class
(no consecutive); j−i > 2 gives the shorter blue path q_0..q_i x q_j..q_{L−1} of length
L−1−(j−i)+2 < L−1, contradicting shortestness; 3 neighbors force distance ≥ 4. ∎
⟹ **d ≤ 2r** (1.1).
**Case L ≥ 13 PROVEN**: m−1 ≤ r²/25 + d/2 ≤ r²/25 + r ≤ r²/25 + 2Lr/25 (needs L ≥ 25/2). ∎
**Case P_Q ≤ 0 PROVEN** (identity −Δ_Q = ρ_Q − P_Q, ρ_Q ≥ 0). ∎
**Hard set exact**: L ∈ {7,9,11}, p=1, h=0, P_Q > 0 ⟺ d > 4Lr/25 (possible only ≤ 11 by
d ≤ 2r). R-stratification R_0/R_1/R_2 by k_x: d = |R_1| + 2|R_2|; P_Q > 0 forces many
R_2 = LANE vertices ({q_i,q_{i+2}} attachments) — the structural source of switch certs.

## THE ONE REMAINING FINITE LEMMA — (Lane coarea)
For L ∈ {7,9,11}, p=1, h=0, P_Q > 0: with S_i = Comp([i,i+2]) the completed interval
switches (i = 0..L−3; completion = interval + B-connected row segments + terminal
prefixes/suffixes + noncrossing + twin + FLAT5 extraction):
  **P_Q ≤ Σ_{i=0}^{L−3} λ_i ν_K(S_i) + R_Q^lane,  λ_i ≥ 0, R ≥ 0.  (Lane coarea)**
Averaging form: max_i ν_K(S_i) ≥ P_Q / C_L for explicit C_L. Mechanism: lane vertex x
witnesses a blue detour q_i−x−q_{i+2}; flipping S_i trades the two row edges at q_{i+1} via
the lane; gamma-min makes ν_K(S_i) ≥ 0 record exactly the lane pressure. One-switch battery
certificates = extreme rays of this cone.

## Assembly (§8)
Case 1 L≥13 ✓; Case 2 P_Q≤0 ✓; Case 3 = (Lane coarea) ⟹ ρ_Q ≥ P_Q ⟹ Bank-L. Then
Bank-L + H_BD-overfull + cell ledger ⟹ Banked-UPO ⟹ GERSH_{L>5}.

## Machine obligations
1. Codex: per hard row emit the (Lane coarea) identity — LP over ≤ L−2 interval switches
   (TINY support: 5/7/9 switches for L=7/9/11) + R; any UNSAT → instant relay. Battery has
   10525 rows, only 31 signatures.
2. GPT-Pro next: prove (Lane coarea) per length (finite; C_7, C_9, C_11 explicit).
3. Claude: audit emitted lane identities; stress the lemma on klane constructions (R_2-heavy).

## ADDENDUM (2026-07-03, reply 2): LANE COAREA PROVEN MODULO (CD)
PROVEN STEPS: (1.2) P_Q <= (25-2L)*n_2 (only genuine lane vertices supply pressure; n_1
coefficient 25/2-2L < 0 for L>=7); (2.2) Sigma_i sigma_i^0 >= 4*n_2 (each lane vertex >= 4
blue boundary incidences over the interval family; row edges give 2L-8, f costs 2, net
2L-10 >= 4 for L >= 7); ⟹ (2.3) **P_Q <= kappa_L * Sigma sigma_i^0 with kappa_7=11/4,
kappa_9=7/4, kappa_11=3/4 — RAW LANE COAREA PROVEN.**
REMAINING BRIDGE: **(CD) completion dominance**: 25*Sigma sigma_i^0 <= Sigma nu_K(S_i) + R,
R >= 0 (residuals: nu_K slacks, detour deficits, FLAT5 extraction slack, noncrossing
closure residual). CORE ARGUMENT SKETCHED: a raw interval that is already a valid connected
switch has nu_K(I_i) >= 25*sigma_i^0 directly — case delta_M(I_i)=0: every new bad edge has
odd-cycle length >= 5 so nu >= 25|delta_B| >= 25 sigma^0; case delta_M(I_i)=1 (f crosses,
K=L^2): nu_K >= 25(sigma^0+1) - L^2 + L^2*sigma^0 >= 25 sigma^0 + (25 + L^2(sigma^0-1))
>= 25 sigma^0 when sigma^0 >= 1, and gamma-min handles sigma^0=0. Completion repairs
non-valid intervals WITHOUT losing raw slack (transfer + nonneg residuals) = the exact
content of (CD), per-instance certified by Codex's interval-switch LP.
FINAL FORM (4.1): P_Q <= mu_L * Sigma_i nu_K(S_i) + R with **mu_7=100/11, mu_9=100/7,
mu_11=100/3**; one-switch constants C_L = mu_L*(L-2): C_7=500/11, C_9=700/7=100, C_11=300.
ASSEMBLY COMPLETE MODULO (CD): raw coarea (proven) x (CD) ⟹ (4.1) ⟹ Bank-L case 3.
Battery facts consistent: hard set L=7:10311, L=9:214, L=11:0; max P_Q/rho_Q = 69/116.
