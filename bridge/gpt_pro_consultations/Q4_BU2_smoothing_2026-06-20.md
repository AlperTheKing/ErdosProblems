# Q4 (SECONDARY, off critical path) — BU2 blow-up peeling, smoothing proof

Status: SAVED for manual relay (GPT-Pro degenerate this session). PRIMARY manual-
relay question remains the `a_7(5n)<n^2` sub-bound in `GPT_PRO_QUESTION.md` (that
one is on the critical path to the general core H2; THIS one only closes the
blow-up special case). Relay this only after the primary.

## Self-contained problem
Fix integer `n>=7`. For `m=(m_0,...,m_4) ∈ Z_{>=0}^5` (indices mod 5) with
`Σ m_i = 5n`, define the cyclic min-product
  `P(m) = min_i m_i·m_{i+1}`.
(Background: `P(m) = β(C5[m])`, the min number of edges to delete to make the
balanced-blow-up graph `C5[m]` bipartite; proved separately.)

Define the **best 5-vertex peeling value**
  `G(m) = max { P(m') : m' ∈ Z_{>=0}^5, m' <= m componentwise, Σ m'_i = 5n−5 }`
(remove 5 vertices to keep the min-product as large as possible), and
  `Δ(m) = P(m) − G(m)`.

**CONJECTURE (BU2):** `Δ(m) <= 2n−1` for all such `m`, with equality iff `m` is
balanced `(n,n,n,n,n)`.

## Verified facts
- BU3 (proved): `P(m) <= n^2`, equality iff balanced.
- Case A (proved): if all `m_i >= n−1`, set `m'_i = n−1` (valid since
  `Σ(m_i−(n−1)) = 5`); then `Δ = P(m) − (n−1)^2 <= n^2 − (n−1)^2 = 2n−1`. ✓
- R1 (proved): if `P(m) <= 2n−1` then `Δ <= P(m) <= 2n−1` trivially (`G>=0`).
  So only the regime `P(m) >= 2n` with some `m_i <= n−2` is open.
- R2 (proved): in regime `P>=2n`, at most one class has `m_i = 1` (a size-1 class
  forces both neighbours `>= 2n`).
- COMPUTATIONALLY VERIFIED `Δ(m) <= 2n−1` for ALL `m`, `n = 7..16` (exhaustive),
  worst case uniquely balanced.

## Failed approaches (all explicit removal rules REFUTED, in complementary regimes)
- all-ones `s=(1,1,1,1,1)`: fails from `n=16`, e.g. `m=(2,31,7,9,31)` gives `Δ=32>31`
  (a small part flanked by two `~2n` parts is over-reduced).
- greedy-max (decrement current max ×5): fails from `n=9`, e.g. `m=(6,11,8,9,11)`
  gives `Δ=18>17` (over-trims one big neighbour of a small class).
- L2-balanced reduction / water-filling: also fail (reduce a small-class neighbour
  too far). The true optimum keeps BOTH neighbours of a small class EQUAL and as
  high as possible and trims the interior; there are many co-optimal `s`.

## Update (2026-06-20): naive smoothing route REFUTED
The per-transfer monotonicity (route (i) below) is FALSE: `Δ` is not monotone
under toward-balance transfers `m→m−e_i+e_j` — 6320 violations at n=7, e.g.
`m=(1,10,1,10,13)` has `Δ=1` but `(2,9,1,10,13)` has `Δ=0`. All violations are in
LOW-`Δ` (small-`P`, R1-trivial) configs, so the BOUND still holds and
`max_m Δ(m)=2n−1` is confirmed uniquely at balanced (n=7..20). So any smoothing
proof must be restricted to the high-`Δ`/`P>=2n` regime, or replaced by a direct
global bound. Five natural routes now refuted (all-ones, greedy-max, water-filling,
L2-balance, naive smoothing).

## Smallest obstruction / exact ask
The optimum is a genuine max–min (protect bottleneck small-class neighbours), not a
balance heuristic. We want a proof of the CONJECTURE. Two concrete routes to assess:
(i) **Smoothing/majorisation:** show any "toward-balance" transfer
   `m → m − e_i + e_j` (with `m_i >= m_j + 2`, respecting the 5-cycle) does not
   decrease `Δ(m)`, so the max of `Δ` is at balanced `= 2n−1`. Is this monotonicity
   actually true, and how to prove it for a max–min functional?
(ii) **Direct construction:** an explicit `m' <= m`, `Σ=5n−5`, with
   `P(m') >= P(m) − (2n−1)`, with a clean correctness proof. The optimum protects
   small-class neighbours — is there a provable closed-form for `m'`?
Please give a complete proof or a counterexample to the equality-at-balanced claim,
plus the correct general removal rule if one exists.
