# Slack-CAGE Canonical Cage / Xi2 Plan

Source: fresh GPT-Pro consult on the Slack-CAGE proof gap, read from the
in-app browser on 2026-07-01.

## Main Correction

The tempting lemma

```text
zero-slack non-balanced cage => DeltaGamma < 0
```

is false as stated.  The smallest obstruction is an odd cycle such as `C7`
with the alternating maximum cut: `B` is a path and the single bad edge closes
the cycle.  A terminal prefix switch has

```text
sigma(S) = 0
B^S connected
DeltaGamma(S) = 7^2 - 7^2 = 0
```

It is not a Slack-CAGE obstruction because it carries no positive residual
row debt.  Therefore the strict statement must include residual positivity:

```text
zero-slack + residual-positive + not banked C5-flat => Gamma drop.
```

Exact sanity check:

```text
C7 with bad edge (0,6), blue path 0-1-2-3-4-5-6.

S={0}:       sigma=0, B^S connected, DeltaGamma=0, new bad edge=(0,1)
S={0,1}:     sigma=0, B^S connected, DeltaGamma=0, new bad edge=(1,2)
S={0,1,2}:   sigma=0, B^S connected, DeltaGamma=0, new bad edge=(2,3)
```

This confirms that zero-slack odd-cycle rotations are harmless only when
their residual surplus is zero.

The right square-length object is not just `DeltaGamma`; it is a witness
matching square surplus `Xi2(S)`.

## Atomic Measure

For a fixed failed pair `(Q,U)`, define the counted row family

```text
R = {(g,P): g in M, P in cyc[g], V(P) subset U, V(P) cap V(Q) nonempty}
alpha_(g,P) = 1 / |cyc[g]|
```

and for `X subset U`,

```text
mu_Q(X) =
  sum_{(g,P) in R} alpha_(g,P) * |V(P) cap V(Q) cap X|.
```

Thus `mu_Q(U)=D_Q(U)`.

Important correction after the CTD structure scan: this fixed atomic measure
is not sufficient for the Flat5 bank accounting.  The bank branch is driven by
rows that disappear when a cage is peeled out of `U`, so the relevant dynamic
quantity is

```text
del_Q(S;U) = D_Q(U) - D_Q(U-S),
drop_Q(S;U) =
  del_Q(S;U) - |S| - (sigma(U)-sigma(U-S)).
```

Equivalently,

```text
drop_Q(S;U) = pre_Q(U) - pre_Q(U-S).
```

The eta-bank charge is the positive-part consumption

```text
bank_Q(S;U) = max(0, pre_Q(U)) - max(0, pre_Q(U-S)).
```

The fixed residual

```text
mu_Q(S) - |S| - sigma(S)
```

can be zero or negative on the same Flat5 cage that consumes all dynamic
positive prebank.  Therefore CTD should not be stated as "find a cage with
positive fixed `mu_Q(S)-|S|-sigma(S)`" in the bank branch.  The correct split is:

```text
Flat5 bank branch:      bank_Q(S;U)>0 via dynamic row deletion.
Non-Flat5 strict branch: zero-slack residual cage with Xi2(S)>0.
```

## Canonical Terminal Closure

The suggested closure `tc(X)` is a deterministic saturation inside `U`.

Start from `X_0=X`.  Repeatedly apply:

```text
Row-terminal saturation:
  If a counted row P has X_t cap V(P) nonterminal, replace it by the
  smallest terminal superset when exactly one endpoint is already in X_t.
  If neither endpoint or both endpoints are in X_t, add all of V(P).

Blue side-door closure:
  If e=xy in B has x in X_t and y in U-X_t, and no counted row has e as
  first exit from X_t, add y.

Boundary abort:
  If the same unwitnessed blue edge has y outside U, this seed is not
  cage-generating.
```

A non-aborted fixed point is row-terminal for all counted rows and every blue
boundary edge is witnessed by a counted-row first exit.

## Residual Surplus

For a canonical fixed point `S`, define

```text
rho_Q(S) = mu_Q(S) - |S| - sigma(S) - beta_5(S),
```

where `beta_5(S)` is the banked length-5 flat-cell contribution.

## Lemma CTD: Canonical Terminal-Cage Decomposition

If

```text
D_Q(U) - |U| - sigma(U) - eta > 0,
```

then after terminal-closure peeling of the positive part of

```text
mu_Q(X) - |X| - sigma(X) - beta_5(X),
```

there is a canonical cage `S subset U` with

```text
rho_Q(S) > 0.
```

Exact gate:

```text
For every minimal failed pair (Q,U), compute all terminal-closed S subset U.
Assert max_S rho_Q(S) > 0 among connected canonical cages.
```

## Bank5 Local

A flat length-5 cell is a five-class object

```text
Z = (Z0,Z1,Z2,Z3,Z4)
Z_i Z_{i+1} subset B for i=0,1,2,3
Z4 Z0 subset M
all shortest rows for bad edges in Z4 Z0 are exactly length-5 paths
through one vertex in each class.
```

Let `n_i=|Z_i|`, `n=sum_i n_i`, and assume `n0*n4` is a minimum adjacent
product.  For a fixed row `Q`, let `a_i=1` if `Q` uses a vertex of `Z_i`,
otherwise `0`.  The cell contribution is

```text
mu_Q(Z) =
  a0*n4 + a4*n0 + n0*n4*(a1/n1 + a2/n2 + a3/n3).
```

Define

```text
beta_Q(Z) = max(0, mu_Q(Z) - n).
```

GPT-Pro's proposed local algebraic target:

```text
beta_Q(Z) <= n^2/25 - n0*n4.                       (BANK5-local)
```

This should be checked carefully.  The given proof sketch reduces the
worst case to `x=b`, `z=a`, `y=max(a,b)` under the adjacent-product
constraints and then to

```text
(a-b)(9a-4b+25) >= 0
```

after assuming `a>=b`.

Follow-up: the complete-cell local formulation is not merely de-risked; it is
stronger than needed.  In a complete weighted `C5` flat cell, the positive
part is always zero.

Write

```text
a=n0, p=n1, q=n2, r=n3, b=n4, m=ab.
```

The adjacent-product constraints are

```text
p>=b,      r>=a,      pq>=ab,      qr>=ab.
```

The complete-cell row charge is

```text
mu = a+b + ab/p + ab/q + ab/r,
n  = a+p+q+r+b.
```

So `mu<=n` is equivalent to

```text
ab/p + ab/q + ab/r <= p+q+r.                       (*)
```

For fixed `a,b,p,r`, the right-minus-left side of `(*)` is increasing in
`q`, because its derivative is

```text
1 + ab/q^2 > 0.
```

Thus it is enough to take

```text
q=max(ab/p, ab/r).
```

If `p<=r`, then `q=ab/p`, and the difference in `(*)` becomes

```text
r - ab/r.
```

Here `p>=b`, `p<=r`, and `r>=a`, so `r>=max(a,b)>=sqrt(ab)`, hence
`r-ab/r>=0`.

The case `r<=p` is symmetric: `q=ab/r`, and the difference becomes

```text
p - ab/p >= 0.
```

Therefore every complete Flat5 cell satisfies `mu<=n`, so

```text
beta_Q(Z)=0.
```

This proves `BANK5-local` in the complete-cell model, but also shows why it is
not the missing bank mechanism.

Exact check: I brute-forced all feasible complete Flat5 class sizes up to 20:

```text
constraint:
  n0*n4 = min(n0*n1, n1*n2, n2*n3, n3*n4, n4*n0)

feasible cells checked = 695197
max beta_Q(Z) = 0
```

So under the adjacent-product/max-cut constraints a complete weighted `C5`
flat cell already has `mu_Q(Z) <= n`; this is the clean `C5` blow-up AM-GM
phenomenon.  It cannot explain the observed `prebank=1` cases.  Those are
cage/subset atoms, for example:

```text
D_Q(U)=9, |U|=6, sigma(U)=2, prebank=1,
```

where peeling a Flat5 singleton cage drops prebank by `3` or `4`.  Therefore
the bank proof must be stated at the Flat5 cage-peeling level, not only as a
complete-cell `beta_Q(Z)` inequality.

## Bank5 Global

The actual global bank lemma is:

```text
sum_Z beta_Q(Z) <= eta.                             (BANK5-global)
```

This is not automatic from BANK5-local unless the selected cells satisfy the
packing inequality

```text
sum_Z (n(Z)^2/25 - m(Z)) <= N^2/25 - m.             (BANK-PACK)
```

So the exact gate should test `BANK-PACK` for the banked flat cells selected
by terminal-closure peeling.  If this fails, the proof route fails at the
bank, not at Gamma descent.

After the complete-cell scan, the more relevant bank target is:

```text
Flat5 cage-peeling bank:
  choose a terminal-closure-compatible sequence of Flat5 zero-slack cages
  S_1,...,S_k inside U.
  Let U_0=U and U_i=U_{i-1}-S_i.
  The raw drop
      raw_i = pre_Q(U_{i-1}) - pre_Q(U_i)
  is not the bank demand; it may exceed eta.
  Charge only the positive part consumed by the peel:
      bank_i = max(0, pre_Q(U_{i-1})) - max(0, pre_Q(U_i)).
  Prove sum_i bank_i <= eta.
```

Exact correction: the raw-drop formulation is false.  In the `N=10/11`
max-prebank witnesses, `pre_Q(U)=1` and a Flat5 singleton peel can send the
remaining prebank to `-2` or `-3`, so `raw_i` can be `3` or `4` while `eta`
is smaller.  The actual bank demand is the positive-part decrement, here
`bank_i=1`.

The full `N<=11` banked-flat gate supports this cage-level version:

```text
N=10: positive_cases=12, all prebank=1, all Flat5, no over_eta.
N=11: positive_cases=40, all prebank=1, all Flat5, no over_eta.
```

## Positive-Part Flat5 Peel Gate

I added the corrected positive-part bank verifier:

```text
problems/23/writeup/_codex_slack_cage_flat5_peel_gate.py
```

For each positive proper-counted prebank case, it asks whether either a strict
zero-slack Gamma drop exists, or a Flat5 zero-slack core `S` satisfies

```text
pre_Q(U-S) <= 0.
```

This is the one-step version of the corrected bank demand

```text
bank(S) = max(0, pre_Q(U)) - max(0, pre_Q(U-S)).
```

Full `N=10`:

```text
python problems/23/writeup/_codex_slack_cage_flat5_peel_gate.py \
  --n 10 --workers 60 --chunksize 8

positive = 12
needs_bank = 12
flat5_consumes_positive = 12
fail = 0
max_prebank = 1
max_bank = 1
VERDICT = PASS_FLAT5_POSITIVE_PART_PEEL
```

Full `N=11`:

```text
python problems/23/writeup/_codex_slack_cage_flat5_peel_gate.py \
  --n 11 --workers 60 --chunksize 8

positive = 40
needs_bank = 40
flat5_consumes_positive = 40
fail = 0
max_prebank = 1
max_bank = 1
VERDICT = PASS_FLAT5_POSITIVE_PART_PEEL
```

The max `N=11` witness remains:

```text
graph = J??CAAoR`Y?
Q = (4,9,1,7,10)
U = (1,4,5,7,9,10)
S = (4,)
pre_Q(U) = 1
pre_Q(U-S) = -3
bank(S) = 1
eta-bank margin = 46/25
```

Thus the corrected positive-part bank gate passes through the full `N<=11`
census.  The raw prebank drop is deliberately not used.

## CTD Structure Scan

I added:

```text
problems/23/writeup/_codex_slack_cage_ctd_structure_gate.py
```

This compares the fixed counted-row residual with the dynamic peel residual.
It confirms that the fixed residual is not the right bank object.

Full `N=10`:

```text
python problems/23/writeup/_codex_slack_cage_ctd_structure_gate.py \
  --n 10 --workers 60 --chunksize 8

positive = 12
flat5_pre_S_nonpositive = 8
flat5_pre_S_positive = 4
max fixed subset pre = 4
```

Full `N=11`:

```text
python problems/23/writeup/_codex_slack_cage_ctd_structure_gate.py \
  --n 11 --workers 60 --chunksize 8

positive = 40
flat5_pre_S_nonpositive = 28
flat5_pre_S_positive = 12
max fixed subset pre = 4
min Flat5 fixed pre_S = -1
```

Example showing the mismatch:

```text
graph = J??CAAoR`Y?
Q = (4,9,1,7,10)
U = (1,4,5,7,9,10)
pre_Q(U) = 1
Flat5 S = (4,)

fixed residual:
  mu_Q(S)-|S|-sigma(S) = 0
  fixed pre after = 1
  fixed consume = 0

dynamic Slack-CAGE residual:
  pre_Q(U-S) = -3
  bank_Q(S;U) = 1
```

So the Flat5 cage is visible only through dynamic deletion of rows from the
`D_Q(U)` sum, not through fixed vertex mass inside `S`.

## Lemma ZERO-SLACK

For a canonical cage `S` with `rho_Q(S)>0`,

```text
sigma(S)=0.
```

Equivalently, for every canonical cage with positive slack, prove

```text
mu_Q(S) - |S| - beta_5(S) <= sigma(S).              (ZS)
```

This is a terminal-closed, side-door-corrected local inequality, not a scalar
Hall inequality over arbitrary prefix sets.

Exact gate:

```text
Enumerate canonical cages S.
For every S with sigma(S)>0, assert mu_Q(S)-|S|-beta_5(S) <= sigma(S).
```

## Witness Matching Square Surplus

For a zero-slack canonical cage `S`, let

```text
C = delta_M(S)
E = delta_B(S)
|C|=|E|
```

Let `C_cnt` be the crossing bad edges witnessed by counted crossing rows.
Build a witness graph between `C_cnt` and `E`:

```text
g ~ e  iff some counted shortest row of g first exits S through e.
```

For each `e in E`, define

```text
lambda_S(e) = min{ ell(g): g in C_cnt and g~e }.
```

The suggested Hall input is:

```text
SDR-SQ:
  every zero-slack canonical residual cage admits a witness bijection
  nu:E -> C with nu(e)~e.
```

Then define the square surplus

```text
Xi2(S) =
  sum_{g in C} ell(g)^2
  - min_{bijections nu:E->C, nu(e)~e} sum_{e in E} ell(nu(e))^2.
```

If no witness bijection exists, this is a separate Hall failure to gate.

## Lemma SQ-DROP

If `S` is safe, zero-slack, `SDR-SQ` holds, and

```text
Xi2(S)>0,
```

then

```text
DeltaGamma(S)<0.
```

Proof sketch: for each new bad edge `e`, use its matched old bad edge `g`
and a terminal witness row.  After flipping `S`, the complementary path in
the old odd cycle gives a `B^S` path for `e` of length `ell(g)-1`, so
`ell_{B^S}(e) <= ell(g)`.  Safe noncrossing bad edges do not increase length.
Thus

```text
DeltaGamma(S) <= -Xi2(S).
```

## Lemma STRICT-RESIDUAL

The repaired strictness target is:

```text
rho_Q(S)>0 and S not banked C5-flat => Xi2(S)>0.   (STRICT)
```

The correct harmless zero-square-surplus obstruction is:

```text
Xi2(S)=0 and rho_Q(S)=0,
```

for example flat odd-cycle rotations such as `C7` prefixes.

Exact gate:

```text
For every zero-slack canonical cage S:
  if rho_Q(S)>0 and S is not banked C5-flat:
      assert Xi2(S)>0.
```

## Final Implication

Assume a minimal positive Slack-CAGE failure.

1. `CTD` gives a canonical cage with `rho_Q(S)>0`.
2. `BANK5-global` ensures positive debt is not entirely banked.
3. `ZERO-SLACK` gives `sigma(S)=0`.
4. `STRICT-RESIDUAL` gives `Xi2(S)>0` unless the cage is banked flat.
5. `SQ-DROP` gives `DeltaGamma(S)<0`.

Since `sigma(S)=0`, the flip preserves maximum-cut size; since `B^S` is
connected by cage definition, this contradicts connected `Gamma`-minimality.

Therefore no minimal positive debt pair exists, proving Slack-CAGE.

## First Exact Xi2 Gate

I added:

```text
problems/23/writeup/_codex_slack_cage_xi2_gate.py
```

This implements `Xi2(S)` on the existing cage-core family.  For a zero-slack
core switch it builds the counted-row witness graph between old crossing bad
edges and new blue-boundary exits, brute-forces the minimum square-cost
witness bijection, and reports whether every non-Flat5 zero-slack core has
positive `Xi2`.

Targeted runs on the two known max-prebank witness graphs:

```text
python problems/23/writeup/_codex_slack_cage_xi2_gate.py \
  --graph 'I?AAD@wF_'

positive_cases = 8
zero cages = 16
flat5 = 16
xi2_zero = 16
VERDICT = PASS_XI2_CORE
```

```text
python problems/23/writeup/_codex_slack_cage_xi2_gate.py \
  --graph 'J??CAAoR`Y?'

positive_cases = 8
zero cages = 16
flat5 = 16
xi2_zero = 16
VERDICT = PASS_XI2_CORE
```

This matches the repaired theory: the observed zero-slack cages with
`Xi2=0` are exactly Flat5 bank atoms, so they are harmless bank cases rather
than required Gamma-drop cases.

## Full N <= 11 Parallel Xi2 Gate

I then ran the graph-sharded parallel gate:

```text
problems/23/writeup/_codex_slack_cage_xi2_parallel_gate.py
```

Full `N=10`:

```text
python problems/23/writeup/_codex_slack_cage_xi2_parallel_gate.py \
  --n 10 --workers 60 --chunksize 8

graphs = 9832
positive_cases = 12
zero cages = 20
flat5 = 20
xi2_zero = 20
VERDICT = PASS_XI2_CORE
```

Full `N=11`:

```text
python problems/23/writeup/_codex_slack_cage_xi2_parallel_gate.py \
  --n 11 --workers 60 --chunksize 8

graphs = 90842
positive_cases = 40
zero cages = 64
flat5 = 64
xi2_zero = 64
errors = 0
VERDICT = PASS_XI2_CORE
```

Max-prebank N=11 case:

```text
graph = J??CAAoR`Y?
cut = 0
m = 2
eta = 71/25
Q = (4,9,1,7,10)
U = (1,4,5,7,9,10)
D_Q(U) = 9
sigma(U) = 2
prebank = 1
margin = 46/25
zero cages: S={4}, S={5}
DeltaGamma = 0
Xi2 = 0
Flat5 = True
```

Here `m=2` is an example-specific global count.  The Xi2/Flat5 classification
is local to the counted zero-slack core and must not assume global `m=2`;
bridged extra odd-cycle components can increase `m` without changing the
local two-row Flat5 atom.

Thus every zero-slack core cage occurring in a positive proper-counted prebank
case through the full `N<=11` census is a Flat5 bank atom with `Xi2=0`.  No
non-Flat5 zero-slack cage with nonpositive `Xi2` occurs at census scale.

## Parallel Xi2 Census Gate

I added a graph-sharded wrapper:

```text
problems/23/writeup/_codex_slack_cage_xi2_parallel_gate.py
```

It reuses the same exact `Xi2` computation, but shards graph6 inputs across
worker processes.  It does not alter the core arithmetic.

Full `N=10`:

```text
python problems/23/writeup/_codex_slack_cage_xi2_parallel_gate.py \
  --n 10 --workers 60 --chunksize 8
```

Result:

```text
graphs = 9832
positive_cases = 12
zero = 20
flat5 = 20
xi2_zero = 20
max_prebank = 1
VERDICT = PASS_XI2_CORE
```

Full `N=11`:

```text
python problems/23/writeup/_codex_slack_cage_xi2_parallel_gate.py \
  --n 11 --workers 60 --chunksize 8
```

Result:

```text
graphs = 90842
positive_cases = 40
zero = 64
flat5 = 64
xi2_zero = 64
max_prebank = 1
VERDICT = PASS_XI2_CORE
```

Thus, in the full `N<=11` census, every zero-slack core switch arising from
a positive proper-counted prebank case is a true `Flat5` switch and has
`Xi2=0`.  The gate finds no non-Flat5 zero-slack core with nonpositive `Xi2`.

This supports the current split:

```text
Flat5 zero-slack cores      -> eta-bank charge
Non-Flat5 zero-slack cores  -> Xi2-positive square surplus -> Gamma descent
```

## Positive-Part Flat5 Peel Gate

The raw Flat5 peel drop is not the eta-bank charge.  The corrected charge is
the positive-part decrement:

```text
bank(S;U)=max(0,pre_Q(U))-max(0,pre_Q(U-S)).
```

I added:

```text
problems/23/writeup/_codex_slack_cage_flat5_peel_gate.py
```

This gate checks whether every positive proper-counted prebank case is either
handled by a strict zero-slack Gamma-drop cage, or by a true Flat5 cage whose
peel sends the remaining prebank to `<=0`.

Full census results:

```text
N=10:
  positive = 12
  needs_bank = 12
  flat5_consumes_positive = 12
  max_bank = 1
  VERDICT = PASS_FLAT5_POSITIVE_PART_PEEL

N=11:
  positive = 40
  needs_bank = 40
  flat5_consumes_positive = 40
  max_bank = 1
  VERDICT = PASS_FLAT5_POSITIVE_PART_PEEL
```

Worst/max-bank case:

```text
graph = cenJ??CAAoR`Y?#cut0
eta = 71/25
pre_Q(U) = 1
Flat5 peel S = (4)
pre_Q(U-S) = -3
bank(S;U) = 1
```

So at census scale, every Flat5 bank case consumes exactly one positive
prebank unit, even though the raw prebank drop may be `3` or `4`.
