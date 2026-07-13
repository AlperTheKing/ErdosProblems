# P02: interval-sensitive Cayley-sum graph bound

## Verdict

**PROVED LEMMA; PRECISE BARRIER TO \(4/3\).**  The \(K_{2,3}\)-free Cayley
sum graph gives a stronger bound when its right vertex set is the occupied
thickening \(A+X\), rather than the whole ambient interval.  For an interval
\(I_h=\{0,\ldots,h-1\}\), the resulting exact inequality is

\[
 |A|^2h^2
 \le |A+I_h|\left(|A|h+2V_h(A)+2W_h(A,e)\right),                 \tag{1}
\]

where \(V_h\) counts represented short differences once and \(W_h\) counts
exactly the differences having two representations.  The latter has an exact
formula in terms of the *forced* reflected core \(A\cap(e-A)\), including the
midpoint/diagonal case.  No reflection of all of \(A\) is assumed.

For \(\sqrt N\ll h\ll N\), (1) implies

\[
 \frac{|A|^2}{N}
 \le { |A+I_h|\over N}
 \left(1+{2W_h(A,e)\over h^2}\right)+o(1).                    \tag{2}
\]

Thus the graph lane reaches the conjectured constant if one proves the sharp
support--duplicate tradeoff

\[
 { |A+I_h|\over N}
 \left(1+{2W_h(A,e)\over h^2}\right)
 \le {4\over3}+o(1)                                           \tag{3}
\]

for some such \(h\).  The usual bounds on the two factors separately give
only \(2+o(1)\).  Moreover, the reflected-Sidon lower family has the two
factors tending to \(2/3\) and \(2\), respectively, so (3) is sharp and a
standalone improvement of the codegree bound is impossible.

## 1. Exact difference profile, including diagonals

Let \(A\subseteq[1,N]\), \(k=|A|\), and suppose that \(e\) is its unique
repeated unordered sum.  Put

\[
 \rho_A(d)=\#\{(a,b)\in A^2:a-b=d\}\qquad(d>0),
\]

and define

\[
 \Delta=\{d>0:\rho_A(d)>0\},\qquad
 D=\{d>0:\rho_A(d)=2\}.
\]

If there is no repeated sum, put \(D=\varnothing\).  In the exceptional case
define only the forced core

\[
 C=A\cap(e-A),\qquad
 B=\{b\in C:2b<e\},\qquad
 \delta=1_{\{e\text{ even and }e/2\in A\}}.
\]

Writing \(b=|B|\), one has the disjoint decomposition

\[
 C=B\mathbin{\dot\cup}(e-B)
   \mathbin{\dot\cup}\bigl(\{e/2\}\text{ if }\delta=1\bigr),
 \qquad r_A(e)=b+\delta.                                      \tag{4}
\]

### Lemma 1 (forced codegree-two set)

For every \(d>0\),

\[
 \rho_A(d)\le2.                                               \tag{5}
\]

Moreover, the following union is disjoint and is exactly \(D\):

\[
\begin{split}
 D={}&\{y-x:x<y,\ x,y\in B\}\\
 &\mathbin{\dot\cup}\{e-x-y:x<y,\ x,y\in B\}\\
 &\mathbin{\dot\cup}
 \begin{cases}
   \{e/2-x:x\in B\},&\delta=1,\\
   \varnothing,&\delta=0.
 \end{cases}                                                  \tag{6}
\end{split}
\]

Consequently

\[
 |D|=2\binom b2+\delta b=b(b-1+\delta),                       \tag{7}
\]

and

\[
 \binom k2=|\Delta|+|D|.                                     \tag{8}
\]

#### Proof

Suppose \(x-y=u-v=d>0\) are two distinct representations.  Then

\[
 x+v=u+y.
\]

The unordered pairs \(\{x,v\}\) and \(\{u,y\}\) are distinct (otherwise the
two difference representations coincide, since \(d\ne0\)).  Admissibility,
with diagonal pairs included, therefore forces

\[
 x+v=u+y=e.
\]

Hence

\[
 (u,v)=(e-y,e-x).                                             \tag{9}
\]

There cannot be a third representation, proving (5).  Equation (9) also
shows that a positive difference is doubled exactly when it is represented by
two elements of \(C\) whose sum is not \(e\).

The involution

\[
 (x,y)\longmapsto(e-y,e-x)
\]

on ordered positive-difference representations has the following nontrivial
orbits: a lower--lower pair and its upper--upper reflection; two crossed pairs
indexed by distinct \(x,y\in B\); and, when present, a lower--midpoint pair
and its midpoint--upper reflection.  Their differences are precisely the
three lines in (6).  Distinct orbits cannot give the same difference, by (5),
so the union is disjoint.  Counting the orbits proves (7).  Finally every
positive difference has multiplicity one off \(D\) and multiplicity two on
\(D\), which gives (8).  This proof includes the collision
\(x+(e-x)=e/2+e/2\) when \(\delta=1\).  \(\square\)

The set \(U=A\setminus C\) is a genuine Sidon set.  More strongly, every
difference representation involving an element of \(U\) is unique and its
difference lies outside \(D\).  This follows immediately from (9).

## 2. Occupied Cayley-slice inequality

For a finite \(X\subset\mathbb Z\) and \(E\subset\mathbb Z_{>0}\), write

\[
 Q_E(X)=\#\bigl\{\{x,x'\}\in\tbinom X2:|x-x'|\in E\bigr\}.
\]

The bipartite graph below is the slice of the Cayley sum graph
\(\Gamma(\mathbb Z,A)\) with left vertices \(-X\), but using two labelled
parts avoids all loop conventions.

### Lemma 2 (arbitrary shift set; partitioned form)

Let \(A=A_1\mathbin{\dot\cup}\cdots\mathbin{\dot\cup}A_t\) be any partition
into nonempty sets, let \(k_j=|A_j|\), \(k=|A|\), and \(s=|X|\).  Then

\[
 \boxed{
 \sum_{j=1}^t {k_j^2s^2\over |A_j+X|}
 \le ks+2Q_\Delta(X)+2Q_D(X)
 \le ks+s(s-1)+2Q_D(X).}                                    \tag{10}
\]

In particular, with the one-part partition,

\[
 \boxed{
 k^2s^2
 \le |A+X|\left(ks+2Q_\Delta(X)+2Q_D(X)\right)
 \le |A+X|\left(ks+s(s-1)+2Q_D(X)\right).}                  \tag{11}
\]

#### Proof

Form a bipartite graph \(H_X\) with left part \(X\), right part \(A+X\), and

\[
 x\sim y\quad\Longleftrightarrow\quad y-x\in A.
\]

Every left vertex has degree \(k\).  If \(x<x'\), their common neighbours are
in bijection with representations

\[
 a-b=x'-x,\qquad a,b\in A.
\]

Thus their codegree is

\[
 \rho_A(x'-x)=1_\Delta(x'-x)+1_D(x'-x)\le2.                 \tag{12}
\]

This is the exact partial-symmetric/\(K_{2,3}\)-free input.

For \(y\in A+X\), let \(d_j(y)\) count the incident edges labelled by
elements of \(A_j\), and put \(d(y)=\sum_jd_j(y)\).  Double-counting pairs of
left neighbours gives

\[
 \sum_y d(y)^2
 =ks+2Q_\Delta(X)+2Q_D(X).                                  \tag{13}
\]

On the other hand,

\[
 \sum_y d(y)^2
 \ge\sum_j\sum_y d_j(y)^2
 \ge\sum_j{(k_js)^2\over|A_j+X|},                           \tag{14}
\]

by Cauchy--Schwarz.  Equations (13)--(14) prove the first inequality in
(10); \(Q_\Delta(X)\le\binom s2\) proves the second.  Equation (11) is its
one-part specialization.  \(\square\)

## 3. Exact interval form

Take \(I_h=\{0,1,\ldots,h-1\}\) and define

\[
 M_h(S)=|S+I_h|,
\]

\[
 V_h(A)=\sum_{d\in\Delta}(h-d)_+,
 \qquad
 W_h(A,e)=\sum_{d\in D}(h-d)_+,
 \qquad (z)_+=\max(z,0).                                    \tag{15}
\]

Since \(Q_E(I_h)=\sum_{d\in E}(h-d)_+\), (10) becomes

\[
 \boxed{
 \sum_{j=1}^t {|A_j|^2h^2\over M_h(A_j)}
 \le kh+2V_h(A)+2W_h(A,e)
 \le kh+h(h-1)+2W_h(A,e).}                                 \tag{16}
\]

The one-part form is (1).  If \(S=\{s_1<\cdots<s_m\}\ne\varnothing\), its
occupied length is exactly

\[
 M_h(S)=h+\sum_{i=1}^{m-1}\min\{h,s_{i+1}-s_i\}.             \tag{17}
\]

Thus (16) retains the actual interval gaps rather than replacing the right
part by \(N+h-1\).

By (6), the duplicate term itself has the exact interval-sensitive formula

\[
\begin{split}
 W_h(A,e)={}&\sum_{x<y\atop x,y\in B}
 \left((h-y+x)_+ +(h-e+x+y)_+\right)\\
 &\quad+\delta\sum_{x\in B}(h-e/2+x)_+.                     \tag{18}
\end{split}
\]

No term in (18) comes from an assumed reflection of \(A\): only members of
the forced core \(C=A\cap(e-A)\) occur.

For the canonical partition \(A=C\mathbin{\dot\cup}U\), (16) gives the
additional rigorous inequality

\[
 { |C|^2h^2\over M_h(C)}+{ |U|^2h^2\over M_h(U)}
 \le kh+h(h-1)+2W_h(A,e),                                   \tag{19}
\]

with an empty term omitted.  This prevents an unpaired Sidon residual from
being hidden inside the degree average when its thickening is spatially
separate from the core.

## 4. Unconditional consequences

The elementary bounds

\[
 M_h(A)\le N+h-1,\qquad
 V_h(A)\le\binom h2,\qquad
 W_h(A,e)\le\binom h2,\qquad
 W_h(A,e)\le h|D|                                            \tag{20}
\]

and (1), first with \(h=\lfloor N^{3/4}\rfloor\), imply

\[
 k=O(\sqrt N).
\]

Taking any \(\sqrt N\ll h\ll N\) then recovers

\[
 k^2\le(2+o(1))N.                                            \tag{21}
\]

This is the generic \(K_{2,3}\) constant and matches the known
\((\sqrt2+o(1))\sqrt N\) upper bound.

There is a genuine improvement when the exceptional fibre is small.  If

\[
 r_A(e)=o(\sqrt N),                                          \tag{22}
\]

then (7) gives \(|D|=o(N)\).  Choose

\[
 \max\{\sqrt N,|D|\}\ll h\ll N.
\]

Now \(W_h\le h|D|=o(h^2)\), and (1), (20) yield the proved conditional
asymptotic

\[
 \boxed{|A|^2\le(1+o(1))N.}                                 \tag{23}
\]

Hence every family with \(|A|\ge(1+\varepsilon)\sqrt N\) must have
\(r_A(e)=\Omega_\varepsilon(\sqrt N)\).  The unrestricted exceptional
multiplicity is therefore the only asymptotic regime in which the \(4/3\)
problem remains.

More precisely, for every mesoscopic \(h\), (1) gives the exact and coarse
profiles

\[
 {k^2\over N}
 \le {M_h(A)\over N}
 \left({2V_h(A)+2W_h(A,e)\over h^2}
       +o(1)\right)                                         \tag{24}
\]

and

\[
 {k^2\over N}
 \le {M_h(A)\over N}
 \left(1+{2W_h(A,e)\over h^2}+o(1)\right).                  \tag{25}
\]

Equation (3) is therefore a sufficient sharp frontier lemma.

## 5. Sharpness and the precise barrier

Let \(B_L\subseteq[1,L]\) be genuine Sidon sets with

\[
 |B_L|=(1+o(1))\sqrt L,
\]

and set

\[
 A_L=B_L\cup(3L+1-B_L)\subseteq[1,3L].                      \tag{26}
\]

This is used only as a sharpness family, not as an assumption on general
admissible sets.  Its three sum ranges are disjoint, and all noncentral cross
sums are unique differences of \(B_L\).  Thus its only repeated unordered
sum is \(e=3L+1\), with \(|B_L|\) representations; diagonals create no second
exception.

For \(h<L\), (6) shows that the second family of duplicate differences is at
least \(L+1\).  Hence

\[
 W_h(A_L,e)=\sum_{x<y\atop x,y\in B_L}(h-y+x)_+.             \tag{27}
\]

The dense-Sidon interval equidistribution theorem implies that the normalized
counting measures of \(B_L\) converge to Lebesgue measure on \([0,1]\).  For
fixed \(0<c<1\) and \(h=\lfloor cL\rfloor\), (27) therefore gives

\[
 {W_h(A_L,e)\over L^2}
 \longrightarrow
 \int_0^c(c-t)(1-t)\,dt
 ={c^2\over2}-{c^3\over6}.                                  \tag{28}
\]

Letting \(c=c_L\downarrow0\) sufficiently slowly, while
\(\sqrt L\ll h=c_LL\ll L\), gives

\[
 {W_h(A_L,e)\over h^2}\longrightarrow{1\over2}.             \tag{29}
\]

Also \(M_h(A_L)\le2(L+h)=2L+o(L)\).  Since
\(|A_L|^2=(4+o(1))L\), inequality (1) and (29) force the reverse asymptotic
bound, so

\[
 {M_h(A_L)\over3L}\longrightarrow{2\over3}.                 \tag{30}
\]

Consequently the two factors in (3) satisfy

\[
 {M_h(A_L)\over N}\longrightarrow{2\over3},
 \qquad
 1+{2W_h(A_L,e)\over h^2}\longrightarrow2,                 \tag{31}
\]

and their product tends exactly to \(4/3\).

This also gives an asymptotic falsifier to any proposed standalone estimate
\(W_h\le(1/6+o(1))h^2\).  A small exact guardrail is

\[
 A=\{1,2,5,6\},\quad e=7,\quad D=\{1,4\},\quad
 W_3=2>{3^2\over6};                                         \tag{32}
\]

the complete unordered sum list has only \(1+6=2+5=7\) repeated, including
all four diagonal sums in the check.

The remaining obstruction is now precise: one must couple a large duplicated
short-difference profile to a small occupied thickening (or, using (19), show
that any unpaired residual has negligible \(\sqrt N\)-scale size).  Bare
\(K_{2,3}\)-freeness supplies only \(W_h\le\binom h2\) and
\(M_h\le N+h-1\), whose product in (25) is \(2+o(1)\).  The reflected lower
family shows that the first inequality can be asymptotically tight, so no
improvement of the local codegree count alone can reach \(4/3\).  What is
missing is exactly the nonlocal interval statement (3), not a stronger
Kovari--Sos--Turan estimate.

## References used for the graph encoding and sharpness audit

1. A. Forey, J. Fresan, E. Kowalski, and Y. Wigderson,
   *Spectrally indistinguishable pseudorandom graphs*, arXiv:2511.21351,
   Proposition 3.1 (partial symmetric Sidon sets give \(K_{2,3}\)-free Cayley
   sum graphs).
2. J. Cilleruelo, *Gaps in Dense Sidon Sets*, Integers 0 (2000), A11,
   Theorem 1.1 (interval equidistribution in the dense regime used in (28)).
