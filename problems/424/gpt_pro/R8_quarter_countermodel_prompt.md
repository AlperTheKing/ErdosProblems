# R8 prompt: quarter-scale inequality

We are studying the following exact number-theory problem.

Let `G` be the least subset of the positive integers containing `2` and `3`
and closed under `xy-1` whenever `x,y in G` are distinct. Only integers
`n>=2` with `n mod 3 != 1` are relevant. Write `U(n)=2n-1`.

At cutoff `X`, classify an allowed even hole `r` as:

- structural splitless if `r+1` has no factorization `r+1=ab` with
  `2<=a<b` and `a,b` both allowed;
- hard if such an allowed factorization exists, but no such pair has both
  factors in `G`, and `r` has no usable seed-3 reduction.

Let `A_H(X)` be the number of hard even roots `r<=X` for which every
`U^j(r)<=X` remains outside `G`. Let `D(X)` be the number of structural
splitless even roots `e<=X` for which some `U^j(e)<=X` lies in `G`.

Exact independent computation at every cutoff through `10^9` found

`A_H(X) <= D(X) + A_H(floor(X/4)) + 1`

with equality first at `X=186`. A proof would be load-bearing; finite
verification is not a proof. Also `D(X)=o(X)` is already known, so any fixed
positive comparison between `D` and `A_H` is theorem-strength.

Please do one thing only: either prove the displayed quarter-scale inequality
for every integer `X` from the definitions, by giving an explicit
injective/bounded-multiplicity map or a rigorous event-amortization argument,
or refute the proposed mechanism with a precise counterexample/countermodel.
Do not return an equivalent reformulation, an empirical argument, or assume
the desired density conclusion. Track distinct inputs and all floor/endpoint
cases exactly. If the full statement is presently out of reach, isolate the
strongest genuinely proved lemma that advances it and state exactly what
remains.
