# R43 owner-balance turnover for a support-constant detour

Consider a genuine row replacement

```text
Q  = (a,x,m,y,b)
Q' = (a,x,v,y,b)
```

in a directed neutral cycle.  Support monotonicity forces

```text
pairCount_omega(m,x)=pairCount_omega(m,y)=1,
pairCount_omega(v,x)=pairCount_omega(v,y)=0.
```

The old active edges `vx,vy` become selected and the old selected edges
`mx,my` become active.  Assume the relevant middle is an `ActiveOwner`, so
half zero is reserved on each oriented active edge.

For an active owner `u`, define the local same-first balance

```text
B_omega(u)
  = #{unreserved FreeHalf keys with sourceX=u}
    - 2 * sum_z max(pairCount_omega(u,z)-1,0).
```

The second term is exactly the collision-half demand owned by `u`.  Sources
with first coordinate `u` are P1-compatible with every such demand.

## Exact identity

If `r_m=pairCount_omega(m,m)`, then

```text
B_omega'(m)-B_omega(m) = 6 + 2*1[r_m>=2].             (1)
```

If `r_v=pairCount_omega(v,v)`, then

```text
B_omega'(v)-B_omega(v) = -6 - 2*1[r_v>=1].            (2)
```

For each retained endpoint `z`, decreasing `pairCount(m,z)` by one either
creates two same-first halves (when the count was one) or deletes two
collision demands (when it was at least two).  This contributes `+2`
independently of the multiplicity.  The two path pairs become active and
lose one reserved half each, subtracting two in total.  The diagonal count
contributes another two exactly when `r_m>=2`.  This proves (1); (2) is the
reverse calculation.

Thus a support-constant detour is not merely a four-key source swap.  It
transfers six or eight units of literal owner Hall balance in the direction
opposite to the middle replacement.  Any zero-exposure rotor must transport
this imbalance through companion/P4/P5/common-blue eligibility to other
owners; per-state key turnover and base-component coherence alone omit this
constraint.

## Scope

This identity does not yet exclude a source-swap SCC.  An alternating
eligibility chain can, in principle, export the gained `m` capacity and import
capacity to the worsened `v` shore.  The next graph lemma must show that such
transport forces either an unused source, a diagonal co-occurrence
`pairCount(m,v)>0` and hence additional complete-row detours through `x,y`, or
a checked lower-defect tuple.

Exact replay:

```powershell
python tmp/fanout/r43_owner_turnover/check_owner_turnover.py
```
