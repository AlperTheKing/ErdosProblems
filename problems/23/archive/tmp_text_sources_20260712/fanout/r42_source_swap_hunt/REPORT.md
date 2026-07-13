# R42 source-swap active-pin hunt

## Verdict

`BOUNDED_NO_GRAPH_HIT`.  This is an exact finite-family search, not a proof of
`NoPositiveDefectSourceSwapRotor` outside the generated family.

Manifest canonical SHA-256:

```text
c15f16a047885e61675b4797713f9a96af68d91ddb47f62bab9b8f2a0a4842f5
```

## Exact spaces

The abstract phase exhausts the four one-component physical-key systems with
four usable turnover keys and collision demand in `5,6,7,8`.  Every system has
an exact two-state source swap, eight raw turnover keys, four half-zero
reservations, positive defect, and all usable keys consumed by every optimal
matching.  This is an abstract matching result only, never a graph hit.

The graph phase exhausts all 16 subsets of the four active pins
`{am,bm,av,bv}`.  Each member has the source-swap core

```text
Q_m = a-x-m-y-b,  Q_v = a-x-v-y-b,  P = c-m-d-v-e,
```

plus four private C5 background rows that select the pin interiors.  All
arithmetic is integer/set arithmetic.  Maximum cut uses deterministic integer
bucket elimination; shortest-row families are reconstructed by BFS plus DFS.
The eliminator independently agrees with fixed-vertex-zero brute force on all
1,024 simple graphs on five vertices.

| graph gate | count |
|---|---:|
| triangle-free, displayed maximum cut, but blue-disconnected | 15 |
| fully evaluated connected cage | 1 |
| hit SCCs | 0 |

The connected mask is `15`: it has 29 vertices, 40 total edges (34 blue,
6 bad), and exact `MaxCut=34`, equal to the displayed cut.  Its complete
anchored shortest-row family sizes are `(8,3,1,1,1,1)`, so all 24 row tuples
are evaluated.

## Strongest bounded invariant

Every structurally valid member of this 16-mask active-pin family has minimum
canonical production collision defect zero.  In the sole connected member,
all 24 tuples are defect-minimal with defect zero; the positive-defect SCC
domain is empty.

That cage still realizes two genuine support-constant inverse source swaps.
For each direction the gate confirms: unique old middle edges, exactly eight
raw new ordered FreeHalf keys, exactly four scoped half-zero reservations, and
four usable half-one keys.  It rejects both transitions because all four usable
keys are `UNUSED_ELIGIBLE`, and there are 32 unused production common-blue
probe keys.  Thus `productionExposure=36` in each direction.

The generator uses the current P1/P2/P3/strict-P4/P5 production relation,
exclusive common-blue terminal reservations, and BaseKeyComponentCoherent
matching.  Input hashes for those imported production modules are pinned in
the manifest.

## Replay

```powershell
python -m py_compile tmp/fanout/r42_source_swap_hunt/source_swap_hunt.py tmp/fanout/r42_source_swap_hunt/verify_manifest.py
python tmp/fanout/r42_source_swap_hunt/source_swap_hunt.py --workers 1
python tmp/fanout/r42_source_swap_hunt/verify_manifest.py
```
