# C84: global flow-to-dual coarea and the first ambient-greedy obstruction

## Verdict

There is an exact global way to convert any full C65 arithmetic flow into a
C79 dual.  The construction recursively grounds every generated-factor load,
so old closure multipliers are revised whenever the cutoff grows.  In
particular, it is compatible with C82: the multiplier on

\[
u_5\le u_2+u_3
\]

is not fixed or locally bounded.

This does **not** prove that the required flow exists at every cutoff.  The
strongest deterministic ambient-online recursion tested here is false.  If
one adds one canonical shortest forward path at each new hard-hole cutoff and
never reroutes an old path, the first failure is exactly

\[
X=1710,qquad 80<81.
\]

There is no remaining source-to-ground path after its first 80 choices.  This
is a failure of the canonical recursion, not of the global path-packing
frontier: an exact CP-SAT certificate supplies 81 deadline-respecting paths at
the same cutoff.  Those paths produce an exact C79 dual with

\[
\alpha_{5,2,3}=269.
\]

Thus C84 proves the flow-to-dual lemma and falsifies the canonical monotone
greedy rule.  It leaves the existential forward ordered-bank lemma open.

## 1. Exact C79 dual equations

Let `V_X` be the allowed values and let `K_X` be all hard-shaped values, both
generated and missing.  Eliminate the fixed coordinates

\[
u_2=u_3=0,
\qquad
u_e=1\quad(e\text{ structural splitless}).
\]

For each admissible distinct-factor row `n+1=ab`, write

\[
C_{n;a,b}=u_a+u_b-u_n\ge0.
\]

For each seed edge `p -> c=2p-1`, write

\[
B_c=q_c+u_c-u_p\ge0.
\]

The remaining bound slacks are `u_n`, `1-u_n`, and `q_c`.  A zero-objective
C79 dual is therefore exactly a nonnegative identity

\[
\sum_c q_c-\sum_{h\in K_X}u_h
=
\sum_{n;a,b}\alpha_{n;a,b}C_{n;a,b}
+\sum_c\beta_c B_c
+\sum_n \lambda_n u_n
+\sum_n\nu_n(1-u_n)
+\sum_c\delta_c q_c,                                      \tag{1}
\]

after the fixed coordinates are substituted.  All multipliers are
nonnegative.  Before substitution, its stationarity equations are

\[
1=\beta_c+\delta_c,                                       \tag{2}
\]

and

\[
-1_{n\in K_X}
=A_n(\alpha)+B_n(\beta)+\lambda_n-\nu_n,                  \tag{3}
\]

where

\[
A_n(\alpha)
=\sum_{r:n\in\{a,b\}}\alpha_{r;a,b}
-\sum_{a,b}\alpha_{n;a,b},                               \tag{4}
\]

and

\[
B_n(\beta)
=1_{n=2p-1}\beta_n
-1_{2n-1\le X}\beta_{2n-1}.                              \tag{5}
\]

The constant equation is the constant term of (1) after substituting the
fixed seeds and splitless values.  The exact checker verifies (1), hence all
of (2)--(5), coefficient by coefficient over the integers.

## 2. Arithmetic flow network

Let `G_X` be the grounded closure and `M_X=V_X\G_X`.  The directed network
has:

* a unit source arc to every hard hole;
* an unlimited source arc to every structural splitless hole;
* an unlimited unary arc `n -> p` whenever
  `n+1=g p`, with `g in G_X`, `p in M_X`, and `g != p`;
* a unit seed arc `p -> 2p-1`, ending at ground if the child is generated.

All factorizations use strict distinctness.  Let `k` be the number of hard
holes.  A full arithmetic flow means an integral source-to-ground flow of
value `k`.

## 3. Flow-to-dual lemma

### Lemma 3.1

For every cutoff `X`, every integral arithmetic flow of value `k` constructs
an exact zero-objective C79 dual by a finite descending recursion.  In
particular,

\[
\sum_{h\in K_X}u_h\le\sum_c q_c                         \tag{6}
\]

for every feasible C79 potential.

### Proof

Give source and ground potentials `1` and `0`, respectively, and give a hole
node `n` potential `u_n`.  Decompose the integral flow into paths.

A path starting at a hard hole `h` contributes the source drop `1-u_h`.  A
path starting at a splitless hole `e` contributes `1-u_e=0`.  On a unary arc

\[
n\longrightarrow p,qquad n+1=gp,qquad g\in G_X,
\]

the closure row gives

\[
u_n-u_p\le u_g.                                         \tag{7}
\]

On a seed arc `p -> c`, the boundary row gives

\[
u_p-u_c\le q_c.                                         \tag{8}
\]

Every seed edge carries at most one unit, so its flow is a valid multiplier
`0<=beta_c<=1`.  Every hard source edge carries at most one unit.

It remains to remove the generated loads in (7), the generated terminal
loads, and the objective terms belonging to generated hard shapes.  For each
generated `g>3`, choose one grounded witness

\[
g+1=a_gb_g,qquad a_g,b_g\in G_X,qquad a_g<b_g.
\]

Let `L_g` be the initial load at `g`: unary-flow uses with witness `g`, plus
terminal seed-flow uses at `g`, plus `1` when `g` is hard-shaped.  Process
generated values in decreasing order and define

\[
w_g=L_g+\sum_{r>g:\,g\in\{a_r,b_r\}}w_r.                \tag{9}
\]

Add `w_g` copies of `C_{g;a_g,b_g}`.  Since both factors are strictly smaller
than `g`, (9) terminates at the fixed seeds.  Algebraically,

\[
\sum_g L_g u_g+
\sum_{g>3}w_g(u_{a_g}+u_{b_g}-u_g)=0.                   \tag{10}
\]

This is the global grounding recursion.  Its coefficient on an old row can
increase at every later cutoff.

Now telescope all flow paths and apply (7)--(10).  If `a_h` is the used flow
on the hard source arc and `b_c` is the used flow on the seed edge ending at
`c`, the resulting exact identity is

\[
\begin{aligned}
\sum_cq_c-\sum_{h\in K_X}u_h
={}&\sum_{n;a,b}\alpha_{n;a,b}C_{n;a,b}
+\sum_c b_c B_c\\
&+\sum_{h\in K_X\cap M_X}(1-a_h)(1-u_h)
+\sum_c(1-b_c)q_c.                                     \tag{11}
\end{aligned}
\]

Every term on the right is nonnegative.  Equation (11) is (1) with explicit
dual multipliers and proves (6).  QED.

The base-load growth in C82 is now transparent: every grounding request whose
chosen derivation passes through `5 <- (2,3)` adds to `alpha_5`.

## 4. Exact cutoff-1710 certificate

At `X=1710` the model has:

```text
hard shapes                  123
hard holes                    81
generated hard shapes         42
deadline-respecting paths     81
hard-source paths             20
splitless-source paths         61
unary-flow units               14
used unit seed edges          149
path grounding requests        95
objective grounding requests   42
alpha_5                       269
nonzero alpha rows            192
nonzero beta rows             149
```

The saved path list is independently replayed without calling OR-Tools.  The
dual constructor then checks every `u` and `q` coefficient in (11) over
Python integers.  Normal and `python -O` dual outputs are byte-identical.

This finite certificate is stronger than merely solving the C79 LP at 1710:
it exhibits the global arithmetic path packing and its exact grounding
recursion.

## 5. Exact obstruction to canonical ambient recursion

Consider the following deterministic recurrence.

1. Increase the ambient cutoff through the hard holes.
2. At each new hard hole, add one shortest source-to-ground path available at
   that cutoff.
3. Order source nodes increasingly, with splitless sources before hard
   sources; explore unary arcs increasingly before the seed arc.
4. Never reuse a unit seed edge or hard source edge, and never retract an old
   path.

This rule is global: unary steps may move between seed chains, and converting
each path by Lemma 3.1 recursively increases old grounding coefficients.  It
is therefore not excluded by C82's growing-base obstruction.

The exact replay checks every arrival through `X=10000`.  Its first failure is

```text
cutoff                    1710
hard demand                 81
completed paths             80
used seed edges            147
available next path       none
```

The last completed arrival is `1704`.  Exact reachability in the residual
forward graph at `1710` finds no source-to-ground path.  Hence this canonical
ambient-online recursion is false.

The obstruction is choice-sensitive.  A separate exact deadline-packing
model finds 81 paths through `1710`, using 149 seed edges.  Therefore C84 does
not falsify the existential no-cancellation frontier and does not prove or
disprove C56/C79 for arbitrary cutoffs.

## 6. Reproduction

```powershell
python problems/424/compute/wave5/C84_global_dual_coarea.py `
  --generate 10000 `
  --output problems/424/compute/wave5/C84_online_10000.json

python -O problems/424/compute/wave5/C84_global_dual_coarea.py `
  --verify problems/424/compute/wave5/C84_online_10000.json

python problems/424/compute/wave5/C84_deadline_pack.py `
  --solve 1710 --workers 64 --seconds 300 `
  --output problems/424/compute/wave5/C84_deadline_pack_1710.json

python -O problems/424/compute/wave5/C84_deadline_pack.py `
  --verify problems/424/compute/wave5/C84_deadline_pack_1710.json

python problems/424/compute/wave5/C84_flow_to_dual.py `
  --packing problems/424/compute/wave5/C84_deadline_pack_1710.json `
  --output problems/424/compute/wave5/C84_dual_1710.json

python -O problems/424/compute/wave5/C84_flow_to_dual.py `
  --packing problems/424/compute/wave5/C84_deadline_pack_1710.json `
  --output problems/424/compute/wave5/C84_dual_1710_replay.json
```

```text
E5DE6A65AF12E36E3266D9198AFB3A3886812D7B3C4579825B4CC37BC8636415  C84_global_dual_coarea.py
DF7F6D2FFCF916A7287DAEA5127FA17996665E5F785A4C5B8FFC8D50C253055D  C84_deadline_pack.py
70CD890AF0183CB28CA9A47BE98D76F389FCB863F9FA7C8E9F4ADE1632CBFFE8  C84_flow_to_dual.py
70322882C5354F44BAC6C8598B84F19AE4D3C96D4A459D2C7B9D047740EFE588  C84_online_10000.json
499654AD73FA8C0EFCECFA55761A39D4F7C0EF22909BDB553422A3D676BBB01F  C84_deadline_pack_1710.json
67EE097EF65968E92576892DDC8E70DA8F7B0DC5522E6DEA3B17502CEC36FF39  C84_dual_1710.json
67EE097EF65968E92576892DDC8E70DA8F7B0DC5522E6DEA3B17502CEC36FF39  C84_dual_1710_replay.json
```

No `native_decide` is used.

