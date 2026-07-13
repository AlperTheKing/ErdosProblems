# P21: same-parity three-sum-free Sidon reformulation

## Exact bijection

Let

\[
Z=\{0=z_0<z_1<\cdots<z_{p-1}=W\},\qquad G\geq1,
\]

and put \(L=G+2W\).  The fully reflected signed-ruler condition is that
the \(p^2\) integers

\[
\{z_j-z_i:i<j\}\ \dot\cup\
\{G+z_i+z_j:i\leq j\}                              \tag{1}
\]

are all distinct.  Define

\[
E=G+2Z=\{G+2z:z\in Z\}.                              \tag{2}
\]

Then \(E\) is a set of \(p\) positive integers of one parity, with
\(\min E=G\) and \(\max E=L\).  Moreover,

\[
e_j-e_i=2(z_j-z_i),\qquad
e_i+e_j=2(G+z_i+z_j).                                  \tag{3}
\]

Consequently, (1) holds if and only if:

1. every unordered pair sum in \(E\), including the diagonals, is
   distinct; and
2. no positive difference of two elements of \(E\) is an unordered sum
   of two elements of \(E\).

The first condition is literal Sidonicity.  The second is equivalent to

\[
\boxed{E\cap(E+E+E)=\varnothing,}                       \tag{4}
\]

where repetitions are allowed in \(E+E+E\).  Indeed,

\[
e_j-e_i=e_a+e_b
\quad\Longleftrightarrow\quad
e_j=e_i+e_a+e_b.                                         \tag{5}
\]

All elements are positive, so an equality in (5) automatically has
\(e_j>e_i\); no orientation case is lost.

Conversely, let \(E=\{e_0<\cdots<e_{p-1}\}\) be a positive same-parity
Sidon set satisfying (4).  Put

\[
G=e_0,\qquad z_i=(e_i-e_0)/2.
\]

Then the \(z_i\) are integers, (3) holds, and Sidonicity plus (4) proves
that (1) is a disjoint set of \(p^2\) labels.  This proves a bijection,
including every diagonal and every repeated summand in (4).

## Equivalent asymptotic target

The fully reflected case of Problem 864 is therefore exactly the statement

\[
\boxed{
 E\text{ same-parity Sidon and }E\cap3E=\varnothing
 \quad\Longrightarrow\quad
 \max E\geq(3-o(1))|E|^2.}                              \tag{6}
\]

The Erdos--Freud construction lies at the range-separated boundary.  If a
dense Sidon ruler \(Z\subseteq[0,W]\) is translated to

\[
E=G+2Z
\]

with \(G>W\), then \(3\min E=3G>G+2W=\max E\), so (4) is automatic.
With \(G=(1+o(1))W\) and \(W=(1+o(1))p^2\), this gives
\(\max E=(3+o(1))p^2\).

Thus the missing theorem can be read as a stability assertion: a
same-parity Sidon set of asymptotically maximal order that is disjoint from
its threefold sumset must be pushed into the top third, up to lower-order
error.  P13 shows that this cannot be proved after replacing the integer
supports by weak occupation densities; the unit-lattice Sidon and phase
conditions remain essential.

