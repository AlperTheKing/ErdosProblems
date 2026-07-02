# Slack-CAGE UNIT-FLAT5 Packing Target

This note isolates the current Flat5 bank subproblem.

## Local Unit Atom

For a row `Q` and a set `U`, a positive row-union Flat5 bank atom has the
following exact local signature:

```text
counted rows inside U touching Q: P0, P1
row lengths:                       5, 5
row geodesic denominators:          1, 1
Q is one of P0,P1
|V(P0) cap V(P1)| =                4
U = V(P0) union V(P1)
|U| =                               6
D_Q(U) =                            9
sigma(U) =                          2
pre_Q(U) = D_Q(U)-|U|-sigma(U) =    1
```

There is no strict zero-slack `Gamma` drop.  A zero-slack Flat5 peel deletes
length-5 row mass and consumes exactly the clipped positive part:

```text
bank_Q(S;U) = pre_Q(U)_+ - pre_Q(U-S)_+ = 1.
```

This is local only.  It does not imply global `m=2`; a glued extra odd-cycle
component preserves the same local atom while increasing global `m`.

## Global Packing Target

For a fixed connected-B gamma-minimal maximum cut, let `A` be any canonical
terminal-compatible selected family of UNIT-FLAT5 atoms.  The global bank
target is:

```text
|M| + |A| <= N^2/25.                         (UNIT-PACK)
```

Equivalently,

```text
|A| <= eta = N^2/25 - |M|.
```

If `UNIT-PACK` holds for the Flat5 bank peels selected by the dynamic
Slack-CAGE deletion process, then the Flat5 branch is eta-paid.

## Naive Grouped Census Gate

I added:

```text
problems/23/writeup/_codex_slack_cage_unit_pack_group_gate.py
```

The gate groups unit row-union cases by graph/cut and by the unordered pair
of counted row paths.  This avoids double-counting the same unit atom for the
two choices of `Q`.

Full census results:

```text
N=10:
  graphs = 9832
  cuts = 15497
  candidates = 1839450
  positive = 12
  unit_cases = 12
  nonunit_positive = 0
  atom_count_hist = {0:15491, 1:6}
  fails = 0

N=11:
  graphs = 90842
  cuts = 164986
  candidates = 43646364
  positive = 40
  unit_cases = 40
  nonunit_positive = 0
  atom_count_hist = {0:164966, 1:20}
  fails = 0
  min_margin = 21/25
```

Thus through the full `N<=11` census even the naive graph/cut-level unique
unit atom count satisfies `|M|+#atoms <= N^2/25`.  Moreover no graph/cut has
more than one unique unit atom in the exact census.

This is evidence, not proof.  The proof still needs:

1. **LOCAL extraction:** in the Flat5 bank branch, dynamic deletion selects
   only UNIT-FLAT5 atoms as above.
2. **GLOBAL packing:** terminal-compatible selected UNIT-FLAT5 atoms satisfy
   `UNIT-PACK`.

## Current Proof Lead

A dense fan of many length-5 rows sharing the same terminal 4-path is not a
source of many positive bank units.  Extra rows raise the relevant boundary
slack `sigma(U)` for the two-row union and kill positive prebank unless the
fan is exactly the two-row unit atom.

So the expected mechanism for `UNIT-PACK` is not "count every pair of rows".
It is a side-door packing theorem:

```text
each selected UNIT-FLAT5 atom requires enough max-cut side-door capacity
that it behaves like one pseudo-bad edge in the C5 extremal count.
```

The next useful finite gate is to generate larger terminal-compatible
Flat5-fan families and verify that the only positive selected atoms are the
two-row units and that their selected count is eta-paid.

## Named Row-Union Eta-Or-Unit Stress

The row-union gate:

```text
problems/23/writeup/_codex_slack_cage_rowunion_unit_gate.py
```

was also run on the named/two-lane/blowup battery:

```text
python problems/23/writeup/_codex_slack_cage_rowunion_unit_gate.py \
  --two-lane-max 28 --max-cuts 8 --max-union-rows 2 --include-gmins-blowups
```

Exact result:

```text
candidates = 1750374
positive = 38
eta_paid = 38
unit_eta_paid = 2
nonunit_eta_paid = 36
fails = 0
VERDICT = PASS_ROWUNION_ETA_OR_UNIT
```

The nonunit positives in this stress are long-row/two-lane row-union cases
with large eta margin, for example:

```text
two-lane-L8:
  n=27, m=4, eta=629/25
  row_lengths=[5,7,7,9]
  pre=1, margin=604/25
```

Thus the Flat5 bank branch remains isolated: the only row-union positives
not directly eta-paid are the UNIT-FLAT5 shape, and the named/gmins stress
does not create a multi-atom packing failure.

## Shared-Path Fan Guardrail

I added a parametric fan stress:

```text
problems/23/writeup/_codex_slack_cage_flat5_fan_stress.py
```

The generated intended cut has `t` length-5 bad rows sharing the same terminal
4-vertex blue path.  This is the obvious way UNIT-FLAT5 atoms could
proliferate.

The intended cut is a useful wrong-cut guardrail:

```text
python problems/23/writeup/_codex_slack_cage_flat5_fan_stress.py --max-t 20

t=2:
  N=8, m=2, eta=14/25, atoms=1
  UNIT-PACK margin = -11/25
```

So `UNIT-PACK` is false for arbitrary cuts.  This is not a contradiction to
the target, because the cut is not one of the connected-B gamma-min maximum
cuts.

Exact gmins check for the same family:

```text
python problems/23/writeup/_codex_slack_cage_flat5_fan_stress.py \
  --max-t 4 --gmins --max-cuts 32

t=2: gmins cuts checked = 3, intended cut not gmins, positive=0
t=3: gmins cuts checked = 3, intended cut not gmins, positive=0
t=4: gmins cuts checked = 3, intended cut not gmins, positive=0
VERDICT = PASS_FLAT5_FAN_STRESS
```

Interpretation: a raw shared-path fan can create a unit-packing violation, but
maxcut/gamma-min cut selection rotates away from that fan.  Therefore the
proof of `UNIT-PACK` must use maxcut side-door balance essentially.  It cannot
be a statement about arbitrary terminal row geometry.

## Boundary Dump Guardrail

I added:

```text
problems/23/writeup/_codex_slack_cage_unit_atom_boundary_dump.py
```

It compares three atoms:

```text
1. base N=10 census atom I?AAD@wF_
2. glued N=15 local atom plus an extra C5 component
3. intended t=2 shared-path fan, which is not a gmins cut
```

All three have the same local row-union shape:

```text
two length-5 unique rows
row intersection size = 4
U = row union, |U| = 6
D_Q(U) = 9
sigma(U) = 2
pre_Q(U) = 1
delta_M(U) = empty
two singleton zero-slack Flat5 peels
each peel has DeltaGamma = 0 and bank = 1
```

The difference is global:

```text
base N=10:        eta = 2       so one selected atom is eta-paid
glued N=15:       eta = 6       same local atom remains eta-paid
intended fan N=8: eta = 14/25   one selected atom would violate UNIT-PACK
```

The intended fan is not a true `gmins` cut:

```text
t=2 gmins check: cuts_checked=3, intended_in_checked=False, positive=0.
```

The sharper diagnostic:

```text
problems/23/writeup/_codex_slack_cage_flat5_cut_obstruction.py
```

shows that the intended fan is killed already by maximum-cut optimality, not
only by Gamma-minimality:

```text
base N=10:
  maxcut_bad_edges = 2
  intended_bad_edges = 2
  intended_is_connected_maxcut = True
  intended_is_gmin = True
  min_sigma_over_switches = 0

glued N=15:
  maxcut_bad_edges = 3
  intended_bad_edges = 3
  intended_is_connected_maxcut = True
  intended_is_gmin = True
  min_sigma_over_switches = 0

intended fan N=8:
  maxcut_bad_edges = 1
  intended_bad_edges = 2
  intended_is_connected_maxcut = False
  min_sigma_over_switches = -1
  min_sigma_sets include (0,1,2,6) and (5,7)
```

So `UNIT-PACK` cannot be proved from the local UNIT-FLAT5 shape.  The missing
global input is maxcut side-door balance: the fake fan has the same local
bank atom, but its terminal side doors expose a negative-slack switch.  The
good N=10/N=15 atoms have only zero-slack Flat5 rotations, never negative
slack.

This is now a hard proof guardrail:

```text
UNIT-FLAT5 local extraction is necessary but never sufficient.
UNIT-PACK must be stated for canonical atoms selected inside true connected-B
gamma-minimal maximum cuts, not for arbitrary terminal row fans.
```

## Theta-Fan Maxcut Collapse Guardrail

I extended the same stress script with:

```text
--family theta
```

The theta family has `t` private bad leaves sharing an inner length-4 blue
corridor and also an outer length-4 blue corridor.  The intended cut creates
many pairwise UNIT-FLAT5 row-union atoms and violates naive packing for
`t>=3`:

```text
python problems/23/writeup/_codex_slack_cage_flat5_fan_stress.py \
  --family theta --max-t 8

t=2: positive=2,  unit=2,  fails=0, atom_hist={1:1}
t=3: positive=6,  unit=6,  fails=1, atom_hist={3:1}
t=4: positive=12, unit=12, fails=1, atom_hist={6:1}
...
t=8: positive=56, unit=56, fails=1, atom_hist={28:1}
VERDICT = FAIL_FLAT5_FAN_STRESS
```

But true `gmins` cuts collapse the fan:

```text
python problems/23/writeup/_codex_slack_cage_flat5_fan_stress.py \
  --family theta --max-t 12 --gmins --max-cuts 64

t=2: cuts_checked=4,  intended_in_checked=False,
     positive=8, unit=8, fails=0, atom_hist={1:4}

t=3..12: cuts_checked=15 each, intended_in_checked=False,
        positive=0, unit=0, fails=0, atom_hist={0:15}

VERDICT = PASS_FLAT5_FAN_STRESS
```

Interpretation: the dangerous multi-leaf theta fan is killed by maximum-cut
selection before the bank can proliferate.  The only surviving theta case is
the two-leaf local UNIT atom.  This sharpens the proof target to a
**MAXCUT-FAN-COLLAPSE** lemma:

```text
If a terminal Flat5 fan contains three or more leaves sharing the same
two-corridor side-door structure, then some switch reduces the bad-edge
count.  Hence no connected-B maximum cut can select all those leaves as
bad rows.
```

This is the currently smallest structural route to `UNIT-PACK`: selected
UNIT-FLAT5 atoms must be disjoint two-leaf fan residues; attempted
multi-leaf residues expose a negative-slack side-door switch.

The local maxcut atom is isolated in:

```text
problems/23/writeup/SLACK_CAGE_MAXCUT_FAN_COLLAPSE_CODEX.md
```

I also added:

```text
problems/23/writeup/_codex_slack_cage_unit_fan_component_gate.py
```

This groups UNIT atoms by their common four-row core.  It detects the
intended theta counterfamily exactly:

```text
intended theta t=3..8: FAIL, max_group_rows=t
true gmins theta t=2..12: PASS, max_group_rows<=2
```

Full census results:

```text
N=10: positive=12, unit_cases=12, max_group_rows=2, bad_groups=0
N=11: positive=40, unit_cases=40, max_group_rows=2, bad_groups=0
```

The protector-path gate:

```text
problems/23/writeup/_codex_slack_cage_unit_protector_gate.py
```

also passes the exact census:

```text
shared-path fan intended:
  t=2: atoms=1, atom_door_count_hist={2:1},
       atom_outside_dist_hist={None:1}, atom_missing=1

shared-path fan gmins through t=8:
  no UNIT cases

N=10: unit_cases=12, atoms=6,
      atom_door_count_hist={2:6},
      atom_outside_dist_hist={3:6}, atom_missing=0

N=11: unit_cases=40, atoms=20,
      atom_door_count_hist={2:20},
      atom_outside_dist_hist={3:18,4:2}, atom_missing=0
```

Thus every census UNIT atom has exactly two blue doors and a blue protector
path between the outside door endpoints.  The shared-path fan shows that two
doors alone are not enough: its intended `t=2` local atom has no outside
protector.  Intended theta fans with `t>=3` fail because the row-union
boundary has three or more outside doors and no two-door protector.

## Protected-Cell Shape Catalog

I added:

```text
problems/23/writeup/_codex_slack_cage_unit_shape_catalog.py
```

For a selected UNIT atom with row union `U`, it takes the two old blue door
edges of `delta_B(U)` and a shortest blue path outside `U` between their
outside endpoints.  The protected cell is:

```text
C = U union outside_B_path.
```

The decisive recorded quantities are:

```text
shape =
(
  |C|,
  outside_path_length,
  e_B(C),
  e_M(C),
  |delta_B(C)|,
  |delta_M(C)|,
  |delta_B(U)|,
  |delta_M(U)|
)
```

Exact results:

```text
theta intended:
  t=2: shape=(10,3,10,2,0,0,2,0), missing=0
  t>=3: all UNIT atoms have missing protector path

theta true gmins through t=12:
  unit_cases=8, atoms=4
  shape=(10,3,10,2,0,0,2,0) for every case
  |delta_M(C)|=0

N=10 full census:
  graphs=9832, cuts=15497
  unit_cases=12, atoms=6
  shape=(10,3,10,2,0,0,2,0) for every case
  |delta_M(C)|=0

N=11 full census:
  graphs=90842, cuts=164986
  unit_cases=40, atoms=20
  shapes:
    (10,3,10,2,1,0,2,0) x24
    (10,3,10,2,2,0,2,0) x12
    (11,4,11,2,0,0,2,0) x4
  |delta_M(C)|=0 for every case
```

So every exact census UNIT atom is not merely two-doored.  It is contained in
a protected cell `C` with:

```text
|C| >= 10,
e_M(C) = 2,
|delta_M(C)| = 0,
bank_atom(C) = 1.
```

The first two fake fan families fail before this point:

```text
shared-path fan: no outside protector path
theta intended t>=3: no two-door protected cell; multi-leaf fan collapses by maxcut
```

## Protected-Cell Peel Target

The new local packing lemma to prove is:

```text
PROTECTED-UNIT-CELL.
Let A be a canonically selected UNIT-FLAT5 atom in a connected-B
gamma-minimal maximum cut.  Then either

  (i) A belongs to a multi-leaf fan core with at least three bad leaves, hence
      a negative-slack maxcut switch exists; or

  (ii) A has a protected cell C such that
       |C| >= 10,
       e_M(C) = 2,
       |delta_M(C)| = 0,
       and the selected bank atoms supported in C have total count 1.
```

The induction/discharge is then scalar and clean.  If `C` is removed and the
remaining selected atoms are handled recursively, then no bad edge crosses
from `C` to `V\C`, so:

```text
|M| + |A|
  = (e_M(C)+1) + (|M_rest|+|A_rest|)
  <= 3 + (N-|C|)^2/25.
```

Since `|C|>=10`,

```text
3 <= |C|^2/25,
```

and therefore

```text
3 + (N-|C|)^2/25
  <= |C|^2/25 + (N-|C|)^2/25
  <= N^2/25.
```

This proves `UNIT-PACK` for a disjoint protected-cell peel family.

Thus the remaining structural proof obligation is now narrower:

```text
Either selected UNIT atoms produce a maxcut-forbidden multi-leaf fan,
or they admit a vertex-disjoint peel ordering by bad-boundary-free protected
cells.
```

The exact next gate should test this peel ordering directly: build all
protected cells for selected UNIT atoms in a cut, construct their intersection
graph, and verify that every nontrivial intersection component is either a
single protected cell or a previously detected multi-leaf fan component.

## Endpoint Fan-Cut Gate

I added:

```text
problems/23/writeup/_codex_slack_cage_unit_fan_cut_gate.py
```

This gate groups selected UNIT atoms by their common four-row core, forms the
endpoint fan-side cut, and measures its maxcut slack `sigma`.

It detects the intended theta obstruction exactly:

```text
intended theta:
  t=2: sigma=0
  t=3: sigma=-1
  t=4: sigma=-2
  t=5: sigma=-3
  t=6: sigma=-4
```

Thus the multi-leaf intended theta family is forbidden by maxcut as soon as
there are three selected leaves sharing the same two-door fan.

True cuts pass:

```text
theta gmins through t=8:
  atoms only at t=2
  fan_records=6
  negative=0
  sigma_hist={0:6}

shared-path fan intended t=2:
  fan_records=1
  sigma_hist={0:1}
```

The shared-path fan guardrail again shows that fan-side sigma alone is not
enough; its two-leaf atom is maxcut-tight but has no outside protector.

Full census:

```text
N=10:
  atoms=6
  fan_records=10
  negative=0
  sigma_hist={0:10}

N=11:
  atoms=20
  fan_records=33
  negative=0
  sigma_hist={0:33}
```

So every census fan-side record is maxcut-tight, while the intended
multi-leaf theta failures expose strictly negative slack.

## Protected-Cell Peel Gate

I added:

```text
problems/23/writeup/_codex_slack_cage_unit_peel_gate.py
```

For each selected UNIT atom, it constructs the protected cell

```text
C = U union outside_B_path
```

and checks:

```text
|C| >= 10,
e_M(C) = 2,
delta_M(C) = 0,
```

then builds the protected-cell intersection components.  The current gate
accepts only singleton components unless the component has already been killed
by the fan-collapse branch.

Exact results:

```text
intended theta:
  t=2: atom_count_hist={1:1}, local cell passes
  t=3..6: missing_cell=3,6,10,15 respectively, FAIL

theta gmins through t=12:
  atom_count_hist={0:150,1:4}
  missing_cell=0
  bad_cell=0
  overlap_fail=0
  VERDICT=PASS_PROTECTED_CELL_PEEL

N=10 full census:
  graphs=9832
  cuts=15497
  atom_count_hist={0:15491,1:6}
  cell_comp_hist={(1,):6}
  missing_cell=0
  bad_cell=0
  overlap_fail=0
  VERDICT=PASS_PROTECTED_CELL_PEEL

N=11 full census:
  graphs=90842
  cuts=164986
  atom_count_hist={0:164966,1:20}
  cell_comp_hist={(1,):20}
  missing_cell=0
  bad_cell=0
  overlap_fail=0
  VERDICT=PASS_PROTECTED_CELL_PEEL
```

This leaves a precise structural obligation:

```text
canonical selected UNIT atoms either form a maxcut-forbidden multi-leaf fan,
or admit a peel ordering by protected cells with |C|>=10, e_M(C)=2,
delta_M(C)=0.
```

## Glued Multi-Cell Stress

I added:

```text
problems/23/writeup/_codex_slack_cage_multi_protected_cell_stress.py
```

It glues `k` copies of the known `N=10` protected atom `I?AAD@wF_` by blue
cut bridges.  This creates a connected-B cut with several independent local
UNIT atoms, testing the peel bookkeeping not exercised by the `N<=11`
census.

The generic collector is already clean for two copies:

```text
python -u problems/23/writeup/_codex_slack_cage_multi_protected_cell_stress.py --max-k 2

k=1: atom_hist={1:1}, cell_comp_hist={(1,):1}
k=2: atom_hist={2:1}, cell_comp_hist={(1,1):1}
VERDICT=PASS_GLUED_PROTECTED_CELL_STRESS
```

For larger `k`, a targeted shifted-atom collector avoids brute-force row-union
mixing across copies:

```text
python -u problems/23/writeup/_codex_slack_cage_multi_protected_cell_stress.py \
  --targeted --max-k 8

k=1..8:
  targeted_atoms=k
  cell_comp_hist={(1,...,1):1}
  missing=0
  bad_cell=0
VERDICT=PASS_GLUED_PROTECTED_CELL_STRESS
```

So the protected-cell peel abstraction handles multiple disjoint cells when
they are present.  The remaining untested/proof-critical case is not
disjoint gluing; it is overlapping protected cells or a multi-leaf fan core.

The same script now has a first overlapping-cell guardrail:

```text
python -u problems/23/writeup/_codex_slack_cage_multi_protected_cell_stress.py \
  --nested-overlap
```

This tries to reuse the base protector path as a second UNIT core.  It does
not produce an admissible protected-cell overlap:

```text
atom_count_hist={1:1}
bad_cell=1
first_bad_cell has:
  cell_size=10
  cell_bad_inside=3
  cell_bad_boundary=1

bad_intended=4
max_bad=2
intended_conn_max=False
min_sigma=-2
VERDICT=PASS_NESTED_OVERLAP_GUARDRAIL
```

So the most direct overlap attempt is already killed by maxcut, and before
that it fails the protected-cell condition because an extra bad edge crosses
or enters the would-be cell.
