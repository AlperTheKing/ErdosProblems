# P70: uniform carry mixing for the natural Ruzsa lifts

## 1. Result

Let \(p\) be an odd prime, put

\[
        b=p-1,\qquad n=p(p-1),
\]

and fix a primitive root \(g\) modulo \(p\).  For
\(e\in\mathbb F_p^*\), let

\[
 B_e=\{b_i:0\le i<b\}\subseteq\{0,\ldots,n-1\},
 \tag{1}
\]

where \(b_i\) is the unique least nonnegative integer satisfying

\[
 b_i\equiv i\pmod b,\qquad
 b_i\equiv e(g^i-1)\pmod p.                              \tag{2}
\]

For \(0\le t<n\), define \(R_{B_e}(t)\) exactly as in P30: it is the
number of tuples \((x,y,z,w)\) with

\[
 x,y,z,w\in B_e,\qquad x\le y,\qquad z>w,
\]

and

\[
                  x+y+z-w=2n+t.                          \tag{3}
\]

Equivalently, by the strong modular Sidon property, it is the P30 support
count

\[
 \#\{s\in\Sigma_1(B_e):s>t,\ n+t-s\in\Delta^+(B_e)\}.
\]

**Theorem P70 (uniform Ruzsa carry mixing).**  Uniformly in

\[
       e\in\mathbb F_p^*,\qquad 0\le t<n,
\]

one has

\[
 \boxed{
 R_{B_e}(t)
   =\frac{p^2}{12}\left(1-\frac{t}{n}\right)^3+o(p^2).
 }
 \tag{4}
\]

In particular, for every fixed \(\alpha<1\), if

\[
                  c_\alpha=\frac{(1-\alpha)^3}{24},       \tag{5}
\]

then, for all sufficiently large primes \(p\), uniformly in \(e\) and
\(0\le t\le\alpha n\),

\[
                  R_{B_e}(t)\ge c_\alpha p^2>0.           \tag{6}
\]

Thus the alternative in the assignment has a positive answer.  Natural
Ruzsa CRT lifts have no carry hole in any fixed compact subinterval of
\([0,n)\) once \(p\) is large.  Consequently this construction cannot
produce an infinite reflected family with coefficient bounded below \(3\)
by a fixed positive constant.

## 2. The modular surface and its size

Write

\[
 \delta_i=[e(g^i-1)]_p,\qquad
 q_i=[i-\delta_i]_{p-1},\qquad
 b_i=\delta_i+p q_i.                                     \tag{7}
\]

Let

\[
 H=t\pmod {p-1},\qquad T=t\pmod p,
\]

with the displayed residues represented in their respective finite
fields.  An ordered quadruple of indices \((a_1,a_2,a_3,a_4)\) satisfies

\[
 b_{a_1}+b_{a_2}+b_{a_3}-b_{a_4}\equiv t\pmod n          \tag{8}
\]

if and only if, on writing

\[
 X=g^{a_1},\quad Y=g^{a_2},\quad Z=g^{a_3},\quad D=g^{a_4},
\]

one has

\[
 D=\lambda XYZ,\qquad X+Y+Z-D=K,                         \tag{9}
\]

where

\[
             \lambda=g^{-H},\qquad K=2+T/e.              \tag{10}
\]

Indeed, the first equation in (9) is the \((p-1)\)-coordinate of (8),
and the second is its \(p\)-coordinate after division by \(e\).

Eliminating \(D\), the solution surface is

\[
             X+Y+Z-\lambda XYZ=K.                        \tag{11}
\]

Outside the locus \(1-\lambda XY=0\), it has the rational
parametrization

\[
             Z=\frac{K-X-Y}{1-\lambda XY}.               \tag{12}
\]

The pairs for which the denominator or numerator in (12) vanishes account
for \(O(p)\) points, uniformly in \(\lambda,K\).  If both denominator and
numerator vanish, then \(XY=\lambda^{-1}\) and \(X+Y=K\), so there are at
most two such pairs, each with at most \(p-1\) choices of \(Z\).  It
follows that the total number \(Q_{e,t}\) of ordered modular solutions is

\[
                  Q_{e,t}=p^2+O(p)                       \tag{13}
\]

uniformly in \(e,t\).

## 3. Exact Fourier conversion

Let \(\chi_m\) be the multiplicative character of \(\mathbb F_p^*\)
defined by

\[
                 \chi_m(g)=\exp(2\pi i m/(p-1)),          \tag{14}
\]

and put \(\psi(u)=\exp(2\pi i u/p)\).  Formula (7) gives the following
identity with no approximation:

\[
 \boxed{
 \exp(2\pi i m b_i/n)
   =\chi_m(g^i)\,\psi\bigl(-me(g^i-1)\bigr).
 }
 \tag{15}
\]

To check it, use \(q_i\equiv i-\delta_i\pmod {p-1}\):

\[
 \begin{aligned}
 \exp(2\pi i m b_i/n)
 &=\exp(2\pi i m q_i/(p-1))
   \exp(2\pi i m\delta_i/(p(p-1)))\\
 &=\chi_m(g^i)
   \exp(-2\pi i m\delta_i/(p-1))
   \exp(2\pi i m\delta_i/(p(p-1)))\\
 &=\chi_m(g^i)\exp(-2\pi i m\delta_i/p).
 \end{aligned}
\]

The last factor is the claimed additive character because
\(\delta_i\equiv e(g^i-1)\pmod p\).

This exact identity is the main simplification relative to a direct
least-representative analysis.

## 4. The hybrid surface estimate

We need only the first three normalized coordinates.  The following lemma
is uniform in all parameters.

**Lemma 4.1 (Ruzsa surface estimate).**  Fix an integer triple
\(m=(m_1,m_2,m_3)\ne(0,0,0)\).  For all sufficiently large \(p\),

\[
 \begin{aligned}
 &\sum_{(a_1,a_2,a_3,a_4)\text{ satisfying }(8)}
 \exp\left(
   \frac{2\pi i}{n}
   (m_1b_{a_1}+m_2b_{a_2}+m_3b_{a_3})
 \right)\\
 &\hspace{45mm}=O_m(p^{3/2}),                             \tag{16}
 \end{aligned}
\]

uniformly in \(e,t\).  For \(m\) in any fixed finite box, the implied
constant may be chosen uniformly over that box.

**Proof.**  Remove the \(O(p)\) exceptional points from Section 2 and use
\((X,Y)\) as coordinates on the open subset \(U\subset\mathbb A^2\) on
which (12) is defined and nonzero.  By (15), apart from a constant phase,
the summand is

\[
 \chi_{m_1}(X)\chi_{m_2}(Y)\chi_{m_3}(Z)
 \psi\bigl(-e(m_1X+m_2Y+m_3Z)\bigr),                    \tag{17}
\]

where \(Z\) is the rational function (12).

The Artin--Schreier phase in (17) is geometrically nonconstant on the
surface.  More explicitly, if

\[
                  AX+BY+CZ=c                              \tag{18}
\]

were an identity on (11), then substitution from (12) and multiplication
by \(1-\lambda XY\) would give

\[
 (AX+BY-c)(1-\lambda XY)+C(K-X-Y)=0.                     \tag{19}
\]

The coefficients of \(X^2Y\) and \(XY^2\) first force \(A=B=0\); the
coefficient of \(XY\) then forces \(c=0\), and the coefficients of
\(X,Y\) force \(C=0\).  Thus (18) is constant only for the zero triple.
For fixed nonzero \(m\) and sufficiently large \(p\), the rational
function in (17) is also not of Artin--Schreier form \(F^p-F+c\): all of
its pole orders have absolute value bounded independently of \(p\), and a
nonconstant \(F^p-F\) has a pole order divisible by \(p\).  A nonconstant
rational function on the projective compactification has a pole somewhere.
The resulting wild Artin--Schreier monodromy cannot be cancelled by any of
the tame Kummer factors.

For a more elementary quantitative estimate, apply the Weil bound one
fibre at a time.  First suppose \((m_2,m_3)\ne(0,0)\), fix \(X\), and sum
over \(Y\).  The nonconstant part of the additive phase is

\[
 m_2Y+m_3\frac{K-X-Y}{1-\lambda XY}.                     \tag{20}
\]

If \(m_2\ne0\), its numerator after multiplication by
\(1-\lambda XY\) has quadratic coefficient \(-m_2\lambda X\ne0\), so
the rational function (20) is nonconstant on every fibre.  If \(m_2=0\)
and \(m_3\ne0\), it can be constant only when

\[
                 \lambda X(K-X)=1,                       \tag{21}
\]

which holds for at most two values of \(X\).  On every other fibre, the
summand is the trace function of a geometrically nonconstant rank-one
Kummer--Artin--Schreier sheaf on \(\mathbb P^1\) with a bounded number of
punctures and bounded conductor.  The one-variable Weil bound is therefore
\(O_m(p^{1/2})\), uniformly in \(e,\lambda,K,X\).  The at most two
exceptional fibres contribute \(O(p)\) in total.  Summing over \(X\) gives
\(O_m(p^{3/2})\).

If \(m_2=m_3=0\), then \(m_1\ne0\).  Interchange \(X\) and \(Y\) and
sum first in \(X\); the additive phase \(m_1X\) is nonconstant on every
fibre, so the same one-variable Weil bound again gives \(O_m(p^{3/2})\).
Restoring the \(O(p)\) points omitted from the parametrized open set does
not change the estimate.  This proves (16).  \(\square\)

For completeness, if all four coordinates were retained, the only
exceptional Fourier line would be

\[
             (m_1,m_2,m_3,m_4)=(r,r,r,-r).               \tag{22}
\]

On (9), both the additive phase and the Kummer product are then constant.
Indeed, after substituting \(D=X+Y+Z-K\), the nonconstant part of the
additive phase is

\[
 (m_1+m_4)X+(m_2+m_4)Y+(m_3+m_4)Z.
\]

The calculation (19) shows that it is constant only on the line (22).  On
that line the Kummer product is

\[
 \chi_r(XYZ/D)=\chi_r(\lambda^{-1}),
\]

also constant by (9).  Hence there are no further exceptional modes.
This is exactly the annihilator of the affine torus

\[
 u_1+u_2+u_3-u_4=t/n\pmod1.
\]

Projecting to the first three coordinates removes this line completely,
which is why Lemma 4.1 has no exceptional nonzero mode.

## 5. Uniform equidistribution and the carry tetrahedron

Put the uniform probability measure on the first three normalized
coordinates of the modular solutions:

\[
 \mu_{p,e,t}
 =\frac1{Q_{e,t}}
   \sum_{(8)}
   \delta_{(b_{a_1}/n,b_{a_2}/n,b_{a_3}/n)}.             \tag{23}
\]

Equations (13) and (16), followed by Weyl's criterion, show that

\[
       \mu_{p,e,t}\Longrightarrow\text{Lebesgue measure on }[0,1)^3
                                                                    \tag{24}
\]

uniformly in \(e,t\).  Here uniformity has its literal sequential meaning:
for every sequence \(p\to\infty\) and every choice of \(e=e(p)\) and
\(t=t(p)\), all nonzero Fourier coefficients tend to zero.  If a uniform
box-discrepancy statement failed, compactness would supply a contradicting
sequence.  Finite grid approximation then extends this uniformly to the
moving tetrahedra below, since their planar boundaries have uniformly
bounded area.

Let

\[
                     \theta=t/n.
\]

For a modular solution, put

\[
 b_{a_1}+b_{a_2}+b_{a_3}-b_{a_4}=t+kn.                  \tag{25}
\]

Because \(0\le b_{a_4}<n\), equation (25) gives

\[
 k=\left\lfloor
      \frac{b_{a_1}+b_{a_2}+b_{a_3}}n-\theta
    \right\rfloor.                                      \tag{26}
\]

Thus the literal top carry \(k=2\) is exactly the tetrahedron

\[
 \mathcal T_\theta
 =\{(u_1,u_2,u_3)\in[0,1)^3:
                         u_1+u_2+u_3\ge2+\theta\}.        \tag{27}
\]

Its volume is

\[
 \operatorname{vol}(\mathcal T_\theta)
 =\frac{(1-\theta)^3}{6};                                \tag{28}
\]

translate each coordinate by its deficit from one to obtain the standard
simplex of side \(1-\theta\).  Uniform equidistribution therefore gives
the ordered top-carry count

\[
 C_{e,t}
 =\frac{(1-t/n)^3}{6}p^2+o(p^2),                         \tag{29}
\]

uniformly in \(e,t\).

Every solution counted in (27) automatically has \(b_{a_3}>b_{a_4}\),
because

\[
 b_{a_3}-b_{a_4}
   =2n+t-b_{a_1}-b_{a_2}\ge t+2>0.                       \tag{30}
\]

It remains only to pass from ordered \((a_1,a_2)\) to \(x\le y\).  The
number of solutions with \(a_1=a_2\) is \(O(p)\) uniformly: with \(X=Y\),
equation (11) becomes

\[
              (1-\lambda X^2)Z=K-2X,                    \tag{31}
\]

which has at most one \(Z\) for each \(X\), apart from at most two values
of \(X\) for which both sides vanish, each contributing at most \(p-1\)
choices.  Off the diagonal, swapping \(a_1,a_2\) acts freely.  If
\(D_{e,t}\) denotes the diagonal count, then exactly

\[
                    C_{e,t}=2R_{B_e}(t)-D_{e,t},
\]

with \(D_{e,t}=O(p)\).  Hence

\[
 R_{B_e}(t)=\frac12C_{e,t}+O(p),                          \tag{32}
\]

which together with (29) proves (4).

## 6. Relation to the exact all-cut data

The independently verified all-cut records through \(p=293\) are fully
consistent with the theorem but show that the finite onset is late.  The
smallest first-hole offsets \(t/n\) over all cuts are

\[
\begin{array}{c|c}
p&\min_e t_{\rm first}(e)/n\\ \hline
257&26183/32896\\
263&52229/68906\\
269&27123/36046\\
271&1829/2439\\
277&14924/19113\\
281&31021/39340\\
283&10753/13301\\
293&67943/85556.
\end{array}                                               \tag{33}
\]

These are exact finite holes, not counterexamples to (4).  For example,
the main term at a fixed \(\theta<1\) is quadratic, whereas Lemma 4.1 by
itself gives a square-root-saving error of order \(p^{3/2}\); the theorem
does not supply a small numerical threshold.  Also \(R_{B_e}(t)\) is not
monotone in \(t\), so a first-hole statistic cannot replace the slice count
in the proof.

The records and their independent exact verifier are

~~~text
problems/864/compute/p30/all_cuts_p257.json
problems/864/compute/p70/all_cuts_p263.json
problems/864/compute/p70/all_cuts_p269.json
problems/864/compute/p70/all_cuts_p271.json
problems/864/compute/p70/all_cuts_p277.json
problems/864/compute/p70/all_cuts_p281.json
problems/864/compute/p70/all_cuts_p283.json
problems/864/compute/p70/all_cuts_p293.json
problems/864/compute/p70/verify_all_cut_records.py
problems/864/compute/p70/verified_extrema_p257_p293.json
~~~

All arithmetic in those files is integral or rational, and every reflected
census includes diagonal pair sums.

## 7. Scope and analytic input

P70 closes the natural Ruzsa carry lane.  It does not resolve Erdős 864:
it proves that this particular modular Sidon family cannot supply the
desired counterconstruction.

The analytic input in Lemma 4.1 is only the standard one-variable Weil
bound for a geometrically nonconstant rank-one
Kummer--Artin--Schreier sheaf on \(\mathbb P^1\).  The fibre functions in
(20) have bounded degree, a bounded number of punctures, and bounded tame
and Swan conductors.  Equations (20)--(21) explicitly classify the only
fibres on which the additive phase can become constant; there are at most
two, and their trivial bound is harmless.  Thus no two-dimensional Betti
estimate and no unexamined exceptional Fourier mode is hidden in the
invocation.  A primary source for the weight estimate underlying the Weil
bound is P. Deligne, *La conjecture de Weil II*, Publ. Math. IHES 52
(1980), 137--252.
