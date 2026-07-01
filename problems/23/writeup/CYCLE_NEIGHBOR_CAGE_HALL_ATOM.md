# Cycle-Neighbor CAGE Hall Atom

Date: 2026-07-01.

## Statement To Gate

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

## Gates Run

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

## Proof Burden

The desired proof should show that every Hall-deficient set `Y` would induce a
neutral connected terminal-shadow switch with negative square-length
variation, contradicting gamma-minimality. The promising geometric point is
that each atom carries two closed odd-cycle neighbor pairs, so a deficient set
has to trap both local cycle exits around every overlap point.

This is not yet a proof. It is a concrete, exact-testable Hall formulation of
ROWSUM-O that has survived the current coefficient-free guardrails.
