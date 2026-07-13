# R33 selector proof lane: full-bank defect exchange

## Verdict

The theorem below is a noncircular, defect-decreasing simultaneous-row
exchange theorem for the honest R32 objective.  It uses the support-expansion
lemma from `tmp/fanout/p5_selection_adversary/REPORT.md`, but it does not
replace the full-bank defect by raw demand, a scalar P5 score, or a
common-blue Hall defect.

It does not prove `canonicalMicroFeasibleTuple_exists`.  It isolates the
strict exchange certificate that a positive-defect canonical tuple must
forbid.

## 1. Honest objective

Fix a valid row tuple `omega`.  Let

```text
D(omega) = CollisionHalf(omega)
           disjoint_union (HitNeed(omega) x Fin 25).
```

Let `S(omega)` be the finite set of checked full-bank schedules.  A schedule
contains exact rational spend variables and all auxiliary reservation and
source-component labels.  It is checked against the following literal R32
conditions.

1. Every micro-obligation receives total spend at most one.
2. Collision obligations can spend only literal `FreeHalf` resources.
3. A free key has capacity one, with
   `rawFreeSpend(key) + tokenizedSpend(key) <= 1`.
4. Every bank term has its typed canonical key and satisfies
   `priorSpend + localReserve + newSpend <= capQ`.
5. Every positive spend is incident to its owner/port under the checked
   terminal predicate.  Switch loss is an admissibility check, not capacity.
6. Source keys are globally deduplicated.  All positive uses of the two
   halves of one canonical source base have one destination component.
7. No spend crosses components, and all reservation deductions are included
   before residual capacity is used.

Thus this definition includes exclusive reservations and coherent source
bases.  In particular, it is smaller than the permissive P1--P5 relation.

For `X in S(omega)`, write

```text
served_X(d) = total spend into d,        0 <= served_X(d) <= 1,
value(X)    = sum_(d in D(omega)) served_X(d),
F(omega)    = max_(X in S(omega)) value(X),
Delta_mu(omega) = |D(omega)| - F(omega).
```

The zero schedule exists.  There are finitely many source-component
orientations; for each orientation the feasible schedules form a bounded
rational polytope.  Hence the maximum exists and is rational.  Clearing the
common denominator gives the equivalent exact integer formulation.  No
floating-point optimization is involved.

## 2. What support expansion supplies

Let `omega, eta` satisfy the four hypotheses of the support-expansion lemma:

```text
V_eta subseteq V_omega,
F_omega subseteq F_eta,
r_eta(v) <= r_omega(v) for v in A_eta,
c_eta(v) <= c_omega(v) for v in A_eta.
```

Then its proof gives

```text
A_eta subseteq A_omega,
h_eta(v) <= h_omega(v) for v in A_eta.
```

At owner `v`, the full-bank micro-demand has cardinality

```text
d_omega(v) = c_omega(v) + 25 h_omega(v).
```

Therefore there is an owner-preserving injection

```text
i : D(eta) -> D(omega).                                      (1)
```

This is only a demand-fibre injection.  It asserts no matching, flow, or bank
capacity.  One may choose it canonically by taking prefixes of the collision
and hit-copy enumerations at each owner.

Write

```text
R = D(omega) minus image(i),       q = |R| = |D(omega)|-|D(eta)|.
```

## 3. Checked ledger lift

Let `X` be a maximum schedule at `omega`.  The persistent part of `X` means
the spends whose obligation lies in `image(i)`.  A checked ledger lift of
this persistent part consists of an injective map `rho` from every physical
resource used by the persistent part to a resource at `eta`, satisfying:

```text
L1. rho preserves typed kind and canonical physical key;
L2. every old positive incidence (i(d),s) becomes a checked incidence
    (d,rho(s)) at eta;
L3. residual cap_eta(rho(s)) >= residual cap_omega(s), where both residuals
    deduct prior spend, local reservation, and every reservation footprint;
L4. every used FreeHalf remains free and outside the new reservation union;
L5. destination components agree under i, and rho preserves the chosen
    component label of every used canonical source base;
L6. the pushed raw, tokenized, and bank spends obey the two exclusive
    inequalities in Section 1.
```

These are finite row/graph/ledger checks.  For a literal free source, `L4`
can be proved by the local conditions

```text
pairCount_eta(x,y) = 0
and
the key (x,y,half) is outside every eta reservation footprint.
```

For a P5 source, the old attachment/reach witness must persist, exactly as in
Lemma 2 of the prior report.  `L5` is the additional R32 correction: half-key
injectivity alone is insufficient because the two halves of one base may not
be sent to different active components.

Pushing the persistent spends through `(i,rho)` gives a checked schedule
`X_keep` at `eta` with

```text
served_X_keep(d) = served_X(i(d)).                            (2)
```

No existence of a complete flow is hidden in this definition: only resources
actually used by one displayed maximum partial schedule are transported.

## 4. Defect-decreasing exchange theorem

**Theorem (exclusive coherent support exchange).**

Assume:

1. `omega,eta` are valid row choices related by a simultaneous row exchange;
2. the four support-expansion hypotheses hold;
3. `X` is an exact maximum full-bank schedule at `omega`;
4. the persistent part of `X` has a checked ledger lift `X_keep` to `eta`;
5. after that lift there is an explicit compatible residual augmentation `Z`
   of total rational mass `a >= 0` at `eta`.

Here compatible means that `X_keep + Z` passes the same incidence,
reservation, exclusivity, capacity, and base-component-coherence checks as a
full schedule.  Define

```text
s = sum_(d in R) served_X(d).
```

Then

```text
Delta_mu(eta) <= Delta_mu(omega) - (q - s + a).               (3)
```

Consequently, if `q-s+a > 0`, then

```text
Delta_mu(eta) < Delta_mu(omega).                              (4)
```

In the denominator-cleared integral model it is enough that the exchange
deletes one obligation left unmatched by `X`; then `q-s >= 1`.  Alternatively
an explicit positive residual augmenting path gives `a > 0`, even if every
deleted obligation was saturated.

### Proof

Because `X` is maximum,

```text
F(omega) = value(X).
```

The flow carried by deleted obligations is exactly `s`.  Equation (2) gives

```text
value(X_keep) = F(omega) - s.
```

Compatibility of `Z` gives a checked eta schedule `X_keep+Z`, so

```text
F(eta) >= F(omega) - s + a.                                  (5)
```

The demand injection (1) gives

```text
|D(eta)| = |D(omega)| - q.                                   (6)
```

Subtract (5) from (6):

```text
Delta_mu(eta)
 = |D(eta)| - F(eta)
 <= |D(omega)| - q - (F(omega)-s+a)
 = Delta_mu(omega) - (q-s+a).
```

This proves (3).  Since each deleted demand has served mass at most one,
`s <= q`, so the parenthesized quantity is nonnegative.  Strict positivity
proves (4).  Every step is valid over `Q`; multiplying by a common denominator
proves the integral form.  QED.

## 5. Useful graph-facing corollary

Let `omega` minimize the honest `Delta_mu`, and suppose `Delta_mu(omega)>0`.
Fix any maximum partial schedule `X`.  Then every simultaneous row exchange
`eta` satisfying support expansion and `L1`--`L6` must satisfy both:

```text
(C1) every obligation deleted by the demand injection is saturated by X;
(C2) the transported schedule has no positive compatible residual
     augmentation at eta.
```

Otherwise the theorem contradicts minimality.  Thus a positive-defect
canonical tuple is an exact cage against two concrete operations:

```text
delete an X-unsaturated collision/hit microcopy while preserving used keys;
or augment the transported partial ledger through residual typed capacity.
```

This is stronger and more accurate than minimizing raw `mu`: a strict drop in
raw demand alone need not lower `Delta_mu`, because all deleted obligations
could have been served.  The correction term `q-s` is exactly the missing
quantity.

## 6. Noncircularity audit

The theorem does not assume any of the following:

```text
Delta_mu(eta)=0;
eta has a complete matching;
every owner shore is feasible;
the P5 relation is component-unique;
switch loss is spendable capacity;
reservations are idempotent.
```

Its strict certificate is smaller than a full solution.  It needs one exact
maximum *partial* old schedule, persistence of only its surviving used keys,
and either one deleted unsaturated microcopy or one explicit residual
augmentation.  All are finite exact certificates.  The theorem therefore
does not restate `canonicalMicroFeasibleTuple_exists`.

## 7. Remaining selector lemma

To close the singular wall by descent, it now suffices to prove the following
graph statement, with no score proxy:

```text
If Delta_mu(omega)>0, choose an exact maximum exclusive/coherent schedule X.
Then there is a simultaneous shortest-row exchange eta satisfying the four
support-expansion hypotheses and L1--L6, such that either an X-unsaturated
micro-obligation is deleted or a positive compatible residual augmentation
is exposed.
```

The contrapositive describes the required all-tuple positive-defect cage:
every support-expanding simultaneous exchange must either destroy a used
physical source/reservation/component label, delete only saturated demand,
and expose no residual augmentation.  No graph-realizable cage with these
properties is produced in this lane.

No claim about the main theorem is made.

## 8. Targeted 2943 subdivision candidate: rejected by P1

The proposed sharpened construction was tested exactly by
`subdivided_anchor_gate.py`.

### Construction

For each of the 1,352 R29 arm edges `(y,55)`, delete that edge and add two
private vertices `a_y,b_y` and the blue path

```text
y -- a_y -- b_y -- 55.
```

This gives

```text
N = 2943 + 2*1352 = 5647,
|B| = 7039 - 1352 + 3*1352 = 9743,
|M| = 1383,
|E| = 11126.
```

### Structural gates

All of the intended graph and row facts pass.

```text
triangle-free:                         true
blue connected:                        true
displayed cut:                         9743
exact max-cut upper bound:             7039 + 2*1352 = 9743
all 1383 bad-edge blue distances:      4
Gamma:                                 1383*25 = 34575
shortest-row family histogram:         707 families of size 1,
                                       676 families of size 4
```

The max-cut proof is exact.  For fixed colors of `y` and `55`, a private
length-three path has maximum cut value

```text
2 + [y and 55 have different colors].
```

Restrict any cut of the new graph to the 2,943 old vertices and apply the old
`MaxCut <= 7039` certificate.  Summing the 1,352 path inequalities gives
`MaxCut <= 7039+2704=9743`; the displayed alternating extension attains it.

Every selector family has exactly four surviving local rows.  For each of all
676 families their four-row vertex-union has size 9 and support-edge union has
size 11.  Every such row avoids vertices `0..55`, so the hub collision fibres
are tuple-invariant:

```text
collision(0)=collision(1)=collision(2)=6650.
```

The larger `N` makes all three old hub HitNeed values zero.

### Decisive P1 failure of the candidate

Every one of the 2,704 new private vertices is absent from every selected row.
For each hub owner `o in {0,1,2}`, each new vertex `w`, and each half
`h in Fin 2`, the literal key

```text
(o,w,h)
```

is a same-first P1 `FreeHalf`: `pairCount(o,w)=0`, `o!=w`, there is no blue
edge `o--w`, and hence neither half is scoped-reserved.  The keys are globally
distinct.  This contributes exactly

```text
3 * 2704 * 2 = 16224
```

new P1 sources to the hub shore, uniformly over all `4^676` local tuples.

The literal production source reconstruction on the baseline local tuple
gives:

```text
hub collision demand                 19950
P1 same-first reach                  33549   margin 13599
P1/P3 union reach                    36149   margin 16199
```

The P1 count is itself tuple-invariant: selector rows avoid `0..55`; hub
co-occurrences are fixed by the rigid traffic rows; and every graph edge with
first coordinate a hub has tuple-independent selected/support status.  Thus
the proposed persistent hub defect 28 is destroyed before P5, Doors, or any
other bank class is considered.

**Verdict:** the length-three subdivision construction is not an all-tuple
positive-defect cage.  It is rejected by the exact P1 margin `+13599` on the
intended collision shore.  No P5 starvation claim is needed.

## 9. Reservation-free collision selector theorem

The cleaner selector objective excludes common-blue entirely.  Define

```text
C(omega) = ActiveCollisionHalf(omega),
R0(omega) = P1_sameFirst union P3_rowCompanion
            union strict_P4 union static_P5.
```

Every resource is a literal canonical `FreeHalf` key of unit capacity.  A key
must avoid the already-defined `ScopedReserved` predicate, but using an
`R0` terminal introduces no new reservation footprint.  The matching is
globally injective on half keys and base-component coherent.  HitNeed is not
in this matching problem; it is assigned only to typed Door, vertexSlack,
prune, or other checked bank capacity.

Let `M0(omega)` be the maximum cardinality of an `R0` partial matching and

```text
Delta_0(omega) = |C(omega)| - M0(omega).
```

This is an integer objective.  The following is the collision-only
specialization of the theorem in Section 4.

**Theorem (reservation-free collision exchange).**  Let `omega,eta` satisfy
the support-expansion hypotheses.  Let

```text
i : C(eta) -> C(omega)
```

be the owner-preserving fibre injection supplied by
`c_eta(v) <= c_omega(v)`.  Choose a maximum coherent `R0` partial matching
`X` at `omega`.  Assume every `X`-used key attached to `image(i)` remains a
FreeHalf at `eta`, remains in `R0` for the corresponding owner, remains
outside `ScopedReserved`, and keeps the same destination component for its
canonical base key.

Let `R=C(omega)\image(i)`, `q=|R|`, and let `s` be the number of matched
members of `R`.  If the transported matching at `eta` admits an explicit
compatible augmenting family of `a` additional half keys, then

```text
Delta_0(eta) <= Delta_0(omega) - (q-s+a).
```

In particular, deleting one `X`-unmatched collision half gives strict descent
without any augmentation, and one compatible augmenting path gives strict
descent without deleting unmatched demand.

The proof is the integral form of Section 4: restrict `X` to persistent
demands, transport its `M0(omega)-s` keys, add the `a` residual keys, and
subtract from `|C(eta)|=|C(omega)|-q`.  No complete matching at `eta` is
assumed.

For this specialization the source-persistence checks are concrete:

```text
P1: pairCount_eta(owner,y)=0 and the half is not newly scoped-reserved;
P3: the two owner companions persist, their source pair stays free, and the
    half is not newly scoped-reserved;
P4: the strict outside-selected component/attachment witness persists;
P5: the active component, quiescent component, attachment witnesses, and
    FreeHalf predicate persist;
all: the assigned canonical base keeps one destination component.
```

### Common-blue status

Neither proof artifact in this lane needs common-blue:

```text
reservation-free collision exchange theorem:  common-blue excluded
subdivided-anchor rejection:                   P1 alone
2943 repair mechanism used by the model:       static P5
```

On the exact 2943 all-anchor tuple, the hub collision demand is `19950` and
P1/P3/strict-P4 reach is `19925`, a collision defect of `25`.  The checked 28
static P5 keys raise the reach to `19953`, margin `3`; their destination is
the same active component, so the displayed repair is compatible with the
base-coherence requirement.  The older defect `28` included three HitNeed
units and belongs to the one-copy mixed-demand model.

Thus common-blue is unnecessary for the current large-fixture evidence and
is deliberately absent from the selector theorem.  Its terminal reservation
and exclusivity ledger cannot be used to prove or refute this simplified
statement.

## 10. Lock-cost versus P1/P3 capacity

The failed subdivision gives a general exact counting lemma.  It uses only
P1 and P3, and it is immune to scoped half-zero reservations by using half
`1` throughout.

Fix a valid maximum-cut row tuple `omega`, a nonempty deficient owner shore
`U`, and a set `W` of proposed blocker vertices with `U` and `W` disjoint.
For `o in U`, put

```text
C_o = {w in W : pairCount_omega(o,w) > 0},
d_o = |C_o|.
```

Let

```text
Shadow(U,W) = union_(o in U) {{x,y} subset C_o : x != y},
Q_W = {{x,y} subset W : pairCount_omega(x,y) > 0},
p_W = |Q_W|.
```

`Shadow` records blocker pairs that are companions of a common shore owner;
`Q_W` records pairs already made non-free by some selected row.

### Lemma (lock-capacity dichotomy)

The P1/P3 neighborhood of the owner shore `U` contains at least

```text
L(U,W) = |U||W| - sum_(o in U) d_o
         + 2 * max(0,
             ceil((sum_(o in U) binom(d_o,2))/|U|) - p_W)       (7)
```

distinct unreserved `FreeHalf` keys.

### Proof

For every missing incidence `(o,w)` with `w notin C_o`, the ordered key

```text
(sourceX,sourceY,half) = (o,w,1)
```

is free and P1-eligible for owner `o`.  Half `1` is never `ScopedReserved`.
These keys are distinct as `(o,w)` varies, giving the first term in (7).

Every unordered pair `{x,y}` in `Shadow\Q_W` is free and consists of two
companions of at least one common owner `o`.  Maximum-cut minimality gives

```text
sigma({x,y}) >= 0,
```

so both ordered half-one keys `(x,y,1)` and `(y,x,1)` are P3-eligible and
unreserved.  They are distinct from all P1 keys because their first
coordinate lies in `W`, whereas every counted P1 first coordinate lies in
the disjoint set `U`.

The sum `sum_o binom(d_o,2)` counts pairs in `Shadow` with multiplicity at
most `|U|`.  Therefore

```text
|Shadow| >= ceil((sum_o binom(d_o,2))/|U|).
```

At most `p_W` shadow pairs are removed by `Q_W`.  Each remaining pair gives
the two oriented P3 keys above.  Adding the disjoint P1 and P3 families proves
(7).  QED.

The obstruction term is itself charged to selected rows.  If
`w_R=|R intersect W|` for a selected five-vertex row `R`, then

```text
p_W <= sum_(selected rows R) binom(w_R,2) <= 10 * |M|.          (8)
```

The first inequality assigns each pair in `Q_W` to one row witnessing its
positive pair count; the second uses `w_R<=5`.

There is also an exact owner-load identity.  Put

```text
q_UW = sum_(o in U, w in W) pairCount(o,w),
i_UW = sum_(o in U) d_o.
```

Then

```text
q_UW - i_UW
  = sum_(o in U,w in W) max(0,pairCount(o,w)-1),               (9)
2*(q_UW-i_UW) <= collisionDemand(U),                           (10)
q_UW = sum_(selected rows R) |R intersect U|*|R intersect W|
     <= 6*|M|.                                                 (11)
```

Equation (9) separates the first owner-blocker contact from repeated contact;
(10) is the corresponding sub-sum of the literal collision demand.  Equation
(11) double-counts `(row,owner,blocker)` incidences and uses
`a*b<=6` when `a+b<=5`.  Thus blockers made non-P1 by insertion through
overloaded owners consume selected-row slots immediately, and repeated
insertions raise the very collision demand that the source pool must cover.

### Selector consequence

Suppose `W` hits the alternative rows whose use could lower `Delta_0`.
Equation (7) gives the promised dichotomy without mentioning common-blue:

1. If many blocker-owner incidences are absent, their owner-keyed P1 halves
   directly enlarge the deficient shore.
2. If most blocker-owner incidences are present, the sets `C_o` are large.
   Unless blocker pairs are densely packed into selected rows, their free
   companion shadow supplies P3 halves.
3. If both P1 and P3 are small, (7) forces `p_W` large; by (8), the blockers
   consume many selected-row pair slots.  Repeated use is additionally visible
   in the exact identities (9)--(11).

For the failed subdivision, `|U|=3`, `|W|=2704`, and every `d_o=0`.  The
reservation-proof lower bound already gives `L=8112` new P1 half-one keys;
the graph has no owner-blocker edges, so both halves are unreserved and the
exact gate obtains `16224`.

This lemma does not yet prove the selector theorem.  The remaining geometric
step is now precise: from a blocker set with `L(U,W)` below the deficient
shore demand, use the forced dense selected-row pair structure in (8) to
construct a simultaneous shortest-row exchange satisfying the persistence
hypotheses of Section 9.  That is the only branch not paid directly by
reservation-free P1/P3 capacity.
