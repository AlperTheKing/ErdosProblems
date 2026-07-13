# C09: fixed-subsystem threshold for hyperbola pair supply

## Verdict

There is a rigorous bridge, but the fixed affine subsystem does not currently
cross it.

Let `B` be the least set containing `2,3,5` and closed under the licensed maps

\[
T_k(x)=kx-1,\qquad k\in\{2,3,5\},\qquad x\ne k.
\]

The following statements are proved below.

1. If two subsets of the two modulo-3 channels have pointwise counting bounds
   \(\gg X/(\log X)^{\alpha_i}\), then their hyperbola pair count is
   \(\gg X(\log X)^{1-\alpha_0-\alpha_2}\). Thus
   \(\alpha_0+\alpha_2\le 1\) is sufficient. No additional dyadic-shell
   hypothesis is needed when the counting bounds hold for every large cutoff.
2. A shell-uniform version gives the same threshold from explicit lower bounds
   on every dyadic shell.
3. A single bound \(B(X)\gg X/(\log X)^\alpha\), with
   \(\alpha\le 1/2\), transfers injectively to explicit subsets of both
   residue channels and hence gives \(\Omega(X)\) hyperbola pairs.
4. The exact Boolean recurrence would give the required
   \(X/\sqrt{\log X}\) bound from one floor-exact immediate-parent collision
   estimate stated in Proposition 3.1.
5. The currently applicable Shamazov--Talambutsa theorem gives a superlinear
   **orbit multiset**, not a near-linear orbit set. Converting it to the needed
   set bound requires the orbit-value second-moment estimate (M) below.
   Their free critical-orbit theorem and exact-cover theorem cannot supply the
   threshold for any block family from this alphabet.
6. An exact finite scan finds that (R) fails at 32 integer cutoffs, first at
   24 and last at 64. It passes at every integer through \(10^8\) thereafter
   and on both sides of all \(725{,}940{,}178\) collision-tax events from 24
   through \(10^{11}\). This finite statement does not prove (R) eventually.

This is a conditional pair-supply result, not a proof that the represented
products have positive density. Multiplicative product collisions remain a
separate energy problem.

## 1. Explicit channel reservoirs

Write

\[
C(X)=|B\cap[1,X]|.
\]

The reduction proved in B02 is

\[
B=\{2,3,5\}\cup\{T_w(9):w\in\{2,3,5\}^*\}
 \cup\{T_w(14):w\in\{2,3,5\}^*\}.                 \tag{1}
\]

In particular, \(B\subseteq G\). Define the explicit images

\[
\mathcal B_2=T_3(B\setminus\{3\}),\qquad
\mathcal B_0=T_2T_3(B\setminus\{3\}).              \tag{2}
\]

The first map in (2) is licensed because only the input 3 is removed. Its
output is at least 5, so the following \(T_2\) is also licensed. The maps are
injective, and

\[
T_3(x)=3x-1\equiv2\pmod3,\qquad
T_2T_3(x)=6x-3\equiv0\pmod3.
\]

Consequently

\[
\mathcal B_2\subseteq G_2,\qquad \mathcal B_0\subseteq G_0,              \tag{3}
\]

and, exactly,

\[
\begin{aligned}
|\mathcal B_2\cap[1,X]|
 &=C\!\left(\left\lfloor{X+1\over3}\right\rfloor\right)
   -1_{\{X\ge8\}},\\
|\mathcal B_0\cap[1,X]|
 &=C\!\left(\left\lfloor{X+3\over6}\right\rfloor\right)
   -1_{\{X\ge15\}}.
\end{aligned}                                                        \tag{4}
\]

The subtracted point is the forbidden input 3. Hence every pointwise lower
bound

\[
C(X)\gg {X\over(\log X)^\alpha}                                      \tag{5}
\]

transfers, with the same exponent and uniformity in \(X\), to both explicit
channel reservoirs in (2).

## 2. Hyperbola pair-supply lemma

For sets \(U,V\subseteq\mathbb N\), put

\[
U(t)=|U\cap[1,t]|,\quad V(t)=|V\cap[1,t]|,
\quad
P_{U,V}(X)=\#\{(u,v)\in U\times V:uv\le X\}.           \tag{6}
\]

### Lemma 2.1 (pointwise cumulative form)

Let \(0\le\alpha_U,\alpha_V<1\). Suppose that, for every real
\(t\ge t_0>1\),

\[
U(t)\ge c_U{t\over(\log t)^{\alpha_U}},\qquad
V(t)\ge c_V{t\over(\log t)^{\alpha_V}}.                \tag{7}
\]

Then, for \(X\ge t_0^2\),

\[
\boxed{
P_{U,V}(X)\ge
{c_Uc_V X\over(1-\alpha_V)(\log X)^{\alpha_U}}
\left[
 \left({\log X\over2}\right)^{1-\alpha_V}
 -(\log t_0)^{1-\alpha_V}
\right].}                                               \tag{8}
\]

In particular,

\[
P_{U,V}(X)\gg
X(\log X)^{1-\alpha_U-\alpha_V}.                        \tag{9}
\]

Thus \(\alpha_U+\alpha_V\le1\) implies
\(P_{U,V}(X)=\Omega(X)\).

#### Proof

Restrict the second factor to \(v\le\sqrt X\). Then
\(X/v\ge\sqrt X\ge t_0\), so (7) gives

\[
\begin{aligned}
P_{U,V}(X)
&=\sum_{\substack{v\in V\\v\le X}}U(X/v)\\
&\ge {c_UX\over(\log X)^{\alpha_U}}
       \sum_{\substack{v\in V\\v\le\sqrt X}}{1\over v}.             \tag{10}
\end{aligned}
\]

Partial summation gives, for \(T\ge t_0\),

\[
\sum_{\substack{v\in V\\v\le T}}{1\over v}
= {V(T)\over T}+\int_1^T{V(t)\over t^2}\,dt
\ge c_V\int_{t_0}^T{dt\over t(\log t)^{\alpha_V}}.     \tag{11}
\]

Taking \(T=\sqrt X\) evaluates the last integral and proves (8). \(\square\)

The pointwise hypothesis in (7) already forces enough harmonic mass in every
long logarithmic range. It does **not** imply a lower bound in each individual
dyadic shell, but such a shell bound is unnecessary for (8).

### Lemma 2.2 (dyadic-shell form)

Suppose instead that, for every integer \(j\ge j_0\),

\[
\begin{aligned}
|U\cap[2^j,2^{j+1})|&\ge d_U{2^j\over(j+1)^{\alpha_U}},\\
|V\cap[2^j,2^{j+1})|&\ge d_V{2^j\over(j+1)^{\alpha_V}}.
\end{aligned}                                                        \tag{12}
\]

Let \(s=\alpha_U+\alpha_V\), \(N=\lfloor\log_2X\rfloor\), and assume
\(N\ge\max(12,3j_0)\). Then

\[
P_{U,V}(X)\ge
{d_Ud_V\over96}\,{XN\over(N+1)^s}.                     \tag{13}
\]

In particular, if \(s\le1\), then

\[
P_{U,V}(X)\ge {d_Ud_V\over192}X.                        \tag{14}
\]

#### Proof

For every integer

\[
\left\lceil{N\over3}\right\rceil
\le j\le
\left\lfloor{N\over2}\right\rfloor,
\qquad k=N-2-j,                                          \tag{15}
\]

both \(j,k\ge j_0\). A pair from the corresponding shells has product
strictly below \(2^{j+k+2}=2^N\le X\). There are at least \(N/12\) choices
of \(j\), while \(j+1,k+1\le N+1\). Summing their disjoint pair sets and
using \(2^{N-2}>X/8\) proves (13). If \(s\le1\), then
\(N/(N+1)^s\ge N/(N+1)\ge1/2\), proving (14). \(\square\)

### Corollary 2.3 (the requested threshold)

If (5) holds with \(\alpha\le1/2\), then (4) and Lemma 2.1 give

\[
P_{\mathcal B_0,\mathcal B_2}(X)
\gg X(\log X)^{1-2\alpha}=\Omega(X).                    \tag{16}
\]

The two factors are automatically distinct because they lie in different
residue classes. Every pair therefore gives a licensed element
\(uv-1\in G_2\).

Equation (16) counts pairs, not distinct products. To infer
\(\Omega(X)\) distinct products one still needs, in the notation of C00,

\[
E_\times(X)\ll {P_{\mathcal B_0,\mathcal B_2}(X)^2\over X}.             \tag{17}
\]

Nothing in Lemmas 2.1 or 2.2 supplies (17).

## 3. What the exact Boolean recurrence would need

Let \(b_n=1_{\{n\in B\}}\). For \(n\ge6\), membership is given exactly by

\[
b_n=\bigvee_{\substack{k\in\{2,3,5\}\\k\mid n+1\\(n+1)/k\ne k}}
b_{(n+1)/k}.                                               \tag{B}
\]

For \(X\ge24\), let

\[
F(X)=C(X)-{1\over2},\qquad
M_k(X)=\left\lfloor{X+1\over k}\right\rfloor.
\]

Summing the three image sets by inclusion-exclusion gives the exact recurrence

\[
F(X)+\Delta(X)=F(M_2)+F(M_3)+F(M_5),                    \tag{18}
\]

where

\[
\begin{aligned}
P_{23}(X)&=\#\{t\le (X+1)/6:2t,3t\in B\},\\
P_{25}(X)&=\#\{t\le (X+1)/10:2t,5t\in B\},\\
P_{35}(X)&=\#\{t\le (X+1)/15:3t,5t\in B\},\\
P_{235}(X)&=\#\{t\le (X+1)/30:6t,10t,15t\in B\},\\
\Delta(X)&=P_{23}(X)+P_{25}(X)+P_{35}(X)-P_{235}(X).
\end{aligned}                                                        \tag{19}
\]

is the immediate-parent collision tax.

For \(\alpha\ge0\), define

\[
w_\alpha(Y)={Y+1\over(\log(Y+1))^\alpha}                \tag{20}
\]

and the floor-exact allowable collision coefficient

\[
\tau_\alpha(X)=
{w_\alpha(M_2)+w_\alpha(M_3)+w_\alpha(M_5)
 \over w_\alpha(X)}-1.                                  \tag{21}
\]

Since \(M_k+1\ge(X+1)/k\) and
\(\log(M_k+1)\le\log(X+1)\),

\[
\tau_\alpha(X)\ge {1\over2}+{1\over3}+{1\over5}-1
={1\over30}.                                             \tag{22}
\]

### Proposition 3.1 (exact log-barrier criterion)

Fix \(\alpha\ge0\) and an integer \(X_0\ge24\). If

\[
\boxed{\Delta(X)\le\tau_\alpha(X)F(X)\qquad(X\ge X_0)}                \tag{R_alpha}
\]

for every integer \(X\), then there is \(c>0\) such that

\[
F(X)\ge c\,w_\alpha(X)\qquad(X\ge5).                   \tag{23}
\]

#### Proof

Choose \(c>0\) no larger than

\[
\min_{5\le Y<X_0}{F(Y)\over w_\alpha(Y)}.
\]

This minimum is positive. Assume (23) for every smaller argument needed at
some \(X\ge X_0\). From (18), the induction hypothesis, and
\((R_\alpha)\),

\[
\begin{aligned}
(1+\tau_\alpha(X))F(X)
&\ge F(X)+\Delta(X)\\
&=\sum_{k\in\{2,3,5\}}F(M_k)\\
&\ge c\sum_{k\in\{2,3,5\}}w_\alpha(M_k)\\
&=c(1+\tau_\alpha(X))w_\alpha(X).
\end{aligned}
\]

Cancel the positive coefficient and use strong induction. \(\square\)

For fixed \(\alpha\), expansion of the exact coefficient (21) gives

\[
\tau_\alpha(X)
={1\over30}+{\alpha\mu\over\log(X+1)}
+O_\alpha\!\left({1\over(\log X)^2}\right),             \tag{24}
\]

where

\[
\mu={\log2\over2}+{\log3\over3}+{\log5\over5}
=1.034665268989496\ldots.                                \tag{25}
\]

Thus the exact additional estimate needed by this barrier at the requested
endpoint is

\[
\boxed{\Delta(X)\le\tau_{1/2}(X)F(X).}                  \tag{R}
\]

Asymptotically, (R) permits

\[
{\Delta(X)\over F(X)}
\le {1\over30}+{0.517332634494748\ldots\over\log(X+1)}
+O\!\left({1\over(\log X)^2}\right).                    \tag{26}
\]

The floor-exact formulation (R), not the asymptotic display (26), is the
actual sufficient hypothesis. Among one-step inductions that use only (18)
and the parent barriers \(F(M_k)\ge c w_\alpha(M_k)\), the coefficient in
(21) is maximal: replacing it by a larger allowed collision coefficient no
longer reproduces the same barrier.

No known estimate in the supplied work bounds the correlations in (19) by
(R). The Boolean recurrence is exact, but exactness alone gives no upper
bound on its OR-collisions. Proposition 3.1 therefore isolates an additional
theorem; it does not prove its hypothesis.

### 3.1 Exact finite test of (R)

Define the signed normalized gap

\[
V(X)={\Delta(X)\over F(X)}-\tau_{1/2}(X).                \tag{T}
\]

Thus (R) holds at a cutoff exactly when \(V(X)\le0\). The fixed-subsystem
membership array was regenerated through

\[
L=100{,}000{,}000{,}000
\]

from the Boolean recurrence (B), using \(100{,}000{,}000{,}001\) membership
bytes and 64 workers. The endpoint totals independently reproduced B02:

\[
C(L)=18{,}222{,}202{,}754,\qquad
\Delta(L)=726{,}373{,}017.                               \tag{T1}
\]

The scan had three parts.

1. Every integer cutoff \(24\le X\le10^8\) was tested.
2. A **collision-tax event** is an \(n\in B\) whose immediate-parent
   multiplicity \(m(n)\) is at least 2, so that
   \(\max(m(n)-1,0)>0\). For every such event through \(L\), both \(n-1\)
   and \(n\) were tested. There are \(725{,}940{,}181\) events through \(L\);
   three precede 24, leaving \(725{,}940{,}178\) tested events.
3. Every decimal and power-of-two checkpoint through \(L\) was tested.

All membership, prefix-count, and collision-tax quantities in this scan are
integers. Event comparisons used 80-bit long-double arithmetic; every
reported extremum was reevaluated with 100 decimal digits and independently
recomputed with a second multiple-precision implementation. The smallest
reported absolute event margin is greater than \(0.0145\).

#### Integer failures

Among all \(99{,}999{,}977\) integer cutoffs from 24 through \(10^8\), exactly
32 fail. The first failure, largest violation, last failure, and next cutoff
are:

| cutoff | \(C\) | \(\Delta\) | \(\Delta/F\) | \(\tau_{1/2}\) | \(V\) |
|---:|---:|---:|---:|---:|---:|
| 24 | 6 | 3 | 0.545454545455 | 0.339936507924 | +0.205518037531 |
| 25 | 6 | 3 | 0.545454545455 | 0.330992528297 | **+0.214462017157** |
| 64 | 14 | 3 | 0.222222222222 | 0.218940072606 | +0.003282149616 |
| 65 | 15 | 3 | 0.206896551724 | 0.231611673083 | -0.024715121359 |

Thus the first failed integer cutoff is 24, the last is 64, and the maximum
normalized violation is

\[
V(25)=0.2144620171571010711\ldots.                       \tag{T2}
\]

In unnormalized form, the maximum is

\[
\Delta(25)-\tau_{1/2}(25)F(25)
=1.1795410943640558911\ldots.                            \tag{T3}
\]

No integer failure occurs in the exhaustively tested range
\(65\le X\le10^8\).

#### Collision-event cutoffs

None of the \(725{,}940{,}178\) post-event cutoffs, and none of their
pre-event cutoffs, fails (R). Hence there is no first or last event failure.
The closest approaches to failure are:

| side | cutoff | \(C\) | \(\Delta\) | \(\Delta/F\) | \(\tau_{1/2}\) | \(V\) |
|---|---:|---:|---:|---:|---:|---:|
| after | 97,915,211,825 | 17,861,004,357 | 712,499,539 | 0.039891347921 | 0.054484030706 | **-0.014592682785** |
| before | 97,915,211,248 | 17,861,004,228 | 712,499,533 | 0.039891347873 | 0.054484030693 | -0.014592682820 |
| endpoint | 100,000,000,000 | 18,222,202,754 | 726,373,017 | 0.039861976449 | 0.054465823039 | -0.014603846590 |

The maximum signed event gap is therefore negative. At the closest
post-event cutoff, the unnormalized slack is

\[
\Delta-\tau_{1/2}F
=-260{,}639{,}970.8043367365\ldots.                      \tag{T4}
\]

#### Logarithmic trend

For comparison with the coefficient in (26), put

\[
A(X)=\left({\Delta(X)\over F(X)}-{1\over30}\right)\log(X+1),
\qquad
T(X)=\left(\tau_{1/2}(X)-{1\over30}\right)\log(X+1).
\]

The decimal-checkpoint evaluations below use exact integer inputs; displayed
transcendental values are rounded:

| \(X\) | \(\Delta/F\) | \(\tau_{1/2}\) | \(V\) | \(A(X)\) | \(T(X)\) |
|---:|---:|---:|---:|---:|---:|
| \(10^6\) | 0.041007953933 | 0.073248007678 | -0.032240053746 | 0.106028809591 | 0.551441644747 |
| \(10^7\) | 0.040965561535 | 0.067221355094 | -0.026255793558 | 0.123016984954 | 0.546210379545 |
| \(10^8\) | 0.040753569791 | 0.062777392232 | -0.022023822442 | 0.136685806897 | 0.542379609078 |
| \(10^9\) | 0.040526280705 | 0.059364346377 | -0.018838065672 | 0.149061360540 | 0.539447603331 |
| \(10^{10}\) | 0.040217274611 | 0.056660611599 | -0.016443336988 | 0.158508605667 | 0.537130431953 |
| \(10^{11}\) | 0.039861976449 | 0.054465823039 | -0.014603846590 | 0.165360319459 | 0.535252913508 |

At these six decimal cutoffs the signed margin narrows, \(A(X)\) rises, and
\(T(X)\) falls. The event scan is not monotone: its closest cutoff occurs
before \(10^{11}\), and the endpoint is slightly farther from failure.
These are finite trends only.

The coverage limitation is load-bearing. Every integer was tested only
through \(10^8\). Above \(10^8\), the scan tested logarithmic cutoffs and the
two sides of every collision-tax jump, not every intervening integer. It
therefore neither proves (R) for all \(X\ge65\) nor justifies extrapolating
(T1)--(T4) beyond \(10^{11}\).

## 4. Shamazov--Talambutsa audit

Conjugate by \(u=x-1\). The three maps become

\[
g_k(u)=ku+(k-2),\qquad k\in\{2,3,5\},                    \tag{27}
\]

and the two safe roots in (1) become \(8,13\). These maps have slopes greater
than one and nonnegative integer intercepts, and the starting set is finite,
positive, and discrete. Thus the multiset theorem in
[Shamazov--Talambutsa, Theorem 2](https://arxiv.org/html/2507.06875v2)
applies.

Let \(r(n)\) be the number of pairs \((a,w)\), with
\(a\in\{9,14\}\) and \(w\in\{2,3,5\}^*\), for which \(T_w(a)=n\). Put

\[
R(X)=\sum_{n\le X}r(n),\qquad
E_{\rm orb}(X)=\sum_{n\le X}r(n)^2.                      \tag{28}
\]

If \(\sigma\) is defined by

\[
2^{-\sigma}+3^{-\sigma}+5^{-\sigma}=1,
\qquad
\sigma=1.032812265771883\ldots,                          \tag{29}
\]

then Theorem 2 rigorously gives

\[
R(X)=\Omega(X^\sigma).                                  \tag{30}
\]

It gives (30) for the multiset, with every word representation counted. It
does not give the same bound for the support. Cauchy--Schwarz gives only

\[
|\{n\le X:r(n)>0\}|\ge {R(X)^2\over E_{\rm orb}(X)}.     \tag{31}
\]

Consequently, the single orbit-value collision estimate

\[
\boxed{
E_{\rm orb}(X)\ll
X^{2\sigma-1}(\log X)^{1/2}}
                                                                    \tag{M}
\]

would imply

\[
|\{n\le X:r(n)>0\}|\gg {X\over\sqrt{\log X}}.           \tag{32}
\]

Applying the fixed injective suffixes \(T_3\) and \(T_2T_3\) then gives
the same lower bound in the two explicit channels, and Lemma 2.1 gives
\(\Omega(X)\) hyperbola pairs.

More generally, channel estimates

\[
E_i(X)\ll X^{2\sigma-1}(\log X)^{\beta_i},
\qquad \beta_0+\beta_2\le1,                              \tag{33}
\]

for representation languages supplying the two channels are sufficient.
The symmetric aggregate estimate (M) is a cleaner single target. It is weaker
than the \(E_{\rm orb}(X)=O(X^{2\sigma-1})\) estimate that would prove
positive density for the affine orbit itself.

### 4.1 The free critical-orbit theorem cannot reach the threshold

[Theorem 5 of the same paper](https://arxiv.org/html/2507.06875v2) assumes
that \(m\) affine generators freely generate a semigroup and satisfy

\[
\sum_{j=1}^m{1\over a_j}=1.                              \tag{34}
\]

Its set conclusion is

\[
\Omega\!\left({X\over(\log X)^{(m-1)/2}}\right).         \tag{35}
\]

The elementary family fails both load-bearing hypotheses: its reciprocal
sum is \(31/30\), and it is not free. In application order,

\[
T_{255232}=T_{322255}=600x-381.                           \tag{36}
\]

Passing to a block subfamily cannot make Theorem 5 reach
\(\alpha\le1/2\). Indeed, (35) has exponent at most \(1/2\) only if
\(m\le2\). For \(m=1\), (34) would require slope 1. For \(m=2\), integer
slopes \(a,b\ge2\) and

\[
{1\over a}+{1\over b}=1
\]

force \((a-1)(b-1)=1\), hence \(a=b=2\). A nonempty word over
\(\{2,3,5\}\) has slope equal to the product of its letters, so the only
word of slope 2 is the one-letter word `2`. There are not two distinct
slope-2 block maps, let alone two free generators. Therefore no direct block
application of Theorem 5 can supply the requested exponent.

### 4.2 The exact-cover theorem cannot apply to block maps

[Theorem 7 of the same paper](https://arxiv.org/html/2507.06875v2) assumes
an exact covering system

\[
h_1(\mathbb Z)\sqcup\cdots\sqcup h_m(\mathbb Z)=\mathbb Z.             \tag{37}
\]

For every nonempty word \(w\), let \(k\in\{2,3,5\}\) be its outermost
letter. Then

\[
T_w(\mathbb Z)\subseteq T_k(\mathbb Z)=k\mathbb Z-1.    \tag{38}
\]

In particular, \(0\) belongs to no image in (38), because no one of
\(2,3,5\) divides \(0+1\). Thus no family of nonempty block compositions
from this alphabet can even cover \(\mathbb Z\), before disjointness is
considered. Affine conjugation preserves this obstruction. Theorem 7 is
therefore unavailable for every such block family.

A theorem on an invariant periodic subdomain would be a genuine extension,
not an application of Theorem 7. The bounded searches in B05 found no such
certificate and did not prove that none exists.

## 5. Collision audit

There are four different collision questions, and they cannot be substituted
for one another.

1. **Map relations.** Equation (36) violates the freeness hypothesis of
   Theorem 5. Removing one word from each known map relation does not control
   all orbit-value collisions.
2. **Same-root orbit-value collisions.** Distinct affine maps already agree
   at the root 9:
   \[
   T_{35}(9)=(15x-6)|_{x=9}=129
   = (16x-15)|_{x=9}=T_{2222}(9).                         \tag{39}
   \]
   Thus map deduplication is insufficient for (M).
3. **Cross-root orbit-value collisions.** They also occur between the two
   safe roots:
   \[
   T_{253}(14)=(30x-19)|_{x=14}=401
   =(48x-31)|_{x=9}=T_{32222}(9).                         \tag{40}
   \]
   Estimate (M) must count both same-root and cross-root solutions of
   \(P_wa-C_w=P_vb-C_v\).
4. **Hyperbola product collisions.** Even after (R) or (M) gives linear pair
   supply, different pairs may have the same product. This is controlled by
   (17), not by \(\Delta\) or \(E_{\rm orb}\).

The identities (36), (39), and (40) are exact integer equalities. They show
why neither raw words nor distinct affine maps can be counted as distinct
orbit values.

## 6. Final status

The bridge requested in this lane is proved: the sufficient log-power
threshold furnished by this hyperbola pair-supply argument is

\[
\alpha_0+\alpha_2\le1,
\]

and the symmetric threshold is \(\alpha\le1/2\). The explicit fixed-subsystem
reservoirs are (2).

What is not proved is that the fixed subsystem reaches the threshold. There
are two precise sufficient frontier estimates:

\[
\Delta(X)\le\tau_{1/2}(X)F(X) \quad\text{for all large }X               \tag{R}
\]

for the exact Boolean recurrence, or

\[
E_{\rm orb}(X)\ll X^{2\sigma-1}\sqrt{\log X}                           \tag{M}
\]

for the Shamazov--Talambutsa multiset route. Neither estimate follows from a
currently cited theorem. Theorem 5 cannot attain the threshold for any block
family over this alphabet, and Theorem 7 cannot apply because all nonempty
block images omit an integer.

The finite scan is consistent with taking \(X_0=65\) in (R) on every tested
cutoff, but it does not prove the universal hypothesis. No asymptotic
inference is made from the census through \(10^{11}\).

## References and checks

- [B02 affine-subsystem red team](../wave2/B02_affine_subsystem_redteam.md)
- [B04 collision-exact affine renewal](../wave2/B04_affine_renewal.md)
- [B05 exact-cover compositions](../wave2/B05_exact_cover_compositions.md)
- [C00 hyperbola census](C00_hyperbola_census.md)
- K. F. Shamazov and A. L. Talambutsa,
  ["On orbit sets generated by semigroups of one-dimensional affine
  functions"](https://arxiv.org/abs/2507.06875), arXiv:2507.06875v2;
  *Expositiones Mathematicae* 44(3) (2026), 125765,
  [DOI 10.1016/j.exmath.2026.125765](https://doi.org/10.1016/j.exmath.2026.125765).

Focused exact checks run for this note:

```powershell
cd problems\424\compute\wave2\B02
python -m unittest -v test_affine_census.py

cd ..\B04
python -m unittest -v test_affine_relations.py
```

All 4 B02 tests and all 6 B04 tests passed. An independent integer replay
verified (18) for every \(24\le X\le5000\), verified both injections in (2)
through 5000, and reproduced (29) and (25). These finite checks verify the
formulas tested; they are not asymptotic evidence for (R), (M), or (17).

The \(10^{11}\) condition scan used the temporary sources
<code>C:\tmp\c09_condition_scan.cpp</code> and
<code>C:\tmp\c09_condition_scan.exe</code>,
with SHA-256 values
BF84AAA6C14FC9FAB280AEEAAC258B534F80BC6DE5F5BB49AF97B178C12509E9
and
71B96F4DE7D55F9FA3B7CE409D7F67C7EBF309D73F08C9FE70C1D297A6F4D098,
respectively. The full command was:

~~~powershell
C:\tmp\c09_condition_scan.exe --limit 100000000000 --exhaustive-limit 100000000 --threads 64 --chunk-size 4194304
~~~
