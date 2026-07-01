# CAGE 2x2 Proof Target

Status: proof target after the fixed-sink Hall repairs became circular.

## Why this route

The widened vertex-routing atoms `BALL2` and `row-union-bimoat` repair the
small Hall falsifiers, but on the scale-critical nonuniform `C5` blow-ups
their atom sink masks collapse to `V`.  In that family the Hall condition is
therefore just the target `ROWSUM-O` again.  They are useful diagnostics, not
a proof mechanism.

The non-circular surviving structure is the CAGE / CORR formulation.  Exact
CAGE certificates exist on the named hard cases and census slices, while
uniform CAGE routing fails.  Thus the load-bearing object is adaptive
interval-pair transport.

## Fixed y target

Fix `y >= 0` and one bad edge `f`.

Let `P_f` be the CAGE transportation polytope:

```text
sum_g alpha_{i,j,g} = 1
```

for every layer pair `i<j`, and

```text
sum_{i<=t<j} alpha_{i,j,g} = m_g = H_{f,t} pi_{f,t,e}
```

for every gate `g=(f,t,e)`.

For a feasible route `alpha`, define

```text
A_g^y = sum_v A_g(v) y_v,
B_g^y = sum_v B_g(v) y_v,
Phi_f(alpha;y) = sum_g 2 sqrt(A_g^y B_g^y).
```

The y-dependent CAGE target is:

```text
for every y>=0, choose alpha_f in P_f for each f so that
sum_f Phi_f(alpha_f;y) <= sum_v (N-S(v)) y_v.
```

This implies CORR/LPD, hence ROWSUM-O.

## 2x2 closure

For two layer pairs `p,q` and two gates `g,h`, a 2x2 swap is

```text
alpha_{p,g} -= eps
alpha_{q,h} -= eps
alpha_{p,h} += eps
alpha_{q,g} += eps
```

whenever all four variables exist.  It preserves all pair and gate marginals.

Call `alpha` 2x2-closed for `y` if no positive 2x2 swap decreases
`Phi_f(.,y)`.

Because `Phi_f` is concave on `P_f`, a global minimum is attained at an
extreme point.  The proof target is therefore:

```text
Every CAGE KKT obstruction can be replaced by a 2x2-closed extreme routing.
Every 2x2-closed extreme routing satisfies the global y-dependent CAGE
inequality, with equality only in odd-cycle blow-up extremals.
```

The missing mathematical step is a Monge/uncrossing theorem for shortest
geodesic gates: a 2x2-closed obstruction should force a laminar corridor
structure; triangle-freeness should then make the only tight laminar structure
an odd-cycle blow-up.

## Exact 2x2 derivative

For a fixed `f` and `y`, write the layer weights as

```text
w_i = sum_{v in I_i(f)} y_v p_f(v).
```

For a gate `g`, write

```text
A_g = A_g^y,
B_g = B_g^y,
r_g = sqrt(B_g/A_g)
```

whenever both sides are positive.

Consider layer pairs

```text
p=(i,j),    q=(k,l)
```

and gates `g,h`.  A 2x2 swap of size `eps` from `(p,g),(q,h)` to
`(p,h),(q,g)` changes the objective derivative at `eps=0` by

```text
dPhi/deps
= (w_k-w_i)(r_g-r_h)
  + (w_l-w_j)(1/r_g-1/r_h)
```

or equivalently

```text
dPhi/deps
= (r_g-r_h)
   [ (w_k-w_i) - (w_l-w_j)/(r_g r_h) ].
```

Thus 2x2-closure gives the following single-crossing condition:

if `alpha_{p,g}>0`, `alpha_{q,h}>0`, all four variables exist, and
`r_g>r_h`, then

```text
w_k r_g r_h - w_l >= w_i r_g r_h - w_j.
```

If both crossed supports are positive as well, equality holds.  Therefore
for each ordered gate pair `(g,h)`, the support of a closed route is monotone
with respect to the scalar score

```text
score_{g,h}(i,j) = w_i r_g r_h - w_j.
```

This is the concrete Monge/uncrossing invariant to prove from, or to use as
the KKT signature of a hypothetical obstruction.

## Local evidence

Existing scripts:

```text
_codex_cage_2swap_closure.py
_codex_cage_2swap_batch.py
_codex_cage_ydep_opt.py
_codex_cage_exact.py
```

Fresh checks:

```text
_codex_cage_2swap_batch.py --n 8 --limit 50: positives=0
_codex_cage_2swap_batch.py --n 9 --limit 80: positives=0
_codex_cage_2swap_batch.py --n 10 --limit 500: positives=0
I?BD@g]Qo y-dependent:
  alpha0 gap       = +0.027634728
  adaptive CAGE gap = -0.009481126
```

Monge derivative diagnostics after greedy 2x2 closure:

```text
H?AFBo]          closed gap = -0.229306611, checks=27,  violations=0
I?BD@g]Qo        closed gap = -0.015876099, checks=107, violations=0
I?ABCc]}?        closed gap = -0.257478345, checks=62,  violations=0
J???E?pNu?[2]    closed gap = -0.233656621, checks=907, violations=0
C5[4,3,4,3,4]   closed gap = -0.146889614, checks=3061, violations=0
```

The brute nonuniform `C5[5,4,5,4,5]` diagnostic is too slow without quotient
compression; it was stopped after path enumeration dominated runtime.  The
scale test for this route should therefore be quotient/symmetry reduced, not
raw path enumeration.

Class-symmetric quotient scale check:

```text
_codex_cage_c5quot_ydep.py --k 2 --kmax 20
```

For `C5[k+1,k,k+1,k,k+1]` with the gamma-min cut leaving one adjacent pair
bad, the class-symmetric per-bad-edge quotient has only 20 variables
`beta_{i,j,t}`.  The sweep found no positive quotient gaps:

```text
k=2  N=13   gap=-0.123656431562
k=5  N=28   gap=-0.0536277602524
k=10 N=53   gap=-0.0261177512174
k=16 N=83   gap=-0.0160969433894
k=20 N=103  gap=-0.0128099659184
```

For `k>=3`, the sampled worst class-symmetric `y` was the uniform class
vector.  In that case all layer weights are equal, every feasible quotient
routing has the same conic cost, and the normalized gap is exactly

```text
20 k(k+1) / (20 k^2 + 25 k + 9) - 1
= -(5k+9)/(20 k^2 + 25 k + 9).
```

So the C5 quotient approaches zero from below rather than developing the
large-scale failure that killed the fixed-coefficient Schur/harvest routes.

A stronger fixed-ratio quotient scout also passes:

```text
_codex_cage_c5quot_fixed.py --k 2 --kmax 20
```

This asks for one quotient routing and one ratio per gap type that work for
all class-symmetric `y` simultaneously.  It found `eta<1` throughout:

```text
k=2   eta=0.922198734694
k=5   eta=0.958708402800
k=10  eta=0.978791671056
k=16  eta=0.985883424564
k=20  eta=0.988245564477
```

In the returned solutions all five class budget ratios are balanced at the
common value `eta` (up to numerical tolerance).  This is now the sharper
quotient proof object: derive the balanced five-class certificate formula,
then explain it as the C5 equality-stability model of the general Monge/KKT
core.

An even simpler exact-testable quotient lemma emerged.  The following
rational gap ratios make the eta-one quotient LP feasible for every tested
`2<=k<=1000` with exact `Fraction` verification:

```text
r_0 = r_2 = (k-1/2)/k,
r_1 = r_3 = k/(k-1).
```

Equivalently, clearing halves,

```text
r_0 = r_2 = (2k-1)/(2k),
r_1 = r_3 = k/(k-1).
```

For these fixed rational ratios, the 20-variable quotient LP with target
`eta=1` has been checked by `_codex_cage_c5quot_half_exact.py` for
`k=2,...,1000`.  The checker uses an exact `Fraction` verifier after repairing
the floating LP support as a rational linear system.

The beta support still changes with `k`, so the next algebraic task is not to
overfit one LP vertex but to prove the rational feasibility family, either by:

1. a closed-form beta solution depending on `k`, or
2. a Farkas-dual proof that no class-load obstruction exists.

An earlier half-offset candidate

```text
r_0=r_2=(2k-2)/(2k-1), r_1=(2k-2)/(2k-3), r_3=(2k+1)/(2k-1)
```

verified only up to `k=103` and failed at `k=104`; it should not be used as a
universal formula.

#### Explicit large-k beta

For the universal ratios above, there is a very simple constant beta
certificate for all `k>=5`.

Use the forced adjacent-pair routes

```text
beta_{0,1,0}=beta_{1,2,1}=beta_{2,3,2}=beta_{3,4,3}=1.
```

Use

```text
beta_{0,2,0}=1/12,      beta_{0,2,1}=11/12,
beta_{2,4,2}=11/12,     beta_{2,4,3}=1/12,
```

and

```text
beta_{0,3,0}=1,
beta_{1,3,2}=1,
beta_{1,4,1}=1,
beta_{0,4,3}=1.
```

All other beta variables are zero.  The pair marginals are immediate.  The
gap marginals are:

```text
gap 0: 1 + 1 + 1/12  = 25/12,
gap 1: 1 + 1 + 11/12 = 35/12,
gap 2: 1 + 1 + 11/12 = 35/12,
gap 3: 1 + 1 + 1/12  = 25/12.
```

With class order `[A0,A1,A2,A3,A4]` and layer-to-class map
`[A0,A4,A3,A2,A1]`, the five class-load slacks
`size_c cap_c - load_c` factor as:

```text
c0: (k+1)(51k-97) / (24(k-1)),
c1: (15k^2+50k-37) / (12(2k-1)),
c2: (k+1)(k^2-5k+3) / ((k-1)(2k-1)),
c3: (36k^3+73k^2-182k+69) / (24(k-1)(2k-1)),
c4: (k+1)(4k^2-15k+7) / (2(k-1)(2k-1)).
```

These are all positive for `k>=5`.  Therefore the nonuniform C5 quotient has
an explicit fixed-ratio class certificate for all `k>=5`.  The small cases
`k=2,3,4` are covered by the exact Fraction checker using different beta
vertices.

### Orbit-concavity reduction for clone blow-ups

The class-symmetric quotient is more than a heuristic for this family.

Let a clone-permutation group `G` act on a configuration, preserving the CAGE
polytope and the capacity vector `cap`.  For a fixed feasible routing `alpha`,
the y-dependent CAGE cost

```text
F_alpha(y) = sum_g 2 sqrt((A_g.y)(B_g.y))
```

is concave and homogeneous in `y`, while `cap.y` is linear and `G`-invariant.
If `alpha_bar` certifies the orbit average

```text
y_bar = |G|^{-1} sum_{sigma in G} sigma y,
```

then

```text
|G|^{-1} sum_sigma F_alpha_bar(sigma y)
<= F_alpha_bar(y_bar)
<= cap.y_bar = cap.y.
```

Hence some `sigma` satisfies

```text
F_alpha_bar(sigma y) <= cap.y.
```

Pulling the routing back by `sigma` gives a feasible certificate for the
original `y`.

Thus, for clone blow-ups with a fully symmetric quotient certificate, it is
enough to prove the quotient inequality for class-symmetric `y`.  This does
not solve general graphs, but it closes the specific large-scale C5
guardrail without enumerating clone-asymmetric weights.

Rejected ansatz:

```text
r_{f,i,j} = sqrt(c_j/c_i),
c_i = sum_{v in I_i(f)} (N-S(v)) p_f(v)
```

This layer-aggregate rule fails on hard cases:

```text
I?BD@g]Qo        gap = +1.464367
I?ABCc]}?        gap = +4.058140
J???E?pNu?[2]    gap = +9.815808
```

So the adaptive routing must use the internal distribution of `y` inside
layers and corridors, not only layer aggregate slack.

## Next exact gate

For each exact CAGE certificate and each sampled hard `y`, test whether after
minimizing `Phi_f(.,y)` over each `P_f`:

1. every chosen route can be made 2x2-closed;
2. the global y-dependent CAGE gap is nonpositive;
3. zero gap occurs only when `Gamma=N^2` and the cut is an odd-cycle blow-up
   equality configuration.

The proof should target the corresponding obstruction:

```text
positive y-dependent CAGE gap
=> 2x2-closed extreme transport core
=> non-laminar or non-pentagonal corridor
=> a valid max-cut / Gamma-minimality contradiction.
```
