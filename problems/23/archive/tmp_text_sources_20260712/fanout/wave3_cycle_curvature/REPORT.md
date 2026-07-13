# Wave 3 cycle curvature: canonical source provenance

## Verdict

The strongest canonical scalar available from the existing source interface is
a four-bit provenance weight recording which of `p1`, `p3`, `strictP4`, and
`p5` realizes each matched physical half.  It is graph-derived and is not a
function of collision defect.  Its exact transition formula, however, has a
carry-drift term plus weighted entering and leaving matching terms.  Around a
rotor the three terms telescope together.  Balancedness controls only their
unweighted cardinalities and cannot make the provenance drift nonzero.

There is therefore no source-provenance curvature theorem from M1/M2/M3 as
currently typed.  A smallest nonvacuous abstract positive-defect 2-rotor has
two obligations, one physical key, one component, and constant `p1`
provenance; every edge has zero provenance charge.  An independent eight-
vertex triangle-free max-cut graph realizes a literal inverse live-detour
2-cycle with complete shortest-row databases, showing that endpoint
orientation and shortest-row parity do not supply a sign from the local graph
facts either.

This is not a counterexample to the full production M3 structure.  It is an
exact counterexample to the proposed observable and identifies the missing
cross-transition fields needed before any holonomy argument can force the
provider.

## 1. Exact observable

Fix production data `G,c,bads,R`, a row state `omega`, an ambient obligation
`d`, and a physical key `k : SourceBase G x Fin 2`.  For

```text
J = {p1, p3, strictP4, p5}
```

define `Avail_j(omega,d,k)` to mean that there are

```text
hd : d in obligations G c omega
s  : FreeHalf G omega
```

such that

```text
sourceKey s = k,
not ScopedReserved G c omega s,
R.j omega ((obligationEquivReal G c omega) <d,hd>) s.
```

The proof `hd` is immaterial by proof irrelevance.  Define the canonical
provenance mask

```text
pi(omega,d,k)
  = 1 * 1[Avail_p1]
  + 2 * 1[Avail_p3]
  + 4 * 1[Avail_strictP4]
  + 8 * 1[Avail_p5]                              (1)
```

in `Nat`.  This records all available families rather than choosing an
arbitrary priority when several families realize the same key.  If
`sourceRealized G c R omega d k`, then `1 <= pi(omega,d,k) <= 15`.

For a production trace state `S`, use its payload matching `M_S = S.matching`
and put

```text
Phi(S) = sum over d in M_S.matched of
           pi(S.omega, d, M_S.assign(d)).          (2)
```

`Phi` is not defect in disguise.  With two obligations and one physical key,
both a `p1`-only realization and a `p5`-only realization have optimum size one
and defect one, while (2) is respectively one and eight.

## 2. Exact transition identity

For two trace states `S,T`, write `k_S(d)` and `k_T(d)` for their assigned
physical keys where defined, and define the literal same-key overlap

```text
C_ST = {d : d in M_S.matched and d in M_T.matched
              and k_S(d) = k_T(d)}.
```

Set

```text
P_ST = sum[d in C_ST]
         (pi(T.omega,d,k_S(d)) - pi(S.omega,d,k_S(d))),

N_ST = sum[d in M_T.matched \ C_ST] pi(T.omega,d,k_T(d)),
O_ST = sum[d in M_S.matched \ C_ST] pi(S.omega,d,k_S(d)).
```

The first sum is in `Int`.  Partitioning each matched set by `C_ST` gives the
exact identity

```text
Phi(T) - Phi(S) = P_ST + N_ST - O_ST.              (3)
```

Thus, on `S_0 -> ... -> S_r = S_0`,

```text
0 = sum_i (P_i + N_i - O_i),
H_prov := sum_i P_i = sum_i (O_i - N_i).           (4)
```

The carry provenance can have holonomy only by being compensated by weighted
matching turnover.  The R42 identity knows only

```text
B + L - U - A_reopt = defect(new) - defect(old),
```

so even `B+L=U+A_reopt` gives no relation between the weighted terms in (4).
In particular, replacing every nonzero mask by cardinality one recovers only
the already-known matching bookkeeping; retaining the mask leaves uncontrolled
turnover rather than producing curvature.

There is also a typing obstruction to identifying `C_ST` with M2's `carry`.
M2 proves that `carry` is a valid matching at the new state, but it does not
prove `carry` is contained in `newOptimal.matched`.  M3 does not equate
`ledger(i).newOptimal` with `ledger(succ i).oldOptimal`, and neither is equated
with the corresponding M1 payload matching.  Hence the serialized ledgers do
not compose physical matched tokens around the rotor.

## 3. Smallest exact abstract counterexample

Take

```text
states       S = {0,1}, with edges 0->1 and 1->0;
obligations  O_0 = O_1 = {u,v};
components   kappa(u) = kappa(v) = c;
physical     one key p;
realization  p realizes both u and v, only through p1, in both states.
```

At each state choose the maximum coherent matching `u -> p` and leave `v`
unmatched.  The unique label fiber has rank one, so both defects are exactly
one.  For either transition the checked ledger sets are

```text
persistObligation = {u,v},   persistSource = {u},
carry = {u},                 born = empty,
deadUnmatched = empty,       brokenLive = empty,
reoptimizedGain = 1 - 1 = 0.
```

Consequently `(B,U,L,A)=(0,0,0,0)` and the edge is balanced.  Also

```text
pi(i,u,p)=1,  Phi(i)=1,  P_i=N_i=O_i=0
```

on both directed edges.  The positive-defect rotor has zero provenance
holonomy.

This example is minimal among nonvacuous provenance examples: a nontrivial
rotor needs at least two states, positive defect needs an unmatched
obligation, nonzero provenance needs a matched obligation and a realized key,
so at least two obligations and one physical key are necessary.  The example
attains all three lower bounds.  It also respects physical-half injectivity and
base-component coherence; the failure is not caused by mixing label fibers.

## 4. Exact graph guardrail for row orientation

The local graph facts themselves permit an inverse live-detour 2-cycle.  Let
the vertices be `0,...,7`, with cut shores

```text
L = {0,2,4,5},       R = {1,3,6,7}.
```

Use blue edges

```text
01, 12, 15, 23, 26, 34, 35, 57
```

and bad edges `04,67`.  The graph is triangle-free.  The displayed cut has
size eight and is maximum: the two `04` rows give two 5-cycles whose common
edge set is `{01,34,04}`, while the two `67` rows give two 5-cycles whose
common edge set is `{26,57,67}`; these sets are disjoint, so every odd-cycle
edge transversal, hence every set of uncut edges, has size at least two.

The complete blue length-four row lists are exactly

```text
04 : [0,1,2,3,4], [0,1,5,3,4]
67 : [6,2,1,5,7], [6,2,3,5,7].
```

Fix the selected `67` row as `[6,2,3,5,7]`.  Switching the selected `04` row
gives

```text
state 0 support = {01,12,23,26,34,35,57}, active = {15};
state 1 support = {01,15,23,26,34,35,57}, active = {12}.
```

Thus `0->1` is the literal detour

```text
[0,1,2,3,4] -> [0,1,5,3,4]
```

with active-left edge `15` and already-supported right edge `53`; the reverse
transition has active-left edge `12` and already-supported right edge `23`.
Both row orientations have the same endpoints.  Rooting at vertex zero also
gives equal blue distances `dist(0,2)=dist(0,5)=2`.  Hence endpoint
orientation, middle-position parity, and rooted middle distance all have zero
cycle charge here (or opposite charges on the two directed edges).

An exhaustive check of all `2^8` vertex cuts gives maximum cut eight, and a
simple-path enumeration gives exactly the four rows displayed above.  This
graph does not satisfy the M3 square-window/circuit/profile fields.  Its role
is narrower and exact: triangle-freeness, maximum cut, complete shortest rows,
and the local rooted live-detour facts alone do not orient a rotor edge.  It
can be combined with the abstract matching layer in Section 3 because the
current interfaces contain no root/profile-to-provenance transport law.

## 5. Why M1/M2/M3 cannot repair (4)

The needed coupling data are absent at four separate boundaries.

1. `sourceRealized` existentially forgets the `FreeHalf` witness and which
   source-family disjunct realized it.  M2 carries only `(base,half)`.
2. Adjacent M2 ledgers have no equality connecting their chosen optimal
   matchings, so a token cannot be parallel-transported through the cycle.
3. `CheckedTwoEdgeDetour` does not connect the unmatched root or cursor to
   `v,m,x,y`; M3's profile likewise does not assert that the next owner is the
   current partner.  Positive defect therefore supplies no sign for `P_ST`.
4. The four provenance families are not `TypedFullBankSources.CapSource`
   constructors, and corrected common-blue/c5Base sources used by the R29
   repair are absent from `NoCommonBlueSourceRelations`.  There is no typed
   component, legal edge-to-token incidence, capacity, or no-double-spend map
   to sum around the rotor.

Any integer/rational function of a serialized state has exact differential
and zero cycle sum by definition.  Genuine curvature requires a bundle of
chosen typed source witnesses plus a composable transport map, not another
state scalar.

## 6. Provider consequence of a successful refinement

A provider-producing version would need to add, for every matched edge, a
chosen witness carrying

```text
(FreeHalf, physical key, source-family/CapSource tag, component,
 legal bank incidence)
```

and require successive ledgers to use the same endpoint matching.  A useful
edge theorem would then say that, under positive defect and no augmentation,
parallel transport strictly changes a well-ordered typed token (or has a
strictly positive rational charge), while rematching preserves total typed
weight.  Its nonzero cycle sum would contradict return to the initial typed
matching.  Therefore some transition must expose a fresh legal physical half;
the rooted alternating path would augment the coherent matching.  Iterating
this finite augmentation reduces defect to zero and yields the
`TotalCoherentAssignment` collision provider.

To force the missing FullBank provider rather than only the collision
assignment, the chosen-witness type must include the corrected common-blue
terminal and a map to `CapSource.c5Base` (as well as the other bank kinds),
with component confinement and injectivity on `(component,source)`.  The same
assignment would then serialize `TypedGlobalLedgerData`; physical-key
injectivity would supply no double spend, while the typed incidence and capQ
fields would discharge the `CheckedFullBankMicroFlow`/global-package checks.
Without that adapter, excluding a rotor can force existence of an augmenting
source but cannot construct the typed FullBank package identified as missing
in `R29_TRANSFER_RECONCILIATION.md`.

## Conclusion

The canonical provenance mask (1) is a genuine graph/source observable, but
its exact identity is (3), not a one-signed rotor charge.  The minimal
two-obligation example kills universal positive holonomy, and the eight-
vertex inverse detour kills a sign coming only from row orientation or rooted
shortest-row parity.  The next viable invariant must first enrich M2/M3 with
composable chosen typed witnesses and root/profile coupling; no scalar on the
current serialized state can do the job.
