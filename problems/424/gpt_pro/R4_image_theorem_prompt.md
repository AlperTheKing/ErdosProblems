# GPT-Pro R4 prompt: image theorem for hard holes

One precise combinatorial question for Erdos Problem 424.

Let

\[
\mathcal A=\{n\ge2:n\equiv0\text{ or }2\pmod3\}.
\]

For a set \(S\subseteq\mathcal A\) containing \(2,3\), define

\[
F(S)=\{2,3\}\cup\{ab-1:2\le a<b,\ a,b\in S\}.
\]

Assume \(S\) is forward closed, meaning \(F(S)\subseteq S\), and put
\(T=F(S)\).

Call an even \(n\in\mathcal A\) hard-shaped if \(n+1\) has at least one
factorization \(n+1=ab\) with \(2\le a<b\) and \(a,b\in\mathcal A\), and
the seed-3 factorization is unavailable: either \(3\nmid n+1\), or
\((n+1)/3\notin\mathcal A\), or \((n+1)/3=3\).

Define

\[
H_T(X)=\#\{n\le X:n\text{ is hard-shaped and }n\notin T\},
\]

\[
Q_T(X)=\#\{m\in\mathcal A:m\notin T,\ 2m-1\le X,\ 2m-1\in T\}.
\]

The proposed image theorem is

\[
\boxed{H_{F(S)}(X)\le Q_{F(S)}(X)\quad\text{for every }X.}
\tag{I}
\]

This is stronger than the previously proposed preservation implication: no
hypothesis \(H_S\le Q_S\) is assumed. Exact CP-SAT optimization over every
forward-closed \(S\) found no counterexample at any selected hard cutoff
through \(X=10{,}000\); the optimum of \(H_{F(S)}(X)-Q_{F(S)}(X)\) was
\(-5\) at \(X=2000\) and \(-68\) at \(X=10000\). This is finite evidence
only.

Useful exact structure: the map \(U(m)=2m-1\) partitions \(\mathcal A\)
into chains rooted at even integers. Forward closure makes membership in each
chain an upper tail. Passing from \(S\) to \(F(S)\) either leaves the threshold
fixed or deletes its first member, moving an old boundary child \(c\) to
\(2c-1\); deleting an even root creates a new boundary at \(2r-1\). Thus at
a fixed cutoff \(X\), with \(Y=\lfloor(X+1)/2\rfloor\), the exact slack change
is old slack minus deleted odd boundary thresholds in \((Y,X]\), minus
deleted hard roots in \((Y,X]\), plus deleted nonhard roots in \([2,Y]\).

Do not use a direct missing-factor injection. It is false already at
\(54+1=5\cdot11\): the missing factor \(11\) is not healed, and the family
\(11p-1\) gives unbounded shared-factor fibers.

Please give exactly one load-bearing result:

1. a rigorous proof of (I), with an explicit injection, prefix-majorization,
   or counting identity; or
2. a fully explicit finite forward-closed counterexample \((S,X)\), verified
   directly; or
3. if (I) is false but the weaker one-step preservation theorem is true,
   prove that theorem precisely.

Do not extrapolate the finite census, assume density, or end with an
equivalent unproved matching statement. Every map, capacity, and prefix
inequality must be explicit. No route survey.
