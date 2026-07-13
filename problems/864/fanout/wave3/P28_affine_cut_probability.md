# P28: affine-cut probability and its lower-tail obstruction

Status: two exact lemmas are proved.  First, arbitrary affine translations
can be used without losing the SCG target: a carry zero at any fixed
`d/v=theta>1/3` normalizes to a valid Singer cut and implies `SCG(2/3)` for
all sufficiently large parameters.  Second, translation averaging has a
positive cubic main term of order `q^2`, with an error `O(q log^3 v)`.
Consequently the ordinary first-moment method cannot produce a zero.  The
translation variance is an exact eight-Fourier-factor expression, and the
usual second-moment inequality controls zeros in the wrong direction.  No
infinite family and no falsification of SCG is proved here.

## 1. Setup

Let `D` be a Singer `(v,p,1)` difference set, where

    p=q+1,                 v=q^2+q+1.

For a unit `u mod v` and an arbitrary `b mod v`, put

    C_{u,b}:={ [u x+b]_v : x in D } subset {0,...,v-1}.

Write `Delta(C)` for the ordinary positive-difference set of `C`.  Since
`C` is a perfect difference lift, `Delta(C)` contains exactly one of `h`
and `v-h` for every `1<=h<v`.

For `0<d<v`, use the ordered version of P26's complement violation count:

    E_C^ord(d)
      := #{(alpha,beta) in C^2 : alpha+beta<d,
             d-alpha-beta notin Delta(C)}.

P26, (14), gives the exact tetrahedral form

    E_C^ord(d)
      = sum_{x+y+z<d}
          1_C(x)1_C(y)1_C(z)1_C(v-d+x+y+z).               (1)

All variables in (1) are ordinary representatives in `[0,v-1]`; the last
argument also lies in `[0,v-1]`.  Thus `E_C^ord(d)=0` is exactly the carry
containment event, not a modular relaxation.

## 2. Arbitrary translations reduce to genuine cuts

### Lemma 2.1 (normalization invariance)

Let `C subset {0,...,v-1}`, let `m=min C`, and put

    C_0:=C-m.

If `2m<d<v`, then

    E_C^ord(d)=E_{C_0}^ord(d-2m).                          (2)

#### Proof

Translation by `-m` preserves every positive difference.  Under
`alpha'=alpha-m`, `beta'=beta-m`, one has

    alpha+beta<d  iff  alpha'+beta'<d-2m,

and

    d-alpha-beta=(d-2m)-alpha'-beta'.

This is a bijection between the two sets counted in the definition.  QED.

We also need a uniform bound on cyclic gaps.  Let `G(C)` be the largest
difference between consecutive points of `C` around the cyclic order,
including the wrap gap.  Write `H_n=sum_{j=1}^n 1/j`.

### Lemma 2.2 (explicit affine Singer gap bound)

Every affine Singer image satisfies

    G(C) <= 1 + (v sqrt(q)/p) H_{(v-1)/2}.                 (3)

In particular `G(C)/v=O(q^(-1/2) log q)`, uniformly in `u,b`.

#### Proof

For every nonzero frequency `r mod v`, the perfect-difference identity
gives

    |hat(1_C)(r)|=sqrt(q).

If `I` is a cyclic interval, Fourier inversion and

    |hat(1_I)(r)| <= 1/|sin(pi r/v)| <= v/(2r)

for `1<=r<=(v-1)/2` give

    ||C intersect I|-p|I|/v|
      <= sqrt(q) H_{(v-1)/2}.                              (4)

The interior of a cyclic gap of length `g` is an empty interval of length
`g-1`.  Applying (4) to that interval yields

    p(g-1)/v <= sqrt(q) H_{(v-1)/2},

which is (3).  QED.

### Proposition 2.3 (fixed-level affine zero implies SCG)

Fix a real number

    1/3 < theta < 1/2.                                    (5)

Suppose that for infinitely many prime powers `q` there are a unit `u` and
an arbitrary translation `b` such that, for

    d=floor(theta v),

one has

    E_{C_{u,b}}^ord(d)=0.                                 (6)

Then `SCG(2/3)` holds for those parameters.  Hence P26, Proposition 4.1,
gives an infinite admissible counterfamily to the proposed constant.

#### Proof

Let `m=min C`, `x=max C`, and `C_0=C-m`.  Both empty end intervals belong
to the cyclic wrap gap, so

    m <= G(C),                 x >= v-G(C).                (7)

By (3), `G(C)=o(v)`.  Thus `d_0=d-2m` lies in `(0,v)` for all sufficiently
large `q`, and Lemma 2.1 gives `E_{C_0}^ord(d_0)=0`.

Put `L=x-m` and reflect the normalized cut:

    B:=L-C_0.

This is again an affine Singer cut, with the same positive-difference set.
P26's complement identity gives a literal hole at

    M:=v+2L-d_0.

Indeed `0<d_0<v` gives `2L<M<v+2L`.  Its top-layer residue is

    t:=M-2v
      =2(x-m)-v-(d-2m)
      =2x-v-d.                                             (8)

Using (7), (3), and (5),

    t >= v-d-2G(C) > 0

for all sufficiently large `q`, while `x<=v-1` gives

    t <= v-d-2 < 2v/3.

Thus `0<=t<=floor(2v/3)`, and the hole is exactly an SCG witness.  QED.

Proposition 2.3 is useful because it permits averaging over all `v`
translations, rather than only the `p` translations that visibly send a
Singer point to zero.  Normalization converts any successful affine image
back into one of the allowed cuts.

## 3. Exact translation averaging

Use the Fourier convention

    hat f(r)=sum_x f(x)e_v(-rx).

For fixed `u`, let `f_b=1_{C_{u,b}}`, and let `G_{d,b}` be P26's complete
four-point function

    G_{d,b}(x,y,z)
      =f_b(x)f_b(y)f_b(z)f_b(x+y+z-d mod v).

P26, (21), says

    hat G_{d,b}(r,s,t)
      =(1/v) sum_k
        hat f_b(k)hat f_b(r-k)hat f_b(s-k)hat f_b(t-k)e_v(-kd).   (9)

Translation gives

    hat f_b(a)=e_v(-ab)hat f_0(a).

Since `v` is odd, averaging (9) over all `b mod v` leaves the unique

    k=(r+s+t)/2 mod v.                                    (10)

Therefore the following identity is exact.

### Lemma 3.1 (translation-averaged shifted correlation)

For every `r,s,t`, with `k` as in (10),

    E_b hat G_{d,b}(r,s,t)
      =(1/v) hat f_0(k)hat f_0(r-k)hat f_0(s-k)hat f_0(t-k)e_v(-kd).  (11)

If `(r,s,t)!=(0,0,0)`, at most two of the four frequencies on the
right of (11) are zero.  Consequently Singer flatness gives the uniform
bound

    |E_b hat G_{d,b}(r,s,t)|
      <= p^2 q/v < q+1.                                   (12)

At zero frequency, (11) is exactly `p^4/v`.

#### Proof

The translation phase in a summand of (9) is

    e_v(-b(r+s+t-2k)).

Orthogonality over `b` proves (10)-(11).  If three of
`k,r-k,s-k,t-k` vanish, their defining equations force all four to vanish
and hence `(r,s,t)=0`.  At a nonzero triple there are therefore at most two
zero frequencies.  The zero Fourier coefficient of `f_0` is `p`, and every
nonzero one has magnitude `sqrt(q)`.  The largest possible product is
`p^2 q`; division by `v` proves (12).  QED.

For completeness, let

    T_d={(x,y,z) in {0,...,v-1}^3:x+y+z<d}.

The standard lattice-simplex completion bound is

    (1/v^3) sum_{r,s,t}|hat(1_{T_d})(r,s,t)|
      =O((1+log v)^3),                                    (13)

uniformly in `d<v`.  One direct proof expands the three nested geometric
sums.  Away from coincident frequencies the four vertex-cone terms are
products of three factors `|1-e_v(a)|^{-1}`; summing uses
`sum_{a=1}^{v-1}|1-e_v(a)|^{-1}=O(v log v)`.  On the one- and
two-dimensional coincidence loci, take the corresponding limits; the lost
denominator is replaced by a factor at most `v`, while the number of free
frequencies drops by one.  These strata satisfy the same bound.

Combining (11)-(13) with three-dimensional Fourier inversion proves the
main averaging statement.

### Theorem 3.2 (positive affine-translation mean)

Uniformly in the multiplier `u` and in `0<d<v`,

    (1/v) sum_{b mod v} E_{C_{u,b}}^ord(d)
      = (p/v)^4 binom(d+2,3)
        + O((q+1)(1+log v)^3).                             (14)

For fixed `d/v=theta>0`, the right side is

    (theta^3/6+o(1)) q^2.                                 (15)

#### Proof

Equation (1) is the inner product of `1_{T_d}` and `G_{d,b}`.  The zero
frequency in (11) contributes

    v^(-3) |T_d| p^4/v
      =(p/v)^4 binom(d+2,3).

Bound every nonzero frequency by (12) and apply (13).  This proves (14),
and (15) follows from `p=q+1`, `v=q^2+q+1`.  QED.

This theorem is distinct from P26's pointwise frontier.  P26 asks for
uniform cancellation in one fixed cut.  Here translation orthogonality
really does remove the shifted four-phase sum, but only after averaging the
whole random variable.

## 4. Why the probability route does not presently yield a zero

The random variable in Theorem 3.2 is a nonnegative integer.  At every
fixed macroscopic level, its mean tends to infinity like `q^2`.  Therefore
the only first-moment criterion that forces a zero,

    E E_C^ord(d) < 1,

fails by a quadratic factor.  Translation averaging proves that a typical
total mass is positive; it does not force an empty carry fibre.

The exact Fourier series in the translation variable makes the second-
moment obstruction equally explicit.  Write

    E_{C_{u,b}}^ord(d)=sum_{ell mod v} c_{u,d}(ell)e_v(-ell b).

Fourier inversion in (9) gives

    c_{u,d}(ell)
      =v^(-4) sum_{r,s,t,k: r+s+t-2k=ell}
        hat(1_{T_d})(-r,-s,-t)
        hat f_0(k)hat f_0(r-k)hat f_0(s-k)hat f_0(t-k)e_v(-kd).  (16)

Hence Parseval gives the exact variance

    Var_b(E_{C_{u,b}}^ord(d))
      =sum_{ell!=0}|c_{u,d}(ell)|^2.                       (17)

After expanding the square, (17) is an eight-Fourier-factor, or
eight-Gauss-sum, correlation.  Flat magnitudes again do not determine it.
Moreover even a sharp variance estimate has the wrong logical direction:
Paley-Zygmund gives

    Pr(E_C^ord(d)>0)
      >= (E E_C^ord(d))^2 / E[(E_C^ord(d))^2],             (18)

while Chebyshev only gives an upper bound on the zero probability.  Neither
inequality gives the positive lower bound on `Pr(E_C^ord(d)=0)` required by
SCG.

There is also an exact granularity barrier.  On the affine sample space

    (Z/vZ)^* x Z/vZ,

every nonempty event has probability at least

    1/(v phi(v)).                                          (19)

Thus a Janson-style weak-dependence estimate

    Pr(E_C^ord(d)=0) <= exp(-c q^a)                        (20)

for any fixed `c,a>0` would, for all sufficiently large `q`, be smaller
than (19) and would prove that there are no zeros at that level.  In other
words, ordinary Poisson/Janson behavior would falsify the fixed-level route
to SCG rather than prove it.  The finite zeros must come from a structured
lower-tail atom, not from weakly dependent rare events.

## 5. Precisely quantified remaining probability target

For fixed `theta in (1/3,1/2)`, define

    Z_q(theta)
      :=#{(u,b) in (Z/vZ)^* x Z/vZ:
           E_{C_{u,b}}^ord(floor(theta v))=0}.              (21)

Proposition 2.3 shows that the concrete statement

    Z_q(theta)>=1 for infinitely many prime powers q       (APZ_theta)

implies `SCG(2/3)` and therefore disproves the proposed Erdos-864 constant.
By (19), this is equivalently the lower-tail bound

    Pr(E_C^ord(floor(theta v))=0) >= 1/(v phi(v))           (22)

infinitely often.

Theorem 3.2 says that the random variable in (22) has mean
`(theta^3/6+o(1))q^2`.  Formula (17) says that its variance already requires
an eight-Gauss-sum correlation.  Thus the smallest genuinely new estimate
for the probabilistic lane is not another marginal or flat-spectrum bound:
it is either

1. a structured mechanism producing the atom (22), or
2. a lower-tail/anti-concentration theorem strong enough to show
   `Pr(E=0)<1/(v phi(v))`, which would rigorously kill `APZ_theta`.

Neither estimate is proved here.  The exact q=167 zeros in P26 show that
the atom can occur at finite parameters, while Theorem 3.2 shows why
ordinary affine averaging does not force it.  This is the rigorous
obstruction requested for the probability/averaging attack.

