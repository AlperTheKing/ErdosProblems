# Schur Effective-Shunt Status

This note records the status of the proposed Schur effective-shunt domination
certificate.

Let

```text
H = diag(N - T) + Lstar,
O = {v : T(v) > N},
U = V \ O,
S = H_OO - H_OU H_UU^{-1} H_UO.
```

Since `S` is a symmetric Z-matrix in all exact gates, write

```text
S = L_c + diag(r),
r_o = sum_{o'} S[o,o'].
```

For `R={o:r_o<0}`, let `A=L_c+diag(r^+)`. The EC certificate is

```text
Lambda_R := A_RR - A_RP A_PP^{-1} A_PR >= diag(r^-).
```

## Exact Gate

Fresh run:

```text
python problems/23/writeup/_codex_schur_ec_gate.py
```

Result:

```text
O-cuts = 713
noO = 17968
O_hist = {1:286, 2:280, 3:40, 4:14, 5:1, 6:30, 8:62}
R_hist = {0:712, 1:1}
ec_fail = 0
```

The sole negative-row-shunt case is `MycGrotzsch_N23`, side
`10101101011001000000001`, with `O=[1,2,3,10,22]` and the unique negative
row at vertex `22`.

## Codex Rerun 2026-07-01

Baseline EC gate:

```text
python problems/23/writeup/_codex_schur_ec_gate.py
```

returned:

```text
O-cuts = 713
R_hist = {0:712, 1:1}
q_fail = z_fail = app_fail = ec_fail = 0
```

The same unique negative-row-shunt case is `MycGrotzsch_N23`.

Sharper row-shunt-size gate:

```text
python problems/23/writeup/_Rsize_gate.py
```

returned:

```text
O-nonempty cuts tested = 773
Rmax = 1
|R| histogram = {0:772, 1:1}
|R|>=2 cases = 0
M-matrix/offdiag failures = 0
S not PSD = 0
one-terminal scalar < 0 failures = 0
```

So the currently live sharpened target is:

```text
S is a symmetric M-matrix,
|{i : row_sum_i(S)<0}| <= 1,
and the singleton negative-row case satisfies the one-terminal Schur scalar.
```

Tempting fixed-gauge shortcut:

```text
python problems/23/writeup/_hardy_supersol_gate.py
```

fails.  The coordinatewise supersolution `phi=T+1` has two negative
coordinates on the `MycGrotzsch_N23` guardrail, so the proof must use the
nonconstant Schur ground-state / effective-conductance gauge.

## Interpretation

The EC certificate is a useful final Schur-side certificate, but after the
positive/negative row-shunt split it is algebraically equivalent to `S >= 0`
when the positive-shunt block is nonsingular. It is therefore not yet the
missing combinatorial proof.

The proof-facing target is the mode-wise capacity inequality

```text
Cap(y) := min_{x_U, x_O=y} x^T H x
       >= sum_{o in O} (T(o)-N) y_o^2
```

for every nonnegative overload potential `y`.

## N23 Diagnostic

On the `MycGrotzsch_N23` witness, the Schur ground state `S^{-1}1`,
normalized to value `1` at the apex `22`, is approximately

```text
[0.239468, 0.305466, 0.239468, 0.235275, 1].
```

Simple gauges such as `1/T`, `1/(T-N)`, and `deg/T` do not match this shape.

The worst generalized mixed-mode margin for `S` against the overload diagonal
is approximately

```text
0.007674
```

in ratio form. Equivalently the worst normalized mode has

```text
y^T S y ~= 0.149573,
sum_o (T(o)-N)y_o^2 ~= 19.490262.
```

The best subset/indicator capacity margin on the same witness is much larger,
about `1.191131` at `{22}`. Thus scalar subset Hall has too much slack to see
the true bottleneck; the remaining proof must be genuinely matrix-capacitary.

## Valid Blowup Stress, 2026-07-01

A first inherited-cut blowup stress with a fixed bad `C5` edge produced many
`|R|>=2` artifacts.  That run is invalid for nonuniform blowups because the
fixed edge need not be a minimum adjacent product, hence the inherited side is
not necessarily a maximum cut.

The corrected stress chooses, for each odd-cycle blowup, the bad adjacent edge
with minimum product and uses the corresponding inherited maximum-cut side.
For all `C5` size vectors with entries in `1..7` and total at most `24`, plus a
small `C7` sample, the exact `_Rsize_gate.test_cut` result was:

```text
cuts = 14092
O-nonempty Schur cuts = 3845
Rmax = 0
Rhist = {0: 3845}
R>=2 = 0
Mmat_fail = 0
S_notpsd = 0
oneterm_fail = 0
```

Thus the valid odd-cycle blowup slice has no negative Schur row shunts at all.
The earlier `R>=2` observations were side-choice artifacts, not candidate
counterexamples to the sharpened Schur target.

## Apex-Uniqueness Gate, 2026-07-01

Exact rerun:

```text
python problems/23/writeup/_apex_uniqueness_gate.py
```

returned:

```text
O-nonempty gamma-min cuts tested = 586
cuts with |O|>=2 = 315
S>=0 fail / UU-not-PD = 0
R_hist = {0:585, 1:1}
|R|>=2 cases = 0
R={o*} but o* != argmax T = 0
R={o*} but o* != unique negative raw diagonal = 1
```

Thus the exact battery supports the sharper graph-specific target

```text
row_sum_o(S) < 0  ==>  o is the unique global max-load apex.
```

The tempting stronger shortcut

```text
row_sum_o(S) < 0  ==>  H[o,o] < 0 uniquely on O
```

is false on the same `MycGrotzsch_N23` guardrail: the singleton negative row is
vertex `22`, but `negdiagO=[]`.

## Strict-Majority Probe, 2026-07-01

The stronger proof target is:

```text
row_sum_o(S) < 0
  ==>  T(o)-N > sum_{p in O, p!=o} (T(p)-N).
```

This implies `|R|<=1` because at most one overloaded vertex can carry a strict
majority of the total overload on `O`.

Exact reruns:

```text
python problems/23/writeup/_apex_uniqueness_probe3.py
python problems/23/writeup/_apex_uniqueness_probe4.py
```

returned:

```text
probe3: O=672, R_hist={0:671,1:1}, R_not_subset_MAJ=0, MAJge2=0
probe4: O=575, R_hist={0:575}, R_not_subset_MAJ=0, MAJ_only=328
```

Here `MAJ={o in O : T(o)-N > sum_{p!=o}(T(p)-N)}`.  The inclusion

```text
R subset MAJ
```

holds in both probes.  The converse is false: `MAJ_only=328` in probe4, so
strict majority is necessary but not sufficient for a negative Schur row.

## Schur Absorption-Hall Gate, 2026-07-01

Let

```text
a_o = T(o)-N,
rho_o = row_sum_o(S),
b_o = a_o + rho_o.
```

By the harmonic-current identity, `b_o` is the current absorbed at overloaded
terminal `o` from the underloaded block when all vertices of `O` are held at
potential `1`.  The subset strengthening tested is:

```text
for every X subset O:
  a(X) <= a(O\X)  ==>  b(X) >= a(X).
```

The singleton case gives `R subset MAJ`.

Exact run:

```text
python problems/23/writeup/_schur_absorption_hall_gate.py
```

returned:

```text
Ocuts = 713
O_hist = {1:286, 2:280, 3:40, 4:14, 5:1, 6:30, 8:62}
R_hist = {0:712, 1:1}
subset Hall checks = 12053
singular = 0
R_not_MAJ = 0
hall_fail = 0
```

This is now the sharpest proof-facing form for `|R|<=1`: prove the current
absorption-Hall inequality for the Schur harmonic extension.

## Compact N23 Schur Table

For the sole current non-diagonal-dominant guardrail,
`MycGrotzsch_N23` with side
`10101101011001000000001`, the overloaded set is

```text
O = [1, 2, 3, 10, 22].
```

The Schur row sums are approximately

```text
rho = [4.482905065, 1.095890278, 4.482905065, 4.684400554, -3.201078048].
```

The Schur matrix `S` on `O` is approximately

```text
[
  [10.046823, -2.951145, -0.733930, -0.819565, -1.059277],
  [-2.951145,  8.993171, -2.951145, -0.964867, -1.030124],
  [-0.733930, -2.951145, 10.046823, -0.819565, -1.059277],
  [-0.819565, -0.964867, -0.819565,  8.531929, -1.243531],
  [-1.059277, -1.030124, -1.059277, -1.243531,  1.191131],
]
```

The negative row is vertex `22`.  The exact star-rescue terms have positive
signs and approximate values

```text
v=1:  c=1.059276915, rho=4.482905065, term=0.856817381
v=2:  c=1.030124146, rho=1.095890278, term=0.530995004
v=3:  c=1.059276915, rho=4.482905065, term=0.856817381
v=10: c=1.243531373, rho=4.684400554, term=0.982669694
```

so

```text
rho_22 + sum_p c_22,p rho_p / (c_22,p + rho_p)
  ~= 0.0262214118 > 0.
```

The exact Fraction computation checked the signs; the decimals above are only
for readability.

## Scope Check: Hard H3 Maxcut Side

The Schur effective-shunt certificate is not valid on arbitrary connected-`B`
maximum cuts.  On the hard row-side `h_blowup(3)` side

```text
111111111111111100000000000
```

the exact `_Rsize_gate.test_cut` computation gives

```text
O-nonempty = 1
Rmax = 6
Rhist = {6: 1}
Mmat_fail = 0
S_notpsd = 1
```

Thus `H >= 0` fails on this side.  This side is a genuine connected-`B`
maximum cut, but the decisive question is whether it is also `Gamma`-minimal.
Its basic metrics are

```text
cut = 90
badcount = 18
Gamma = 666
ell multiset = 5^9, 7^9
```

The helper inherited `h_blowup(3)` side has the same metrics.  A full
Gamma-minimum check over all maximum cuts is feasible by quotienting the
3-fold blowup into the `4^9` clone-count patterns.  Exact rerun:

```text
python problems/23/writeup/_hblowup3_gamma_min.py
```

returned:

```text
max cut value = 90
max count patterns = 90
connected-B max patterns = 90
Gamma histogram = {450:68, 522:4, 594:4, 666:14}
Gamma min = 450
hard Gamma = 666
inherited Gamma = 666
Schur on Gamma-min representatives: O-nonempty=68, R_hist={0:68}, S_notpsd=0
```

Thus the Schur-failing hard side is not `Gamma`-minimal.  This closes the H3
scope caveat locally and confirms that `Gamma`-minimality is load-bearing for
the Schur-EC bypass.

## Algebraic Star-Rescue Lemma

For a symmetric Z-matrix Schur block

```text
S = L_c + diag(r),
c_ij = -S_ij >= 0,
r_i = sum_j S_ij,
```

the following purely algebraic implication is enough for the currently
observed structure.

Assume:

```text
1. r_i >= 0 for every i, except possibly one vertex a;
2. r_a + sum_{p != a} c_ap r_p / (c_ap + r_p) >= 0,
   with terms of denominator 0 omitted.
```

Then `S >= 0`.

Reason: split

```text
S = A - (-r_a) e_a e_a^T,
A = L_c + diag(r^+).
```

The PSD condition is equivalent to the effective conductance from `a` to the
positive-shunt network `A` dominating `-r_a`.  By Rayleigh monotonicity, this
effective conductance is at least the network obtained by deleting all
positive-positive conductances and keeping only the direct branches

```text
a --(c_ap)-- p --(r_p)-- ground.
```

Each branch has series conductance

```text
c_ap r_p / (c_ap + r_p),
```

and the branches are in parallel.  Thus condition (2) implies the full EC
certificate and hence `S >= 0`.

So the graph-theoretic proof target can be stated without matrix inverses:

```text
For every Schur block produced by the Hardy matrix H,
there is at most one negative row shunt, and if it exists then the direct
star-rescue inequality above holds.
```

This is stronger than the general EC certificate but matches every exact gate
run so far.  It also isolates the only non-diagonal-dominant behavior in the
current battery: the `MycGrotzsch_N23` apex row.
