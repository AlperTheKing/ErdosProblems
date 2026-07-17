# C42: additive-one rank dominance suffices

Let \(M(X)\) count allowed holes of the least grounded set \(G\), let
\(E(X)\) count splitless allowed holes, and put \(R(X)=M(X)-E(X)\).
Let \(H(X)\) and \(Q(X)\) be the hard-hole and healed seed-2 boundary
counts of C23/C31.

## Proposition

Assume the C13 theorem \(E(X)=o(X)\). If, for every \(X,d\),

\[
 H_{\le d}(X)\le Q_{\le d}(X)+1,                         \tag{1}
\]

then

\[
 M(X)=o(X)
\]

and therefore \(G\) has natural density \(2/3\).

## Proof

For fixed \(X\), every hole through \(X\) has finite death rank. Taking
\(d\) at least the maximum of those finitely many ranks in (1) gives

\[
 H(X)\le Q(X)+1.                                         \tag{2}
\]

Put

\[
 Y=\left\lfloor\frac{X+1}{2}\right\rfloor,
 \qquad
 Z=\left\lfloor\frac{X+1}{3}\right\rfloor.
\]

The exact C23 decomposition gives

\[
 R(X)\le M(Y)-Q(X)+M(Z)+H(X).
\]

Using (2),

\[
 M(X)\le E(X)+M(Y)+M(Z)+1.                              \tag{3}
\]

Let \(L=\limsup_{X\to\infty}M(X)/X\), which is finite. Given
\(\varepsilon>0\), C13 gives \(E(X)\le\varepsilon X\) for all sufficiently
large \(X\). Divide (3) by \(X\) and take limsup. Since
\(Y/X\to1/2\) and \(Z/X\to1/3\),

\[
 L\le \varepsilon+\frac12L+\frac13L
   =\varepsilon+\frac56L.
\]

Thus \(L\le6\varepsilon\). Letting \(\varepsilon\downarrow0\) yields
\(L=0\), hence \(M(X)=o(X)\). The allowed integers have natural density
\(2/3\), and \(G\) is their complement by exactly \(M(X)\) points through
\(X\), so \(d(G)=2/3\). \(\square\)

## Consequence for the frontier

The zero-slack image theorem \(H\le Q\) is stronger than needed. The exact
remaining F3 input may be replaced by the additive-one rank-prefix theorem
(1), whose constant `1` is forced by the source `362` of rank `2` in C31.
