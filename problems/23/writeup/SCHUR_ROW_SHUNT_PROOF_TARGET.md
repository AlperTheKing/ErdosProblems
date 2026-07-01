# Schur Row-Shunt Proof Target

Status: live spectral-bypass target for delta=0.

This note isolates the exact point where the Schur effective-shunt route needs
graph theory.  The surrounding linear algebra is generic and should be proved
once; the row-shunt structure is the only load-bearing combinatorial content.

## Setup

For a connected-`B`, `Gamma`-minimal maximum cut, let

```text
H = diag(N - T) + Lstar,
O = {v : T(v) > N},
U = V \ O.
```

Here `Lstar` is the rational Hardy Laplacian already used in
`_hardy_gate.py`.  Assume the principal block `H_UU` is nonsingular
Stieltjes, and form

```text
S = H_OO - H_OU H_UU^{-1} H_UO.
```

The goal is `H >= 0`; by Schur complement this is equivalent to `S >= 0`.

## Generic Algebra

The following facts are purely matrix-theoretic.

### A. Z-matrix inheritance

If `H_UU` is nonsingular Stieltjes and `H_OU <= 0` entrywise off the terminal
block, then `H_UU^{-1} >= 0`, so `S` is a symmetric Z-matrix.

Write

```text
c_ij = -S_ij >= 0      (i != j),
rho_i = sum_j S_ij.
```

Then

```text
S = L_c + diag(rho).
```

### B. Nonnegative row shunts imply PSD

If all `rho_i >= 0`, then `S` is a weakly diagonally dominant symmetric
M-matrix, hence `S >= 0`.

### C. One-negative star rescue

If exactly one row shunt is negative, say `rho_a < 0`, and all other row
shunts are nonnegative, then `S >= 0` follows from the one-terminal condition

```text
rho_a + sum_{p != a} c_ap * rho_p / (c_ap + rho_p) >= 0,        (STAR)
```

with zero-denominator terms omitted.

Proof: discard all conductances inside `O \ {a}`.  The discarded conductances
are a PSD Laplacian.  The remaining star-plus-killing matrix has leaves with
diagonal `c_ap + rho_p`, and Schur-eliminating the leaves gives exactly
`(STAR)`.

### D. The row-shunt uniqueness is not generic

The condition `|{i : rho_i < 0}| <= 1` cannot follow from `S` being a PSD
symmetric Z-matrix alone.  For example,

```text
[[ 2, -3,  0],
 [ -3, 10, -3],
 [  0, -3,  2]]
```

has leading principal minors `(2, 11, 4)`, so it is positive definite, but its
row sums are `(-1, 4, -1)`.  Therefore the missing proof must use the fact that
`S` is the overloaded Schur complement of the Hardy matrix of a shortest-row
triangle-free max-cut configuration.

### E. Row sums as Schur normal currents

Let `h` be the harmonic extension of the boundary value `1` on `O`:

```text
h_O = 1,
H_UU h_U = - H_UO 1_O.
```

Then

```text
rho = S 1_O = (H h)_O,
(H h)_U = 0.
```

Since `H = diag(N-T)+Lstar`, this gives the pointwise identity

```text
rho_o = (N - T(o)) + (Lstar h)_o.
```

Equivalently, with overload `a_o := T(o)-N > 0`,

```text
rho_o < 0
  <=>  the Hardy current leaving o under the harmonic boundary h
       is smaller than a_o.
```

This is the proof-facing form of the row-shunt problem.  The current exact
gates suggest that such a current deficit can occur only at a strict-majority
overload apex.

It is useful to name the absorbed current

```text
b_o := a_o + rho_o.
```

Then `b_o` is exactly the current delivered to overloaded terminal `o` by the
underloaded block under the harmonic boundary value `h_O=1`.  The observed
structure is stronger than the singleton statement: every overload subset with
at most half the total overload is fully covered by this current.

## Graph-Specific Lemma To Prove

The current exact gates support the following statement.

### Schur Row-Shunt Lemma

For every connected-`B`, `Gamma`-minimal maximum cut in a triangle-free graph,
with `H,S,c,rho` as above:

```text
1. H_UU is nonsingular Stieltjes after deleting decoupled zero-load components.
2. S_ij <= 0 for all i != j.
3. |{i in O : rho_i < 0}| <= 1.
4. If rho_a < 0, then (STAR) holds.
```

Items 1 and 2 have standard M-matrix explanations.  Items 3 and 4 are the
actual open graph-theoretic content.

The currently sharp way to prove item 3 is the following stronger inclusion.

### Strict-Majority Shunt Lemma

For `o in O`, put

```text
a_o := T(o)-N,
A := sum_{p in O} a_p.
```

The sharper target is the following subset inequality.

### Schur Absorption-Hall Lemma

For every `X subset O`,

```text
sum_{o in X} a_o <= sum_{o in O\X} a_o
  ==>
sum_{o in X} b_o >= sum_{o in X} a_o.
```

Equivalently,

```text
a(X) <= A-a(X)  ==>  rho(X) >= 0.
```

The singleton case gives the strict-majority implication

```text
rho_o < 0  ==>  a_o > A - a_o.
```

The right-hand side says that `o` carries a strict majority of the total
overload on `O`.  Since at most one vertex can carry a strict majority, this
implies

```text
|{o in O : rho_o < 0}| <= 1.
```

This is stronger than merely saying the negative row is a maximum-load vertex.
It also avoids the false raw-diagonal shortcut: on `MycGrotzsch_N23`,
`rho_22<0` and vertex `22` is the strict-majority overload apex, but no
overloaded vertex has negative raw diagonal `H[o,o]`.

## Exact Gates

Local gates:

```text
python problems/23/writeup/_codex_schur_ec_gate.py
python problems/23/writeup/_Rsize_gate.py
```

Current results:

```text
R_hist = {0: 772, 1: 1}
Mmat_fail = 0
S_notpsd = 0
one-terminal failures = 0
```

The sole negative-shunt case in the current local gate is `MycGrotzsch_N23`,
where the singleton negative row is rescued by a positive exact star margin.

Strict-majority probes:

```text
python problems/23/writeup/_apex_uniqueness_probe3.py
python problems/23/writeup/_apex_uniqueness_probe4.py
```

returned:

```text
probe3: O=672, R_hist={0:671,1:1}, R_not_subset_MAJ=0, MAJge2=0
probe4: O=575, R_hist={0:575}, R_not_subset_MAJ=0, MAJ_only=328
```

Here `MAJ={o in O : a_o > sum_{p!=o} a_p}`.  Thus the exact probes support

```text
{rho_o<0} subset MAJ.
```

The inclusion is not an equivalence: many cuts have `MAJ` nonempty but all
Schur row sums nonnegative.

The subset form was tested by:

```text
python problems/23/writeup/_schur_absorption_hall_gate.py
```

which returned:

```text
Ocuts = 713
O_hist = {1:286, 2:280, 3:40, 4:14, 5:1, 6:30, 8:62}
R_hist = {0:712, 1:1}
subset Hall checks = 12053
hall_fail = 0
R_not_MAJ = 0
```

This suggests that the proof of `|R|<=1` should target the absorption-Hall
subset inequality rather than only the singleton majority corollary.

Claude independently reran the same subset target on the current full
acceptance battery:

```text
O-nonempty gamma-min cuts = 708
subset checks = 12043
O_hist = {1:286, 2:275, 3:40, 4:14, 5:1, 6:30, 8:62}
R_hist = {0:707, 1:1}
absorption-Hall failures = 0
R-subset-MAJ failures = 0
```

Thus the live Schur proof target is the absorption-Hall implication:

```text
a(X) <= a(O\X)  ==>  rho(X) >= 0.
```

A tempting stronger affine shortcut is false.  The candidate

```text
rho(X) >= A - 2 a(X)
```

already has a negative exact margin on the `MycGrotzsch_N23` Schur guardrail.
So the proof cannot be a one-line affine dominance by overload imbalance; it
has to use the harmonic current / capacitary structure of the Schur extension.

Valid inherited max-cut odd-cycle blowup stress with minimum-product bad edge
has

```text
cuts = 14092
O-nonempty = 3845
Rhist = {0: 3845}
```

so blowups exhibit only the diagonally dominant case.

### Scope check: hard H3 maxcut side

The Schur row-shunt statement is not valid for arbitrary connected-`B`
maximum cuts.  On the hard `h_blowup(3)` all-max side
`111111111111111100000000000`, the exact Schur gate gives

```text
Rmax = 6
Rhist = {6: 1}
S_notpsd = 1
```

That side has `cut=90`, `badcount=18`, `Gamma=666`, and shortest-length
multiset `5^9, 7^9`, matching the helper inherited max-cut side on these
metrics.

The exact quotient enumeration

```text
python problems/23/writeup/_hblowup3_gamma_min.py
```

uses the `4^9` clone-count patterns of the 3-fold blowup and gives

```text
Gamma histogram on connected-B max patterns = {450:68, 522:4, 594:4, 666:14}
Gamma min = 450
hard Gamma = inherited Gamma = 666
Schur on 68 Gamma-min representatives: R_hist={0:68}, S_notpsd=0
```

So the hard Schur-failing side is not `Gamma`-minimal.  The Schur row-shunt
target survives this guardrail, but `Gamma`-minimality is load-bearing and
must remain explicit.

## Proof Guidance

A successful proof should explain why the normal derivative vector

```text
rho = S * 1_O
```

has at most one negative coordinate after the Hardy underload block is
Schur-eliminated.  Since scalar subset Hall is known insufficient, the proof
must be genuinely capacitary or mode-wise.  The natural physical statement is:

```text
multiple negative overloaded terminal shunts cannot be separated by the
positive-shunt network generated by shortest-row Hardy conductances; and a
single negative terminal is effectively connected to enough positive shunt to
pay its deficit.
```

Any proposed strengthening should be stated in terms of exact objects
`M, ell, T, cyc, H, O, U, S, c, rho` and sent to Claude for Fraction testing
before being used as proof input.
