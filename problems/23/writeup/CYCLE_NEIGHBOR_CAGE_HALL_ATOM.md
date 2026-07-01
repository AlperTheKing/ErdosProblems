# Cycle-Neighbor CAGE Hall Atom

Date: 2026-07-01.

## Verdict

False as stated. The atom is a useful diagnostic, but it is too local to prove
ROWSUM-O.

Exact falsifier:

```text
graph6 = H?AFBo]
selected gamma-min side = 000111100
bad edges = (1,7), (2,7), both length 5
f = (1,7)
Y = {1,2,3,4,6,7,8}
Hall demand into Y = 8
|Y| = 7
ROWSUM-O value for f = 8 < N = 9
```

Both subset enumeration and exact Fraction flow report the same deficit:

```text
python problems\23\writeup\_gpt_cycle_neighbor_cage_gate.py --g6 'H?AFBo]' --method enum
python problems\23\writeup\_gpt_cycle_neighbor_cage_gate.py --g6 'H?AFBo]' --method flow

=> {'fail': True, 'label': 'H?AFBo][1]', 'n': 9, 'f': (1, 7),
    'atoms': 32, 'rowsum': Fraction(8, 1), 'viol': Fraction(1, 1),
    'Y': [1, 2, 3, 4, 6, 7, 8], 'lhs': Fraction(8, 1), 'rhs': 7}
```

The original CLI failed to stop on this because failure dictionaries omitted a
`fail=True` key; that reporter bug is now fixed.

The obstruction is informative: every trapped atom center `x` is already in
`Y`, so allowing the atom to route to `x` in addition to its closed-cycle
neighbors would not repair this Hall set. The missing capacity must come from
outside the local four-neighbor port set.

## Original Statement

Fix a bad edge `f`. For every bad edge `g`, every shortest `f`-row `P`,
every shortest `g`-row `Q`, and every shared vertex `x in P cap Q`, form one
atom

```text
(g, P, Q, x)
```

with mass

```text
1 / (|cyc[f]| |cyc[g]|).
```

Let `N_P(x)` be the two cycle-neighbors of `x` on the closed odd cycle
`P + f`, and define `N_Q(x)` similarly. The atom may be routed only to

```text
N_P(x) union N_Q(x).
```

The proposed Hall condition is:

```text
for every Y subset V,
  total mass of atoms whose allowed neighbor set is contained in Y <= |Y|.
```

Equivalently, the atom hypergraph has a fractional matching into vertices of
capacity `1`.

## Why This Is Relevant

For fixed `f`, the total atom mass is exactly

```text
sum_g <p_f, p_g> = (O 1)_f.
```

Therefore, if the Hall condition holds for every `f`, all this mass can be
routed into `N` vertices of capacity `1`, proving

```text
(O 1)_f <= N.
```

Thus the atom would imply ROWSUM-O. The open part is the graph-theoretic proof
of the Hall inequality from triangle-free connected-B gamma-minimality.

## Exact Gate

Implemented in:

```text
problems/23/writeup/_gpt_cycle_neighbor_cage_gate.py
```

The checker has two exact modes:

```text
enum: enumerate all Y subsets, exact Fraction zeta transform;
flow: exact Fraction max-flow on compressed neighbor masks.
```

The flow mode also extracts a concrete Hall set `Y` from the residual min-cut
if a deficit is found.

## Gates Previously Run

These gates are superseded by the falsifier above. Earlier broad runs reported
false passes because the CLI did not recognize failure dictionaries.

Named hard case:

```text
python problems\23\writeup\_gpt_cycle_neighbor_cage_gate.py --g6 'I?BD@g]Qo' --method flow
=> {'label': 'I?BD@g]Qo[1]', 'n': 10, 'checked': 3, 'fail': None}
```

Full selected gamma-min census:

```text
python problems\23\writeup\_gpt_cycle_neighbor_cage_gate.py --census-n 10 --method flow
=> PASS census_n=10 seen=9832
```

N=11 selected gamma-min sample:

```text
python problems\23\writeup\_gpt_cycle_neighbor_cage_gate.py --census-n 11 --limit 5000 --method flow
=> PASS census_n=11 seen=5001
```

N=10 all gamma-min sample:

```text
python problems\23\writeup\_gpt_cycle_neighbor_cage_gate.py --census-n 10 --limit 1500 --all-gmins --method flow
=> PASS census_n=10 seen=1501 checked_cuts=1755
```

Equal C5 blowups:

```text
DUW[2], DUW[3], DUW[4]
=> no Hall failures; checked rows 4, 9, 16.
```

Nonuniform C5 guardrail with side `{0,1,3} | {2,4}` and sizes
`[k+1,k,k+1,k,k+1]`, using a direct quotient construction:

```text
k=2  N=13  PASS
k=3  N=18  PASS
k=4  N=23  PASS
k=5  N=28  PASS
k=6  N=33  PASS
k=7  N=38  PASS
k=8  N=43  PASS
k=9  N=48  PASS
k=10 N=53  stopped as too slow in raw quotient row enumeration
```

This includes the `N=28` and `N=33` nonuniform C5 blowups that refuted the
fixed-coefficient harvest/quantitative Schur subtree.

## Lesson

The total atom mass is still exactly `(O1)_f`, so this was a legitimate
sufficient certificate. The failure shows that a valid ROWSUM proof cannot
force all overlap mass through only the two closed-cycle neighbor pairs of the
two participating rows. Any Hall/CAGE replacement needs additional nonlocal
corridor exits or a different capacity object.
