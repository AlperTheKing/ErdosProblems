# C25: hard-hole fixed-multiplier sieve

## Verdict

No proof that \(H(X)=o(X)\) is obtained.  The output is:

1. a rigorous two-residue, finite-multiplier upper recurrence with an exact
   Perron--Frobenius criterion;
2. a subcritical concrete matrix with
   \(\rho=0.999214644481743992\ldots<1\);
3. an exact counterexample to the residual-free recurrence at \(X=252\);
4. an exhaustive audit through \(10^8\), independently replayed through
   \(10^5\).

The counterexample is structural.  The seventh residue-zero hard hole is
\(252\), and

\[
252+1=11\cdot23
\]

has no generated factor.  At this cutoff all eligible generated-multiplier
channels together have capacity only \(6\).  Thus a direct fixed-multiplier
sieve necessarily retains a residual class.

At \(10^8\), that residual contains

\[
3{,}065{,}623\quad\hbox{of}\quad 3{,}368{,}726
\]

hard holes.  This is a finite obstruction, not a proof that the residual
has positive upper density.

Code and exact output are in
[C25_hard_hole_sieve](../../compute/wave3/C25_hard_hole_sieve/).

## 1. Two residue types

Retain C16's notation

\[
\mathcal A=\{n\ge2:n\not\equiv1\pmod3\},\qquad
\mathcal M=\mathcal A\setminus G.
\]

Let \(M_i(X)\) count holes \(n\le X\) with \(n\equiv i\pmod3\), for
\(i\in\{0,2\}\).  Split the odd reducible holes in the same way and call
their counts \(O_0,O_2\).  Write \(H_0\) for the hard holes divisible by
3 and \(H_2\) for the remaining hard holes.

Every member of \(H_2\) is \(2\pmod {18}\).  Indeed, write
\(n+1=3q\).  The hard condition says that the seed-3 cofactor \(q\) is
forbidden modulo 3; since \(n+1\) is odd, \(q\equiv1\pmod6\).

Let \(E_i\) be the splitless holes of residue \(i\), and let \(S\) be the
seed-3 even holes.  The partition and the seed injections give

\[
\begin{aligned}
M_0(X)&=E_0(X)+O_0(X)+H_0(X),\\
M_2(X)&=E_2(X)+O_2(X)+S(X)+H_2(X),                 \tag{1}\\
O_0(X)&\le M_2\!\left(\left\lfloor{X+1\over2}\right\rfloor\right),\\
O_2(X)&\le M_0\!\left(\left\lfloor{X+1\over2}\right\rfloor\right),\\
S(X)&\le M_0\!\left(\left\lfloor{X+1\over3}\right\rfloor\right)
       +M_2\!\left(\left\lfloor{X+1\over3}\right\rfloor\right). \tag{2}
\end{aligned}
\]

C13 proves \(E_0(X)+E_2(X)=o(X)\).

## 2. Which fixed multipliers can act

For a hard hole \(n\), the number \(N=n+1\) is odd.  Consequently:

* no even generated multiplier, including \(14\), divides \(N\);
* \(9\nmid N\): for \(H_0\), \(3\nmid N\), while for \(H_2\),
  \(v_3(N)=1\);
* on \(H_0\), an admissible odd generated divisor must be
  \(d\equiv2\pmod3\);
* on \(H_2\), one may use either \(d\equiv2\pmod3\), or
  \(d=3e\) with \(e\equiv2\pmod3\), equivalently \(d\equiv6\pmod9\).

This removes two of the first suggested multipliers before any
computation: \(9\) and \(14\) are inert on \(H\).

Fix finite sets

\[
D_2\subset\{d\in G:d\text{ odd},\ d\equiv2\pmod3\},
\]

\[
D_0\subset\{d\in G:d\equiv6\pmod9\}.
\]

Define \(J_0(X)\) to count the \(H_0\) holes through \(X\) for which no
\(d\in D_2\) gives a distinct admissible split
\(n+1=d\,m\).  Define \(J_2(X)\) analogously using \(D_2\cup D_0\).

### Lemma 1 (disjoint fixed-divisor sieve)

For every \(X\),

\[
\boxed{
H_0(X)\le J_0(X)+
\sum_{d\in D_2}O_2\!\left(\left\lfloor{X+1\over d}\right\rfloor\right)
}                                                        \tag{3}
\]

and

\[
\boxed{
\begin{aligned}
H_2(X)\le J_2(X)
&+\sum_{d\in D_2}O_0\!\left(\left\lfloor{X+1\over d}\right\rfloor\right)\\
&+\sum_{d\in D_0}O_2\!\left(\left\lfloor{X+1\over d}\right\rfloor\right).
\end{aligned}}                                             \tag{4}
\]

These remain valid if each nonresidual source is assigned to its first
eligible divisor in any fixed priority order.

#### Proof

For \(n\in H_0\) assigned to \(d\in D_2\), put \(m=(n+1)/d\).
The factors \(d,m\) are distinct and allowed.  Since \(d\in G\) and
\(n\notin G\), closure forces \(m\notin G\).  Also \(m\) is odd and
\(m\equiv2\pmod3\), so it is an \(O_2\) hole.  For fixed \(d\), the map
\(n\mapsto m\) is injective and has the cutoff in (3).

For \(n\in H_2\), a divisor \(d\in D_2\) leaves an odd residue-zero
cofactor, hence an \(O_0\) hole.  If \(d=3e\in D_0\), then
\((n+1)/d=q/e\equiv2\pmod3\), hence the cofactor is an \(O_2\) hole.
The same fixed-\(d\) injection proves (4).  Summing is legitimate because
the priority classes of sources are disjoint; target overlap is only
overcounted. \(\square\)

## 3. Closed two-type criterion

Put

\[
a=\sum_{d\in D_2}{1\over d},\qquad
b=\sum_{d\in D_0}{1\over d}.
\]

### Corollary 2 (spectral residual criterion)

Suppose \(J_0(X)+J_2(X)=o(X)\).  If

\[
a<{1\over3},\qquad
3-10a+3a^2-3b>0,                                           \tag{5}
\]

then

\[
M_0(X)+M_2(X)=o(X).
\]

#### Proof

Let \(\mu_i=\limsup M_i(X)/X\).  Equations (1)--(4), the splitless
estimate, and scaling of limsups give

\[
\binom{\mu_0}{\mu_2}
\le
T(a,b)\binom{\mu_0}{\mu_2},
\qquad
T(a,b)=
\begin{pmatrix}
a/2&1/2\\
5/6+b/2&1/3+a/2
\end{pmatrix}.                                             \tag{6}
\]

Exactly,

\[
\det(I-T)={3-10a+3a^2-3b\over12}.                           \tag{7}
\]

Under (5), both diagonal entries are below 1 and (7) is positive, so the
nonnegative matrix \(T\) has spectral radius below 1.  The only
nonnegative vector satisfying (6) is therefore zero. \(\square\)

This is sharper than the unsplit criterion.  A one-type argument would
require \(a+b<1/3\); the concrete choice below has \(a+b>1/3\), but its
two-type matrix is subcritical.

## 4. Concrete spectral calculation

After deleting multipliers that are inert or divisibility-redundant, take
the initial eligible generated multipliers through \(77\):

\[
D_2=\{5,17,41,53,77\},\qquad D_0=\{33,69\}.                  \tag{8}
\]

They are certified directly by

\[
\begin{gathered}
5=2\cdot3-1,\quad9=2\cdot5-1,\quad17=2\cdot9-1,\\
14=3\cdot5-1,\quad41=3\cdot14-1,\quad
27=2\cdot14-1,\quad53=2\cdot27-1,\\
26=3\cdot9-1,\quad77=3\cdot26-1,\quad
33=2\cdot17-1,\quad69=5\cdot14-1.
\end{gathered}
\]

The exact coefficients are

\[
a={4480997\over14222285},\qquad
b={34\over759},\qquad
a+b={353148583\over981337665}>{1\over3}.                    \tag{9}
\]

The matrix is

\[
T=
\begin{pmatrix}
4480997/28444570&1/2\\
433/506&41887561/85333710
\end{pmatrix},
\]

and

\[
3-10a+3a^2-3b
={59225568637646\over4652287984288175}>0.                  \tag{10}
\]

Thus

\[
\rho(T)=0.999214644481743992\ldots<1.                       \tag{11}
\]

The next nonredundant eligible multiplier is
\(87=2\cdot44-1\), where \(44=5\cdot9-1\).  Adding it to \(D_0\)
changes (10) to

\[
{-2934746493796441\over134916351544357075}<0
\]

and gives \(\rho=1.0013398214751619\ldots\).  Hence (8) is the
subcritical initial-prefix boundary for this two-type system.

## 5. Exact falsifier

The residual-free version of (3) is false at its seventh source:

\[
H_0(252)=7.
\]

The seven holes are

~~~text
54, 114, 144, 174, 186, 234, 252.
~~~

At the five cutoffs supplied by \(D_2\),

~~~text
d=5:  floor(253/5)=50, O2={11,23,29,35,47}
d=17: floor(253/17)=14, O2={11}
d=41: floor(253/41)=6,  O2={}
d=53: floor(253/53)=4,  O2={}
d=77: floor(253/77)=3,  O2={}
~~~

Therefore

\[
\sum_{d\in D_2}O_2(\lfloor253/d\rfloor)=5+1=6<7.            \tag{12}
\]

The extra source is \(252\): both \(11\) and \(23\) are allowed holes, so
\(252\) is reducible, while neither factor of \(253=11\cdot23\) is
generated.  In fact, (12) is unchanged if every generated fixed
multiplier is admitted.  The only eligible generated multipliers small
enough to have nonzero \(O_2(\lfloor253/d\rfloor)\) are \(5\) and \(17\);
the first \(O_2\) hole is \(11\).

The combined residual-free recurrence

\[
H_0(X)+H_2(X)\le
\sum_{d\in D_2}\bigl(O_2(\lfloor(X+1)/d\rfloor)
                     +O_0(\lfloor(X+1)/d\rfloor)\bigr)
+\sum_{d\in D_0}O_2(\lfloor(X+1)/d\rfloor)
\]

survives longer but is also false.  Its first failure is

\[
X=18{,}938,\qquad 1006>1005.                               \tag{13}
\]

## 6. Exhaustive census

The audit reconstructs the least closure by exact ascending divisor
recursion.  It checks each hard event; since a recurrence excess can
increase only when its left side gains a hard hole, this is equivalent to
checking every cutoff for validity and every positive extremizer.

| \(X\) | \(H_0\) | \(H_2\) | \(H\) | \(J_0+J_2\) | row-0 capacity | row-2 capacity |
|---:|---:|---:|---:|---:|---:|---:|
| \(10^2\) | 1 | 1 | 2 | 0 | 1 | 1 |
| \(10^3\) | 34 | 7 | 41 | 8 | 27 | 31 |
| \(10^4\) | 437 | 81 | 518 | 212 | 268 | 299 |
| \(10^5\) | 4,388 | 720 | 5,108 | 3,018 | 2,005 | 2,202 |
| \(10^6\) | 40,135 | 5,448 | 45,583 | 33,762 | 13,013 | 13,875 |
| \(10^7\) | 353,769 | 39,192 | 392,961 | 332,974 | 78,871 | 79,755 |
| \(10^8\) | 3,086,708 | 282,018 | 3,368,726 | 3,065,623 | 486,487 | 462,146 |

The row-0 recurrence has maximum excess \(2{,}600{,}221\) at
\(X=99{,}999{,}972\).  The row-2 recurrence has no failure through
\(10^8\); its largest source-event excess is \(0\), first attained at
\(X=74\).
This finite fact is not an asymptotic estimate.

The combined recurrence has maximum excess \(2{,}420{,}094\) at
\(X=99{,}999{,}972\).  At \(10^8\), the residual proportion is exactly

\[
{3065623\over3368726}=0.910024442475\ldots.                 \tag{14}
\]

The C16 forced family contributes \(278{,}968\) holes \(11p-1\) through
\(10^8\).  Exactly \(278{,}964\) of them lie in the residual for (8);
only \(p\in\{5,17,41,53\}\) is caught.

## 7. Verification and boundary

The independent Python implementation reproduces through \(10^5\)

~~~text
M0=16823, M2=10000, E=11928,
O0=3589, O2=4152, S=2046,
H0=4388, H2=720, residual=3018.
~~~

It also reproduces (12), (13), and the forced-\(11\) counts
\(350\) total and \(346\) residual at that cutoff.

Reproduction from the repository root:

~~~powershell
g++.EXE -O3 -std=c++20 -Wall -Wextra -Wpedantic problems/424/compute/wave3/C25_hard_hole_sieve/hard_hole_sieve.cpp -o problems/424/compute/wave3/C25_hard_hole_sieve/hard_hole_sieve.exe

problems/424/compute/wave3/C25_hard_hole_sieve/hard_hole_sieve.exe 100000000 problems/424/compute/wave3/C25_hard_hole_sieve/result_1e8.json

python problems/424/compute/wave3/C25_hard_hole_sieve/verify_small.py --limit 100000 --output problems/424/compute/wave3/C25_hard_hole_sieve/result_verify.json
~~~

SHA-256:

~~~text
hard_hole_sieve.cpp  E48B194087C27B1795681B50418B06FAF63DBCCDA8A4E7ACBE168FF5CE55B926
verify_small.py      AC6C9C4C024797943E60E16F3231D80AEA54DB13D8880A01EB8F1B8ED62C1CEB
result_1e8.json      58D6AF199E5C5D60B2E229F623C34341B19D9D7FCE03026088F3DA70EFD654E0
result_verify.json   994BD04C938F14D97279F386753C1141163FE43D663E23000376924F5CF16FC2
~~~

The [official problem page](https://www.erdosproblems.com/424) was checked
on 2026-07-13 and still lists #424 as open with no partial solution.
C13 proves the splitless estimate used here; C16 defines the hard class.
No cited source supplies (3)--(7).

The unresolved statement is now precise: prove

\[
J_0(X)+J_2(X)=o(X)
\]

for some subcritical channel system, or replace the fixed-divisor residual
by a new recurrence.  The data in (14) give no such proof, and \(H=o(X)\)
is not claimed.
