# PMS-5 hard-face diagnostic

Status: exact diagnostic, not a proof.

The active frontier is the equal-length `L=5` multi-geodesic branch.  The
seven-cut OC-PMS atom is:

```text
75*(I(P)-N) <= 2*(N^2 - 25m)
```

for positive integer weights satisfying the seven quotient cut inequalities in
`_codex_ocpms_sevencut_gate.py`.

## Exact checks

Exhaustive integer box:

```text
python problems/23/writeup/_codex_ocpms_hard_reservoir_diag.py --max-weight 5 --keep 12
```

Result:

```text
selected=1722795
crude_neg=679853
first_fail=none
```

The closest reservoir compensation case in the `1..5` box is:

```text
w=(1,1,1,1,1,5,5,5,5,5)
active: all seven cut inequalities tight
f0=-4100
reservoir=1183400/287
margin=6700/287
reservoir/(-f0)=11834/11767
```

Random stress:

```text
samples=300000
max_weight=100
selected=36911
crude_neg=21575
first_fail=none
```

No random case was closer than the saturated all-seven-tight ray below.

## Saturated hard ray

For

```text
w(t)=(1,1,1,1,1,t,t,t,t,t)
```

all seven cut inequalities are tight for `t>=1`.  In the decomposition

```text
F = F0 + R19 + R27 + R79
```

where `F0` uses the crude coefficient caps
`c19,c27<=7/3` and `c79<=2`, exact symbolic simplification gives:

```text
F0 = -25*(t-1)*(6*t+11)

R19 = 25*(t-1)*(7*t+12)/(t+2)
R27 = 25*(t-1)*(7*t+12)/(t+2)
R79 = 75*t*(t-1)*(2*t^2+5*t+1)/(t^2+3*t+1)

F = 25*(t-1)*(2*t^2+3*t+2)/((t+2)*(t^2+3*t+1))
```

Thus the margin is positive for `t>1` but the reservoir ratio is
asymptotically tight:

```text
reservoir/(-F0) - 1
= (2*t^2+3*t+2)/((t+2)*(6*t+11)*(t^2+3*t+1)).
```

The hard face is therefore not a failure of the seven-cut atom.  It is an
asymptotic near-cancellation where all seven quotient cut inequalities are
tight and the coefficient-deficit reservoirs pay exactly the crude cap deficit.

## Suggested proof subtarget

A natural finite algebraic sublemma is:

```text
Among all real weights w_i>=1 satisfying the seven cut inequalities,
any minimizer of F / (-F0) on the crude-negative region either lies on the
all-seven-tight saturated face or has strictly larger reservoir ratio.
```

For the proof, the immediate KKT leaf to attack is the all-seven-active face:

```text
w5=w9,
w6=w7,
w3+w5=w2+w9,
w4+w6=w1+w7,
D27=m,
D0=m,
D19=m.
```

The ray above is the simplest one-dimensional slice of this face and gives the
observed asymptotic hard cases.

## Exhaustive C++ extension

Exact C++ scanner:

```text
problems/23/writeup/_codex_ocpms_hard_reservoir_scan.cpp
```

It compares `reservoir/(-F0)` by integer cross-multiplication and checks the
PMS margin numerator exactly.  Results:

```text
B=6 total=60466176 selected=10032993 crude_neg=4193702 failures=0
best=(1,1,1,1,1,6,6,6,6,6) ratio=5193/5170

B=7 total=282475249 selected=44837306 crude_neg=19553005 failures=0
best=(1,1,1,1,1,7,7,7,7,7) ratio=33988/33867

B=8 total=1073741824 selected=164869281 crude_neg=74342588 failures=0
best=(1,1,1,1,1,8,8,8,8,8) ratio=26332/26255

B=9 total=3486784401 selected=521638107 crude_neg=241870821 failures=0
best=(1,1,1,1,1,9,9,9,9,9) ratio=78126/77935
```

In all four boxes the exact best crude-negative reservoir ratio is the same
all-seven-tight saturated ray.

## All-seven-active symbolic split

On the all-seven-active face, write

```text
a=w0, x=w1, y=w2, p=w5, q=w6, r=w8.
```

The first four active linear constraints give

```text
w9=p, w7=q, w3=y, w4=x.
```

The two active equations `D27=m` and `D0=m` imply `p=q=t`.  The remaining
active equations then imply

```text
(y-x)(r-t)=0.
```

So the all-seven-active face splits into two branches.

### Branch 1: `r=t`

This forces `x=y=a`, hence

```text
w=(a,a,a,a,a,t,t,t,t,t).
```

The exact PMS margin is

```text
F = 25*a^2*(4*a^3 + 14*a^2*t - 6*a^2
            + 10*a*t^2 - 15*a*t + 2*t^3 - 9*t^2)
    / ((2*a+t)*(a^2+3*a*t+t^2)).
```

After shifting `a=1+A`, `t=1+T`, the numerator factor becomes

```text
4*A^3 + 14*A^2*T + 20*A^2
+ 10*A*T^2 + 33*A*T + 23*A
+ 2*T^3 + 7*T^2 + 7*T.
```

All coefficients are nonnegative.  Thus branch 1 is closed for `a,t>=1`,
with equality only at `a=t=1`.  The hard ray found by finite search is the
subray `a=1, t>=1` inside this branch.

### Branch 2: `x=y`, `r!=t`

The active equations give

```text
x=y=t*(a+r-t)/(2*t-r).
```

The positivity domain forces `r<2t` and `a+r-t>0`.  A naive shifted expansion
with `d=2t-r`, `a=1+A`, `t=1+T`, `d=1+D` has negative coefficients, so this
branch is not closed by immediate coefficient positivity.  It is the next
all-seven-active KKT/domain subcase to attack.

## Branch 2 closure by Bernstein coefficients

Branch 2 is also algebraically closed.

Use variables `t,x,r` and solve the active relation for

```text
a = 2*x + t - r*(x+t)/t.
```

The domain `a>=1`, `t>=1`, `x>=1`, `r>=1` is equivalent to

```text
t>=1,
 x>=1,
 1 <= r <= U(t,x),
 U(t,x)=t*(2*x+t-1)/(x+t).
```

Indeed `U>=1` after shifting `t=1+T`, `x=1+X`, because

```text
t*(2*x+t-1)-(x+t)=T^2+2*T+X+2*T*X >= 0.
```

After substitution, the branch-2 PMS margin has the form

```text
F = x*P(t,r,x)
    / (t^2*(t+2*x)*(r*t*x+r*x^2+t^3+2*t^2*x)),
```

where the denominator is positive.  The numerator `P` is cubic in `r`.
Write it in the Bernstein basis over the interval `[1,U(t,x)]`:

```text
r = 1 + theta*(U-1), 0 <= theta <= 1.
```

The four Bernstein coefficients are

```text
B0 = P(1),
B1 = P(1) + (U-1)*P'(1)/3,
B2 = P(U) - (U-1)*P'(U)/3,
B3 = P(U).
```

Exact symbolic verification gives the following denominators:

```text
B0 denominator: 1
B1 denominator: 3*(t+x)
B2 denominator: 3*(t+x)^3
B3 denominator: (t+x)^3
```

After clearing these positive denominators and shifting

```text
t=1+T,
 x=1+X,
```

every numerator has only nonnegative coefficients:

```text
B0 numerator: 28 terms, 0 negative coefficients, min coefficient 20
B1 numerator: 38 terms, 0 negative coefficients, min coefficient 40
B2 numerator: 48 terms, 0 negative coefficients, min coefficient 20
B3 numerator: 47 terms, 0 negative coefficients, min coefficient 30
```

Therefore all Bernstein coefficients are nonnegative for `t,x>=1`, hence
`P(t,r,x)>=0` on the full interval `1<=r<=U(t,x)`.  This closes branch 2.

Conclusion: the entire all-seven-active PMS-5 face is closed:

- branch 1 (`r=t`) by direct shifted coefficient positivity;
- branch 2 (`x=y`) by cubic Bernstein positivity on the exact feasible interval.

## Six-active masks 125/126 closure

The active-mask scan shows the next-nearest faces after the all-seven-active
face are masks `125` and `126`.  These are symmetric; it is enough to close
mask `125`.

Mask `125` is the face where all seven quotient inequalities are active except
`w6=w7`.  Use the parametrization

```text
w5=w9=t,
 w6=t,
 w7=u,
 u<=t,
 w2=w3=w4=b,
 w1=b+t-u.
```

The active D-equations give

```text
r=w8=(b*(t+u)+t^2-a*t)/(b+t).
```

The domain `r>=1` gives the interval

```text
1 <= a <= Amax,
Amax=(b*(t+u)+t^2-b-t)/t.
```

Set `t=u+s`, with `s>=0`.  The PMS margin numerator is cubic in `a`.  In the
Bernstein basis on `[1,Amax]`, after clearing positive denominators and shifting

```text
b=1+B,
 u=1+U,
 s=S,
```

all four numerator polynomials have nonnegative coefficients:

```text
B0: 429 terms, 0 negative coefficients, min coefficient 30
B1: 525 terms, 0 negative coefficients, min coefficient 20
B2: 629 terms, 0 negative coefficients, min coefficient 40
B3: 520 terms, 0 negative coefficients, min coefficient 20
```

Repro script:

```text
python problems/23/writeup/_codex_ocpms_mask125_bernstein.py
```

prints `VERDICT PASS`.  Hence mask `125` is closed; mask `126` is closed by
left/right symmetry.

## Mask 47 partial closure

After masks `127` and `125/126`, the active-mask scan identifies masks `47/95`
as the next closest faces.  They are symmetric; work on mask `47`.

Mask `47` has active constraints

```text
w5=w9,
 w6=w7,
 linL,
 linR,
 D0=m.
```

Use variables

```text
p=w5=w9,
 q=w6=w7,
 x=w1,
 y=w2,
 r=w8,
 a=w0.
```

Then

```text
w3=y,
 w4=x,
 a=(x*p+y*q+q*p-r*(y+p))/p.
```

### Closest ray

The observed closest ray is

```text
w=(1,1,2,2,1,t-1,t,t,t,t-1),  t>=2.
```

Its exact PMS margin is

```text
F = 50*(2*t^5 + 8*t^4 + 15*t^3 + 11*t^2 - 15*t - 9)
    /(t*(t+2)*(t+3)*(t^2+2*t-1)).
```

After `t=2+T`, the numerator is coefficient-positive:

```text
100*T^5 + 1400*T^4 + 7950*T^3 + 22650*T^2 + 31250*T + 15850.
```

### Subcase `q>=p` and `p*x>=q*y`

Write

```text
q=p+s,
 x=y*q/p+h,
 s,h>=0.
```

Then `D19>=m` is automatic and `D27>=m` follows from `a>=1`.  The feasible
interval is `1<=r<=U`, where `U` is obtained from `a=1`:

```text
U=(h*p + p^2 + p*s + 2*p*y - p + 2*s*y)/(p+y).
```

The PMS margin numerator is quartic in `r`.  In the Bernstein basis on
`[1,U]`, after clearing positive denominators and shifting

```text
p=1+P,
 s=S,
 y=1+Y,
 h=H,
```

all five numerator polynomials have nonnegative coefficients:

```text
B0: 1195 terms, 0 negative coefficients, min coefficient 10
B1: 1622 terms, 0 negative coefficients, min coefficient 18
B2: 2038 terms, 0 negative coefficients, min coefficient 18
B3: 2482 terms, 0 negative coefficients, min coefficient 20
B4: 2480 terms, 0 negative coefficients, min coefficient 8
```

Repro script:

```text
python problems/23/writeup/_codex_ocpms_mask47_subcase_ge.py
```

prints `VERDICT PASS`.

### Boundary `a=w0=1` in the complementary hard side

The complementary side of mask `47` has

```text
q>=p,\qquad p*x<q*y.
```

The nearest exhaustive examples lie on the domain boundary `a=w0=1`, not on
the `D19=m` boundary.  On this boundary

```text
r=w8=(x*p+y*q+q*p-p)/(y+p).
```

Two coefficient-positive subcases are now closed.

#### Subcase `y<x`

Set

```text
q=p+s,\qquad x=y+e,\qquad y>=1,\qquad e,s>=0.
```

After substituting `a=1` and clearing positive denominators, the exact PMS
margin numerator has only nonnegative shifted coefficients after

```text
p=1+P,\qquad y=1+Y.
```

Repro script:

```text
python problems/23/writeup/_codex_ocpms_mask47_a1_y_lt_x.py
```

prints:

```text
terms 1391 negative 0 min_coeff 8
VERDICT PASS
```

#### Subcase `y>=x` and `y-x<=q-p`

Set

```text
q=p+s,\qquad x=1+h,\qquad y=x+d,\qquad s=d+e,
```

with `d,e,h>=0`.  After substituting `a=1` and clearing positive
denominators, the exact PMS margin numerator has only nonnegative shifted
coefficients after

```text
p=1+P.
```

Repro script:

```text
python problems/23/writeup/_codex_ocpms_mask47_a1_d_le_s.py
```

prints:

```text
terms 1719 negative 0 min_coeff 10
VERDICT PASS
```

#### Integer infeasibility of `y>=x` and `y-x>q-p`

Write

```text
s=q-p,\qquad d=y-x,\qquad d=s+e.
```

On the `a=1` boundary the remaining cut inequality `D19>=m` is equivalent,
after clearing the positive denominator, to

```text
h*(s-e*(2p+s))
+ s*(p+s+1)
- e*(e*(p+s)+p^2+2ps+p+s^2)
>= 0,
```

where `x=1+h`.  If the weights are integer and `d>s`, then `e>=1`.  In that
case

```text
e*(2p+s)-s >= 2p > 0,
```

and at `e=1` the constant deficit already equals

```text
p*(p+s+2)>0
```

with the same sign worsening for larger `e`.  Hence `D19>=m` is impossible.

The reduced integer diagnostic confirms the split:

```text
python problems/23/writeup/_codex_ocpms_mask47_a1_scan.py --max-weight 80
```

prints:

```text
B 80 total_a1_integer 810107 kept_hard 406129 failures 0
y<x min_margin 237876/407 w (1, 3, 2, 2, 3, 2, 4, 4, 5, 2)
y>=x,d<=s min_margin 1585/28 w (1, 1, 2, 2, 1, 1, 2, 2, 2, 1)
VERDICT PASS
```

So the entire integer `a=1` boundary of the `q>=p, p*x<q*y` complement is
closed.

## Mask 47 boundary-lift diagnostic

After closing the integer `a=w0=1` boundary of the `q>=p, p*x<q*y`
complement, the natural next sublemma is a boundary lift:

```text
F(a,x,y,p,q) >= F(1,x,y,p,q)
```

on the feasible mask47 branch, where `D0=m` determines

```text
r(a)=(x*p+y*q+q*p-a*p)/(y+p).
```

Exact integer diagnostic:

```text
python problems/23/writeup/_codex_ocpms_mask47_a_lift_scan.py --max-weight 40
```

prints:

```text
B 40 compared 303147 lower 0
best_diff 0 w (1, 1, 1, 1, 1, 1, 2, 2, 2, 1) boundary (1, 1, 1, 1, 1, 1, 2, 2, 2, 1)
VERDICT PASS
```

Strict interior diagnostic:

```text
python problems/23/writeup/_codex_ocpms_mask47_a_lift_scan.py --max-weight 35 --strict-interior
```

prints:

```text
B 35 compared 151065 lower 0
best_diff 26989/616 w (4, 1, 1, 1, 1, 2, 3, 3, 1, 2) boundary (1, 1, 1, 1, 1, 2, 3, 3, 3, 2)
VERDICT PASS
```

However, neither `dF/da>=0` nor `F(a)-F(1)>=0` is raw shifted-coefficient
positive on the `y<x` subregion:

```text
dF/da: terms 13629 negative 5322 min_coeff -2370593400
(F(a)-F(1))/(a-1): terms 11974 negative 4903 min_coeff -1185296700
```

So the lift, if true, needs to use the remaining mask47 feasibility/reservoir
inequalities rather than plain coefficient positivity.

### Multiprecision boundary-lift scan

The first C++ boundary-lift scanner used `__int128`; at `B=120` it produced a
spurious negative difference due to overflow.  The reported point

```text
w=(106,1,104,104,1,1,109,109,108,1)
boundary=(1,1,104,104,1,1,109,109,109,1)
```

was checked with Python `Fraction` and has exact positive difference

```text
484268054695365142837332732/1966381809703681858781 > 0.
```

A corrected multiprecision scanner is:

```text
problems/23/writeup/_codex_ocpms_mask47_a_lift_scan_bigint.cpp
```

Compiled and run with 64 workers:

```text
problems\23\writeup\_codex_ocpms_mask47_a_lift_scan_bigint.exe 120 64
```

prints:

```text
B 120 workers 64 compared 22659306 lower 0
best_diff 26989/616 w 4 1 1 1 1 2 3 3 1 2 boundary 1 1 1 1 1 2 3 3 3 2
VERDICT PASS
```

and

```text
problems\23\writeup\_codex_ocpms_mask47_a_lift_scan_bigint.exe 200 64
```

prints:

```text
B 200 workers 64 compared 178457920 lower 0
best_diff 26989/616 w 4 1 1 1 1 2 3 3 1 2 boundary 1 1 1 1 1 2 3 3 3 2
VERDICT PASS
```

Thus the boundary-lift conjecture has no exact integer counterexample in this
large reduced box, and the closest strict interior point is stable.

### Real strip on `a=1`, `y>=x`, `y-x>q-p`

Claude observed that the previous infeasibility argument for this bucket was
integer-only.  The real strip is now closed directly.

Write

```text
q=p+s,
 x=1+h,
 y=x+s+e.
```

On the `a=1` boundary, after clearing the positive denominator, the `D19>=m`
slack is

```text
h*(s-e*(2p+s))
+ s*(p+s+1)
- e*(e*(p+s)+p^2+2ps+p+s^2).
```

At `h=0` the positive root is

```text
e=s/(p+s).
```

For `e>s/(p+s)`, the coefficient of `h` is already negative, so the slack is
negative for every `h>=0`.  Thus the whole feasible real strip is

```text
0 <= e <= s/(p+s).
```

Set

```text
e = z*s/(p+s),        0 <= z <= 1.
```

Then the exact PMS margin numerator has degree `7` in `z`.  In the Bernstein
basis on `[0,1]`, after clearing positive denominators and shifting
`p=1+P`, every coefficient polynomial has only nonnegative coefficients:

```text
python problems/23/writeup/_codex_ocpms_mask47_a1_real_strip.py
```

prints:

```text
B 0 den 1 terms 865 negative 0 min_coeff 30
B 1 den 7 terms 865 negative 0 min_coeff 210
B 2 den 21 terms 865 negative 0 min_coeff 630
B 3 den 35 terms 865 negative 0 min_coeff 1050
B 4 den 35 terms 865 negative 0 min_coeff 1050
B 5 den 21 terms 865 negative 0 min_coeff 630
B 6 den 7 terms 865 negative 0 min_coeff 210
B 7 den 1 terms 865 negative 0 min_coeff 30
degree_z 7
VERDICT PASS
```

So the entire real `a=1` boundary of the `q>=p, p*x<q*y` complement is closed:

- `y<x` by `_codex_ocpms_mask47_a1_y_lt_x.py`,
- `y>=x, y-x<=q-p` by `_codex_ocpms_mask47_a1_d_le_s.py`,
- `y>=x, y-x>q-p` by `_codex_ocpms_mask47_a1_real_strip.py`.
