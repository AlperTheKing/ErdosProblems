# R41 exact real-cage square-rotor realization gate

## Verdict

The strict R38 multiplicity-saturated two-state square rotor is excluded.
The bounded real construction is a 33-vertex triangle-free cage with connected
blue graph, nine anchored bad atoms, and an exact maximum cut of 38.  It
contains the square `x-m0-y-m1-x`, the two producer rows

```text
a-x-m0-y-b
a-x-m1-y-b
```

and anchored background rows giving `n(m_i,z)>=2` for every retained
`z in {a,x,y,b}` and `r(m_i)>=2` whenever `m_i` is the outgoing middle.

The complete shortest-row family sizes are

```text
(9,2,1,1,2,2,1,1,2)
```

so all 144 row tuples were enumerated.  For every tuple the production
P1/P3/common-blue/strict-P4/P5 coherent collision matching was solved exactly.
Every tuple has defect zero.  There are 32 multiplicity-saturated producer
swaps and 16 inverse state pairs, but none is an inverse active rotor.

## Exact obstruction

Let a selected shortest row `Q` contain the square edge `m-x`.  If
`n_omega(m,x)>=2`, another selected row also contains `m,x`.  Since `m-x` is
blue and the rows are shortest, the pair is consecutive in that other row.
After replacing `Q`, the edge `m-x` therefore remains in selected support and
cannot be active.  The same argument applies to `m-y`.

Thus the multiplicity conditions required to suppress `NewFree` simultaneously
destroy the two active edges needed for the inverse middle swap.  The exact
enumeration checks this on all 32 saturated transitions with zero failures.

## Singleton cut-tight prune

For every nonempty all-weak attachment product `X x Y`, maximum-cut
nonnegativity and `sigma({x,y})=sigma({x})+sigma({y})<=1` imply that all
singletons in one whole class `X` or `Y` have loss zero.  The gate enforces
this necessary condition.

In the saturated real cage, all 32 saturated states have empty attachment
classes because all four square edges remain selected support.  Hence there
are zero states combining multiplicity saturation with a singleton cut-tight
attachment class.  Saturation is maxcut-realizable; saturation plus the active
all-weak rotor geometry is not.

## Replay

```powershell
python tmp/fanout/r41_rotor_realization/search_rotor_realization.py
python tmp/fanout/r41_rotor_realization/verify_manifest.py
python -m py_compile tmp/fanout/r41_rotor_realization/*.py
```
