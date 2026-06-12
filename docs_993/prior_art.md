# Prior-Art Summary & Novelty Assessment — Erdős #993

**Problem.** Erdős #993 (Alavi–Malde–Schwenk–Erdős, 1987): the independence sequence
`i_0(T), i_1(T), …` of every finite tree `T` is unimodal. **Open** (verified by computer to `n≤29`).
We commit to #993 and do not switch problems.

This document records what is already in the literature and pins down exactly which of our
machine-checked contributions are *verifiably absent* from it. Every novelty claim is tagged with
our confidence and the evidence checked.

## What is already known (checked)

| Source | Result | Method | Formalized? |
|---|---|---|---|
| Alavi–Malde–Schwenk–Erdős 1987 | the conjecture itself | — | — |
| **arXiv 2501.04245** (Jan 2025) | **all spiders have log-concave (∴ unimodal) independence polynomials** | chromatic symmetric functions | No |
| arXiv 2101.06744 (Yosef et al.) | unimodality results for tree families | combinatorial | No |
| arXiv 2603.03025 (Mar 2026) | unimodality of two families `T_{3,m,n}, T*_{3,m,n}` (non-log-concave) | direct | No |
| **B. Rey manuscript** (github.com/BrettRey/erdos-problem-993) | `μ_T(1)<n/3` in `d_leaf≤1`; reduces #993 (in `d_leaf≤1`) to a tie-fugacity ("Lemma M") lemma | Steiner peeling; **equal-arm spider margin via case-split** (computes `k=1,2,3`, inequalities for `k≥12`, + asymptotics); **mixed spider only computationally** (`k≤3000` certificate + tail) | **Partially** — coefficient algebra + leaf case only; **tie-fugacity/spider results NOT formalized; 2 open `sorry`s** |

**Key distinction (verified):** *log-concavity of the spider independence polynomial does NOT imply
the tie-fugacity inequality* `μ(λ_m) ≥ m−1` (GPT-5.5 Pro exhibited a log-concave-but-failing
truncated geometric sequence; verified numerically). So 2501.04245 (spider log-concavity) does **not**
subsume the tie-fugacity machinery, which is the route to the *full* #993 (all trees) via the
`d_leaf≤1` reduction — not merely spider unimodality.

## Our contributions and their novelty status

Tags: **[FV]** = formally verified in Lean 4 (sorry-free, `native_decide`-free, axioms
`[propext, Classical.choice, Quot.sound]`); **[VC]** = verified by exact computation;
**[RI]** = rigorous informal (referee-checked).

1. **[FV] First machine-checked proof of the equal-arm spider `S(2^k)` local tie-balance.**
   `SpiderLTB.equal_spider_local_tie_balance` (`ltb_main.lean` / PR #4192). For `c_t = 2^t\binom{k}{t}+\binom{k}{t-1}`,
   at every rising tie `c_r≤c_{r+1}`, `N_r := Σ_t (t-r)c_t c_r^t c_{r+1}^{k+1-t} ≥ 0`.
   - *Novel vs. literature:* the **formalization** is absent (manuscript leaves it unformalized);
     our proof is a **single uniform closed-form positivity certificate** (no case-split into
     small-`k` computation + large-`k` asymptotics), and is **mode-free** (all rising ties, not only
     the mode `m`). The *inequality at the mode* appears in the manuscript (Prop. 7), so we do **not**
     claim the mathematical statement as new; we claim the **first formal proof + uniform/mode-free method**.

2. **[FV] First machine-checked, closed-form proof of the one-leaf mixed spider `S(2^a,1)` local
   tie-balance — unconditional.** `Erdos993.MixedOneLeaf.mixed_spider_one_leaf_local_tie_balance`
   (`mixed_oneleaf.lean` / PR #4192). For `c_t = 2^t\binom{a}{t}+(2^{t-1}+1)\binom{a}{t-1}`,
   `N_r ≥ 0` for **all** `r<a` (no rising-tie hypothesis).
   - *Novel vs. literature:* the manuscript establishes mixed-spider margins **only computationally**
     (`k≤3000`); our **closed-form, uniform, unconditional, formally-verified** proof of the `e=1`
     case is, to our checked knowledge, **absent from the literature** (no closed-form proof, no
     formalization). Confidence: high for "absent as a formal/closed-form proof".

3. **[FV] New factorization of the symmetric double-spider's independence polynomial.**
   `EmSpider.symm_double_spider_factor` (`emspider.lean`): `I_{D(m,m,3)} = E_m · F_m`,
   `E_m=(1+2x)^{m+1}+x(1+x)^m`, `F_m=(1+2x)^m+x(1+x)^m` (the equal-arm spider `S(2^m)`).
   - *Novel vs. literature:* **absent from the manuscript** (no double-spiders/factorizations).
     The literature's "well-covered spider" factorizations are **different** (`D(m,m,3)` is not
     well-covered). Confidence: high vs. the #993 manuscript; medium vs. the entire independence-
     polynomial literature (could be folklore for some product construction — flagged, not over-claimed).
   - *Connection to the tree* (that the closed form equals the actual tree's independence polynomial)
     is **[VC]** (graph DP, `search993/verify_double.py`, exact, 0 mismatch).

4. **[FV] Local tie-balance for the factor `E_m`.** `EmSpider.em_factor_local_tie_balance`
   (`emspider.lean`): `N_r≥0` for `r<m`, unconditional. `E_m` is an algebraic factor (not a tree),
   introduced here; this lemma is a building block toward the double-spider via (3).
   - *Novel:* `E_m` and its tie-balance are introduced in this work; absent from the literature.

## Honest limits (the open frontier — logged as progress)

- Erdős #993 **remains open**; we do **not** claim to resolve it.
- The symmetric double-spider `D(m,m,3)`'s tie-balance would follow from (3)+(4)+ the equal-arm
  lemma **plus a "product certificate"** `μ_E(λ_r)+μ_F(λ_r)≥r` at the *convolution* tie. This is an
  **open research step**: GPT-5.5 Pro's adversarial verdict was "no complete joint product
  certificate yet" (reverse-Bernoulli is circular; the natural decoupling split provably fails —
  168/168 ties of `D(m,m,3)`, `m≤12`, `search993/explore_double_d3.py`). Logged as an obstruction.
- Spider *unimodality* is already known (2501.04245); our value added is the **formalized
  tie-fugacity machinery** (toward the full conjecture) and the **double-spider structure**, not
  spider unimodality.

## Summary of what is verifiably absent from the literature

The **machine-verified** (Lean 4, sorry-free) proofs of the spider/mixed-spider tie-fugacity
inequalities (items 1–2), the **double-spider factorization** (item 3), and the **`E_m` factor
lemma** (item 4). The state-of-the-art manuscript explicitly leaves these inequalities unformalized
(2 open `sorry`s) and never treats double-spiders, so our formal artifacts and the factorization are
genuinely new contributions — literature-novel progress on #993, with the product certificate
identified as the precise open frontier.
