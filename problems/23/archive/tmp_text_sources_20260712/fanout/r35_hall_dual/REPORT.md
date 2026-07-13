# Coherent Hall dual at a lex-minimal tuple: exact obstruction

## Verdict

The requested uncrossing/Farkas/matroid argument does **not** follow from the
current abstract collision-defect interface.  The obstruction is the
base-component coherence law itself:

> the two half keys of one ordered-pair base may be used together only for
> obligations in one component.

This makes coherent matchability non-matroidal and makes its rank function
non-submodular.  Consequently, least deficient coherent shores do not uncross.
Moreover, a lex-minimal row tuple can have positive coherent defect while
admitting neither an augmentation nor a simultaneous lex trade in the abstract
interface.

This is not a counterexample to the final real-graph theorem.  It identifies
the exact extra graph lemma required to turn a coherent Hall obstruction into
a row trade.

## 1. Exact three-obligation obstruction

Use one physical ordered-pair base `b` with its two honest half keys

```text
(b,0), (b,1).
```

Use three distinct collision obligations

```text
x1, x2  in component A,
y       in component B.
```

Each symbol denotes one full obligation identity, including producer atom,
positive occurrence, collision copy, debit half, and component.  No copy or
half is collapsed.  In the abstract `Data`, declare `sourceRealized` true from
every obligation to both source halves.  An assignment is injective on
`(base,half)` and obeys the production
coherence law: if two assigned keys have base `b`, their obligations must have
the same component.

For `X` a set of obligations, let `r(X)` be the maximum cardinality of a
coherent partial assignment using only obligations in `X`.  Exhaustion gives

| `X` | `r(X)` | `|X|-r(X)` |
|---|---:|---:|
| `empty` | 0 | 0 |
| any singleton | 1 | 0 |
| `{x1,x2}` | 2 | 0 |
| `{x1,y}` | 1 | 1 |
| `{x2,y}` | 1 | 1 |
| `{x1,x2,y}` | 2 | 1 |

The reason is exact: both halves can be spent on `x1,x2`, but any set using
one `A` obligation and `y` can spend at most one half of `b`.

Thus `{x1,y}` and `{x2,y}` are least-cardinality and inclusion-minimal
deficient coherent shores.

## 2. Uncrossing fails numerically

Put

```text
P = {x1,y},     Q = {x2,y}.
```

Then

```text
r(P) = 1,
r(Q) = 1,
r(P union Q) = 2,
r(P intersection Q) = r({y}) = 1.
```

Hence

```text
r(P)+r(Q) = 2 < 3 = r(P union Q)+r(P intersection Q).
```

So coherent rank is not submodular.  The two least deficient shores cross,
but their intersection is not deficient.  The standard Hall uncrossing step
cannot replace them by a smaller deficient shore.

Raw half-neighborhood Hall is also unsound here: `{x1,y}` sees both half keys,
so `|N({x1,y})|=2=|{x1,y}|`, although no coherent total assignment exists.
Defining the shore capacity as `r(X)` repairs the statement only tautologically:
computing `r` is the original coherent matching problem.

## 3. The local system is not a matroid

Let coherent assignable obligation sets be the proposed independent sets.
The sets

```text
I = {x1,x2},    J = {y}
```

are independent and `|I|>|J|`.  But neither `J union {x1}` nor
`J union {x2}` is independent.  This violates the matroid exchange axiom.

Therefore there is no matroid-rank dual or matroid uncrossing argument for
the present assignment-level coherence law.  Duplicating `b` by component
does not fix the issue: one must then enforce that at most one component-copy
of `b` is selected, which restores the same disjunctive constraint.

## 4. What Farkas does and does not provide

An unsafe common linearization introduces assignment variables `u[d,h]` and
component activations `z[A],z[B]`:

```text
sum_h u[d,h] = 1                       for each demanded d,
sum_d u[d,h] <= 1                      for h=0,1,
u[d,h] <= z[component(d)],
z[A]+z[B] <= 1.
```

For the deficient pair `{x1,y}`, its LP relaxation has the fractional point

```text
u[x1,0]=u[x1,1]=1/2,
u[y,0] =u[y,1] =1/2,
z[A]=z[B]=1/2.
```

Every displayed constraint holds, while the integer coherent assignment is
impossible.  Thus Farkas applied to this relaxation yields no obstruction.

One can strengthen the formulation, or take the exact convex hull of all
coherent assignments.  Farkas then gives a separating inequality, but that
inequality must encode the component-disjunction, for example the valid
mixed-component inequality

```text
sum_h u[x1,h] + sum_h u[y,h] <= 1.
```

The family of such inequalities has the non-submodular rank table above.
An exact-convex-hull Farkas certificate therefore does not supply laminar
uncrossing, and it contains no operation that changes rows.  Converting such
a certificate into a simultaneous row change is precisely the missing graph
theorem, not a consequence of finite-dimensional duality.

## 5. Lex minimality does not force a trade

Take the row-state type to be the singleton `{omega}` and set
`rowCode(omega)=0`.  Use the data from Section 1 at `omega`.

The matching

```text
x1 -> (b,0),
x2 -> (b,1)
```

is coherent and leaves exactly `y` unmatched.  The rank table proves that no
matching covers all three obligations, so

```text
collisionDefect(omega)=1.
```

The sole state `omega` is lex-minimal exactly in the sense of
`CheckedCollisionLexTrade.LexMinimal`.  There is no coherent augmentation,
because rank is two.  There is no checked defect trade, because every new
state equals `omega`.  There is no checked lex trade, because it would require
`rowCode(omega)<rowCode(omega)` when defect is unchanged.

Hence the following abstract implication is false:

```text
lex-minimal state + least deficient coherent shore
  => coherent augmentation or simultaneous lex trade.
```

This countermodel instantiates the semantics of
`CheckedCollisionDefectTrade.Data`, `CoherentPartialMatching`,
`BaseKeyComponentCoherent`, and `LexMinimal`.  It deliberately does not claim
to instantiate the complete real graph source relation.

## 6. Relation to R34, the 24-vertex obstruction, and the adapter

R34's repeated-state argument already fails because a closed alternating
walk can be a matching rotation.  The example above identifies a second,
independent failure mode: a free or alternatingly reachable half can be
blocked solely by the component already attached to its base.

The real 24-vertex R35 cage has a different obstruction.  Its 72 central
obligations all have the same active-component label, so base coherence causes
no loss there.  Nevertheless its concrete tuple has only 48 reachable
P1/P3/strict-P4/P5 halves and defect 24.  This independently rules out static
endpoint source floors.  Its explicit alternative row lowers central demand,
but that fact alone does not prove a checked trade at every canonical least
shore.

`CollisionDefectGraphAdapter.lean` correctly retains physical half keys and
assignment-level base coherence.  It also honestly leaves
`NoCommonBlueCollisionFeasibility` as a hypothesis.  The current adapter uses
the no-common-blue P1/P3/strict-P4/P5 union, so it is not yet the final frozen
six-relation adapter.  Nothing in the adapter converts a deficient shore into
a row change, and the abstract countermodel shows that such a conversion
cannot be added as pure matching bookkeeping.

## 7. Exact missing lemma and viable decomposition

The load-bearing graph statement must explicitly use canonical row geometry.
A noncircular form should split into two lemmas for an optimal coherent
matching `M` at the lex-minimal tuple `omega` and a least deficient shore `Z`.

### A. Base purification or checked trade

For every base reached from `Z`, either all obligations that can use that base
have one component label, or the mixed-component conflict constructs a
graph-realized simultaneous row change `omega -> omega'` and a coherent
matching `M'` such that

```text
unmatchedCount(M') <= unmatchedCount(M),
rowCode(omega') < rowCode(omega).
```

The conclusion must be an actual `CheckedCollisionLexTrade.Trade`; merely
finding a repeated cursor, closed cycle, free half, or alternative shortest
row is insufficient.

### B. Pure-shore expansion or checked trade

After base purification, ordinary half-key matching is a transversal-matroid
problem and standard alternating-path/Hall uncrossing is valid.  The graph
lemma must then show, for the actual deficient shore, either enough eligible
physical half keys for an augmentation or another checked simultaneous lex
trade.  This cannot be a static endpoint floor, by the real 24-vertex cage;
it must depend on the canonical tuple and the specific deficient shore.

Together A and B would yield the desired augment-or-trade dichotomy.  At a
lex-minimal tuple with an optimal matching, augmentation contradicts
optimality and a checked lex trade contradicts lex minimality.  Without A and
B, the proposed uncrossing/Farkas/matroid route is blocked exactly by the
three-obligation model above.
