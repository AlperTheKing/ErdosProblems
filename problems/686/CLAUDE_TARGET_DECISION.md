# Target decision after the easy-first scan (2026-07-26)

User directive: pick whichever we can most easily get a RESULT on; Codex joins afterwards.

## What was rejected, and why

| problem | shape | verdict |
|---|---|---|
| 562 | `log^[r-1] R_r(n) ~[atTop] n` | asymptotic — the failure mode we just stopped for |
| 566 / 567 | `r-hat(G,H) << m` | asymptotic |
| 52 | `max(\|A+A\|,\|AA\|) >> \|A\|^(2-eps)` | Erdos-Szemeredi sum-product, asymptotic AND famous |
| 1210 | `<= sum 1/p + O(1)` | asymptotic |
| 595 | infinite graph, countable unions | infinite/set-theoretic, no finite certificate |
| 701 | Chvatal's conjecture | finite but open since 1974, heavily attacked |
| 938 / 1052 / 1108 | "only finitely many ..." | needs effective bounds |
| 686 | `N = C(m+k,k)/C(n+k,k)` | see below — answer for N=4 is probably NO |

## Why 686 was tried and then downgraded

Chosen because one part is a lone existence question, which closes by exhibiting a witness. Two
exact results came out of it and are kept:

* **binomial form**: `prod_{i=1..k}(a+i) = C(a+k,k)*k!`, so the problem is exactly
  `N = C(m+k,k)/C(n+k,k)` with the same `k` and `m >= n+k`;
* **Kummer carry criterion**: `4*prod(n+i) = prod(m+i)` iff `carries_2(m,k) = carries_2(n,k)+2` and
  `carries_p(m,k) = carries_p(n,k)` at every odd prime `p`;
* every `N` in `2..40` is representable EXCEPT `4` and `25`; no representation of either for
  `k <= 120`, `d <= 400`, `n <= 2,000,000`.

The k=3 case is `4(a^3-a) = b^3-b`, an elliptic curve, so each fixed `k` has finitely many solutions
by Siegel — but the problem quantifies over ALL `k`, so an impossibility proof needs infinitely many
curves at once. **That is a hard Diophantine impossibility target, not a finite closure.** My
selection criterion assumed the answer was yes; it is probably no, so the criterion did not apply.

## The pick: Erdos 306

> Let `a/b > 0` with `b` squarefree. Are there `1 < n_1 < ... < n_k`, each a product of TWO DISTINCT
> primes, with `a/b = 1/n_1 + ... + 1/n_k`?

Reasons it is the best available shape:

1. **Constructive existence.** A positive answer is closed by exhibiting constructions — the one
   shape that admits a finite, checkable closure.
2. **The sibling is SOLVED.** The same Lean file carries `erdos_306.variants.integer_three_primes`
   as `research solved`: every positive integer is an Egyptian fraction with denominators that are
   products of THREE distinct primes. So a working technique sits one step away, and the open gap is
   exactly "three primes -> two primes".
3. **No asymptotics anywhere in the statement** — it is an exact rational identity.
4. **Divergence is on our side**: `sum 1/(pq)` over squarefree semiprimes diverges (roughly
   `(sum 1/p)^2/2`), so no target is excluded on size grounds.

Status of my probes, stated honestly: greedy represents `1/6, 1/3, 1/15` and fails elsewhere, and a
naive DFS over denominators `< 6000` with `<= 10` terms did not terminate in budget. **Neither is
evidence against representability** — greedy is known to be poor for constrained Egyptian fractions,
and the DFS box was too small. The next step is a proper method: fix a denominator set and solve the
exact rational subset-sum by dynamic programming over numerators against a common denominator, which
is exact and far better suited than DFS.
