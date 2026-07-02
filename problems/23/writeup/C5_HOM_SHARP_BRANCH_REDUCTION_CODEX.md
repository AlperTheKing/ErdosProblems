# C5-HOM Sharp Branch Reduction Notes

Status: live proof-frontier notes, not a proof.

## Context

Claude's C5-RS split shows all tightness in census `N<=11` lies in C5-HOM K-components. The exact tight branch is weighted pentagonal/C5-HOM stability; the non-C5-HOM branch is separate and still needs a genuine bound or superstructure reduction.

The census overloaded rows occur in two `N=10` seeds:

```text
I?BD@g]Qo    equality seed, covered by seven-cut algebra.
I?`FAo]]?    sibling seed.
```

The sibling seed contains the equality seed as a spanning subgraph plus one extra blue edge for 14 of its 16 overloaded rows. The remaining 2 rows are residual-low rows with `I=152/15`.

## Dead Subtarget: Simple Blue-Edge Monotonicity

Proposed but now exact-falsified:

```text
If a sibling overloaded row is an equality-row supergraph with one extra blue edge, then the weighted row-overlap I_sib is always <= I_eq under the pulled-back weights.
```

New gate:

```text
python problems/23/writeup/_codex_ocpms_sibling_weighted_monotonicity.py \
  --mode exhaustive --max-weight 3 --require-qmax --require-over-sib
```

Counterexample:

```text
weights_sib = [3,1,3,3,1,3,3,3,3,3]
eq_side = 0101111000, eq_P = (7,5,8,6,9)
sib_side = 1111000010, sib_P = (4,8,6,1,9)
extra blue edge = (3,7)
I_eq  = 232/9
I_sib = 1651/63
gap   = I_eq - I_sib = -3/7
```

The counterexample is a valid weighted quotient case under the gate filters:

```text
both quotient cuts are maximum,
sibling row is overloaded: I_sib - N = 13/63 > 0.
```

But it is very far from the desired PMS/C5-LIFT boundary:

```text
N = 26,
m = 15,
eta = 301/25,
I_sib - N = 13/63,
C5-LIFT margin = (2/3)eta - (I_sib-N) = 12317/1575.
```

So the simple monotonicity lemma is too strong and false, but the failing region is low-ratio / high-slack. The sibling proof should not try to dominate every sibling row by an equality row. It should instead prove a separate sibling stability inequality, or use monotonicity only after adding a near-tightness hypothesis.


## Direct Weighted C5-LIFT Quotient Gate

After simple monotonicity failed, I added a direct quotient gate that computes the actual row loads `s_i` and C5-LIFT margin for every length-5 quotient row under weighted blow-ups.

Gate file:

```text
problems/23/writeup/_codex_c5lift_weighted_quotient_gate.py
```

Commands and results:

```text
python problems/23/writeup/_codex_c5lift_weighted_quotient_gate.py --graph sib --mode exhaustive --max-weight 2 --require-qmax --only-length5
# checked_rows=43286, min_lift=1/3, first_fail=None

python problems/23/writeup/_codex_c5lift_weighted_quotient_gate.py --graph eq --mode exhaustive --max-weight 2 --require-qmax --only-length5
# checked_rows=45710, min_lift=0 at equality atom, first_fail=None

python problems/23/writeup/_codex_c5lift_weighted_quotient_gate.py --graph sib --mode random --samples 5000 --max-weight 30 --require-qmax --only-length5
# checked_rows=69271, min_lift=534006463/7368348, first_fail=None

python problems/23/writeup/_codex_c5lift_weighted_quotient_gate.py --graph eq --mode random --samples 5000 --max-weight 30 --require-qmax --only-length5
# checked_rows=59664, min_lift=5646213811/71550600, first_fail=None
```

Interpretation:

```text
simple monotonicity: false,
direct sibling weighted C5-LIFT stability: exact-supported so far,
equality seed: tight only at the expected equality atom in the tested range.
```

The next proof target for the sibling branch should be direct weighted stability, not domination by the equality atom.

## Surviving Sharp-Branch Split

1. Equality seed: seven-cut algebra remains the tight equality-atom route.
2. Sibling strict-supergraph rows: simple monotonicity is false; need either
   - a near-tight monotonicity statement, or
   - a direct weighted sibling stability certificate.
3. Sibling residual-low rows: already have explicit denominator pattern `(5,5,3)` and unweighted margin; need weighted version or a structural coarse bound.
4. Non-C5-HOM rows: separate branch; current small census shows no exact tightness, but Claude scale stress shows the margin can shrink, so constant-slack closure is not available.

## Current Gate Files

```text
_codex_ocpms_sibling_embedding.py        # 14/16 strict supergraph rows
_codex_ocpms_sibling_delta.py            # unweighted contribution deltas
_codex_ocpms_residual_low_dump.py        # two residual-low rows
_codex_ocpms_sibling_weighted_monotonicity.py  # weighted monotonicity gate; false globally
```




## 2026-07-01 direct weighted quotient stress update

Script:
`problems/23/writeup/_codex_c5lift_weighted_quotient_gate.py`

Candidate checked:
`row_sum(Q) + inactive_deficit(Q) <= N + (2/3) eta`, where `tau=5m/N`, `eta=N^2/25-m`, and `inactive_deficit=sum_{i:s_i<=tau}(tau-s_i)`.

Random stress, qmax cuts only, length-5 rows only, 20,000 random weight vectors with weights in `[1,100]`:

Equality seed `I?BD@g]Qo`:
- command: `python problems\23\writeup\_codex_c5lift_weighted_quotient_gate.py --graph eq --mode random --samples 20000 --max-weight 100 --require-qmax --only-length5`
- checked rows: 225070
- first_fail: None
- min_lift: `16472865450719201/35314116871905`
- verdict: PASS

Sibling seed `I?`FAo]]?`:
- command: `python problems\23\writeup\_codex_c5lift_weighted_quotient_gate.py --graph sib --mode random --samples 20000 --max-weight 100 --require-qmax --only-length5`
- checked rows: 265027
- first_fail: None
- min_lift: `6654143672464094509/11657460740256975`
- verdict: PASS

This does not prove C5-LIFT-PMS, but it supports the direct weighted stability target after simple equality-to-sibling monotonicity was exact-falsified.

## 2026-07-01 exhaustive max-weight-3 direct quotient stress

Same script and candidate as above, qmax cuts only and length-5 rows only.

Equality seed `I?BD@g]Qo`:
- command: `python problems\23\writeup\_codex_c5lift_weighted_quotient_gate.py --graph eq --mode exhaustive --max-weight 3 --require-qmax --only-length5`
- checked weights: 59049
- checked rows: 1604900
- first_fail: None
- min_lift: `0`
- tight case: all weights 1, side `0001111000`, row `(7,5,8,6,9)`, `N=10`, `m=3`, `eta=1`, `tau=3/2`, `s=[2,34/15,32/15,34/15,2]`, row_sum `32/3`, inactive_deficit `0`.
- verdict: PASS

Sibling seed `I?`FAo]]?`:
- command: `python problems\23\writeup\_codex_c5lift_weighted_quotient_gate.py --graph sib --mode exhaustive --max-weight 3 --require-qmax --only-length5`
- checked weights: 59049
- checked rows: 1635313
- first_fail: None
- min_lift: `1/3`
- min case: all weights 1, side `0001111000`, row `(1,6,8,4,9)`, `N=10`, `m=3`, `eta=1`, `tau=3/2`, `s=[2,11/5,34/15,28/15,2]`, row_sum `31/3`, inactive_deficit `0`.
- verdict: PASS

## 2026-07-02 active-5 symbolic diagnostics

Added diagnostic scripts:

```text
problems/23/writeup/_codex_active5_overfull_extract.py
problems/23/writeup/_codex_active5_symbolic_margin.py
problems/23/writeup/_codex_seed_qmax_constraints.py
problems/23/writeup/_codex_active5_cone_lp.py
```

All-ones active-5 overfull rows:

```text
equality seed:
  active5_over_rows=20,
  one load profile s=[2,34/15,32/15,34/15,2],
  row_sum=32/3, debt=2/3.

sibling seed:
  active5_over_rows=14,
  worst rows have row_sum=31/3, debt=1/3,
  lower rows have row_sum=61/6, debt=1/6.
```

For the representative sibling worst row
`side=0001111000`, `Q=(1,6,8,4,9)`, the active-5 margin numerator

```text
2*(N^2-25m)-75*(I(Q)-N)
```

has denominator

```text
w6*(w0*w4 + w3*w8 + w4*w8)
  *(w0*w4*w6 + w3*w5*w8 + w3*w6*w8 + w4*w5*w8 + w4*w6*w8)
```

and stats:

```text
raw numerator: degree 8, terms 578, negative coefficients 109, min coefficient -150.
shifted by w_i=1+x_i: terms 4579, negative coefficients 994, min coefficient -8381.
```

Thus sibling direct stability is not coefficient-positive after the basic
integer shift; max-cut/qmax constraints are essential.

The same representative side has `448` canonical qmax inequalities and `13`
that are tight at the all-ones atom.  Coefficient-cone LP probes for

```text
shifted numerator = nonnegative polynomial
                  + sum nonnegative monomial multiples of qmax slacks
```

gave:

```text
13 tight qmax slacks: degree 0,1,2,3 all infeasible.
all 448 qmax slacks: degree 0,1,2,3 all infeasible.
```

The largest run used degree `3`, all `448` qmax slacks, `128128` candidate
multiplier monomials, and was still infeasible.  So the sibling proof likely
needs a KKT/face decomposition or a structural quotient map; a low-degree
coefficientwise qmax-cone certificate is not visible here.

### True max-weight-4 sibling worst row

The exhaustive active-5 scan through weights in `[1,4]` has a worse sibling
row than the all-ones representative above:

```text
side = 0001111001
weights = (2,1,2,1,2,1,2,1,1,2)
f = (4,9)
Q = (4,8,6,1,9)
N = 15
m = 7
eta = 2
tau = 7/3
row_sum = 35971/2261
debt = row_sum - N = 2056/2261
debt / eta = 1028/2261
margin for coefficient 2/3 = 2876/6783
s = [41/17, 1293/323, 7153/2261, 443/133, 3]
```

For this true worst row the active-5 margin numerator

```text
2*(N^2-25m)-75*(I(Q)-N)
```

has bad edges `(1,7)`, `(3,9)`, `(4,9)` and denominator

```text
w8*(w1*w5 + w1*w6 + w2*w6)
  *(w0*w1*w6 + w0*w2*w6 + w1*w5*w8 + w1*w6*w8 + w2*w6*w8)
  *(w0*w4*w6 + w3*w5*w8 + w3*w6*w8 + w4*w5*w8 + w4*w6*w8)
```

with stats:

```text
raw numerator: degree 11, terms 1765, negative coefficients 337, min coefficient -600.
shifted by w_i=1+x_i: terms 26942, negative coefficients 5366, min coefficient -116133.
```

At the true worst integer point the side has `448` canonical qmax inequalities
and `14` active tight constraints.  Degree-1 coefficient-cone probes failed
both with the `13` all-ones tight slacks and with all `448` qmax slacks:

```text
tight slacks degree 1: infeasible.
all qmax slacks degree 1: infeasible.
```

This strengthens the conclusion above: the sibling active-5 certificate is not
a low-degree qmax-cone identity on the obvious representatives.  The next
reasonable finite proof target is a qmax-face/KKT decomposition or a structural
map reducing every overfull row to the equality seed atom plus nonnegative
face slack.

### One true-worst qmax face closes exactly

For the true max-weight-4 worst record above, the `14` tight qmax constraints
have exact gradient rank `8`, leaving a two-dimensional tangent space.  More
importantly, the tight equalities themselves reduce the positive-weight face to
the following two-parameter form:

```text
(w0,w1,w2,w3,w4,w5,w6,w7,w8,w9)
= (2b, a, 2b, b, a+b, b, a+b, b, a, a+b).
```

This comes from the displayed tight qmax equalities:

```text
w9 = w7 + w8,
w4 = w1 + w3,
w2 = 2 w3,
w0 = 2 w7,
w6 = w4,
w5 = w3,
w1 = w8,
w7 = w3.
```

On this face the row is automatically active at all five vertices:

```text
load(v)-tau > 0
```

for every `v in Q=(4,8,6,1,9)` and every `a,b>0`.  With the quotient integer
domain `w_i>=1`, this face has `a>=1` and `b>=1`.

The active-5 margin on this face is

```text
2*(N^2-25m)-75*(I(Q)-N)
= 50*b^10*(b*A(x)-C(x)) / positive_denominator,
```

where `x=a/b`,

```text
A(x)=2x^9+32x^8+204x^7+668x^6+1224x^5
     +1304x^4+800x^3+256x^2+32x,

C(x)=6x^8+63x^7+255x^6+552x^5+780x^4
     +756x^3+480x^2+168x+24.
```

Thus it remains to prove `b*A(x)-C(x)>=0` under `a,b>=1`.

If `x>=1`, then `b>=1`, so it is enough to prove `A(x)-C(x)>=0`.  This is
immediate after shifting `x=y+1`, since

```text
A(y+1)-C(y+1)
= 2y^9 + 44y^8 + 421y^7 + 2296y^6 + 7819y^5
 + 17086y^4 + 23679y^3 + 19728y^2 + 8695y + 1438.
```

If `0<x<=1`, then `a=xb>=1` gives `b>=1/x`, so it is enough to prove
`A(x)-x*C(x)>=0`.  Equivalently

```text
A(x)-x*C(x)
= -x*(4x^8+31x^7+51x^6-116x^5-444x^4
      -548x^3-320x^2-88x-8).
```

The polynomial in parentheses is negative on `[0,1]`.  A compact certificate is
that its negative has degree-8 Bernstein coefficients

```text
8, 19, 290/7, 1191/14, 5812/35, 4325/14, 15313/28, 7331/8, 1438,
```

all strictly positive.  Hence `A(x)-x*C(x)>=0` for `0<=x<=1`.

Therefore the active-5 `2/3` stability inequality is proved on this complete
two-parameter qmax face.  This is not yet a proof of the whole sibling seed,
but it is a concrete KKT-face leaf certificate for the worst observed
weight-orbit.

Verifier:

```text
python problems/23/writeup/_codex_active5_face_cert.py
PASS true-worst sibling active5 qmax-face certificate
```

## 2026-07-02 S7 sibling atom from GPT-Pro

GPT-Pro proposed a smaller algebraic replacement for the representative sibling
row

```text
side = 0001111000
Q = (1,6,8,4,9)
```

using only seven qmax-derived slacks.  Relabel

```text
(a,b,c,d,e,f,x,y,u,v) = (w0,w3,w4,w5,w6,w8,w1,w2,w7,w9).
```

Then the bad products are

```text
m = xu + xv + yv,
N = a+b+c+d+e+f+x+y+u+v.
```

Define

```text
Y = ac + bf + cf,
Z = eY + df(b+c),

A = bd+cd+df+ac+ae+bf+be+cf+ce+ef,
B = ac+ae+bf+be+cf+ce+ef.
```

Exact symbolic path enumeration gives

```text
I(Q)-N = x(u+v)A/Z + yvB/(eY) - (a+b+c+d+e+f).
```

The proposed S7 lemma is:

```text
all variables >= 1,

s1 = e-v >= 0,
s2 = d+e-u-v >= 0,
s3 = b+c-x-y >= 0,
s4 = ac+bf+cf-m >= 0,
s5 = ae+bf+cf-m >= 0,
s6 = ac+df+ef-m >= 0,
s7 = ae+df+ef-m >= 0

==>

2(N^2-25m) - 75(I(Q)-N) >= 0.
```

This proves the active-5 `2/3` stability for this row because the full qmax
constraints imply `s1,...,s7 >= 0`.

Partial exact checks:

```text
python problems/23/writeup/_codex_sib_s7_gate.py
PASS S7 identity and central KKT face
```

The script verifies the path identity above and the central seven-tight KKT
face

```text
b=d=f=u=y=1,
c=e=x=v=t,
a=t+1-1/t,
t>=1.
```

On this face

```text
Phi(t) = [20t^7 - 18t^6 - 166t^5 + 76t^4 + 459t^3
          +117t^2 -117t + 4]
         / [t^2(t+2)(t^3+2t^2+t+1)].
```

The numerator has value `375` at `t=1` and Sturm root count `0` on `[1,∞)`,
so this central face is positive.  A bounded numerical falsifier search over
the S7 region found no negative value; best observed `Phi` was about `2.4569`
near this central face.

Exact integer grids also found no S7 failure.  The Python/Fraction gate covered
`[1,4]`; the C++ exact cross-multiplied gate then covered `[1,5]` and `[1,6]`:

```text
B = 4: checked = 1048576,  feasible = 229898,   best Phi = 25
B = 5: checked = 9765625,  feasible = 1986447, best Phi = 25
B = 6: checked = 60466176, feasible = 11714321, best Phi = 25
B = 8: checked = 1073741824, feasible = 195658681, best Phi = 25
best point = all-ones in all four grids
```

This is not a proof of S7, but it identifies a compact next exact gate: prove
S7 for the 10-variable seven-slack semialgebraic region, or find a rational
counterexample.

Additional face-discovery evidence:

```text
If Phi<0 at a feasible point, uniform down-scaling all ten variables preserves
the seven S7 inequalities and preserves Phi<0 until some variable reaches 1.
So any counterexample has at least one variable equal to 1.

SLSQP scans of the ten var=1 faces:
  low faces: b=1, d=1, f=1, y=1, u=1
    all flow to the central seven-tight curve above, min Phi ~= 2.4307.
  high faces: a=1, c=1, e=1, x=1, v=1
    all flow to the all-ones atom, min Phi ~= 25.
```

The next exact proof target is therefore a two-class face certificate:

1. prove the five high faces have `Phi >= 0`, preferably by shifted/Bernstein
   positivity after clearing the positive denominator;
2. prove the five low faces reduce to the already-closed central seven-tight
   curve, or close their residual KKT leaves directly.

One additional KKT curve is already closed.  On the `a=1` high face, the
all-seven-tight numerical minimizer lies on

```text
a=b=d=u=y=1,
c=e=x=v=f=t,
t>=1.
```

There

```text
Phi(t) = 25(2t^3 + 4t^2 + 5t + 4) / ((t+2)(t^2+3t+1)),
```

which is strictly positive for `t>=1`.

There is also a useful fixed-core endpoint reduction.  For fixed
`a,b,c,d,e,f`, put

```text
C0 = a+b+c+d+e+f,
p = A/Z,
q = B/(eY),
Mcap = min(Y, ae+bf+cf, ac+df+ef, ae+df+ef).
```

Then the S7 endpoint variables satisfy only

```text
x,y,u,v >= 1,
v <= e,
u+v <= d+e,
x+y <= b+c,
m = xu+xv+yv <= Mcap,
```

and

```text
Phi =
2(C0+x+y+u+v)^2 + 75C0
- 50(xu+xv+yv)
- 75p x(u+v)
- 75q yv.
```

Thus, for a fixed core, the nonlinear part is a four-variable KKT problem with
linear endpoint faces and at most one active quadratic cap `m=Mcap`; the four
original nonlinear S7 inequalities enter only through `Mcap`.

Exploratory fixed-core endpoint scans support this reduction.  On 2,000 random
cores, the endpoint minimizer signatures were dominated by

```text
y=1, v=e, m=Mcap,
```

with either `x+y=b+c`, `u+v=d+e`, or `u=1` as the remaining active endpoint
condition.  The scan is not an acceptance gate, but it narrows the KKT leaves
that need exact treatment.

## GPT-Pro compact FJ-S7 gate

GPT-Pro's next suggested exact route is to avoid unbounded KKT by compactifying
S7.  Normalize the old variables by the old total `N_old`, and add

```text
theta = 1 / N_old.
```

Thus the normalized variables satisfy

```text
a+b+c+d+e+f+x+y+u+v = 1,
a,b,c,d,e,f,x,y,u,v >= theta,
theta >= 0.
```

Keep the same homogeneous definitions

```text
m = xu+xv+yv,
Y = ac+bf+cf,
Z = eY+df(b+c),
A = bd+cd+df+ac+ae+bf+be+cf+ce+ef,
B = ac+ae+bf+be+cf+ce+ef.
```

Then define the compact numerator

```text
P =
2 e Y Z (1 - 25m)
- 75 theta ( eY x(u+v) A + Z yv B - eYZ(a+b+c+d+e+f) ).
```

For every finite old feasible point,

```text
P = eYZ theta^2 Phi.
```

Since `eYZ>0`, proving `P>=0` on the compact normalized feasible set proves
S7.

The compact constraints are:

```text
H := a+b+c+d+e+f+x+y+u+v-1 = 0,

theta >= 0,
a-theta >= 0, ..., v-theta >= 0,

e-v >= 0,
d+e-u-v >= 0,
b+c-x-y >= 0,
Y-m >= 0,
ae+bf+cf-m >= 0,
ac+df+ef-m >= 0,
ae+df+ef-m >= 0.
```

There are `18` inequalities.  If S7 is false, `P` attains a negative minimum
on this compact set.  At such a minimum Fritz-John stationarity gives, for
some active set `A` of inequalities,

```text
lambda0 grad(P) - sum_{g in A} lambda_g grad(g) + mu grad(H) = 0,
lambda0 >= 0, lambda_g >= 0,
lambda0 + sum_{g in A} lambda_g = 1.
```

Strict negativity can be encoded algebraically by an auxiliary `r`:

```text
-P r^2 - 1 = 0.
```

By conic Caratheodory on the tangent space `H=0`, it is enough to check
active sets of size at most `11`.  The resulting exact finite gate is:

```text
For every active set A among the 18 inequalities with |A|<=11,
the real semialgebraic system

  H=0,
  g=0 for g in A,
  all compact inequalities g>=0,
  -P r^2 - 1 = 0,
  FJ stationarity and nonnegative multipliers

has no real solution.
```

The central positive-dimensional face already found numerically is the old
seven-tight curve.  It is separately closed by the exact Sturm certificate
above.

Sanity check on the compact boundary: at `theta=0`, a random feasible search
found no `P<0`, and a targeted SLSQP maximization of `m=xu+xv+yv` over the
normalized S7 constraints gave

```text
max m = 1/25
```

with all seven S7 slacks tight.  Since `P=2eYZ(1-25m)` on `theta=0`, this
supports the compactification: the escape boundary appears to be exactly the
C5 extremal boundary, not a spurious negative component.

## Exact theta=0 compact boundary lemma

The compact S7 boundary at `theta=0` is now covered by a short exact AM-GM argument.  On `theta=0` put

```text
A = a+f,    B = b+c,    D = d+e,
P = x+y,    Q = u+v,    m = xu+xv+yv.
```

The normalized total is

```text
A+B+D+P+Q = 1.
```

The S7 constraints imply

```text
P <= B,
Q <= D,
m <= P Q,
m <= ac+bf+cf <= (a+f)(b+c) = A B,
m <= ae+df+ef <= (a+f)(d+e) = A D.
```

Let `t=sqrt(m)`.  Then

```text
P+Q >= 2t,
A+B >= 2t,
A+D >= 2t.
```

If `A >= t`, then

```text
1 = A+B+D+P+Q >= A+2(P+Q) >= 5t,
```

because `B+D >= P+Q`.  If `A <= t`, then

```text
(A+B)+(A+D)+(P+Q) >= 6t
```

gives

```text
1+A >= 6t,
```

and hence again `1 >= 5t`.  Therefore `m=t^2 <= 1/25`.

Consequently, at `theta=0`,

```text
P_compact = 2 e Y Z (1-25m) >= 0.
```

The exact witness script is

```text
python problems/23/writeup/_codex_sib_s7_theta0_boundary.py
```

and the equality boundary is the expected five-block C5 extremal:

```text
b=d=u=0,
c=e=v=x+y=1/5,
a+f=1/5.
```

## Exact S7 scaling-to-lower-bound-face reduction

The theta-positive part also has an exact homogeneity reduction.  Write

```text
D = N^2 - 25m,
E = x(u+v)A/Z + yvB/(eY) - (a+b+c+d+e+f),
Phi = 2D - 75E.
```

Under uniform scaling by `lambda>0`, the S7 constraints stay feasible and

```text
D(lambda w) = lambda^2 D(w),
E(lambda w) = lambda E(w),
Phi(lambda w) = lambda(2 lambda D(w) - 75 E(w)).
```

The five-block AM-GM argument above is homogeneous, so every S7-feasible point
satisfies `D>=0`.  Hence if `Phi(w)<0`, then `E(w)>0`, and for every
`0<lambda<=1`,

```text
Phi(lambda w) <= lambda Phi(w) < 0.
```

Therefore any negative S7 counterexample can be uniformly scaled down until
one of the ten variables hits its lower bound `1`.  It is enough to prove S7
on the ten lower-bound faces

```text
a=1, b=1, c=1, d=1, e=1, f=1, x=1, y=1, u=1, v=1.
```

The exact witness script is

```text
python problems/23/writeup/_codex_sib_s7_scaling_reduction.py
```

which verifies the symbolic scaling identities and slack homogeneities.


## Exact endpoint-fiber reduction to fourteen S7 faces

GPT-Pro's theta-positive endpoint reduction is now checked by the exact script

```text
python problems/23/writeup/_codex_sib_s7_endpoint_fiber.py
```

Freeze

```text
a,b,c,d,e,f, p=x+y, q=u+v, theta.
```

Then set

```text
x=p-y,
v=q-u,
S=a+b+c+d+e+f,
m=pq-yu,
alpha=A/Z,
beta=B/(eY).
```

The compact numerator satisfies the exact identity

```text
P_compact/(eYZ) = C + K*y*u - H*y,
```

where

```text
C = 2 - 50pq - 75 theta alpha pq + 75 theta S,
K = 50 + 75 theta beta > 0,
H = 75 theta (beta-alpha)q.
```

The frozen endpoint fiber is

```text
theta <= y <= p-theta,
L <= u <= U,
L=max(theta,q-e),
U=q-theta,
yu >= R := pq - M*,
M* = min(M4,M5,M6,M7),
```

with

```text
M4=Y,
M5=ae+bf+cf,
M6=ac+df+ef,
M7=ae+df+ef.
```

For fixed `y`, the expression is strictly increasing in `u`, since

```text
d/du(P_compact/(eYZ)) = K y > 0.
```

Thus the minimizing `u` is

```text
u(y)=max(L,R/y).
```

On the `u=R/y` branch the objective is linear in `y`, and on the `u=L`
branch it is also linear in `y`.  Therefore a negative compact point can be
moved, without increasing `P_compact`, to an endpoint or kink.  Together with
the already closed `theta=0` boundary, S7 reduces to the following fourteen
faces:

```text
y=theta,
x=theta,

for j in {4,5,6,7}:
    s_j=0 and u=theta,
    s_j=0 and v=theta,
    s_j=0 and v=e.
```

Here `s4=Y-m`, `s5=ae+bf+cf-m`, `s6=ac+df+ef-m`, `s7=ae+df+ef-m`, and
`v=e` is the linear face `s1=0`.  This replaces the raw compact-FJ support
search (`121670` theta-positive multiplier supports after excluding theta=0)
by fourteen exact real-algebraic emptiness checks.

## Exact seven-tight `y=1` manifold certificate

The hardest 14-face numerical minima land on the all-seven-tight manifold with
`y=1`.  This stratum is now closed by

```text
python problems/23/writeup/_codex_sib_s7_seventight_y1.py
```

On the all-seven-tight manifold with `y=1`, the equations give

```text
d=b,
e=c,
u=b,
v=c,
x=b+c-1,
a=((b+c)^2-b-f(b+c))/c,
1 <= f <= b+c-1.
```

First parameterize

```text
b=1+B,
c=1+C,
f=1+r(b+c-2),     0<=r<=1.
```

The numerator of `dPhi/db` has Bernstein coefficients in `r`; every one is a
coefficient-positive polynomial in `B,C`.  Hence `Phi` is increasing in `b` on
this stratum, so the minimum occurs at `b=1`.

With `b=y=1`, parameterize

```text
c=1+C,
f=1+rC,           0<=r<=1.
```

The numerator of `Phi` has degree `3` in `r`.  Its Bernstein coefficient at
`r=0` is the already known central curve

```text
P0(t)/(t^2(t+2)(t^3+2t^2+t+1)),
P0(t)=20t^7-18t^6-166t^5+76t^4+459t^3+117t^2-117t+4,
```

with `P0(1)=375` and `SturmRoots(P0,[1,infty))=0`.  The other three Bernstein
coefficients are coefficient-positive polynomials in `C`.  Therefore
`Phi>=0` on the entire all-seven-tight `y=1` manifold.

## Codex Refined Endpoint-Fiber Split

`_codex_sib_s7_endpoint_refine.py` verifies a smaller exact face reduction for the compact S7 atom.  The endpoint-fiber identity

```text
P/(eYZ) = C + K*y*u - H*y,        K = 50 + 75 theta B/(eY) > 0
```

was already used to reduce a negative compact point to fourteen faces.  On either broad endpoint face `y=theta` or `x=theta` (that is, `y=p-theta`), the endpoint coordinate `y` is fixed and positive, so the same identity is strictly increasing in `u`.

Thus the two broad endpoint faces can be replaced by smaller two-equation faces:

```text
y=theta and (u=theta or v=e or s_j=0 for j=4,5,6,7),
x=theta and (u=theta or v=e or s_j=0 for j=4,5,6,7).
```

Together with the original interior/kink endpoint faces, the S7 theta-positive search now has no one-equation broad faces: all remaining branches have at least two active endpoint/capacity equations.  This is still only a reduction, not a closure of the remaining branches.
