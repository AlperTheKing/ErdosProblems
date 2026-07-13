# Label-fiber matroid intersection and rotor conservation

## Verdict

The physical-half problem is not one matroid or one gammoid.  The production
base-component coherence law makes it a finite union of matroid-intersection
fibers, one fiber for each choice of a component label on every physical base.
Inside a fiber the problem is ordinary bipartite matching; changing fibers is
an integral disjunction and can evict a carried match.

This gives an exact finite primal/dual gate and an exact CDC-style cycle
identity.  It does not prove that any production state passes the gate, and it
does not construct the missing graph-derived FullBank provider.

## The theorem

**Theorem (state-indexed label-fiber intersection and exact rotor
conservation).**  Let `S,O,B,C` be finite sets, let `C` be nonempty, and put
`H={0,1}`.  For every state `s in S`, suppose we are given

```text
O_s subset O,                         finite obligations,
kappa_s : O_s -> C,                  destination component,
R_s subset O_s x B x H.              realized physical-half relation.
```

The physical key is `(b,h) in B x H`; the state occurs only in `R_s`.  A
coherent partial assignment at `s` consists of `D subset O_s` and an injection
`f:D -> B x H` such that `R_s(d,f(d))` and

```text
f(d).base = f(e).base  implies  kappa_s(d)=kappa_s(e).       (Coh)
```

For `lambda:B -> C`, define the finite edge set

```text
E(s,lambda) = {(d,b,h) : d in O_s, R_s(d,b,h),
                           kappa_s(d)=lambda(b)}.
```

On `E(s,lambda)`, let `M_O` be the partition matroid with capacity one on
each obligation fiber, and let `M_H` be the partition matroid with capacity
one on each physical-half fiber `(b,h)`.  Write

```text
nu(s,lambda) = max {|I| : I is independent in both M_O and M_H},
rho(s)       = max_lambda nu(s,lambda),
Delta(s)     = |O_s| - rho(s).
```

Then:

1. `rho(s)` is exactly the maximum size of a coherent partial assignment.
   In particular, a total physical-half provider exists at `s` iff
   `rho(s)=|O_s|`.

2. If `r_O,r_H` are the two matroid rank functions, Edmonds' finite
   matroid-intersection min-max theorem gives

```text
nu(s,lambda)
  = min_{X subset E(s,lambda)}
      (r_O(X) + r_H(E(s,lambda) \ X)).                       (MI)
```

   Consequently the following is an exact finite gate, not an unlabelled
   scalar Hall test:

```text
Provider(s) iff
  exists lambda:B->C, forall X subset E(s,lambda),
    |O_s| <= r_O(X) + r_H(E(s,lambda) \ X).                  (GATE)
```

   A passing certificate is `(lambda,I)` with `|I|=|O_s|`.  A failing
   certificate supplies, for every `lambda`, one set `X_lambda` whose right
   side in `(MI)` is less than `|O_s|`.  Both certificates are finite and use
   exact integers.

3. Let `s,t in S`, let `(M_s,f_s)` and `(M_t,f_t)` be maximum coherent
   assignments, and let

```text
C_st = {d in M_s intersect O_t :
          R_t(d,f_s(d)) and kappa_t(d)=kappa_s(d)}
```

   be the physically and component-persistent carry set.  Define

```text
B = |O_t \ O_s|,
U = |(O_s \ O_t) \ M_s|,
L = |(M_s intersect O_t) \ C_st|,
A = |M_t| - |C_st|.
```

   The carry assignment is coherent at `t`, so `|C_st|<=|M_t|`; hence `A`
   is a natural number.  The exact signed identity is

```text
Delta(t)-Delta(s) = B + L - U - A.                           (DD)
```

   Thus on a directed state cycle `s_0,...,s_n=s_0`, the edge charge
   `g_i=B_i+L_i-U_i-A_i` is the coboundary `d Delta`.  After reduction in
   every finite field `F_p`, its pairing with the fundamental cycle is zero:

```text
sum_i g_i = 0 in Z, and therefore in every F_p.               (CDC)
```

   If all rotor states have equal positive defect, then each checked edge has
   `g_i=0`, equivalently `B_i+L_i=U_i+A_i`.  This is exactly the content of
   `CheckedDetourTransportLedger.defect_delta` and
   `CheckedBalancedDeficiencyRotor.ledger_balanced`.

### Proof

Fix `s` and `lambda`.  A common independent set in `M_O intersect M_H`
uses each obligation and each physical half at most once, so it is a partial
injection.  Every edge at base `b` has obligation label `lambda(b)`, which
proves `(Coh)`.

Conversely, let `(D,f)` be coherent.  For every used base `b`, `(Coh)` makes
the component of all obligations assigned to `b` unique; assign that value to
`lambda(b)`.  Give unused bases any fixed element of the nonempty set `C`.
The triples `(d,f(d))` then form a common independent set in
`E(s,lambda)`.  These two constructions preserve cardinality, proving part 1.
Part 2 is the finite matroid-intersection min-max theorem applied to the two
explicit partition matroids.

For part 3, put `DminusM=M_s intersect (O_s \ O_t)`.  The relevant sets
partition exactly as follows:

```text
|O_t|-|O_s| = B - |DminusM| - U,
|M_s|       = |C_st| + |DminusM| + L,
|M_t|       = |C_st| + A.
```

Subtracting matched cardinality from obligation cardinality cancels
`|DminusM|` and gives `(DD)`.  Summing `(DD)` around a cycle telescopes,
which proves `(CDC)`.

## Why this cannot be collapsed to one matroid or submodular flow

Take one base `b` with the two literal halves `(b,0),(b,1)`.  Let
`x1,x2` have component `A`, let `y` have component `B`, and make every
obligation realized at both halves.  The coherent independent sets include

```text
I={x1,x2},    J={y},    |I|>|J|,
```

but neither `J union {x1}` nor `J union {x2}` is coherent.  This violates the
matroid exchange axiom, so the global system is not a matroid and hence not a
gammoid.  Its exact rank also violates submodularity:

```text
r({x1,y}) + r({x2,y}) = 1+1
  < 2+1 = r({x1,x2,y}) + r({y}).
```

Equivalently, the natural virtual-key base capacity
`q_b(X)=max_c |X intersect ({b}x{c}xH)|` is not submodular.  The outer
`max_lambda` in the theorem is therefore essential.

This example also fixes the interpretation of `A_reopt`.  Carry only `y` at
`(b,0)`.  The global optimum has size two, using `x1,x2`, so
`A_reopt=2-1=1`; nevertheless no size-two coherent matching contains the
carry `y`.  Thus `A_reopt` is a rank difference, not one unit of augmenting
flow that extends the carried physical assignment.  Any flow model that treats
it as such is unsound.

## Exact neutral-rotor counterexample

The conservation statement itself does not exclude a balanced rotor.  Here
is the smallest state-dependent abstract witness.

```text
S={0,1}, C={c}, B={b0,b1}.
O_0={u0,v0}; only physical key p0=(b0,0) is realized for both.
O_1={u1,v1}; only physical key p1=(b1,0) is realized for both.
```

At state `i`, match `ui -> pi` and leave `vi` unmatched.  The unique label
fiber has matroid-intersection rank one, so both defects are exactly one.  The
obligation sets are disjoint, and the physical key available in one state is
not realized in the other.  Therefore both transitions have empty carry and

```text
edge    B  U  L  A    Delta(new)-Delta(old)    B+L-U-A
0->1    2  1  0  1             0                  0
1->0    2  1  0  1             0                  0
```

Thus the exact `(2,1,0,1)` neutral ledger is simultaneously compatible with
state-dependent physical keys, per-state matroid intersection, `(DD)`, and
the finite-field cycle law `(CDC)`, while neither state has a total provider.
This is an exact abstract counterexample to deriving provider existence from
those mechanisms alone.  It is not a graph-derived `CheckedBalancedDeficiencyRotor`:
it does not claim the triangle-free graph, complete rows, owner profile, or
circuit fields required by production M3.

## Production specialization and provider status

For the compiled collision adapter, instantiate

```text
B       = CollisionDefectGraphAdapter.SourceBase G,
O_s     = obligations G c omega,
kappa_s = CollisionObligation.component,
R_s     = sourceRealized G c relations omega.
```

This explicitly handles dependent `FreeHalf G omega` types correctly.  A
`FreeHalf` value is never compared across states.  Its proof fields are
forgotten, the canonical physical key is `sourceKey s = (base,half)`, and the
state-dependent freeness, reservation, and source-family facts remain inside
`R_s`.  The carry set rechecks `R_t` on the same canonical physical key, just
as `CheckedDetourTransportLedger.SourcePersists` does.

**Missing-provider answer: no.**  The theorem constructs a
`TotalCoherentAssignment` only after a concrete production relation has been
supplied and `(GATE)` has passed.  Nothing here proves that some graph-derived
row state passes it.  It also supplies no map from corrected common-blue
terminals to `TypedFullBankSources.CapSource`, no legal off-support
edge-to-token incidence, and no checked global no-double-spend package.
Therefore it does not construct `CheckedFullBankMicroFlow`,
`FullBankGlobalPackage.Checked`, or the missing real graph-derived FullBank
provider identified in `R29_TRANSFER_RECONCILIATION.md`.

The exact usable finite gate is to enumerate labels only on contested bases
(bases seen by obligations from at least two components), run partition-
matroid intersection in every fiber, and emit either one total `(lambda,I)`
or one dual `X_lambda` for every fiber.  To exclude a production rotor rather
than merely audit it, a new graph lemma must create nonzero cycle curvature,
for example typed source provenance or incidence that cannot return to its
initial value.  The present `defect_delta` charge is an exact coboundary, so a
balanced rotor annihilates it identically.
