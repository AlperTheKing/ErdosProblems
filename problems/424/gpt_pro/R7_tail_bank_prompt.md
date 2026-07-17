# CX-R7 prompt: persistent hard-chain tail bank

We are studying Erdos Problem #424 in the following exact distinct-value form.

Let G be the least subset of the positive integers containing 2,3 and closed
under `xy-1` for distinct `x,y in G`. Put

`A={n>=2:n is not congruent to 1 mod 3}`, `M=A\G`.

For allowed `n`, let `P(n)` be the set of pairs `2<=a<b`, `a,b in A`,
`ab=n+1`. A hole `n in M` is splitless when `P(n)` is empty. Let `E(X)`
count splitless holes `<=X`; the elementary sieve proof `E(X)=o(X)` is
available.

An even hole `r` is called hard when `P(r)` is nonempty and it is not
seed-3-easy, where seed-3-easy means `3` divides `r+1` and
`q=(r+1)/3` is allowed and `q!=3`. Define `U(n)=2n-1` and `top_X(r)` as
the largest `U^j(r)<=X`. Let `A_H(X)` count hard roots `r<=X` such that
every `U^j(r)<=X` is still a hole.

Exact computation through `10^6` gives

`A_H(X) <= E(X)-E(floor(X/2))`

at every cutoff (largest observed ratio `656/1033`), but this is only finite
evidence. Proving merely `A_H(X)=o(X)` is already enough for the current
hole-contraction proof of positive density; a bounded-error injection into
upper-half splitless holes would be stronger than needed.

Please work on this precise scalar arithmetic question, not the previously
failed global rank-matching theorem:

1. Prove `A_H(X)=o(X)`, preferably from a necessary arithmetic condition on
   a persistent hard chain and a sieve/counting argument; or
2. prove `A_H(X) <= E(X)-E(floor(X/2))+o(X)`; or
3. give a rigorous obstruction showing why these statements do not follow
   from the known splitless characterization.

The distinct-input condition `a<b` is essential. Do not infer anything from
the finite census alone. Do not return a reduction equivalent to the original
density conjecture. Exact-test any proposed pointwise map against the first
persistent roots `54,74,114,144,174,186`. A useful response must contain one
concrete proved lemma, a derivation with all quantifiers, or an explicit
falsifier to a proposed intermediate claim.
