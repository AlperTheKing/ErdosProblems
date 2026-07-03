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

## ADDENDUM 2 (2026-07-03, reply 3): (CD) PROOF DELIVERED
(1.1) PROVEN: nu_K(S) >= 25*sigma(S) for EVERY valid completed switch (neutral: gamma-min;
sigma>=1: new bad lengths >= 5 by tri-free ⟹ nu >= 25|dB| - K_S ⟹ nu_K >= 25|dB| +
K_S(sigma-1) >= 25 sigma). COMPLETION LOSS TELESCOPE (2.1-2.4): per-op slack-loss residuals
tau_a >= 0 summed: 25 sigma^0(I_i) <= 25 sigma(S_i) + Sigma tau_a <= nu_K(S_i) + R_i.
Section 3 identifies each op residual with an allowed ledger (op1 segment absorption, op2
terminal prefix/suffix closure — THIS produces the cumulative prefixes Codex observes! —
op3 co-B closure, op4 twin, op5 FLAT5 → cell ledger). Tail: 'this completes the Bank-L
proof route and therefore the Branch-B Banked-UPO assembly.'
RECONCILIATION with Codex 18:35Z finding: width-2 raw gate UNSAT=39 is EXPECTED — the
completion of Comp([i,i+2]) ABSORBS the row prefix when f crosses (op2 on f's own row),
yielding path_interval(0,k)/endpoint-singleton forms = exactly the battery certificates.
Codex must implement op1-op5 EXACTLY and re-gate; remaining UNSATs after full completion
(if any) → relay. MY AUDIT PENDING: op2/op5 residual details (reply slices C5-C9) before
final acceptance; then FULL BRANCH-B ASSEMBLY RE-AUDIT.

## ADDENDUM 3 (2026-07-03): COMPLETE (CD) PROOF — user-relayed full text (authoritative)
(1.1) nu_K(S) >= 25 sigma(S) PROVEN (neutral: gamma-min; sigma>=1: nu >= 25 dB - K_S ⟹
nu_K >= 25 dB + K_S(sigma-1) >= 25 dB >= 25 sigma). (2.2) rho_a = 25[sigma-drop]_+ per op;
telescope (2.4) ⟹ (CD-i) with R_i = Sigma rho_a. OP DETAILS: op1 seg absorption (3.2);
op2 TERMINAL CLOSURE with witness argument — new bad edge p_t p_{t+1} has odd-cycle witness
via the closed walk p_t..p_0, g, p_{l-1}..p_{t+1} so lambda <= ell(g), and >= 5 by tri-free;
SHORTESTNESS used (shorter witness would contradict P shortest); op3 NONCROSSING + CO-B
CLOSURE — kills 'unwitnessed lane doors' (every shortest row meets the switch in empty /
one interval / terminal prefix / terminal suffix; complement B-connected via exterior
anchor absorption); op4 twin closure (quotient-invariant); op5 FLAT5 extraction handoff
(3.10): 25 sigma(before) <= 25 sigma(after) + 25 pi(A) + rho_cell(A), cell surplus
|C_A|^2/25 - 3 >= 0 + archived fan/cactus global ledger (Pi_fan <= |dB(F_u)|,
Pi_cell <= eta/2). §4 VALIDITY: switch + complement B-connected, all new bad edges
witnessed, nu/K/nu_K well-defined. §6: IF the residual dictionary is restricted, the ONLY
remaining machine obligation = DICTIONARY INCLUSION (6.1): each rho_a lies in
cone(tri-free, terminal-prefix, noncrossing, twin, protected-cell residuals) — finite
LP/Farkas per op. §7: lane certificate lambda_7=11/100, lambda_9=7/100, lambda_11=3/100;
with L>=13 + P_Q<=0 + sparse + detour + cell ledger: **Bank-L route COMPLETE ⟹ Branch-B
Banked-UPO assembly COMPLETE** (modulo (6.1) gating + full-completion re-gate + my audit).
CODEX TAXONOMY MESH (its 17:55/18:05 posts): free 3688 / tight 34 / clean-damage 9731 /
clean-nuK-escape 7 (dense m=2 mini-pattern, terminal switch nu_K=98 pays 47) / residue 787
— its 'damage-or-terminal-nuK' two-branch = exactly the raw-exchange side + completed-
switch side of (CD); the 7 escapes and 787 residue rows are covered by terminal completed
switches per op2/op3 (its own v2 certificates confirm: singleton/path_interval(0,1)
terminal switches).
