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

Protected-cell shape catalog:

```text
theta gmins through t=12:
  atoms=4
  shape=(10,3,10,2,0,0,2,0) for every atom

N=10 census:
  atoms=6
  shape=(10,3,10,2,0,0,2,0) for every atom

N=11 census:
  atoms=20
  shapes:
    (10,3,10,2,1,0,2,0) x24 unit cases
    (10,3,10,2,2,0,2,0) x12 unit cases
    (11,4,11,2,0,0,2,0) x4 unit cases
```

Here

```text
shape=(|C|, outside_path_length, e_B(C), e_M(C),
       |delta_B(C)|, |delta_M(C)|, |delta_B(U)|, |delta_M(U)|).
```

Thus every census protected cell has:

```text
|C| >= 10,
e_M(C) = 2,
delta_M(C) = 0.
```

Protected-cell peel gate:

```text
theta gmins through t=12:
  atom_count_hist={0:150,1:4}
  missing_cell=0
  bad_cell=0
  overlap_fail=0

N=10 census:
  atom_count_hist={0:15491,1:6}
  cell_comp_hist={(1,):6}
  missing_cell=0
  bad_cell=0
  overlap_fail=0

N=11 census:
  atom_count_hist={0:164966,1:20}
  cell_comp_hist={(1,):20}
  missing_cell=0
  bad_cell=0
  overlap_fail=0
```

The discharge after a protected-cell peel is scalar:

```text
(e_M(C)+1) = 3 <= |C|^2/25       because |C|>=10.
```

Since `delta_M(C)=0`, no bad edge crosses from the cell to its complement.
So a vertex-disjoint protected-cell peel family pays one selected bank atom
per cell.

Glued multi-cell stress:

```text
problems/23/writeup/_codex_slack_cage_multi_protected_cell_stress.py
```

Generic collection passes through two glued copies:

```text
k=1: atom_hist={1:1}, cell_comp_hist={(1,):1}
k=2: atom_hist={2:1}, cell_comp_hist={(1,1):1}
```

Targeted shifted-atom collection passes through eight copies:

```text
k=1..8:
  targeted_atoms=k,
  cell_comp_hist={(1,...,1):1},
  missing=0,
  bad_cell=0.
```

This confirms the scalar peel bookkeeping on a generated connected cut with
several independent protected cells.  It does not address overlapping cells;
that remains the structural gap.

Nested-overlap guardrail:

```text
python -u problems/23/writeup/_codex_slack_cage_multi_protected_cell_stress.py \
  --nested-overlap
```

This tries to reuse the base protector path as a second UNIT core.  Exact
result:

```text
atom_count_hist={1:1}
bad_cell=1
first_bad_cell:
  cell_size=10
  cell_bad_inside=3
  cell_bad_boundary=1
bad_intended=4
max_bad=2
intended_conn_max=False
min_sigma=-2
VERDICT=PASS_NESTED_OVERLAP_GUARDRAIL
```

Thus the first natural protected-cell overlap attempt creates extra bad
boundary in the old cell and is not a maximum cut.  This supports the
structural conjecture that genuine overlap forces either bad-boundary failure
or a maxcut-forbidden fan switch.

Exhaustive base-cell path-reuse overlap search:

```text
problems/23/writeup/_codex_slack_cage_overlap_attempt_search.py
```

This enumerates every way to create a second UNIT-FLAT5 atom by reusing a
3-edge blue path already inside the known `N=10` protected cell.  It tests:

```text
one_existing_one_new:
  one second-cell leaf is an existing cell vertex, one leaf is new;

two_new:
  both second-cell leaves are new, but the common blue path lies in the old
  protected cell.
```

Exact result:

```text
base_paths_len3 = 24
attempts = 44
triangle_free = 44
negative_sigma = 44
intended_conn_max = 0
bad_cell = 4
overlap_fail = 2
VERDICT = PASS_OVERLAP_ATTEMPT_SEARCH
```

The only overlap-fail shapes are the symmetric reuse of the old protector path
as the second UNIT core.  In both orientations:

```text
bad_intended = 4
max_bad = 2
intended_conn_max = False
min_sigma = -2
```

and each affected protected cell gains bad boundary:

```text
cell_bad_inside = 2
cell_bad_boundary = 2
cell_blue_boundary = 2.
```

The actual negative-slack witnesses are small terminal sides.  For the reuse
of the old protector path

```text
path = (2,7,0,5),
```

one minimum witness is:

```text
S = {5,9},      sigma(S) = -2.
```

For the reverse orientation

```text
path = (5,0,7,2),
```

one minimum witness is:

```text
S = {2,3,4,8},  sigma(S) = -2.
```

So, in the complete local base-cell search, every path-reuse overlap is
already killed by maxcut negativity; none yields a connected maximum cut with
two valid overlapping protected cells.  This strengthens the next structural
lemma to prove:

```text
If two canonical protected UNIT cells overlap, then their overlap contains a
blue path-reuse configuration whose blue-closed side has negative sigma, or
one of the cells is not protected because it has bad boundary.
```

Two-copy protected-cell path-amalgamation stress:

```text
problems/23/writeup/_codex_slack_cage_two_cell_amalgam_stress.py
```

This takes two copies of the known protected `N=10` cell and identifies a
side-compatible blue path in the second copy with a blue path in the first.
It tests path edge-lengths `2`, `3`, and `4`.

Exact results:

```text
length 4:
  attempts = 160
  triangle_free = 160
  negative_sigma = 152
  bad_cell = 4
  remaining 8 have atom_count_hist={0:1}
  VERDICT = PASS_TWO_CELL_AMALGAM_STRESS

length 3:
  attempts = 144
  triangle_free = 144
  negative_sigma = 144
  overlap_fail = 1
  overlap-fail min_sigma = -1
  VERDICT = PASS_TWO_CELL_AMALGAM_STRESS

length 2:
  attempts = 194
  triangle_free = 194
  bad_cell = 32
  overlap_fail = 4
  every overlap-fail has min_sigma = -1
  VERDICT = PASS_TWO_CELL_AMALGAM_STRESS
```

For length `4`, the only nonnegative-sigma amalgams identify an entire counted
row path so completely that no UNIT atom remains.  For lengths `2` and `3`,
every amalgamated overlapping-cell component detected by the classifier has a
negative-sigma witness.  Thus, across these two-copy positive-length
path-overlap models, a valid connected maximum cut never contains two
overlapping protected UNIT cells.

Single-vertex contact correction:

The stronger "protected cells are vertex-disjoint" formulation is false.  Two
protected cells can touch in exactly one vertex and still survive both maxcut
and Gamma-minimality.  The remaining contact model is therefore cactus-like:
positive-length path overlap is killed as above, but one-vertex contacts must
be allowed in the packing lemma.

Exact vertex-sharing survey over two copies of the known protected `N=10` cell:

```text
side-compatible single-vertex identifications:
  attempts = 31
  triangle_free = 31
  bad_cell = 6
  overlap_fail = 6

overlap-fail pairs:
  (0,0), (0,2), (2,2), (5,5), (5,7), (7,7)
```

For all six overlap-fail pairs:

```text
n = 19
bad_intended = 4
max_bad = 4
conn_maxcuts = 361
intended_conn_max = True
min_sigma = 0
Gamma(intended) = 100
min_Gamma among connected maxcuts = 100
number of Gamma-min connected maxcuts = 16
atom_count_hist = {2:1}
cell_comp_hist = {(2,):1}
```

So one-vertex contacts are genuine Gamma-minimal connected-maximum-cut
configurations, not artefacts of a nonmaximal cut.  The corrected structural
target is:

```text
In a Gamma-min connected maximum cut, canonical protected UNIT cells form a
cactus family: any two distinct cells intersect in at most one vertex.  If
they share a positive-length blue path, then either one cell has bad boundary
or a negative-sigma terminal side exists.
```

The discharge must therefore be stated for cactus families, not only for
vertex-disjoint families.  A component of `k` protected UNIT cells with only
single-vertex contacts has union size at least `9k+1` in the two-copy model,
and no bad edge crosses an individual protected cell boundary.  The remaining
proof obligation is the general cactus-packing inequality that pays one
selected bank atom per protected cell under these allowed one-vertex contacts.

Claude independent gate, 2026-07-02T01:42:21Z:

```text
census N<=11 gmins:
  N=10 cell_comp_hist={(1,):6}
  N=11 cell_comp_hist={(1,):20}
```

Thus every protected-cell intersection component in the exact census is a
singleton; no overlapping pair of protected UNIT cells appears in census
`N<=11`.  This makes the positive-length overlap trichotomy vacuous on census,
consistent with the local two-copy stress above.

C5 blow-ups are also vacuous for UNIT-FLAT5.  A protected unit atom needs two
denominator-1 length-5 rows, but in a nontrivial C5 blow-up every bad edge has
at least `a*b*c` shortest rows (balanced `t>=2` gives `t^3`).  So dense C5
blow-ups can be skipped by an early exit:

```text
if all |cyc[g]| > 1:
    no UNIT-FLAT5 atom can exist.
```

Claude's extension tail for glued chains, islands, MycGrotzsch N23, and
two-lane stresses is still running as of that block.  Glued chains already
reported:

```text
3900 cuts, 0 atoms.
```
