# Cycle-neighbor CAGE atom

Status: false as a ROWSUM certificate.  Kept as a diagnostic of why the
purely local closed-cycle-neighbor routing is too narrow.

Exact falsifier:

```text
graph6 = H?AFBo]
side = 000111100
f = (1,7)
Y = {1,2,3,4,6,7,8}
Hall demand = 8
|Y| = 7
ROWSUM-O value for f = 8 < N = 9
```

Thus the atom can fail even when ROWSUM has slack.  The failure is not repaired
by also allowing the atom to route to the overlap vertex `x`, since all trapped
atom centers already lie in `Y`.

## Atom

Fix a connected-`B` gamma-minimal maximum-cut configuration and one bad edge
`f`.  For a shortest `f`-row `P`, a bad edge `g`, a shortest `g`-row `Q`, and
a shared vertex `x in V(P) cap V(Q)`, create one atom with mass

```text
1 / (|cyc[f]| |cyc[g]|).
```

Let `N_P(x)` be the two neighbors of `x` on the closed odd cycle `P + f`,
and let `N_Q(x)` be the two neighbors of `x` on the closed odd cycle `Q + g`.
The atom may be routed only to

```text
N_P(x) union N_Q(x).
```

The proposed sufficient ROWSUM certificate is the fractional Hall condition

```text
for every Y subset V,
  total mass of atoms whose allowed-neighbor set is contained in Y <= |Y|.
```

Equivalently, the atoms can be fractionally packed into vertex capacities `1`.

## Why it implies ROWSUM-O

For fixed `f`, the total atom mass is

```text
sum_g E_{P in cyc[f], Q in cyc[g]} |V(P) cap V(Q)|
= sum_g <p_f,p_g>
= (O 1)_f.
```

If the Hall condition holds, total routable mass is at most total vertex
capacity `N`, hence `(O 1)_f <= N`.

The atom is coefficient-free: it uses neither fixed Schur-current constants nor
finite-depth inverse truncations, so it survives the known scale obstruction in
principle.  The proof obligation is purely geometric:

```text
triangle-free + gamma-minimal max-cut
=> the cycle-neighbor Hall condition above.
```

## Exact gate

Implemented in:

```text
problems/23/writeup/_gpt_cycle_neighbor_cage_gate.py
```

The gate compresses atoms by their allowed-neighbor masks and checks Hall either
by subset enumeration or exact `Fraction` max-flow.

## Current checks and correction

The early positive checks below are superseded.  The checker originally failed
to mark failure dictionaries with `fail=True`, so census mode ignored a
deficit.  The reporter is now fixed in `_gpt_cycle_neighbor_cage_gate.py`.

Small exact checks from the progress log:

```text
N7,N8,N9 all gamma-min cuts: PASS
N10 first 2000 graphs, all gamma-min cuts: PASS
Named hard cases I?BD@g]Qo, I?ABCc]}?, J???E?pNu?: PASS
```

Local guardrail rerun:

```text
python problems/23/writeup/_gpt_cycle_neighbor_cage_gate.py --g6 DUW --blow 2 --method flow
python problems/23/writeup/_gpt_cycle_neighbor_cage_gate.py --g6 DUW --blow 3 --method flow
python problems/23/writeup/_gpt_cycle_neighbor_cage_gate.py --g6 DUW --blow 4 --method flow
```

All equal `C5[t]` checks passed through `t=4`.

Nonuniform `C5[k+1,k,k+1,k,k+1]`, with the gamma-min cut leaving class `0-1`
bad, passed:

```text
k=2, N=13, checked=6, fail=None
k=3, N=18, checked=12, fail=None
k=5, N=28, checked=30, fail=None
```

The `k=8, N=43` direct uncompressed flow run was stopped after about 120s with
no output; this is a performance limit, not a mathematical failure.

## Lesson

For a fixed `Y`, define

```text
a_f^Y(x) =
  Pr_{P in cyc[f]}[x in P and N_P(x) subset Y],

S^Y(x) =
  sum_g Pr_{Q in cyc[g]}[x in Q and N_Q(x) subset Y],
```

where `N_P(x)` means the two neighbors of `x` on the closed odd cycle `P+f`.
Then the Hall demand for `Y` factors exactly as

```text
D_f(Y) = sum_x a_f^Y(x) S^Y(x).
```

So the proposed atom is equivalent to the masked ROWSUM family

```text
for every f and Y subset V,
  sum_x a_f^Y(x) S^Y(x) <= |Y|.
```

The falsifier shows that this masked family is stronger than ROWSUM-O.  A
future CAGE/Hall replacement needs capacity outside the four local cycle
neighbors, or a proof object that is not a direct vertex-capacity matching for
these atoms.
