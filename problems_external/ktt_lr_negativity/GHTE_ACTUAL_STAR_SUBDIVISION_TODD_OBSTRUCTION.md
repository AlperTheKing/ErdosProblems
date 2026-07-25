# Todd pullback obstruction on the actual hive star subdivision

Date: 2026-07-22

Status: **canonical coarse-to-refined effective transport fails in codimensions
one and two.**  Both endpoint fans themselves satisfy GHTE in every degree.
This is a transport obstruction, not a counterexample to GHTE, KTT, or
Ehrhart-coefficient positivity.

## 1. Exact actual fan map

Use the rays from the rank-four wall in
`HIVE_WALL_CIRCUIT_CLASSIFICATION.md`:

```text
a=(-1,1,0),  b=(0,-1,0),  c=(-1,0,0)=a+b,
e=(1,0,0),   u=(0,0,1),   v=(1,0,-1).
```

The coarse and refined complete smooth fans have maximal cones

```text
Sigma_L: abu, abv, aeu, aev, beu, bev,
Sigma_R: acu, acv, bcu, bcv, aeu, aev, beu, bev.       (1)
```

Every maximal determinant has absolute value one.  `Sigma_R` is the star
subdivision of `Sigma_L` along `cone(a,b)` by the primitive ray `c=a+b`.
Let

```text
pi : X_R -> X_L
```

be the resulting smooth toric blowdown, and let `z=[D_c]` be its exceptional
divisor class.

## 2. Chow rings and pullback

For the coarse fan, the linear and Stanley--Reisner relations give

```text
A=B=x,   U=V=y,   E=x-y,
A*(X_L)_Q = Q[x,y]/(y^2, x^2(x-y)).                    (2)
```

For the refined fan, put `C=z`.  Then

```text
A=B=x,   U=V=y,   E=x+z-y,
A*(X_R)_Q = Q[x,y,z]/(x^2, y^2, z(x+z-y)).             (3)
```

In particular,

```text
z^2=-xz+yz.
```

The exact toric pullback is

```text
pi^*x=x+z,       pi^*y=y.                              (4)
```

This agrees with `pi^*D_a=D_a+D_c` and
`pi^*D_b=D_b+D_c` because `c=a+b`.

## 3. Todd classes in every codimension

Expanding

```text
product_rho D_rho/(1-exp(-D_rho))
```

and reducing by (2)--(3) gives

| `q` | `t_q(X_L)` | `pi^*t_q(X_L)` | `t_q(X_R)` | `t_q(X_R)-pi^*t_q(X_L)` |
|---:|---|---|---|---|
| 0 | `1` | `1` | `1` | `0` |
| 1 | `(3x+y)/2` | `(3x+y+3z)/2` | `(3x+y+2z)/2` | `-z/2` |
| 2 | `x^2+(5/6)xy` | `(5/6)xy+xz+(11/6)yz` | `(5/6)xy+xz+yz` | `-(5/6)yz` |
| 3 | `x^3` | `xyz` | `xyz` | `0` |

Thus the complete correction vector is

```text
Delta_q := t_q(X_R)-pi^*t_q(X_L)
         = (0, -z/2, -(5/6)yz, 0),   q=0,1,2,3.        (5)
```

The codimension-one sign also follows from the usual blowup identity
`c_1(X_R)=pi^*c_1(X_L)-D_c`.  Equation (5) is stronger: it gives the exact
codimension-two defect required by GHTE.

## 4. Exact balanced separation of the negative corrections

### Codimension one

Order the refined rays as

```text
(a,b,c,e,u,v).
```

The strictly positive weight

```text
w_1=(1,1,1,1,1,1)
```

is balanced because the six primitive rays sum to zero.  Therefore

```text
<-z/2,w_1>=-1/2.                                       (6)
```

### Codimension two

In the exact primitive quotient-balance ordering

```text
(ac,ae,au,av,bc,be,bu,bv,cu,cv,eu,ev),
```

the checker reconstructs `B_{R,2}` and verifies

```text
w_2=(2,1,1,1,2,1,1,1,1,1,2,2),
B_{R,2} w_2=0.                                         (7)
```

All entries of `w_2` are positive.  Since `yz=[V(cu)]` in (3),

```text
<-(5/6)[V(cu)],w_2>=-5/6.                              (8)
```

Every nonnegative invariant cycle pairs nonnegatively with `w_1` or `w_2`,
while every balancing relation pairs to zero.  Equations (6) and (8) prove
that neither negative class in (5) has a nonnegative representative modulo
balancing.  The failure is therefore intrinsic to the Chow/balance class,
not an artifact of the displayed monomials.

## 5. Both endpoint fans still satisfy GHTE

The same exact audit gives nonnegative Todd representatives in all degrees:

```text
Sigma_L:
q=0: [X_L],
q=1: (1/2) sum_{rho in Sigma_L(1)} [V(rho)],
q=2: [V(ab)] + (5/6)[V(au)],
q=3: [V(abu)].

Sigma_R:
q=0: [X_R],
q=1: (1/2) sum_{rho in Sigma_R(1)} [V(rho)],
q=2: [V(ac)] + (5/6)[V(au)] + [V(cu)],
q=3: [V(acu)].                                          (9)
```

For `q=2`, the checker independently rebuilds every Euclidean-complement BV
entry and solves the exact balance-row-space equations to (9).  Thus (9) is
not merely a formal Chow reduction; it is an exact GHTE Farkas certificate
on both fans.

## 6. Exact transport decision

Refinement descent remains valid:

```text
GHTE(Sigma_R) => GHTE(Sigma_L).
```

The canonical reverse construction fails.  Equations (5)--(8) rule out an
identity of the form

```text
t_q(X_R) = pi^*t_q(X_L) + E_q
```

with `E_q` nonnegative modulo balancing, already at `q=1` and again at
`q=2`.  Hence coarse GHTE certificates cannot be lifted across this actual
hive star subdivision by canonical pullback plus a nonnegative correction.

This does **not** refute the Boolean implication
`GHTE(Sigma_L) => GHTE(Sigma_R)`: in this example the implication is true
because both sides satisfy GHTE independently by (9).  It also does not rule
out a different hive-specific positive map.  It kills precisely the
canonical pullback-effectivity transport proposed for the wall route.

## 7. Replay

Run

```text
python problems_external/ktt_lr_negativity/ghte_actual_star_subdivision_todd_audit.py
```

The expected output begins

```text
PASS
payload_sha256=97a25d46affb25d58c1a9cc9a575930a89bc16623da874e7c9150f0469c0e554
```

The payload includes both complete fans, both Chow/Todd expansions, the exact
pullback, the two quotient-balance matrices and Farkas representatives, and
the balanced separators (6)--(8).
