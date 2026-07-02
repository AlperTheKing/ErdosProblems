# Protected UNIT-FLAT5 Packing Lemma Target

Date: 2026-07-02

This note states the current proof target for the Flat5 bank branch of
SLACK-CAGE after the protector-path gates.

## Local Protected Unit

A selected `UNIT-FLAT5` atom consists of two unique length-5 rows:

```text
P_a = (a,x1,x2,x3,t),
P_b = (b,x1,x2,x3,t)
```

up to reversal and the opposite-ended variant.  The row union is:

```text
U = V(P_a) union V(P_b),
|U| = 6,
pre_Q(U) = D_Q(U)-|U|-sigma(U) = 1.
```

It is a local bank atom, not a Gamma-decreasing switch:

```text
zero-slack Flat5 peel consumes bank 1.
```

The exact gates show that a true selected unit in a connected-B gamma-min
maximum cut has more structure:

```text
|delta_B(U)| = 2,
```

and if the two outside endpoints of `delta_B(U)` are `r` and `s`, then:

```text
there is a B-path from r to s contained in V \ U.
```

Call this a **protected UNIT-FLAT5 atom**.

## Guardrails

Two false local statements are now ruled out.

### Two Rows Alone Is Not Enough

The shared-path fan at `t=2` has one local two-row UNIT atom, but the outside
door endpoints are not connected in `B[V\U]`.  The intended cut is not a
maximum cut.

Exact gate:

```text
shared-path fan intended t=2:
  atoms=1
  atom_door_count_hist={2:1}
  atom_outside_dist_hist={None:1}
  atom_missing=1
  VERDICT=FAIL_PROTECTOR_GATE
```

### Protector Length Is Not Fixed

Full census `N=11` has protected atoms with outside protector distance `4`.
Thus the proof must use existence of the outside path, not a fixed 10-vertex
cell.

Exact gate:

```text
N=11 census:
  atoms=20
  atom_door_count_hist={2:20}
  atom_outside_dist_hist={3:18,4:2}
  atom_missing=0
```

## Remaining Lemma

Let `A` be the canonical selected family of protected UNIT-FLAT5 atoms
arising from a minimal positive-debt SLACK-CAGE deletion process.

Define the blue-closed selected fan component of a subfamily by closing the
six-vertex row unions under:

1. shared terminal four-row cores;
2. shared bad leaves;
3. shared blue door endpoints;
4. outside protector paths in `B[V\U]`.

For a component `C`, let:

```text
k(C) = number of selected bad leaves represented in C,
b(C) = number of blue boundary side-door edges leaving C.
```

The desired protected packing lemma is:

```text
For every selected fan component C,
    b(C) >= k(C).
```

Equivalently, if `k(C) >= 3`, then `C` must expose at least `k(C)` blue
side-door boundary edges.

## Why This Proves The Flat5 Branch

If a component violates the lemma, then:

```text
sigma(C) = delta_B(C)-delta_M(C) <= b(C)-k(C) < 0,
```

because the `k(C)` selected leaves give distinct bad boundary edges.  This
contradicts maximum-cut optimality.

Therefore a connected-B maximum cut cannot contain an overpacked selected
protected fan component.  The remaining bookkeeping task is to show that the
canonical selected family has:

```text
|selected protected UNIT atoms| <= eta = N^2/25 - |M|.
```

The intended theta family shows the exact obstruction that the lemma must
kill:

```text
t selected leaves sharing one corridor
=> b=2, k=t, sigma=2-t.
```

True `gmins` cuts eliminate all `t>=3` cases.

## Current Exact Evidence

Protector-path gate:

```text
true gmins theta through t=12:
  atoms=4, atom_missing=0

N=10 census:
  atoms=6, atom_missing=0

N=11 census:
  atoms=20, atom_missing=0
```

Fan-component gate:

```text
intended theta t>=3:
  max_group_rows=t, FAIL

true gmins theta through t=12:
  max_group_rows<=2, PASS

N=10 census:
  max_group_rows=2, bad_groups=0

N=11 census:
  max_group_rows=2, bad_groups=0
```

The proof should now focus on converting the exact common4/protector
structure into the component inequality `b(C) >= k(C)`.
