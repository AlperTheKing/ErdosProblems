# ActiveScoped real-wall invariance audit

## Scope and evidentiary boundary

The staged directory contains no R29 definitions or implementation, only the task text. Accordingly, this report distinguishes (i) exact **interface-level R29 witnesses**, checked on the carrier `V={0,...,28}`, from (ii) **geometry-realization obligations**. The witnesses prove that a dependency can break invariance if a real-wall move can change the named field; they do not assert that the unstaged R29 geometry admits that move. No floating-point arithmetic is used.

## Criterion

For a selector predicate `P`, ActiveScoped invariance across real-wall states `w,w'` fails exactly when there is an active candidate tuple `x` for which `P(w,x) != P(w',x)`. A dependency is therefore harmless only if its relevant restricted datum is equal in both states. Equality of the full global datum is stronger than necessary.

| predicate/source | smallest datum that must be stable on active candidates | direct breaking channel | exact checked witness |
|---|---|---|---|
| `sameFirst(a,b)` | partition of active candidates induced by `first` | `U_omega` or active-component changes alter first representative | `first(1):1->0`, pair `(0,1)` |
| `sameOwner(a,b)` | partition induced by `owner` | active/attachment component reassignment, or reservation-based ownership | `owner(1):1->0`, pair `(0,1)` |
| `commonBad(a,b)` | `bad` membership on the queried pair | `U_omega`, active components, attachment boundary, or reservation can change badness | `bad: empty->{0,1}` |
| `rowCompanion(a,b)` | active row co-occurrence relation | row membership/co-occurrence changes | add row pair `(0,1)` |
| `outsideAttachment(a)` | attachment-component membership and boundary status of `a` | component split/merge or boundary change | remove `0` from its attachment component; separately add boundary `0` |
| each FullBank kind | legality, residual capacity, and reservation status for the queried source | any of those three changes | checked independently for all four kinds |

The first/owner partitions, not their literal labels, are the exact invariant: a simultaneous relabeling cannot change `sameFirst`/`sameOwner`. Likewise, irrelevant changes outside the queried active scope do not matter.

## Dependency audit

Legend: **D** direct input; **I** indirect only (must change a direct input); `-` no breaking path absent an unstated coupling.

| selector | `U_omega` | active comps | attachment comps/boundaries | rows | reservations | legality/capacity |
|---|---:|---:|---:|---:|---:|---:|
| `sameFirst` | I | D | I | - | - | - |
| `sameOwner` | I | D | D | - | I | - |
| `commonBad` | I | I | I | - | I | - |
| `rowCompanion` | - | I | - | D | - | - |
| `outsideAttachment` | - | - | D | - | - | - |
| `Door` | I | I | D | - | D | D |
| `vertexSlack` | D | D | I | - | D | D |
| `c5Base` | I | I | I | D | D | D |
| `prune` | I | I | I | I | D | D |

Here “source selector” means availability of a FullBank source. `prune` is treated as a source kind, as requested, not as the act of pruning.

### Source-kind details

- **Door.** Smallest abstract breaker: an active door source `d` is legal with positive residual capacity and unreserved before the move, and afterward at least one of those facts is false (or conversely). Attachment boundary is a structural route to legality; it is not independently relevant once legality/capacity are held fixed.
- **vertexSlack.** Smallest abstract breaker: an active vertex `v` crosses membership in `U_omega`, changes active-component slack, is reserved/unreserved, changes legality, or crosses residual capacity zero. Only a change visible in the final legality/capacity/reservation tuple breaks selection.
- **c5Base.** Smallest abstract breaker: an active base changes certified C5/row co-occurrence, or its legality, residual capacity, or reservation changes. Component and attachment changes matter only insofar as they invalidate that certificate or alter the final tuple.
- **prune.** Smallest abstract breaker: a candidate enters/leaves the prunable domain through an upstream filter, or its legality/capacity/reservation tuple changes. `U_omega`, component, attachment, and row changes are indirect unless the actual definition reads them directly.

## Necessary and sufficient stability statement

Let `A` be the union of candidates queried by ActiveScoped selectors in the two wall states. All audited selector values are invariant if and only if, on those queries:

1. the equality relations induced by `first` and `owner` agree;
2. relevant `bad` memberships agree;
3. relevant row co-occurrence pairs agree;
4. attachment membership and boundary bits agree; and
5. for every queried `(kind,source)` with kind in `{Door,vertexSlack,c5Base,prune}`, the triple `(legal, residual-capacity-positive, reserved)` agrees.

This is smaller than requiring stable `U_omega`, component decompositions, rows, or reservations globally. Those objects can change without breaking invariance when their projections above remain unchanged.

## Exact checks

Run:

```text
python checks.py
```

Expected exact output:

```text
PASS carrier=R29 predicate_witnesses=6 source_witnesses=12 floats=0
```

The six predicate witnesses isolate `first`, `owner`, `bad`, rows, attachment-component membership, and attachment boundary. For each of the four source kinds, three more witnesses independently isolate legality, capacity crossing `1->0`, and reservation. Each pair differs in exactly one state field; assertions reject accidental multi-field witnesses.

## Unresolved geometry-realization obligations

Without the R29 wall-to-state definitions, no honest concrete real-wall pair can be certified. The smallest missing facts are: whether a real-wall move can change each projected datum above while retaining the queried candidates in ActiveScoped scope, and the exact derivations of `first`, `owner`, `bad`, source legality, and capacity. Supplying those definitions would allow the interface witnesses to be refined into concrete wall coordinates; no float-based search is needed.
