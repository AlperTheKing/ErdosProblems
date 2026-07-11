# R43 owner-balance turnover: corrected live attachment surface

Consider the R37 attachment replacement

```text
Q  = (a,x,m,y,b)
Q' = (a,x,v,y,b).
```

Here `x` is an old active neighbour of `v`, while `y` is an old
selected-support neighbour. Therefore `xv` is genuinely new support but `vy`
is already support. This is not the two-new-edge surface considered in the
first R41 draft.

Write

```text
u = 1[pairCount(m,x)=1] + 1[pairCount(m,y)=1].
```

Both old middle pairs are positive because they occur in `Q`. Only their
unique occurrences disappear, while `xv` is the sole new support edge. Hence

```text
supportDelta = 1-u.                                      (1)
```

The exact N<=12 census checks (1) on 7,600,710 genuine detours and obtains
support deltas `-1,0,+1`. In particular support is not monotone. A
support-constant transition has `u=1`: exactly one old middle edge becomes
active and the other remains selected support.

For an active owner `z`, define the local same-first balance

```text
B_omega(z)
  = #{unreserved FreeHalf keys with sourceX=z}
    - 2 * sum_w max(pairCount_omega(z,w)-1,0).
```

The second term is exactly the collision-half demand owned by `z`; every
source counted in the first term is P1-compatible with those demands.

## Live support-constant identity

Assume the transition is support-constant. If
`r_m=pairCount_omega(m,m)`, then

```text
B_omega'(m)-B_omega(m) = 7 + 2*1[r_m>=2].              (2)
```

If `r_v=pairCount_omega(v,v)`, then

```text
B_omega'(v)-B_omega(v) = -7 - 2*1[r_v>=1].             (3)
```

For each endpoint pair `(m,a)` and `(m,b)`, decreasing a positive
multiplicity either creates two unreserved same-first halves or deletes two
collision demands, contributing `+2` independently of multiplicity. Of the
two old middle pairs, the unique one becomes active and contributes `+1`;
the repeated one loses two collision demands and contributes `+2`. The
diagonal contributes another two exactly when `r_m>=2`. This is (2).
Equation (3) is the reverse calculation: the old active pair `vx` costs one,
the already-supported pair `vy` gains two collision demands, and the two
endpoint pairs cost two each.

The Lean file
`Gamma/OwnerBalanceTurnover.lean` proves these identities for all natural
multiplicities. It also retains the older six/eight formulas, explicitly
scoped to a different two-new-active-edge detour class.

## Consequence and limitation

The live move transfers seven or nine units of owner Hall balance from the
entering owner to the disappearing middle. Around a four-state rotor these
signed transfers can cancel. Thus the identity is not a monotone potential
and does not by itself exclude the rotor.

A zero-exposure sink SCC must instead route every gained middle-owner unit
through P3/P4/P5/common-blue eligibility while absorbing the symmetric loss
at the entering owner. The remaining graph theorem must show that this
alternating transport exposes an unused same-side endpoint source, forces a
checked lower-defect tuple, or realizes an exact counterexample.

The earlier prose claim that all live neutral cycles were fully unsaturated
is withdrawn. It relied on the false premise that both entering edges were
old active edges.
