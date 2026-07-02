# UNIT-FLAT5 Side-Door Packing Target

Date: 2026-07-02

## Local Shape

A selected UNIT-FLAT5 atom has two counted unique length-5 rows

```text
P_a = (a, x_1, x_2, x_3, t),
P_b = (b, x_1, x_2, x_3, t),
```

with bad edges

```text
at, bt in M,
```

and common blue tail

```text
x_1-x_2-x_3-t.
```

The row-union set is

```text
U = {a,b,x_1,x_2,x_3,t}.
```

The exact local numbers are:

```text
D_Q(U)=9,
sigma(U)=2,
pre_Q(U)=1,
delta_M(U)=empty.
```

There are two singleton zero-slack Flat5 rotations:

```text
S={a}: at -> ax_1,
S={b}: bt -> bx_1.
```

Each has:

```text
sigma(S)=0,
DeltaGamma(S)=0,
bank=1.
```

This local shape is not enough for UNIT-PACK.

## Guardrail: Fake Fan

The t=2 shared-path fan has the same local atom:

```text
P_0=(0,2,3,4,5),
P_1=(1,2,3,4,5),
M={(0,5),(1,5)}.
```

It fails UNIT-PACK:

```text
N=8,
m=2,
eta=14/25,
#atoms=1.
```

The failure is already forbidden by maximum-cut optimality:

```text
maxcut_bad_edges=1,
intended_bad_edges=2,
min_sigma=-1.
```

Concrete negative-slack side-door switches include:

```text
W={0,1,2,6},    delta_B(W)=1, delta_M(W)=2,
W={5,7},        delta_B(W)=1, delta_M(W)=2.
```

So the fake fan is not a counterexample to UNIT-PACK under the real
hypotheses.  It is the minimal model showing what the proof must forbid.

## Good Atoms

For the N=10 census atom `I?AAD@wF_`:

```text
maxcut_bad_edges=2,
intended_bad_edges=2,
intended_is_connected_maxcut=True,
intended_is_gmin=True,
min_sigma=0.
```

For the N=15 glued local atom:

```text
maxcut_bad_edges=3,
intended_bad_edges=3,
intended_is_connected_maxcut=True,
intended_is_gmin=True,
min_sigma=0.
```

Thus the real selected atoms live exactly at maxcut zero-slack.  The fake fan
has the same local row geometry but exposes a negative side-door switch.

## Proposed Proof Atom

### UNIT-FLAT5 Side-Door Packing Lemma

Let `A` be the canonical selected family of UNIT-FLAT5 atoms produced by the
SLACK-CAGE deletion process in a connected-B maximum cut.  Then:

```text
|M| + |A| <= N^2/25.
```

Equivalently:

```text
|A| <= eta.
```

The intended proof is by contradiction.  If a selected family overpacks the
eta bank, then the selected UNIT-FLAT5 atoms contain a side-door deficient
subfan.  That subfan supplies a vertex set `W` with:

```text
delta_B(W) < delta_M(W),
```

contradicting maximum-cut optimality.

This is the exact role of the fake fan: it is the deficient subfan after
forgetting the global side-door balance.

## Exact-Testable Strengthening

For every candidate selected family `A`, build the auxiliary incidence graph:

```text
left vertices:  selected UNIT-FLAT5 atoms;
right vertices: blue side-door boundary edges that can pay the atom;
```

where a side-door pays an atom if it is the first blue boundary edge of one of
the two terminal-side sets associated to the atom.

The target Hall condition is:

```text
for every X subset A:
  |X| <= eta_X,
```

where `eta_X` is the exact maxcut side-door capacity of the union of the
terminal sides of atoms in `X`.  A failed Hall set should construct the
negative-slack switch `W` directly:

```text
delta_M(W)-delta_B(W) = |X|-eta_X > 0.
```

The N=8 fake fan realizes `|X|=1`, `eta_X=14/25` at the global scalar level
and, more sharply, a concrete integral side-door deficit:

```text
delta_M(W)-delta_B(W)=1.
```

The N=10 and N=15 true atoms are tight with no negative-slack set:

```text
min_W sigma(W)=0.
```

This is the next structural object to formalize: the selected family must be
chosen so that any failure of the global eta pack creates one of these
negative-slack side-door switches.

## Canonical Side-Door Cut Gate

I added:

```text
problems/23/writeup/_codex_slack_cage_unit_sidedoor_cut_gate.py
```

For every grouped UNIT-FLAT5 atom, it extracts the two canonical side-door
cuts.

### Same-ended atom

Rows share a terminal four-vertex path in the same orientation:

```text
(a,x1,x2,x3,t), (b,x1,x2,x3,t).
```

If the blue boundary of `U` exits at `x1` and `t`, the canonical cuts are:

```text
{a,b,x1, outside_at_x1},
{t, outside_at_t}.
```

The fake N=8 fan has exactly this shape and both cuts have slack `-1`.

### Opposite-ended atom

Rows share the four vertices in opposite orientations:

```text
(a,x1,x2,x3,b), (c,x3,x2,x1,d)
```

equivalently the private endpoints lie on opposite ends of the shared
four-path.  In that case the canonical side-door cuts are the private-end
doors:

```text
{private_endpoint, outside_door}.
```

These occur in the N=10 census with positive side slack `(1,1)`.

## Exact Results

Generated intended cuts:

```text
fan, max_t=8, intended:
  atoms=1
  neg_side=1
  hist={(-1,-1):1}

theta, max_t=8, intended:
  atoms=84
  bad_shape=83
  neg_side=83
  hist includes large negative side-door slacks
```

True `gmins` generated cuts:

```text
theta, max_t=12, gmins:
  atoms=4
  bad_shape=0
  neg_side=0
  hist={(0,0):2, (2,2):2}
```

Full census:

```text
N=10 gmins:
  atoms=6
  bad_shape=0
  neg_side=0
  hist={(0,0):2, (1,1):2, (2,2):2}

N=11 gmins:
  atoms=20
  bad_shape=0
  neg_side=0
  hist={(0,0):2, (0,1):5, (1,1):2, (1,2):5, (2,2):2, (2,3):4}
```

Interpretation:

```text
false local Flat5 fans expose negative canonical side-door cuts;
true gmins UNIT-FLAT5 atoms have canonical side-door slack >= 0.
```

This strengthens the proof target:

```text
Overpacked selected UNIT-FLAT5 family
=> some canonical side-door Hall set has negative total slack
=> some W has delta_B(W)<delta_M(W)
=> contradiction to maximum-cut optimality.
```

## Theta-Fan Collapse Formula

The theta-family guardrail makes the side-door deficit completely explicit.
It has `k` private leaves `p_1,...,p_k`, a common endpoint `d`, and two
length-4 blue corridors from the leaf side to `d`.  In the intended cut the
bad edges are:

```text
p_i d,  i=1,...,k.
```

There is a terminal-side switch `W` consisting of all leaves and the first
corridor vertex on one side.  Its boundary counts are:

```text
delta_M(W) = k,
delta_B(W) = 2,
sigma(W) = 2-k.
```

Therefore any theta fan with `k>=3` is impossible in a maximum cut.  The
exact diagnostic:

```text
python problems/23/writeup/_codex_slack_cage_flat5_cut_obstruction.py \
  --theta-max-t 6
```

returns:

```text
theta-t2: min_sigma=0, intended_bad_edges=2, maxcut_bad_edges=2
theta-t3: min_sigma=-1, intended_bad_edges=3, maxcut_bad_edges=2
theta-t4: min_sigma=-2, intended_bad_edges=4, maxcut_bad_edges=2
theta-t5: min_sigma=-3, intended_bad_edges=5, maxcut_bad_edges=2
theta-t6: min_sigma=-4, intended_bad_edges=6, maxcut_bad_edges=2
```

So the two-leaf UNIT atom is the unique maxcut-tight residue of this fan
shape.  This suggests the proof of UNIT-PACK should first reduce any
overpacked selected UNIT family to a blue-closed theta fan with at least
three leaves; the displayed switch then contradicts maximum-cut optimality.
