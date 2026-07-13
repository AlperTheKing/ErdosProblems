# P47: phase-sensitive equal-modulus polynomials

## Verdict

Put

\[
 P(x)=\sum_{z\in Z}x^z,\qquad
 A(x)=P(x)P(x^{-1}),\qquad
 B(x)=x^G P(x)^2,
\]

where \(Z=\{0=z_0<\cdots<z_{p-1}=W\}\) is integer Sidon and
\(G\geq 1\).  The all-circle phase statement is stronger than Parseval:
it says that the complete aperiodic autocorrelations of the coefficient
vectors of \(A\) and \(B\) agree at every lag.  This identity is exact,
but it is independent of \(G\).  The only part that locates \(G\) is the
coefficientwise exclusion.

A generic uncertainty theorem for equal-modulus polynomials with disjoint
coefficient supports cannot give coefficient \(3\).  Lemma P47.1 below
gives two ordinary, all-circle families with endpoint

\[
                         (2+o(1))p^2.
\]

The first family is palindromic and has exactly the coefficient profile,
central coefficient, \(\ell^1\) norm, and \(\ell^2\) norm of
\(P(x)P(x^{-1})\).  The second family is a nontrivial zero flip, rather
than a monomial translate.

These examples do not settle the structured problem.  They do not
simultaneously retain the square profile

\[
              1^p,\quad 2^{\binom p2}
\]

and the common factorization \(PP^\#\) versus \(x^G P^2\).  An
all-circle coefficient-two family retaining those data would itself be
an asymptotic signed-ruler counterexample.  Thus the result of this lane
is negative for a generic phase/uncertainty principle and open for an
arc-sensitive inequality using the exact Newman factor and both
coefficient profiles.

## 1. Complete coefficient and phase lemma

For a real Laurent polynomial \(R\), write

\[
                     R^\#(x)=R(x^{-1}).
\]

Let \(D^+(Z)=\{z_j-z_i:0\leq i<j<p\}\) and let
\(S(Z)=\{z_i+z_j:0\leq i\leq j<p\}\).

**Lemma P47.1 (exact aperiodic phase data and coefficient-two
barriers).**

1.  If \(Z\) is Sidon, then the coefficients \(a_n=[x^n]A\) are

    \[
    a_0=p,\qquad
    a_n=
    \begin{cases}
    1,&n\in D^+(Z)\cup(-D^+(Z)),\\
    0,&\text{otherwise}
    \end{cases}
    \quad(n\ne0).
    \tag{1}
    \]

    Hence

    \[
    |\operatorname{supp}A|=p(p-1)+1,\qquad
    \operatorname{supp}A\subseteq[-W,W].
    \tag{2}
    \]

    The coefficients \(b_n=[x^n]B\) are

    \[
    b_{G+2z_i}=1\quad(0\leq i<p),
    \tag{3}
    \]

    \[
    b_{G+z_i+z_j}=2\quad(0\leq i<j<p),
    \tag{4}
    \]

    and all other coefficients vanish.  The exponents in (3)--(4)
    are distinct.  Therefore

    \[
    |\operatorname{supp}B|=\binom{p+1}{2},\qquad
    \operatorname{supp}B\subseteq[G,G+2W].
    \tag{5}
    \]

2.  Since \(G\geq1\),

    \[
    \operatorname{supp}A\cap\operatorname{supp}B=\varnothing
    \quad\Longleftrightarrow\quad
    D^+(Z)\cap(G+S(Z))=\varnothing.
    \tag{6}
    \]

    In particular, the zero difference is not a support collision:
    it is one support point of \(A\), with coefficient \(p\), whereas
    \(B\) has no exponent zero.

3.  The complete aperiodic autocorrelation identity is

    \[
                  A(x)A^\#(x)=B(x)B^\#(x)
                  =P(x)^2P(x^{-1})^2.
    \tag{7}
    \]

    Equivalently, if \(a=(a_n)\) and \(b=(b_n)\), then for every
    integer lag \(h\),

    \[
             \sum_n a_{n+h}a_n=\sum_n b_{n+h}b_n.
    \tag{8}
    \]

    Consequently \(|A(e^{i\theta})|=|B(e^{i\theta})|\) for every
    real \(\theta\).  Identity (7), and hence every lag in (8), is
    unchanged when \(G\) is changed.

4.  The full coefficientwise interaction is the Hadamard collision
    polynomial

    \[
    \begin{aligned}
    {\cal C}_{Z,G}(t)
      &:=\operatorname{CT}_x\!\left[A(tx)B(x^{-1})\right]\\
      &=\sum_n a_nb_nt^n\\
      &=\sum_{0\leq i\leq j<p}
        (2-\mathbf 1_{i=j})
        \mathbf 1_{\,G+z_i+z_j\in D^+(Z)}
        t^{G+z_i+z_j}.
    \end{aligned}
    \tag{9}
    \]

    Thus (6) is equivalent to
    \({\cal C}_{Z,G}(t)\equiv0\).  For every \(r\geq0\),

    \[
    \left.(t\,d/dt)^r{\cal C}_{Z,G}(t)\right|_{t=1}
      =\sum_n n^r a_nb_n.
    \tag{10}
    \]

    Hence every polynomially frequency-weighted orthogonality obtained
    by differentiating the phase pairing is already a derivative of
    the exact collision polynomial.  It supplies no independent
    inequality once (6) is assumed.

5.  There are two explicit coefficient-two barriers.

    (a) Put \(r=\binom p2\) and define the Laurent polynomials

    \[
       F_p(x)=p+\sum_{\substack{-r\leq j\leq r\\j\ne0}}x^{2j},
       \qquad H_p(x)=xF_p(x).
       \tag{11}
    \]

    Their supports are disjoint and together occupy every frequency
    in \([-2r,2r+1]\).  They have equal modulus on the whole unit
    circle and equal aperiodic autocorrelations.  Each has one
    coefficient \(p\) and \(p(p-1)\) coefficients \(1\), so

    \[
    \|F_p\|_{\ell^1}=\|H_p\|_{\ell^1}=p^2,\qquad
    \|F_p\|_{\ell^2}^2=\|H_p\|_{\ell^2}^2=2p^2-p.
    \tag{12}
    \]

    Moreover \(F_p^\#=F_p\).  After multiplying both polynomials by
    \(x^{2r}\), they are ordinary polynomials supported in
    \([0,N_p]\), where

    \[
                    N_p=4r+1=2p^2-2p+1.
    \tag{13}
    \]

    (b) Define

    \[
    U_p(x)=\sum_{i=0}^{p-1}x^{2i},\qquad
    V_p(x)=\sum_{j=0}^{p-1}(j+1)x^{2pj},
    \tag{14}
    \]

    \[
    F'_p(x)=U_p(x)V_p(x),\qquad
    H'_p(x)=x^{\,2p(p-1)+1}U_p(x)V_p^\#(x).
    \tag{15}
    \]

    The support of \(F'_p\) is every even frequency in
    \([0,2p^2-2]\), and the support of \(H'_p\) is every odd
    frequency in \([1,2p^2-1]\).  They are disjoint, fill all
    \(2p^2\) slots, and

    \[
                    |F'_p(e^{i\theta})|
                    =|H'_p(e^{i\theta})|
                    \quad\text{for every }\theta.
    \tag{16}
    \]

    For \(p\geq2\), \(H'_p\) is not a monomial multiple of \(F'_p\).

6.  At \(p=3\), even both exact coefficient profiles are compatible
    with a short all-circle zero-flip pair.  Namely,

    \[
    F=1+x+x^2+3x^3+x^6+x^8+x^{10},
    \]

    \[
    H=x^4+x^5+2x^9+2x^{11}+2x^{12}+x^{14}.
    \]

    These supports are disjoint, the profiles are respectively
    \(3,1^6\) and \(1^3,2^3\), and \(|F|=|H|\) on the whole unit
    circle.  This is a finite certificate only: \(F\) is not
    self-reciprocal and the pair does not have the signed-ruler
    orientation.

### Proof

For (1), expand

\[
       P(x)P(x^{-1})=\sum_{i,j}x^{z_i-z_j}.
\]

There are exactly \(p\) diagonal ordered pairs, all at exponent zero.
If two positive differences agree, say

\[
                        z_j-z_i=z_\ell-z_k>0,
\]

then \(z_j+z_k=z_\ell+z_i\).  Sidonicity makes the two unordered
pairs equal.  The crossed identification would force a zero difference,
so the original ordered pairs agree.  Thus every nonzero signed
difference has coefficient one.  This proves (1)--(2).

Next,

\[
        x^G P(x)^2=\sum_i x^{G+2z_i}
          +2\sum_{i<j}x^{G+z_i+z_j}.
\]

Sidonicity, with diagonal pairs included, says that all displayed
unordered sums are distinct.  This proves (3)--(5), including both the
diagonal coefficient \(1\) and the off-diagonal coefficient \(2\).

All exponents of \(B\) are positive.  The negative support and zero
coefficient of \(A\) therefore cannot meet \(B\); its positive support
is exactly \(D^+(Z)\).  This proves (6).

Since \(A^\#=A\) and

\[
                 B^\#=x^{-G}P(x^{-1})^2,
\]

both sides of (7) are \(P^2(P^\#)^2\).  Comparing the coefficient of
\(x^h\) gives (8).  On \(|x|=1\), \(P(x^{-1})=\overline{P(x)}\), so
\(A=|P|^2\) and \(|B|=|P|^2\).  The monomials \(x^G,x^{-G}\) cancel
from (7), proving the asserted independence from \(G\).

Expanding the constant term in (9) gives
\(\sum_n a_nb_nt^n\).  Substituting (1), (3), and (4) gives its final
displayed expression.  All its coefficients are nonnegative, so it
vanishes identically exactly when the supports are disjoint.  Applying
the Euler derivative \(t\,d/dt\) proves (10).

For (11), \(F_p\) has all even frequencies from \(-2r\) through \(2r\),
and \(H_p=xF_p\) has all odd frequencies from \(-2r+1\) through
\(2r+1\).  These sets partition the stated interval.  The equality
\(|H_p|=|F_p|\), the autocorrelation equality, the coefficient
profile, (12), self-reciprocity, and (13) are immediate.

For (14)--(15), every exponent of \(F'_p\) is

\[
                          2(i+pj).
\]

The base-\(p\) representation is unique, so these are precisely the
even exponents \(0,2,\ldots,2p^2-2\).  Every exponent of \(H'_p\) is

\[
  2p(p-1)+1+2i-2pj
    =1+2\bigl(p(p-1)+i-pj\bigr).
\]

For fixed \(j\), the expression in parentheses runs through an interval
of \(p\) consecutive integers; as \(j\) runs from \(p-1\) down to zero,
these intervals partition \(\{0,\ldots,p^2-1\}\).  Hence the support is
exactly the claimed set of odd exponents.  On the unit circle,
\(|V_p^\#|=|V_p|\), which proves (16) and the full autocorrelation
identity.  Finally, the coefficient of \(x\) in \(xF'_p\) is \(1\),
whereas the coefficient of \(x\) in \(H'_p\) is \(p\); hence the two
are not monomial translates.

For the finite certificate, put

\[
 U=1+x+x^3,\qquad V=1+x^2+x^3-x^4+x^7,
\]

and \(V^*(x)=x^7V(x^{-1})\).  Direct multiplication gives
\(F=UV\) and \(H=x^4UV^*\).  Therefore \(|F|=|H|\) on the unit
circle.  The displayed expansions verify both profiles and support
disjointness.  Reversing the coefficient vector of \(F\) shows that
it is not self-reciprocal.  QED.

## 2. Exact support accounting for the signed ruler

The support and multiplicity data from Lemma P47.1 give

\[
\begin{array}{c|c|c}
\text{polynomial}&\text{coefficient values}&\text{support size}\\ \hline
A=P P^\#&p\text{ once at }0,\ 1\text{ at every nonzero signed difference}
  &p(p-1)+1\\
B=x^G P^2&1\text{ on }p\text{ diagonals},\
  2\text{ on }\binom p2\text{ off-diagonals}
  &\binom{p+1}{2}.
\end{array}
\tag{17}
\]

Both coefficient sums and squared coefficient norms agree:

\[
 \sum_n a_n=\sum_n b_n=p^2,\qquad
 \sum_n a_n^2=\sum_n b_n^2=2p^2-p.
 \tag{18}
\]

Equation (18) is only the zero-lag shadow of (7); the lemma keeps every
lag.

There are two different support counts that must not be conflated.
The full disjoint Laurent supports have total cardinality

\[
 p(p-1)+1+\binom{p+1}{2}
       ={3p^2-p+2\over2}.
 \tag{19}
\]

But the positive difference labels and shifted unordered-sum labels
both lie in \([1,L]\), where \(L=G+2W\), and their total cardinality is

\[
        |D^+(Z)|+|S(Z)|
        =\binom p2+\binom{p+1}{2}=p^2.
 \tag{20}
\]

The zero difference is absent from (20): it is not one additional
positive label.  Also, diagonal sums contribute \(p\) support points,
not \(p\) off-diagonal coefficients of weight \(2\).  Forgetting either
point gives an incorrect uncertainty count.

The bare packing consequence of (20) is only \(L\geq p^2\).  Recovering
coefficient \(3\) requires leading-order information about the placement
of the two supports, equivalently a proof that the allowed phase shift
\(G\) is asymptotically as large as \(W\).  Identity (7) alone cannot do
this because it contains no \(G\).

For comparison with a standard polynomial uncertainty statement, multiply
both polynomials by \(x^W\):

\[
 \widehat A=x^WA,\qquad \widehat B=x^WB.
\]

They are ordinary polynomials with disjoint supports in
\([0,N]\), where

\[
                        N=L+W.
\]

The distinguished signed-ruler quantity is \(L=N-W\), not the ambient
polynomial degree.  Families (11) and (15) show that the bare analytic
hypotheses allow \(N=(2+o(1))p^2\).  They are therefore barriers to an
ambient-degree uncertainty principle, not counterexamples to the
one-sided signed-ruler statement.

## 3. What the coefficient-two families do and do not kill

Family (11) proves that the following data are jointly compatible with
endpoint \(2p^2-2p+1\):

* ordinary Laurent polynomials;
* nonnegative coefficients;
* disjoint coefficient supports;
* equal modulus at every point of the unit circle;
* equality of every aperiodic autocorrelation lag;
* a palindromic first polynomial;
* the exact \(p,1^{p(p-1)}\) profile of \(P P^\#\);
* the exact norms in (18).

Family (15) proves the same coefficient-two obstruction after excluding
the trivial monomial-shift ambiguity.

There are further exact losses.  Although the displayed coefficients are
nonnegative, family (11) is not asserted to be nonnegative as a function
on the unit circle, and the construction does not impose a p-point
Sidon-difference realization.  Family (15) is not self-reciprocal.  In the genuine pair,
\(A(e^{i\theta})=|P(e^{i\theta})|^2\geq0\), and both polynomials come from
the same sparse Newman factor.  These properties remain available to a
structured inequality.

Neither infinite family has the exact second profile in (17).  This is a
material loss, not cosmetic bookkeeping.  The finite \(p=3\) certificate
shows that even both multiplicity tables do not by themselves restore the
missing self-reciprocal orientation.  If an asymptotic family also had the
form

\[
                 P_ZP_Z^\#,\qquad x^G P_Z^2
\]

for a \(p\)-term Sidon Newman polynomial \(P_Z\), and had disjoint
supports with \(G+2W\leq(2+o(1))p^2\), then (6) would give an asymptotic
counterexample to the signed-ruler target itself.  No such family is
produced here.

Consequently, a theorem with only the generic hypotheses "equal modulus
and disjoint supports" is false at coefficient \(3\).  A viable theorem
must use at least the asymmetric second profile and the common sparse
spectral factor, and must be sensitive to the one-sided integer arc
\([0,W]\) and its winding relative to \(G\).

## 4. Why the Singer coefficient-two model is not an all-circle model

P15 gives Singer models in the cyclic ring of modulus

\[
                  m=2q,\qquad q=p^2-p+1.
\]

After cyclic reduction, they retain both exact profiles in (17), disjoint
supports, and equality of periodic autocorrelations.  Equivalently, the
two reduced polynomials have equal modulus at every \(m\)-th root of
unity.

For coefficient arrays supported in \(\{0,\ldots,m-1\}\), all-circle
equality is stronger: it is equivalent to equality of the aperiodic
autocorrelations at each integer lag.  Periodic autocorrelation combines
the aperiodic lags \(h\) and \(h-m\), so wrap terms can cancel a mismatch.
The exact P47 audit finds:

\[
\begin{array}{c|c|c|c|c}
p&m&\text{first absolute lag}&
  \operatorname{AC}_{\rm diff}&\operatorname{AC}_{\rm sum}\\ \hline
3&14&2&8&9\\
4&26&4&14&11\\
6&62&2&35&41.
\end{array}
\tag{21}
\]

Thus every tested reduced Singer pair fails the all-circle identity,
despite passing the complete finite-dual identity and both coefficient
profiles.  If instead one uses the unreduced ordinary products from
the even Singer lifts, all-circle equality returns, but the corresponding
small endpoints are

\[
 (p,L)=(3,27),(4,57),(6,127),
 \tag{22}
\]

not the cyclic moduli \(14,26,62\).  This is the exact wrap/arc distinction
that prevents the P15 coefficient-two cyclic family from answering the
P47 all-circle question.

## 5. Exact computation

The audit is in

    problems/864/compute/p47/audit_polynomial_phase.py

and writes

    problems/864/compute/p47/audit_results.json

Run it with

    python -B problems/864/compute/p47/audit_polynomial_phase.py

All operations are integer Laurent convolution.  The script checks:

* the five genuine signed rulers \(p=5,9,10,11,12\);
* formulas (1)--(8), including every aperiodic lag;
* the coefficient profiles, zero coefficient, diagonals, norms, and
  support disjointness;
* the first six Hadamard moments in (10);
* family (11) at \(p=3,4,6,10,50\);
* family (15) at \(p=3,4,10\);
* the finite exact-profile zero-flip certificate at \(p=3\);
* the periodic/aperiodic distinction (21) for the three small Singer
  models.

The stored signed-ruler lower halves for \(p=10,11,12\) were reversed to
\(W-Z\), as required by the P47 orientation.  No floating-point samples
are used.

## 6. Precise remaining analytic target

The all-circle equality is fully represented by (7)--(8), and the
coefficientwise exclusion is fully represented by (9).  Therefore a
coefficient-three continuation must prove a genuinely structured
inequality for the same \(p\)-term Newman factor, for example an
arc-sensitive estimate of the form

\[
 {\cal C}_{Z,G}\equiv0,\quad
 \operatorname{coeff}(A)=\{p,1^{p(p-1)}\},\quad
 \operatorname{coeff}(B)=\{1^p,2^{\binom p2}\}
 \quad\Longrightarrow\quad
 G\geq W-o(p^2).
 \tag{23}
\]

Together with the Sidon width scale, (23) would give the desired
\(G+2W\geq(3-o(1))p^2\).  Lemma P47.1 shows why (23) cannot be replaced
by a generic uncertainty principle, by scalar norms, by the phase
autocorrelation identity alone, or by finite-dual phase data.  No proof
of (23) is obtained here.
