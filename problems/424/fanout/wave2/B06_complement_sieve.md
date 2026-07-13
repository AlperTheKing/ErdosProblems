# B06: complement sieve and fixed-alphabet audit

## Verdict

**NOT SOLVED.** I did not prove positive lower density for the Problem 424
set \(A\). In particular, there are no justified constants \(c>0\) and
\(X_0\) such that

\[
|A\cap[1,X]|\ge cX\qquad(X\ge X_0).
\]

The strongest positive finite result is an exact fixed-alphabet subclosure
with 23 verified multipliers. It has count \(45,233,066\) and maximum gap
\(24\) through \(10^8\). The maximum-gap assertion is finite only.

The strongest falsifier is universal: a nonempty periodic residue set cannot
close a strong induction under any finite family of inverse branches
\((n+1)/d\). Thus an eventual-full-residue-class certificate cannot prove the
desired density, regardless of modulus or the verified multipliers chosen.

## 1. Exact fixed-alphabet reduction

For finite \(D\subset A\), let \(S_D\) be the least set containing \(D\) and
closed under

\[
T_d(q)=dq-1,\qquad d\in D,\quad q\ne d.
\]

Then \(S_D\subset A\). Moreover, ascending membership is exact:

\[
n\in S_D
\iff
n\in D\ \text{or}\quad
\exists d\in D:\ d\mid n+1,\ q=(n+1)/d\in S_D,\ q\ne d. \tag{1}
\]

Every tested parent in (1) is smaller than \(n\), so this is a strong
induction, not a truncated closure heuristic.

The main alphabet was the following 23 values, all in the exact Problem 424
prefix:

\[
\begin{split}
D_{100}=\{&2,3,5,9,14,17,26,27,33,41,44,50,51,53,\\
           &65,69,77,80,81,84,87,98,99\}.
\end{split}
\]

The C++ implementation of (1) gave:

| \(X\) | \(|S_{D_{100}}\cap[1,X]|\) | density | maximum gap |
|---:|---:|---:|---:|
| \(10^3\) | 250 | 0.25000000 | 21 |
| \(10^4\) | 3,207 | 0.32070000 | 21 |
| \(10^5\) | 38,669 | 0.38669000 | 24 |
| \(10^6\) | 424,869 | 0.42486900 | 24 |
| \(10^7\) | 4,439,509 | 0.44395090 | 24 |
| \(10^8\) | 45,233,066 | 0.45233066 | 24 |

The first gap of size 24 is \((89259,89283)\), and no larger gap occurs
through \(10^8\).

At \(X=10^6\), using \(D=A\cap[2,K]\) gave the exact comparison:

| \(K\) | \(|D|\) | count | density | maximum gap |
|---:|---:|---:|---:|---:|
| 5 | 3 | 197,450 | 0.197450 | 459 |
| 20 | 6 | 343,572 | 0.343572 | 44 |
| 100 | 23 | 424,869 | 0.424869 | 24 |
| 1000 | 250 | 457,599 | 0.457599 | 21 |

The \(K=1000\) row equals the full supplied census at \(10^6\). This equality
also follows from (1): the smaller factor in a witness for \(n\le10^6\) is at
most \(\sqrt{n+1}\), and the exact alphabet contains every member of \(A\)
through 1000.

These rows do not imply a lower-density bound. In particular, extending the
observed maximum gap 24 past \(10^8\) would be an unsupported extrapolation.

## 2. Exact residue-state complement condition

Fix a modulus \(M\) divisible by every \(d\in D\). For a residue \(r\) with
\(r\equiv-1\pmod d\), the possible residues of the parent
\(q=(n+1)/d\), as \(n\) ranges over \(r\pmod M\), are exactly

\[
Q_d(r)=
\left\{
\frac{r+1}{d}+j\frac{M}{d}\pmod M:0\le j<d
\right\}. \tag{2}
\]

Thus the natural finite strong-induction certificate asks for a nonempty
\(R\subset\mathbb Z/M\mathbb Z\) such that every \(r\in R\) has some
\(d\in D\) satisfying

\[
r\equiv-1\pmod d,\qquad Q_d(r)\subset R. \tag{3}
\]

Condition (3) retains all \(d\) quotient states. Replacing \(Q_d(r)\) by one
chosen quotient would be an invalid scalar union bound.

The greatest-fixed-point deletion was run with all exact \(A\)-divisors of
each modulus:

| \(M\) | number of multipliers | deletion passes | final core |
|---:|---:|---:|---:|
| 30 | 3 | 5 | 0 |
| 90 | 4 | 7 | 0 |
| 270 | 5 | 8 | 0 |
| 630 | 7 | 7 | 0 |
| 1,890 | 9 | 8 | 0 |
| 5,670 | 11 | 9 | 0 |
| 13,230 | 15 | 9 | 0 |
| 39,690 | 19 | 10 | 0 |

The following theorem explains why enlarging this particular search cannot
succeed.

### Periodic-core falsifier

Let \(D\) be any finite set of integers at least 2. There is no nonempty
periodic \(P\subset\mathbb Z\) such that

\[
P\subset\bigcup_{d\in D}T_d(P). \tag{4}
\]

**Proof.** If \(0\in P\), (4) would give \(0=dx-1\) for integers
\(d\ge2\) and \(x\), which is impossible. Hence \(0\notin P\).
A nonempty periodic set contains negative integers; let \(y\) be its largest
negative member. By (4), \(y=dx-1\) for some \(x\in P\). The cases
\(x\ge1\) and \(x=0\) are impossible, so \(x\le-1\). But then
\(y=dx-1<x<0\), contradicting the maximality of \(y\). \(\square\)

For \(P=\{n:n\bmod M\in R\}\), condition (3) implies (4). Therefore every
finite residue-core search of this form has empty output. This falsifies the
proposed route "prove that selected whole residue classes are eventually in
\(A\)"; it does not falsify a residue-state density inequality that tracks
nonperiodic occupancy inside each class.

## 3. Remaining frontier

The finite result isolates a concrete but unproved statement:

> Every interval of 24 consecutive integers above 89259 meets
> \(S_{D_{100}}\).

That statement would immediately imply positive lower density for \(A\), but
the census verifies it only through \(10^8\). The periodic-core falsifier says
that its proof cannot consist of declaring a nonempty union of complete
residue classes to be eventually present. A valid next lemma must instead
control nonperiodic forbidden gap patterns, or retain quantitative occupancy
vectors and their collision states.

No inequality produced in this lane closes such an induction. Accordingly,
no value of \(c\) or \(X_0\) is claimed.

## 4. Code and reproduction

All B06 code is under problems/424/compute/wave2/B06.

~~~powershell
python problems/424/compute/wave2/B06/census_fixed_alphabet.py --limit 1000000 --cutoffs 5 20 100 1000
python problems/424/compute/wave2/B06/search_periodic_core.py --moduli 30 90 270 630 1890 5670 13230 39690
g++ -O3 -std=c++20 -Wall -Wextra -pedantic problems/424/compute/wave2/B06/census_fixed_alphabet.cpp -o problems/424/compute/wave2/B06/census_fixed_alphabet.exe
problems/424/compute/wave2/B06/census_fixed_alphabet.exe 100000000 100
~~~

search_canonical_matrix.py is a diagnostic collision-routing search. It uses
floating-point power iteration and is not part of any exact theorem or
density claim above.

The attempted \(10^9\) census was interrupted before producing output and is
not used.
