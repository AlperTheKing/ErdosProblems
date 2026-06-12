# GPT-5.5 Pro round-21 proof (2026-06-09): T_{2,t,1} & T_{3,t,1} unimodality

Source: ChatGPT "Unimodal Trees Proof" chat (c/6a253e43-8280-83eb-b638-e94c8a851ac1), GPT-5.5 Pro.
Scope: complete human proof of the BRIDGE (H_k≥0 ⟹ unimodal) for m∈{2,3} + the complete m=3 H_k≥0 certificate.
(The uniform all-m proof remains OPEN — slope-ratio S_k/T_k monotonicity; additive-concavity route proven FALSE.)

Setup: U=1+2x, V=1+x, W=U^t+xV^t, N=mt, P=W^m, Q=xU^N, Z=P+Q.
p_k=[x^k]P, q_k=[x^k]Q=2^{k-1}C(N,k-1) (1≤k≤N+1, else 0), z_k=p_k+q_k.
A_k=2^k C(N,k). D^Z_k=z_k²−z_{k-1}z_{k+1}, D^P_k=p_k²−p_{k-1}p_{k+1}.

## PIECE 1 — BRIDGE (H_k≥0 ⟹ T_{m,t,1} unimodal, m∈{2,3})

### B1 (exact identity)  [VERIFIED numerically, m=2 & m=3, 0 mismatches]
D^Z_k = D^P_k + C_k, where
  C_k = q_k² − q_{k-1}q_{k+1} + 2 p_k q_k − p_{k-1}q_{k+1} − p_{k+1}q_{k-1}.
And  H_k = (2k(N−k+2)/q_k) · C_k.
Since q_k>0 and 2k(N−k+2)>0 for 1≤k≤N: **H_k≥0 ⟺ C_k≥0**.

### B2 (D^P_k ≥ 0, i.e. W^m log-concave)  — HOGGAR CONVOLUTION
- W = U^t + xV^t: compute w_k²−w_{k-1}w_{k+1} ≥ 0 for 1≤k≤t; all coeffs w_0..w_{t+1}>0, no internal zeros ⟹ W log-concave.
- **Hoggar's theorem**: if A=(a_i), B=(b_i) nonneg log-concave w/ no internal zeros, convolution c_n=Σ_i a_i b_{n-i} is LC w/ no internal zeros. PROOF (Hoggar identity, out-of-range=0):
    c_k² − c_{k-1}c_{k+1} = Σ_{i≤j} (a_i a_j − a_{i-1} a_{j+1})(b_{k-i} b_{k-j} − b_{k-i+1} b_{k-j-1}).
  Each factor ≥0 because LC+no-internal-zeros ⟹ ratios a_i/a_{i-1} nonincreasing ⟹ a_i a_j ≥ a_{i-1}a_{j+1} for i≤j (same for b). So every summand ≥0 ⟹ convolution LC.
- Apply repeatedly to W^m ⟹ P=W^m log-concave ⟹ D^P_k ≥ 0.

### B3 (prefix-LC + tail ⟹ unimodal)
- D^Z_k ≥ 0 for 1≤k≤N ⟺ z_k² ≥ z_{k-1}z_{k+1} ⟺ adjacent ratios ρ_k=z_k/z_{k-1} nonincreasing (1≤k≤N+1).
- So prefix z_0,…,z_{N+1} is unimodal PROVIDED the last step is nonincreasing: z_N ≥ z_{N+1}.
- z_N ≥ z_{N+1}:  q_N = N·2^{N-1} ≥ q_{N+1} = 2^N  (since N=mt≥2),  AND  p_N ≥ p_{N+1} ≥ p_{N+2} ≥ ⋯ (the P=W^m tail is decreasing). Tail-decreasing via reversed poly W̃(y)=y^d W(1/y), d=t+1 (mode(W^m) ≤ N).
- Combine B1+B2+B3: H_k≥0 (⟹C_k≥0) + D^P_k≥0 ⟹ D^Z_k≥0 ⟹ (with tail) (z_k) unimodal.
- For m∈{2,3}, H_k≥0 holds for all 1≤k≤N (Piece 2 + m=2 already done), so the whole prefix is LC ⟹ Z unimodal.

## PIECE 2 — m=3 H_k≥0 (complete certificate)

Row decomp: p_k=[x^k]W^3 = A_k + 3B_{k-1} + 3C_{k-2} + D_{k-3}, A=U^{3t}, B=(U²V)^t, C=(UV²)^t, D=V^{3t}.
Operator: H_k = H^A + 3H^B + 3H^C + H^D + 2(N+1)A_{k-1}, each H^X = 4k(N-k+2)X_{k-1} − 4(N-k+1)(N-k+2)X_{k-2} − k(k-1)X_k.

### KEY NEW TECHNIQUE — TWO-SIDED coefficient bounds (provide the LOWER bound to KEEP the positive term)
- B=(U²V)^t: from (1+19/12 x)^3 ≤coeff U²V ≤coeff (1+5/3 x)^3 (both verified: U²V−(1+19/12 x)^3 = (1/4)x+(23/48)x²+(53/1728)x³ ≥0; (1+5/3 x)^3−U²V=(1/3)x²+(17/27)x³ ≥0). Raise to t:
    (19/24)^n A_n ≤ B_n ≤ (5/6)^n A_n.
- C=(UV²)^t = (1+4x+5x²+2x³)^t: from (1+34/27 x)^3 ≤coeff UV² ≤coeff (1+4/3 x)^3. Raise to t:
    (34/27 · 1/2)^n A_n ≤ C_n ≤ (4/3 · 1/2)^n A_n = (2/3)^n A_n.   [lower (17/27)^n A_n]
- D=V^{3t}: D_n = (1/2)^n A_n exactly.

### Row bounds (each: keep positive term via lower bound, upper-bound negatives; case analysis by k)
- (b2) reserve: H^A + 2(N+1)A_{k-1} ≥ (22/3) k A_k  [exact A-ratio algebra, N=3t].
- (bB) 3H^B ≥ −4 k A_k.
- (bC) 3H^C ≥ −k A_k.
- (bD) H^D ≥ −(1/3) k A_k.  (D exact binomial; case analysis: small k explicit; k≥12 tail bound Y_k=(k-1)(5k²-13k+12)/96 · 2^{-(k-4)} decreasing, Y_12=33/128<1/3.)
Sum: H_k ≥ (22/3 − 4 − 1 − 1/3) k A_k = 2 k A_k > 0.

The bB/bC proofs (s=N-k+1): split into k-ranges (e.g. 6≤k≤13 via convex-quadratic Q_k(s) in s, Q_k'(1)>0 & Q_k(1)>0 at boundary k; 14≤k≤21 via B*_k≤B*_14<3; k≥22 cruder tail: drop positive, T_k=(k-1)(7k-6)/6·(2/3)^{k-3} decreasing). Explicit rational checks at boundary k-values (k=10: 8746021846/10460353203>0; k=13: 578.../205...>0).

## FORMALIZATION STATUS / PLAN
- B1: pure algebra (q-ratios q_{k-1}/q_k=(k-1)/(2(N-k+2)), q_{k+1}/q_k=2(N-k+1)/k + the C_k formula) — formalizable via linear_combination.
- B2 (Hoggar): the convolution-LC identity = the BIGGEST piece (double sum, no Mathlib API). Elementary but long.
- B3: ratios-nonincreasing + tail-decreasing — formalizable (sequence manipulation).
- m=3 two-sided bounds: coefficientwise domination BOTH directions (have the upper via raised_dom_m3a/b; need the LOWER, e.g. (1+19/12 x)^3 ≤coeff U²V raised to t) + the case analysis (large; many k-range lemmas).
- NOTE: full "T_{m,t,1} unimodal" also needs graph↔poly identity I(T)=Z (separate graph-theory layer); achievable Lean deliverable = the ANALYTIC theorem "coeffs of W^m+xU^N unimodal".

## m=3 bB/bC FORMALIZATION ROUTE (verified this session — my own crude route, simpler than GPT's k-range cases)
**m3_bB (3H^B ≥ -4kA_k):** H^B=4k(N-k+2)B_{k-1}-4(N-k+1)(N-k+2)B_{k-2}-k(k-1)B_k, B=(U²V)^t.
- pos: B_{k-1} ≥ (19/12)^{k-1} C(3t,k-1) [raised_dom_m3a_lower]; C(3t,k-1)=k C(3t,k)/(N-k+1) [Cq_down]; (N-k+2)/(N-k+1)≥1 ⟹ pos ≥ 4k²(19/12)^{k-1} C(3t,k).
- neg: B_{k-2}≤(5/3)^{k-2}C(3t,k-2) [raised_dom_m3a], C(3t,k-2)=k(k-1)C(3t,k)/((N-k+1)(N-k+2)) [c_chain2] ⟹ 4(N-k+1)(N-k+2)B_{k-2} ≤ 4k(k-1)(5/3)^{k-2}C(3t,k); B_k≤(5/3)^k C(3t,k).
- ⟹ 3H^B ≥ C(3t,k)·k·[12k(19/12)^{k-1} − 12(k-1)(5/3)^{k-2} − 3(k-1)(5/3)^k]; and -4kA_k=-4k·2^k·C(3t,k).
- SUFFICES scalar **S_B(k) = 12k(19/12)^{k-1} − 12(k-1)(5/3)^{k-2} − 3(k-1)(5/3)^k + 4·2^k ≥ 0** — VERIFIED k≤399 (0 fails, min 20). Prove by induction (2^k dominates; 2>5/3>19/12).
**m3_bC (3H^C ≥ -kA_k):** analogous, C=(UV²)^t, j=2 shift (C at k-2,k-3,k-1); lower (34/27) [raised_dom_m3b_lower], upper (4/3) [raised_dom_m3b]; derive the analogous scalar S_C(k)≥0 + assemble.
Then **m3_Hk_nonneg**: H_k = (H^A+reserve) + 3H^B + 3H^C + H^D ≥ (22/3 − 4 − 1 − 1/3)kA_k = 2kA_k, from m3_b2 + m3_bB + m3_bC + m3_bD (linear combo, like m2_Hk_nonneg).

## PROGRESS + bC CAUTION (2026-06-09 interactive, continued)
**FORMALIZED + VALIDATED (galvin_dom.lean 941 lines, 0 sorry):** `scalar_SB` (the bB scalar S_B(j+2)≥0,
interval_cases j<18 + decay induction) — in addition to bridge B1, m=3 lower bounds, m3_b2, m3_bD.
**m3_bB ASSEMBLY (clean, NEXT):** boundPos `4k(N-k+2)B_{k-1} ≥ 4k²(19/12)^{k-1}C(3t,k)` [raised_dom_m3a_lower
+ Cq_down + (N-k+2)/(N-k+1)≥1]; boundNeg1 `4(N-k+1)(N-k+2)B_{k-2} ≤ 4k(k-1)(5/3)^{k-2}C(3t,k)` [raised_dom_m3a
+ c_chain2]; boundNeg2 `k(k-1)B_k ≤ k(k-1)(5/3)^k C(3t,k)` [raised_dom_m3a]; ⟹ 3H^B ≥ k C(3t,k) S_B(k) ≥ 0
(scalar_SB), and -4kA_k=-4k2^k C(3t,k) ⟹ done.
**★ bC CAUTION:** the analogous crude route for bC does NOT give a clean single scalar — the positive term
4k(N-k+2)C_{k-2} lower-bounded gives 4k²(k-1)(34/27)^{k-2}C(3t,k)/(N-k+1) (the (N-k+2) cancels, leaving a
N-DEPENDENT /(N-k+1) factor ≤1, weak for small k), while the negatives are worst for k near N — opposite-end
worst cases, no single worst k. So bC needs GPT's k-range CASE ANALYSIS (Cases 1-5 in this doc, the
convex-quadratic Q_k(s) in s=N-k+1 + boundary rational checks), NOT a crude scalar. Formalize bC via GPT's cases.
