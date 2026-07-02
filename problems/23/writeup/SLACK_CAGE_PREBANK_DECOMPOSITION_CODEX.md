# Slack-CAGE Prebank Decomposition Target

This note isolates the proof obligation suggested by the exact Slack-CAGE
gates through the full `N=11` census.

## Target

For a connected-`B`, `Gamma`-minimal maximum cut, a row `Q`, and `U subset V`,
write

```text
D_Q(U) = sum_g (1 / |cyc[g]|)
         sum_{P in cyc[g], V(P) subset U} |V(P) cap V(Q)|

sigma(U) = delta_B(U) - delta_M(U)
eta = N^2/25 - m
pre_Q(U) = D_Q(U) - |U| - sigma(U)
```

Slack-CAGE is

```text
pre_Q(U) <= eta.                                      (SC)
```

At `U=V`, this gives the corrected row-sum ceiling.

## Evidence Pattern

The exact gates show:

```text
Full N=11 all-subset census:
  graphs = 90842
  connected gamma-min maximum cuts = 171182
  checks = 2167949312
  violations = 0
  min proper nonempty margin = 251/150
```

The largest observed proper-counted prebank witness at `N=11` is:

```text
graph = J??CAAoR`Y?
m = 2
eta = 71/25
Q = (4,9,1,7,10)
U = (1,4,5,7,9,10)
D_Q(U) = 9
sigma(U) = 2
pre_Q(U) = 1
margin = eta - pre_Q(U) = 46/25
```

The displayed `m=2` is the global bad-edge count of this census witness only.
It is not part of the local Flat5 bank atom: the same two-counted-row
configuration survives after gluing an additional bridged `C5`, where the
global graph has `m=3`.

The exact cage classifier finds eight symmetric positive cases on this graph.
Every one has zero-slack flat singleton cages:

```text
S = {4} or S = {5}
sigma(S) = 0
DeltaGamma(S) = 0
strict_drop_cases = 0
```

Peeling these flat cages gives:

```text
pre_Q(U)       =  1
pre_Q(U - {4}) = -3
pre_Q(U - {5}) = -2
pre_Q(U - {4,5}) = -6
```

So the observed positive proper prebank is not a non-balanced obstruction; it
is a balanced length-5 cell whose contribution is strictly removable and paid
by `eta`.

## Proposed Proof Split

The proof should not first choose balanced cells globally. It should first
decompose `pre_Q(U)`.

### Lemma 1: Minimal Prebank Support

If `(Q,U)` is lexicographically minimal with `pre_Q(U) > eta`, then every
vertex of `U` is used by either:

```text
1. a counted row contained in U and meeting Q, or
2. a blue/bad boundary edge contributing to sigma(U).
```

Otherwise removing an unused blue-closed component of `U` preserves or
increases `pre_Q(U)-eta`, contradicting minimality.

Exact gate:

```text
For every positive-prebank U, remove each B[U]-component not touched by
counted rows or boundary.  Check pre_Q(U') >= pre_Q(U).
```

### Lemma 2: Terminal Cage Cover

For a minimal positive-debt pair, the positive part of `pre_Q(U)` admits a
cover by inclusion-minimal terminal cages `S_i subset U` such that:

```text
every counted row crossing S_i crosses terminally;
every e in delta_B(S_i) is a first exit of a counted row;
B^{S_i} is connected.
```

Moreover the cage accounting has the form

```text
pre_Q(U)
<= bank_5(Q,U) + sum_i surplus(S_i),                (COVER)
```

where `bank_5` is supported only on flat balanced length-5 cells, and
`surplus(S_i)` is nonpositive unless the cage is zero-slack or better.

Exact gate:

```text
For every positive proper-counted prebank case:
  enumerate inclusion-minimal cage cores;
  assert either a flat length-5 bank cage is peelable,
  or a zero-slack strict-drop cage exists.
```

### Lemma 3: Eta Pays The Flat Length-5 Bank

The total flat bank satisfies

```text
bank_5(Q,U) <= eta.                                  (BANK)
```

A flat bank atom is a zero-slack cage with:

```text
sigma(S) = 0
DeltaGamma(S) = 0
all crossing counted rows have length 5
peeling S strictly decreases pre_Q
```

Observed atoms have singleton cages, but the lemma should allow a blue-closed
balanced `C5` cell.

Exact gate:

```text
Iteratively peel all flat length-5 cages S with pre_Q(U-S) < pre_Q(U).
Track total pre_Q drop.  Assert total dropped flat bank <= eta and the
remaining U either has nonpositive prebank or a strict-drop cage.
```

Equivalent extremal form to prove:

```text
m + bank_5(Q,U) <= N^2/25.                           (AUG-C5)
```

This is the non-circular way to use the global deficit.  A Flat5 bank atom
does not decrease `Gamma`; instead it behaves like one missing unit in the
`C5` extremal bad-edge count.  The proof should build an augmented length-5
quotient from the selected flat cells and show that the original bad edges
plus these bank atoms still obey the sharp `C5` product bound.

The exact evidence suggests that each observed Flat5 atom has unit bank
demand:

```text
bank_atom(S) = max(0, pre_Q(U)) - max(0, pre_Q(U - S))
               after normalizing overlaps
```

but the proof should allow overlapping flat cells by selecting a laminar or
peeling order and charging only the consumed positive prebank.  The raw
quantity `pre_Q(U)-pre_Q(U-S)` is not a valid bank demand: exact witnesses can
drop from `1` to a negative value, giving raw drops `3` or `4` while the
actual bank consumption is only `1`.

Exact gate refinement:

```text
For every positive prebank case:
  choose a sequence of Flat5 peelings S_1,...,S_k.
  Let bank_i = max(0, pre(U_{i-1})) - max(0, pre(U_i)).
  Assert sum_i bank_i <= eta
  and pre(U_k) <= 0 unless a strict-drop cage exists.
```

This gate is stronger than merely finding one flat cage, because it tests the
proposed augmented extremal budget.

Implemented exact gate:

```text
problems/23/writeup/_codex_slack_cage_flat5_peel_gate.py
```

Full census results:

```text
N=10: positive=12, needs_bank=12, flat5_consumes_positive=12, fail=0.
N=11: positive=40, needs_bank=40, flat5_consumes_positive=40, fail=0.
```

In every positive case through `N<=11`, a single Flat5 zero-slack peel consumes
all positive prebank in the corrected positive-part sense.  The maximum bank
charged is `1`.

### Dynamic Deletion, Not Fixed Mass

The Flat5 bank must be formulated with dynamic row deletion:

```text
drop_Q(S;U) = pre_Q(U) - pre_Q(U-S)
            = D_Q(U)-D_Q(U-S) - |S| - (sigma(U)-sigma(U-S)).
```

The fixed-row residual

```text
mu_Q(S)-|S|-sigma(S)
```

does not see all Flat5 bank atoms.  I added:

```text
problems/23/writeup/_codex_slack_cage_ctd_structure_gate.py
```

It gives:

```text
N=10: positive=12, flat5 fixed-pre nonpositive=8, positive=4.
N=11: positive=40, flat5 fixed-pre nonpositive=28, positive=12.
```

In the max `N=11` witness, `pre_Q(U)=1`, the Flat5 peel has fixed residual
`0`, but dynamic `pre_Q(U-S)=-3`, so it consumes the full positive bank.  Thus
the proof target is a dynamic deletion/peeling lemma, not a positive fixed-mass
cage lemma.

### Lemma 4: Non-Balanced Zero-Slack Cage Drops Gamma

If a terminal cage `S` is not a flat balanced length-5 bank atom and

```text
sigma(S) = 0,
```

then

```text
DeltaGamma(S) < 0.                                  (DROP)
```

Reason: flipping `S` replaces each crossing bad edge by witnessed first-exit
blue edges. Terminality gives replacement paths in the switched blue graph.
Shortestness gives weak square-length domination; equality forces every
crossing packet to be a length-5 balanced cell. Therefore non-balanced equality
is impossible.

Exact gate:

```text
Enumerate minimal terminal cages with sigma(S)=0.
If DeltaGamma(S)=0, assert the crossing-row data is a flat length-5 bank atom.
If not flat, assert DeltaGamma(S)<0.
```

### Lemma 5: Positive Residual Forces Zero Slack

After removing the flat bank atoms, if the residual prebank is still positive,
then some residual terminal cage has

```text
sigma(S) = 0.                                      (ZERO)
```

If every residual cage had `sigma(S)>0`, summing first-exit inequalities over
the terminal-cage cover would make the residual contribution nonpositive,
contradicting positive residual prebank.

Exact gate:

```text
After flat-bank peeling, classify all positive residual cases.
Assert existence of a minimal cage with sigma=0.
```

## Consequence

Assume `(SC)` fails.  Choose a minimal pair with `pre_Q(U)>eta`.

By `BANK`, flat length-5 cells account for at most `eta`.  Therefore the
residual prebank is positive.  By `ZERO`, some residual cage has `sigma=0`.
By `DROP`, that cage has `DeltaGamma<0`.

Flipping it preserves maximum-cut size and connectedness but lowers `Gamma`,
contradicting `Gamma`-minimality.  Hence `(SC)` holds.

## Current Status

The stronger census-scale version of the flat-bank check is recorded in:

```text
problems/23/writeup/SLACK_CAGE_BANKED_FLAT_CELL_SPLIT_CODEX.md
problems/23/writeup/_codex_slack_cage_banked_flat_gate.py
```

That gate scans all positive proper-counted prebank cases and tests:

```text
if no strict Gamma-drop zero-slack cage exists:
    prebank <= eta
    and at least one Flat5 zero-slack cage exists.
```

It has already passed the full `N <= 11` census:

```text
N=10:
  positive_cases = 12
  strict_cases = 0
  no_strict_cases = 12
  no_strict_flat = 12
  no_strict_over_eta = 0
  no_strict_no_flat = 0
  prebank_values = {1: 12}
  VERDICT = PASS_BANKED_FLAT

N=11:
  graphs = 90842
  cuts = 171182
  positive_cases = 40
  strict_cases = 0
  no_strict_cases = 40
  no_strict_flat = 40
  no_strict_over_eta = 0
  no_strict_no_flat = 0
  prebank_values = {1: 40}
  VERDICT = PASS_BANKED_FLAT
```

So the exact census state is stronger than the targeted max-witness checks
below: every positive proper-counted prebank case through `N=11` is eta-paid
and Flat5.

The following exact facts support the split:

```text
N=10 full classifier:
  positive proper-counted prebank cases = 12
  all have prebank = 1
  no_zero = 0
  no_flat = 0
  strict_drop_cases = 0
  verdict = PASS_BALANCED

N=11 max-prebank witness classifier:
  positive proper-counted prebank cases = 8
  all have prebank = 1
  no_zero = 0
  no_flat = 0
  strict_drop_cases = 0
  flat cages S={4},{5}
```

The explicit flat-bank gate

```text
problems/23/writeup/_codex_slack_cage_flat_bank_gate.py
```

was then run on the two known max-prebank witness graphs:

```text
python problems/23/writeup/_codex_slack_cage_flat_bank_gate.py \
  --graph 'I?AAD@wF_'

N=10 witness:
  cases = 8
  no_flat_bank = 0
  prebank_values = {1: 8}
  flat cages S={3},{4}
  peel drops = 4 and 3
  VERDICT = PASS_FLAT_BANK
```

```text
python problems/23/writeup/_codex_slack_cage_flat_bank_gate.py \
  --graph 'J??CAAoR`Y?'

N=11 witness:
  cases = 8
  no_flat_bank = 0
  prebank_values = {1: 8}
  flat cages S={4},{5}
  peel drops = 4 and 3
  VERDICT = PASS_FLAT_BANK
```

No exact evidence currently shows a positive proper-counted prebank case that
is not a banked flat length-5 cell.

## Updated deletion profile for the bank branch

The corrected dynamic deletion gate profiles the rows removed by the Flat5
bank peel.  It shows that the useful bank unit is the clipped positive-part
drop, not the raw prebank drop.

```text
script:
  problems/23/writeup/_codex_slack_cage_flat5_deletion_profile.py

N=10:
  cases = 12
  deleted profiles:
    one length-5 unit row with |P cap Q|=4 : 4
    one length-5 unit row with |P cap Q|=5 : 4
    both of the above                         : 4
  raw drops = 3,4,5 each in 4 cases
  sigma_diff = 0 in all 12 cases

N=11:
  cases = 40
  deleted profiles:
    one length-5 unit row with |P cap Q|=4 : 14
    one length-5 unit row with |P cap Q|=5 : 14
    both of the above                         : 12
  raw drops:
    3 : 14
    4 : 14
    5 : 12
  sigma_diff = 0 in all 40 cases
```

Thus every observed bank peel is a length-5 row-deletion event with no cut
slack change, but its charge to the global eta-bank is always

```text
pre_Q(U)_+ - pre_Q(U-S)_+ = 1.
```

The proof obligation is now to show that any terminal-compatible sequence of
these Flat5 bank units can be injected into the global C5 deficit bank:

```text
|M| + sum bank_i <= N^2/25.
```
