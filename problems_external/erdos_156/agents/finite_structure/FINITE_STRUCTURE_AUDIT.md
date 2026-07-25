# Erdős 156 Route B: finite maximal-ruler structure audit

## Frontier verdict

The three calibrated finite witnesses do not extend to a scalable
construction.

They satisfy a stronger property than maximality: their entire host interval
is covered by \(A+A-A\), without using midpoint witnesses.  However:

1. the apparent cubic continuation from orders \(3,4,5\) predicts a
   six-mark witness at \(N=72\), and the audited exhaustive C++ run returns
   `NO_HIT`;
2. every nontrivial Cartesian/radix product of finite rulers contains an
   explicit parallelogram and is not Sidon.

Thus the finite-seed and radix-product mechanism exits.  This does not close
Erdős problem 156.  The single missing bridge is an infinite algebraic
family of non-Cartesian Singer lifts whose signed triple set covers every
required residue/quotient pair.

## 1. Exact maximality identity

Let \(A\subset\mathbb Z\) be Sidon and let \(x\notin A\).  The only new sums
after adjoining \(x\) are \(x+a\), \(a\in A\), and \(2x\).  Therefore
\(A\cup\{x\}\) is not Sidon if and only if at least one of the following
holds:

\[
 x+a=b+c\qquad(a,b,c\in A),
\tag{1}
\]

or

\[
 2x=a+b\qquad(a,b\in A,\ a\ne b).
\tag{2}
\]

The unordered pairs in (1) are automatically different because
\(x\notin A\).  Equation (2) is also nontrivial because a Sidon set cannot
contain the midpoint of two distinct members.

Define

\[
 T(A)=A+A-A
\]

and

\[
 H(A)=\{(a+b)/2:a,b\in A,\ a<b,\ a+b\equiv0\pmod2\}.
\]

Then the exact identity is

\[
 A\text{ is maximal Sidon in }[1,N]
 \iff
 [1,N]\subseteq T(A)\cup H(A).
\tag{3}
\]

Equivalently, writing
\(\Delta(A)=\{|a-b|:a,b\in A,\ a\ne b\}\), a missing \(x\) is blocked when
one of its new distances \(|x-a|\) is in \(\Delta(A)\), or when two new
distances are equal.  The second case is exactly (2).

## 2. General counting obstruction

Let \(|A|=k\).  For each subtracted element \(a\), there are
\(k(k+1)/2\) unordered pairs \(\{b,c\}\), allowing \(b=c\).  Exactly \(k\)
of those pairs contain \(a\); all of their expressions \(b+c-a\) lie in
\(A\).  Hence

\[
 |T(A)|\le k+\frac{k^2(k-1)}2.
\tag{4}
\]

There are at most \(\binom{k}{2}\) midpoint values, so (3) implies

\[
 N\le
 k+\frac{k^2(k-1)}2+\binom{k}{2}
 =\frac{k^3+k}{2}.
\tag{5}
\]

This is a rigorous obstruction valid for every maximal Sidon set in an
integer interval.  In particular, five marks can saturate at most

\[
 \frac{5^3+5}{2}=65
\]

integers.  Thus any maximal Sidon set in \([1,72]\) has at least six
members.  Combined with the exhaustive `NO_HIT` at \(N=72,k=6\), the
calibrated search implies that the minimum there is at least \(7\).

Equation (5) has the correct cubic scale but does not provide an upper
construction.

## 3. Exact finite witness structure

Translation does not change the difference set or the length of a covered
interval.  Normalize each witness by subtracting its minimum.

### Order 3

\[
 A=\{2,5,6\},\qquad R=\{0,3,4\}.
\]

\[
 \Delta^+(R)=\{1,3,4\}.
\]

Direct evaluation gives

\[
 T(R)=
 [-4,-3]\cup[-1,8].
\]

Thus \(R+2\) covers \([1,10]\) by (1) alone.

### Order 4

\[
 A=\{4,7,12,13\},\qquad R=\{0,3,8,9\}.
\]

\[
 \Delta^+(R)=\{1,3,5,6,8,9\}.
\]

Direct evaluation gives

\[
 T(R)=
 [-9,-8]\cup[-6,-5]\cup[-3,18].
\]

Thus \(R+4\) covers \([1,22]\) by (1) alone.

### Order 5

\[
 A=\{10,18,19,25,30\},\qquad
 R=\{0,8,9,15,20\}.
\]

\[
 \Delta^+(R)=\{1,5,6,7,8,9,11,12,15,20\}.
\]

Direct evaluation gives

\[
 T(R)=
 \{-20,-15\}\cup[-12,-11]\cup[-9,32]\cup\{35,40\}.
\]

Thus \(R+10\) covers \([1,42]\) by (1) alone.

The second \(N=42\) witness listed in OEIS,
\(\{13,18,24,25,33\}\), is the reflection of the first:
after normalization it is
\[
 20-R=\{0,5,11,12,20\}.
\]

For all three calibrated witnesses, every integral midpoint already belongs
to \(T(R)\); midpoint witnesses add nothing.

The main consecutive components have lengths
\[
 10,\ 22,\ 42.
\tag{6}
\]

These are the observed maxima for \(k=3,4,5\).  They happen to fit
\[
 F(k)=2+\frac{k^3-k}{3},
\tag{7}
\]
which predicts \(F(6)=72\).  The exact `NO_HIT` at \(N=72,k=6\) disproves
this continuation at its first unobserved value.  No inference from the
finite OEIS terms is therefore valid.

The OEIS data used only for comparison were:

- A382397, minimum size of a maximal ruler in \([1,n]\);
- A382396, number of minimum-size maximal rulers.

The OEIS entry itself warns that the known terms are insufficient to
distinguish candidate continuations.

## 4. Exact obstruction to radix and block products

The standard way to scale a finite digit construction is a Cartesian/radix
product

\[
 C=R+QB=\{r+Qb:r\in R,\ b\in B\}.
\]

This can never be Sidon when \(|R|,|B|\ge2\).  Choose distinct
\(r_1,r_2\in R\) and distinct \(b_1,b_2\in B\).  Then

\[
 (r_1+Qb_1)+(r_2+Qb_2)
 =
 (r_1+Qb_2)+(r_2+Qb_1),
\tag{8}
\]

and the two unordered pairs are different.  This is a nontrivial Sidon
collision for every integer \(Q\), irrespective of carry separation.

The same identity shows that duplicating a block is impossible:
\[
 R\cup(T+R)
\]
is not Sidon for any \(T\) when \(|R|\ge2\), because
\[
 r_1+(T+r_2)=r_2+(T+r_1).
\tag{9}
\]

Consequently:

- Cartesian powers of any calibrated witness are not Sidon;
- mixed-radix digit concatenation is not Sidon;
- recursive unions of translated copies are not Sidon.

Any scalable construction must correlate the digits globally so that no
rectangle (8) survives.  Selecting an arbitrary non-Cartesian subset is not
a bridge: it must also retain \(O(N^{1/3})\) points and prove the full
coverage identity (3).

## 5. Search audit and exact scope

The search engine

`problems_external/erdos_156/engine/small_maximal_search.cpp`

has source SHA-256

`404D35AD74C3C7904FED6A865A1906F366D3A98165541678E5713237799C93CF`.

It partitions all increasing \(k\)-subsets by their first element.  During
depth-first search it rejects exactly repeated positive differences.  At a
leaf, for every \(x\notin A\), it checks:

1. whether a new distance \(|x-a|\) repeats an old difference; or
2. whether two new distances \(|x-a|\) coincide.

These are exactly (1) and (2), so a completed `NO_HIT` is an exhaustive
finite result for that \((N,k)\).  It is not an asymptotic theorem.

## Exit condition

`DEAD: the finite-witness cubic extrapolation fails at k=6, N=72, and every
nontrivial radix/Cartesian replication has the explicit parallelogram
collision (8).`

This audit does not resolve Erdős 156.  The sole theorem-closing bridge still
missing is:

> Construct, for infinitely many prime powers \(p\), a non-Cartesian family
> of \(p+1\) Singer lifts with \(M=\Theta(p)\) whose signed triple values
> cover every admissible residue/quotient pair, and prove that coverage
> uniformly in \(p\).

Without that bridge, additional isolated finite certificates are excluded by
the Route B exit condition.
