# P13: coupled variational relaxation of the signed ruler

## Verdict

The strongest weak-occupation relaxation obtained directly from

\[
D(Z)\cap(G+S(Z))=\varnothing
\]

does **not** force

\[
\frac{G+2W}{p^2}\geq 3-o(1).
\]

This remains false when the two label laws are not optimized independently:
they are required to be the difference and shifted-sum marginals of the
same ruler-pair measure.  The relaxation has sharp infimum \(2\).  An exact
interior rational countermodel is

\[
w=1,\qquad g=\frac12,\qquad \mu={\bf 1}_{[0,1]}(x)\,dx,
\qquad \ell=g+2w=\frac52<3.                 \tag{1}
\]

Here \(w=W/p^2\), \(g=G/p^2\), and
\(\ell=(G+2W)/p^2\).  The countermodel satisfies the full measure-domination
inequality for every nonnegative test function, the exact joint
difference/sum coupling, and every continuum lag-window constraint.  Thus
no LP or moment projection of this weak continuum model can prove the
coefficient \(3\).

The information lost is microscopic.  Exact rulers have two disjoint
integer label colours at lattice scale one.  Weak convergence remembers
only their fractional local densities, so the colours may interlace on
successive lattice cells.  Closing the signed-ruler problem requires a
two-scale arithmetic invariant controlling this phase interlacing (or an
equivalent unit-scale mixed Fourier correlation), not another macroscopic
moment or interval-capacity inequality.

## 1. Exact finite normalization

Let

\[
Z_p=\{0=z_0<z_1<\cdots<z_{p-1}=W_p\},\qquad G_p>0,
\]

and assume all labels in

\[
\{z_j-z_i:i<j\}\ \dot\cup\
\{G_p+z_i+z_j:i\leq j\}                         \tag{2}
\]

are distinct.  This is exactly the signed-ruler condition from P07; in
particular it retains all diagonal shifted sums.  Put

\[
w_p=\frac{W_p}{p^2},\qquad g_p=\frac{G_p}{p^2},\qquad
\mu_p=\frac1p\sum_{i=0}^{p-1}\delta_{z_i/p^2}.             \tag{3}
\]

The complete scaled label measure is

\[
\nu_p=\frac1{p^2}\sum_{i<j}
 \delta_{(z_j-z_i)/p^2}
+\frac1{p^2}\sum_{i\leq j}
 \delta_{(G_p+z_i+z_j)/p^2}.                              \tag{4}
\]

It has mass exactly one.  Since (2) consists of distinct integers, every
bounded interval \(I\) satisfies

\[
\nu_p(I)\leq |I|+\frac{2}{p^2}.                           \tag{5}
\]

Suppose along a subsequence that \(w_p\to w<\infty\),
\(g_p\to g\geq0\), and \(\mu_p\Rightarrow\mu\).  Products of probability
measures converge weakly, while the \(p\) diagonal terms have total mass
\(1/p\).  Hence (4) converges to

\[
\boxed{
\nu_{\mu,g}
=\frac12\,(|x-y|)_\#(\mu\otimes\mu)
+\frac12\,(g+x+y)_\#(\mu\otimes\mu).}                    \tag{6}
\]

Passing (5) to the limit gives the full occupation constraint

\[
\boxed{\nu_{\mu,g}\leq {\bf 1}_{[0,g+2w]}(t)\,dt.}        \tag{7}
\]

Equivalently, for every continuous compactly supported
\(\varphi\geq0\),

\[
\frac12\iint \varphi(|x-y|)\,d\mu(x)d\mu(y)
+\frac12\iint \varphi(g+x+y)\,d\mu(x)d\mu(y)
\leq\int_0^{g+2w}\varphi(t)\,dt.                         \tag{8}
\]

This is strictly stronger than a finite moment system: it contains every
nonnegative cutoff, interval, polynomial-majorant, and moment inequality
at once.

## 2. The same-ruler coupling is retained

The two marginals in (6) are not free variables.  On the ordered triangle
\(x<y\), define the joint ruler-pair measure

\[
J_{\mu,g}=(y-x,\ g+x+y)_\#
 \bigl((\mu\otimes\mu)|_{\{x<y\}}\bigr).                  \tag{9}
\]

Its coordinates \(d,c\) obey the exact pair identities

\[
c-d=g+2x,\qquad c+d=g+2y.                                 \tag{10}
\]

For atomless \(\mu\), the first marginal of \(J_{\mu,g}\) is the
difference part of (6), and its second marginal is the shifted-sum part.
Thus (9) preserves the complete coupling of the same pair of ruler points,
not merely the cardinalities or separate scalar moments of the two label
families.

The variational relaxation is therefore:

* \(g\geq0\), \(w\geq0\), and \(\mu\) is a probability measure on
  \([0,w]\);
* \(J\) is exactly the pushforward (9), so all mixed moments and (10) hold;
* the sum of its two label marginals satisfies (7);
* minimize \(\ell=g+2w\).

Because this retains the actual product measure and its joint pushforward,
it is stronger than an LP obtained by replacing \(J\) by an arbitrary
coupling with matching marginals.  A feasible point here is consequently
feasible in every such LP relaxation.

## 3. Sharp universal bound of the relaxation

The relaxation always has \(w\geq1\).  This is more than the mass bound and
uses the entire difference law.

Let

\[
\rho=(x-y)_\#(\mu\otimes\mu)=\mu*\widetilde\mu.
\]

The difference component in (6) is half the law of \(|x-y|\).  For every
Borel \(E\subset(0,\infty)\), symmetry gives

\[
\frac12\Pr(|x-y|\in E)=\rho(E).                           \tag{11}
\]

Equation (7) therefore gives \(\rho\leq dt\) away from zero.  It also
forces \(\rho(\{0\})=0\), since an atom of \(\mu\) would create an atom of
the first measure in (6).  By symmetry,



\[
\rho\leq dt\quad\hbox{on all of }\mathbb R.               \tag{12}
\]

Use the Fourier convention
\(\widehat f(\xi)=\int e^{-2\pi i\xi x}f(x)\,dx\), and let

\[
\phi_\varepsilon(t)=\varepsilon^{-1/2}
 e^{-\pi t^2/\varepsilon},\qquad
\widehat\phi_\varepsilon(\xi)=e^{-\pi\varepsilon\xi^2}.
\]

From (12), Fourier inversion for finite measures, and positivity,

\[
\int_{\mathbb R}e^{-\pi\varepsilon\xi^2}
 |\widehat\mu(\xi)|^2\,d\xi
=\int\phi_\varepsilon\,d\rho
\leq\int\phi_\varepsilon(t)\,dt=1.                       \tag{13}
\]

Monotone convergence as \(\varepsilon\downarrow0\) gives
\(\widehat\mu\in L^2\) with norm at most one.  Plancherel then gives
\(\mu=f(x)dx\) and

\[
\int f(x)^2\,dx\leq1.                                    \tag{14}
\]

Since \(f\) is supported on an interval of length at most \(w\), Cauchy
gives

\[
1=\left(\int f\right)^2\leq w\int f^2\leq w.              \tag{15}
\]

Thus

\[
\boxed{\ell=g+2w\geq2.}                                  \tag{16}
\]

Section 4 gives feasible profiles with \(g\downarrow0\), \(w=1\), so the
infimum is exactly \(2\).

## 4. Exact rational fractional countermodel

Take the data in (1).  Equivalently, let \(X,Y\) be independent uniform
variables on \([0,1]\).  On \(X<Y\), put

\[
d=Y-X,\qquad c=\frac12+X+Y.                               \tag{17}
\]

The joint measure (9) has the exact rational density

\[
dJ(d,c)=\frac12\,
 {\bf1}_{\{0<d<1,\;\frac12+d<c<\frac52-d\}}\,dd\,dc.     \tag{18}
\]

Thus the pairwise coupling (10) is realized, rather than relaxed away.
Its difference marginal has density

\[
a(t)=(1-t){\bf1}_{[0,1]}(t),                              \tag{19}
\]

and its shifted-sum marginal has density

\[
b(t)=
\begin{cases}
0,&t<\frac12,\\
\frac{t-1/2}{2},&\frac12\leq t\leq\frac32,\\
\frac{5/2-t}{2},&\frac32\leq t\leq\frac52,\\
0,&t>\frac52.
\end{cases}                                               \tag{20}
\]

Their combined occupation density is

\[
a(t)+b(t)=
\begin{cases}
1-t,&0\leq t\leq\frac12,\\
\frac34-\frac t2,&\frac12\leq t\leq1,\\
\frac{t-1/2}{2},&1\leq t\leq\frac32,\\
\frac{5/2-t}{2},&\frac32\leq t\leq\frac52,\\
0,&\text{otherwise}.
\end{cases}                                               \tag{21}
\]

Every piece in (21) lies between zero and one.  Hence (7) and therefore
every test inequality (8) hold exactly, while

\[
\ell=\frac12+2=\frac52<3.                                \tag{22}
\]

More generally, the same uniform ruler with any rational \(0<g\leq1\)
is feasible.  On the only overlap interval \(g\leq t\leq1\),

\[
a(t)+b_g(t)=1-t+\frac{t-g}{2}\leq1,                       \tag{23}
\]

and outside that interval each marginal is at most one.  Therefore
\(\ell=2+g\), proving that the infimum in (16) is \(2\).  At the closed
boundary \(g=0\), the total density simplifies to

\[
\frac{d\nu}{dt}=1-\frac t2\quad(0\leq t\leq2),           \tag{24}
\]

and all its moments are rational:

\[
\int t^r\,d\nu(t)=
\frac{2^{r+1}}{(r+1)(r+2)}\qquad(r\geq0).                 \tag{25}
\]

Thus even the complete moment sequence has an exact \(L=2\) boundary
countermodel.

## 5. Audit against the rank-window constraints

Let \(q(s)=s\) be the quantile function of the uniform ruler.  For a
normalized lag cutoff \(0\leq\alpha\leq1\), the continuum versions of
P07's \(M_r\) and \(T_r\) are

\[
m_\alpha=\int_0^\alpha(1-s)\,ds
=\alpha-\frac{\alpha^2}{2},                               \tag{26}
\]

\[
\tau_\alpha
=\int_0^\alpha\int_0^{1-s}
 (q(t+s)-q(t))\,dt\,ds
=\frac{\alpha^2}{2}-\frac{\alpha^3}{3}.                  \tag{27}
\]

The exact gap-multiplicity upper bound becomes

\[
\tau_\alpha\leq\frac{\alpha^2w}{2}=\frac{\alpha^2}{2},  \tag{28}
\]

which (27) satisfies for every \(\alpha\).  The selected lag-window
difference measure is simply

\[
(1-t){\bf1}_{[0,\alpha]}(t)\,dt,                          \tag{29}
\]

a submeasure of (19).  Hence adding it to the same shifted-sum marginal
still obeys every nonnegative weighted capacity inequality inherited from
(7).  In particular, all continuum positive-part cutoffs underlying P07
Lemma 1 hold simultaneously, not merely at one optimized cutoff.

The countermodel therefore survives:

1. the full joint pair law (18);
2. all mixed moments implied by (17);
3. all nonnegative test functions in (8);
4. every nested lag-window and its first-moment bound (26)--(29).

It is not a cardinality-only or scalar-moment artefact.

## 6. The missing discrete invariant

Let \(d_p(n)={\bf1}_{D(Z_p)}(n)\) and
\(s_p(n)={\bf1}_{G_p+S(Z_p)}(n)\).  Exact signed rulers satisfy the
unit-lattice identity

\[
d_p(n)s_p(n)=0\qquad\text{for every integer }n.            \tag{30}
\]

After replacing each lattice cell by an interval of width \(1/p^2\), the
two bounded colour fields may converge only weakly.  Weak limits preserve

\[
a(t)+b(t)\leq1,                                           \tag{31}
\]

but do not preserve \(a(t)b(t)=0\).  In the rational profile (19)--(20),

\[
\int_{1/2}^{1}a(t)b(t)\,dt
=\int_{1/2}^{1}(1-t)\frac{t-1/2}{2}\,dt
=\frac1{96}>0.                                            \tag{32}
\]

There is no contradiction: (32) represents microscopic checkerboarding of
difference and shifted-sum labels.  A Young measure can realize it at each
macroscopic \(t\) by assigning probabilities

\[
\Pr(D)=a(t),\qquad \Pr(S)=b(t),\qquad
\Pr(\varnothing)=1-a(t)-b(t),                             \tag{33}
\]

while every microscopic cell still has only one colour.

What is missing is a theorem that the arithmetic phases of the two colours
cannot checkerboard with the fractional densities (19)--(20) when both are
generated by one integer ruler.  Equivalently, one must retain a unit-scale
mixed correlation of

\[
\sum_n d_p(n)s_p(n)=0                                     \tag{34}
\]

together with the fact that both indicator polynomials come from the same

\[
P_p(z)=\sum_{x\in Z_p}z^x.                                \tag{35}
\]

Macroscopic moments, interval occupancies, and the joint continuum law
(18) erase this phase.  A viable next invariant must therefore be
two-scale: for example a quantitative unit-circle Fourier restriction on
the mixed difference/sum correlation, or an arithmetic residue/phase
rigidity statement strong enough to forbid (33).  Simply imposing
\(a(t)b(t)=0\) on weak limits would be invalid, because products are not
weakly continuous.

## 7. Consequence for the proof frontier

For a fully reflected admissible set of size \(2p\), the desired
\(2/\sqrt3\) constant is exactly the asymptotic signed-ruler assertion

\[
G+2W\geq(3-o(1))p^2.                                     \tag{36}
\]

The relaxation above proves only the sharp bound

\[
G+2W\geq(2-o(1))p^2,                                     \tag{37}
\]

and (1) shows a strict gap of (1/2) even with positive normalized (G).
Therefore the coefficient (3) cannot be obtained from any continuum LP
whose state consists of the ruler distribution, its complete coupled
pair-label law, weak label capacities, and rank-window moments.  The next
attack must expose the microscopic arithmetic phase in (30)--(35).
