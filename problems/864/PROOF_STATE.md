# Proof State

Status: novelty gate and wave-1 discovery.

Completed:
- exact statement and conventions frozen;
- official open status checked;
- Erdos-Freud lower constant recorded;
- elementary sqrt(2) upper route identified;
- exact values through N=69 located.

Current frontier:
- no sharp upper-bound mechanism is yet accepted.

Acceptance:
- full quantified upper bound or explicit asymptotic disproof;
- no theorem-strength missing lemma;
- exact falsification of every proposed bridge.

## Lemma D1: exact duplicated-difference structure

Let A be admissible, let k=|A|, and let sigma be its repeated sum when one exists. For d>0, write m(d)=#{(x,y) in A^2:x-y=d}. If (x,y) and (u,v) are distinct representations of d, then x+v=u+y. These are distinct unordered sum representations, hence their common value is sigma. Therefore (u,v)=(sigma-y,sigma-x), so m(d)<=2 and every duplicate is one reflection orbit.

Put P=A intersect (sigma-A), p=|P|, and let q be the number of off-diagonal pairs {x,sigma-x} in A. Among the binom(p,2) positive-difference pairs internal to P, exactly q are fixed by reflection; all others form 2-orbits. Hence

    |{x-y:x,y in A, x>y}| = binom(k,2) - (binom(p,2)-q)/2 <= N-1.

If there is no repeated sum, take p=q=0. The proof is exact and includes midpoint/diagonal cases. Exhaustive gate check_difference_identity.py passed all 131070 subsets through N=16, including 15057 admissible subsets. D1 is accepted but is not sharp enough alone.


## Wave-1 exact lemmas and barriers

### Lemma C1: occupied Cayley-slice inequality

For any finite X and any partition A=A_1 dotcup ... dotcup A_t, P02 proves

    sum_j |A_j|^2 |X|^2 / |A_j+X|
      <= |A||X| + 2 Q_Delta(X) + 2 Q_D(X),

where Delta is the represented positive-difference set and D is the set of doubled differences. For X=[0,h-1], this retains the exact occupied thickening and the exact reflected duplicate weight. In particular, if the exceptional multiplicity is o(sqrt N), then |A|^2 <= (1+o(1))N. This is accepted.

### Lemma W1: rank-window partial theorem

Writing rho=|A intersect (sigma-A)|/|A|, P03 proves

    span(A) >= (1-rho+rho^2/2-o(1)) |A|^2.

Thus the 4/3 target holds whenever rho <= 1-1/sqrt(2)+o(1). The method is sharp within lag-only windows and stops at coefficient 1/2 for fully reflected sets. This is accepted as a conditional theorem, not a complete solution.

### Lemma E1: exact hybrid support identity

With q=|A intersect (sigma-A)| and delta the exceptional midpoint indicator, P04 proves

    |A+A| + |(A-A) intersect Z_{>0}|
      = |A|^2 + 1 - (q^2+3 delta)/4.

It also proves the exact sum/difference fibre moments. Scalar moment and global-support Fourier arguments cannot reach 4/3; the Erdos-Freud family is an exact barrier.

### Current frontier

The only unresolved high-reflection regime has exceptional multiplicity Omega(sqrt N). Two sharp equivalent attack surfaces are:

1. the occupied-thickening tradeoff

       |A+[0,h-1]|/N * (1+2 W_h/h^2) <= 4/3+o(1)

   for some sqrt(N)<<h<<N;

2. the coupled signed-ruler inequality for a fully reflected core, together with a quantitative elimination of the unpaired residual.

One-point compression is dead: P06 gives the exact extremal falsifier {1,3,4,8,10} in [10], including all 25 exchanges and exception relocation.


## Wave-1 closure: signed-ruler frontier

### Lemma H1: hybrid support in the low-reflection regime

P08 proves

    H(A):=|A+A|+|(A-A) intersect Z_{>0}| <= N+O(N^{3/4})

when q=|A intersect (sigma-A)|=O(sqrt(|A|)), and H(A)<=N+o(N)
when q=o(|A|). For a fully reflected set B union (M-B), admissibility is
equivalent to B being Sidon and

    M notin S(B)+Delta^+(B).

In that case H=3|B|^2+1. Thus the fully reflected frontier is the hole
estimate M>=3|B|^2-o(|B|^2). Range separation M>3 span(B) proves it, but
cannot be assumed.

### Lemma SR1: exact signed-ruler cutoff

Write the fully reflected core as a Sidon ruler

    Z={0=z_0<...<z_{p-1}=W},  G>=1,

with D(Z) disjoint from G+S(Z), and L=G+2W. P07 proves, for 1<=r<p,

    u M_r-binomial(u,2)+Phi_{Z,G}(u) <= T_r
    <= binomial(r+1,2) W,

where M_r=rp-r(r+1)/2 and

    Phi_{Z,G}(u)=sum_{i<=j}(u-G-z_i-z_j)_+.

The p=5 interlacing witness saturates every nonnegative packing weight;
there is no universal finite slack. Exact CP-SAT minima are

    4,10,19,30,48,68,85,116 for p=2,...,9.

For p=10,11,12, exact admissible witnesses have L=152,191,238, but no
optimality certificate is claimed.

### Lemma U1: unpaired residual packing

With core size 2p+delta and residual size u, P09 proves the exact packing

    p(p+delta)+(2p+delta)u+binomial(u,2) <= span(A).

It also proves the occupied-thickening core-deficit inequality and the
exact core/residual distance coupling. The missing gain over W1 is

    p^2+pu-u^2/4.

An infinite deletion family shows that both core and residual can have
Theta(sqrt(N)) size, so residual negligibility cannot be assumed.

### Lemma DC1: decorated cutoff and barrier

P10 extends SR1 by adding exact residual-label weight, midpoint weight,
the core-residual coupling charge, and U-U autocorrelation. The resulting
inequality was exhaustively checked on 8044 cutoff instances from all
relevant admissible subsets of [1,14]. The seven-point set

    {1,2,4,9,13,30,31}

is an exact falsifier to replacing the residual autocorrelation by the
P09 core deficit: it would force 5/3<=1. The remaining theorem-strength
frontier is a same-ruler distribution lower bound for Phi_{Z,G}, followed
by its decorated analogue for the residual.

## Wave-2 closure and current frontier

### Lemma GD1: exact gap-defect tradeoff

P22 proves the residual-safe inequality

    kH-M_H(A) >= (4Z_H(A)+2J_H(A))/m_H(C),

together with scalar elimination, an averaged-in-H strengthening of C1,
and a colored onset inequality sharp on the Erdos-Freud construction.
The formulas were exhaustively checked on 13,505 admissible sets through
span 16. They do not close the theorem because the uncolored duplicated
difference weight can avoid the required onset phase.

### Barrier SD1: unconditional support-defect coupling is false

P23 constructs an infinite admissible Ruzsa-reflection family for which,
at every mesoscopic adaptive scale,

    M_H(A)/N = 1+o(1),    liminf Z_H(A)/H^2 >= 1/4.

Hence the P02 product has liminf at least 3/2, not 4/3. This kills both
the pointwise and adaptive-existential unconditional support-defect
frontiers. Exact self-tests covered 4,606 profiles and 510 sets; the
certificate suite verified 13 candidate records.

### Lemma ES1: exact endpoint-shadow inequality

For valid signed-ruler data E={e_1<...<e_q=M}, P24 proves that every
represented distance d=e_j-e_i satisfies

    B(M-e_j) <= tau(d)
      <= R-d/2-F(M-d)-q+F(d)+1.

The checker passed 2,861 rulers, 14,405 represented differences, 93,494
slices, and all known witnesses through q=12. This is accepted but does
not yet sum to the coefficient-three span bound.

### Algebraic carry frontier

For a Singer perfect-difference lift B modulo v, literal reflected
admissibility is equivalent to a zero coefficient in the integer carry
layer of S(B)+Delta^+(B). The exact carry audit independently verified:

    40/40 stored Singer/Bose-Chowla candidates;
    26/26 natural Singer parameter records;
    every stored candidate has a layer-two hole through 2v/3.

The worst natural record is parameter 128, with best hole ratio

    10821/16513,

and no cut with a hole through 1/2. Thus the half-window conjecture is
false, while the finite data support the following exact open statement:

    SCG(2/3): for infinitely many Singer parameters, some affine lift/cut
    has a layer-two carry hole t <= 2v/3.

SCG(2/3) would give fully reflected admissible sets with center at most
(8/3+o(1))p^2, disproving the proposed constant and yielding lower
constant at least sqrt(3/2). No infinite theorem is presently proved.
The current frontier is to prove or falsify SCG(2/3) by integer carry
mixing; cyclic modular identities alone are insufficient.

### Post-audit corrections and algebraic dichotomy

The earlier claim that P20's centered fixed-scale candidate was false is
withdrawn. P23 tested duplicate weight D_H rather than centered defect
Z_H=D_H-Q_H; the corrected p=503 audit satisfies centered C20 with cleared
margin -305894457730641.

For a Singer lift B, C=L-B, and d=v+2L-M, P26 proves the exact hole test

    E_C(d)=#{alpha<=beta in C:
             alpha+beta<d, d-alpha-beta notin Delta+(B)}=0.

Its ordered version is the tetrahedral four-point correlation

    sum_{alpha+beta+delta<d}
      1_C(alpha)1_C(beta)1_C(delta)
      1_C(v-d+alpha+beta+delta).

The Fourier zero mode is

    E_0(d)=d^3/(12v^2)+O(q),

not the previously guessed quadratic d^2/(8v). Singer flatness proves the
two marginal estimates but does not control their same-cut correlation.
The exact q=167 audit has identical flat spectra with counts ranging from
0 to 100 at d=floor(v/4).

The Singer dichotomy is now resolved in the STM direction. P29, corrected by
P35's convention-safe type-(3,1) normalization, proves the uniform nonzero
Fourier bound

    |hat G_(C,d)(r,s,t)| <= 12 q^(3/2).

P35 supplies an explicit four-piece simplex decomposition with normalized
Fourier algebra norm at most

    4(1+H_((v-1)/2))^5,

and hence

    |E_C(d)-E_0(d)|
      <= 48q^(3/2)(1+H_((v-1)/2))^5+5q.

Since E_0(d) is of order q^2 for d>=epsilon v, no affine Singer cut has a
macroscopic carry hole for sufficiently large q. Thus every affine Singer
hole has d=o(v), and the associated reflected construction has coefficient
M/(q+1)^2 -> 3. The Singer lane cannot disprove the proposed constant.
P16 separately shows that residue histograms, aggregate wraps, quotient
moments through degree 3, and polynomially weighted modulus averages cannot
replace the missing indexed phase data in a general construction.

### Correction: centered support defect remains open

P23 used positive duplicate weight D_H, whereas P02 and P20 use the centered
quantity Z_H=D_H-Q_H with missing-difference weight Q_H. Consequently the
earlier wave-2 statements declaring the centered P02 product and P20 C20
dead are withdrawn.

The corrected exact p=503 audit has

    D_H=25058720, Q_H=25569511, Z_H=-510791,

and centered C20 cleared margin -305894457730641. Thus P23 is only a
falsifier to duplicate-only couplings. The centered C20 candidate at
H=ceil(N^(2/3)) remains an open theorem-strength frontier, with zero failures
in its original 193-sample, 1,811,499-profile exact corpus.

P33 proves the exact tangent-gap factorization

    Phi_H=Psi_H+2(3M_H-2N)(2Z_H-H^2),

where C20 is `Phi_H<=0`, `G_H=N+H-1-M_H`, and

    Psi_H=8NZ_H-12H^2G_H+3H^3-12H^2-9N(k-1)H.

Since `2Z_H<H^2`, C20 is automatic when `3M_H<=2N`; in the
large-support case it is enough to prove `Psi_H<=0` (LG33). The
factorization has zero mismatches on all 1,811,499 profiles and exhaustive
integer verification covers every endpoint-normalized admissible set through
N=24. LG33 is the current centered frontier, not yet a theorem.

P50 proves a noncircular LG33 subcase. If

    Esharp_H=9N(N-1)-3H^3+12H^2+(12H^2-9N)G_H,

then the exact identity

    RHS(LG33)-Esharp_H=9N(kH-M_H)>=0

shows that `8NZ_H<=Esharp_H` implies LG33. At the prescribed scale
`H=ceil(N^(2/3))`, the simpler condition `4Z_H<=3N` suffices. The exact
audits leave 78 of 21,674 endpoint sets through `N=24` and 151 of 193 stored
prescribed profiles outside the sharp envelope; none falsifies LG33. The
coefficient `13/6` survives only the prescribed corpus: at `N=H=11`,
`A={1,2,4,8,10,11}` falsifies its all-scale form by 341.

### Affine Singer averaging and proved Katz-simplex mixing

P28 proves that a fixed-level affine carry zero with d/v in (1/3,1/2)
normalizes to an SCG witness. It also proves the exact translation mean

    E_b E_C^ord(d)
      =(p/v)^4 binom(d+2,3)+O(q log^3 v),

so the mean is positive of order q^2. Ordinary first/second moment methods
therefore do not force a zero; the variance is an eight-Gauss-sum
correlation and standard inequalities point in the wrong direction.

P29 proves the complete Fourier bound

    |hat G_(C,d)(r,s,t)| <= 12 q^(3/2)

at every nonzero frequency. The all-nonzero case is the direct Katz
type-(3,1) trace Hyp_Psi((A,B,C);(1);-z); frequencies containing zero use
an exact Singer Sidon identity. P35 independently corrected the displayed
normalization, verified the exceptional-character terms, and supplied the
explicit simplex completion proving STM uniformly with exponent K=5.
Finite normalization/decomposition audits passed for q=2,3 and all odd
v<=15; they check identities only, while the asymptotic bound uses Katz's
Theorem 8.4.2 and P35's Fourier-algebra proof.

The complete q=167 affine scan checked 14,028 unit classes and 2,356,704
cuts. Its exact best finite record is

    p=168, M=72728, M/p^2=9091/3528,
    d=8859, E_C(d)=0.

This is finite evidence only and is compatible with eventual Singer drift.

### Modular construction obstruction

P34 proves a family-independent finite-group threshold. If a p-element
same-parity set in Z_(2h) is strong Sidon (diagonals included) and disjoint
from its modular threefold sumset, then

    2h >= 3p^2-p+2.

The proof counts `B+B` and `B-B`: if their cardinalities sum past the group
order, every class lies in `3B-B`. It also proves that every odd-characteristic
finite-field parabola and every modular Welch graph is saturated by `3S-S`,
and that fixed odd residue gates with arbitrary modular fibers have
coefficient at least `4-o(1)`. Exact audits and the Lean theorem
`P34.modular_cover_overlap` pass without `native_decide`. These results close
direct modular constructions but leave literal nonmodular carry placements.

### Translate-block and continuum obstruction

P37b proves the exact translate-block identity for a same-parity Sidon set
(E) with (Ecap3E=arnothing). Its low triple-sum blocks have pairwise
intersection at most one, and the block degree at every low target is at most
(|E|-1), sharply.

For every rational (0<g<1), it also gives a continuum profile of coefficient
(2+g<3) satisfying the coupled P13 occupation law and every continuum P24
endpoint-shadow inequality. Therefore endpoint-shadow and uncolored
occupation inequalities alone cannot prove coefficient three. A completion
must retain unit-lattice carry phase or a new constraint on equal-three-sum
partitions. Exact integer/Fraction audits pass in
`compute/p37/audit_reflected_3e.py`.

### Exact signed carry identities and their obstruction

P45 proves the literal carry identity

    delta = M_1 + M_2 - u + a_0 + c_0,

where `M_i` counts carry-level `i` pairs, `u` counts residues missed by both
supports, and `a_0,c_0` count doubled fibers outside the opposite support.
For doubled sum fibers it also proves

    a = A_11 + A_12 + A_22,
    c = A_11 + 2A_12 + 4A_22,

and hence `a <= c <= 4a` and `0 <= 4a-c <= 2p`.

The exact pair `B-={2,4,5}`, `B+={2,3,5}` at `h=6,b=2` has identical
unsigned fiber data but carry profiles `(M_1,M_2)=(3,4)` and `(4,3)`.
It disproves both universal carry-level dominance and `M_1-M_2 <= u`.
Thus any reflected completion must use literal placement or phase beyond all
unsigned fiber statistics. The independent verifier is
`compute/p45/audit_signed_carry_identity.py`.

The correct reflected target is one-sided. Since

    max(E) = 3p^2-p+b-2delta,

the desired lower bound is equivalent to `delta_+=o(p^2)`, not to
two-sided `delta=o(p^2)`. GPT-Pro supplied the exact prime family
`z_i=2qi+(i^2 mod q)`, `G=W+1`, for which `delta/p^2 -> -3/2`; it satisfies
the desired lower bound with large slack. The exact verifier
`compute/p54/audit_delta_positive_part.py` checks the first ten odd primes.
All carry searches may therefore restrict to the hard regime `delta>0`.

### Primary-source theorem bridge audit

P49 finds no existing theorem that supplies coefficient three. For odd
positive sets, integer Sidonicity plus `E intersect 3E = empty` is strong
4-independence, but Bajnok--Ruzsa's cyclic coefficient `1/sqrt(3)` is their
Conjecture 15, not a theorem. Reduction modulo `max(E)+1` is false: the valid
set `{1,7,11}` acquires `1+1 = 7+7 (mod 12)`. Even valid sets need not be
strongly 4-independent, as `{2,4}` has `4=2+2`. The strongest directly
applicable audited theorem is the Carter--Hunter--O'Bryant Sidon-diameter
bound, which gives only `(2-o(1))p^2` after parity normalization.

### Generic polynomial phase obstruction

P47 proves the exact aperiodic autocorrelation identity for
`A=PP#` and `B=x^G P^2` and shows that it is independent of `G`. It gives
two infinite families of nonnegative, disjoint-support, equal-modulus
polynomials with ambient endpoint `(2+o(1))p^2`, including a nontrivial zero
flip. Thus no generic equal-modulus/disjoint-support uncertainty theorem can
supply coefficient three.

The genuine signed-ruler problem retains additional structure: both
coefficient profiles, the common p-term Sidon Newman factor, self-reciprocal
nonnegative `A`, and one-sided integer orientation. The precise surviving
analytic target is an arc-sensitive inequality forcing `G>=W-o(p^2)` from
these joint data. The exact verifier `compute/p47/audit_polynomial_phase.py`
passes all integer convolution checks and family sweeps through `p=25`.

### Exhaustive carry-statistics barrier

P46 proves the exact identities

    delta = |I| + C_S + C_D - H_0

and

    delta = U_1 + U_2 + C_out - H_0,

where `C_S,C_D` are modular sum/difference fold counts, `H_0` is the
missed-both count, and `U_i` are literal carry counts. Its exhaustive
width-30 census contains 464,981 admissible positive-defect holes and agrees
with all 2,329 legacy P44 fields.

The exact collision-only witness

    p=4, h=14, b=1, B={1,3,9,13}

has `delta=9`, `I=empty`, `H_0=0`, `C_S=3`, and `C_D=6`. Thus every
inequality depending only on carry overlap or signed carry moments is false;
the modular collision defects must also be controlled. P45's energy identity
relates them by `C_S <= C_D <= 4C_S` and `4C_S-C_D <= 2p`.

One exact candidate gate survived all width-30 holes and all 137 stored
reflected profiles:

    C_S <= 2p-3.

It is not yet a theorem. Together with the energy identity it controls the
fold contribution, but not the collision-free literal carry defect.

P53 shows that the same inequality is false without the literal-hole
hypothesis. Its exact `p=25,h=494` Sidon ruler has `C_S=49>47=2p-3` and
positive defect 432, but both `-1` and `-2` lie in `3B-B`. Thus the actual
hole-restricted candidate survived P53 but is later falsified by P75. P53
also kills the direct KST proof:
the zero-fold Bose carry graphs need at least 34 and 17 edge deletions to
become `C_4`-free, while the visible correction budget is only 7.

The second candidate is now false. An exact scan of all 165,225 admissible
translations of 133 stored rulers finds 22 failures. The strongest is the
Bose ruler

    p=17, W=207, gamma=80, b=2, h=288,
    delta=138, C_S=C_D=0.

The first scale repair

    max(delta-5(C_S+C_D),0)^2 <= 4p^3

had zero failures on 630,343 initial instances, but P58 gives the exact
Singer counterexample

    p=14, h=183, b=1,
    B={33,60,72,75,79,81,95,119,124,132,149,150,160,182},
    delta=105, C_S=C_D=0.

Here `105^2=11025>10976=4*14^3`. Thus the constant `2` in the
`p^(3/2)` repair is false. An unspecified-constant `O(p^(3/2))` bound
remains open.

P75 falsifies the conjectured positive-defect hole-fold implication exactly.
The Sidon ruler

`B={3,5,69,169,211,223,251,329,373,403,409,501,505,519,631,639,689,715,775,863,883,915,931,953,977,987}`

has `(p,h,b,delta)=(26,988,1,14)`, satisfies the literal hole
`-1 notin 3B-B`, and has `C_S=51>49=2p-3`. All 351 unordered sums including
diagonals and all 325 positive differences are unique. Thus neither the
unrestricted nor positive-defect P65 fold bound survives. The standalone
integer verifier is `compute/p75/verify_hard_fold_counterexample.py`.

### Natural-modulus Bose carry audit

P62 exhausts every affine Bose-Chowla lift at `h=q^2-1` for the prime powers

    q=3,4,5,7,8,9,11,13,16,17,19,23,25,27,29,31,32,
      37,41,43,47,49,53,59,61,64.

Every lift has `C_S=C_D=0`. Literal holes exist for every tested `q<=23`,
with exactly one at `q=19` and `q=23`. There are no holes among all 115,130
distinct affine lifts for `25<=q<=64`. This kills no infinite family by
itself: eventual nonexistence for Bose-Chowla lifts is still unproved.

### Guarded heterogeneous recursion obstruction

P55 repairs and proves P48's construction obstruction. If endpoint-normalized
integer Sidon rulers `X,Y` have disjoint positive difference sets and
`p=|X|+|Y|>=9`, then with `r=floor(sqrt(p))`,

    span(X)+span(Y)
      >= r/(r+1) * (p-(3r+1)/2)^2
      >= p^2(1-4/sqrt(p)-1/p).

Together with P48's strict range guards this gives endpoint coefficient at
least five. Cross-disjointness without internal Sidonicity is insufficient;
P55 gives the exact family `X={0,1}`, `Y={0,2,...,2(q-1)}`. Thus fully
range-separated binary recursions cannot disprove Problem 864.

### Integer equal-three-sum barycenters

P51 proves that distinct triple representations of a fixed sum have disjoint
supports. After removing type-21 representations, their remaining support
`B_x` satisfies the exact integer constraints

    3 sum(B_x) = x |B_x|,
    |B_x| = epsilon_x (mod 3).

This yields a subset-sum column capacity

    I_Z(K) <= sum_{x<=K} beta_Z(x) + 2D_Z(K),

which reduces the stored Bose `q=128` coarse capacity from 36,068 to 1,685
for 791 actual incidences. The exact width-18 audit covers 6,783 valid pairs.
The next step must couple the barycentric subsets across different `x`; the
scalar capacity alone remains a relaxation. The smallest all-distinct
collision is `Z={0,1,5,11,13,20,44}, G=16`, with
`25=0+5+20=1+11+13`.

P59 kills the first leading-order coupling. For

    Z={0,7,9,12,20,26,30,58}, G=15,

maximum capacity witnesses at sums 37 and 39 both have size 6 but intersect
in five marks, exceeding the proposed block-count bound 4. Actual balanced
supports at sums 39 and 42 have the same failure. A C++ width-first search
checks 2,005,269 endpoint rulers and proves `(p,W)=(8,58)` minimal in that
order. The barycenter identities remain valid, but ordinary support
intersection cannot supply the missing one-third reduction.

### Arc spectral staircase

P52 factors

    P*(x)-x^(G+W)P(x) = (1-x)R(x),

where `R` has a positive palindromic unimodal integer staircase. Its
autocorrelation gives the exact tail domination

    (1/2) sum_{k>n} [x^k](x^G P^2)
      >= |D^+(Z) intersect (n,W]|.

The associated principal Toeplitz spectrum is independent of `G,W,Z`, and
the slope of the autocorrelation need not be unimodal. The exact structured
falsifier `Z={0,3,4},G=2` has slope segment `5,4,6`. Thus the surviving
analytic target is a bound on the span of curvature reversals, not a
single-peak theorem.

P60 closes that unconditional target. It proves the exact ordered-pair tail

    2s_n=#{(i,j): |z_i-z_j|<=n<G+z_i+z_j}>=1

and the span-blind variation identity `sum|2c_n|=2p^2-p`. A doubled
Erdos--Turan Sidon family with odd `G` has `W-G=(4+o(1))p^2`, so staircase
positivity alone cannot bound the inversion span. Exact examples also kill
bounded reversals, a growing tail floor, Hankel log-concavity, and a centered
Newman zero count. The only surviving analytic target is the compensated
defect `3p^2-(G+2W)=o(p^2)` in the width-subcritical regime.

P68 separately kills literal-hole smoothing. The exact admissible profile

    Z={0,24,26,29,30}, G=7

has no represented shift in `Z-3Z` from 7 through 23. The exhaustive
width-30 audit finds 54,458 three-consecutive-hole failures among 140,109
nontrivial positive-defect holes. A single missing coefficient need not be
isolated, so local averaging around the hole is not a valid bridge.

### Reflected-core completion with collision defect

P56 decomposes a general admissible set as paired core `P` and residual `R`.
For the virtual completion `F=A union (sigma-R)`, let

    beta=(p+u)(p+u+delta)-|D^+(F)|.

Deleting at most `min(u,beta)` residual reflection-pairs produces a fully
reflected admissible set. Consequently

    span(A)+|sigma-min(A)-max(A)|
      >= H_delta(p+u-min(u,beta)).

This is an exact noncircular reduction, but it closes the general theorem
only when the residual credit pays the completion defect and reflection
shift. The smallest blocked completion is `A={0,2,3,6}`: adding the missing
reflection of 2 creates repeated sums 4,6,8. The N<=22 audit checks all
2,097,151 endpoint-normalized subsets.

P61 removes the reflection shift as an independent obstruction. In the P56
notation, with midpoint flag `eps`, it proves

    L-tau >= H_eps(p),
    L+tau >= max(H_eps(p+u-b), |D+(A)|+binom(u-b+1,2)).

Adding gives a shift-free two-scale completion inequality. If the reflected
sharp bound has error `E_eps`, then

    L >= 3k^2/4 + 3(u^2-2b(k+u)+2b^2)/4
         -(E_eps(p)+E_eps(p+u-b))/2.

For example, `u=k/2,b<=k/12` supplies `k^2/96` positive credit regardless
of `tau`. The remaining general-case obstruction is the completion collision
ratio `b/k`, not residual size alone. Exact audits cover 8,458 residual
records through `N=22`, 412,860 stress records through `N=36`, and all stored
extremizer/construction rows.

### Further exact completion evidence

P66 exhausts every endpoint-normalized admissible set of span at most 55.
Among 35,776,005 admissible sets, 30,899,206 have nonempty residual and
18,800,840 lie outside the already proved P61.2 range. None violates
`2 beta <= h_S`; the minimum margin in the unproved range is one. The
standalone verifier reconstructs every stored extremal witness exactly.
This is finite evidence only; the unrestricted inequality remains open.

### LG33 reflected specialization

P64 proves that for a separated reflected set `A=B union (c-B)`, the P50
LG33 residual has an exact formula in the short-difference weight of `B`,
its long-gap excess, and the central gap. Sliding-window Cauchy then shows
that LG33 on dense Sidon halves already implies `c >= (3-o(1))p^2`.
Thus LG33 contains the sharp reflected-center problem rather than reducing
it to a routine local estimate. A one-label strengthening is false on the
stored `N=4925` row by the exact margin 64,625.

### Natural-modulus Bose sidecar

P63 proposes a uniform character-sum theorem: every affine Bose-Chowla lift
at modulus `q^2-1` has `(1/6+o(1))q^2` literal solutions of
`x1+x2+x3+b=x4`, uniformly in the affine parameters and `b in {1,2}`.
The exact parametrization and finite censuses reproduce through `q=29`,
with no tested hole from `q=25`. The asymptotic theorem is retained as a
candidate pending independent review of its sheaf nonconstancy and uniform
conductor claims; it is not yet used as an accepted proof node.

An independent referee supplied the missing split-torus local-monodromy
calculation and a uniform tame Betti-number argument. With those details,
P63 is accepted: natural-modulus affine Bose-Chowla holes do not persist for
large prime powers. This closes that construction lane only.

### Hole-restricted folds

P65 tests the then-surviving conjecture `C_S<=2p-3` on 9,953,261 valid
translations from every normalized Sidon ruler of width at most 45 and on
165,225 P20 translations, with zero failures. The stronger `C_S<=p-1` is
false at `p=19,C_S=20`. A valid Singer row contains an outer-graph `K_3,3`
and has degeneracy six, so planarity and low-degeneracy proofs are invalid.
P75 later gives a positive-defect literal-hole counterexample to the
conjecture itself.
The conditioned `2p-3` bound remains open as a labeled sum/difference claim.

### Width-compensated Fourier reduction

P69 proves an exact dichotomy. If
`E=3p^2-(G+2W)>=epsilon p^2`, then either the modular sum/difference fold
loss is at least `epsilon p^2/8`, or a nonzero Fourier coefficient of the
four-point incidence function is at least
`epsilon p^2/(256(2+H_floor(h/2))^5)`. The proof uses the literal-hole
tetrahedron and a bounded Fourier-algebra norm. It isolates a fourth-order
obstruction but does not bound it for arbitrary Sidon rulers.

### Ruzsa all-cut extension

P70 scans every natural Ruzsa cut at p=263,269,271,277,281,283,293. The
best exact ratios `M/|B|^2` range from 2.760082 to 2.818394; five parameters
lie below 14/5. An independent verifier reconstructs all CRT lifts, proves
every earlier center represented, and checks all reflected sum censuses.
This revives but does not prove an infinite sub-three construction family.

### Multi-column barycenter obstruction

P67 constructs, for every q>=3, a valid Sidon/gap instance with two genuine
type-111 fibers of q blocks whose supports intersect in `3q-1` marks, while
the total block count is `2q`. Thus no pairwise support-intersection bound
with even an `o(q)` correction can close P59. Any surviving barycenter route
must couple several columns globally or retain quantitative carry location.

### Corrections after independent review

P70 is accepted after an independent analytic referee supplied the complete
fibrewise Kummer--Artin--Schreier conductor check and a quantitative uniform
discrepancy argument. Uniformly in every natural Ruzsa cut and `0<=t<n`,

`R_B(t)=(p^2/12)(1-t/n)^3+o(p^2)`.

Therefore no fixed compact subinterval of the carry range contains holes
for all large primes. The finite sub-14/5 centers are genuine but do not
persist at a fixed distance from three. The natural Ruzsa construction lane
is closed.

P71 falsifies the unrestricted P65 bound for `b=1`. Starting from the P53 ruler with
`p=25,h0=494,C_S=49`, the affine lift `B_q=qA+(q-1)`, `h_q=qh0`, preserves
all diagonal-inclusive sum distinctions and all folds, while positive
differences are `0 mod q` and `B_q+B_q+1` is `-1 mod q`. Thus every q>=2
is a literal-hole counterexample with `C_S=49>47`. Hole-restricted
`C_S<=2p-3` without a defect restriction is dead. However
`delta_q=926-494q<0` for every q>=2 (the displayed member has `delta=-62`),
so P71 does not touch the required hard-regime implication
`delta>0 => C_S<=2p-3`. That statement and the fixed `b=2` variant remain
open.

### Completion defect decomposition

For the P56 completion defect, write `v=sum_{d in D(A)}q_d` and let `w` be
the number of missing difference labels with `q_d=2`. Then `beta=v+w` and

`h_S=2h_D+|D_R|-u`.

The full target is equivalent to

`2v+2w+u<=|D_R|+2h_D`.

The exact span-55 census now records these pieces on all 30,899,206 residual
cases. The tempting `2v<=|D_R|` fails 136 times, first at span 38. The two
stronger coordinated statements

`w<=h_D`,

`2v+w+u<=|D_R|+h_D`

have zero failures. Together they prove the full target. The first has an
immediate label injection once one notes that `q_d=2` forces `d<=L`; the
second is the current general-case proof frontier.

P74 removes that exact frontier at the asymptotic scale. Selecting all
residual points, one point from every reflected core pair, and the midpoint
when present gives a genuine Sidon subset of size `s=p+u+delta`. An
elementary difference count proves `L>=s^2-3s^(3/2)`, hence

`h_D>=binom(u+1,2)+delta*s-3s^(3/2)`.

Together with `beta<=binom(u+1,2)` and the exact P61.2 range, this proves
`2beta<=h_S` for every sufficiently large admissible set. This proves the
P66 charge itself. A separate assembly check is still required to show that
this charge makes the P61 completion credit sufficient in every regime; the
fully reflected sharp center bound also remains open.

### Completion overlap and assembly obstruction

P73 proves the exact three-layer identity

`2beta=|J intersect S|+|K intersect(S union J)|`

for the reflected completion layers. Weighted short-difference bounds reduce
the unrestricted completion charge to 35 finite parameter boxes; any
remaining counterexample has at most 29 points and span at most 567. The
independent referee accepted the mathematics after endpoint, cutoff,
and checker repairs. The repaired exact checker returns all 45 pre-census
triples in 1.3 seconds; the span-55 census leaves the stated 35 boxes.

P72 independently proves `w<=h_D` by a centered signed-layer count. Its
centered inclusion-exclusion cancels the remaining `v` term exactly, so it
does not prove the stronger mixed inequality outside the P61.2 range.

P76 performs the full normalized optimization of P61's two branches,
difference packing, P74's exact charge, and a hypothetical sharp reflected
bound. These statements alone permit

`inf L/k^2=3/8`

at `u/k=b/k=1-1/sqrt(2)`. An exact integer parameter ray realizes every
displayed inequality. Thus P74 does not complete the general assembly; a new
placement-sensitive bound on the repair cover number `b=min(u,beta)` is
required, in addition to the fully reflected center theorem.

P77 proves the unconditional fourth-order inequality

`L_h^5 Lambda(B,h,b) >= (E-p+b-10C_S)_+/128`.

It removes the difference-fold variable from P69 but retains the sum-fold
count. The proposed corollary eliminating `C_S` used P65 and is invalidated
by P75. Thus the live analytic target is a joint estimate on fold count and
the phase-sensitive fourth-order coefficient, not a pure Fourier bound.

P79 falsifies the proposed K2,4 and K4,4 exclusions on the positive-defect
literal-hole corpus. The outer graph can contain K5,5 and have pair
codegree 12. No K6,6 occurs in 165,225 exact rows, so a universal K6,6
exclusion would still imply `C_S=o(p^2)` by KST, but it is unproved.

P80 falsifies the universal endpoint repair `C_S<=2p-1`: a 29-point ruler
at `h=640` has 58 folds. It has 89 literal-hole collisions for `b=1` and 97
for `b=2`, so it does not falsify a hole-conditioned asymptotic estimate.

P82 gives a uniform removal-theoretic reduction. Mapping every fold
`a+c+h=u+v` to `(a_A,c_C,u_U)` produces a linear 3-partite 3-graph, whose
shadow contains `C_S` edge-disjoint canonical triangles. Therefore
`C_S>=epsilon*p^2` forces `T_F>=eta(epsilon)*p^3` loose fold triangles.
The literal hole does not forbid this configuration pointwise: the exact
P75 verifier gives `C_S=51` and `T_F=25`. The surviving reflected frontier
is to prove that the endpoint phase zero forces `T_F=o(p^3)`, or to derive
an equivalent phase-sensitive joint fold/Fourier bound.

P83 retains the endpoint phase in every loose triangle. With parameters
`(a,c,u,s,X,Z,R)`, all nine marks are recovered from
`a,c,u,s,a+X,c+Z,u+R,s+R+X,s+R+Z`, and the three low labels
`d,d+Z,d+X`, `d=a+c+b`, are distinct missing positive differences. Loose
triangles inject into shared triples `(a,c,u)` with `a<=c<u`, proving the
exact universal bound `T_F<=binom(p+1,3)`. This is cubic and therefore does
not close P82. P75 has only three in-range natural endpoint targets among 25
triangles, and a seven-point exact row falsifies the extra nonedge `d-R`.

P84 identifies an exact closing candidate. For the three zero-one fold
shadows,

`C_S+T_F=sum_{a,c,u} M_AC(a,c) M_AU(a,u) M_CU(c,u)`.

The conjectural inequality `T_F<=C_S` would combine with P82 to force
`C_S=o(p^2)` immediately. It has zero failures on all 464,981 width-30
positive-defect literal holes, 134 stored positive-defect rows, and P75;
the largest stored ratio is `80/141`. This remains a finite-data candidate.
The exact Fourier tensor shows why the scalar hole coefficient alone cannot
prove it: the triangle trace uses off-diagonal two-frequency slices, and
dropping the order mask enlarges P75's trace from 76 to 1296.
P94 exact-tests the same candidate on every literal hole in the archived
translation and insertion domains: 313,863 translations and 242 insertions,
again with zero failures. The strongest observed ratio is `116/142` at
`(p,h,b)=(104,14484,1)`. An independent direct verifier rebuilds both
archived ratio maxima; the audit JSON hash is
`B9CED807C1D4602269CD7B13423E598C8882792F68AF9D30E22E71C1C6C95963`.
The stronger componentwise statement, that every connected loose-triangle
component has at most as many triangle edges as fold vertices, also has zero
failures on all three exact domains. In the ratio-maximizing row its unique
nontrivial component is tight with 116 triangles on 116 folds.
P100 further shows that C84 and its componentwise and ordered color-threshold
strengthenings have zero failures on all 791,869 endpoint translations of
every integer Sidon ruler of width at most 30, without positive defect or
the literal hole. This finite extrapolation is false in larger order: P88
gives a 60-point endpoint Sidon row with positive defect and
`(C_S,T_F)=(182,200)`. Its component excess is 35 and its ordered prefix,
suffix, and total slacks are `-43,-34,-18`. The exact row fails both literal
holes; all 75 failing positive-defect translations end before the first
literal-hole translation. Thus only the full phase-conditioned C84 remains
a candidate. The P100 JSON hash is
`FEE46F7E2EE08D7304D7C19E060839EC3CFC3FB7993511F7B98A334C0E07177E`.

P101 gives a sharper proof target that includes the load-bearing phase.
Let `V_b` be the number of canonical folds with low sum `s` for which
`s+b` is a represented positive difference. The global inequality

`T_F <= C_S + V_b`

has zero failures on 1,583,738 unrestricted width-30 rows and all 4,170
positive-defect translations of P88. The componentwise corrected form fails
twice, so any proof must charge globally. Under the literal hole `V_b=0`,
this becomes C84 and closes the fold frontier through P82. The audit JSON
hash is `8EAA7664524920197BBBA36483BA45F0413F85C2BA9BB74B127956B4AF2F7974`.

P93 rules out two global-looking simplifications. The P94 tight component
has a 2-core with 75 triangles on 64 folds, so leaf peeling cannot prove the
component count. Among 313,863 archived literal holes, seven violate the
shared-high prefix inequality, with maximum excess one. P102 also finds
collision-corrected prefix and suffix failures on P88 translations while
the total corrected inequality remains nonnegative. The surviving P101
target is therefore intrinsically nonlocal and cannot be reduced to one
ordered threshold.

P90 identifies C84 as a strong-edge-coloring defect bound and P82 loose
triangles as the triforce configuration. The closest primary theorems do
not preserve the arithmetic color or endpoint phase. Prendiville's theorem
does apply to give `Omega(p^4)` pairwise-distinct equal-three-sum sextuples
in every dense frontier Sidon set, but these are translation invariant and
do not control the distinguished coefficient `H-b`.

P89 factors the six-hole stencil: five values are residuals already attached
to the three supporting folds, while `tau=u-a-c-b` is absent for every
shared triple independently of any arms. For every Singer ruler of width
`W<=p^2-p`, translating by `floor(W/2)+1` gives an infinite positive-defect
literal-hole family in which every stencil value lies below `min B`.
Therefore occupancy and shared-triple deletion cannot improve P83's cubic
bound; C84 must use global compatibility of the three unique Sidon arms.

P85 proves that the standard stability upgrades do not supply the missing
phase. Sidon subsets have exact energy `2m^2-m` and quadratic doubling, so
constant-parameter BSG is unavailable. DRC and corners operate on rank
projections and erase the distinguished coefficient `H-b`; P75 is an exact
pointwise countermodel. The surviving lemma remains a positive-density
statement connecting cubic loose-triangle mass to `r_{3B}(H-b)>0`.

P86 scans 2,526 oriented archived rulers, 1,613,120 translations, and
312,094 parity-lift insertion candidates exactly. No cubic-density family
appears. Reflecting P75 preserves `(p,h,b,delta,C_S)=(26,988,1,14,51)` but
changes `T_F` from 25 to 37, so loose-triangle control must retain phase.
The one-insertion parity-lift mechanism cannot persist asymptotically:
positive defect requires at least `(2/sqrt(3)-1-o(1))p` inserted marks.

P87 rewrites each loose triangle as a punctured three-arm grid around
`K=a+c+h-u`. Both `K` and `h-b-K` miss `B`, and four further correlated
phase values are excluded. Its exact center-degree sum and reduction to
eight sign chambers still allow `Theta(p^3)`. Thus neither center absence
nor degree moments alone improve P83's cubic bound.

### Positive-defect residual-interval frontier

P105 supplies an exact literal-hole counterexample to unrestricted P101:

`(p,h,b,delta,C_S,T_F,V_b)=(57,6572,1,-1726,159,160,0)`.

Thus the positive-defect hypothesis is essential. P98 independently kills
every componentwise route under the full gates: a `p=103`, `delta=1379`
literal-hole row has 110 triangles on 109 folds in one component, although
globally `(C_S,T_F,V_b)=(132,110,0)`.

P97 gives the strongest surviving formulation. Attach to every canonical
or loose shadow triple `(a,c,u)` the interval with endpoints

`tau=u-a-c-b`, `lambda=h-b-u`.

Each fold `(a,c,u,v)` supplies slots at `h-b-v` and `h-b-u`, and one extra
lower slot when `a+c+b` is a represented positive difference. The assertion
that all intervals match injectively to contained slots (RM97) implies
`T_F<=C_S+V_b`. Its exact interval-window Hall form has zero failures in all
current positive-defect and literal-hole domains, including the P98 row, but
fails the negative-defect P105 witness. Proving or falsifying RM97 under
`delta>0` is now the reflected-case frontier.

GF(2) triangle-relation nullity and per-color pseudoforest strengthenings
are exactly false, so the proof must couple interval windows globally.

P109 rules out closing RM97 through components of the canonical residual
intervals. The full positive-defect literal-hole width-30 scan finds 304
rows where one loose triangle bridges distinct canonical interval
components; the first has `B={8,10,15,23,24,27}`, `h=28`, `b=2`.

P103 supplies an independent global algebraic frontier. For each loose
triangle, combine its three-fold incidence vector with the two formal
six-mark relations `L1,L2` and the phase-weighted blocks `dL1,dL2`. If these
vectors are always linearly independent, then

`T_F <= C_S + 4p = O(p^2)`,

which contradicts the cubic lower bound from P82 whenever `C_S` has positive
quadratic density. Exact modular rank is full on every current hard system,
including P98 and the negative-defect P105 witness. The independence lemma
is unproved and is now being attacked in parallel with positive-defect RM97.

P107 exact optimization finds no positive-defect literal-hole failure in
the complete P88 hard-regime subset lattice, the complete P94 deletion
lattice through five marks, or 5,869 full-gate mutation rows. All RM97 Hall
objectives are at most zero and all P101 objectives are strictly negative.

P111 shows that the tempting fold-only projection `(S,E,dE)` is not
universally independent: an exact ordered linear 3-graph has 51 rows of
rank 50. Therefore the surviving P103/P110 route must use the arithmetic
six-mark relations through `Q`; a generic rooted-hypergraph proof is
impossible.

P112 removes two unnecessary blocks from the P103 matrix. The vectors
`(S,L1,dL1)` use only `C_S+2p` columns and have full exact modular rank on
all 1,583,738 complete width-30 rows, all P88 translations, and every named
hard witness. Their general independence would prove the stronger
`T_F<=C_S+2p`.

P113 gives a combinatorial version with a larger but still quadratic
resource bank. For each loose triangle, the three pairwise differences of
its fold phase labels are represented positive differences of `B`. Exact
Hall matching to the three supporting folds plus these three difference
labels has zero failures on 793,954 audited fold systems and all named hard
rows. Matching to differences alone fails three P88 translations. The
remaining proof target is

`|X| <= |support_folds(X)| + |difference_labels(X)|`

for every family `X` of loose triangles arising from an endpoint fold
system. This would give `T_F<=C_S+binom(p,2)=O(p^2)` and close P82.

P114 shows that using only the outer fold endpoints and the span difference
is insufficient even for an abstract ordered linear proper-middle system;
all three support and difference resources, or additional arithmetic, must
remain in the proof.

### P106--P122 corrections and live reflected frontier

P106 exactly falsifies RM97 under positive defect alone. Its endpoint Sidon
row has `(p,h,b,delta,C_S,T_F,V_b)=(67,6572,1,129,199,221,20)`, so
`T_F>C_S+V_b`. A minimal residual window contains 411 intervals and 410
slots. The row is not a literal hole, so the joint hard regime is untouched.

P110 also falsifies the global weighted-relation matrices by dimension. The
smallest dense row has `(p,C_S,T_F)=(104,579,1104)`, hence
`T_F>C_S+4p`; P103 and the shorter P112 matrix cannot be universally
independent. Only P110's minimum-phase filtered classes remain open.

P108 proves lower-slot reservation, the upper color-window equivalence, and
the directed-cycle endpoint cancellation. Its proposed global budget BC108
is false: P115's exact positive-defect non-hole row has
`(p,V_1,E_+)=(104,314,598)`, so `E_+>p+V_1` by 180. The parity lift makes
the hole literal but makes the defect negative. Thus both hard gates are
load-bearing.

The current weaker candidate P122 keeps both gates. For each color `u`, let
`d_u=(t_u-n_u)_+` and let `D_u` be the represented differences
`|v_i-v_j|` exposed by its arm arcs. The exact Hall target is

`sum_{u in U} d_u <= |union_{u in U} D_u|` for every color set `U`.

It implies `sum d_u<=binom(p,2)` and therefore
`T_F<=C_S+binom(p,2)=O(p^2)`, enough for P82. It has zero failures on all
mandatory live rows and all 1,037 positive-defect literal-hole triangle rows
through width 30. Nineteen dense P110 rows falsify the ungated statement.
P113 support-plus-difference Hall remains the independent stronger route.
