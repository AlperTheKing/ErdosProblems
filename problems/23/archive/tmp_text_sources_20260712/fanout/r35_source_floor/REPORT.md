# R35 source floor: exact shore identity, component-coherence tax, and the remaining strict-P4 gap

## Verdict

There is a sharp identity, but there is **no positive source floor from row
endpoint anchoring alone**.  For every fixed base-to-component labeling and
every owner shore, coherent Hall is exactly

```text
linear pressure + component-coherence tax
    <= quadratic P3 endpoint supply - P3 overlap loss + strict-P4 extra supply.
```

The precise formula is (SF) below.  The anchored R35 K3,3 core violates the
formula by 10 when strict P4 is set empty, even though all producer endpoint
pairs and selected rows are distinct and the coherence tax is zero.  Thus the
smallest missing graph lemma is not an endpoint-diversity estimate.  It must
force strict-P4 exposure (or an explicit coherent augment/row trade) from the
max-cut boundary that supports a least deficient shore.

## 1. Exact collision demand

Fix a valid selected row tuple `omega`.  Put

```text
n_xy = number of selected rows containing both x and y,
q_v  = n_vv = number of selected rows containing v,
C_v  = {x : n_vx > 0},
s_v  = |C_v|.
```

Each selected row is a simple five-vertex path.  Therefore

```text
sum_x n_vx = 5 q_v.
```

The collision-half demand at owner `v` is consequently

```text
D_v = 2 sum_x (n_vx - 1)_+
    = 2(5 q_v - s_v).                                      (D)
```

This is the exact sense in which collision demand is linear in the anchored
producers.  Endpoint anchoring is needed to retain the correct producer and
occurrence in a trade, but (D) itself only uses length five and row simplicity.

For an owner shore `A`, write

```text
D(A) = sum_{v in A} D_v,
r(A) = sum_{v in A} q_v.
```

All collision obligations at one owner are twins in the current
P1/P3/strict-P4 relation.  Hence a maximum-deficiency Hall shore may be taken
as a union of complete owner fibers: adding the remaining obligations of an
already present owner raises demand and does not enlarge its source
neighborhood.

## 2. P1 and the exact pressure identity

Let `rho_1(v)` be the number of unavailable half-zero orientations among the
ordered P1 bases `(v,y)` with `y notin C_v`.  Equivalently, in the current
scoped model it is the number of demanded active edges oriented out of `v`.
The P1 source sets of distinct owners are disjoint, because their first
coordinates differ.  Thus

```text
Own(A) = sum_{v in A} [2(N-s_v) - rho_1(v)].                (P1)
```

Subtracting (P1) from (D) cancels every `s_v`:

```text
D(A) - |Own(A)|
  = 2(5 r(A) - N|A|) + rho_1(A)
  =: press(A),                                             (PRESS)
```

where `rho_1(A)=sum_v rho_1(v)`.  This is the collision-only specialization of
the earlier R24 shore identity.  It is exact, not a relaxation.

## 3. Sharp quadratic P3 term and its losses

Because the displayed cut is maximum, the two-vertex switch loss is
nonnegative for every pair.  Therefore a free ordered base `(x,y)` is P3
eligible for `v` exactly when `x,y in C_v`.

To count only P3 keys not already counted by P1 for the shore, set

```text
X_v(A) = C_v \ A,
d_v(A) = |X_v(A)|.
```

The condition `x notin A` is exact: if `x in A` and `n_xy=0`, then `(x,y)` is
already a P1 base for owner `x`; if `x notin A`, it is not P1 for any owner in
the shore.

There are

```text
d_v(A)(s_v-1)
```

ordered candidate bases with `x in X_v(A)`, `y in C_v`, and `x != y`.  Define

```text
b_v(A) = #{(x,y): x in X_v(A), y in C_v, x != y, n_xy > 0},
rho_3(v,A) = number of these free bases whose half-zero is reserved.
```

The exact number of P3 half incidences from owner `v`, after deleting P1, is

```text
t_v(A) = 2[d_v(A)(s_v-1) - b_v(A)] - rho_3(v,A).           (P3-inc)
```

This displays the desired quadratic endpoint-diversity term and the first
unavoidable loss: other selected rows may block a candidate by making
`n_xy>0`.

The same source half can be P3-eligible for several owners.  Let

```text
ov_3(A) = sum_{v in A} t_v(A) - |Extra_3(A)| >= 0,          (OV)
```

where `Extra_3(A)=P3(A)\Own(A)`.  This is the exact deduplication/overlap loss,
not an estimate.  Hence

```text
|Extra_3(A)| = sum_{v in A} t_v(A) - ov_3(A).              (P3)
```

Endpoint anchoring only says different bad-edge indices select different
ordered rows.  It does not bound either `b_v(A)` or `ov_3(A)` strongly enough
to close Hall.

## 4. Base/component coherence is an explicit tax

For an available ordered source base `k=(x,y)`, let `H_k` be its available
half keys, so `|H_k|` is one or two.  For a shore `A`, let

```text
E_k(A) = { active component of v : v in A and k is eligible for v }.
```

Fix a base-label map `lambda`, choosing at most one active component for each
base.  The label-filtered reach is

```text
Reach_lambda(A)
  = sum_k |H_k| * 1[lambda(k) in E_k(A)].
```

Let `RawReach(A)` ignore the base-component restriction.  The exact coherence
tax is

```text
kappa_lambda(A)
  = |RawReach(A)| - |Reach_lambda(A)|
  = sum_k |H_k| * 1[E_k(A) != empty and lambda(k) notin E_k(A)].  (KAPPA)
```

This labeling reduction is exact:

```text
a coherent total assignment exists
iff
there is a label map lambda for which the ordinary label-filtered
bipartite graph satisfies Hall for every owner shore A.
```

Forward direction: label each used base by the common component forced by
`BaseKeyComponentCoherent`, and label unused bases arbitrarily.  Reverse
direction: every assignment in the label-filtered graph uses a given base only
inside `lambda(k)`, so it is coherent.

Ordinary raw Hall cannot replace (KAPPA).  Two half keys of one base, each
eligible to one owner in each of two components, pass every raw Hall shore for
demands `(1,1)`.  A coherent assignment is impossible: either base label
leaves one singleton owner shore with filtered reach zero.  The checker below
verifies this exact two-owner obstruction.

## 5. The sharp source-floor inequality

Define strict-P4 extra supply after literal key deduplication by

```text
Extra_4(A) = P4(A) \ (Own(A) union P3(A)).
```

Then

```text
RawReach(A) = Own(A) disjoint-union Extra_3(A)
                         disjoint-union Extra_4(A).
```

Combining (PRESS), (P3), and (KAPPA), Hall for the fixed label map is exactly

```text
2(5 r(A) - N|A|) + rho_1(A) + kappa_lambda(A)
 <= sum_{v in A}
      {2[d_v(A)(s_v-1) - b_v(A)] - rho_3(v,A)}
    - ov_3(A)
    + |Extra_4(A)|.                                        (SF)
```

No term in (SF) is asymptotic or fractional.  A least deficient Hall shore
for a fixed label map is precisely a shore on which (SF) is strict in the
opposite direction.

Equivalently, the exact strict-P4 amount required at such a shore is

```text
|Extra_4(A)| >=
  press(A) + kappa_lambda(A) - |Extra_3(A)|.                (P4-floor)
```

Thus a proof based on source counting has one remaining graph-derived task:
prove (P4-floor), or turn its failure into an explicit coherent augmentation
or checked simultaneous lex trade.

## 6. Anchored K3,3 obstruction is sharp

For the R35 `a x b` double-star at the central owner `v`,

```text
q_v = ab,
s_v = a+b+3,
D_v = 2(5ab-a-b-3).
```

The endpoint P3 bases are exactly the ordered same-shore pairs, so

```text
|P3(v)| = 2[a(a-1)+b(b-1)],
D_v-|P3(v)| = 2(5ab-a^2-b^2-3).                            (DS)
```

At `a=b=t`, (DS) is `6t^2-6`.  This is the exact refutation of a universal
quadratic endpoint floor: the selected rows themselves consume every
cross-shore endpoint pair.

For the R35 K3,3 instance (`a=b=3`, `N=29`, two P1 half-zero reservations):

```text
demand                         = 72
P1                             = 38
quadratic P3 candidates        = 64 ordered bases
blocked by selected cooccurrence = 52
free P3 bases                  = 12
P3 half supply                 = 24
component-coherence tax        = 0
strict-P4 supply required      = 72-38-24 = 10.
```

So even the one-component case fails without strict P4.  Component coherence
is a real additional difficulty, but it is not the cause of the R35 gap.

## 7. What max-cut gives, and the precise remaining geometric gap

In the double-star, apply max-cut domination to the terminal shore consisting
of `c_L` and all left leaves.  Its bad boundary has size `ab`, while the core
blue boundary contributes only `r-c_L`.  Therefore the external blue boundary
must have size at least

```text
ab-1.
```

The right shore gives another `ab-1`.  This is sharp and is the origin of the
lock budget in the real double-star cages.

But boundary-edge multiplicity is not source-key multiplicity.  Many lock
edges can share outside vertices, and selected-but-noncompanion lock vertices
are invisible to strict P4.  The 2943 cage realizes exactly this blind spot.
Therefore the remaining lemma must use more than the scalar max-cut boundary:

```text
LOCK-EXPOSURE-OR-TRADE (minimal missing lemma).
For a canonical (defect,rowCode)-minimal tuple, every fixed-label least
deficient shore A satisfies (P4-floor); otherwise the concentrated or hidden
lock boundary yields an explicit coherent augmentation or an explicit checked
nonincreasing-defect, rowCode-decreasing simultaneous row trade.
```

This is strictly smaller than `NoCommonBlueCollisionFeasibility`: all demand,
P1, P3, overlap, reservation, and base/component accounting have already been
eliminated by (SF).  Its only content is converting graph-forced lock boundary
into strict-P4 keys or a checked trade.

## 8. Exact checker

Run:

```powershell
python tmp/fanout/r35_source_floor/check_source_floor.py
```

It uses integer/set arithmetic only and checks:

1. all seven owner shores of `I?rFf_{N?`, choice `[0,0,0,7]`;
2. the R35 K3,3 equalities above; and
3. the two-component coherence-tax obstruction.

For the pinned N=10 tuple, the worst P1/P3/P4 shore is `{4,6,8}`:

```text
demand=32, P1=18, press=14,
P3 owner incidences=8, P3 overlap loss=4, P3 extra=4,
P4 extra=0, raw reach=22, raw defect=10,
coherence automatic=true.
```

The final line is:

```text
PASS exact source-floor identities and coherence-tax obstruction
```

