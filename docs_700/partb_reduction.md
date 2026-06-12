# Erdős #700 part (b): reduction to a concrete lemma  (state 2026-06-09)

**Goal (part b):** infinitely many composite `n` with `f(n) > n^{1/2}`, where
`f(n) = min_{1<k≤n/2} gcd(n, C(n,k))`.

## 1. The construction (RIGOROUS, verified)

Take `n = q(q+1)`, `q` an odd prime. Write `m = q+1` (so `n = m(m-1)`).

**Facts (all proven):**
- Every prime factor of `q+1` is `< q` (since `q+1 ≤ 2q` and `q` is prime, the largest prime
  factor of `q+1` is `≤ (q+1)/2 < q`). Hence `P(n) = q` and `n/P(n) = q+1`.
- `q+1 > sqrt(n)` **always**: `(q+1)^2 = q^2+2q+1 > q^2+q = n`. So **a "hit" (f(n)=n/P(n)=q+1) gives f(n) > sqrt(n)** automatically.
- **`f(n) = q+1`  ⟺  `q+1` is not "fully sheddable":** there is no `k ∈ (1, n/2]` such that
  `C(n,k)` is coprime to `q+1` (equivalently, `k` is a base-`p` submask of `n` for every prime `p | q+1`).

*Proof of the equivalence.* For prime `p | q+1`, `v_p(n) = v_p(q+1) =: a_p` (as `p ∤ q`), so the
last `a_p` base-`p` digits of `n` are `0`; thus a base-`p` submask `k` of `n` must satisfy `p^{a_p} | k`.
Over all `p | q+1` this forces `(q+1) | k`, i.e. `k = t(q+1)`, `1 ≤ t ≤ ⌊q/2⌋` (from `k ≤ n/2`).
By Kummer, for `k = t(q+1)`, `v_q(C(n,k)) = #carries` adding `t(q+1)` and `(q-t)(q+1)` base `q`;
since in base `q`, `n = (1,1,0)_q`, the only base-`q` submask of `n` in `(1,n/2]` is `k=q`, and
`C(n,q) = (q+1)C(n-1,q-1)`, giving `gcd(n,C(n,q)) = q+1`. For any `k ≠ q` in range, `q | C(n,k)`,
so `gcd(n,C(n,k)) = q · (q+1-part)`. This is `< q+1` iff the `(q+1)`-part is `1`, i.e. iff `k`
fully sheds `q+1`. Hence `f(n) = q` if some `k=t(q+1)` fully sheds `q+1`, else `f(n) = q+1`. ∎

So **`f(q(q+1)) ∈ {q, q+1}`, and `= q+1` (a hit) iff `q+1` is not fully sheddable.**

## 2. The reduction to a fixed-prime lemma

Since `q` is odd, `2 | q+1` always. Restrict to primes `q ≡ -1 (mod 15)` — equivalently
`q ≡ 29 (mod 30)` — so that `2, 3, 5` all divide `q+1`.

**Target Lemma (L).** *If `q` is a prime with `30 | q+1`, then there is no `t ∈ [1, q/2]` such that
`k = t(q+1)` is simultaneously a base-2, base-3 and base-5 submask of `n = q(q+1)`.*

**(L) ⟹ part (b).** Full shedding of `q+1` requires shedding every prime factor, in particular
`2, 3, 5`. So (L) ⟹ `q+1` is not fully sheddable ⟹ by §1, `f(q(q+1)) = q+1 > sqrt(n)`.
By Dirichlet there are infinitely many primes `q ≡ 29 (mod 30)` (`gcd(29,30)=1`). Each gives a
composite `n = q(q+1)` with `f(n) > sqrt(n)`. Hence infinitely many — **part (b) holds.** ∎

## 3. Status of Lemma (L) — **FALSE as stated**; the honest frame is *density*

- **The `{2,3,5}`-covering *technique* (L) is FALSE** — but the *statement* "q≡29 mod30 ⟹ hit"
  is NOT refuted. GPT‑5.5 Pro's example (confirmed on compute): `q = 30032129` is prime,
  `q ≡ 29 (mod 30)`, `q+1 = 2·3·5·61·16411`, and at `t=1` (`k=q+1`) the value `k` IS a base-2,
  base-3 AND base-5 submask of `n` (carries `0,0,0`). So `{2,3,5}` *is* jointly sheddable — the
  *sufficient condition* "(no t sheds {2,3,5}) ⟹ hit" no longer applies. **HOWEVER, brute force over
  all `t∈[1,q/2]` gives `X(30032129)=0` — q=30032129 is STILL A HIT** (no `t` fully sheds `q+1`;
  `t=1` fails to shed `61`). So this is a counterexample to the *proof technique*, not to the family.
- **Status of "q≡29 mod30 ⟹ hit":** ZERO counterexamples known anywhere (verified all `q<2·10^5` by
  full `X(q)`; the dominant terms `D_1=D_2=0` for all 43576 primes `q<5·10^6`; and `X=0` at GPT's
  `q≈3·10^7`). The hit-ness is *more robust* than any fixed-small-prime covering — but, per GPT,
  *any proof must use all prime factors of `q+1` (or a factor not fixed in advance)*. (The cousin
  `ω(q+1)≥4 ⟹ hit` IS genuinely false: `q=36137`, `q+1=2·3·19·317` is an actual non-hit.)
- So no clean fixed-small-prime lemma proves it; the viable route is *density* (below).
- **Mechanism (heuristic; search700/joint_exponent.py, EX_decay.py):** let
  `X(q) = #{t ∈ [1,q/2] : t(q+1) sheds every p | q+1}`; `q` is a hit ⟺ `X(q)=0`. The count of `t`
  passing one base-`p` gate is `G_p(q) ≈ q^{α(p)}`, `α(p) = (2/p)log_p(p!) − 1` (`α(2)=0, α(3)≈.087,
  α(5)≈.19`); under near-independence `X(q) ≈ q^{β}`, `β = 1 − Σ_{p|q+1}(1−α(p))`. `β = 0` exactly
  at `q+1 = 2^a` (Mersenne — matches 0% hit), and `β < 0` once `q+1` has `2` plus any odd prime.
- **What is rigorous:** Markov — `(density of misses in a class) ≤ E[X | class]`. Empirically
  `E[X | q ≡ -1 mod 30] → 0`. If one proves `E[X | class] < 1` (indeed `→0`), a **positive
  proportion** of primes `q` in the class are hits ⟹ infinitely many ⟹ part (b).
- **THE GAP (unproven):** bounding `E[X | class]` rigorously = bounding the "dangerous-pair" count
  `#{(q,t) : q ≤ x, q ≡ -1 (mod 30), t(q+1) sheds all p|q+1}` by `o(π_{30}(x))`, uniformly in `t`.
  This is an equidistribution-of-base-`p`-digits estimate for shifted primes `q+1` (empirically the
  count grows like `x^{0.45}`, sublinear). It is **not currently proven** — this is the heart of
  why part (b) has been open since 1978.

## 4. GPT‑5.5 Pro verdict on provability (rigorous)  — conditional theorem + partial result

GPT‑5.5 Pro assessed the first-moment route against current analytic number theory. Verdict:

**(i) Provable NOW (unconditional partial result).** For every *fixed* `t`,
  `D_t(x) ≪_t x/(log x)^{3/2}`  (a `(log x)^{1/2}` saving over `π(x;30,29) ≍ x/log x`),
by a Selberg/Brun upper-bound sieve on the **units-digit blocker**: for `p∥q+1`, `p∤30`, writing
`c≡(q+1)/p (mod p)`, the base-`p` units digit of `t·(q+1)/p` is `tc mod p` and must be `≤ p−c`;
this removes local density `~1/(2p)` from `q (mod p^2)`. Also proven: a large `P⁺(q+1)` alone does
**not** force a hit (if `P⁺(q+1)>(q+1)^{2/3}` the base-`P⁺` gate is only a weak units-digit gate).

**(ii) Conditional theorem (clean reduction).** Let
  `N_{235}^P(x) = Σ_{q≤x, q≡29(30), q prime} #{1≤t≤q/2 : t passes the 2,3,5 gates}`.
**If `N_{235}^P(x) = o(x/log x)`** (the empirical `x^{0.45}` behaviour is far stronger), **then**
there are infinitely many primes `q≡29 (mod 30)` with `X(q)=0`, hence infinitely many `n=q(q+1)`
with `f(n)=q+1 > √n` — **part (b) holds.** (Proof: a full-shed `t` must pass the 2,3,5 gates since
`2,3,5|q+1`; so #non-hits `≤ N_{235}^P(x) = o(π)`.) A purely combinatorial version (drop primality,
count over all `q≡29 mod30`) is stronger and would also suffice.

**(iii) The barrier (not currently known).** The needed input — a **uniform-in-`t`, multi-base,
high-digit no-carry estimate** for `t(q+1)/p^{a_p} ⪯_p q(q+1)/p^{a_p}` simultaneously in bases
2,3,5, averaged over primes `q≡29 (mod 30)` — does **not** follow from current sieve theory,
shifted-prime factorization results, or digital-prime theorems. It is "closer to a new theorem on
uniform distribution of integers/primes inside multi-base carry-defined sets." This is the genuine
Erdős–Szekeres 1978 barrier.

## 5. Summary (honest)

Part (b) is **reduced to one concrete, empirically-true estimate** `N_{235}^P(x)=o(x/log x)`, with:
a rigorous construction (§1), a rigorous reduction + conditional theorem (§2, §4ii), an
unconditional fixed-`t` partial result (§4i), the `β`-exponent mechanism, and extensive verification
(the `q≡29 mod30` family has **zero** counterexamples anywhere tested — incl. `X=0` at GPT's
`q≈3·10^7`; the `{2,3,5}`-covering *technique* is refuted but the *statement* is not). What remains
is a uniform-in-`t` multi-base carry estimate that is **beyond current methods** (GPT‑5.5 Pro). So
this is a substantial, well-structured **reduction + conditional theorem + partial result** on a
1978-open problem — **not a complete solution.**
