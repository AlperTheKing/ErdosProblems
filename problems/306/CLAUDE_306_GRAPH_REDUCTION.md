# Erdos 306 — the semiprime set is a GRAPH on primes, and integrality is a local congruence

Root-agent entry, 2026-07-26. Mine. Target selected after the easy-first scan (see
`problems/686/CLAUDE_TARGET_DECISION.md`).

## Statement

Let `a/b > 0` be rational with `b` SQUAREFREE. Are there `1 < n_1 < ... < n_k`, each a product of two
distinct primes, with `a/b = 1/n_1 + ... + 1/n_k`?

## 1. The hypothesis is exactly the necessary condition

The lcm of squarefree numbers is squarefree, so ANY sum of reciprocals of squarefree numbers has
squarefree denominator. So "`b` squarefree" is precisely the obvious obstruction, and 306 asks
whether it is the ONLY one. That is a good shape: it asks whether the trivial necessary condition is
sufficient.

## 2. The natural construction route is provably dead

One would like `1 = sum 1/(2q) = (1/2) sum 1/q` by making `sum_{q in S} 1/q = 2` over distinct odd
primes. **Impossible**: writing `sum_{q in S} 1/q = (sum_q prod_{r != q} r) / prod_q q`, any
`q_0 in S` divides every numerator term except the `q = q_0` one, so `q_0` does not divide the
numerator and the fraction is never an integer. (This is the classical fact that a sum of distinct
prime reciprocals is never an integer.)

## 3. The reduction: a graph on primes with a local congruence at each vertex

Choose a prime set `P`, put `L = prod(P)`, and view the chosen semiprimes as an EDGE SET `T` on `P`.
Then `sum_{(p,q) in T} 1/(pq)` has numerator `sum_{(p,q) in T} L/(pq)` over `L`, and
`L/(pq) = prod_{s not in {p,q}} s`.

Reduce the numerator mod a fixed `p in P`. Every edge avoiding `p` contributes a multiple of `p`;
the edges at `p` contribute `L_p/q` with `L_p = L/p`, which is prime to `p`. With `S_p` the set of
primes matched to `p`,

```
        numerator  ==  L_p * sum_{q in S_p} q^{-1}   (mod p).
```

Integrality of the sum forces `L | numerator`, hence `p | numerator`, and `p` does not divide `L_p`:

> **For every `p in P`:  `sum_{q in S_p} q^{-1} == 0  (mod p)`.**

So the CONGRUENCES decide integrality and the MAGNITUDE `sum_{(p,q) in T} 1/(pq)` decides which
integer. This also explains item 2 cleanly: for single primes the same computation gives the
condition `1 == 0 (mod q)`, which is impossible — the semiprime case escapes it only because `S_p`
has many elements.

**Verified** (`tools/claude_erdos306_graph.py`): over all `2^15` edge sets on primes `<= 13` and all
`2^21` on primes `<= 17`, **no non-integer subset passes every congruence** — zero false positives,
confirming necessity. Neither prime set yields an integer sum, which is expected since
`sum 1/(pq)` is below 1 there.

## 4. Base case status: is 1 representable?

`sum 1/(pq)` over squarefree semiprimes DIVERGES (roughly `(sum 1/p)^2 / 2`), so no target is
excluded on size grounds. But the sum grows slowly:

```
        primes <= 13   total 0.685348
        primes <= 19   total 0.838242
        primes <= 23   total 0.901524
        primes <= 29   total 0.953212
        primes <= 31   total 1.002678   <- first prime set that can reach 1 at all
```

Exact meet-in-the-middle over all 55 semiprimes on primes `<= 31` finds **no** subset summing to 1;
with only `0.0027` of slack there is essentially no freedom. So any representation of 1 needs primes
beyond 31. Greedy and naive DFS also fail, but both are weak methods here and neither is evidence.

## 5. The open target, stated precisely

> Find a finite prime set `P` and a graph `T` on `P` with `sum_{q in S_p} q^{-1} == 0 (mod p)` at
> every vertex `p`, and `sum_{(p,q) in T} 1/(pq) = 1`.

The congruence system is local and highly constrained, which is what makes this searchable rather
than hopeless: it is a constraint-satisfaction problem on a graph, not an unstructured subset-sum.
A concrete handle: for the largest prime `P`, two edges `(P,x)` and `(P,y)` satisfy the condition
whenever `P | x + y` — e.g. `P = 31` with `x = 2, y = 29`, giving `1/62 + 1/58`.
