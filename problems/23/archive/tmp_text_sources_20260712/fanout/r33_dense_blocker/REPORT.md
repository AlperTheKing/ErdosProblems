# R33 dense blocker: anchored endpoint residual

## Verdict

The dense-blocker branch admits a rigorous finite residual inequality, but
`large p_W => trade` is false at the counting interface.  Row endpoint
anchoring makes every bad edge inside `W` a permanent pair lock: every
alternative row for that atom still contains its two endpoints.  These locks
must be removed from the exchange signal.

For a fixed coherent-label branch and a positive integral Hall shore `U`, the
exact P1/P3 family constructed below proves

```text
4 p_S + rho_1 + rho_3 + kappa
  >= 2 A + 4 |S| - D(U) + 1.                         (12)
```

Here `S` is the exact companion shadow, `p_S=|S intersect Q_W|`, `A` is the
number of missing owner-blocker incidences, `rho_1,rho_3` count half-zero
reservations in the displayed P1/P3 family, and `kappa` counts displayed keys
excluded by fixed base-component labels.  This is the smallest exact residual
found: every term has a literal finite witness in the operational model.

If `b_S=|S intersect M[W]|` is the number of anchoring-mandatory bad-edge
locks, (12) forces at least

```text
max(0,
  ceil((2 A + 4 |S| - D(U) + 1 - rho_1 - rho_3 - kappa)/4)
  - b_S)                                               (13)
```

additional, non-bad pair locks.  A universal trade would need a new graph
fact converting one such additional lock into an explicit
`CheckedCollisionDefectTrade`.  No such universal conversion is claimed.

There is, however, a complete one-owner corollary.  For `t` distinct bad
neighbors of an endpoint-pure owner, anchoring and triangle-freeness force a
quadratic P3 floor while collision demand is linear.  With no component-label
loss, a positive singleton defect forces

```text
p_T >= binom(t-2,2),
m-t >= ceil(binom(t-2,2)/3).                           (14)
```

Consequently the five-atoms-one-row sterile core remains impossible after
anchoring: at `t=5` it needs at least three terminal-pair locks and at least
one additional row, whereas the sterile core has none.

## Assumption ledger

Every proof and computation below uses the following assumptions explicitly.

1. `G=(V,B union M)` is a finite simple triangle-free graph; `B` and `M` are
   disjoint.
2. The displayed cut is maximum.  Hence the two-vertex switch quantity used
   by P3 satisfies `sigma({x,y}) >= 0`.
3. Each atom is one bad edge in `M`, with no duplicated/parallel bad edge.
4. A row is a simple five-vertex blue path, and RowEndpointAnchoring holds:
   the first and last row vertices are exactly that atom's bad-edge endpoints.
5. One row is selected for every atom.  Write `m=|M|` for the number of
   selected rows.
6. `pairCount(x,y)` is the number of selected rows containing both vertices.
   It is symmetric; `pairCount(x,x)` is the row count of `x`.
7. Operational collision demand is

   ```text
   c(o)=2 sum_y max(0,pairCount(o,y)-1).
   ```

   In particular, the `y=o` self-repeat is included.
8. `U` is a nonempty owner shore in one fixed base-component-label branch of
   the exact coherent source relation.  Its integral demand and reach satisfy
   `D(U)>N_lambda(U)`, hence `N_lambda(U)<=D(U)-1`.
9. `W` is disjoint from `U`.  The proof works for any such `W`; the audit uses
   the external endpoints of rows containing owners in `U`.
10. P1 and P3 have their operational meanings.  Half one is unreserved.
    `rho_1,rho_3` record every displayed half-zero key rejected by the actual
    reservation predicate; no half-zero availability is assumed silently.
11. `kappa` records every otherwise displayed key removed by an already fixed
    ordered-base component label.  The label-free version is obtained only
    when `kappa=0`.
12. P4 and P5 are ignored in the lower bound.  They may increase reach but can
    never invalidate (12).
13. HitNeed is excluded from Hall demand and remains bank-funded, matching the
    R32 collision-only objective.
14. The common-endpoint corollary additionally assumes a singleton shore and
    no label exclusion on its displayed endpoint P3 keys (`kappa_T=0`).

The computations use the pinned Gamma-minimum maximum cut, all length-five
bad-edge rows, the exact P1/P3/strict-P4/P5 relation, and exact integer
matching.  Common-blue is absent.

## Exact residual proof

Fix `U,W` as above and put

```text
C_o = {w in W : pairCount(o,w)>0},
i   = sum_(o in U) |C_o|,
A   = |U||W|-i,
S   = union_(o in U) binom(C_o,2),
Q_W = {{x,y} subset W : pairCount(x,y)>0},
p_S = |S intersect Q_W|.
```

Thus `A` is exactly the missing-incidence term in (7), while `S` is the exact
shadow before the multiplicity relaxation used there.

For every missing `(o,w)`, P1 gives `(o,w,1)` and also `(o,w,0)` unless that
half-zero key is reserved.  If `rho_1` is the number of rejected half-zero P1
keys, this gives `2A-rho_1` physical keys.

For every `{x,y} in S minus Q_W`, both vertices are companions of a common
owner, the pair is free, and maximum-cut minimality gives `sigma({x,y})>=0`.
P3 therefore gives both orientations and both halves, except for the
explicitly reserved oriented half-zero keys.  If their number is `rho_3`, this
gives

```text
4(|S|-p_S)-rho_3
```

physical keys.  The P1 and P3 families are disjoint: every P1 first coordinate
lies in `U`, every P3 first coordinate lies in `W`, and `U intersect W` is
empty.  Let `kappa` be the number of these keys whose ordered base is fixed to
a component containing no eligible owner in `U`.  The remaining keys all lie
in the labeled neighborhood of `U`.  Hence

```text
N_lambda(U)
 >= 2A-rho_1 + 4(|S|-p_S)-rho_3-kappa.
```

Using `N_lambda(U)<=D(U)-1` and rearranging proves (12).  This proof constructs
literal keys; it does not use a score proxy, a trace, or a repeated state.

### Reservation-proof form and (7)-(11)

Counting only half one gives the label-aware form

```text
2 p_S + kappa_1 >= A + 2|S| - D(U) + 1,              (15)
```

where `kappa_1` counts only excluded displayed half-one keys.  Put

```text
q = sum_(o in U,w in W) pairCount(o,w),
e = q-i.
```

Substituting `A=|U||W|-q+e` in (15) gives the exact residual

```text
q + 2 p_S + kappa_1
  >= |U||W| + 2|S| - D(U) + 1 + e.                   (16)
```

Now (8) gives `p_S<=p_W<=10m`, (9) gives the exact `e=q-i`, (10) gives
`2e<=D(U)`, and (11) gives `q<=6m`.  Therefore every positive shore satisfies

```text
|U||W| + 2|S| + e <= D(U)-1 + 26m + kappa_1.         (17)
```

Equation (17) is a scalar necessary condition; (12) is the stronger finite
certificate because it retains the actual shadow locks, reservations, and
component-label exclusions.

## What anchoring adds

For each `o in U`, let `T_o` be the set of endpoints outside `U` of selected
rows containing `o`, and put

```text
E_U = union_(o in U) binom(T_o,2).
```

RowEndpointAnchoring gives `T_o subset C_o`, so `E_U subset S`.  It also gives
the crucial negative fact:

```text
M[W] intersect S subset Q_W intersect S.              (18)
```

Indeed, if `{x,y}` is a bad edge, its selected row starts at one endpoint and
ends at the other, so `pairCount(x,y)>0`.  Changing that atom's row cannot
unlock the pair because every alternative row has the same endpoints.  Thus
the `b_S` term in (13) is compulsory anchoring load, not exchange pressure.

This is why `p_W` cannot by itself force a trade.  The useful quantity is the
additional lock count

```text
a_S = p_S - |S intersect M[W]|.
```

Even `a_S>0` only supplies a co-occurrence obstruction.  A pair `{x,y}` is
row-unlockable precisely when every currently selected row containing both
has an alternative in the same anchored atom family that omits at least one
of them.  Replacing all witness rows gives an explicit simultaneous row
change with `pairCount_eta(x,y)=0`.  It is not yet a defect trade: persistence,
the old exact matching, and a new coherent matching with fewer unmatched
obligations still must be supplied.

## Common-endpoint fan corollary

Let `v` have `t>=2` distinct bad neighbors `T=N_M(v)`.  Let `r` be the number
of selected rows containing `v`, and let the singleton owner shore be `{v}`.

First, `T` is independent in the whole graph.  Any edge between two members
of `T`, together with their bad edges to `v`, would make a triangle.

Second, a selected row containing both `v` and `d in T` must place them at
distance four on the row: their blue distance is four.  They are therefore
the two row endpoints, and anchoring plus no parallel atoms identifies the
unique atom `{v,d}`.  Thus `pairCount(v,d)=1`.  A row containing `v` locks no
pair inside `T`.

Let `s_v` be the number of distinct vertices co-occurring with `v`, including
`v`.  Since each row has five vertices,

```text
c(v)=2(5r-s_v).                                       (19)
```

The `t` endpoints, `v`, and the three internal vertices of one incident row
are distinct, so `s_v>=t+4` and

```text
c(v)<=10r-2t-8.
```

If `p_T` terminal pairs co-occur in selected rows, the other
`binom(t,2)-p_T` pairs are graph nonedges and supply all four oriented P3
halves.  With no component-label exclusion, positive singleton defect implies

```text
p_T >= binom(t,2)-floor((10r-2t-9)/4).                (20)
```

A row not containing `v` has at most three vertices of the independent set
`T` (nonconsecutive positions on a five-vertex path), so it locks at most
three terminal pairs.  Rows containing `v` lock none.  Hence

```text
p_T<=3(m-r).                                           (21)
```

Equations (20)-(21) are the general finite implication.  If the owner is
endpoint-pure, `r=t`, they reduce to (14).

Under the live collision definition, the `t=5` sterile star has collision
demand at most `32`, not `24`: the earlier quick R34 count omitted the
self-repeat `pairCount(v,v)-1`.  Its unlocked terminal endpoints nevertheless
supply `4 binom(5,2)=40` P3 keys, so the anchored exclusion remains valid and
is stronger after correcting the convention.

## Exact falsifier replay

The namespaced verifier is `r33_dense_blocker_audit.py`.  The full command is

```powershell
python tmp/fanout/r33_dense_blocker/r33_dense_blocker_audit.py --full-census --workers 61
```

CPython on Windows caps `ProcessPoolExecutor` at 61 workers.  The completed
run used exact integers and finite sets only and returned:

```text
generated connected triangle-free graphs     1,246,466
eligible pinned-cut/all-length-five graphs      992,618
row tuples checked                            40,228,399
positive-defect tuples                               297
graphs containing them                                29
elapsed seconds                                    123.722
failure-record SHA256  09eae42e67edab24b50c0340f452fb62ac3ab30df9dfde364a9620976063b9ed
audit SHA256           0fa080a96b7aafbdcf6f4a74593c2145cef3000b3c61f1fcda9831a995dd469f
```

All 297 known failures were replayed, not sampled.  Every operational key in
the displayed lower bound was checked against P1/P3, reservation status, and
the final coherent base labels.  Results:

```text
endpoint-shadow size range                         1..10
coherence exclusions kappa                            0
reach minus operational displayed floor          16..41
tuples with an endpoint lock                         285
tuples with an additional non-bad endpoint lock      133
tuples where (13) forces a non-bad shadow lock         21
forced cases having an unlockable endpoint lock        21
forced cases lacking one                                0
canonical first unlocking changes lowering defect     133
canonical first unlocking changes preserving defect     0
canonical first unlocking changes increasing defect     0
```

The order split matters.  All 32 failures at `N=10` and all 120 at `N=11`
have only anchoring-mandatory endpoint locks and no row-unlockable endpoint
lock.  At `N=12`, 133 of 145 failures have an additional unlockable endpoint
lock.  This falsifies any proof that silently treats every large `p_W` as
movable, while supporting the corrected additional-lock branch.

### One explicit finite trade payload

The verifier emits a full finite payload for graph6 `K?ABAaJFdQN_`:

```text
atoms       (0,5), (1,11), (2,6), (3,7)
old choice  [0,6,8,5]
new choice  [0,0,0,5]
changed row indices  1,2
old collision demand/matched/defect  40/37/3
old deficient shore {7,10}           32/29
new collision demand/matched/defect   0/0/0
old unmatched obligations
  (7,11,0,1), (10,11,0,0), (10,11,0,1)
old assignment SHA256
  e3024394e2cc208c2891926124fc93e5d5f237534a08abe0f157961cc47663cf
```

The payload contains all 37 old obligation/source/component records, checks
source injectivity and realization, checks ordered-base component coherence,
checks that both changed rows stay in their anchored atom families, and uses
the coherent empty matching at the zero-demand new state.  It is a finite
Python replay shaped like `CheckedCollisionDefectTrade`; it is not asserted to
be a Lean constructor or a universal trade theorem.

## The 2943 all-local shore

For the deficient hub shore `U={0,1,2}`, each hub lies in the 676 traffic
rows.  The exact endpoint audit gives

```text
r_o=676, s_o=55, c(o)=2(5*676-55)=6650
W=52
|S|=|E_U|=binom(52,2)=1326
p_S=p_W=676
anchoring-mandatory bad-edge locks=676
free endpoint pairs=650
P3 physical keys from those pairs=2600
q_UW=4056, i_UW=156, e_UW=3900
hub demand/reach/defect=19950/19925/25
```

All 650 free endpoint pairs are graph nonedges, so no half-zero reservation
query is needed for the `2600` count.  Every one of the 676 locked pairs is a
traffic bad edge, its witness is a rigid singleton row family, and
`p_W=sum_R binom(|R intersect W|,2)=676` is tight.  The known defect-lowering
2943 trade changes the 676 selector rows instead.  Thus 2943 is a concrete
warning that even maximal endpoint-pair density can be entirely rigid and
geometrically disjoint from the actual trade.

## Remaining graph fact

The dense-blocker branch is reduced to the following exact statement, which
is not proved here:

```text
At a positive-defect canonical/minimal tuple, if (12)-(13) force an
additional non-bad shadow lock, then some explicit simultaneous anchored row
change carries a CheckedCollisionDefectTrade payload: a realized new state,
the exact old coherent matching, and a new coherent matching with fewer
unmatched obligations.
```

Row-unlockability is a necessary finite precursor, not a trade terminal.
Repeated states, closed walks, and rotations are not used anywhere in this
report.
