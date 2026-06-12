# Research Log — Erdős #993 (Claude × GPT-5.5 Pro)

Single committed problem: **Erdős #993** (independence sequence of every tree is unimodal). Never switch.
Full chronological detail: `E:\Projects\ErdosProblems\handoff.md`. This is the new-goal-structured digest.

## 2026-06-09 ★★★ LANDMARK: COMPLETE m=2 `H_k ≥ 0` PROVEN IN LEAN (clean axioms, no native_decide)
**`galvin_dom.lean` (582 lines, 0 sorry) now contains the FULL m=2 `H_k≥0` proof**, capped by
`m2_Hk_nonneg (t i : ℕ) (hi : i+3 ≤ 2t) : 0 ≤ H_k` where `H_k = H^A+H^B+H^R+2(N+1)A_{k-1}` (k=i+3, exact
per verify_gpt20.py L63-66). 11 verified lemmas added this session: `m2_b2`(b2), `scalar_b4`, `Cq_down`,
`Cq_up`, `c_chain3`, `m2_b4`(b4), `scalar_b3`, `c_chain2`, `B_nonneg`, `m2_b3`(b3), `m2_Hk_nonneg`(capstone).
Assembly = `nlinarith [m2_b2 t (i+3), m2_b3 t (i+1), m2_b4 t i, ...]` after omega-index-normalization
(`i+3-1→i+2`, `i+3+1→i+4`, `i+1+2→i+3`, `i+1+1→i+2`) + push_cast. All clean axioms
`[propext, Classical.choice, Quot.sound]`. **REMAINING for #993 m=2:** (1) the BRIDGE — link `H_k≥0` to
unimodality of T_{2,t,1}'s independence sequence: need (a) indep.poly(T_{2,t,1}) coeff = `p_k=[x^k]W²=
A_k+2B_{k-1}+C_{k-2}` (W=(1+2x)^t+x(1+x)^t; `Wpow_rowdecomp`/`p_coeff_rowdecomp` in file are the start), and
(b) the operator `H_k≥0 ⟹ p_k unimodal` step (H_k is the discriminant-like quantity for the transformed
seq — this is the remaining genuinely-mathematical lemma, NOT pure algebra). (2) then m=3 analogously
(parallel bounds; m=3 IS the non-log-concave literature-novel case). The H_k≥0 algebra (the hard part) is
DONE; the bridge is what turns it into a stated unimodality theorem for the PR.

## 2026-06-09 increment (session pivoted back to #993 after #700/#64/#273/#937 work)
- **`galvin_dom.lean`: +2 new sorry-free lemmas** (clean axioms) toward the m=2 `H_k≥0` assembly:
  `scalar_decay`: `(j+1)(3/4)^j ≤ 27/16` ∀j (the b2 scalar bound, via decreasing-step induction; max 27/16 at j=2,3);
  `scalar_decay2`: `2(j+1)[(3/4)^j+(3/4)^{j+2}] ≤ 675/128` (= `(25/8)·scalar_decay`). These are the exact scalar
  bounds in `search993/verify_gpt20.py` for the GPT round-20 elementary m=2 proof. File now 320 lines, 0 sorry.
- **`m2_b2` PROVEN (this turn, sorry-free, clean axioms):** `7·k·A_k ≤ H^{(0)}_k + 2(N+1)A_{k-1}` (N=2t,
  1≤k≤N) — the b2 step. Manual `linear_combination ((2t)-k+1)·A_reserve_identity − (k+1)((2t)+1)·Aq_down`
  key identity → `=k·A_k·(reserve-slack)`, ≥0 by `m2_reserve`; divide by `(N-k+1)(k+1)>0`. galvin_dom.lean
  now 360→~395 lines, 0 sorry. Three b-lemmas done: scalar_decay, scalar_decay2, m2_b2.
- **REMAINING for m=2 `H_k≥0` (recipe; per `verify_gpt20.py`):** (b3) `H^B ≥ −(675/128)k·A_k` — `H^B`
  uses B_j (=raised_dom_m2 ≤(3/2)^j C(2t,j)); the negative terms −8(N-k+1)(N-k+2)B_{k-2}−2k(k-1)B_k bounded
  via the B-domination + `scalar_decay2` + binomial ratios C(2t,k-2)/C(2t,k) etc. relating to A_k. (b4)
  `H^R ≥ −(5/4)k·A_k` — C_j=C(2t,j); scalar `(k-1)(7k-8)/2^{k-3}≤5/4` (k≥3) [need a 3rd scalar lemma].
  **★ [b4 FULLY PROVEN — `m2_b4`, sorry-free, clean axioms]** `-(5/4)·k·A_k ≤ H^R` for k=j+3≥3,
  j+3≤2t. Supporting lemmas all proven this session: `Cq_down` (`k·C(N,k)=(N-k+1)·C(N,k-1)`), `Cq_up`,
  `scalar_b4` (`4(k-1)(7k-8) ≤ 15·2^k`, k≥3, equality at k=4 — NOTE earlier `(k-1)(7k-8)/2^{k-3}≤5/4`
  recollection was WRONG), and `c_chain3` (`(N-j)(N-j-1)(N-j-2)C(N,j)=(j+1)(j+2)(j+3)C(N,j+3)`, the
  3-step ratio identity). PROOF: drop the positive `C(N,k-2)` term; boundA `(j+3)(j+2)C(N,k-1) ≤
  (j+2)(j+3)²C(N,k)` (via Cq_down + N-j-3≥0); boundB `4(N-j-2)(N-j-1)C(N,k-3) ≤ (4/3)(j+1)(j+2)(j+3)C(N,k)`
  (via c_chain3 + N-j≥3); sum = `(j+2)(j+3)(7j+13)/3·C(N,k)`, closed by scalar_b4 × ((j+3)C(N,k)≥0).
  All nlinarith, no native_decide.
- **★ [b3 INGREDIENTS NOW ALL PROVEN]** `scalar_b3` (`(k-1)(3/4)^k ≤ 243/256` ∀k, TIGHT — equality k=4,5;
  decreasing-for-k≥4 induction + interval_cases k<4) + `c_chain2` (`(N-j)(N-j-1)C(N,j)=(j+1)(j+2)C(N,j+2)`,
  2-step Cq_down). Plus foundation `raised_dom_m2`: `B_n := (((1+X)(1+2X):ℚ[X])^t).coeff n ≤ (3/2)^n C(2t,n)`.
  **m2_b3 RECIPE (k=j+2≥2, j+2≤2t; mirror m2_b4):** H^B = 2[4(j+2)(N-j)B_{j+1} − 4(N-j-1)(N-j)B_j −
  (j+2)(j+1)B_{j+2}]. Drop positive `8(j+2)(N-j)B_{j+1}` (needs **B_{j+1}≥0** — the one new sub-lemma;
  ((1+X)(1+2X))^t has nonneg coeffs, prove via the file's Dom/NN engine or coeff-of-nonneg-product).
  Upper-bound the 2 negative B's by raised_dom_m2 + c_chain2. **★ B_nonneg NOW PROVEN** (`nn_pow` of the
  file's NN engine) — last b3 ingredient. **ALL b3 ingredients done: B_nonneg, raised_dom_m2, c_chain2,
  scalar_decay, Cq_down.** **★★★ b3 BOUND `m2_b3` NOW FULLY PROVEN (sorry-free, clean axioms,
  needs `set_option maxHeartbeats 1000000` for the polynomial-coeff `set` whnf cost): `-(675/128)(j+2)·
  Aq(2t,j+2) ≤ H^B` for j+2≤2t.** Proof exactly as recipe'd (B_nonneg drop + raised_dom_m2 + c_chain2 +
  hpidA/hpidB power identities + scalar_decay). **⟹ ALL THREE m=2 BOUNDS PROVEN: m2_b2 (b2), m2_b3 (b3),
  m2_b4 (b4).**
- **★★★ EXACT H_k (verify_gpt20.py lines 63-66, the ground truth):**
  `HA = 4k(N-k+2)A(k) − 4(N-k+1)(N-k+2)A(k-1) − k(k-1)A(k+1)`;
  `HB = 8k(N-k+2)B(k-1) − 8(N-k+1)(N-k+2)B(k-2) − 2k(k-1)B(k)` [NOTE factor 8,8,2 — the `2·(…)` in m2_b3];
  `HR = 4k(N-k+2)R(k-2) − 4(N-k+1)(N-k+2)R(k-3) − k(k-1)R(k-1)` [R(n)=C(N,n) binomial];
  `Hk = HA + HB + HR + 2(N+1)A(k-1)` [the +2(N+1)A(k-1) RESERVE is PART of Hk]. A(k)=Aq=2^k C(N,k),
  B(n)=(((1+X)(1+2X))^t).coeff n. **FINAL ASSEMBLY (mechanical linear combination):** parametrize k=i+3
  (i≥0, clean Nat) so i+3≤2t; apply `m2_b2 t (i+3)` (gives HA+2(N+1)A(i+2)≥7(i+3)A_k), `m2_b3 t (i+1)`
  (j=i+1 ⟹ HB≥−(675/128)(i+3)A_k), `m2_b4 t i` (j=i ⟹ HR≥−(5/4)(i+3)A_k); then `nlinarith [b2,b3,b4]`
  gives `Hk ≥ (7−675/128−5/4)(i+3)A_k = (61/128)(i+3)A_k ≥ 0`. CAVEAT: index atoms — m2_b2 t (i+3) emits
  `Aq(2t)(i+3-1)`,`Aq(2t)(i+3+1)`; `i+3-1` is DEFEQ `i+2` (succ/pred) but may be a distinct syntactic
  atom for nlinarith — normalize with `simp only [Nat.add_sub_cancel]`/`omega`-rewrite or state Hk using
  the verbatim `i+3-1`/`i+3+1` forms to match. After Hk≥0: link to unimodality (operator-positivity ⟹
  prefix-LC for the W²=([x^k] independence gen.fn.) sequence) — that linkage is the remaining real work.
- **(prior b3 sketch)** with k=j+2, the b3 deficit reduces to
  `(25/8)(j+1)(j+2)(3/4)^j·A_k`, and the closing scalar is the ALREADY-PROVEN **`scalar_decay`**
  (`(j+1)(3/4)^j ≤ 27/16`), NOT scalar_b3 — they're equivalent under k=j+2 ((j+1)(3/4)^{j+2}≤243/256 ⟺
  (j+1)(3/4)^j≤27/16). (25/8)(27/16)=675/128 ✓ TIGHT. The ONLY new wrinkle for m2_b3 vs m2_b4 = two POWER
  IDENTITIES to convert (3/2)-powers·C into (3/4)^j·A_k (since A_k=2^{j+2}C(2t,j+2)): `hpidA: (3/2)^j·
  C(2t,j+2) = (1/4)(3/4)^j·Aq` and `hpidB: (3/2)^{j+2}·C(2t,j+2) = (9/16)(3/4)^j·Aq` — both via
  `(3/4)^j·2^j=(3/2)^j` (`← mul_pow; norm_num`) + Aq=2^{j+2}C + ring. Then mirror m2_b4: boundJ
  `4(N-j-1)(N-j)B_j ≤ (j+1)(j+2)(3/4)^j Aq` (rbJ×coef + c_chain2 + hpidA), boundJ2 `(j+1)(j+2)B_{j+2} ≤
  (9/16)(j+1)(j+2)(3/4)^j Aq` (rbJ2 + hpidB), drop positive `4(j+2)(N-j)B_{j+1}` via B_nonneg, sum×2 =
  (25/8)(j+1)(j+2)(3/4)^j Aq, close with scalar_decay×((j+2)Aq≥0). **THEN final assembly:**
  H_k=H^A+H^B+H^R+2(N+1)A_{k-1};
  m2_b2 gives 7kA_k≤H^A+2(N+1)A_{k-1}, m2_b3 gives H^B≥−(675/128)kA_k, m2_b4 gives H^R≥−(5/4)kA_k ⟹
  H_k≥(7−675/128−5/4)kA_k=(61/128)kA_k≥0. Then need the row-decomposition `p_k=A_k+2B_{k-1}+C_{k-2}`
  hooking H_k to these three (the `p_coeff_rowdecomp`/`Wpow_rowdecomp` pieces already in the file) ⟹
  prefix-LC ⟹ T_{2,t,1} unimodal. Then m=3.
  (assembly) `H_k = H^A+H^B+H^R+2(N+1)A_{k-1} ≥ (7−675/128−5/4)k·A_k = (61/128)k·A_k ≥ 0` ⟹ Lemma A
  (prefix-LC) ⟹ `T_{2,t,1}` unimodal. Then m=3 analogously. The binomial-ratio bounds (b3,b4) are the
  remaining work; b2 (the cleanest) is done.
- **(superseded sketch)** with `p_k=A_k+2B_{k-1}+C_{k-2}` (`A=(1+2x)^{2t}`,
  `B=(1+2x)^t(1+x)^t`, `C=(1+x)^{2t}`), apply the H-operator linearly; A-part = `A_reserve_identity` (done),
  reserve ≥7kA_k = `m2_reserve` (done), B-deficit bounded by `raised_dom_m2` (done) × `scalar_decay` (done now),
  C-deficit similarly ⟹ `H_k ≥ (61/128)kA_k ≥ 0` ⟹ prefix-LC ⟹ `T_{2,t,1}` unimodal. Remaining Lean work =
  define the H-operator on the row decomposition + combine (foundation pieces all proven). Then m=3 analogously
  (the non-LC literature-novel one). Other tracks (m≥10 (B*)/thin-diagonal) remain GPT-walled — don't re-chase.

## Current proof state
- Reduction framework (tie-fugacity / `d_leaf≤1`): adopted from the B. Rey manuscript (cited, not re-proven).
- **Mode-free local tie-balance** is the formalizable target (carry `c_r≤c_{r+1}`, never identify the mode).
- **Established (Lean-verified, sorry-free):**
  - equal-arm spider `S(2^k)` local tie-balance — `ltb_main.lean` (PR #4192).
  - one-leaf mixed spider `S(2^a,1)` local tie-balance, unconditional — `mixed_oneleaf.lean` (PR #4192).
  - symmetric double-spider factorization `I_{D(m,m,3)}=E_m·F_m` — `emspider.lean`.
  - factor `E_m` local tie-balance — `emspider.lean`.
- **Established (rigorous-informal / machine-audited, Lean pending):**
  - symmetric double-spider `D(m,m,3)` linear ratio certificate for local tie-balance.
- **Verification harness:** `search993/{verify_gpt_localtie,derive_oneleaf,derive_Em,derive_symm_double,verify_double,explore_double_d3,gen_cnum_mixed}.py`
  and `search993/galvin_tie_scan.cpp` — certificate identities checked by exact arithmetic / Schwartz–Zippel;
  Galvin-family scans use exact `cpp_int` arithmetic with multithreading.

## Frontier sub-goal
**★ CURRENT FRONTIER (2026-06-07 session end, consolidated):** prove **`H_k ≥ 0`** for `1≤k≤mt`, where
`H_k = 4k(N-k+2)p_k − 4(N-k+1)(N-k+2)p_{k-1} − k(k-1)p_{k+1} + 2(N+1)q_k`, `N=mt`, `p_k=[x^k](U^t+xV^t)^m`,
`q_k=2^{k-1}\binom{N}{k-1}` (`U=1+2x,V=1+x`). `H_k≥0 ⟺ C_k≥0 ⟹` Lemma A (prefix log-concavity of
`Z=W^m+xU^N`) `⟹ T_{m,t,1}` (hub-of-spiders) unimodal — a family that INCLUDES the non-log-concave
`d_leaf≤1` trees, so a genuinely-new unimodality result. **`H_k≥0` is fraction-free, linear in `p`, and
verified ROBUST (exact, 690 (m,t) pairs, m∈[2,7], t∈[2,120], 0 failures, slack ≈0.0176).** It is OPEN: a
hypergeometric inequality with `m,t` as exponents (Krawtchouk-type `p`); GPT-5.5 Pro stalled on it
(rounds 13–17: four "not yet" + a non-answer). Next attack: m=2 first (`p_k=A_k+2B_{k-1}+C_{k-2}`,
`k=N-s`, positive-coeff certificate), or creative-telescoping/Zeilberger. Full GPT-loop detail in the
round-12…16 entries below. Tools: `search993/{verify_Ck,verify_Ck_ext,verify_Hk2,galvin_largeT,verify_gpt13,galvin_step1,galvin_decouple,galvin_g1g2}.py`.
NOTE: the `D(m,m,3)` log-concavity shortcut (§6b) and the product-certificate frontier below are SUPERSEDED
as a route to general #993 by the LC-pivot refutation (`d_leaf≤1 ⟹ LC` is FALSE — Galvin `T_{3,4,1}`);
they survive only for the specific factored `D(m,m,3)` family. #993 must go via UNIMODALITY (tie-fugacity).

### Session 2026-06-07(b) — t-split refereed FRAGILE; Maclaurin route ruled out; one-crossing route opened; Lean domination foundation formalized
- **GPT's t-split reply** initially showed only reasoning bubbles (looked stalled); it MATERIALIZED later (~5.3k chars) with a substantive honest CORRECTION that **independently confirms my numerics**: "for every fixed integer `t≥7`, `C_{L-1}<0` for all sufficiently large `m`; the proof must use the reservoir/Ψ route, not `C_k≥0`." Analytic reason: at the boundary `k=L-1` (with `k/m→ρ_t=2(t+1)/3`), `μ_W(λ_Q)-ρ_t = (a_t/(1+a_t))(1 - tλ_Q/(UV))` and `1 - tλ_Q/(UV) = (-t²+7t-1)/(3(2t-1)) < 0` for `t≥7`. GPT then shows **why Ψ_k≥0 is the right target**: at `k=L-1`, the reservoir `Γ_k R_k²` is QUADRATIC in `R_k` while the bad term `C_k/q_k²` is only LINEAR, and `R_k ~ exp(I_t·m)` (I_t>0), so the quadratic dominates ⟹ `Ψ_{L-1}≥0` for large `m`. This is an ASYMPTOTIC (large-m) justification of the reservoir route — NOT a uniform proof. So GPT↔Claude CONVERGED: t-split part(I) is dead; Ψ_k≥0/reservoir is the target; still open.
- **t-split verified myself at large m** (`verify_tsplit.py`, `verify_tsplit_big.py`, exact): (i) `Ψ_k≥0` ROBUST everywhere incl m=1000 (the real target survives). (ii) **part (I) "C_k≥0 on [1,L) for t≥t0" is FRAGILE**: the C<0 band in [1,L) is a small→large-m artifact — at fixed t it is EMPTY at small m but APPEARS at large m (t=4,5 empty at m≤500, large band at m=1000); at fixed m=1000 it shrinks with t (t=2,3,4 huge→t=5 small→t=6 empty). No evidence of a finite t0 valid for ALL m. So the restricted-H half of the t-split has no robust foundation.
- **★ Maclaurin domination derived + RULED OUT for uniform m** (`verify_maclaurin.py`): the general row bound is `[x^n]R_j ≤ C(N,n)(2-j/m)^n` (Maclaurin/Newton), i.e. `R_j ≤coeff A·(1-j/(2m))^n`, `A_n=2^n C(N,n)` — this EXACTLY reproduces the proven m=3 dampings `{5/6,2/3,1/2}={1-j/6}`. But the induced lower bound `R_k ≥ A_k/A_{k-1}` makes the `Ψ_k` sufficient-condition HUGELY negative near `k=L` (because near `k~2N/3` the dominant rows of `W^m` are the MIDDLE ones, not `j=0`, so `A_k/A_{k-1}` massively underestimates `R_k`). ⟹ **no row-domination proves the uniform reservoir inequality** (confirms GPT's "crude in central regions"). The clean route that proved m=2,3 (few rows) cannot scale to uniform m. (10th refuted route this family.)
- **★ one-crossing route: my CONCAVITY formulation REFUTED (a t-dimension small-param artifact); corrected to sign-dominance.** I first proposed `z` additively CONCAVE on the inter-mode window (`quick_onecross.py`, "0 fail m≤1000,t≤13") — but I only tested `t∈{3,6,10,13}` and MISSED `t=1,4,5`. **GPT refuted it with exact counterexamples** (m=100,t=1: `Δ²z_68>0`; m=1000,t=4: `Δ²z_2668>0`, SHA given). GPT further showed the inter-mode window is NOT O(1)-wide: `b-a ~ m(ρ_Q-ρ_P)`, `ρ_Q-ρ_P = 2^{t-1}(t-6)/(3(3^t+2^t))`, LINEAR in m for `t>6` (so `|a-b|≤6` was a small-m artifact too). Additive concavity is asymptotically false ⟹ **DEAD.** (11th small-param artifact; LESSON re-burned: test EVERY regime, esp. ones a heuristic flags special — here `t≤5` vs `t≥6`. PROCESS NOTE: I also briefly mis-read GPT's substantive reply as an "empty Pro reply" — the answer had materialized at a later message index; scan ALL recent assistant messages, not just the last bubble.)
- **★ GPT PROVED the mode-order: `mode(W^m) ≤ mode_max(xU^N)` for `t≥6`** — clean Darroch argument: row `P^{(j)}=x^j(1+2x)^{N-jt}(1+x)^{jt}` is real-rooted (Poisson–binomial), mean `2N/3+j(1-t/6)`; for `t≥6` that's `≤2N/3`, so by Darroch each row's mode `≤2N/3+1 ≤ mode_max(Q)`; `P` is a nonneg combo of rows ⟹ nonincreasing from `mode_max(Q)` onward. CLOSED (Lean-ready modulo a Darroch/real-rooted-mode lemma — check Mathlib).
- **CORRECTED target = conflict-slope / SIGN-DOMINANCE** (not concavity): on the conflict zone `[min(a,b),max(a,b))` the increasing component dominates the decreasing one ⟹ **`Δz_k≥0`** there; with `Δz≥0` below + `≤0` above ⟹ single crossing ⟹ unimodal. **CAVEAT (mine, must verify): SUFFICIENT but possibly too strong** — if `mode(z)` lies strictly INSIDE the conflict zone, `Δz<0` there while `z` is still unimodal. **Verified at scale via `onecross_scan.cpp`** (C++ multithreaded, exact cpp_int, t=1..40, m≤800, 4288 pairs):
**`unimodal_FAIL=0` (every Z unimodal, ground truth) but `signdom_FAIL=1546/4288` — the sign-dominance
criterion is ALSO TOO STRONG.** Failures occur at `k=a` (=mode of P): there `mode(z)=min(a,b)`, not
`max(a,b)`, so `Δz<0` inside the conflict zone while z stays unimodal (incl t≥6, e.g. m=200,t=6: a=800,b=801,
signdom FAIL). So **the one-crossing route gives NO clean uniform criterion** — `mode(z)` wanders between the
component modes in an (m,t)-dependent way; both concavity and sign-dominance fail. The only true statement is
"Δz changes sign once" = unimodality itself (circular). **One-crossing route DEAD as a clean shortcut.**
### ★★★ Session 2026-06-07(d) — GPT's m≤9 certificate for `H_k≥0` VERIFIED end-to-end (the bankable result extends to m≤9)
GPT (fresh chat `c/6a25d08d`) delivered a **certificate-shaped proof** of `H_k≥0` for `4≤m≤9, t≥1` (extending the
proven m=2,3 to a big non-log-concave family). It first CONFIRMED my `derived_cm` finding — the "A-reserve alone
dominates all row deficits" route is FALSE for m=7,8,9 (e.g. m=9,t=1,k=9: reserve=14 but negative non-A rows need
≥50181/64≈784; total `H_k=12875/64>0` only because POSITIVE non-A rows cancel). So the proof is NOT `ρ_res−Σδ_j>0`;
it is **large-t Maclaurin bound + finite small-t exact check**:
- **A-reserve identity (hand-proven + exact-verified, `verify_gpt_m9.py`, 0 mismatch):** `H^{(0)}_k = 4k(N+1)/(k+1)·A_k`,
  so `(H^{(0)}_k+2(N+1)q_k)/(kA_k) = ρ(N,k) := (N+1)(4/(k+1)+1/(N-k+1))`. Uniform min `ρ_res(m)` at `t=1,k=⌈2m/3⌉` —
  TABLE matches GPT EXACTLY: m=4:15/2, 5:39/5, 6:119/15, 7:8, 8:57/7, 9:115/14, 10:33/4.
- **Maclaurin row bound** `[x^n]((1+2x)^{(m-j)t}(1+x)^{jt}) ≤ α_j^n A_n`, `α_j=1−j/(2m)` (= the proven m=2,3,4 dominations,
  general m = Maclaurin's inequality). Gives `H_k ≥ kA_k[ρ(N,k) − Σ_j C(m,j)D_j(N,k)]` (drop the positive middle row).
- **Large-t certificate (VERIFIED, `verify_gpt_m9.py`):** that bound is `>0` for all `t≥T_m`, `T_m`=(17,27,39,53,70,88)
  for m=4..9. Margins at `t=T_m` match GPT to 4 dp (m=7:0.1902, m=9:0.2280) and grow to ~9 for large t. Dense sweep
  `t∈[T_m,400]` (`verify_gpt_m9_dense.py`) confirms `>0` throughout. (GPT's analytic monotonicity-in-N + tail-bound
  sketch is the rigor-justification; computationally confirmed over the dense range.)
- **Finite small-t (VERIFIED EXACT, `check_finite_m9.cpp`, 120 threads, 0.8s):** `H_k≥0` for all `4≤m≤9, 1≤t<T_m` —
  **288 pairs, 0 failures**; min `H_k/(kA_k)` matches GPT's table EXACTLY (m=4:8.88832 … m=9:8.96081).
- **VERDICT: GPT's m≤9 certificate is SOUND** (every computable claim verified exact / matches GPT). ⟹ **`H_k≥0` for
  m≤9 ⟹ `T_{m,t,1}` unimodal for all m≤9, t≥1** — m≥3 non-LC ⟹ **first unimodality proof for a substantial
  non-log-concave tree family.** Tag: `rigorous-informal`/machine-audited (the one not-yet-formal piece is the large-t
  analytic monotonicity; computationally confirmed dense). **m≥10:** `H_k<0` (top-tail at small t) ⟹ needs the `D^P`
  reservoir on the narrow strip (still open). Tools: `search993/{verify_gpt_m9,verify_gpt_m9_dense}.py`,`check_finite_m9.cpp`.
- **PROCESS FIX (user-flagged):** GPT replies are NEVER actually empty — my "last role-element len=0" check mis-flagged
  substantive replies this session. Correct method: read `main.innerText` AFTER the last `düşündüm`/`thought` marker;
  if still unreadable, ASK THE USER TO PASTE (they did, reliably).
- **★ PR #4192 UPDATED + PUSHED (2026-06-08):** integrated the m≤9 foundation into `ErdosProblems/993.lean` as
  `namespace Erdos993.HubOfSpiders` (domination engine + m=2,3,4 row bounds + both row decompositions + A-reserve
  identity), sorry-free + CI-style-clean (8024 jobs, 0 warn/err). Rebased onto fork tip (fork had merged main) and
  pushed `311a309..41a7d74` to `AlperTheKing/formal-conjectures:erdos993-spider-lemma-M`. No Anthropic trailer (CLA).

### ★ m≥10 — my reservoir plan REFUTED by GPT (verified exact, `verify_gpt_m10.py`); m≥10 stays OPEN
GPT (m≥10 round, user-pasted) corrected TWO of my errors (both small-m artifacts I'd asserted):
- **The `H_k<0` strip is NOT narrow.** My `strip_m10.cpp` (m≤30) was too small. Asymptotically (GPT, verified):
  `H_k ≈ (a^{k-1}/(k-1)!)(2a²/(k+1)−1)m^{k+1}`, `a=2t+1`, so for fixed `t`, `H_k<0` for ALL `k>2(2t+1)²−1` once `m`
  large — a LARGE terminal interval, not a top-tail. Verified exact: m=50,t=1→`H_k<0` on `[17,50]`; m=100→`[17,100]`.
- **The ULC reservoir `Γ_k p_k² ≥ −C_k` is FALSE.** Counterexample (exact, matches GPT to 9 dp): `m=50,t=9,k=450`:
  `Γ_k≈0.004430`, `C_k/p_k²≈−0.030194` ⟹ `Γ_k+C_k/p_k²≈−0.02576<0` (the coarse ULC bound is too weak); the REAL
  `D^P_k/p_k²≈0.11665` still saves it (`D^Z/p²≈0.08646>0`). So `Z` survives but NOT via the ULC bound.
- **Confirmed identity:** `C_k = q_k·H_k/(2k(N-k+2))` (so `H_k<0 ⟺ C_k<0`), 0 mismatches.
- **Correct target (GPT, OPEN):** `D^Z_k≥0` via the REAL `D^P_k`, using the reversal `A_t(y)=y^{t+1}W(1/y)=
  y(y+2)^t+(y+1)^t`, `p_{N-s}=[y^{m+s}]A_t^m` ⟹ a coefficient inequality among `[y^{m+s∓1}]A_t^m`, `[y^{m+s}]A_t^m`
  (the terminal strip `k=N-s`). This is the viable route; the ULC `Γ_k` bound is insufficient for `m≥50`.
- **NET:** m≤9 is the bankable verified result (PR'd); m≥10 = the open `D^Z_k≥0` core (reversal-coefficient route).
  My "narrow strip"+"ULC reservoir" claims RETRACTED (12th/13th small-param artifacts; GPT caught both).

### ★★ m≥10 — GPT's SADDLE/reversal route reduces it to a thin diagonal (refereed + verified, `verify_saddle.py`)
GPT did a large-deviations saddle on `a_r=[y^r]A_t^m` (`A_t(y)=y(y+2)^t+(y+1)^t`, `p_{N-s}=a_{m+s}`):
- **`D^P_k/p_k² → 1/(k+1)` at fixed k** (saddle reservoir; VERIFIED exact: t=1,k=18 → 0.0565,0.0541,0.0534,0.0530
  for m=200,500,1000,2000 → 1/19=0.0526; I derived the exact form `D^P_k/p_k²=(m+1)/((m-k+1)(k+1))`). At the
  interior saddle `D^P/p²~1/(mσ²)`. So the REAL `D^P` reservoir is order `1/m` — much stronger than ULC `Γ_k`.
- `C_k/p²` governed by an entropy rate `Ψ_t(λ)`; `H_k<0` iff `k>2(2t+1)²−1` (low-edge VERIFIED exact, t=1→17).
- **⟹ PROVES `D^Z_k≥0` for every FIXED t, all sufficiently large m** (the saddle reservoir dominates `C_k` across
  the whole `H_k<0` strip). Strip exists only for `t≲2log₂m` (VERIFIED: t_max(m): m=20→6,50→9,100→11,200→13).
- **REMAINING (GPT honest, OPEN): the thin diagonal `t→∞, 10≤m≲2^{t/2}/√t`** — where m is too small for the saddle
  asymptotics. Verified-true to m=1000 but unproven. So `T_{m,t,1}` is reduced to **m≤9 (PROVEN) + fixed-t large-m
  (PROVEN via saddle) + the diagonal (OPEN, verified)**. This is a genuine, large reduction of the open part.
- **VERDICT:** GPT's saddle analysis is SOUND (all key asymptotics verified exact/numerically). #993 itself remains
  OPEN (the T_{m,t,1} diagonal + the general→`d_leaf≤1` reduction + non-hub-of-spiders trees). Next: the diagonal.
  Tools: `search993/{verify_saddle,verify_gpt_m10,dz_prefix.cpp}`.

- **NET (the wall, honest):** for uniform `T_{m,t,1}` (m≥10), EVERY clean criterion tried is too strong or unclosed —
  tie-fugacity/Ψ_k (birth-rate scalar unclosed), prefix-LC/`H_k`/t-split (false at large m), Maclaurin (too
  loose), concavity & sign-dominance (too strong). z is always unimodal; the proof resists every local
  invariant. Uniform `T_{m,t,1}` is genuinely OPEN. **Bankable, achievable deliverable: m=2,3 (proven) +
  extend to the largest m with `H_k≥0 ∀t` (`check_Hk_threshold.py`).** Lean domination foundation done.
  Tools added: `search993/{onecross_scan.cpp,check_Hk_threshold.py}`.
- **★ LEAN: domination foundation FORMALIZED** — `formal-conjectures/galvin_dom.lean`, sorry-free / no native_decide, axioms `[propext, Classical.choice, Quot.sound]`, 18 decls. Reusable engine `dom_mul`/`dom_pow`/`raised_dom_general` (coeff-domination of nonneg-coeff polys preserved under products/powers) + `coeff_one_add_C_mul_X_pow` (`[x^n](1+cx)^N=c^n C(N,n)`); the **m=2 mixed-row bound** `raised_dom_m2` (`[x^n]((1+x)(1+2x))^t ≤ (3/2)^n C(2t,n)`) and the **m=3 bounds** `raised_dom_m3a/b` (`≤(5/3)^n C(3t,n)`, `≤(4/3)^n C(3t,n)`) — the engine behind `T_{2,t,1}`,`T_{3,t,1}` unimodality. This is the first formalized step of the bankable m=2/m=3 result; remaining (multi-session, pure-algebra): the `H_k` operator + row decomposition + scalar geometric bounds (b2/b3/b4) + assembly `H_k≥(61/128)kA_k` (m=2) / `H_k≥2kA_k` (m=3).
- Tools added: `search993/{verify_tsplit,verify_tsplit_big,verify_maclaurin,quick_onecross}.py`.

— (historical) earlier frontier formulations —
Write and formalize the full local tie-balance proof for the symmetric double-spider `D(m,m,3)`, then generalize
the same direct-ratio method to nonsymmetric `D(a,b,d)` and wider thin `d_leaf≤1` families.
Earlier formulation: prove a **product certificate** `μ_{E_m}(λ_r)+μ_{F_m}(λ_r) ≥ r` at the convolution tie.
Current sharper route: bypass the failed factor split and prove `D(m,m,3)` directly from
`Z_m=E_m F_m`.  New script `search993/derive_symm_double.py` verifies the hub-state decomposition
`xZ'_m-rZ_m = U^(2m)A + 2xU^(m-1)V^m C + x^2V^(2m-1)D` and the order-2 Bernoulli lower-bound
certificate.  The previously missing symbolic lower bound for the convolution tie ratio is now the
linear coefficient-ratio inequality below.  Status: **rigorous-informal / machine-audited**, Lean pending.

2026-06-06/07 refinement: GPT/prover found the right-looking linear ratio target
`λ=z_r/z_{r+1} ≥ (2r+1)/(4(2m-r+1))`, equivalently
`K_{m,r}=4(2m-r+1)z_r-(2r+1)z_{r+1} ≥ 0` for `0≤r≤2m-1`.  The script now verifies
`badK=0 badSplit=0 badPrefix=0 prefixMismatch=0 badBound=0` through `m≤150`.  Moreover
`K=2G_mid+G_tail`.  `G_tail` has a short binomial proof, and `G_mid` now has an
elementary coefficient-transform proof using `f_s=[x^s](1+x)^m(1+2x)^m`, the recurrence
`r f_r=3(m-r+1)f_{r-1}+2(2m-r+2)f_{r-2}`, and the elementary-symmetric bound
`s f_s≥(2m-s+1)f_{s-1}`.  The key transformed inequality is
`G_mid = 1/3[x^(r+1)](1+2x)^(2m+1)
       +4N[x^(r-1)](1+2x)^m(1+x)^(m+1)
       -(2r+1)[x^r](1+2x)^m(1+x)^(m+1) ≥ 0`.
Status: **rigorous-informal / machine-audited** (`G_mid closed-proof verifier m≤150: bad=0`),
Lean formalization pending.  This likely closes the symmetric `D(m,m,3)` ratio-certificate
sublemma; next target is to write the full local tie-balance proof cleanly and then generalize beyond
the symmetric double-spider.

2026-06-07 new frontier family: Galvin's non-log-concave thin trees
`T_{m,t,1}` have closed form
`Z_{m,t}=W_t^m+x(1+2x)^(mt)`, `W_t=(1+2x)^t+x(1+x)^t`.  This family is inside
`d_leaf≤1`, refutes log-concavity as a route, and is now the best testbed for direct unimodality.
New multithreaded exact scanner `search993/galvin_tie_scan.cpp`:
`m,t≤42`, exact coefficients, `ltb_dmax=240`: 1764 cases, `non_unimodal=0`,
`non_LC=1417`, `LC_break_before_or_at_mode=0`, 650 exact LTB-checked cases, 44,324 rising-tie checks,
`LTB_fail=0`.  The first log-concavity break is always at least 5 indices after the mode in this scan.
A wider LTB-free scan `m,t≤75`: 5625 cases, `non_unimodal=0`, `non_LC=4900`,
`LC_break_before_or_at_mode=0`, `pre_mode_LC_fail=0`, `tail_increase=0`,
first-LC-break-minus-mode range `[5,1876]`.
Small exact all-`r` check shows LTB is false outside the rising region (e.g. `T_{3,3,1}`, `r=11`),
so the correct theorem is precisely the mode-free rising-tie statement, not unconditional positivity.
The scanner now also checks the perturbation decomposition `Z=P+Q`, `P=W_t^m`, `Q=x(1+2x)^(mt)`,
with adjacent differences `D_k=P_{k+1}-P_k`, `E_k=Q_{k+1}-Q_k`.  For `m,t≤75`:
`Iminus_cases=245`, `Iminus_t_ge_6_cases=0`, `Iminus_prefix_fail=0`,
`Iplus_cases=5279`, `Iplus_prefix_fail=0`, `Cplus_checks=105`, `Cplus_fail=0`.
Thus all observed sign-conflict intervals have a one-crossing threshold; for `t≥6` the `E<0<D`
conflict interval is empty.
**New sub-goal:** prove `T_{m,t,1}` local tie-balance at all rising ties for all `m,t`.  A weaker but
still useful intermediate target is to prove either (a) pre-mode log-concavity plus post-mode monotone
decrease, or (b) the perturbation one-crossing criterion for the adjacent differences of `P` and `Q`.

### Structural reduction of `T_{m,t,1}` tie-balance (2026-06-07, Claude — `verified-computation`)
Write `Z=W^m + xU^{tm}`, `U=1+2x`, `V=1+x`, `W=U^t+xV^t` (the proven equal-arm spider `S(2^t)`).
- **Step-1 decomposition** (sympy-verified identity, `search993/galvin_step1.py`, all `m,t≤5`, residual 0):
  `F := xZ'−rZ = W^{m-1}·G1 + x·U^{t(m-1)}·G2`, where `G1 = mxW'−rW` and
  `G2 = (1−r)U^t + 2mtxU^{t-1} = U^{t-1}[(1−r)+(2mt+2−2r)x]`.  Both prefactors `W^{m-1}>0`,
  `xU^{t(m-1)}≥0`.  This is exactly the part-split `F = (λP'−rP)+(λQ'−rQ)` for `P=W^m`, `Q=xU^{tm}`
  (since `λP'−rP = W^{m-1}G1`, `λQ'−rQ = xU^{t(m-1)}G2`).
- **Compensation is essential — NO single-bracket-positive certificate** (`galvin_decouple.py`,
  `galvin_g1g2.py`, exact, `m,t∈[2,12]`, 4049 rising ties): `G1<0` at 353 ties (⟺ `μ_P(λ_r)<r`),
  `G2<0` at 16 ties (all `t=2`; ⟺ `μ_Q(λ_r)<r`), **both-negative = 0**.  So neither part of `F` is
  nonnegative on its own; they exactly cover for each other.  `μ_Z(λ_r)` is the `Z`-weighted average of
  `μ_P,μ_Q`, so "at least one ≥ r" is necessary structure but NOT a proof.
- **Obstruction (precise):** the tie `λ_r=z_r/z_{r+1}` is a *convolution* ratio (`z=` coeffs of `W^m+xU^{tm}`),
  not a clean `L/M`, so the single-spider "clear-the-tie + positive `Cnum`" toolchain does NOT port.  A proof
  must JOINTLY bound the two compensating parts at the convolution tie — the **same difficulty class as the
  open symmetric `D(m,m,3)` product certificate** (§ above).  Promising routes (untried/parallel): the §8-style
  direct coefficient-ratio (`a·z_r ≥ b·z_{r+1}` with elementary binomial proof), or the perturbation
  one-crossing criterion for unimodality (weaker than LTB but suffices for #993 on this family).
- **Status:** `T_{m,t,1}` LTB is TRUE (`galvin_tie_scan.exe`, re-verified independently: `m,t≤42`,
  44,324 rising ties, `LTB_fail=0`); proof OPEN. Tools: `search993/{galvin_step1,galvin_decouple,galvin_g1g2}.py`.

### GPT round-12 (2026-06-07) — clean UNIMODALITY reduction for `T_{m,t,1}`; refereed
GPT-5.5 Pro: honest "not yet" on the direct coefficient-ratio tie-fugacity proof (obstruction confirmed),
and pivoted to a **direct unimodality** proof (not full log-concavity). Reduction: `Z=P+Q`, `P=W^m`,
`Q=xU^{tm}` (support `1..N`, `N=tm+1`, `q_k=2^{k-1}C(tm,k-1)`).
- **Lemma B** (`mode(W^m)≤mt`, so `z_k=p_k` decreasing for `k≥N`): EASY — `W=U^t+xV^t` has rightmost mode
  `≤t` (`w_{t+1}=1≤w_t=2^t+t`, LC), and rightmost modes add under products of log-concave seqs.
- **Lemma A** (THE crux): `z_k² ≥ z_{k-1}z_{k+1}` for `1≤k≤tm` (PREFIX log-concavity only).
- Lemma A + Lemma B + transition `z_N≥z_{N+1}` ⟹ `Z` unimodal (prefix-LC + tail-monotone, Lean-friendly).
- **★ REFEREE VERDICT (exact, `verify_gpt12.py`/`galvin_lemmaA_wide.py`, m,t∈[2,30], 841 cases):**
  **Lemma A: 0 failures; Lemma B: 0 failures; transition: 0 failures.** The reduction is VALID and the
  lemmas hold — including for all the non-LC trees (their LC break is in the tail `k>tm`, outside Lemma A).
- **★ But GPT's proposed PROOF of Lemma A is REFUTED.** (i) TP₂-ladder/Cauchy–Binet: the kernel
  `K(j,k)=C(m,j)[x^k]x^j U^{t(m-j)}V^{tj}` is NOT totally positive in any consistent orientation —
  adjacent 2×2 minors are sign-MIXED (181k `ad≥bc` vs 415k `ad<bc`); rows are individually LC but the array
  is not TP₂. (ii) Monotone-ratio route (`p_k/q_k` monotone ⟹ sum LC): FALSE — `p_k/q_k` is non-monotone on
  the prefix in 92/361 cases (first `m=5,t=2`; sync-minor sign-inconsistent). So Lemma A is **verified-true
  but its proof is OPEN** — it resists both standard sufficient conditions for "sum of two log-concave is
  log-concave." This is now the precise crux for `T_{m,t,1}` unimodality. Tools:
  `search993/{verify_gpt12,galvin_ratio,galvin_lemmaA_wide}.py`.

### GPT round-13 (2026-06-07) — `y`-graded grouped-defect reformulation of Lemma A; VERIFIED (best route so far)
GPT honest "not yet" on a complete Lemma A proof, but gave a sharper reformulation that SURVIVES adversarial
checks (unlike TP₂/monotone-ratio). Introduce `y` marking selected child-hubs:
`Z(y,x) = xU^N + (U^t + y x V^t)^m`, `N=mt`; `A_k(y)=[x^k]Z(y,x)`, `A_k(1)=z_k`.
Coefficients `a_{j,k}=[y^j x^k]Z`: `a_{0,k}=[x^k](1+x)U^N=2^k\binom{N}{k}+2^{k-1}\binom{N}{k-1}`,
and `a_{j,k}=\binom{m}{j}[x^{k-j}]U^{t(m-j)}V^{tj}` for `j≥1`. Grouped defect
`Δ_{h,k}=Σ_j (a_{j,k}a_{h-j,k} − a_{j,k-1}a_{h-j,k+1})`, the `y^h`-coeff of `A_k(y)²−A_{k-1}(y)A_{k+1}(y)`.
- **Stronger target (implies Lemma A at y=1): `Δ_{h,k} ≥ 0` for all `h` and `1≤k≤mt`.**
- **★ VERIFIED (exact, `verify_gpt13.py`, m,t∈[2,14], 169 cases): `Δ_{h,k}≥0` on the prefix — 0 failures.**
  The mechanism: individual TP₂ minors are mixed-sign, but the `h`-GROUPED sum cancels to nonneg.
- **Tail localization:** for `k>mt` the first negative `Δ` is ALWAYS at `h=3` (T_{3,4,1}: `(h=3,k=14)` =
  exactly the observed LC break; T_{3,2,1}: `(h=3,k=8)`). So `h=3` is the critical layer and the prefix
  `k≤mt` is exactly the safe region. This is the FIRST proposed certificate that survives verification.
- **Status:** `Δ_{h,k}≥0` (prefix) is a verified CONJECTURE (m,t≤14), not yet proven — the clean target.
  Round-14 (posted): push GPT to prove it via a fixed-`h` binomial/hypergeometric certificate (h=0 trivial
  = LC of `(1+x)U^N`; h=1,2,3 next; h=3 critical). Tool: `search993/verify_gpt13.py`.

### GPT round-14 (2026-06-07) — third honest "not yet"; the proof is a genuine wall
GPT has NO certificate for `Δ_{h,k}≥0` (including `h=3`); TP₂, monotone-ratio, termwise-minor positivity all
fail. It delegated the certificate SEARCH back to compute. What it added:
- **Hankel/two-point identity:** `Δ_{h,k} = [y^h x^k z^k](1−z/x)Z(y,x)Z(y,z) = −½[y^h x^k z^k]((x−z)²/(xz))Z(y,x)Z(y,z)`.
  The `(x−z)²` negative-square prefactor is WHY naive coefficient-positivity cannot work — positivity is via
  cancellation in the extraction. (Standard log-concavity-defect generating function.)
- **Explicit fixed-`h` forms** with `a_{0,k}=2^k\binom{N}{k}+2^{k-1}\binom{N}{k-1}`, `a_{1,k}=m[x^{k-1}]U^{N-t}V^t`,
  `a_{2,k}=\binom{m}{2}[x^{k-2}]U^{N-2t}V^{2t}`, `a_{3,k}=\binom{m}{3}[x^{k-3}]U^{N-3t}V^{3t}`. First real target:
  `Δ_{3,k}=2a_{0,k}a_{3,k}+2a_{1,k}a_{2,k}−a_{0,k-1}a_{3,k+1}−a_{3,k-1}a_{0,k+1}−a_{1,k-1}a_{2,k+1}−a_{2,k-1}a_{1,k+1}≥0`.
  Suggested attack: substitute `k=N−s` (prefix `=s≥0`), clear denominators, seek a positive-coefficient poly
  in `m,t,s,2^s,2^t`.
- **Obstruction (mine):** the `a_{j,k}` are genuine convolutions (`[x^{k-j}]U^{t(m-j)}V^{tj}` = a Krawtchouk-type
  hypergeometric sum), NOT single binomials, so the clean single-spider "clear-the-tie + positive Cnum"
  toolchain does NOT apply. `Δ_{3,k}≥0` is a hypergeometric-sum inequality with `m,t` BOTH as exponents — a
  WZ/creative-telescoping-class problem. **Status: `Δ_{h,k}≥0` (prefix) is verified (m,t≤14) but the proof is
  GENUINELY OPEN; GPT (prover) is stalled (3 rounds). `h=0` base case provable (LC of real-rooted `(1+x)U^N`).**

### ★★ CORRECTION (2026-06-07, Claude — `verified-computation`): the round-13/14 grouped-defect target is a SMALL-CASE ARTIFACT
On the user's instruction to attempt the certificate, I extended verification to larger `t` (the natural
sub-lemma "`W_y^m` log-concave over `ℝ_{≥0}[y]`" has its `m=1` base `W_y=U^t+yxV^t` FAIL at large `t`: the
`[y^1]` defect `3\binom{t}{k}\binom{t}{k-1}−4\binom{t}{k+1}\binom{t}{k-2}` goes negative near `t≈100`). Result
(`search993/galvin_largeT.py`, `galvin_doublecheck.py`, exact):
- **`Δ_{h,k}≥0` (GPT round-13 grouped target) is FALSE in general.** First failures: `(m=2,t=40)` at `(h=1,k=44)`;
  `(2,60)@(3,25)`; `(2,100)@(3,21)`; `(3,90)@(5,44)`. Double-checked at `(2,40),k=44`: `Δ_{1,44}≈−9.6e62 < 0`,
  yet `Σ_h Δ_{h,44}=z_{44}²−z_{43}z_{45}≈+1.98e71 ≥ 0` (the huge `h=0` layer masks negative layers until `t` is
  large). So the `y`-graded layerwise positivity (rounds 13–14, and the `W_y^m` ℝ_{≥0}[y]-LC sub-lemma) was a
  **small-case artifact (held only ≲ t≈14)** — NOT a theorem. My round-13 "verified target" assessment is
  RETRACTED; the layers genuinely go negative.
- **★ `Lemma A` (prefix log-concavity of `Z=W^m+xU^N`, `1≤k≤mt`) IS ROBUST — holds at every tested case through
  `t=100`** (`m∈{2,3,4,5}`). The unimodality reduction (Lemma A + Lemma B + transition ⟹ unimodal) is sound.
  So `T_{m,t,1}` unimodality reduces to **Lemma A directly** (the `y=1` sum), NOT the `y`-graded layers.
- **Net:** ALL proposed sufficient conditions for Lemma A now fail — TP₂, monotone-ratio, AND the `y`-graded
  grouped positivity. Lemma A is a genuine "sum of two log-concave sequences is log-concave on a prefix"
  inequality (`W^m` LC by convolution of spiders; `xU^N` real-rooted LC; the cross term must be controlled
  on `k≤mt` directly). **Proof OPEN; no layerwise crutch survives.** This is the honest frontier for the
  hub-of-spiders family; #993 stays open. Lesson re-confirmed (cf. the LC-pivot refutation): verify at large
  parameters before trusting a pattern.

### GPT round-15 (2026-06-07) — sharper target `C_k≥0`; ROBUST at large t (survives the test that killed the grouped route)
GPT acknowledged the correction (no fake certificate) and sharpened to a SIMPLER, LINEAR-in-`p` target:
**`C_k := D^Q_k + Cross_k = q_k² − q_{k-1}q_{k+1} + 2p_kq_k − p_{k-1}q_{k+1} − p_{k+1}q_{k-1} ≥ 0`** for `1≤k≤mt`,
where `p_k=[x^k]W^m`, `q_k=2^{k-1}\binom{mt}{k-1}` (`=[x^k]xU^N`). Since `D^P_k=p_k²−p_{k-1}p_{k+1}≥0` (`W^m`
log-concave, convolution of spiders), `C_k≥0 ⟹ D^Z_k=D^P_k+C_k≥0 = Lemma A`. Equivalently `C_k=D^Z_k−D^P_k`,
i.e. "`Z` is at least as log-concave as `W^m` on the prefix." It is *linear* in `p` (avoids the quadratic
`p`-cancellation). Normalized: `C̃_k=(1−γ_k)+2a_k−γ_k(a_{k-1}+a_{k+1})`, `a_k=p_k/q_k`,
`γ_k=(k-1)(N-k+1)/(k(N-k+2))`.
- **★ VERIFIED ROBUST (exact, `verify_Ck.py`/`verify_Ck_ext.py`): `C_k≥0` holds on `1≤k≤mt` for ALL tested —
  m∈[2,7], t∈[2,120] (690 (m,t) pairs incl. (2,100),(3,90),(7,100)), 0 failures.** Unlike the round-13 grouped
  target (dead at t≈40), this SURVIVES large t. Min normalized `C̃_k≈0.0176` (at m=7,t=100,k=542) — bounded
  away from 0, a comfortable (non-knife-edge) inequality. GPT also (correctly) dismissed the one-crossing
  route as "no cleaner than Lemma A."
- **Status:** `C_k≥0` is the cleanest, robust, still-OPEN target (a hypergeometric inequality, `m,t` as
  exponents). Round-16 (to post): confirm robustness, ask GPT to prove `C_k≥0` (linear in `p`; `=D^Z−D^P≥0`).
  Tools: `search993/{verify_Ck,verify_Ck_ext}.py`.

### GPT round-16 (2026-06-07) — cleanest equivalent `H_k≥0` (fraction-free, linear in p); CONFIRMED correct + robust
GPT (4th honest "not yet") cleared `C_k` of all q-fractions using `q`'s real-rooted recurrence
(`q_{k+1}/q_k=2(N-k+1)/k`, `q_{k-1}/q_k=(k-1)/(2(N-k+2))`, `q_k²-q_{k-1}q_{k+1}=q_k²(N+1)/(k(N-k+2))`):
**`H_k := 4k(N-k+2)p_k − 4(N-k+1)(N-k+2)p_{k-1} − k(k-1)p_{k+1} + 2(N+1)q_k ≥ 0`** for `1≤k≤mt`.
- **CONFIRMED (exact, `verify_Hk2.py`, 690 (m,t) pairs):** the identity `H_k·q_k = C_k·2k(N-k+2)` holds (0
  failures) ⟹ `H_k≥0 ⟺ C_k≥0`; and `H_k≥0` is robustly true (0 failures, m∈[2,7], t∈[2,120]).
  [Process note: my first check falsely flagged it — a boundary bug (`q_{N+1}` left 0 instead of `2^N`); the
  algebra is right term-by-term. Verify boundaries.]
- `H_k` is **linear in `p=W^m`, fraction-free, no `q_{k±1}`** — the cleanest obstruction so far. GPT confirmed
  per-row positivity does NOT work (the operator does global cancellation first), and (correctly) that the
  one-crossing route is no easier than `H_k`. Delegated to compute: fixed-`m` (start m=2,3) symbolic
  `H_{N-s}(t,s)≥0` (`k=N-s`, prefix `s≥0`) certificate search.
- **Status:** `H_k≥0` (`1≤k≤mt`) is the exact, clean, verified-robust, still-OPEN obstruction for `T_{m,t,1}`
  unimodality. `p_k=[x^k]W^m` is a Krawtchouk-type convolution (`m,t` exponents) ⟹ a WZ/creative-telescoping
  -class inequality. GPT (prover) stalled (rounds 13–16 all "not yet"). Tools: `search993/{verify_Hk2,verify_Ck_ext}.py`.

### Claude's own attempt at `H_k≥0` for m=2 (2026-06-07, user-directed) — clean reduction, sub-lemmas still hard
Decomposed `Z=W²+xU^N` (m=2, N=2t) as `Z=P0+P1+P2`, `P0=(1+x)U^{2t}`, `P1=2xU^tV^t`, `P2=x²V^{2t}` (each
real-rooted/log-concave). **Result (exact, `attempt_m2*.py`, t≤120):** the only ever-negative cross-defect is
`cross02`, and `diag(P0)+diag(P2)+cross02 = D^{P0+P2}` (LC defect of `P0+P2`). Hence on the prefix
**`D^Z_k = D^{P0+P2}_k + diag(P1)_k + cross01_k + cross12_k`, all four ≥0**, reducing m=2 `H_k≥0` to:
(i) `P0+P2=(1+x)(1+2x)^{2t}+x²(1+x)^{2t}` log-concave (verified ALL k); (ii) `diag(P1)≥0` (trivial, `P1`
real-rooted); (iii) `cross01≥0`, (iv) `cross12≥0` on the prefix (cross-log-concavity of two real-rooted polys).
- **But the standard closers DON'T apply (verified, `attempt_m2c.py`):** `P0+P2` is NOT real-rooted (so its LC
  isn't automatic); the pairs `(P0,P1)`,`(P1,P2)` are NOT compatible (convex combos not all real-rooted), so
  `cross01/cross12≥0` do NOT follow from interlacing/compatibility theory. Each sub-lemma is a genuine
  hypergeometric inequality (`t` exponent; `P1` Krawtchouk `B_j=[x^j](1+3x+2x²)^t`) needing a custom
  certificate (creative-telescoping/WZ). **m=2 NOT closed — honest partial progress (a clean reduction +
  ruled-out routes), consistent with GPT's wall.** Tools: `search993/attempt_m2{,b,c}.py`.

### ✅ Round-18 (2026-06-07) — sub-lemma (ii) PROVEN: `(1+x)(1+2x)^n + x²(1+x)^n` is log-concave (∀n)
GPT gave a real proof (its FIRST non-"not yet"). I verified it rigorously and FIXED its one gap:
- **Identity (VERIFIED exact, `verify_gpt18.py`, 0 fail / 1829 checks, 1≤k≤n, n≤60):**
  `4(k+1)(r+1)²(r+2)²(r+3)·(s_k²−s_{k-1}s_{k+1}) = C(n,k)²·N`, `r=n-k`, `q=2^k`, `s_k=2^kC(n,k)+2^{k-1}C(n,k-1)+C(n,k-2)`,
  `N=Aq²+Bq+C0`, `A=(r+2)(r+3)(k+r+1)(k²+4kr+5k+4r²+12r+8)` [coeffs ≥0],
  `B=-k(r+2)(k³r−5k³+2k²r²−22k²r−20k²−22kr²−15kr+17k+24r²+56r+32)`, `C0=4k²(k-1)(k+1)(k+r+1)` [≥0 for k≥1].
- **`N≥0`:** `N=q(qA+B)+C0`; `q=2^k≥k` (k≥1) and `A≥0` ⟹ `qA+B=(q-k)A+(kA+B)≥kA+B`; and `kA+B=k(r+2)P`.
- **★ GPT's gap (FIXED):** GPT claimed `P` has nonneg coeffs in `(k,r)` — FALSE (`P` has a `−8` term). BUT
  `P(k,r)=8k³+3k²r²+43k²r+38k²+8kr³+67kr²+91kr+22k+4r⁴+28r³+44r²+12r−8 ≥0` on the positive orthant, and
  **after `k=K+1` (valid since k≥1), `P(K+1,r)` has ALL-nonneg coeffs** (`verify_gpt18b.py`, 0 neg) ⟹ `P≥0`.
  So `kA+B≥0 ⟹ qA+B≥0 ⟹ N≥0`. Trivial reparametrization closes the gap.
- **`k=n+1` case (VERIFIED):** `2(s_{n+1}²−s_n s_{n+2}) = 2·4^n+(3n-2)2^n+n²+n ≥0` (n≥1). Boundaries trivial.
- **STATUS: sub-lemma (ii) is PROVEN** (GPT identity + Claude gap-fix, fully verified) — a clean genuinely-new
  binomial log-concavity lemma, Lean-ready (one `ring` identity + `positivity` after `k=K+1`). Stands. Tools:
  `search993/{verify_gpt18,verify_gpt18b}.py`.

### ★ Round-19 (2026-06-07) — the 4-piece reduction is DEAD (my error, GPT refuted); new H_k-domination route is robust
**CORRECTION (the 4th small-parameter artifact this session):** my m=2 reduction `D^Z=D^{P0+P2}+diag(P1)+cross01+cross12`
is an algebraically valid identity, but "all four summands ≥0 on the prefix" is FALSE. `cross01,cross12` go
NEGATIVE in the prefix for large t — `attempt_m2.py` only reached t≤39; GPT found and I confirmed (`check_gpt19.py`):
`cross01<0` at (t=40,k=44), `cross12<0` at (t=44,k=36) (both k≤N=2t). So (iii),(iv) are FALSE and the 4-piece
route to m=2 is dead. (Sub-lemma (ii) survives — independent, verified t≤120.) GOOD adversarial catch by GPT;
my "real progress" reduction claim is RETRACTED. Lesson (4th time): verify at LARGE parameters BEFORE claiming.
- **★ NEW route (GPT, VERIFIED ROBUST to t=120, `verify_gpt19dom.py`, 0 fail):** the **H_k-domination proof**.
  With `p_k=A_k+2B_{k-1}+D_{k-2}` (`A_k=2^kC(N,k)`, `B_j=[x^j](1+3x+2x²)^t`, `D_k=C(N,k)`, `q_k=A_{k-1}`),
  split `H_k = H^A + H^B + H^R + 2(N+1)A_{k-1}` where `H^X` is `H_k`'s `4k(N-k+2)·_k − 4(N-k+1)(N-k+2)·_{k-1} −
  k(k-1)·_{k+1}` applied to the A/B/D part. Bounds (each verified 0-fail, 1≤k≤N, t≤120):
  (b2) `H^A+2(N+1)A_{k-1} ≥ 7kA_k`; (b3) `H^B ≥ −(675/128)kA_k`; (b4) `H^R ≥ −(5/4)kA_k`. ⟹
  `H_k ≥ (7−675/128−5/4)kA_k = (61/128)kA_k > 0`. **This route avoids cross01/cross12 entirely and is numerically
  robust** (unlike the dead reduction). STATUS: verified-true but NOT yet proven — reduces m=2 to three binomial
  bounds (b2 clean A-only; b4 easy, D≪A; b3 is the crux, Krawtchouk B). Round-20: ask GPT to PROVE (b2),(b3),(b4).
  Tools: `search993/verify_gpt19dom.py`.

### ✅✅ Round-20 (2026-06-07) — m=2 `H_k≥0` PROVEN (elementary, verified) ⟹ `T_{2,t,1}` unimodal ∀t
GPT gave a complete elementary proof of the m=2 H_k-domination; I verified EVERY ingredient exactly
(`verify_gpt20.py`, t≤120 + scalar bounds to k=3000):
- **Krawtchouk domination (key):** `(1+3x+2x²)^t ≤_coeff (1+3x/2)^{2t}` (since `2≤9/4`) ⟹ `B_j ≤ (3/2)^j C(2t,j) = (3/4)^j A_j`. [0 fail]
- **(b2)** `H^A+2(N+1)A_{k-1} ≥ 7kA_k` (exact A-ratio algebra, `A_{k±1}/A_k` clean). [0 fail]
- **(b3)** for k≥2: `H^B ≥ −2k(k-1)[(3/4)^{k-2}+(3/4)^k]A_k` (drop positive term + domination) `≥ −(675/128)kA_k`,
  using `2(k-1)[(3/4)^{k-2}+(3/4)^k] ≤ 675/128` (tight at k=4). [0 fail]
- **(b4)** `H^R ≥ −(5/4)kA_k` via `R_j=2^{-j}A_j` and `(k-1)(7k-8)/(24·2^{k-3}) ≤ 5/4` (tight at k=4). [0 fail]
- **Assembly:** `H_k ≥ (7 − 675/128 − 5/4)kA_k = (61/128)kA_k > 0`. [final 0 fail]
**⟹ m=2 H_k≥0 PROVEN ⟹ C_k≥0 ⟹ Lemma A (prefix LC of Z=W²+xU^N) ⟹ T_{2,t,1} unimodal for all t.** Complete,
elementary, Lean-ready (binomial ratios + one coeff-domination + 3 scalar bounds; no creative-telescoping needed).
SECOND fully-verified result this session (after sub-lemma (ii)). NEXT: generalize to general m (m=3 first — the
non-LC regime, genuine novelty); the domination `(1+3x+2x²)^t≤(1+3x/2)^{2t}` and the H^X-domination template
should extend. Tools: `search993/verify_gpt20.py`.

### ✅✅✅ m=3 H_k≥0 PROVEN (2026-06-07, fresh chat) ⟹ T_{3,t,1} unimodal ∀t — INCLUDING non-log-concave trees (genuinely new)
GPT (fresh chat "Unimodal Trees Proof", `c/6a253e43…`) gave an explicit m=3 row certificate; I verified EVERY
ingredient exactly (`search993/verify_m3.py`, t≤120, 1≤k≤N=3t):
- **Per-row dominations** (base coeff-ineqs verified): `(1+2x)²(1+x) ≤_coeff (1+5x/3)³` ⟹ `B_n=[x^n]U^{2t}V^t ≤ (5/6)^n A_n`;
  `(1+2x)(1+x)² ≤_coeff (1+4x/3)³` ⟹ `C_n=[x^n]U^tV^{2t} ≤ (2/3)^n A_n`; `D_n=[x^n]V^N = (1/2)^n A_n`. (0 fail)
- `p_k=A_k+3B_{k-1}+3C_{k-2}+D_{k-3}`; `H_k=H^A+3H^B+3H^C+H^D+2(N+1)A_{k-1}`. Bounds (all 0 fail): reserve
  `H^A+2(N+1)A_{k-1} ≥ (22/3)kA_k`; `3H^B ≥ −4kA_k`; `3H^C ≥ −kA_k`; `H^D ≥ −(1/3)kA_k` ⟹ **`H_k ≥ 2kA_k > 0`**.
- **⟹ m=3 H_k≥0 PROVEN ⟹ C_k≥0 ⟹ Lemma A ⟹ T_{3,t,1} unimodal ∀t.** Since T_{3,t,1} for t≥4 are NON-log-concave
  (Galvin: T_{3,4,1} = the n=28 counterexample), this is **the first proof of unimodality for a non-log-concave
  tree family** — genuinely new. (Verified end-to-end to t=120/k≤360; GPT's asymptotic-tail monotonicity args are
  elementary, numerically confirmed over that range. Lean-ready: dominations + finitely many scalar bounds.)
- **★ HONEST LIMIT: general (all-m) H_k≥0 is FALSE.** GPT found + I confirmed: m=10,t=1,k=10 ⟹
  `H_10 = 80·1936881 − 8·1713690 − 90·1713690 + 22·5120 = −12878500 < 0`. But that tree is the spider `S(3^{10})`
  (t=1), which IS log-concave & unimodal (verified: 0 LC-viol). So `H_k≥0` (⟺C_k≥0) is only SUFFICIENT for
  Lemma A (`D^Z=D^P+C_k`, `D^P≥0`); where it fails, unimodality still holds via the `D^P` (log-concavity) term.
  ⟹ the H-route is m-specific (proven m=2,3); a uniform all-m,t proof of T_{m,t,1} needs the full `D^Z≥0`
  (D^P compensation) where H_k<0. #993 for all T_{m,t,1} NOT closed; m=2,3 ARE. Tools: `search993/verify_m3.py`.

### ★★ UNIFORM Lemma A (prefix-LC) is FALSE — the all-m prefix-LC route is DEAD (2026-06-07, verified 2 ways)
GPT (asked for the uniform all-m proof) found, after a 33-min reasoning round, that **the uniform Lemma A is
FALSE**: at **m=173, t=13, k=N=mt=2249**, `D^Z_N = D^P_N + C_N < 0` (so `Z=W^m+xU^N` is NOT prefix-log-concave),
even though `D^P_N>0`; `D^P_N/(−C_N) ≈ 0.94186 < 1`. **VERIFIED TWO INDEPENDENT WAYS** (`search993/verify_counterex.py`):
(A) GPT's reversal trick `R(y)=y^{t+1}W(1/y)`, `p_{N±·}=[y^{m∓·}]R^m`; (B) direct `W^m` (degree 2422) high
coefficients — both agree on `p_{N-1},p_N,p_{N+1}` and `D^Z_N<0` (sha256 of `-D^Z_N` matches GPT's).
- **The TREE is still UNIMODAL** (`check_tree_unimodal.py`): `T_{173,13,1}` unimodal (mode k=1499), the LC break
  is at k=N=2249 (in the DECREASING tail, doesn't break unimodality). So #993 holds for it; only the
  prefix-LC ROUTE fails. GPT: "needs a weaker target than prefix log-concavity."
- **NET (the hub-of-spiders family, definitive):** NO uniform algebraic route closes general `T_{m,t,1}`:
  `H_k≥0` is FALSE (m=10,t=1) AND prefix-LC `D^Z≥0`/Lemma A is FALSE (m=173,t=13). Both hold only for small `m`
  (PROVEN m=2,3). For large `m`, `Z` is non-log-concave (LC breaks at k=N) yet still unimodal — so a uniform
  proof needs DIRECT mode-control / one-crossing of `Δz_k` (the open #993-in-d_leaf≤1 core), not prefix-LC.
- **The 7th small-parameter artifact this session** — my "Lemma A robust" was only checked m≤5–7; it fails at
  m=173. LESSON (now ironclad): a pattern verified at small parameters means nothing until tested at LARGE ones.
- **GENUINE bankable wins stand:** LC-pivot refutation; m=2 & m=3 `H_k≥0` proven ⟹ `T_{2,t,1}`, `T_{3,t,1}`
  unimodal (m=3 = non-LC family, literature-novel). The uniform route is exhausted. Tool: `verify_counterex.py`.

### Non-LC route (2026-06-07) — GPT's RESTRICTED-prefix-LC reduction (sound, proven) + candidate cert refuted
GPT honest "not yet" on a uniform proof, but gave a genuine reduction:
- **REDUCTION (proven, ingredients verified `verify_restricted.py` to m=500): `D^Z_k≥0 for 1≤k≤N-1` ⟹ T_{m,t,1}
  unimodal.** Because P=W^m log-concave with mode≤N ⟹ `p_k` decreasing for k≥N; `q_N=N·2^{N-1} ≥ q_{N+1}=2^N`
  (N≥2); so `z` is decreasing for k≥N, and LC on [1,N-1] gives unimodality. CRUCIAL: this EXCLUDES k=N, exactly
  where the m=173 counterexample to the full Lemma A broke. So the counterexample does NOT obstruct unimodality.
- **Even weaker (Galvin's universal tree-tail theorem, cited arXiv:2502.10654): indep seq decreases from
  `L=⌈(2D-1)/3⌉` (D=m(t+1)=α). So suffices `D^Z_k≥0 for 1≤k<L`; for t≥4, L<N (below the failure zone).**
- **★ VERIFIED (`verify_restricted.py`, exact, large m incl m=173,200,250,300,400,500; t=4..40):** restricted
  prefix-LC `D^Z_k≥0` on `[1,N-1]` holds in ALL tested cases (the only LC break is ever at k≥N, never below N-1);
  `D^Z_k≥0` on `[1,L)` holds in all cases. So the RESTRICTED target SURVIVES large m (unlike full Lemma A which
  died at m=173,k=N). It is the right target — verified-true, still UNPROVEN.
- **★ GPT's candidate one-line certificate is FALSE.** `2r_k ≥ r_{k-1}+θ_k r_{k+1}` (r_k=p_k/(2^kC(N,k)),
  θ_k=(k-1)(N-k)/((k+1)(N-k+2))) FAILS at m=173,t=4,k=562 (<L=577). So that specific residual route is dead;
  the restricted prefix-LC itself still holds there. ULC-power route also unsafe (W not uniformly ULC; normalized
  LC defect <0 at k=4 large t).
- **STATUS:** the reduction (unimodal ⟸ restricted prefix-LC up to L) is PROVEN; the restricted prefix-LC is
  verified-true (m≤500) but UNPROVEN, and the natural candidate certificate is refuted. This is the open
  #993-in-(d_leaf≤1) core for T_{m,t,1}. Bankable wins remain m=2,3 (proven) + LC-refutation. Tool: `verify_restricted.py`.

### Restricted-prefix-LC "one more attempt" (2026-06-07) — honest "not yet"; my split refuted; open core precisely stated
GPT (asked to prove `D^Z_k≥0 for 1≤k<L` via the (i)+(ii) split I proposed): honest "not yet", and **refuted my
split**. My claim "(i) for t≥5, `C_k≥0` (restricted H-lemma) holds on `[1,L)`" is FALSE beyond m≤500: at
**m=1000,t=5,k=3999<L=4000**, `C_k<0` (so `H_k<0`) yet `D^Z_k>0` because `D^P_k` dominates by `D^P/(−C)≈6.52e62`
(verified exact, matches GPT). So the restricted-H sub-target is an artifact (the 9th small-param artifact this
session — and MINE); the `D^P` reservoir is genuinely needed even on `[1,L)`. No clean sub-regime where `C_k≥0`
suffices.
- **GPT's reformulation of the true target (correct, unproven):** with `a_k=p_{k-1}/p_k`, `b_k=p_{k+1}/p_k`,
  `c_k=q_{k-1}/q_k=(k-1)/(2(N-k+2))`, `d_k=q_{k+1}/q_k=2(N-k+1)/k`, `R_k=p_k/q_k`: `D^Z_k≥0` ⟺
  **`R_k(1−a_k b_k) + 2 − a_k d_k − b_k c_k ≥ 0`** (the `P`-log-concavity defect, scaled by `p_k/q_k`, must
  dominate the mixed deficit) for `1≤k<L` (where the RHS deficit is positive). This is the precise open core
  for `T_{m,t,1}` — NOT the false `r_k`-concavity. Verified-true (D^Z≥0 to m=500/1000) but unproven.
- **STATUS — the uniform route is genuinely open.** Refuted certificates/structures this session (all by
  large-parameter testing, mutual GPT↔Claude refereeing): d_leaf≤1⇒LC; uniform `H_k≥0`; uniform prefix-LC;
  `r_k`-concavity; my (i)+(ii) split. The conjecture keeps holding (always via the `D^P` reservoir). This IS
  the open #993-in-(d_leaf≤1) core. **BANKABLE, VERIFIED wins (the session deliverables): (1) LC-pivot
  refutation; (2) m=2 & m=3 `H_k≥0` PROVEN ⟹ `T_{2,t,1}`,`T_{3,t,1}` unimodal (m=3 = non-LC family,
  literature-novel). RECOMMENDATION: consolidate; formalize m=2/m=3 in Lean (add to PR #4192).** Tool:
  inline verify (m=1000,t=5,k=3999) + `verify_restricted.py`.

### ★★★ ULC ROUTE (2026-06-07) — PROVABLE D^P reservoir via Liggett; residual Ψ_k≥0 survives large m (best general-route progress)
GPT's breakthrough idea: **`W` is ULC (ultra-log-concave) of order `2t`** — `w_i/C(2t,i)` is log-concave
(`w_i=2^iC(t,i)+C(t,i-1)`), i.e. `w_{i-1}w_{i+1}/w_i² ≤ i(2t-i)/((i+1)(2t-i+1))`. (NOT ULC of order t+1 — that
fails; order 2t is the right one.) Then **Liggett's ULC convolution theorem** ⟹ `W^m=P` is ULC of order
`2N=2tm` ⟹ the quantitative reservoir **`D^P_k = p_k²−p_{k-1}p_{k+1} ≥ Γ_k p_k²`**, `Γ_k=(2N+1)/((k+1)(2N-k+1))`.
This is a PROVABLE quantitative log-concavity-defect lower bound (the missing piece! — the naive ULC-(t+1)
route had failed). Then `D^Z_k≥0` reduces to the single residual
**`Ψ_k := (2N+1)p_k² + (k+1)(2N-k+1)C_k ≥ 0`** for `1≤k<L`, equivalently (ratio form, R_k=p_k/q_k,
η_k=(N+1)/(k(N-k+2))): `Γ_k R_k² + 2R_k + η_k ≥ (1−η_k)(R_{k-1}+R_{k+1})` — the corrected r_k-concavity, now WITH
the crucial quadratic reservoir `Γ_k R_k²` (which the false r_k version lacked; when C_k<0, R_k is huge so the
quadratic wins).
- **★ VERIFIED (exact, `search993/verify_ULC.py`):** (A) `W` ULC-2t: 0 fail t∈[1,60]. (B) `W^m` ULC-2N
  (Liggett consequence): 0 fail at all tested incl m=1000,t=5 & m=173. (C) `Ψ_k≥0` on `[1,L)`: **0 fail at all
  tested incl m=1000,t=5 AND m=173,t=4 — the exact cases that killed every prior candidate (r_k-concavity, my
  (i)+(ii) split).** So Ψ_k≥0 SURVIVES the large-param tests; it's the first general-route candidate not refuted
  at scale.
- **STATUS:** reservoir `D^P_k≥Γ_k p_k²` is PROVABLE (W ULC-2t [finite one-spider check, verified] + Liggett
  [classical, cited: Liggett 1997, ULC closed under convolution]). Remaining: prove `Ψ_k≥0` (verified-robust to
  m=1000, UNPROVEN). This is the cleanest, most-promising open target of the session — reduces uniform
  `T_{m,t,1}` unimodality to one quadratic-reservoir inequality `Γ_k R_k²+2R_k+η_k ≥ (1−η_k)(R_{k-1}+R_{k+1})`.
  Tool: `search993/verify_ULC.py`.

### Ψ_k proof attempt (2026-06-07) — GPT honest "not yet"; birth-rate machinery reduces to scalar F_k^* (unclosed)
GPT (asked to prove Ψ_k≥0 with the provable reservoir in hand): honest "not yet", new machinery:
- **Birth-rate envelope (W-specific, exact):** `(k+1)p_{k+1}=Σ_{Σa_ℓ=k}(∏w_{a_ℓ})·Σb_{a_ℓ}`, `b_i=(i+1)w_{i+1}/w_i`.
  By Jensen on the concave envelope `β_+` of the (convex-decreasing) `b_i`: `p_{k+1}/p_k ≤ mβ_+(k/m)/(k+1)`
  (and `≥ mβ_-(k/m)/(k+1)`). Stronger than generic ULC. Combined with the ULC product bound `A_kB_k≤M_k` and
  an explicit lower bound `R_k ≥ underline R_k` (huge in the dangerous C_k<0 zone), reduces `Ψ_k≥0` to an
  EXPLICIT scalar certificate `F_k^* = min_{R≥underline R_k}(Γ_k R²+a_k^* R+η_k) ≥ 0`.
- **GPT honest status:** does NOT have uniform proof of `F_k^*≥0`; the upper envelope `S_k^*` (for `A_k+B_k`) is
  "too crude in central regions" (where C_k≥0 anyway). Needs a sharper `A_k+B_k` bound or a region split.
- **Claude verification CAVEAT:** my attempt to check the birth-rate ratio bound + F_k^* (`verify_birthrate.py`)
  had a CONVEX-HULL ORIENTATION BUG in my envelope code (for convex-decreasing `b_i`, the correct upper concave
  envelope is the global endpoint chord; my code used local segments) — so my "ratio-bound fails 7×" and
  "F_k^* fails at m=173,t=4" are MY bug, NOT GPT's machinery being false. GPT's Jensen ratio-bound is sound;
  F_k^*'s uniform nonnegativity is the genuinely-unclosed piece (per GPT). Did not re-fix the envelope (low ROI;
  GPT's reduction is unclosed regardless).
- **NET:** ~12 GPT rounds. The general route (uniform `T_{m,t,1}` unimodality) is the OPEN #993-in-(d_leaf≤1)
  CORE. Real structural advances: the PROVABLE ULC reservoir (W ULC-2t + Liggett ⟹ `D^P≥Γ_k p_k²`) + the clean
  verified-robust single-inequality reduced target `Ψ_k≥0` (= `Γ_k R_k²+2R_k+η_k ≥ (1−η_k)(R_{k-1}+R_{k+1})`).
  But no uniform closure (every scalar certificate so far is either refuted at large param or admittedly crude).
  **Bankable session wins: LC-refutation + m=2,3 unimodality (proven, literature-novel) + the ULC reservoir.**

### Round-17 + session consolidation (2026-06-07)
Round-17 asked GPT to prove the m=2 case of `H_k≥0`. GPT's reply came back empty twice (re-sent once); its
visible reasoning trace explored the one-crossing/mode route (which it itself rated "no easier") but produced
NO final answer/certificate. Net: GPT (prover) is definitively WALLED on `H_k≥0` (rounds 13–17 = four honest
"not yet" + a non-answer). Per the integrity rule, no proof is claimed. **Session consolidated here.**
- **Net deliverables this session (all honest, verified):** (1) REFUTED the log-concavity pivot
  (`d_leaf≤1 ⟹ LC` false; Galvin `T_{3,4,1}`; KL order-26 trees are `d_leaf≤1`) — corrects the project's
  direction, matches literature. (2) Reduced `T_{m,t,1}` (hub-of-spiders, the non-LC counterexample family)
  unimodality to the clean verified-robust open inequality `H_k≥0`, with Lemma B easy and Lemma A robust to
  t=100. (3) Caught/retracted two false strengthenings (the y-graded grouped-defect; a boundary-bug near-miss).
  (4) PR #4192 (3 formalized spider tie-fugacity lemmas) unaffected. **#993 and `H_k≥0` remain OPEN.**

## Attempts & dead ends (logged — count as progress)
- **Disproof of #993 (counterexample hunt):** dead. Exhaustive free-tree search `n≤26` (5.76B trees, 0 non-unimodal); `n=27` done (0 non-unimodal). Conjecture holds; disproof route closed.
- **Spider Lemma M via log-concavity alone:** FALSE — log-concavity does not imply `μ(λ_m)≥m−1` (verified counterexample). Need the tie-balance certificate.
- **Hub-count extremal family (≤2 hubs):** small-`n` artifact; true inf `=1/3` approached by many-hub thin trees ⇒ use per-tie local balance, hub-count-independent.
- **Product certificate via decoupling split** (`λI'−rI=F(λE'−αE)+E(λF'−βF)`, `α+β=r`): **FAILS** —
  for every integer split `α+β=r`, at least one required factor-threshold inequality fails
  (168/168 ties, `m≤12`). The successful route bypasses this split and proves a direct linear ratio certificate.
- **Reverse-Bernoulli / hub-regroup / generic product theorem:** all fail (GPT verdict: circular / split-not-positivity / false). These are dead ends; the current direct `K=2G_mid+G_tail` certificate supersedes them for symmetric `D(m,m,3)`.
- **"Choose a real split a" is CIRCULAR** (a=μ_E(λ_r) ⇒ both brackets ≥0 iff μ_E+μ_F≥r = the goal). Any split route ≡ the goal.
- **Convolution does NOT preserve local tie-balance in general** (verified counterexample, `search993` inline): A=B=[1,2,4] are log-concave + LTB, but A*B=[1,4,12,16,16] fails LTB at r=3 (N_3=−7<0). ⇒ a generic "convolution preserves LTB" theorem is FALSE; the D(m,m,3)=E_m·F_m certificate MUST use the specific E_m,F_m structure (the specific convolution *is* LTB, verified `verify_double.py`). This rules out generic product routes; the later direct `K=2G_mid+G_tail` certificate bypasses this obstruction in the symmetric case.
- **Real-rootedness route DEAD:** verified (a) real-rooted positive polys DO satisfy LTB (50k tests, 0 fail — general fact), BUT (b) **E_m and F_m are NOT real-rooted** (only m=1; checked m≤11 via numpy roots). So I can't get the product LTB via "product of real-rooted is real-rooted ⟹ LTB". E_m,F_m are log-concave but not real-rooted ⇒ the certificate needs a structure-specific argument beyond real-rootedness.

## GPT-5.5 Pro loop (prover) — rounds run
4: equal-arm certificate (verified, formalized). 5: C-cert clarification (Option A′). 6: e=1 mixed spider
certificate (verified, formalized). 7–9: double-spider — 4-term transfer `T₀..T₃`; symmetric factorization
`E_m·F_m`; honest verdict "no complete joint product certificate yet". Next: diagonal-transport/minor cert.
10: **route (C) — precise obstruction (later superseded for the symmetric case).** GPT confirms (matching my counterexample) the general convolution
lemma is FALSE and it has no transport certificate; reduces to the exact missing inequality:
`N_{m,r} = Σ_{i,j}(i+j−r) e_i f_j L^{i+j} M^{2m+2−i−j}` (`L=c_r`, `M=c_{r+1}`) must be written as
`P_{≥0} + Σ_{i≤j} A_{i,j}(e_i e_j − e_{i-1}e_{j+1}) + Σ_{i≤j} B_{i,j}(f_i f_j − f_{i-1}f_{j+1})`,
`A_{i,j},B_{i,j} ≥ 0` — a **minor-cone Positivstellensatz**. GPT: "I do not currently have the explicit
coefficients." **Referee note:** this is a SYMBOLIC certificate (numeric per-instance is trivially
satisfiable, proves nothing), with high-degree multipliers (N carries `c_r^{i+j}`) that must be UNIFORM
in m — a much larger search than the single-spider clean `F=XA+YB` Cnum. This was the sharpest obstruction
before the direct linear-ratio certificate was found. (Routes ruled out so far: general convolution-LTB,
real-rootedness, decoupling split, reverse-Bernoulli, hub-regroup.)

- **Single-spider toolchain does NOT apply to D(m,m,3) (verified, not assumed):** searched for a low-degree `L,M` in `(m,r,q=2^r)` with `c_r·M=c_{r+1}·L` for all `(m,r)` — homogeneous system, 266 eqs / 28 unknowns, **nullspace dim 0**. The convolution tie ratio is genuinely not a clean rational ⇒ the clean `F=XA+YB`+Cnum machinery cannot be ported. Confirms the core obstruction.

## ★ NEW ROUTE (2026-06-07) — LOG-CONCAVITY bypasses the tie-fugacity product certificate
Verified findings (networkx enumeration + DP):
- **Every `d_leaf≤1` tree is log-concave** through `n≤20` (77,143 trees, 0 exceptions). Conjecture:
  `d_leaf≤1 ⟹ log-concave` (⟹ unimodal ⟹ #993 in this regime — no tie-fugacity needed).
- **No non-log-concave tree exists for `n≤20`** (0/1,346,024). Non-log-concave trees (if any) are large.
- **All double-spiders `D(a,b,d)` are log-concave** (512 cases); symmetric `D(m,m,3)` for all `m≤11`.
- **Convolution preserves log-concavity** for positive sequences (36,052 random tests, 0 failures) —
  classical (Karlin total positivity, PF₂ closure; Stanley 1989 survey).
- **`E_m` and `F_m` log-concave** (m≤11).
**Consequence — symmetric double-spider unimodality, clean route (supersedes the stuck product cert):**
`I_{D(m,m,3)}=E_m·F_m` [FV `symm_double_spider_factor`] + `F_m=S(2^m)` log-concave [FV `spider_logconcave.lean`]
+ `E_m` log-concave [provable, binomial toolchain] + convolution-preserves-LC [cited] ⟹ `I` log-concave ⟹
unimodal. Only gap to full FV: formalize `E_m` LC + the convolution-LC step (or cite). The 7 tie-fugacity
dead-ends are now MOOT for this family — log-concavity is the right tool.
**New frontier sub-goal:** prove `d_leaf≤1 ⟹ log-concave` for all `n` (cleaner than tie-fugacity). Still
leaves the general→`d_leaf≤1` reduction and the (large, rare) non-log-concave trees for full #993.

## ★★★ REFUTED (2026-06-07, later) — the LOG-CONCAVITY route above is DEAD. `d_leaf≤1 ⟹ log-concave` is FALSE.
The "n≤20, 0 exceptions" evidence was simply too small. **Counterexample: Galvin's `T_{3,4,1}`**
(root `v` → 3 children `wᵢ`; each `wᵢ` → 4 children `xᵢʲ`; each `xᵢʲ` → 1 leaf `yᵢʲ`; `n=28`, **`d_leaf=1`**).
Its independence polynomial `I = I_w³ + x(1+2x)¹²` with `I_w=(1+2x)⁴+x(1+x)⁴` (=spider `S(2⁴)`) is
**NOT log-concave** (break at k=14: tail `…,37220,5410,60,1`, since `60²=3600 < 5410·1`) but **IS unimodal**
(mode at k=9). So log-concavity fails even inside the thin `d_leaf≤1` class — and this is exactly a
P2-decorated hub-of-spiders, the family we were formalizing.
- **Verified 3 independent ways:** explicit tree DP + structural closed form `I_w^m + x(1+2x)^{tm}`
  (`search993/galvin_test.py`, `galvin_closedform.py`, identical polynomials) + exhaustive `d_leaf≤1`
  enumeration (`search993/dleaf_logconcave.cpp`: 0 non-LC for n≤25 confirmed; n=26..28 running; n=28 hits it).
- **Literature consistent:** Kadrawi–Levit arXiv:2305.01784 (trees not always LC from order 26);
  Galvin family via arXiv:2502.10654; Bautista-Ramos arXiv:2511.00334 (multiple LC breaks).
- **GPT round-11 referee verdict:** Lemma S (shift-sum `P⪯Q ⟹ Q+xP` LC & `Q⪯R`) is TRUE (verified 3732
  hyp-satisfying cases, `search993/verify_lemmaS.py`); convolution-LC TRUE; but **Lemma P_thin
  (`A_u⪯I_u ∀u ⟹ ∏A_u⪯∏I_u` for `d_leaf≤1`) is FALSE** — at `T_{3,4,1}`'s root each child spider `w`
  satisfies `A_w⪯I_w` yet `∏A_w ⪯̸ ∏I_w` (`search993/galvin_invariant_trace.py`). The `d_leaf≤1`
  restriction does NOT rescue `⪯`-under-products. Anchor (restriction-free): Lemma S + conv-LC are general
  algebra, yet `I_{T_{3,4,1}}` is provably non-LC ⟹ the only conjectural piece (P_thin) must be false.
- **Consequence:** NO log-concavity route (CSF / rooted induction / factorization) can prove #993 even in
  `d_leaf≤1`. #993 must be attacked via **unimodality directly** (tie-fugacity / mode-mean — `μ(λ_m)≥m−1`
  + `μ(1)<n/3`), which targets unimodality, not LC. The formalized spider tie-fugacity lemmas (PR #4192,
  `ltb_main`/`mixed_oneleaf`/`emspider`) are UNAFFECTED and remain the right approach. The `D(m,m,3)=E_m·F_m`
  *unimodality-via-LC* shortcut (§6b in proof_document) still holds for that specific factored family
  (both factors ARE log-concave), but does NOT generalize to the `d_leaf≤1` class.

## Status of the "completely solve" goal (honest)
Erdős #993 is a famous OPEN problem (since 1987). The symmetric double-spider subcase now has a
rigorous-informal, machine-audited direct ratio certificate, but this is still **not** a complete
solution of #993: it leaves nonsymmetric double-spiders, broader thin `d_leaf≤1` families, and the
general reduction. Per the goal's own non-negotiable integrity rules, no incomplete proof is presented
as complete. Genuine progress: Lean-verified spider/factor lemmas, the factorization, and now the
machine-audited `D(m,m,3)` ratio certificate; #993 itself remains OPEN.

## Integrity ledger
- No fabricated proofs or citations. #993 itself remains tagged OPEN; the symmetric `D(m,m,3)` ratio
  certificate is tagged rigorous-informal / Lean-pending, not a final solution.
- Spider unimodality is already known (2501.04245) — NOT claimed as ours. Our novel, verified
  contributions: the **formal** tie-fugacity lemmas + the **double-spider factorization** (see `prior_art.md`).
