# Ball-2 CAGE Hall Atom

Date: 2026-07-01.

## Motivation

The smaller cycle-neighbor Hall atom is false.  The exact falsifier

```text
graph6 = H?AFBo]
side = 000111100
f = (1,7)
Y = {1,2,3,4,6,7,8}
cycle-neighbor Hall demand = 8 > 7 = |Y|
ROWSUM-O value for f = 8 < N = 9
```

shows that routing only through the four closed-cycle neighbor ports is too
local.  A second test also kills the variant allowing all graph-neighbors plus
the overlap center:

```text
graph6 = I?AAD@wF_
f = (3,9)
Y = {1,2,3,4,5,6,8,9}
graph-neighbor-plus-center demand = 9 > 8 = |Y|
ROWSUM-O value for f = 9 < N = 10
```

In both cases the missing capacity lies in side-door vertices at graph distance
two from the active row corridor.

## Candidate

Fix a bad edge `f`.  For every bad edge `g`, every shortest `f`-row `P`,
every shortest `g`-row `Q`, and every shared vertex `x in P cap Q`, form one
atom

```text
(g, P, Q, x)
```

with mass

```text
1 / (|cyc[f]| |cyc[g]|).
```

The allowed sink set is the full-graph radius-2 ball around `x`:

```text
B_2^G(x) = {v : dist_G(v,x) <= 2}.
```

Each vertex has capacity `1`.  The exact Hall condition is:

```text
for every Y subset V,
  total mass of atoms with B_2^G(x) subset Y <= |Y|.
```

If this Hall condition holds for every bad edge `f`, then ROWSUM-O follows,
because the total mass of all atoms for fixed `f` is still exactly

```text
sum_g <p_f,p_g> = (O 1)_f.
```

## Gate

Implemented as an explicit port mode:

```text
python problems\23\writeup\_gpt_cycle_neighbor_cage_gate.py ... --ports ball2
```

The checker uses exact `Fraction` max-flow over compressed radius-2 ball masks.
On failure it returns a concrete Hall set `Y`.

## Current Exact Gates

Regression:

```text
--ports neighbors on H?AFBo] fails as expected.
--ports ball2 on H?AFBo] passes.
--ports ball2 on I?AAD@wF_ passes.
```

Selected gamma-min census:

```text
N=8  full selected census: PASS
N=9  full selected census: PASS
N=10 full selected census: PASS, seen=9832
N=11 selected sample limit 5000: PASS, seen=5001
```

All gamma-min sample:

```text
N=10 all-gmins limit 1500: PASS, checked_cuts=1755
```

Nonuniform C5 guardrail `[k+1,k,k+1,k,k+1]`, side `{0,1,3}|{2,4}`:

```text
k=2  N=13 PASS
k=3  N=18 PASS
k=4  N=23 PASS
k=5  N=28 PASS
k=6  N=33 PASS
k=7  N=38 PASS
k=8  N=43 PASS
k=9  N=48 stopped before completion due raw row enumeration cost
```

## Proof Burden

A Hall-deficient set `Y` for this atom is stronger than for the dead
cycle-neighbor atom: every contributing overlap point has its entire radius-2
graph ball contained in `Y`.  Thus the complement `V \ Y` is at graph distance
at least `3` from every contributing overlap point.

The intended proof shape is:

```text
Hall-deficient Y
=> a radius-2 closed corridor shadow with too much trapped overlap mass
=> a neutral connected terminal-shadow switch whose replacement square length
   is lower than the removed square length
=> contradiction to gamma-minimality.
```

This is still only a candidate.  It is broader than the false local-neighbor
atom and has survived the current coefficient-free guardrails, but it needs
Claude's independent exact gate and a genuine geometric proof.
