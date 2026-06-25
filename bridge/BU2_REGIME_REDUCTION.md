# BU2 (blow-up peeling) — regime reduction + structure (2026-06-20)

Owner: Step-2 lead. Sharpens the blow-up case of the Peeling Lemma (H2).
Verifier: `experiments/verify_BU2_blowup_peeling.py`.

## Statement (blow-up case of H2)
For `m ∈ Z_{>=0}^5`, `Σ m_i = 5n`, write `P = β(C5[m]) = min_i m_i m_{i+1}` (BU1,
proved). Removing `s_i` vertices from class `i` (`Σ s_i = 5`, `0<=s_i<=m_i`)
gives `C5[m−s]` with `β = P'(s) = min_i (m_i−s_i)(m_{i+1}−s_{i+1})`.
**BU2:** there exists such `s` with peeling drop `Δ(s) = P − P'(s) <= 2n−1`.

## NEW (this cycle): two exact structural facts that simplify BU2

### R1 — Trivial regime `P <= 2n−1`  [PROVED, clean]
`Δ(s) = P − P'(s) <= P` for every valid `s` (because `P'(s) >= 0`; removing
vertices cannot raise β). Hence if `P <= 2n−1`, **any** `s` gives `Δ <= 2n−1`.
⟹ **BU2 only needs the regime `P >= 2n`** (every adjacent product `>= 2n`).

### R2 — In regime `P >= 2n`, at most ONE class has size 1  [PROVED]
If `m_i = 1` then its two products `m_{i−1}·1` and `1·m_{i+1}` are `>= P >= 2n`,
forcing **both neighbors `>= 2n`**. Two size-1 classes cannot be adjacent (their
shared product would be `1 < 2n`); two *non-adjacent* size-1 classes would force
three classes `>= 2n` plus two `=1`, total `>= 6n+2 > 5n`. ⟹ ≤ 1 size-1 class.

## Why the naive route fails (counterexample, corrects a trap)
All-ones `s=(1,1,1,1,1)` is NOT always valid/sufficient: for
`m=(1,24,5,6,24)` (`n=12`, `P=24=2n`) all-ones drops the size-1 class to 0, so
`P'=0` and `Δ_allones = 24 = 2n > 2n−1`. **Adaptive `s` avoiding the size-1
class is required**, e.g. `s=(0,2,1,1,1) ⟹ Δ=4`. (General principle from the
data: the optimal `s` always sets `s_p = 0` on a size-1 class `p` and removes
from its large neighbors / the interior.)

## Computational status — EXHAUSTIVE, COMPLETE through n=20
`verify_BU2_blowup_peeling.py`, ALL compositions of `5n` into 5 positive parts,
`n = 7..20` CONFIRMED (skipping the R1-trivial `P<=2n−1` cases; the `P>=2n` regime
ranges from 10 806 cases at n=7 to 2 030 186 at n=20):
- **`Δ_best <= 2n−1` with ZERO violations for every `n=7..20`** ⟹ BU2 verified.
- **Worst case is UNIQUELY the balanced blow-up** `m=(n,n,n,n,n)`, `s=(1,1,1,1,1)`,
  `Δ = 2n−1` exactly (the extremal `C5[n]`). Every unbalanced `m` has `Δ_best < 2n−1`.
- All-ones fails on the small-part-flanked configs (size-1, and for `n>=16` size-2);
  adaptive `s` always recovers `Δ <= 2n−1` (see CORRECTION below).

## ⚠️ CORRECTION (2026-06-20): all-ones is REFUTED even for all-parts-`>=2`
Earlier notes/ledger suggested all-ones `(1,1,1,1,1)` settles the all-`m_i>=2`
sub-case. **FALSE for `n>=16`.** First counterexample (exhaustive search):
`m=(2,31,7,9,31)`, `n=16`, all parts `>=2`, `P=62`: all-ones gives `Δ=32=2n >
2n−1=31`. The structure is a SMALL part (here 2) flanked by two `≈2n` parts — the
same obstruction as a size-1 part; all-ones over-reduces the small part. The
lemma still holds via ADAPTIVE `s` (e.g. for `(39,2,39,10,10)` n=20,
`s=(1,0,2,0,2)` gives `Δ=4`). First all-`>=2` all-ones failure by `n`:
`n=16:(2,31,7,9,31)`, `n=17:(2,33,6,11,33)`, `n=18:(2,35,6,12,35)`,
`n=19:(2,37,6,13,37)`, `n=20:(2,39,6,13,40)`. (All-ones works for ALL configs
when `n<=15`; that is why the prior `n<=13` check did not see it.)

## Honest status
- R1 (trivial regime) and R2 (≤1 size-1 class): **PROVED**.
- BU2 itself: **COMPUTATIONALLY VERIFIED `n<=20`** (`Δ_best<=2n−1`, worst UNIQUELY
  balanced `C5[n]`), reduced to the structured regime `P>=2n`. **No simple explicit
  removal rule can work — all three natural candidates are REFUTED in COMPLEMENTARY
  regimes:**
    * all-ones REFUTED for `n>=16` on SMALL-part-flanked configs (e.g.
      `(2,31,7,9,31)`);
    * greedy-max (decrement current-max ×5) REFUTED from `n=9` on NEAR-balanced
      configs (e.g. `(6,11,8,9,11)`, `Δ=18>17`);
    * water-filling REFUTED (EXP-5, `(7,12,9,10,12)`).
  all-ones is optimal near balance / greedy-max near small-parts, but each fails
  where the other works ⟹ the optimal `s` must INTERPOLATE.
- **The non-constructive smoothing route is ALSO refuted (2026-06-20):** the per-
  transfer monotonicity "balancing `m→m−e_i+e_j` (with `m_i>=m_j+2`) never decreases
  `Δ_best`" is FALSE — 6320 violations at n=7 (e.g. `m=(1,10,1,10,13)`, `Δ_best=1`,
  transfer to `(2,9,1,10,13)` gives `Δ_best=0`). The violations are confined to
  LOW-`Δ` configs (small `P`, the R1-trivial regime), so they do NOT threaten the
  bound, but they kill the naive majorisation proof. **Confirmed positively:**
  `max_m Δ_best(m) = 2n−1` exactly, uniquely at balanced, for every `n=7..10`
  (and `n<=20` by exhaustive `verify_BU2`). So the lemma is robustly TRUE; the
  difficulty is purely proof-theoretic — `Δ_best` is a max–min difference that
  peaks at balanced without being monotone toward it. A valid proof likely needs
  monotonicity restricted to the high-`Δ` (`P>=2n`) regime, or a direct global
  bound. **All five natural routes (4 explicit rules + naive smoothing) refuted;
  full proof OPEN and apparently genuinely hard.**
- Scope reminder: BU2 is the BLOW-UP special case; it does NOT close the general
  Peeling Lemma (H2/MC4), which remains the open core over arbitrary triangle-free
  graphs.
