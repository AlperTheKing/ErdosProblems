# Erdos 686 — exact binomial reformulation and the carry criterion

Root-agent entry, 2026-07-26. Mine. Everything here is an exact identity; nothing is a relaxation.

## 1. The problem is a ratio of binomial coefficients

`prod_{i=1..k}(a+i) = (a+k)!/a! = C(a+k, k) * k!`, so the `k!` cancels and

```
        N = prod_{i=1..k}(m+i) / prod_{i=1..k}(n+i)   <==>   N = C(m+k, k) / C(n+k, k),
```

with the SAME lower index `k` on both sides and `m >= n+k`. Writing `M = m+k`, `L = n+k`:

> **Erdos 686 asks: for which `N` do there exist `k >= 2` and `L, M` with `M >= L + k` and
> `C(M, k) = N * C(L, k)`?**

## 2. Kummer's theorem turns it into a CARRY condition

`v_p(C(a+k, k))` equals the number of carries when adding `a` and `k` in base `p` (Kummer). Applying
this to `C(M,k) = N * C(L,k)` prime by prime, with `N = 4`:

```
        carries_2(m, k) = carries_2(n, k) + 2
        carries_p(m, k) = carries_p(n, k)        for EVERY odd prime p
```

Derivation: `v_p(prod_{i=1..k}(a+i)) = (k - s_p(a+k) + s_p(a))/(p-1)` where `s_p` is the base-`p`
digit sum, and `s_p(a+k) - s_p(a) = s_p(k) - (p-1) * carries_p(a, k)`. Matching valuations on both
sides of `4 * prod(n+i) = prod(m+i)` gives exactly the two lines above.

So a representation of `4` is precisely a pair `(n, m)` whose base-`p` carry counts against `k` agree
at every odd prime and differ by exactly `2` at `p = 2`. That is a rigid arithmetic condition, and it
is why representations are scarce rather than merely hard to find.

## 3. Search status (exact, mine)

`tools/claude_erdos686_search.py` — every `N` in `2..40` is representable EXCEPT `4` and `25`.
`tools/claude_erdos686_deep.py` — for each `(k, d)` with `m = n+k+d`, the ratio is strictly decreasing
in `n`, so `n` is found by exact binary search rather than scanned. Over

```
        k <= 120,   d = m-n-k <= 400,   n <= 2,000,000
```

there is **no representation of 4 and none of 25**. Control: the known representations of
`2, 3, 9, 16, 36` are re-found, so the search is not silently broken.

## 4. Honest reassessment of this target

I selected 686 because one part is a single existence question, and an existence question closes by
exhibiting a witness. The evidence now says the answer for `4` is probably **NO**, so no witness
exists and the finite-closure route does not apply. Proving non-representability is a Diophantine
impossibility statement, which is a different and harder kind of target.

What is genuinely in hand: the binomial reformulation and the carry criterion above, which are exact
and reduce the question to base-`p` carry combinatorics, plus a large explicit region where 4 and 25
are certified absent. That is a real starting point, but it is NOT a proof, and by the standing rule
an exhausted search is never an impossibility proof.

## 5. The k = 2 case for N = 4, settled by argument

`4(n+1)(n+2) = (m+1)(m+2)`; with `a = n+1`, `b = m+1`, `b(b+1) = 4a(a+1)`; multiplying by 4 and
setting `X = 2b+1`, `Y = 2a+1` gives `X^2 - 4Y^2 = -3`, so `(X-2Y)(X+2Y) = -3`, forcing `X = Y = 1`
and `a = b = 0`. **No admissible solution at `k = 2`.** This is the model for what a real
impossibility argument looks like here: a Pell-type descent, not an exhausted range.
