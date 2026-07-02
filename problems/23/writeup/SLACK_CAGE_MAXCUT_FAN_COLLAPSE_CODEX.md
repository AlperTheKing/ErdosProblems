# Slack-CAGE Maxcut Fan-Collapse Atom

This note isolates the local maxcut mechanism behind the UNIT-FLAT5 bank
packing target.

## Two-Door Fan Lemma

Let `(G,B,M)` be any cut of a graph.  Suppose there is a nonempty vertex set

```text
W = L union A
```

with `|L|=k`, such that:

1. each `l in L` has one bad boundary edge from `W` to `V\W`;
2. these `k` bad boundary edges are distinct;
3. the blue boundary of `W` has size at most two:

```text
|delta_B(W)| <= 2;
```

4. no other bad boundary edges are needed for the lower bound, i.e.

```text
|delta_M(W)| >= k.
```

Then maximum-cut optimality implies

```text
k <= 2.
```

Indeed,

```text
sigma(W) = |delta_B(W)| - |delta_M(W)| <= 2-k.
```

If `k>=3`, then `sigma(W)<0`, contradicting the maxcut inequality
`delta_B(W) >= delta_M(W)`.

## Theta-Fan Instance

The theta guardrail family realizes the lemma with:

```text
L = {p_1,...,p_k},
A = {a},
W = L union {a}.
```

The bad boundary edges are:

```text
p_i d,  i=1,...,k.
```

The only blue boundary edges of `W` are the two first side-door edges out of
`a`, one into each corridor:

```text
a b,
a o_1.
```

Thus:

```text
delta_M(W)=k,
delta_B(W)=2,
sigma(W)=2-k.
```

The exact diagnostic

```text
python problems/23/writeup/_codex_slack_cage_flat5_cut_obstruction.py \
  --theta-max-t 6
```

returns `min_sigma = 2-k` for `k=2,...,6`.  The gmins stress

```text
python problems/23/writeup/_codex_slack_cage_flat5_fan_stress.py \
  --family theta --max-t 12 --gmins --max-cuts 64
```

has no positive UNIT bank cases for `k>=3`.

## Role In UNIT-PACK

A UNIT-FLAT5 atom is a two-leaf residue of this fan shape.  It is maxcut-tight:

```text
k=2,
sigma(W)=0.
```

The global packing problem is to prove that any attempted over-selection of
UNIT-FLAT5 atoms contains a blue-closed subfamily whose terminal side has
exactly this two-door fan form with `k>=3`.  Then the lemma gives a negative
slack switch, contradicting maximum-cut optimality.

So the remaining reduction target is:

```text
UNIT-overpack
  => exists blue-closed two-door selected fan W
     with k>=3 selected bad leaves and |delta_B(W)|<=2.
```

Once this reduction is proved, UNIT-PACK follows from the maxcut inequality.

## Exact Gate To Add Next

For every selected UNIT-FLAT5 atom, extract its two zero-slack singleton
peels.  Build a graph whose vertices are singleton peels and whose components
are blue-closed under shared side-door corridors.  For each component `C`,
compute:

```text
k(C)      = number of selected bad leaves in the component,
bdoor(C)  = number of blue boundary side-door edges of the component.
```

The finite gate is:

```text
if k(C) >= 3, then bdoor(C) >= k(C).
```

Equivalently, a component with `bdoor(C)<=2` must have `k(C)<=2`.  A failure
immediately constructs the negative-slack switch:

```text
sigma(W_C) = bdoor(C)-k(C) < 0.
```

This is stronger and more structural than the scalar grouped atom count.  It
is the exact combinatorial bridge needed between local UNIT-FLAT5 extraction
and global eta packing.

I added the first version of this gate:

```text
problems/23/writeup/_codex_slack_cage_unit_fan_component_gate.py
```

It groups selected UNIT-FLAT5 atoms by the common four vertices of their two
length-5 rows.  A group containing at least three distinct rows is the
row-level shadow of a multi-leaf fan.

Theta-family behavior:

```text
intended theta cuts:
  t=2: max_group_rows=2, bad_groups=0
  t=3: max_group_rows=3, bad_groups=1
  ...
  t=8: max_group_rows=8, bad_groups=1
  VERDICT = FAIL_FAN_COMPONENT_GATE

true gmins theta cuts through t=12:
  t=2: max_group_rows=2, bad_groups=0
  t=3..12: no positive UNIT cases
  VERDICT = PASS_FAN_COMPONENT_GATE
```

Full census:

```text
N=10:
  graphs=9832, cuts=15497
  positive=12, unit_cases=12
  max_group_rows=2, bad_groups=0
  group_row_hist={2:6}
  VERDICT = PASS_FAN_COMPONENT_GATE

N=11:
  graphs=90842, cuts=164986
  positive=40, unit_cases=40
  max_group_rows=2, bad_groups=0
  group_row_hist={2:20}
  VERDICT = PASS_FAN_COMPONENT_GATE
```

Thus, in all exact census UNIT cases, every common four-row core has exactly
two rows.  The intended theta counterfamily is detected precisely when it has
three or more rows sharing the same core, and true `gmins` cuts remove it.

## Protector-Path Gate

I added a second structural gate:

```text
problems/23/writeup/_codex_slack_cage_unit_protector_gate.py
```

For each selected UNIT-FLAT5 atom, let `U` be the six-vertex row union.  The
gate checks:

1. `delta_B(U)` has exactly two boundary door edges;
2. the two outside door endpoints are joined by a `B`-path entirely outside
   `U`.

This distinguishes true maxcut atoms from fake fans.  In theta intended cuts
with `t>=3`, the row-union boundary has three or more outside doors and no
two-door protector.  In true gmins theta cuts, only the two-leaf residue
survives and its protector distance is `3`.

Exact results:

```text
shared-path fan intended:
  t=2: unit_cases=2, atoms=1, atom_door_hist={2:1},
       atom_outside_dist_hist={None:1}, atom_missing=1
  t>=3: no UNIT cases in this row-union gate

shared-path fan gmins through t=8:
  no UNIT cases
  VERDICT = PASS_PROTECTOR_GATE

theta intended:
  t=2: unit_cases=2, atoms=1, door_hist={2:2}, atom_door_hist={2:1}, missing=0
  t=3: unit_cases=6, atoms=3, door_hist={3:6}, atom_door_hist={3:3}, missing=6
  t=4: unit_cases=12, atoms=6, door_hist={4:12}, atom_door_hist={4:6}, missing=12
  t=5: unit_cases=20, atoms=10, door_hist={5:20}, atom_door_hist={5:10}, missing=20

theta gmins through t=12:
  unit_cases=8, atoms=4, atom_door_hist={2:4}, atom_outside_dist_hist={3:4}, missing=0

N=10 census:
  unit_cases=12, atoms=6, atom_door_hist={2:6}, atom_outside_dist_hist={3:6}, missing=0

N=11 census:
  unit_cases=40, atoms=20, atom_door_hist={2:20}, atom_outside_dist_hist={3:18,4:2}, missing=0
```

So every exact census UNIT atom has a genuine outside blue protector path.
The shared-path fan shows why "two blue doors" alone is not enough: its
intended `t=2` atom has two doors but no outside protector path, and the
intended cut is not maxcut.

The proof target can be sharpened:

```text
selected UNIT atom
  => two blue doors + outside B-protector path;

three selected leaves sharing the same first-door side
  => at least three bad boundary edges but only two blue side doors
  => sigma<0.
```

## Endpoint Fan-Cut Gate

I added:

```text
problems/23/writeup/_codex_slack_cage_unit_fan_cut_gate.py
```

This gate builds the endpoint fan-side cut associated to each selected
common-four core and computes its actual `sigma`.

Generated guardrails:

```text
intended theta:
  t=2: sigma=0
  t=3: sigma=-1
  t=4: sigma=-2
  t=5: sigma=-3
  t=6: sigma=-4

theta gmins through t=8:
  atoms only at t=2
  fan_records=6
  negative=0
  sigma_hist={0:6}

shared-path fan intended t=2:
  fan_records=1
  negative=0
  sigma_hist={0:1}
```

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

So the intended theta obstruction is exactly a negative-slack fan-side cut
when `t>=3`, while every selected census fan-side record is maxcut-tight.
The shared-path fan still requires the protector-path gate, because its
two-leaf cut is tight but unprotected.

## Protected-Cell Peel Gate

The stronger protected-cell gate is:

```text
problems/23/writeup/_codex_slack_cage_unit_peel_gate.py
```

For each selected UNIT atom, it constructs

```text
C = U union outside_B_path
```

and verifies:

```text
|C| >= 10,
e_M(C) = 2,
delta_M(C) = 0.
```

Then it checks the intersection graph of protected cells.  Current exact
results:

```text
theta intended:
  t=2: atom_count_hist={1:1}, local cell passes
  t=3..6: missing_cell=3,6,10,15 respectively, FAIL

theta gmins through t=12:
  atom_count_hist={0:150,1:4}
  missing_cell=0
  bad_cell=0
  overlap_fail=0

N=10 full census:
  atom_count_hist={0:15491,1:6}
  cell_comp_hist={(1,):6}
  missing_cell=0
  bad_cell=0
  overlap_fail=0

N=11 full census:
  atom_count_hist={0:164966,1:20}
  cell_comp_hist={(1,):20}
  missing_cell=0
  bad_cell=0
  overlap_fail=0
```

This converts the local fan-collapse target into the current global packing
target: prove that canonical selected UNIT atoms either enter a negative-slack
multi-leaf fan or can be peeled by bad-boundary-free protected cells.
