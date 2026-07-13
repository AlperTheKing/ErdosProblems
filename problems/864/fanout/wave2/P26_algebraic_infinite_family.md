# P26: algebraic infinite-family lane

Status: exact complement and tetrahedral carry reductions isolated; no
infinite family is proved. The proposed quadratic mixing main is not the
Fourier zero mode. A corrected fourth-order mixing lemma is the frontier.

## 1. Setup

For an integer `r`, let `[r]_n` be its least residue in `{0,...,n-1}`.  A set
`C subset Z/nZ` is *strongly modular Sidon* if all residues

    c_i+c_j (mod n),       c_i,c_j in C, c_i <= c_j,

are distinct, with diagonals included.  Fix a unit `u mod n` and a point
`a in uC`, and make the cyclic lift

    B=B(u,a):={ [uc-a]_n : c in C } subset {0,...,n-1}.

Thus `0 in B`.  Write `L=max(B)`, and define

    S(B)       := {x+y : x,y in B, x<=y},
    Delta+(B)  := {z-w : z,w in B, z>w},
    Sigma_0(B) := {x+y   : x,y in B, x<=y, x+y<n},
    Sigma_1(B) := {x+y-n : x,y in B, x<=y, x+y>n}.

Diagonals `x=y` occur in `S`, `Sigma_0`, or `Sigma_1`.  If `B` is strongly
modular Sidon, `x+y=n` cannot occur: it would collide modulo `n` with the
pair `0+0`.  Integer equality of two pair sums implies modular equality, so
every such lift is also literal Sidon.

The main family below is Singer.  If `q` is a prime power, put

    n=q^2+q+1.

For a primitive `gamma in F_(q^3)`, the projective trace-zero exponent set

    D_q := {i mod n : Tr_(F_(q^3)/F_q)(gamma^i)=0}

has `q+1` elements and is a perfect `(n,q+1,1)` cyclic difference set.  The
definition is well-defined modulo `n`, since `gamma^n in F_q^*` and trace
zero is invariant under `F_q^*` scaling.  See Singer [1] and the modern
finite-field description in Meszaros-Ronyai-Szabo [2].

A perfect difference set is strongly modular Sidon.  Indeed, from

    c_1+c_2 = c_3+c_4 (mod n)

one gets `c_1-c_3=c_4-c_2`.  If this residue is nonzero, uniqueness of the
ordered difference gives `(c_1,c_3)=(c_4,c_2)`; if it is zero, the two pairs
are equal directly.  This also audits diagonal/off-diagonal collisions.

For a Singer lift, `p:=|B|=q+1` and

    n=p^2-p+1.                                             (1)

Moreover `Delta+(B)` contains exactly one member of every pair `{d,n-d}`,
`1<=d<n`.  This sign-selector fact is the useful extra structure Singer has
over the Bose-Chowla and Ruzsa families.

## 2. Exact carry formula

Define the top-carry correlation

    R_B(t) := #{s in Sigma_1(B) : s>t and n+t-s in Delta+(B)}

for `0<=t<n`.

### Lemma 2.1 (both carry layers)

For every normalized strongly modular Sidon B subset [0,n-1] with 0 in B and every 0<=t<n, one has

    n+t in S(B)+Delta+(B)

if and only if at least one of the following holds:

    (i)  some s in Sigma_0(B) has s>t and n+t-s in Delta+(B);
    (ii) some s in Sigma_1(B) has s<t and t-s in Delta+(B).

For the top layer,

    2n+t in S(B)+Delta+(B)  iff  R_B(t)>0.                 (2)

#### Proof

Take an actual unordered pair sum `x+y` and `d in Delta+(B)`.  Write

    x+y = kappa*n+s,       kappa in {0,1}, 0<=s<n,
    s+d = j*n+t,           j in {0,1},     0<=t<n.

Then

    x+y+d = (kappa+j)n+t.                                  (3)

For layer `n+t`, either `(kappa,j)=(0,1)`, when
`d=n+t-s in [1,n-1]` is equivalent to `s>t`, or
`(kappa,j)=(1,0)`, when `d=t-s>0` is equivalent to `s<t`.
For layer `2n+t`, necessarily `(kappa,j)=(1,1)`, and
`d=n+t-s<n` is equivalent to `s>t`.  These are exactly the stated
conditions.  No pair with `d=0` is admitted, and diagonal pair sums remain
present throughout.  QED.

For the affine Singer lift, equation (2) has a completely explicit exponent
form.  Put `x_r=[u c_r-a]_n`.  A potential hit satisfies

    u(c_1+c_2+c_3-c_4)-2a = t (mod n),                    (4)

but it hits `2n+t` over the integers only when

    x_1<=x_2,  x_3>x_4,  x_1+x_2>n,
    x_1+x_2+x_3-x_4=2n+t.                                 (5)

The case `c_1=c_2` is allowed.  Thus (4), which finite-field algebra sees,
is not enough: (5) is the exact cyclic-order/carry condition it must also
control.

## 3. Reflected admissibility, including diagonals

### Lemma 3.1

Let `B subset [0,L]` be literal Sidon with `0,L in B`.  If

    M>2L  and  M notin S(B)+Delta+(B),                     (6)

then

    A_0 := B union (M-B)

has size `2|B|`, and its only repeated unordered sum is `M`, with exactly
`|B|` representations.

#### Proof

Condition `M>2L` makes the two blocks disjoint.  Sums internal to the low
block are `S(B)<M`; sums internal to the high block are `2M-S(B)>M`.
Literal Sidonicity makes both classes simple, including their diagonal sums.

A cross sum is `M+b-b'`.  Its nonzero differences are simple because a
repeated positive difference would give a repeated pair sum in `B`.  The
`|B|` choices `b=b'` give the exceptional sum `M`.  A low internal sum `s`
collides with a cross sum `M-d` exactly when `M=s+d`; reflecting gives the
same criterion for high internal sums and cross sums `M+d`.  These are all
possible cross-class collisions, and (6) excludes them.  QED.

## 4. Conditional negative target

### Singer carry-gap lemma `SCG(2/3)`

There are infinitely many prime powers `q` for which, with
`n=q^2+q+1` and the trace-zero Singer set `D_q`, there exist

    u in (Z/nZ)^*,
    a in uD_q,
    t in {0,...,floor(2n/3)}

such that, for `B=B(u,a)`,

    R_B(t)=0.                                               (SCG)

Equivalently, there is no quadruple `c_1,c_2,c_3,c_4 in D_q` satisfying
(5), where the `x_r` are the affine/cut representatives above.  This is a
finite-field/carry lemma with no hidden asymptotic clause: its only
quantifiers are `q,u,a,t` and the four trace-zero exponents.  It remains
unproved.

The multiplier may be omitted for the stronger deterministic natural-cut
version.  The P12 natural-cut data support that stronger `2/3` version at all
26 stored parameters, but no uniform theorem follows from those finite data.

### Proposition 4.1 (`SCG(2/3)` gives an infinite counterfamily)

Assume `SCG(2/3)`.  For every supplied `q`, set

    p=q+1,       M=2n+t.

The Singer property makes `B` literal Sidon.  Since `L<n`,

    M>=2n>2L.

By (2) and `R_B(t)=0`, condition (6) holds.  Lemma 3.1 therefore makes
`A_0=B union (M-B)` admissible with `|A_0|=2p`.  From (1),

    M <= 2n+floor(2n/3) <= 8n/3
      < 8p^2/3 = (3-1/3)p^2.                              (7)

Translating `A_0` by `1` puts it in `[1,M+1]` without changing sum
multiplicities.  Along the infinite sequence,

    limsup F(N)/sqrt(N)
      >= liminf 2p/sqrt(M+1)
      >= sqrt(3/2)
      > 2/sqrt(3).                                         (8)

Thus `SCG(2/3)` alone disproves the conjectured asymptotic, with the explicit
margin `epsilon=1/3` in (7).  No further structural or density lemma is
needed.

The complement formulation below shows what a uniform mixing theorem would
have to rule out. In particular, SCG(2/3) forces a macroscopic complement
parameter d; the corrected mixing lemma STM would make that impossible.

## 5. Complement Mixing And Its Exact Obstruction

### 5.1 Complement Containment

Let B subset [0,L] be a Singer lift, put

    C:=L-B,       Delta:=Delta+(B)=Delta+(C),

and suppose 2L<M<v+2L. Define

    d:=v+2L-M,       so 0<d<v.                             (COMP)

For alpha<=beta in C, the corresponding pair in B has sum
2L-alpha-beta, and

    M-(2L-alpha-beta)=v-d+alpha+beta.

If alpha+beta>=d, this is at least v and hence is not in Delta. If
alpha+beta<d, put h=d-alpha-beta. The Singer sign-selector property says
exactly one of h,v-h lies in Delta. Therefore

    M notin S(B)+Delta

if and only if

    {d-alpha-beta : alpha<=beta in C, alpha+beta<d}
        subset Delta.                                      (12)

This includes the diagonal alpha=beta. Define the violation count

    E_C(d):=#{(alpha,beta): alpha<=beta in C,
              alpha+beta<d, d-alpha-beta notin Delta}.      (13)

Thus a reflected hole in this branch is exactly E_C(d)=0.

### 5.2 Exact Tetrahedral Identity

Let E_C^ord(d) count ordered pairs in (13), so off-diagonal pairs count
twice. For h=d-alpha-beta, the condition h notin Delta means that the
unique modular difference representation of h wraps across the cut.
Equivalently, there is a unique delta in C with

    0<=delta<h,       gamma:=delta+v-h in C.

Consequently

    E_C^ord(d)
      = sum_{alpha+beta+delta<d}
          1_C(alpha)1_C(beta)1_C(delta)
          1_C(v-d+alpha+beta+delta).                        (14)

This is an exact four-point correlation over a tetrahedron, not a product of
two independent densities. If T_diag(d) is the same sum with alpha=beta,
then

    E_C(d)=(E_C^ord(d)+T_diag(d))/2.                         (15)

Put rho=p/v. The all-zero Fourier contribution to (15) is

    E_0(d)
      = (rho^4/2) binom(d+2,3)
        +(rho^3/2) floor((d+1)^2/4).                        (16)

For d=theta v and fixed theta>0, its leading term is

    E_0(d) = d^3/(12v^2)+O(q),                              (17)

not d^2/(8v). The latter expression takes the low-pair main and multiplies
by a global 1/2 sign density. The relevant sign is a wrap event: for a
difference residue h, its smooth probability is h/v, not 1/2.

### 5.3 What Singer Flatness Proves Uniformly

For every affine cut C, Singer flatness gives

    |hat(1_C)(r)|=sqrt(q)       for r nonzero mod v.

Indeed, the perfect-difference identity is
1_C*1_(-C)=q delta_0+1_(Z/vZ); applying a nontrivial character gives the
displayed magnitude. Interval Fourier inversion therefore gives the uniform discrepancy

    ||C intersect I|-rho|I|| = O(sqrt(q) log v)             (18)

for every cyclic interval I. Let D_0 denote the right side of (18).
Summing interval counts and using partial summation proves, uniformly in
1<=d<v,

    #{alpha<=beta in C: alpha+beta<d}
      = rho^2 d^2/4+O(p D_0),                               (19)

and

    #{1<=h<=d: h notin Delta}
      = rho^2 d^2/2+O(p D_0).                               (20)

For (20), pair h notin Delta with the unique positive difference
v-h=gamma-delta: for each delta<d, count gamma in
C intersect [v-d+delta,v), an interval of length d-delta. The proof of (19)
is the analogous sum of |C intersect [0,d-alpha)| over alpha<d.

Both errors are O(q^(3/2) log v). In particular, the selector-complement
density inside [1,d] is smoothly d/(2v), not 1/2. Equations (19) and (20)
are only marginal estimates. They do not control their pointwise convolution
(13); the same-cut dependence is exactly (14).

### 5.4 Fourier Phase Obstruction

Use hat f(r)=sum_x f(x)e_v(-rx) and let f=1_C. Define the complete modular
four-point function

    G_d(x,y,z):=f(x)f(y)f(z)f(x+y+z-d mod v).

Its three-dimensional Fourier transform is exactly

    hat G_d(r,s,t)
      = (1/v) sum_k hat f(k)hat f(r-k)hat f(s-k)hat f(t-k)e_v(-kd).
                                                               (21)

At zero frequency, perfect differences give the exact complete count

    hat G_d(0,0,0)=p^2+(p-1)r_C+C^ord(d)=p^4/v+O(q),

because every nonzero difference has one ordered representation and the zero
difference has p. Strong modular Sidonicity gives r_C+C^ord(d)<=2.

Flatness specifies the magnitude of each factor in (21), but not the phases
of this shifted fourth moment. Taking absolute values gives only O(q^2) for
a nonzero coefficient, the same order as the total number of points. An
O(q^(3/2) polylog q) simplex discrepancy requires new cancellation in (21).
A sufficient concrete finite-field estimate is

    max_{(r,s,t) nonzero} |hat G_d(r,s,t)| = O(q^(3/2)),    (21a)

uniformly in d and in all coincident-frequency cases. Standard Fourier
completion of the integral simplex then costs only polylogarithmic factors.

For a trace-zero Singer set, nontrivial hat f(k) is, up to convention,
q^(-1) times a Gauss sum over F_(q^3). Thus the missing input is a uniform
shifted four-Gauss-sum correlation bound, including coincident-frequency
cases. The usual flat character-sum identity is only a two-point statement
and does not supply this bound.

### 5.5 Corrected Mixing Frontier STM(epsilon)

A sufficient positive obstruction would be: for every fixed epsilon>0,
some fixed exponent K and all Singer affine cuts,

    E_C(d)=E_0(d)+O_epsilon(q^(3/2)(log q)^K)                (STM)

uniformly for epsilon v<=d<v. By (17), the main is
Omega_epsilon(q^2), so STM would imply E_C(d)>0 for all sufficiently large
q. Every Singer hole would then have d=o(v). Since v/p^2->1 and Section 6.2
gives L/p^2->1, (COMP) would force

    M=v+2L-d=(3-o(1))p^2.                                  (22)

Hence STM, if proved, is the sharp obstruction explaining why all finite
Singer ratios must drift to 3. It remains unproved; equation (21) is the
precise missing finite-field lemma.

## 6. Why modular and range arguments stop

### 6.1 Modular Saturation Is Automatic

For a Singer perfect difference set,

    D_q-D_q = Z/nZ.

Consequently

    3D_q-D_q = 2D_q+(D_q-D_q) = Z/nZ.                     (9)

Hence a modular `3D-D` hole never exists.  The full modular coverage stored
in every P12 record is not a finite accident; (9) proves it for the whole
Singer family.  Any successful algebraic proof must distinguish the carry in
(5), not merely solve or avoid congruence (4).

### 6.2 The Endpoint Hole Has Sharp Coefficient 3

For every normalized `B subset [0,L]` with `0,L in B`, diagonals give

    2L=L+L in S(B),       L=L-0 in Delta+(B).

Thus `3L in S(B)+Delta+(B)`, while every integer above `3L` is absent.  The
first hole forced solely by endpoint range is therefore exactly

    M_range=3L+1.                                          (10)

There may be earlier correlation holes, but no endpoint argument can certify
one.

The classical interval Sidon upper bound gives

    p <= sqrt(L+1)+O(L^(1/4)),

so a `p`-point Singer lift, for which `L<=n=p^2-p+1`, satisfies
`L/p^2 -> 1`; see for example the explicit modern bound in [3].  Therefore

    (3L+1)/p^2 -> 3.                                       (11)

This proves the precise drift-to-3 obstruction for pure span/range
separation.  It does **not** prove that the first genuine carry hole drifts to
3; the fourth-order estimate STM is the missing uniform input.

## 7. Family Comparison

The same carry identity applies to every strongly modular lift scanned in
P12.

* Bose-Chowla uses `q` residues in `Z/(q^2-1)` represented by exponents
  `e` with `theta^e-theta in F_q`.  The even modulus in many parameters means
  strong modular diagonals must be checked rather than inferred.
* Ruzsa uses `p-1` residues in `Z/(p(p-1))`, with CRT coordinates

      c_i = ip-(p-1)g^i (mod p(p-1)).

  Its carry is an inequality for the chosen CRT representative, while its
  modular equation mixes the index and discrete exponential.
* Singer has odd modulus and perfect differences.  Therefore every affine
  lift is strongly modular Sidon and `Delta+` is an exact one-of-two sign
  selector.  This removes two auxiliary lemmas and leaves only the
  one-dimensional tail correlation `R_B(t)`, so Singer is the cleanest
  theorem lane.

The selected Bose, Ruzsa, and Singer examples all pass the same independent
carry audit below, but no uniform Bose or Ruzsa carry theorem was found.

## 8. Exact Audit And Falsifier

The independent standard-library checker is

    problems/864/compute/p26/carry_audit.py

Run from the repository root with

    python problems/864/compute/p26/carry_audit.py --output problems/864/compute/p26/carry_audit.json

It imports no P12 checker.  For each selected lift it constructs literal
`S(B)+Delta+(B)`, constructs both sides of Lemma 2.1 independently as
bitsets, compares them for all `n` residues in both carry layers, and runs a
fresh unordered-sum census on `B union (M-B)`.

Verified output in `carry_audit.json`:

1. All 40 candidate records in `verification_all_recheck.json` pass both
   all-residue carry identities and the reflected census.  Every audited lift
   has a top-layer hole with `t<=floor(2n/3)`.
2. The natural Singer residues were reconstructed at the 26 parameters

       37,41,43,47,49,53,59,61,64,67,71,73,79,81,
       83,89,97,101,103,107,109,113,121,125,127,128.

   Every cyclic cut was rescanned.  At every parameter, at least one cut has
   a top-layer hole by `t=floor(2n/3)`.
3. The worst best ratio in those natural scans is the endpoint `q=128`:

       p=129, n=16513, t=10821, M=43847,
       t/n=10821/16513, M/p^2=43847/16641.

   Exactly 3 of its 129 cuts have a hole by `floor(2n/3)=11008`.

### Exact falsifier to the half-window natural-cut lemma

The tempting strengthening

> For every prime power `q`, some cyclic cut of the unmultiplied trace-zero
> Singer set has `R_B(t)=0` for `0<=t<=floor(n/2)`

is false for the exact `q=128` Singer representative in
`singer_natural_xlarge.jsonl`.  The audit checks all 129 cuts and finds

    cuts with a hole for 0<=t<=8256: 0.

Thus cut averaging alone cannot establish a universal `1/2` threshold.  This
falsifier does not cover all affine multipliers: P12 sampled 32 of 7056 unit
classes at `q=128`, and its best sampled affine lift has

    u=800, a=109, t=9816, M=42842,
    t/n=9816/16513, M/p^2=42842/16641.

That affine value is also independently accepted by the P26 carry audit, but
it is finite evidence only.

### Complement-Mixing Audit At q=167

The independent complement checker is

    problems/864/compute/p26/mixing_audit.py

Run it with

    python -B problems/864/compute/p26/mixing_audit.py --output problems/864/compute/p26/mixing_audit.json

The stored output mixing_audit.json verifies (12), (14), and
(15) literally for both stored q=167 candidates. The independent P12 carry
checker also accepted all nine new records. Across the eight q=131,...,167
sampled records, d/v ranges from 5084/18907=0.268895... to
6547/17293=0.378592.... The 512-multiplier scan
improves the construction record to

    p=168, v=28057, L=27697, u=9828, a=407,
    M=73386, M/p^2=4077/1568=2.60012755...,
    d=10065, d/v=10065/28057.

There are 473 low unordered pairs in (12), all 473 satisfy the containment,
and E_C(d)=0. The proposed quadratic main is 451.332; the tetrahedral zero
mode is 111.979.

All 168 cuts of this same multiplier were then tested at four fixed d.
Every cut has the same flat Fourier magnitudes, but the joint counts vary:

| d/v | minimum | maximum | mean | d^2/(8v) | E_0(d) |
|---|---:|---:|---:|---:|---:|
| 1/4 | 0 | 100 | 47.96 | 219.18 | 38.30 |
| 1/3 | 6 | 178 | 105.01 | 389.65 | 90.00 |
| 1/2 | 91 | 535 | 333.89 | 876.72 | 301.06 |
| 2/3 | 323 | 1048 | 753.79 | 1558.61 | 710.46 |

The finite means track the cubic tetrahedral scale, not the independent-half
quadratic scale. More importantly, at d=floor(v/4), identical flat spectra
coexist with counts from 0 to 100. This is an exact falsifier to any argument
that treats flat Fourier magnitudes alone as the needed joint mixing
statement. It is not an asymptotic falsifier to STM, whose allowed error at
this q can exceed the displayed main.

## 9. Frontier Verdict

No infinite negative construction and no uniform mixing theorem is
established. The exact dichotomy is now:

* SCG(2/3) would produce an infinite counterfamily with epsilon=1/3.
* STM(epsilon) would force every Singer affine/cut hole to coefficient 3.

The proposed d^2/(8v) estimate is not the Fourier zero-mode formula. Singer
flatness proves the two marginals (19) and (20), but the required joint
estimate is the tetrahedral four-point correlation (14), equivalently the
shifted four-Gauss-sum phase bound (21). This is the precise surviving
finite-field/carry lemma. Modular saturation, endpoint range, and the
cut-only half-window claim are separately obstructed by (9), (11), and the
exact q=128 falsifier.

## References

1. J. Singer, "A theorem in finite projective geometry and some applications
   to number theory," Trans. AMS 43 (1938), 377-385.
   https://doi.org/10.1090/S0002-9947-1938-1501951-4
2. T. Meszaros, L. Ronyai, T. Szabo, "Singer difference sets and the
   projective norm graph," 2019. https://arxiv.org/abs/1908.05591
3. J. Balogh, Z. Furedi, S. Roy, "An upper bound on the size of Sidon sets,"
   2021. https://arxiv.org/abs/2103.15850


### Full affine q=167 scan

The complete scan over all 14,028 unit classes and all 168 cuts per class
finished after the sampled scans. It checked 2,356,704 affine lifts and found

    p=168, v=28057, u=1932, cut base=23141,
    L=26765, M=72728, M/p^2=9091/3528.

The independent literal verifier returns a reflected set of size 336 whose
only repeated sum is (72728,168). In complement coordinates,

    d=v+2L-M=8859,
    d/v=8859/28057.

There are 488 low unordered pairs alpha<=beta with alpha+beta<d; their
488 excesses are distinct and all lie in Delta+(B), so E_C(d)=0 exactly.
This is a stronger finite record, not an asymptotic counterfamily. It is
consistent with STM because q=167 is finite and d/v is about 0.3158.
