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

---

## 6. BASE CASE SETTLED: 1 IS representable

`tools/claude_erdos306_csp.py` searched the prime-graph CSP directly -- processing primes in
increasing order, fixing each vertex's neighbourhood, and checking its congruence immediately, which
prunes by a factor of about `p` per vertex. Primes `<= 31` and `<= 37` gave nothing within the node
cap; primes `<= 41` produced a solution.

```
        1 = sum of 58 distinct 1/(pq),  primes used {2,3,5,7,11,13,17,19,23,29,31,37,41}

        6   10   14   15   21   22   26   33   34   35   38   39   46   51   55   57
       58   62   65   69   77   85   91   93   95  111  115  119  133  143  145  155
      161  187  203  209  217  221  247  253  259  299  341  403  437  451  481  533
      551  589  629  713  779  851  899  943 1147 1517
```

**Independently gated** (`problems/306/claude_gate_306_one.py`, own factorisation, nothing imported
from the search):

* every denominator is a product of exactly two DISTINCT primes — yes, all 58;
* all distinct — 58 unique of 58;
* all `> 1` and strictly increasing when sorted — yes;
* **sum of reciprocals `= 1` exactly** as a rational — yes.

The predicted local congruence holds at every one of the 13 primes (`sum of inverse neighbours == 0
mod p`), with degrees `10,10,10,11,10,11,7,10,10,5,10,7,5`. That confirms the reduction of section 3
is correct and not merely convenient.

### What this does and does not settle

It settles the **base case** `a/b = 1`, which was the first thing that had to be true: had `1` been
unrepresentable the answer to 306 would have been no outright. It also shows the CSP formulation is
an effective search method rather than a restatement — it found in seconds what greedy, naive DFS and
meet-in-the-middle all failed to find.

It does **not** prove 306, which asks for every `a/b` with `b` squarefree. The next targets are the
integers `2, 3, ...` and then rationals with nontrivial squarefree denominators, where the congruence
at each `p | b` changes (the right-hand side is no longer `0 mod p`).
