# P01: rigorous baseline bounds for Problem 864

Write \([N]=\{1,\ldots,N\}\), and for \(A\subseteq[N]\) put

\[
r_A(s)=\#\{(a,b)\in A^2:a\le b,\ a+b=s\}.
\]

Thus diagonal pairs are counted.  A set is **admissible** if at most one
integer \(s\) has \(r_A(s)\ge2\).  A **Sidon set** below means a set for which
all unordered sums, including diagonals, are distinct.

Let

\[
S(n)=\max\{|C|:C\subseteq[n]\text{ is Sidon}\},\qquad S(0)=0.
\]

The only standard input used here is the classical interval Sidon theorem

\[
S(n)=(1+o(1))\sqrt n. \tag{1}
\]

Its lower half follows, for example, from the classical finite-field Sidon
constructions (choosing a prime power of size \((1-o(1))\sqrt n\)); its upper
half is the classical Erdős--Turán bound.  Everything concerning the exceptional
sum is proved below.

## 1. The Erdős--Freud reflected construction

Fix \(N\ge1\), let

\[
m=\left\lfloor\frac N3\right\rfloor,
\]

take any Sidon set \(B\subseteq[1,m]\), and define

\[
H=N-B=\{N-b:b\in B\},\qquad A=B\cup H. \tag{2}
\]

Here \([1,0]=\varnothing\).  If \(m=0\), then \(B=A=\varnothing\) and all
claims below are immediate, so the sum-band argument may assume \(m\ge1\).

### Placement and overlap

For \(b\in B\),

\[
1\le b\le m,\qquad N-m\le N-b\le N-1.
\]

Hence \(A\subseteq[N]\).  Since \(m\le N/3<N/2\), every element of \(B\) is
strictly smaller than every element of \(H\).  In particular,

\[
B\cap H=\varnothing\quad\text{and}\quad |A|=2|B|. \tag{3}
\]

The three possible types of sums lie in the following *integer* bands:

\[
\begin{array}{ccl}
B+B&\subseteq&[2,2m],\\
B+H&\subseteq&[N-m+1,N+m-1],\\
H+H&\subseteq&[2N-2m,2N-2].
\end{array} \tag{4}
\]

Indeed, a mixed sum is \(x+(N-y)=N+x-y\), where
\(1-m\le x-y\le m-1\).  Since \(3m\le N\),

\[
2m<N-m+1,
\qquad
N+m-1<2N-2m. \tag{5}
\]

Thus the three bands are pairwise disjoint, with strict inequalities for every
residue class of \(N\pmod 3\).  Consequently a collision cannot involve two
different sum types.

### Uniqueness within each band

Sums inside \(B\) are unique by hypothesis.  Sums inside \(H\) are unique as
well, because

\[
(N-x)+(N-y)=(N-u)+(N-v)
\iff x+y=u+v,
\]

and Sidonicity of \(B\) then identifies the two unordered pairs.

It remains to classify mixed sums.  Suppose

\[
x+(N-y)=u+(N-v),\qquad x,y,u,v\in B. \tag{6}
\]

Equation (6) is equivalent to

\[
x+v=u+y. \tag{7}
\]

Both sides of (7) are unordered sums from \(B\), so Sidonicity gives
\(\{x,v\}=\{u,y\}\).  There are only two matchings:

* \(x=u\) and \(v=y\), in which case the two mixed pairs in (6) are identical;
* \(x=y\) and \(v=u\), in which case both mixed sums equal \(N\).

It follows that every mixed sum other than \(N\) has exactly one
representation, while

\[
r_A(N)=|B|,
\quad\text{with representations }\{b,N-b\}\ (b\in B). \tag{8}
\]

These really are distinct unordered pairs: \(b<N-b\) because \(b\le m<N/2\).
There is no additional diagonal representation of \(N\).  If \(N\) is odd this
is immediate; if \(N\) is even, \(N/2\notin A\), since

\[
B\subseteq[1,m]\subset[1,N/2)
\quad\text{and}\quad
H\subseteq(N/2,N-1].
\]

All other diagonal sums occur within \(B+B\) or \(H+H\), where they are already
covered by Sidonicity and by the disjoint bands (4).  Therefore (2) is
admissible.  When \(|B|\ge2\), its unique exceptional sum is \(N\), with
unrestricted multiplicity \(|B|\); when \(|B|=0\) or \(1\), there is no
exceptional sum, which still satisfies the "at most one" condition.

### Asymptotic size

Choose \(B\subseteq[m]\) with \(|B|=S(m)\).  As \(N\to\infty\), (1) and
\(m=N/3+O(1)\) give

\[
|A|=2S(m)
=2(1+o(1))\sqrt m
=\left(\frac2{\sqrt3}+o(1)\right)\sqrt N. \tag{9}
\]

Hence, if \(F(N)\) denotes the largest size of an admissible subset of \([N]\),

\[
F(N)\ge\left(\frac2{\sqrt3}+o(1)\right)\sqrt N. \tag{10}
\]

## 2. A uniform \(\sqrt2\) upper bound

The dependence of the split point on the exceptional sum requires a uniform
version of the upper half of (1).

### Uniform Sidon-error lemma

There is a sequence \(\eta_N\to0\) such that, simultaneously for every integer
\(0\le q\le N\),

\[
S(q)\le\sqrt q+\eta_N\sqrt N. \tag{11}
\]

To prove this directly from (1), define

\[
\eta_N=\max_{0\le q\le N}
\frac{(S(q)-\sqrt q)_+}{\sqrt N}.
\]

Here \(x_+=\max\{x,0\}\).
Given \(\varepsilon>0\), choose \(Q\) so that
\(S(q)\le(1+\varepsilon)\sqrt q\) for all \(q\ge Q\).  For such \(q\le N\),

\[
S(q)-\sqrt q\le\varepsilon\sqrt q\le\varepsilon\sqrt N.
\]

For \(q<Q\), the numerator is bounded by the fixed constant
\(C_Q=\max_{0\le q<Q}(S(q)-\sqrt q)_+\), and
\(C_Q/\sqrt N\to0\).  Thus \(\limsup_N\eta_N\le\varepsilon\); since
\(\varepsilon\) was arbitrary, \(\eta_N\to0\), proving (11).

### Splitting at an actual exception

Let \(A\subseteq[N]\) be admissible and suppose it has an exceptional sum
\(s\).  Necessarily \(2\le s\le2N\).  In fact \(s\ne2,2N\), since the endpoint
sums have only the respective representations \(1+1\) and \(N+N\).  Thus
\(3\le s\le2N-1\), although the estimates below remain valid at formal
endpoints as well.

Put

\[
t=\left\lfloor\frac s2\right\rfloor,
\qquad
A_-=A\cap[1,t],
\qquad
A_+=A\cap[t+1,N]. \tag{12}
\]

We claim that both pieces are genuine Sidon sets.

For \(A_-\), every internal sum is at most \(2t\le s\).  If \(s\) is odd then
\(2t=s-1\), so no internal sum equals the exceptional value.  If \(s\) is even,
say \(s=2t\), the only pair \(x,y\le t\) satisfying \(x+y=s\) is
\(x=y=t\).  Hence at most one unordered pair in \(A_-\) represents \(s\).
Any repeated internal sum would therefore be a repeated global sum different
from \(s\), or would give two internal representations of \(s\); both are
impossible.  Thus \(A_-\) is Sidon, including its possible boundary diagonal
\(t+t=s\).

For \(A_+\), every element is at least \(t+1\), so every internal sum is
strictly larger than \(s\): it is at least \(s+2\) when \(s=2t\), and at least
\(s+1\) when \(s=2t+1\).  A repeated internal sum would again be a second
exceptional value.  Thus \(A_+\) is Sidon.

The first piece lies in an interval of length \(t\).  Translating the second
piece by \(-t\) preserves all sum equalities and puts it in \([1,N-t]\).
Consequently (11) gives, uniformly in \(s\),

\[
\begin{aligned}
|A|
&=|A_-|+|A_+|\\
&\le S(t)+S(N-t)\\
&\le \sqrt t+\sqrt{N-t}+2\eta_N\sqrt N\\
&\le \sqrt{2N}+2\eta_N\sqrt N.
\end{aligned} \tag{13}
\]

The last inequality is Cauchy--Schwarz:
\((\sqrt t+\sqrt{N-t})^2\le2(t+N-t)=2N\).  Since \(\eta_N\to0\),

\[
|A|\le(\sqrt2+o(1))\sqrt N, \tag{14}
\]

where the \(o(1)\) is independent of the location and parity of \(s\).

### No exception and endpoint splits

If no exceptional sum exists, then \(A\) itself is Sidon, so directly

\[
|A|\le S(N)\le(1+\eta_N)\sqrt N,
\]

which is stronger than the uniform bound in (13).  No artificial exceptional
value is needed.
The uniform lemma also covers interval lengths \(0\) and \(N\), because
\(S(0)=0\), although an actual exception always gives \(1\le t\le N-1\).
The endpoint sum values \(s=2\) and \(s=2N\) cannot be exceptional, while the
near-endpoint exceptions \(s=3\) and \(s=2N-1\) give \(t=1\) and \(t=N-1\)
and are already included in (13), with the same error term.

Thus every admissible \(A\), with or without an exception, satisfies
\(|A|\le(\sqrt2+2\eta_N)\sqrt N\).  Taking the maximum over all admissible
sets and using \(\eta_N\to0\) proves

\[
F(N)\le(\sqrt2+o(1))\sqrt N. \tag{15}
\]

## 3. Flaw audit

The two baseline claims are correct, but abbreviated versions conceal two
points that must not be used without repair.

1. Writing \(S(t)=(1+o(1))\sqrt t\) and
   \(S(N-t)=(1+o(1))\sqrt{N-t}\) does **not by itself** give an error uniform in
   the exceptional sum: one of \(t,N-t\) may stay bounded while \(N\to\infty\).
   The uniform lemma (11) closes this genuine quantifier gap.
2. In the reflected construction, the sentence "the exceptional sum is
   \(N\)" has a small-cardinality exception: if \(|B|\le1\), then
   \(r_A(N)=|B|<2\), so there is no exceptional sum.  This has no asymptotic
   effect.  The exact bands (4)--(5), the mixed-sum calculation (6)--(8), and
   the midpoint check show that there is no range, parity, overlap, or diagonal
   flaw in the construction itself.

No further flaw occurs in either bound once these points are made explicit.
