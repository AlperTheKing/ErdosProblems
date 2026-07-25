# Todd-cycle wall law for a unit crepant `2<->2` flip

Date: 2026-07-22

Status: **exact obstruction to canonical nonnegative GHTE transport.**  The
obstruction occurs in a complete smooth three-dimensional normal fan, at
`q=2`.  It does not provide a negative balanced witness for either fan, and
therefore it does not prove that GHTE itself is false or that its truth value
differs across this flip.

## 1. What is universal and what is not

Let `Sigma_L` and `Sigma_R` be complete rational fans which differ by a
`2<->2` flip on the primitive circuit

```text
a+d=b+c,                                                   (1)
```

with the same link, and let `Sigma_0` be the common wall fan.  Write `S_L`
and `S_R` for invariant-cycle pushforward to `Sigma_0`.  BV additivity under
subdivision gives, for every `q`,

```text
S_L t_q(Sigma_L) = t_q(Sigma_0) = S_R t_q(Sigma_R).        (2)
```

Equation (2) is the exact Todd-cycle transformation which is valid without
smoothness or a lattice-saturation shortcut.  Both pushforwards preserve
nonnegative cycles and balancing relations.  Thus GHTE on either side
descends to the wall fan.

The internal diagonal cones are sent to zero by (2).  Consequently (2) has
no positive inverse in general.  The smallest exact fan below shows more:
the graph correspondence between the two smooth sides sends the old
exceptional curve to the **negative** of the new one.

## 2. The exact complete normal fans

Use the saturated lattice `N=Z^3` and the primitive outer normals

```text
a=(-1,1,0),   b=(0,0,-1),   c=(0,1,0),
d=(1,0,-1),   r=(0,-1,1).                                (3)
```

They satisfy (1), and all maximal cones below have determinant `+/-1`.
The two complete fans are

```text
Sigma_L max = arb, arc, brd, crd, abc, bcd,              (4)
Sigma_R max = arb, arc, brd, crd, abd, acd.              (5)
```

Thus `Sigma_L` has diagonal `bc`, while `Sigma_R` has diagonal `ad`.
The wall fan replaces the last two cones on either side by the non-simplicial
cone `abcd`.  These are the exact fans of the actual side-four hive wall
found by `ghte_find_r4_wall_pair.py`.

For the Euclidean complement and outer-normal convention fixed in the GHTE
contract, the codimension-two BV values are

| common cone | `ab` | `ac` | `ar` | `bd` | `br` | `cd` | `cr` | `dr` |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| `alpha^BV` | `1/4` | `1/8` | `1/3` | `1/8` | `3/8` | `1/4` | `3/8` | `1/3` |

and

```text
alpha^BV(bc)=1/4,       alpha^BV(ad)=1/3.                (6)
```

The audit rebuilds both primitive quotient-lattice balance matrices.  It
solves the two exact row-space equations and obtains

```text
t_2(Sigma_L) = 13/6 [V(ab)] + [V(bc)]  modulo im(B_L^T), (7)
t_2(Sigma_R) = 13/6 [V(ab)] + [V(ad)]  modulo im(B_R^T). (8)
```

Every BV entry in (6)--(8) is positive; in particular both fans satisfy GHTE
at `q=2` already with Farkas shift `y=0`.

## 3. Chow presentations and the exact graph map

Let `A,B,C,D,R` denote the five invariant divisors.  The linear relations
from (3) give

```text
A=D=x,       B=C=y,       R=x+y.                         (9)
```

The Stanley--Reisner ideals of (4)--(5) therefore give

```text
A*(X_L)_Q = Q[x,y]/(x^2, y^2(x+y)),                     (10)
A*(X_R)_Q = Q[x,y]/(y^2, x^2(x+y)).                     (11)
```

The toric Todd product has degree-two term

```text
prod_rho D_rho/(1-exp(-D_rho)) |_2
  = (1/12) sum_rho D_rho^2 + (1/4) sum_(rho<s) D_rho D_s
  = x^2 + (13/6)xy + y^2.                               (12)
```

Equations (10)--(12) are exactly (7)--(8), since the fans are smooth and
`xy=[V(ab)]`, `y^2=[V(bc)]` on the left, and `x^2=[V(ad)]` on the right.

Put

```text
e=a+d=b+c=(0,1,-1)=-r.                                  (13)
```

Star subdivision along `e` gives the common resolution

```text
p_L : X_W -> X_L,       p_R : X_W -> X_R.
```

If `z` is the exceptional divisor class, its Chow presentation and the two
pullbacks are

```text
A*(X_W)_Q = Q[x,y,z]/(x^2,y^2,z(x+y+z)),                (14)
p_L^*x=x,     p_L^*y=y+z,
p_R^*x=x+z,   p_R^*y=y.                                 (15)
```

In particular, `z^2=-xz-yz`.  Pushing invariant curves through `p_R` gives

```text
p_R*(xy)=xy,   p_R*(xz)=x^2,   p_R*(yz)=0,
p_R*(z^2)=-x^2.                                         (16)
```

A direct Todd expansion in (14) also gives

```text
t_2(X_W) = 13/6 xy + xz + yz,
p_L^*t_2(X_L) = 13/6 xy + 7/6 xz + yz,
p_R^*t_2(X_R) = 13/6 xy + xz + 7/6 yz.                 (16a)
```

Consequently

```text
t_2(X_W)-p_L^*t_2(X_L) = -1/6 xz,
t_2(X_W)-p_R^*t_2(X_R) = -1/6 yz.                      (16b)
```

Thus even the common smooth refinement is GHTE-effective while its canonical
upward pullback formula requires a negative exceptional correction.

For the graph correspondence `G_LR=p_R* p_L^*`, use the ordered class bases

```text
(xy,y^2)_L,                (xy,x^2)_R.                  (17)
```

Equations (14)--(16) give the exact matrix

```text
                 [ 1   0 ]
G_LR          =  [ 1  -1 ].                             (18)
```

Hence

```text
G_LR [V(bc)] = -[V(ad)],                                (19)
G_LR t_2(X_L) = t_2(X_R) + (1/6)[V(ad)].                (20)
```

The reverse graph has the same matrix after exchanging `x` and `y`:

```text
G_RL [V(ad)] = -[V(bc)],                                (21)
G_RL t_2(X_R) = t_2(X_L) + (1/6)[V(bc)].                (22)
```

Thus the exceptional Todd class is neither killed nor carried to an
effective exceptional class: its fundamental curve changes sign, while the
full Todd class acquires the exact `1/6` correction.

For completeness, the entire trivial-link transformation is

| `q` | graph transformation modulo balancing |
|---:|---|
| `0` | `G_LR t_0(X_L)=t_0(X_R)` |
| `1` | `G_LR t_1(X_L)=t_1(X_R)` |
| `2` | `G_LR t_2(X_L)=t_2(X_R)+(1/6)[V(ad)]` |
| `3` | `G_LR t_3(X_L)=t_3(X_R)` |

Here `t_0` is the fundamental class, `t_1=(1/2) sum D_rho`, and the top
Todd zero-cycle has degree `chi(O_X)=1`; the graph preserves each of these
three classes.  Thus `q=2` is the only nonzero correction in dimension three.

The `1/6` sign is independently consistent with the actual hive chamber
calculation in `ACTUAL_HIVE_WALL_EHRHART_OBSTRUCTION.md`.  The new exceptional
edge has normalized length `r=-Omega`; pairing (20) with that volume changes
the linear Ehrhart coefficient by `-r/6`, exactly the `q=2` term of
`binomial(r*n+1,3)`.

## 4. Exact separation from the effective cone

The failure in (19) is not an artifact of the chosen cycle representative.
In the column orders printed by the checker, the exact strictly positive
balanced weights are

```text
w_L=(1,1,1,1,1,2,1,2,1),      B_L w_L=0,               (23)
w_R=(1,1,1,2,1,1,1,1,2),      B_R w_R=0.               (24)
```

Their exceptional entries are one.  Therefore

```text
<- [V(bc)], w_L> = -1,      <- [V(ad)], w_R> = -1.      (25)
```

Every nonnegative cycle has nonnegative pairing with these weights, and a
balancing relation has pairing zero.  Equation (25) proves that the negative
classes in (19) and (21) have no nonnegative representatives modulo
balancing.  Consequently no positive chain map can induce the graph
correspondence in codimension two.

## 5. Common-link extension

For a saturated unimodular transverse circuit with a split common link fan
`Lambda`, the preceding calculation tensors with the link Chow group.  If

```text
t_(q-2)(Lambda) = sum_(eta in Lambda(q-2)) beta_eta [V(eta)]
```

is any PT representative modulo link balancing, then

```text
G_LR t_q(Sigma_L)
 = t_q(Sigma_R)
   + (1/6) sum_eta beta_eta [V(ad+eta)]                 (26)
```

modulo balancing, and the reverse formula uses `bc+eta`.  On each
exceptional summand the graph action is

```text
[V(bc+eta)] -> -[V(ad+eta)].                            (27)
```

Formula (26) follows from Todd multiplicativity after a rational splitting
of the circuit span and link quotient.  It gives no `q=3` correction when the
link is a point; in the three-dimensional atom only `q=2` changes.  For a
non-saturated circuit lattice, unit coefficients alone do not identify the
quotient multiplicities, so the universal statement remains (2), not an
unqualified `1/6` formula.

## 6. GHTE decision and exact scope

The unit crepant relation (1) does **not** supply the missing upward GHTE
transport:

1. the only unconditional positive maps are the two descents (2);
2. the graph map sends an effective extremal curve to a class separated from
   the effective cone by (25); and
3. solving (20) for the target Todd class requires subtracting the
   exceptional `1/6` correction.

This is a smallest exact obstruction: dimension three, trivial link, and
`q=2`.  It kills canonical graph-based nonnegative certificate transport,
even in the primitive unimodular case.  It does **not** establish a Boolean
counterexample to flip-invariance of GHTE, because (6) makes GHTE true on
both sides.  Proving that Boolean statement would require a different
hive-specific positive map; refuting it would require an actual
`w>=0`, `Bw=0`, `<a,w><0` on exactly one side.

Replay the independent symbolic audit with

```text
python problems_external/ktt_lr_negativity/ghte_unit_crepant_flip_todd_audit.py
```

Expected digest:

```text
PASS
payload_sha256=3a0aaa1db8df6d4a9aa376ebf2c742351f19c12339eb01184dcaa6c3ff5afae0
```
