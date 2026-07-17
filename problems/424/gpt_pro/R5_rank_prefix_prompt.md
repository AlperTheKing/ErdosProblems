# GPT-Pro R5: global rank-prefix additive-one theorem

Let

\[
\mathcal A=\{n\ge2:n\not\equiv1\pmod3\},
\]

and let `G` be the least subset of `A` containing `2,3` and closed under
`a,b -> ab-1` for distinct `a,b`.  Put `M=A\G`.

For an allowed hole `n`, let

\[
\mathcal P(n)=\{(a,b):2\le a<b, a,b\in\mathcal A, ab=n+1\}.
\]

Define its obstruction rank recursively by

\[
\rho(n)=0\quad\text{if }\mathcal P(n)=\varnothing,
\]

and otherwise

\[
\rho(n)=1+\max_{(a,b)\in\mathcal P(n)}
\min\{\rho(x):x\in\{a,b\}\cap\mathcal M\}.
\]

This rank is well founded because every factor is smaller than the output.
A reducible even hole `n` is called hard unless `3|(n+1)` and
`q=(n+1)/3` is allowed and distinct from `3`.

For cutoffs `X,d`, put

\[
H_{\le d}(X)=\#\{n\le X:n\text{ hard and }\rho(n)\le d\},
\]

\[
Q_{\le d}(X)=\#\{q\in\mathcal M:2q-1\le X, 2q-1\in G,
\rho(q)\le d\}.
\]

The exact target is

\[
\boxed{H_{\le d}(X)\le Q_{\le d}(X)+1\quad\text{for every }X,d.}
\tag{T}
\]

This is sufficient for density `2/3`: an existing exact decomposition plus
the proved splitless estimate gives

\[
M(X)\le E(X)+M(\lfloor(X+1)/2\rfloor)
+M(\lfloor(X+1)/3\rfloor)+1,
\]

where `E(X)=o(X)` is already proved.

Exact grounded computation found no failure of (T) through `X=2*10^9`.
The constant one is necessary: strict zero slack first fails at
`(X,d)=(362,2)`, with counts `11` and `10`; the online dominance matching
has exactly that one unmatched source.

Known structural facts:

1. `rho(n)=r` iff `n` dies between stages `S_r` and `S_{r+1}` of the
   descending approximants started from all allowed integers.
2. If `q` and `2q-1` are holes, then
   `rho(2q-1)>=rho(q)+1`.
3. (T) is equivalent to Hall for the nested rank-dominance graph with one
   dummy target.
4. Bounded derivation-local matching cannot prove it.  Source `74` has
   factorization `75=5*15`, but `15,29,57` are all holes, so even two
   seed-2 steps give no local target.  At `10^6`, the all-endpoint two-step
   local graph matches only `4965` of `45583` hard sources.
5. A canonical forest sends each non-root hole to `(n+1)/2` when `n` is odd,
   or to `(n+1)/3` when it is seed-3-easy.  Splitless and hard holes are
   roots.  Component-local balance already fails at source `74`; the needed
   credit is genuinely global.
6. The exact defect identity
   `Delta(X)=K(X)-T2(X)-U3(X)` is known, but controlling `Delta^+(X)=o(X)`
   is quantitatively equivalent to the density theorem and is not a proof.

Please do one thing: either prove (T) by a concrete global invariant or
well-founded induction that explains the single dummy, or give a rigorous
mechanism producing an actual counterexample in this least grounded set.
Do not merely restate Hall, assume a bounded local matching, or replace (T)
by an asymptotic claim of equivalent strength.  Every step must respect the
child-coordinate cutoff `2q-1<=X`, obstruction ranks, and distinct-factor
generation.

