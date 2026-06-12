# Proof Document — Erdős #993 (tie-fugacity route), status-tagged

**Status legend:** `conjecture` · `heuristic` · `sketch` · `rigorous-informal` (referee-checked) ·
`formally-verified` (Lean 4, sorry-free, `native_decide`-free, axioms `[propext, Classical.choice, Quot.sound]`) ·
`verified-computation` (exact arithmetic).

Lean sources: `formal-conjectures/ltb_main.lean`, `mixed_oneleaf.lean`, `emspider.lean`,
and `FormalConjectures/ErdosProblems/993.lean` (PR google-deepmind/formal-conjectures #4192).

---

## 0. Problem  — `conjecture` (open)
For every finite tree `T`, the sequence `i_k(T)` = #(independent `k`-sets) is unimodal.
Lean: `Erdos993.erdos_993` (statement, `sorry`).

## 1. Reduction framework  — `rigorous-informal` (B. Rey manuscript, cited; not re-proven here)
Write `I_T(x)=Σ i_k x^k`, `μ_T(λ)=λI_T'(λ)/I_T(λ)`. With `m` the leftmost mode and
`λ_m=i_{m-1}/i_m`, unimodality in the `d_leaf≤1` regime follows from
**(A)** `μ_T(1)<n/3` [manuscript, `d_leaf≤1`] and **(B)** the tie-fugacity inequality `μ_T(λ_m)≥m−1`,
since `λ_m≤1` and `μ_T` is increasing. The general case needs a Hub-Exclusion/Transfer reduction to
`d_leaf≤1` [manuscript; open in full]. **We contribute machine-checked proofs of (B) for the
extremal single-hub families, in a mode-free closed form, plus new double-spider structure.**

## 2. Mode-free local tie-balance — the formalizable target  — `rigorous-informal`
For coefficient sequence `c` of a tree and any `r` with `c_r≤c_{r+1}` (a *rising tie*), set
`λ_r=c_r/c_{r+1}`. Then `μ(λ_r)≥r ⟺ N_r:=Σ_t (t−r)c_t c_r^t c_{r+1}^{D−t} ≥ 0` (`D=deg I`).
Carrying the rise hypothesis (never identifying the mode) makes this directly formalizable; at the
mode it specialises to (B). [GPT-5.5 Pro reframing; refereed.]

## 3. Equal-arm spider `S(2^k)`  — `formally-verified`
`c_t = 2^t\binom{k}{t}+\binom{k}{t-1}`, `I=(1+2x)^k+x(1+x)^k`.
**Thm `SpiderLTB.equal_spider_local_tie_balance (k r)(hr:r<k)(hrise:c_r≤c_{r+1})`:** `N_r≥0`.
Proof skeleton (all FV): gen.fn. `genfn_iseq`; weighted `wgenfn`; Step-1 split
`λI'−rI = X·A+Y·B` (`X=(1+2λ)^{k-1}>0`, `A≥0` at tie, `Y=λ(1+λ)^{k-1}>0`); `B≥0` trivial,
`B<0` via Bernoulli (`one_add_mul_le_pow`) reducing to `C≥0`; the positivity certificate
`M·L·(M+L)·C = Cnum = (s+1)(P+G·H)`, `P` all-nonneg coeffs (`cnum_cert` by `ring`, `positivity`).
Certificate independently checked in `search993/verify_gpt_localtie.py` (Schwartz–Zippel, 0 mismatch).

## 4. One-leaf mixed spider `S(2^a,1)`  — `formally-verified`
`c_t = 2^t\binom{a}{t}+(2^{t-1}+1)\binom{a}{t-1}`, `I=(1+2x)^a(1+x)+x(1+x)^a`.
**Thm `Erdos993.MixedOneLeaf.mixed_spider_one_leaf_local_tie_balance (a r)(hr:r<a)`:** `N_r≥0`,
**unconditional** (all `r`, no rise hypothesis). Same skeleton; `A` quadratic; positive `Cnum`
(131 monomials) with **no rise-gap term** (hence unconditional). Certificate checked in
`search993/derive_oneleaf.py` (Step1, tie, `A≥0`, `Cnum=(s+1)·Ppoly` nonneg, `hW·M²(M+L)=Cnum`).

## 5. Symmetric double-spider factorization  — `formally-verified` (+ tree link `verified-computation`)
**Lemma `EmSpider.symm_double_spider_factor (m x)`:**
`(1+2x)^{2m+1}+2x(1+x)(1+x)^m(1+2x)^m+x²(1+x)^{2m} = E_m·F_m`,
`E_m=(1+2x)^{m+1}+x(1+x)^m`, `F_m=(1+2x)^m+x(1+x)^m=I_{S(2^m)}`.
Proof: with `a=(1+2x)^m,b=(1+x)^m`, LHS=`(1+2x)a²+2x(1+x)ab+x²b²`, RHS=`((1+2x)a+xb)(a+xb)`,
equal since `2(1+x)=(1+2x)+1` (`ring`). **`verified-computation`:** the closed form equals the actual
tree `D(m,m,3)`'s independence polynomial (`search993/verify_double.py`, graph DP, 0 mismatch).
Consequence: `μ_{I} = μ_{E_m}+μ_{F_m}` (mean additive over products).

## 6. Factor `E_m` local tie-balance  — `formally-verified`
`c_t = 2^t\binom{m}{t}+(2^t+1)\binom{m}{t-1}`. **Thm `EmSpider.em_factor_local_tie_balance (m r)(hr:r<m)`:**
`N_r≥0`, unconditional. `A` linear (`A≥0` trivial via `Araw=2(S+2)L−rM` all-positive); Bernoulli
carries an extra `(1+2λ)` factor; positive `Cnum` (131 monomials). Certificate: `search993/derive_Em.py`.

## 6b. LOG-CONCAVITY route (2026-06-07) — supersedes tie-fugacity for these families
**Key theorem (cited):** the product of two polynomials with positive log-concave coefficient
sequences (no internal zeros) has positive log-concave coefficients — `rigorous-informal`/`cited`
(Karlin, *Total Positivity*, 1968 — PF₂ sequences closed under convolution; Stanley 1989 survey).
`verified-computation`: 36,052 random positive-log-concave pairs, 0 convolution failures.

**Symmetric double-spider `D(m,m,3)` is unimodal** — clean proof, no product certificate:
- `I_{D(m,m,3)} = E_m·F_m` — **`formally-verified`** (`symm_double_spider_factor`) + tree link `verified-computation`.
- `F_m = S(2^m)` independence polynomial is log-concave — **`formally-verified`** (`spider_logconcave.lean`),
  also `cited` (arXiv 2501.04245, all spiders log-concave).
- `E_m` coefficients `e_t = 2^t\binom{m+1}{t}+(2^t+1)\binom{m}{t-1}` are log-concave — `verified-computation`
  (m≤11); `rigorous-informal` (same binomial-log-concavity certificate pattern as `spider_logconcave`;
  full Lean formalization mechanical, not yet done).
- ⟹ `I_{D(m,m,3)}` log-concave (cited convolution theorem) ⟹ **unimodal** (log-concave ⟹ unimodal, trivial).

**Empirical structural finding** (`verified-computation`, networkx, `n≤20`): every `d_leaf≤1` tree was
log-concave through `n≤20` (77,143 trees) — but this sample was too small.
- ~~`conjecture`: `d_leaf≤1 ⟹ log-concave`~~ — **REFUTED (2026-06-07), `verified-computation`.**
  Counterexample: Galvin's `T_{3,4,1}` (root → 3 hubs → each 4 length-2 arms; `n=28`, `d_leaf=1`).
  `I = I_w³ + x(1+2x)¹²`, `I_w = (1+2x)⁴+x(1+x)⁴` = spider `S(2⁴)`; coefficient tail `…,37220,5410,60,1`
  violates log-concavity at `k=14` (`60² < 5410·1`) — yet the sequence is **unimodal** (mode `k=9`).
  Triple-verified (tree DP + structural closed form `I_w^m+x(1+2x)^{tm}` + exhaustive `d_leaf≤1`
  enumeration). Consistent with Kadrawi–Levit (arXiv:2305.01784, trees not always log-concave from
  order 26) and Galvin's family (arXiv:2502.10654). **Consequence: no log-concavity route can establish
  #993 even in the `d_leaf≤1` regime; only a unimodality-specific argument (tie-fugacity / mode-mean,
  §2–§6) can.** The §6b `D(m,m,3)=E_m·F_m` shortcut survives only for that specific factored family
  (both factors happen to be log-concave); it does not extend to the `d_leaf≤1` class.

## 6c. Hub-of-spiders `T_{m,t,1}` unimodality — reduced to one verified inequality  — `rigorous-informal` / target OPEN
`T_{m,t,1}` (root → `m` children, each a spider `S(2^t)` of `t` length-2 arms) is the Galvin family that
refutes §6b. Its independence polynomial is `Z = W^m + xU^N`, `W=U^t+xV^t` (`=I_{S(2^t)}`), `U=1+2x`,
`V=1+x`, `N=mt` — `verified-computation` (tree DP = closed form). It is **always unimodal** (`verified-computation`,
`galvin_tie_scan`, m,t≤75) but NOT always log-concave. Reduction (GPT-5.5 Pro rounds 12–16, refereed):
- **Lemma B** (`rigorous-informal`): `mode(W^m)≤mt`, so `z_k=p_k` is decreasing for `k≥N` (W has rightmost
  mode `≤t`; modes add under products of log-concave sequences). Easy.
- **Lemma A** (`verified-computation`, t≤100): prefix log-concavity `z_k²≥z_{k-1}z_{k+1}` for `1≤k≤mt`.
- Lemma A + Lemma B + transition ⟹ `T_{m,t,1}` unimodal (prefix-LC + tail-monotone). **Sound.**
- **Sufficient target `H_k≥0`** (`verified-computation`, ROBUST: 690 (m,t) pairs, m∈[2,7], t∈[2,120], 0 fail):
  `H_k = 4k(N-k+2)p_k − 4(N-k+1)(N-k+2)p_{k-1} − k(k-1)p_{k+1} + 2(N+1)q_k`, `q_k=2^{k-1}\binom{N}{k-1}`.
  `H_k≥0 ⟺ C_k:=D^Q_k+Cross_k≥0`; with `D^P_k≥0` (W^m log-concave) this gives Lemma A. `H_k` is fraction-free
  and linear in `p`. **OPEN:** a hypergeometric inequality (`p` Krawtchouk-type, `m,t` exponents); GPT stalled
  (rounds 13–17). **Refuted strengthenings (do not retry):** the `y`-graded grouped-defect `Δ_{h,k}≥0`
  (small-case artifact, false at t≈40); TP₂ ladder (mixed minors); monotone-ratio `p_k/q_k` (non-monotone).
  Verification: `search993/{verify_Ck,verify_Ck_ext,verify_Hk2,galvin_largeT}.py`.
- *Novelty:* if `H_k≥0` is proved, `T_{m,t,1}` unimodality is a genuinely-new result — the first proof of
  #993 for a family that is provably NOT log-concave, via a prefix-LC + tail-monotone method. OPEN.
- **Uniform `H_k≥0` / prefix-LC route is DEAD for large `m`** (2026-06-07b): `H_k≥0` fails (m=10,t=1),
  prefix-LC fails (m=173,t=13); the clean Maclaurin row-domination `[x^n]R_j ≤ C(N,n)(2-j/m)^n`
  (`= A·(1-j/(2m))^n`; reproduces the m=3 dampings) is **provably too loose near `k=L`** (`verify_maclaurin.py`:
  the induced `Ψ_k` bound is hugely negative there, since the dominant rows of `W^m` near `k~2N/3` are the
  middle ones, not `j=0`). So row-domination proves only small `m` (m=2,3).

## 6d. One-crossing route  — concavity REFUTED; mode-order proven; sign-dominance is the target (2026-06-07b)
`Z=P+Q`, `P=W^m` (mode `a`), `Q=xU^N` (mode `b`), `Δz_k=ΔP_k+ΔQ_k`.
- **`heuristic`→REFUTED:** I first proposed `z` additively CONCAVE on the inter-mode window (`Δ²z_k≤0`),
  "verified" by `quick_onecross.py` (m≤1000, t≤13). **FALSE** — I tested only `t∈{3,6,10,13}`, MISSING
  `t=1,4,5`. GPT-5.5 Pro gave exact counterexamples (`m=100,t=1`: `Δ²z_68>0`; `m=1000,t=4`: `Δ²z_2668>0`)
  and proved the inter-mode window is NOT `O(1)`-wide: `b-a ~ m(ρ_Q-ρ_P)`, `ρ_Q-ρ_P=2^{t-1}(t-6)/(3(3^t+2^t))`,
  linear in `m` for `t>6` (so `|a-b|≤6` was a small-`m` artifact). Concavity is asymptotically false. RETRACTED.
- **`rigorous-informal` (GPT, Darroch): `mode(W^m) ≤ mode_max(xU^N)` for `t≥6`.** Row
  `P^{(j)}=x^j(1+2x)^{N-jt}(1+x)^{jt}` is real-rooted (Poisson–binomial) with mean `2N/3+j(1-t/6)≤2N/3`
  (`t≥6`); Darroch ⟹ each row mode `≤2N/3+1≤mode_max(Q)`; `P=`nonneg combo ⟹ nonincreasing from `mode_max(Q)`.
- **`verified-computation`/proof target — SIGN-DOMINANCE:** on the conflict zone `[min(a,b),max(a,b))` prove
  the increasing component dominates the decreasing one: **`Δz_k≥0`** there. With `Δz≥0` below + `≤0` above
  ⟹ single crossing ⟹ `Z` unimodal. CAVEAT: SUFFICIENT but possibly too strong (fails if `mode(z)` is
  strictly inside the conflict zone). Verified at scale via `search993/onecross_scan.cpp` (C++ exact,
  multithreaded, t=1..40, large m) — checks both `signdom` and ground-truth `unimodal`. [status: under verification]

## 6e. Lean: coefficient-domination foundation + row decomposition  — `formally-verified` (2026-06-07b/c)
`formal-conjectures/galvin_dom.lean` (sorry-free, no `native_decide`, axioms `[propext, Classical.choice,
Quot.sound]`, ~20 decls). Reusable engine: `Dom`/`NN` predicates; `dom_mul`/`dom_pow` (coeff-domination of
nonneg-coeff polynomials is preserved under products/powers); `coeff_one_add_C_mul_X_pow`
(`[x^n](1+cx)^N = c^n C(N,n)`); `raised_dom_general` (`Dom P ((1+cx)^d) ⟹ [x^n]P^t ≤ c^n C(dt,n)` — covers
GENERAL m). **Mixed-row bounds:** `raised_dom_m2` (`[x^n]((1+x)(1+2x))^t ≤ (3/2)^n C(2t,n)`), `raised_dom_m3a`
(`≤ (5/3)^n C(3t,n)`), `raised_dom_m3b` (`≤ (4/3)^n C(3t,n)`). **`Wpoly`/`Wpow_rowdecomp`:** the binomial
row decomposition `W^m = Σ_{j≤m} C(m,j)·x^j·((1+2x)^{m-j}(1+x)^j)^t` (`W = (1+2x)^t+x(1+x)^t`) — DONE.
Also `base_dom_m4_1/2/3`, `raised_dom_m4_1/2/3` (m=4 rows), `p_coeff_rowdecomp` (coeff form), `nn_U2pow_V_pow`.
**A-reserve identity FORMALIZED** (`Aq`=2^k C(N,k); `Aq_down`: `k·A_k=2(N-k+1)A_{k-1}`; `Aq_up`:
`(k+1)A_{k+1}=2(N-k)A_k`; `A_reserve_identity`: `(k+1)·H^{(0)}_k = 4k(N+1)A_k`) — = §6f Part A in Lean, sorry-free.
Lean-`formally-verified` now covers: general domination engine, m=2,3,4 row bounds, both row decompositions,
and the A-reserve identity. Remaining for full m≤9 `H_k≥0` (multi-session): general-j Maclaurin deficit bounds
+ the `H_k`-operator coeff-extraction + the large-t analytic monotonicity + the finite small-t check.

## 6f. m≤9 certificate for `H_k≥0`  — `rigorous-informal` / machine-audited (2026-06-07d). **The bankable result.**
**Thm (machine-audited):** `H_k ≥ 0` for all `4≤m≤9`, `t≥1`, `1≤k≤mt` ⟹ (with §6c reduction) **`T_{m,t,1}`
unimodal for all `m≤9, t≥1`** — and since `m≥3` is non-log-concave (Galvin), this is the first unimodality
proof for a substantial non-log-concave tree family. GPT-5.5 Pro certificate, refereed + verified end-to-end
by Claude (`search993/{verify_gpt_m9,verify_gpt_m9_dense}.py`, `check_finite_m9.cpp`):
- **A-reserve identity** (`rigorous`, hand-proven + exact): `H^{(0)}_k = 4k(N+1)/(k+1)·A_k`, `A_k=2^k C(N,k)`,
  via `kA_k=2(N-k+1)A_{k-1}`, `(k+1)A_{k+1}=2(N-k)A_k`. Hence `(H^{(0)}_k+2(N+1)q_k)/(kA_k) = ρ(N,k) :=
  (N+1)(4/(k+1)+1/(N-k+1))`; uniform min `ρ_res(m)` at `t=1,k=⌈2m/3⌉` (= 15/2,39/5,119/15,8,57/7,115/14 for m=4..9).
- **Honest obstruction** (`verified`): the "A-reserve alone dominates all deficits" route (`ρ_res−Σδ_j>0`) is FALSE
  for `m=7,8,9` — at `m=9,t=1,k=9`, reserve `=14` but negative non-`A` rows need `≥50181/64≈784`; `H_k=12875/64>0`
  only because POSITIVE non-`A` rows cancel. (Independently found by Claude's `derived_cm` + confirmed by GPT.)
- **Large-t certificate** (`rigorous-informal`, dense-verified): Maclaurin row bound `[x^n]((1+2x)^{(m-j)t}(1+x)^{jt})
  ≤ (1−j/2m)^n A_n` ⟹ `H_k ≥ kA_k[ρ(N,k)−Σ_j C(m,j)D_j(N,k)] > 0` for all `t≥T_m`, `T_m=(17,27,39,53,70,88)` for
  m=4..9. Verified `>0` on the dense range `t∈[T_m,400]` with the min exactly at `t=T_m` (monotone); margins at
  `T_m` match GPT (m=7:0.190, m=9:0.228). The one not-yet-formal step: the analytic monotonicity-in-`t` for ALL
  `t≥T_m` (GPT's sketch; computationally confirmed dense).
- **Finite small-t** (`verified-computation`, exact, C++ 120 threads): `H_k≥0` for `4≤m≤9, 1≤t<T_m` — 288 pairs,
  0 failures; `min H_k/(kA_k)` = 8.888..8.961 (matches GPT). **Together ⟹ `H_k≥0` for all m≤9, t≥1.**
- *Lean status:* m=2,3,4 dominations formal (`galvin_dom.lean`); m=5..9 + `H_k` operator + large-t-analytic +
  finite check = multi-session formalization, on the §6e foundation.

## 7. Old product-split obstruction  — `verified-computation` / superseded for symmetric `D(m,m,3)`
Combining §5+§6+§3 by a direct factor split would have required a **product certificate**
`μ_{E_m}(λ_r)+μ_{F_m}(λ_r)≥r` at the *convolution* tie `λ_r=c_r/c_{r+1}` (`c=e*f`).
- **Obstruction (logged, `verified-computation`):** the natural decoupling
  `λI'−rI = F(λE'−αE)+E(λF'−βF)` with a split `α+β=r` **fails** — no split has
  both required factor-threshold inequalities `λ_r≥e_α/e_{α+1}` and `λ_r≥f_β/f_{β+1}`
  (168/168 ties, `m≤12`).
- GPT-5.5 Pro adversarial verdict: "no complete joint product certificate yet" (reverse-Bernoulli
  is circular; hub-regroup gives a split but not positivity; generic product theorem is false).
- This obstruction is still relevant to generic convolution approaches, but it is superseded for
  symmetric `D(m,m,3)` by the direct coefficient-ratio certificate in §8.

## 8. Direct symmetric double-spider certificate  — `rigorous-informal` / Lean pending
For `Z_m=I_{D(m,m,3)}=E_mF_m`, new script `search993/derive_symm_double.py` verifies the
hub-state decomposition
`xZ'_m-rZ_m = U^(2m)A + 2xU^(m-1)V^mC + x²V^(2m-1)D`, where `U=1+2x`, `V=1+x`,
`A=2(2m-r+1)x-r`,
`C=(4m-2r+4)x²+(3m-3r+4)x+(1-r)`,
`D=(2m-r+2)x+(2-r)`.
At rising ties, factoring out `xU^(m-1)V^m` and using the order-2 Bernoulli lower bound for
`(1+x/(1+x))^m` gives a lower-bound certificate. Exact checks:
`N_r≥0` for `m≤35`; the lower bound is nonnegative for rising ties through `m≤150`; 0 failures.
The symbolic proof reduces to the linear coefficient-ratio inequality
`z_r/z_{r+1} ≥ (2r+1)/(4(2m-r+1))` (`0≤r≤2m-1`).  This gives
`A=2(2m-r+1)λ-r ≥ 1/2`, which is stronger than the positivity needed in the order-2
Bernoulli lower-bound step.  Exact verifier status in `search993/derive_symm_double.py`:
`badK=0 badSplit=0 badPrefix=0 prefixMismatch=0 badBound=0` through `m≤150`.
The linearly-cleared numerator
`K=4(2m-r+1)z_r-(2r+1)z_{r+1}` splits as `K=2G_mid+G_tail`.
Both pieces now have elementary `rigorous-informal` proofs below, machine-audited by
`G_mid closed-proof verifier m<=150: bad=0`; Lean formalization is still pending.

For `G_tail`, putting `n=2m-r+1`, `K_0=[x^(r+1)](1+2x)^(2m+1)` and
`K_2=4n\binom{2m}{r-2}-(2r+1)\binom{2m}{r-1}`, one gets
`G_tail=K_0/3+K_2`.  After factoring `\binom{2m}{r-1}` (for `r≥1`) the cleared numerator is
`2^(r+1)n(n+r)(n+1)+12nr(r+1)(r-1)-3r(r+1)(n+1)(2r+1)`.
For `r≥6`, `2^(r+1)≥3r(r+1)` and `n≥2` make this positive; `r=0..5` reduce to fixed positive
polynomials in `n`.

For `G_mid`, let `f_s=[x^s](1+x)^m(1+2x)^m`.  The coefficient-operator identity is
`G_mid(r)=2^(r+1)/3 * binom(2m+1,r+1) - R_r`, where
`R_r=f_r-(2m-3)f_{r-1}+4f_{r-2}`.  Thus it is enough to show `R_r≤0`, except in the
edge cases where the positive binomial term handles the difference.

The recurrence for `f` from `(1+3x+2x^2)F'=m(3+4x)F` is
`r f_r = 3(m-r+1)f_{r-1}+2(2m-r+2)f_{r-2}`.  Hence
`R_r = -((2mr-3m-3)/r)f_{r-1} + (2(2m+r+2)/r)f_{r-2}`.
Since `f_s` is an elementary symmetric polynomial in `2m` weights, all at least `1`,
`s f_s ≥ (2m-s+1)f_{s-1}`.  With `s=r-1`, this proves `R_r≤0` for
`m≥5` and `3≤r≤2m-3`; after clearing denominators the remaining comparison is the
concave quadratic
`E(r)=(2m-r+2)(2mr-3m-3)-2(r-1)(2m+r+2)`, whose endpoint values
`E(3)=6m^2-17m-17` and `E(2m-3)=4m^2-9m-23` are positive for `m≥5`.

The boundary cases are explicit:
`G_0=(4m-1)/3≥0`, `G_1=(8m^2+m-9)/3≥0`,
`R_2=(-3m^2+13m+8)/2≤0` for `m≥5`,
`R_{2m-2}=-2^(m-5)m(9m^3-24m^2-19m+18)≤0` for `m≥5`, and
`G_{2m-1}=2^m/24*(2^(m+3)(2m+1)-3m(7m+9))≥0` with equality only at `m=1`.
The remaining small cases `m=1,2,3,4` have nonnegative lists:
`[1,0]`,
`[7/3,25/3,47/3,11/3]`,
`[11/3,22,250/3,560/3,215,178/3]`,
`[5,41,218,754,1675,2317,1804,472]`.

## 9. Galvin family `T_{m,t,1}`  — `verified-computation` / proof target
This is the first structurally important thin family where log-concavity fails but unimodality appears
to survive.  The tree has root `v`, `m` children `w_i`, and each `w_i` has `t` length-2 arms.  Its
independence polynomial is
`Z_{m,t}(x)=W_t(x)^m+x(1+2x)^(mt)`, where
`W_t=(1+2x)^t+x(1+x)^t` is the equal-arm spider polynomial.

`verified-computation`: new C++ exact scanner `search993/galvin_tie_scan.cpp`
(`boost::multiprecision::cpp_int`, multithreaded; commands
`search993\galvin_tie_scan.exe 42 42 128 240` and
`search993\galvin_tie_scan.exe 10 10 1 120 1`) checks:
- `m,t≤42`, exact coefficients, exact local tie-balance for all cases with degree `≤240`:
  1764 cases, `non_unimodal=0`, `non_LC=1417`, `LC_break_before_or_at_mode=0`,
  650 LTB-checked cases, 44,324 rising-tie checks, `LTB_fail=0`.
- `m,t≤75`, exact coefficients, unimodality/LC only: 5625 cases, `non_unimodal=0`,
  `non_LC=4900`, `LC_break_before_or_at_mode=0`, `pre_mode_LC_fail=0`,
  `tail_increase=0`, and first-LC-break-minus-mode range `[5,1876]`.
- Perturbation diagnostics for `Z=P+Q`, `P=W_t^m`, `Q=x(1+2x)^(mt)`, with
  `D_k=P_{k+1}-P_k` and `E_k=Q_{k+1}-Q_k`: for `m,t≤75`,
  `Iminus_cases=245`, `Iminus_t_ge_6_cases=0`, `Iminus_prefix_fail=0`,
  `Iplus_cases=5279`, `Iplus_prefix_fail=0`, `Cplus_checks=105`, `Cplus_fail=0`.
  Here `Iminus={k:E_k<0<D_k}` and `Iplus={k:D_k<0<E_k}`.  The observed criterion is that
  `D_k+E_k≥0` is a prefix on each sign-conflict interval; this is a direct sufficient condition for
  unimodality because outside those intervals `D_k` and `E_k` have the same sign.
- LTB is **not** unconditional: small exact all-`r` check finds negative `N_r` outside the rising region
  (example `T_{3,3,1}`, `r=11`, where `c_r>c_{r+1}`).  The right statement is exactly the §2
  rising-tie version.

**Proof target:** prove for all `m,t≥1` and all `r` with `z_r≤z_{r+1}` that
`Σ_k (k-r) z_k z_r^k z_{r+1}^{D-k} ≥ 0` for `Z_{m,t}`.  This would cover Galvin's
non-log-concave examples by the same tie-fugacity mechanism and would be a genuine step beyond
the log-concavity literature.

**Weaker intermediate proof target:** prove `Z_{m,t}` is log-concave up to and including its mode, and
then prove the tail is monotone decreasing.  Exact scans show every log-concavity failure occurs strictly
after the mode; global log-concavity is false, but "pre-mode LC" may be the right structural replacement.

**Alternative intermediate proof target:** prove the perturbation one-crossing criterion above.  Since
`P` and `Q` are each log-concave/unimodal, their adjacent differences have one sign change; a prefix
condition on the two sign-conflict intervals forces the adjacent differences of `Z` to have one sign
change as well.  Exact scans further suggest `Iminus` is empty for `t≥6`, leaving only the `Iplus`
threshold inequality in the large-`t` regime.

---

### Verified vs. open at a glance
- **Complete & Lean-verified:** §3, §4, §5 (algebraic core), §6.  (4 sorry-free theorems + 1 factorization.)
- **Computation-backed:** the tree↔closed-form links; all certificate identities (Schwartz–Zippel).
- **Cited (not re-proven):** §1 reduction framework; spider log-concavity (2501.04245).
- **Rigorous-informal / Lean pending:** §8 direct symmetric `D(m,m,3)` ratio certificate.
- **Verified-computation / proof target:** §9 Galvin family `T_{m,t,1}` rising-tie local balance.
- **Open:** §0 (#993 itself), nonsymmetric/wider `d_leaf≤1` tie-balance, and the general reduction.
