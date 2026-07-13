# R41 support-retention referee report

## Verdict

The R41 general obstruction is valid for genuine two-edge detours, and it
strengthens to a monotone-support theorem.  It does not depend on row-path
injectivity across atoms, on preservation of active components, or on the
33-vertex census.  The strict R38 multiplicity-saturated directed rotor is
therefore impossible in every real row system satisfying the stated local
detour hypotheses.

The original R41 wording suppresses two load-bearing local facts: only one
selected row slot is replaced, and every selected row co-occurring on a blue
square edge contains that edge consecutively.  Genuine checked induced
shortest rows supply the second fact.  Without either fact the claim is false;
exact countermodels are listed below.

## Minimal theorem

Let `I` be a finite set of selected-row slots, let `R_i` be a finite vertex
sequence for each `i in I`, and put

```text
Supp(R) = union_i { consecutive unordered pairs of R_i },
n_R(p,q) = #{i in I : p and q both occur in R_i}.
```

Fix one slot `i0`.  Suppose its old and new rows differ only by

```text
Q  = a-x-m-y-b,
Q' = a-x-v-y-b,
```

with the four square edges distinct.  Write

```text
e1 = xm, e2 = my, f1 = xv, f2 = vy.
```

Assume:

1. `f1,f2` are absent from `Supp(R)` (in R41 this follows because they are old
   active edges);
2. for `j != i0` and `e in {e1,e2}`, if both endpoints of `e` occur in `R_j`,
   then `e` is a consecutive edge of `R_j`;
3. the target tuple changes slot `i0` only, from `Q` to `Q'`.

If `R'` is the target tuple and

```text
d = #{e in {e1,e2} : e is absent from every unchanged row},
```

then

```text
|Supp(R')| = |Supp(R)| + 2 - d >= |Supp(R)|.                 (1)
```

Moreover, because `Q` contains both old edges and hypothesis 2 identifies
cooccurrence with support occurrence on unchanged rows,

```text
|Supp(R')| = |Supp(R)|
  iff d = 2
  iff n_R(m,x) = n_R(m,y) = 1.                              (2)
```

Thus support grows strictly if either old pair count is at least two.

## Proof

All unchanged row slots contribute the same support before and after the
detour.  Removing `Q` can remove only `e1,e2`, and it removes exactly those
among them absent from every unchanged row.  Adding `Q'` adds exactly `f1,f2`:
they are distinct and neither was in the old support.  This proves (1).

The integer `d` is at most two, so equality in (1) holds exactly when both old
edges disappear.  Slot `i0` contributes once to each old pair count.  By
hypothesis 2, another slot contains both endpoints exactly when it retains the
corresponding old support edge.  Hence both disappear exactly when both pair
counts equal one, proving (2).

No active-component statement is used.  Even if replacement changes or
destroys a component, an edge remaining in selected support is excluded from
`activeEdges` before components are computed.

## Cycle corollary

Along a directed cycle of genuine two-edge detours, support cardinality is
nondecreasing by (1) and returns to its initial value.  Therefore every edge
of the cycle has equality, and every transition satisfies

```text
n_R(m,x) = n_R(m,y) = 1.
```

In the target state the four ordered pairs

```text
(m,x), (x,m), (m,y), (y,m)
```

all have pair count zero.  With the two half bits this creates eight raw
ordered `FreeHalf` keys per transition.  Consequently a zero-exposure survivor
cannot be the R38 multiplicity-saturated rotor.  It must be a source-swap
rotor in which every created key that passes the target eligibility and
reservation filters is already matched or blocked.  The support theorem alone
does not prove that all eight raw keys pass those filters.

## Edge-case audit

- Same atom: impossible as a source of multiplicity.  Lean `pairCount` counts
  selected row slots, and a `RowChoice` has one selected slot per bad atom.
- Duplicate rows: harmless.  Two distinct slots may contain the same geometric
  row; replacing one leaves the other and its support edge unchanged.
- Pair-count semantics: Lean counts rows satisfying membership, not vertex
  occurrences.  Python's R41 reconstruction agrees on checked nodup rows.
- Replacement and components: the theorem requires a one-slot replacement.
  Component changes are irrelevant after support retention is established.
- Adjacent cooccurrence: the needed property is inducedness on `xm,my`.
  Genuine shortest paths are induced; in the checked five-cycle setting it is
  also forced by row validity and triangle-freeness.
- Active definition: `activeEdges` is formed only after subtracting the full
  deduplicated `selectedSupport`; demanded active edges are a further subset.

## Sharp countermodels to omitted hypotheses

Vertices are `m=0, x=1, a=2`.

Without cooccurrence-to-support, take old rows
`[(m,x), (m,a,x)]` and replace the first by `(a)`.  The old pair count is two,
but target support is `{ma,ax}` and `mx` is active, not retained.

Without one-slot replacement, take two old rows `[(m,x),(m,x)]` and replace
both by `[(a),(a)]`.  The old pair count is two and target support is empty.

With the wrong occurrence semantics, the single malformed row `(m,m,x)` has
raw occurrence product two but actual row-slot `pairCount=1`; replacing it by
`(a)` removes `mx`.  This does not model checked rows or Lean `pairCount`.

## Exact checks

`check_support_retention.py` exhausts 11,232 qualifying two-slot models,
including 936 duplicate-row models, 8,424 repeated-vertex models, and 5,552
models whose active-edge set size changes.  It also checks the detour identity
on 101 induced backgrounds: 75 equality cases, 26 strict-growth cases, zero
failures, and eight raw ordered free halves in every equality case.

```powershell
python tmp/fanout/r41_support_referee/check_support_retention.py
python -m py_compile tmp/fanout/r41_support_referee/check_support_retention.py
python tmp/fanout/r41_rotor_realization/verify_manifest.py
```

The original manifest replay also passes byte-for-byte: 144 tuples, 32
saturated transitions, 16 inverse pairs, zero support-lemma failures, and
minimum defect zero.
