# P29: the shifted four-Gauss-sum estimate

Status: **proved**.  The estimate (21a) holds uniformly, including every
coincident-frequency case.  Katz's hypergeometric bound applies when all
three output frequencies are nonzero.  Frequencies containing zero are the
only cancellation degeneracy and satisfy a stronger elementary bound.

## 1. Statement

Let `q>=2` be a prime power, put

    v=q^2+q+1,

and choose a primitive element `alpha` of `K=F_(q^3)`.  Let

    D={i in Z/vZ : Tr_(K/F_q)(alpha^i)=0}

be the trace-zero Singer difference set.  For a unit `u mod v` and
`a in Z/vZ`, put `C=uD-a`, let `f=1_C`, and use

    hat f(j)=sum_x f(x)e_v(-jx).

For `d in Z/vZ`, define

    G_(C,d)(x,y,z)=f(x)f(y)f(z)f(x+y+z-d).

Its Fourier transform is

    hat G_(C,d)(r,s,t)
      =1/v sum_k hat f(k)hat f(r-k)hat f(s-k)hat f(t-k)e_v(-kd).       (1)

### Theorem 1 (uniform shifted four-Gauss-sum bound)

For every prime power `q`, every affine Singer set `C=uD-a`, every `d`, and
every `(r,s,t)!=(0,0,0)` in `(Z/vZ)^3`,

    |hat G_(C,d)(r,s,t)| <= 12 q^(3/2).                              (2)

In particular, (21a) in P26 is true.  The constant is absolute, and no
separation assumption is needed on `r,s,t`.

The affine reduction is immediate.  Write

    x=uX-a,  y=uY-a,  z=uZ-a.

Then membership of `x+y+z-d` in `uD-a` is membership of

    X+Y+Z-u^(-1)(d+2a)

in `D`.  Hence, up to a unit complex phase,

    hat G_(C,d)(r,s,t)
      =hat G_(D,u^(-1)(d+2a))(ur,us,ut).                              (3)

It is therefore enough to prove (2) for `C=D`.

## 2. Frequencies containing zero

Write `F=hat(1_D)` and `p=q+1`.  Singer flatness, including its zero
coefficient, is the exact identity

    |F(k)|^2=q+v 1_(k=0),                                            (4)

because `p^2-q=v`.  Suppose first that `r=0`.  Applying (4) in (1) gives

    hat G_(D,d)(0,s,t)=q Q_(s,t)(d)+F(s)F(t),                         (5)

where Fourier inversion gives the concrete sum

    Q_(s,t)(d)
      =sum_(x,y in D; x+y=d) e_v(-sx-ty).                             (6)

The Singer set is strongly modular Sidon, so the congruence `x+y=d` has at
most two ordered solutions.  Thus `|Q_(s,t)(d)|<=2`.  If
`(0,s,t)!=(0,0,0)`, then at least one of `s,t` is nonzero and

    |F(s)F(t)| <= (q+1)sqrt(q).

Consequently

    |hat G_(D,d)(0,s,t)|
      <=2q+(q+1)sqrt(q)
      <=3q^(3/2).                                                     (7)

The variables are symmetric, so (7) treats every triple for which at least
one of `r,s,t` is zero.  This includes one zero, two zeros, a repeated pair
beside zero, and all permutations.  The excluded triple with three zeros is
the Fourier main term.

## 3. Singer coefficients as Gauss sums

It remains to assume

    r!=0,  s!=0,  t!=0.                                              (8)

Fix a nontrivial additive character `psi` of `F_q` and put

    Psi=psi o Tr_(K/F_q).

For a multiplicative character `chi` of `K^*`, write

    g(chi)=sum_(x in K^*) chi(x)Psi(x).

Let `X_0` be the group of multiplicative characters of `K^*` that are
trivial on `F_q^*`.  It has order `v`.  Index it by

    chi_j(alpha)=e_v(-j),     j in Z/vZ.

For `j!=0`, additive orthogonality on `F_q` gives

    F(j)=g(chi_j)/q.                                                  (9)

Indeed,

    (q-1)F(j)
      =sum_(x!=0; Tr(x)=0) chi_j(x)
      =1/q sum_(b in F_q) sum_(x!=0) chi_j(x)Psi(bx)
      =(q-1)g(chi_j)/q.

The `b=0` term vanishes because `chi_j` is nontrivial, and every `b!=0`
gives the same Gauss sum because `chi_j` is trivial on `F_q^*`.

Put

    A=chi_r,  B=chi_s,  C=chi_t.

The ordinary-Gauss model for (1) is

    M=1/(vq^4) sum_(chi in X_0)
        g(chi)g(A chi^(-1))g(B chi^(-1))g(C chi^(-1))chi(alpha^d).
                                                                         (10)

Outside the at most four characters for which one of

    chi, A chi^(-1), B chi^(-1), C chi^(-1)                            (11)

is trivial, (9) says that (10) agrees term by term with (1).

## 4. Katz's type-(3,1) bound

Let `X` be the group of all multiplicative characters of `K^*`, and set

    S(z)=sum_(chi in X)
      g(chi)g(A chi^(-1))g(B chi^(-1))g(C chi^(-1))chi(z).             (12)

Expanding the Gauss sums and using character orthogonality gives

    S(z)=(q^3-1)
      sum_(x_0,x_1,x_2,x_3 in K^*; z x_0=x_1x_2x_3)
      A(x_1)B(x_2)C(x_3)Psi(x_0+x_1+x_2+x_3).                         (13)

Put `y=-x_0`.  The constraint becomes `x_1x_2x_3=(-z)y`, and the
additive phase becomes `Psi(x_1+x_2+x_3-y)`.  Thus the inner sum in
(13), divided by `(q^3)^(3/2)`, is up to sign the Katz
hypergeometric trace

    Hyp_Psi((A,B,C);(1);-z).                                         (14)

Equivalently, the dual type-`(1,3)` description uses denominator tuple
`(A^(-1),B^(-1),C^(-1))` and argument `-z^(-1)`, up to a unit-modulus
factor.  Katz's hypergeometric-sheaf theorem applies because the numerator
tuple `(A,B,C)` and denominator tuple `(1)` are disjoint by (8).  The
resulting sheaf is pointwise pure of weight zero and has rank

    max(3,1)=3.

Therefore Deligne's weight bound gives, for every `z in K^*`,

    |S(z)| <= 3(q^3-1)(q^3)^(3/2).                                  (15)

Repetitions inside `(A,B,C)` are allowed: Katz's hypothesis only forbids a
character common to the numerator and denominator tuples.  Thus (15)
already includes `r=s`, `r=t`, `s=t`, and `r=s=t`, with no change in rank
or constant.

The restricted character sum in (10) is an average of (12).  Namely,

    1_(chi in X_0)=1/(q-1) sum_(b in F_q^*) chi(b),

and hence

    sum_(chi in X_0) (...)chi(alpha^d)
      =1/(q-1) sum_(b in F_q^*) S(b alpha^d).                         (16)

Combining (15), (16), `q^3-1=(q-1)v`, and (10) yields

    |M|
      <=3(q^3-1)(q^3)^(3/2)/(vq^4)
      =3(q-1)sqrt(q)
      <=3q^(3/2).                                                     (17)

## 5. Trivial-character correction

It remains only to restore the exceptional terms (11), since

    F(0)=q+1,          g(1)=-1.                                     (18)

For one exceptional value of the summation index, let `m` be the number
of trivial characters in (11).  Assumption (8) implies

    1<=m<=3.                                                         (19)

Singer flatness bounds the corresponding true product in (1) by

    (q+1)^m q^((4-m)/2) <= (q+1)^3 sqrt(q),                          (20)

whereas the product in the Gauss model (10), after division by `q^4`, is
at most

    q^(2-3m/2) <= sqrt(q).                                           (21)

There are at most four exceptional indices.  Since

    (q+1)^3 <= 2q(q^2+q+1)=2qv       for q>=2,

equations (20)-(21) give

    |hat G_(D,d)(r,s,t)-M|
      <=4sqrt(q)((q+1)^3+1)/v
      <=9q^(3/2).                                                     (22)

Together, (17) and (22) prove (2).

## 6. Exhaustion of collision cases

There are only two geometric strata.

1. At least one of `r,s,t` is zero.  The numerator character `1` then
   overlaps a denominator character; the exact identity (5) applies.
2. All of `r,s,t` are nonzero.  The numerator and denominator tuples are
   disjoint, regardless of repetitions within `(r,s,t)`; Katz gives (15).

Thus there is no unhandled coincident-frequency degeneracy and no symbolic
counterexample to (21a).  The naive `O(q^2)` triangle inequality misses the
type-(3,1) hypergeometric cancellation.

## 7. Finite audit (normalization only)

The script

    problems/864/compute/p29/audit_four_gauss_sum.py

was run for `q=2,3,5,7`, for every `d mod v` and every frequency triple.
It separately grouped all zero and coincidence patterns.  It checked (1),
(5), (9), and (16).  The largest identity residual was
`1.19e-7`; the maximum ordered modular sum multiplicity was `2` in every
field.  Full output is in

    problems/864/compute/p29/audit_results.json.

These finite checks audit signs and normalizations only; they are not used
as an asymptotic argument.  The asymptotic estimate is (15), supplied by
the hypergeometric-sheaf theorem.

## References

1. N. M. Katz, *Exponential Sums and Differential Equations*, Annals of
   Mathematics Studies 124, Princeton University Press, 1990, Definition
   8.2.7 and Theorem 8.4.2.
   https://doi.org/10.1515/9781400882434
2. P. Deligne, "La conjecture de Weil II," Publ. Math. IHES 52 (1980),
   137-252. https://doi.org/10.1007/BF02684780
3. E. Fouvry, E. Kowalski, P. Michel, "A study in sums of products,"
   Philos. Trans. Roy. Soc. A 373 (2015), Section 3.4.
   https://doi.org/10.1098/rsta.2014.0309
