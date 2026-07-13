# P32: Primary-source audit for (3,1)-sum-free Sidon sets and Singer fourth moments

Status: primary-source gate completed 2026-07-12.  This file audits exact
theorem statements; it does not use survey assertions as evidence.

## 1. Audit verdict

Let `E` be a finite set of positive integers.  Here

* `E` is Sidon means that `a+b=c+d`, with repetitions allowed, implies
  `{a,b}={c,d}` as multisets;
* `3E={a+b+c:a,b,c in E}`, again with repetitions allowed; and
* the target extra condition is `E intersect 3E = empty`.

The integer-source verdict is negative: none of the proved theorems below
gives the interval/span asymptotic `M=(3+o(1))|E|^2` for same-parity Sidon
sets satisfying `E intersect 3E=empty`.  Bajnok--Ruzsa Conjecture 3.3 has the
numerical constant `1/sqrt(3)`, but it is an unproved conjecture about strong
4-independence in the cyclic group `Z_n`, not this interval problem.

The finite-field verdict is different.  Evans--Hollmann--Krattenthaler--Xiang
Theorem 2.1 supplies the exact Singer/Gauss identity, and Rojas-Leon Theorem 4
supplies a field-uniform `O(Q^(-1/2))` normalized fourth moment.  Projecting
from all characters of `F_(q^3)^*` to the characters trivial on `F_q^*`
gives

    max_(r,s,t) != (0,0,0) |hat G_d(r,s,t)| = O(q^(3/2))              (A)

uniformly in `d`, including coincident frequencies.  Frequencies having a
zero coordinate reduce to a two-factor identity and also satisfy (A).
Thus these primary sources, together with the Fourier-completion reduction
already stated in P26, **supply STM** for trace-zero Singer sets and their
affine/reflected copies.  STM then forces the Singer/cut lane to coefficient
`3`; it does not prove coefficient `3` for arbitrary integer `E`, and it does
not settle Erdos #864.

## 2. Terminology is not interchangeable

### 2.1 Exact equivalence in the odd positive subcase

[Bajnok--Ruzsa, Definition 1.1](https://arxiv.org/pdf/1512.03037#page=3)
calls `A` *t-independent* when every integer relation

    sum_(a in A) lambda_a a = 0,     sum |lambda_a| <= t,

is trivial.  Repetitions are therefore allowed.  If every member of `E` is
positive and odd, then

    E is 4-independent over Z
    iff E is Sidon and E intersect 3E is empty.                       (1)

Indeed, positivity removes zero-sums, parity removes all one-versus-two
relations, Sidonicity removes two-versus-two relations, and the remaining
one-versus-three relation is exactly `E intersect 3E`.

The same statement is false for an arbitrary same-parity set.  For example,
`{2,4}` is Sidon and disjoint from its threefold sumset, but `4=2+2`, so it
is not 4-independent.  Consequently, strong 4-independence is a sufficient
condition for the target, and is equivalent only in the positive odd case.

### 2.2 Source-by-source meaning of the aliases

| Source term | Exact source condition | Relation to the target |
|---|---|---|
| `(3,1)-sum-free` | `3A intersect A=empty`, all summands allowed to repeat | Exact extra equation, but no Sidon condition |
| `sum-free Sidon` (Nathanson) | Sidon and `S intersect 2S=empty` | Different equation; for odd `S`, the sum-free part is automatic |
| `weakly t-independent` (Bajnok--Ruzsa) | coefficients only in `{-1,0,1}` | Repeated summands are omitted, so it does not imply `E intersect 3E=empty` |
| `sum-free Sidon` in `F_2^t` (Czerwinski--Pott) | distinct-term characteristic-two convention | Cannot encode the repeated relation `x=y+y+y` |
| `Sidon` in Hare--Yang | Fourier interpolation on a dual group | Not additive `B_2` uniqueness |

The example `E={1,3}` is weakly `t`-independent for every `t` under
Bajnok--Ruzsa Definition 5.1, but fails the target because `3=1+1+1`.
Thus "weakly sum-free Sidon" is not a safe synonym when the target permits
repeated summands.

## 3. Integer primary sources

### 3.1 Bajnok--Ruzsa: strong and weak independence

Primary source: Bela Bajnok and Imre Z. Ruzsa,
["The independence number of a subset of an abelian group"](https://arxiv.org/pdf/1512.03037),
*Integers* **3** (2003), A02.  The paper is also hosted by the
[journal](https://www.emis.de/journals/INTEGERS/papers/d2/d2.pdf).

Exact hypotheses and constants:

1. Definition 1.1, pp. 3--4: `t`-independence uses arbitrary integer
   coefficients of total `l_1` norm at most `t`; equivalently, sums contain
   not-necessarily-distinct terms.  Its conditions include
   `hA intersect kA=empty` for `1<=h<k` and `h+k<=t`, and uniqueness of all
   `h`-term sums for `h<=floor(t/2)`.
2. [Corollary 3.2](https://arxiv.org/pdf/1512.03037#page=16): for every
   `epsilon,delta>0` and all sufficiently large `n`,

       (1/sqrt(8)-epsilon)sqrt(n) <= s(Z_n,4)
                                      <= (1/sqrt(2)+delta)sqrt(n),
       (1/sqrt(15)-epsilon)sqrt(n) <= s(Z_n,5)
                                      <= (1/sqrt(2)+delta)sqrt(n).

3. [Conjecture 3.3](https://arxiv.org/pdf/1512.03037#page=16) states, but
   does not prove,

       lim_(n to infinity) s(Z_n,4)/sqrt(n) = 1/sqrt(3).

4. [Definition 5.1 and Theorem 5.2](https://arxiv.org/pdf/1512.03037#page=19)
   restrict weak independence to coefficients in `{-1,0,1}` and prove, for
   every finite abelian group `G` of order `n` and every `t>=2`,

       (t! n / 2^t)^(1/t) - t/2
          < w(G,t)
          < (floor(t/2)! n)^(1/floor(t/2)) + t/2.

Applicability: the proved cyclic bounds bracket strong 4-independence between
constants `1/sqrt(8)` and `1/sqrt(2)`.  They neither prove the conjectural
constant nor impose the target's same-parity interval geometry.  The weak
theorem omits precisely the repeated triple `x=y+y+y`.  No proved result in
this paper implies interval coefficient `3`.

### 3.2 Bajnok: the exact `(3,1)` problem without Sidonicity

Primary source: Bela Bajnok,
["On the maximum size of a (k,l)-sum-free subset of an abelian group"](https://arxiv.org/pdf/0803.4486),
*International Journal of Number Theory* **5** (2009), 953--971,
[DOI 10.1142/S1793042109002481](https://doi.org/10.1142/S1793042109002481).

The definition on p. 2 is `kA intersect lA=empty`, where `hA` uses
not-necessarily-distinct terms.  [Theorem 6](https://arxiv.org/pdf/0803.4486#page=4)
proves for every `n>1`

    lambda_(3,1)(Z_n)
      = max_(d|n, d != 2 mod 4) floor((d+2)/4) n/d
      = ((p+1)/p)n/4,

if `n` has a prime divisor `p=3 mod 4` and `p` is the smallest such prime,
and equals `floor(n/4)` otherwise.  Consequently

    n/5 <= lambda_(3,1)(Z_n) <= n/3,

with lower equality for `n in {5,10}` and upper equality when `3|n`.

Applicability: this is the exact repeated-summand exclusion, but its extremal
sets have positive density and need not be Sidon.  The `1/3` here is a cyclic
density, not the span coefficient `3` for a square-root-size Sidon set.  The
theorem neither supplies nor falsifies that coefficient or STM.

### 3.3 Calkin--Taylor: enumeration of `E intersect kE=empty`

Primary source: Neil J. Calkin and Angela C. Taylor,
["Counting sets of integers, no k of which sum to another"](https://www.math.clemson.edu/~calkin/Papers/calkin_taylor.pdf),
*Journal of Number Theory* **57** (1996), 323--327,
[DOI 10.1006/jnth.1996.0051](https://doi.org/10.1006/jnth.1996.0051).

[Theorem 1](https://www.math.clemson.edu/~calkin/Papers/calkin_taylor.pdf#page=4)
fixes `k>=3`, permits the `x_i` to repeat, and proves that a constant `c_k`
exists such that the number of subsets of `[1,n]` with no solution
`x_1+...+x_k=y` is at most

    c_k 2^((k-1)n/k).

For `k=3` this is exactly enumeration of sets disjoint from `3E`, without a
Sidon hypothesis.  It gives neither a maximum-cardinality constant on the
Sidon scale nor a minimum span, so it does not imply coefficient `3`.

### 3.4 Nathanson: "sum-free Sidon" means `S intersect 2S=empty`

Primary source: Melvyn B. Nathanson,
["N-graphs, modular Sidon and sum-free sets, and partition identities"](https://arxiv.org/pdf/math/0002173),
*Ramanujan Journal* **4** (2000), 59--67,
[DOI 10.1023/A:1009830023023](https://doi.org/10.1023/A:1009830023023).

Section 2, p. 4, defines sum-free by `S intersect 2S=empty` and Sidon by
unique two-term sums with diagonal pairs included.  Theorem 1 assumes that
`S` is sum-free Sidon modulo `m` and proves a partition identity.  It places
no `S intersect 3S` condition and no interval extremal constant.  In
particular, oddness makes Nathanson's sum-free condition automatic, while
the target triple exclusion remains open.

### 3.5 Characteristic two is a non-transferable convention

Primary source: Ingo Czerwinski and Alexander Pott,
["Sidon sets, sum-free sets and linear codes"](https://arxiv.org/pdf/2304.07906),
*Advances in Mathematics of Communications* **18** (2024), 549--566,
[DOI 10.3934/amc.2023054](https://doi.org/10.3934/amc.2023054).

[Definition 3.1 and Propositions 3.4--3.5](https://arxiv.org/pdf/2304.07906#page=10)
work in `F_2^t`, define sum-free by `m_1+m_2 != m_3`, and prove

    smax(F_2^t) = sfsmax(F_2^t) + 1

by adjoining/removing `0`.  Their Sidon convention uses four pairwise
distinct elements, as forced by characteristic two.  With repetitions,
every nonempty `E subset F_2^t` violates `E intersect 3E=empty`, since
`x=x+y+y`.  Hence the coding bounds do not transfer to the integer target
and do not imply coefficient `3` or STM.

### 3.6 Harmonic-analysis "independent Sidon" is another collision

Primary source: Kathryn E. Hare and Robert (Xu) Yang,
["Sidon sets are proportionally Sidon with small Sidon constants"](https://arxiv.org/pdf/1808.03128),
*Canadian Mathematical Bulletin* **62** (2019), 798--809,
[DOI 10.4153/S0008439518000620](https://doi.org/10.4153/S0008439518000620).

Their Proposition 1 defines Sidonicity by Fourier interpolation (equivalently
an `l_1`-to-sup norm inequality), not by unique pair sums.  Definition 2
defines `n`-degree independence by bounding each coefficient separately by
`n`.  [Proposition 2](https://arxiv.org/pdf/1808.03128#page=6) assumes that
the discrete group has no nontrivial elements of order at most `n`, that
`E` excludes the identity, and that every `E_k={gamma^k:gamma in E}` for
`1<=k<=n` is harmonic Sidon; it then gives an unspecified `delta_n>0` such that every
finite `F subset E` contains an `n`-degree-independent `H` with
`|H|>=delta_n|F|`.  Theorem 2 specializes this proportional statement to
torsion-free groups.

No numerical lower bound for `delta_n` is stated, and neither "Sidon" nor
the resulting proportional subset is the additive interval object here.
This source does not imply coefficient `3`.

## 4. Singer and Gauss-sum primary sources

### 4.1 Exact Singer Fourier normalization

Primary source: Ronald Evans, Henk D. L. Hollmann, Christian Krattenthaler,
and Qing Xiang,
["Gauss Sums, Jacobi Sums, and p-Ranks of Cyclic Difference Sets"](https://arxiv.org/pdf/math/9807029),
*Journal of Combinatorial Theory, Series A* **87** (1999), 74--119,
[DOI 10.1006/jcta.1998.2950](https://doi.org/10.1006/jcta.1998.2950).

[Theorem 2.1 and its proof](https://arxiv.org/pdf/math/9807029#page=4) take
`L` to be representatives for `F_q^*` in `F_(q^d)^*`, chosen so trace maps
`L` into `{0,1}`, and put `L_0={x in L:Tr(x)=0}`.  They prove that `L_0` is
a difference set in `F_(q^d)^*/F_q^*` with parameters

    v=(q^d-1)/(q-1),
    k=(q^(d-1)-1)/(q-1),
    lambda=(q^(d-2)-1)/(q-1).

For every nontrivial multiplicative character `chi` of `F_(q^d)^*` that is
trivial on `F_q^*`, the proof gives the exact identity

    g(chi) = q chi(L_0),       |chi(L_0)|^2=q^(d-2).          (2)

For `d=3`, write `Q=q^3`; then `v=q^2+q+1`, `p=k=q+1`, and a nonzero
Fourier coefficient of an affine Singer copy `C` has the form

    hat f(a) = phase(a) q^(-1) g(chi_a),
    |hat f(a)|=sqrt(q),                                      (3)

where `f=1_C`.  Affine multiplication, translation, and reflection only
permute frequencies and add unit phases.

Equation (2) is a one-character/two-point identity.  By itself it gives only
the `O(q^2)` triangle-inequality bound for the shifted fourth moment, not (A).

### 4.2 Rojas-Leon: the required uniform fourth-moment input

Primary source: Antonio Rojas-Leon,
["Equidistribution and independence of Gauss sums"](https://arxiv.org/pdf/2207.12439),
*Advances in Mathematics* **450** (2024), article 109762,
[DOI 10.1016/j.aim.2024.109762](https://doi.org/10.1016/j.aim.2024.109762).

The exact hypotheses used here are as follows.

1. [Theorem 1](https://arxiv.org/pdf/2207.12439#page=2) fixes `r`, nonzero
   exponent vectors `a_i=mu_i b_i in Z^r` with primitive `b_i`, characters
   `eta_i`, and twists `t_i`.  In the rational vector space whose basis is
   the character set, put

       v_i = sum_(xi^(mu_i)=eta_i) xi.

   For each primitive `b`, it assumes that the `v_i` with `b_i=b` are
   linearly independent.  Under this hypothesis the normalized Gauss-sum
   tuples equidistribute.
2. [Theorem 4 and its proof](https://arxiv.org/pdf/2207.12439#page=14) make
   this uniform while the field, characters, and twists vary.  Fix `A>0`;
   let finite-field sizes `Q_m` tend to infinity; require
   `max_j |a_(m,i,j)|<=A` and Theorem 1's independence for every `m`.
   For every fixed nonzero Fourier monomial `c in Z^n`, and
   `Q=Q_m>1+nA`, the displayed proof bound is

       | |S|^(-1) sum_(chi in S) Lambda_c(Phi(chi)) |
       <= [C(r) N(r)^(||c||-1) A^(||c||) (Q-1)^r Q^(-1/2)
             + nA (Q-1)^(r-1)]
          /[(Q-1)^(r-1)(Q-1-nA)].                           (4)

   Here `S` omits characters for which a Gauss factor is trivial;
   `C(r)` and `N(r)` are absolute field-independent constants supplied by
   the cited quantitative sheaf estimates.  They are not numerically
   evaluated in the paper.

For this audit, `r=1`, `A=1`, `n<=4`, and `||c||=4`, so (4) is uniformly
`O(Q^(-1/2))`.  This quantitative rate, rather than qualitative
equidistribution alone, is what reaches the exponent in (A).

Katz's earlier [Theorems 9.5--9.6](https://web.math.princeton.edu/~nmk/Katz-GKM.pdf#page=84)
in *Gauss Sums, Kloosterman Sums, and Monodromy Groups* (Annals of
Mathematics Studies 116, 1988) already allow the `r` distinct character
shifts to vary with the field.  If a nontrivial torus monomial has positive
exponents `n_i` on an index set `A` and negative exponents `-m_j` on `B`,
Theorem 9.6 gives the exact uniform estimate

    |integral chi d mu_(F_Q,psi;xi_1,...,xi_r)|
      <= max(sum_(i in A)n_i, sum_(j in B)m_j)/sqrt(Q)
           + 2r/(Q-1).                                  (K9.6)

Its stated tuple uses one common additive character and has no independent
multiplicative twists `chi(t_i)`.  The subgroup projection and cut phase
below introduce just such a twist.  Rojas-Leon Theorem 4 explicitly permits
field-varying `t_i`, while retaining the `O(Q^(-1/2))` rate.  Thus Katz 9.6
is the earlier quantitative no-twist antecedent, not by itself the cited
supplier for the twisted Singer correlation.

## 5. Transfer to the Singer four-character correlation

This section records the transfer, because neither primary source states it
in Singer-cut notation.

Let `X` be the character group of

    F_(q^3)^*/F_q^*,       |X|=v=q^2+q+1,

and identify its characters with the characters of `F_(q^3)^*` trivial on
`F_q^*`.  For `f=1_C`, P26 equation (21) is

    hat G_d(r,s,t)
      = v^(-1) sum_k hat f(k)hat f(r-k)hat f(s-k)hat f(t-k)e_v(-kd).
                                                                    (5)

### 5.1 All of `r,s,t` nonzero

Away from the at most four indices where a factor in (5) is `hat f(0)`,
(3) turns the summand, up to unit phases, into `q^(-4)` times

    g(chi) g(eta_r chi^(-1))
           g(eta_s chi^(-1)) g(eta_t chi^(-1)).              (6)

Coincident shifts are grouped: for each distinct `h` among `r,s,t`, the
factor `g(eta_h chi^(-1))` is assigned multiplicity `c_h`.  The Rojas-Leon
data are therefore

    (eta,a,c)=(1,+1,1),
    (eta_h,-1,c_h),       sum_h c_h=3.                        (7)

All primitive directions in (7) are `b=+1`.  Their vectors in Theorem 1
are the character-basis elements `1` and `eta_h^(-1)`.  Because each `h` is
nonzero and the grouped `h` are distinct, these basis elements are linearly
independent.  Thus Theorem 4 applies even when two or three of `r,s,t`
coincide; the fixed moment vector has `||c||=4`.

The restriction to `X` is imposed by the exact projection identity

    sum_(chi in X) F(chi)
      = 1/(q-1) sum_(u in F_q^*)
          sum_(chi in dual(F_(q^3)^*)) chi(u)F(chi).           (8)

The factors `chi(u)` and `e_v(-kd)`, as well as the affine phases in (3),
are allowed twists in Rojas-Leon Theorem 4.  Put `Q=q^3`.  Equation (4)
says that each inner normalized fourth-moment average in (8) is
`O(Q^(-1/2))`.  There are `Q-1+O(1)` characters, while a raw product of four
nontrivial Gauss sums has scale `Q^2`; hence

    sum_(chi in X) (the raw product (6)) = O(Q^(5/2))
                                               = O(q^(15/2)). (9)

Using the four factors `q^(-1)` in (3) and `v asymp q^2` in (5), (9) gives

    v^(-1) q^(-4) O(q^(15/2)) = O(q^(3/2)).                  (10)

The omitted indices have `hat f(0)=p=q+1` and every nonzero coefficient has
magnitude `sqrt(q)`.  The worst coincidence has three zero factors and one
nonzero factor, contributing

    v^(-1) p^3 sqrt(q) = O(q^(3/2)).                          (11)

Thus (10) remains valid uniformly through all coincident nonzero shifts.

### 5.2 At least one of `r,s,t` is zero

Suppose `r=0`; the other cases are symmetric.  The Singer difference-set
identity gives

    hat f(k)hat f(-k)=q  for k!=0,
    hat f(0)^2=p^2.

Consequently (5) becomes exactly

    hat G_d(0,s,t)
      = q T_d(s,t) + (p^2-q)v^(-1)hat f(s)hat f(t),           (12)

where

    T_d(s,t)=v^(-1)sum_k hat f(s-k)hat f(t-k)e_v(-kd).

After `j=s-k` and Fourier orthogonality,

    T_d(s,t)=unit phase *
       sum_(x+y=d mod v) f(x)f(y)e_v(-(t-s)y).                (13)

A modular Sidon set has at most two ordered representations of a fixed sum:
two different representations would give the same nonzero difference and
must be swaps.  Hence `|T_d(s,t)|<=2`.  Since `(r,s,t)!=(0,0,0)`, at least
one of `s,t` is nonzero; using `|hat f(0)|=p` and
`|hat f(a)|=sqrt(q)` for `a!=0`, the correction in (12) is at most
`O(q^(3/2))`.  Therefore every zero-coordinate case also satisfies (A).

### 5.3 STM and coefficient classification

Equations (10)--(13) prove (A) for trace-zero Singer difference sets and all
affine/reflected copies, with an absolute implied constant for sufficiently
large `q`.  This is exactly P26's sufficient estimate (21a), uniformly in
`d` and in every frequency-coincidence pattern.

P26 states that Fourier completion of the integral tetrahedron costs only a
fixed polylogarithmic factor.  Combining that reduction with (A) gives, for
each fixed `epsilon>0`,

    E_C(d)=E_0(d)+O_epsilon(q^(3/2)(log q)^K)
    uniformly for epsilon v <= d < v,                         (STM)

for some fixed `K`.  Since P26 computes

    E_0(d)=d^3/(12v^2)+O_epsilon(q)=Omega_epsilon(q^2),

STM makes `E_C(d)>0` for every macroscopic `d` and all sufficiently large
`q`.  Hence Singer carry holes have `d=o(v)`, and P26's complement formula
gives `M=(3-o(1))p^2` in this Singer lane.

Classification of the audit finding:

* **Supplies STM:** yes, after the explicit primary-source transfer above
  and P26's already-recorded Fourier completion.
* **Falsifies STM:** no.  The cited moment theorem proves the needed bound.
* **Implies coefficient 3:** yes for Singer affine/cut constructions only.
* **Implies coefficient 3 for all same-parity integer target sets:** no.
* **Resolves Erdos #864:** no; it closes the positive Singer-mixing branch
  of P26's dichotomy and rules out macroscopic Singer carry holes.

## 6. Theorem-level novelty ledger

| Primary result | Exact output | Coefficient 3? | STM? |
|---|---|---:|---:|
| Bajnok--Ruzsa Cor. 3.2 | proved cyclic strong-4 bounds `1/sqrt(8)` and `1/sqrt(2)` | No | N/A |
| Bajnok--Ruzsa Conj. 3.3 | conjectural cyclic constant `1/sqrt(3)` | Conjecture only; not the interval target | N/A |
| Bajnok Thm. 6 | exact density of `(3,1)`-sum-free subsets of `Z_n` without Sidon | No | N/A |
| Calkin--Taylor Thm. 1 | at most `c_k 2^((k-1)n/k)` solution-free subsets | No | N/A |
| Nathanson Thm. 1 | partition identity for `S intersect 2S=empty` plus Sidon | No | N/A |
| Czerwinski--Pott Props. 3.4--3.5 | characteristic-two sum-free Sidon/code equivalence | No transfer | N/A |
| Hare--Yang Prop. 2 / Thm. 2 | proportional harmonic Sidon/degree-independence, unspecified `delta_n` | No | N/A |
| Evans et al. Thm. 2.1 | `g(chi)=q chi(L_0)` and Singer flatness | No by itself | No by itself |
| Katz Thms. 9.5--9.6 | varying distinct shifts; bound (K9.6), but no independent twists | No by itself | No by itself |
| Rojas-Leon Thm. 4 + projection (8) | uniform shifted fourth moment `O(q^(3/2))` | Singer lane: yes | Yes |

The source-level novelty conclusion is deliberately narrow: no audited
integer theorem states the same-parity Sidon interval result, while the 2024
Rojas-Leon quantitative theorem supplies the previously named finite-field
frontier after a short quotient projection.  The Singer application and the
zero-coordinate reduction are deductions recorded here, not claims made in
either primary paper.

The repeat gate used the exact queries `Rojas-Leon Singer difference set`,
`Equidistribution and independence of Gauss sums Singer`, and
`four Gauss sums Singer difference set`.  They returned no direct Singer-cut
application.  This records those queries and is not an exhaustive
nonexistence claim.
