# P35: Katz normalization and simplex-completion audit

Status: **complete, with one normalization correction to P29**.  P29's
shifted four-Gauss-sum estimate is valid.  In Katz's standard convention its
direct hypergeometric realization is type `(3,1)`, not the displayed
type `(1,3)` tuple in P29 (14).  The correction does not change the rank,
purity, collision cases, or constant.  The remaining non-wrapping
tetrahedron completion is also valid, with an explicit Fourier algebra
bound and exponent `K=5`.

Throughout, put

    p=q+1,             v=q^2+q+1,             Q=q^3,

and identify `Z/vZ` with its representatives `0,...,v-1`.  Fourier
transforms are unnormalized:

    hat h(r)=sum_x h(x)e_v(-rx).

## 1. Referee verdict on P29

The following parts of P29 are correct.

1. For `j!=0`, the Singer coefficient is
   `F(j)=g(chi_j)/q`.  The factor is `q^(-1)`, not `Q^(-1/2)`.
2. Projection from all characters of `K^*` to characters trivial on
   `F_q^*` is the exact average in P29 (16).
3. Katz's disjointness condition only forbids a character shared between
   the two tuples.  Multiplicities within one tuple are allowed.
4. The exceptional trivial-character correction in P29 (18)-(22) has the
   right powers of `q` and remains valid when `A,B,C` collide.
5. The elementary zero-output-frequency identity in P29 (5) is exact.

The only correction is the literal normalization of P29 (14).  A
convention-safe version is proved next.

## 2. Exact type-(3,1) normalization

Use Katz's normalized hypergeometric sum over a finite field of order `Q`:

    Hyp_Psi((eta_1,...,eta_n);(rho_1,...,rho_m);t)
      =(-1)^(n+m-1) Q^(-(n+m-1)/2)
        sum_(N(x)=t N(y))
          prod_i eta_i(x_i) prod_j overline(rho_j(y_j))
          Psi(T(x)-T(y)).                                      (1)

All variables in (1) are nonzero.  This is the normalization recalled in
Fouvry-Kowalski-Michel, Section 3.4, from Katz, Definition 8.2.7.

Let `A,B,C` be the nontrivial characters in P29 (8), and define

    S(z)=sum_chi
      g(chi)g(A chi^(-1))g(B chi^(-1))g(C chi^(-1))chi(z),       (2)

where the sum is over every multiplicative character of `K^*`.

### Lemma 2.1 (literal Katz identity)

For every `z in K^*`,

    S(z)=-(Q-1)Q^(3/2)
          Hyp_Psi((A,B,C);(1);-z).                              (3)

Consequently

    |S(z)| <= 3(Q-1)Q^(3/2).                                   (4)

#### Proof

Expanding the four Gauss sums in (2), character orthogonality gives

    S(z)=(Q-1) I(z),                                            (5)

where

    I(z)=sum_(z x_0=x_1 x_2 x_3)
      A(x_1)B(x_2)C(x_3)Psi(x_0+x_1+x_2+x_3).                  (6)

Put `y=-x_0`.  Then the constraint and additive phase become

    x_1 x_2 x_3=(-z)y,
    Psi(x_1+x_2+x_3-y).

Thus (6) is exactly the unnormalized type-`(3,1)` sum with numerator
tuple `(A,B,C)`, denominator tuple `(1)`, and argument `-z`.
Since `3+1-1=3`, (1) gives

    I(z)=-Q^(3/2) Hyp_Psi((A,B,C);(1);-z),

which proves (3).

The numerator and denominator tuples are disjoint because `A,B,C` are
nontrivial.  Katz, Theorem 8.4.2, therefore gives a pointwise pure
weight-zero sheaf, lisse on `G_m`, of rank `max(3,1)=3`.  Its trace at
every nonzero argument has absolute value at most `3`, proving (4).
QED.

For comparison, one can instead put `y_i=-x_i` for `i=1,2,3`.  Under
the convention (1), the resulting dual description is

    I(z)=-A(-1)B(-1)C(-1) Q^(3/2)
      Hyp_Psi((1);(A^(-1),B^(-1),C^(-1));-z^(-1)).              (7)

Thus P29's type-`(1,3)` wording has the right argument up to convention,
but the denominator characters must be inverted under (1).  Formula (3)
is the simpler direct normalization.

### Repeated denominator characters

In the dual form (7), collisions such as `A=B` are repeated denominator
characters.  In the direct form (3), they are repeated numerator
characters.  Katz's hypothesis is disjointness of the two tuples, counted
with multiplicity; it does not require entries within either tuple to be
distinct.  The repeated entries remain part of a length-three tuple, so
the rank is still `3`.  This covers `r=s`, `r=t`, `s=t`, and
`r=s=t`.

## 3. Restriction and exceptional characters

Let `X` be the character group of `K^*`, and let

    X_0={chi in X: chi restricted to F_q^* is trivial}.

For every `chi in X`, character orthogonality on `F_q^*` gives

    1_(chi in X_0)=1/(q-1) sum_(b in F_q^*) chi(b).             (8)

Multiplying (8) by the product of Gauss sums in (2) and by
`chi(alpha^d)` gives the exact identity

    sum_(chi in X_0) (...)chi(alpha^d)
      =1/(q-1) sum_(b in F_q^*) S(b alpha^d).                  (9)

Every argument on the right is nonzero, so (4), `Q=q^3`, and
`Q-1=(q-1)v` imply that the Gauss model `M` in P29 (10) satisfies

    |M|
      <= 3(Q-1)Q^(3/2)/(v q^4)
       = 3(q-1)sqrt(q)
      <= 3q^(3/2).                                            (10)

There is no missing factor `q-1` in the restriction.

It remains to compare the Gauss model to the true Singer coefficients.
The exceptional character values are the distinct elements of

    {1,A,B,C}.                                                  (11)

For one value `chi` in (11), let `m` be the number of trivial
characters among

    chi, A chi^(-1), B chi^(-1), C chi^(-1).                   (12)

Because `A,B,C` are nontrivial,

    1 <= m <= 3.                                               (13)

Singer flatness bounds the absolute value of the true product by

    p^m q^((4-m)/2) <= p^3 sqrt(q).                            (14)

On the other hand, `g(1)=-1` and every nontrivial Gauss sum over `K`
has magnitude `Q^(1/2)=q^(3/2)`.  After the factor `q^(-4)` in the
model, its exceptional product has magnitude

    q^(-4) Q^((4-m)/2)=q^(2-3m/2) <= sqrt(q).                  (15)

There are at most four distinct values in (11).  Therefore

    |hat G_(D,d)(r,s,t)-M|
      <= 4 sqrt(q)(p^3+1)/v
      <= 9q^(3/2),                                             (16)

where `p^3=(q+1)^3<=2qv` for `q>=2`.  Combining (10) and (16)
recovers P29's constant `12`.

For completeness, if `r=0`, Singer flatness gives directly

    hat G_(D,d)(0,s,t)=q Q_(s,t)(d)+F(s)F(t),                  (17)

where

    Q_(s,t)(d)=sum_(x,y in D; x+y=d) e_v(-sx-ty).

A modular Singer set has at most two ordered representations of any sum.
If `(0,s,t)!=(0,0,0)`, then

    |hat G_(D,d)(0,s,t)|
      <= 2q+p sqrt(q)
      <= 3q^(3/2).                                            (18)

Symmetry treats every output triple containing zero.  Equations
(3)-(18) therefore verify all strata of P29.

## 4. Fourier algebra of the non-wrapping tetrahedron

For a function `h` on `(Z/vZ)^k`, define its normalized Fourier
algebra norm by

    ||h||_A = v^(-k) sum_xi |hat h(xi)|.                       (19)

It satisfies

    ||h_1+h_2||_A <= ||h_1||_A+||h_2||_A,
    ||h_1 h_2||_A <= ||h_1||_A ||h_2||_A.                     (20)

The second inequality follows from
`hat(h_1 h_2)=v^(-k)(hat h_1 * hat h_2)`.

The Singer modulus `v=q^2+q+1` is odd.  Put

    n=(v-1)/2,          L_v=1+H_n,
    H_n=sum_(j=1)^n 1/j.                                      (21)

### Lemma 4.1 (interval pullbacks)

If `I` is a cyclic interval in `Z/vZ`, then

    ||1_I||_A <= L_v.                                         (22)

If `ell:(Z/vZ)^k -> Z/vZ` is a surjective homomorphism, then

    ||1_I o ell||_A = ||1_I||_A.                              (23)

#### Proof

Translation does not affect the norm, so take `I={0,...,ell_I-1}`.
For `1<=r<=n`,

    |hat(1_I)(r)|
      <= 1/|sin(pi r/v)|
      <= v/(2r).

Pairing `r` with `v-r` and treating `r=0` separately gives

    v^(-1) sum_r |hat(1_I)(r)|
      <= ell_I/v + sum_(r=1)^n 1/r
      <= L_v.

For (23), the Fourier transform of `1_I o ell` is supported on the
image of the injective dual map.  On that image its coefficients are
`v^(k-1) hat(1_I)(r)`; division by `v^k` proves equality.
QED.

For `0<=d<v`, define the non-wrapping tetrahedron

    T_d={(x,y,z) in {0,...,v-1}^3: x+y+z<d}.                  (24)

### Lemma 4.2 (explicit four-piece decomposition)

Uniformly in `0<=d<v`,

    ||1_(T_d)||_A <= 4 L_v^5.                                 (25)

#### Proof

The linear change of variables

    (a,b,c)=(x,x+y,x+y+z) mod v                               (26)

is an automorphism of `(Z/vZ)^3`.  The no-wrap condition in (24) is
equivalent, using standard representatives, to

    0 <= a <= b <= c < d.                                    (27)

For `d=0` there is nothing to prove.  For `d>=1`, put
`m=ceil(d/2)` and split

    I_0={0,...,m-1},             I_1={m,...,d-1},
    ell_0=m,                     ell_1=d-m,
    D_i={0,...,ell_i-1}.                                      (28)

Since `d<=v-1`, both block lengths are at most `n`.  With all
arguments below interpreted modulo `v`, the indicator of (27) is exactly

    1_I0(a)1_I0(b)1_I0(c)1_D0(b-a)1_D0(c-b)
  + 1_I0(a)1_I0(b)1_I1(c)1_D0(b-a)
  + 1_I0(a)1_I1(b)1_I1(c)1_D1(c-b)
  + 1_I1(a)1_I1(b)1_I1(c)1_D1(b-a)1_D1(c-b).                 (29)

Indeed, the four lines are the disjoint block patterns `000,001,011,111`.
Variables in different blocks are already ordered.  Within a block of
length at most `n<v/2`, the condition `u<=w` is exactly
`w-u mod v in D_i`; a negative ordinary difference lies in
`{v-ell_i+1,...,v-1}`, disjoint from `D_i`.

Each factor in (29) is an interval pulled back by a surjective linear
form.  Lemma 4.1 and (20) therefore bound the two five-factor lines by
`L_v^5` each and the two four-factor lines by `L_v^4` each.  Since
`L_v>=1`,

    ||1_(T_d)||_A <= 2L_v^5+2L_v^4 <= 4L_v^5.

The automorphism (26) preserves the Fourier algebra norm, proving (25).
QED.

The diagonal needed in P26 costs no additional logarithm.  Let

    Delta(x,y,z)=1_(x=y).

Its Fourier transform is

    hat Delta(r,s,t)=v^2 1_(r+s=0, t=0),

so

    ||Delta||_A=1.                                            (30)

For

    K_d=1_(T_d) Delta,

(20), (25), and (30) give

    ||K_d||_A <= 4L_v^5.                                      (31)

The two relevant cardinalities are

    |T_d|=binom(d+2,3),
    sum K_d=floor((d+1)^2/4).                                 (32)

The second identity counts pairs `(x,z)` with `2x+z<d`.

## 5. Completion theorem

Let `C` be any affine Singer set, let `f=1_C`, and put

    G_(C,d)(x,y,z)=f(x)f(y)f(z)f(x+y+z-d mod v).               (33)

Assume the P29 estimate with constant `B`:

    max_(xi!=(0,0,0)) |hat G_(C,d)(xi)| <= Bq^(3/2).           (34)

P29 proves (34) with `B=12`.

### Lemma 5.1 (zero mode)

For every `d`,

    |hat G_(C,d)(0,0,0)-p^4/v| <= 4q.                         (35)

#### Proof

Let

    R_C(d)=#{(x,y) in C^2: x+y=d mod v}.

For each `(x,y) in C^2`, the fourth-point condition asks for
`(w,z) in C^2` with `w-z=x+y-d`.  A Singer difference set has one
ordered representation of every nonzero difference and `p`
representations of zero.  Hence

    hat G_(C,d)(0,0,0)=p^2+(p-1)R_C(d).                       (36)

The difference property also implies `R_C(d)<=2`: two representations
of the same sum are identical or swaps.  Since `p-1=q` and
`p^2-v=q`,

    hat G_(C,d)(0,0,0)-p^4/v
      =q R_C(d)-q p^2/v.

Now `p^2/v<2`, which proves (35).
QED.

### Theorem 5.2 (uniform tetrahedral completion)

For every affine Singer set `C` and every `0<=d<v`,

    E_C(d)=E_0(d)+O(q^(3/2)(log q)^5),                         (37)

uniformly in `C` and `d`, where

    E_0(d)
      =rho^4/2 binom(d+2,3)
       +rho^3/2 floor((d+1)^2/4),       rho=p/v.               (38)

More explicitly, if (34) holds, then

    |E_C(d)-E_0(d)|
      <= 4B q^(3/2)L_v^5+5q.                                 (39)

With P29's `B=12`, the right side is

    48q^(3/2)(1+H_((v-1)/2))^5+5q.                            (40)

#### Proof

For any weight `W` on `(Z/vZ)^3`, Fourier inversion gives

    sum_x G_(C,d)(x)W(x)
      =v^(-3) sum_xi hat G_(C,d)(xi)hat W(-xi).                (41)

Separate the zero frequency.  By (34),

    |sum_x G_(C,d)(x)W(x)
       -v^(-3)hat G_(C,d)(0)hat W(0)|
      <= Bq^(3/2)||W||_A.                                    (42)

Taking `W=1_(T_d)`, equations (25), (32), (35), and
`rho^4 v^3=p^4/v` yield

    |E_C^ord(d)-rho^4 binom(d+2,3)|
      <= 4Bq^(3/2)L_v^5+4q.                                  (43)

The diagonal term in P26 is exactly

    T_diag(d)=sum_x G_(C,d)(x)K_d(x).

Taking `W=K_d` and using (31), (32), and (35) gives

    |T_diag(d)-rho^4 floor((d+1)^2/4)|
      <= 4Bq^(3/2)L_v^5+4q.                                  (44)

P26's zero-mode expression uses `rho^3`, rather than `rho^4`, on the
diagonal because `f(x)^2=f(x)`.  This adjustment is smaller than the
claimed error:

    (rho^3-rho^4) floor((d+1)^2/4)
      <= rho^3 v^2
       = p^3/v
      <= 2q,                                                   (45)

where `p^3<=2qv` for `q>=2`.

Finally,

    E_C(d)=(E_C^ord(d)+T_diag(d))/2.

Combining (43)-(45) proves (39).  Since
`L_v<=2+log v` and `v=q^2+q+1`, (37) follows with `K=5`.
QED.

## 6. Computational audit

The script

    problems/864/compute/p35/audit_simplex_decomposition.py

was run with

    --max-v 15

for every odd `v=3,5,...,15` and every `0<=d<v`, a total of `63`
tetrahedra.  It checked (29), both cardinalities in (32), the interval
bound (22), `||Delta||_A=1`, (25), and (31).  All checks passed.  The
largest observed ratio of the tetrahedron norm to the right side of (25)
was `0.0142262762`.  The complete output is in

    problems/864/compute/p35/audit_results.json.


The unmodified P29 normalization audit was also rerun with

    --q 2 3

The largest Fourier-identity residual was `7.55e-14`, the largest subgroup
projection residual was `1.43e-11`, and the maximum ordered modular-sum
multiplicity was `2`.  Its output is in

    problems/864/compute/p35/p29_recheck.json.

This finite audit checks the identities and normalization only.  The
asymptotic argument is the proof of Lemmas 4.1-5.1 and Theorem 5.2.

## 7. Final disposition

P29's theorem and constant survive independent review.  Its displayed
hypergeometric tuple should be replaced by the exact type-`(3,1)`
formula (3), or by the dual formula (7) with inverse denominator
characters.  There is no remaining simplex-completion gap: (29) supplies
an explicit four-piece carry/order decomposition, (25) gives its
normalized Fourier algebra norm, and Theorem 5.2 proves STM with `K=5`.

## References

1. N. M. Katz, *Exponential Sums and Differential Equations*, Annals of
   Mathematics Studies 124, Princeton University Press, 1990, Definition
   8.2.7 and Theorem 8.4.2.
   https://doi.org/10.1515/9781400882434
2. E. Fouvry, E. Kowalski, P. Michel, "A study in sums of products,"
   *Philosophical Transactions of the Royal Society A* 373 (2015),
   Section 3.4.
   https://people.math.ethz.ch/~kowalski/sums-of-products.pdf
