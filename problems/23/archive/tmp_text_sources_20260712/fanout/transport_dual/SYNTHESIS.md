# transport_dual synthesis

## Decisive exact reduction

For a fixed coordinate with alternative set `Q`, new-demand bundle `Z`, old
outside-shore demand type `D`, old shore-source type `S`, and actual legal
source neighborhood `N(X)`, component-aware transport exists iff

`|X| <= |Q|*|D| + |Q|*|N(X)|` for every `X subset Z`.                 (CA-Hall)

This is both the integral max-flow/Hall condition and the thresholded Farkas
dual. An exact `Fraction` verifier checked all 682 relations through `3x3`.
The unrestricted cardinal inequality gives only an unlabelled injection and
does not imply CA-Hall.

For simultaneous trades, the lead candidate replaces `Q` by the full product
`Omega` and `Z` by `Sigma eta, Demand(eta)`. Its scalar consequence is

`sum_eta S(eta) <= |Omega| * (S(omega)-defect(A))`.                  (PHT)

This excludes a failing global minimum and survives strict Hamming-one local
minima. It passed all 705 exact order-10/11 Hall failures; the smallest
residual after paying `|Omega|*defect` was `1804/108 = 451/27` on graph6
`I?`ebRodO`, choice `(1,4,4)`. It is untested on N=12 and R29's 2943 cage.

The existing one-coordinate component transport, distinct from PHT, now has a
nonvacuous order-12 heavy gate: 4,801,067 tuples at 61 workers, zero transport
failures. The inherited-only branch occurred in 32 groups carrying 416
demands; no group was unanchored. First inherited fixture: graph6
`K?ABBBwerwBw`, choice `(3,4,6,4,9)`, coordinate 4, with 13 groups,
2 inherited-only groups, inherited demand 26, and exact flow `169/169`.

## Exact structural facts

For old row `P`, replacement `Q`, and background ordered co-occurrence count
`b(x,y)`, raw collision change at owner `v` is exactly

`R_Q(v)-R_P(v) = 2*T_Q(v)-2*T_P(v)`,

where `T_S(v)` counts row partners already occupied by another row. Moving
active scope adds exactly the entering-component load and subtracts the
leaving-component load. These identities, component/shore totals, coordinate
collision bounds, and nonpositive coordinate HitNeed variation passed both
Hall-failing tuples of fixture `I?`fBO]]?`: 6 coordinates and 26 alternatives.

Persistent-component containment is not enough for source capacity. Even a
conditional injective map of persistent new components to old components
allows one persistent component to carry two demands competing for one source.
The embedding descendant's stronger component-injection statement assumes
both endpoints of every changed active edge lie in the changed-row union;
current production locality proves only that a changed edge has at least one
endpoint there. Treat that strengthening as an open premise.

The current production Lean file proves persistent new-component containment,
`ActiveOwner` persistence, unchanged selected load away from changed rows,
`activeDegree_new <= activeDegree_old`, and
`hitNeedUnits_new <= hitNeedUnits_old`. Its recomputed SHA-256 after these
additions is `6b10458bedd26b4d460fdd4ad034d55cb6b1dee16a2691f22460e562941dc272`.

For an inclusion-minimal deficient shore with owner demand `d(a)` and defect
`delta`, exact uncrossing gives deficiency supermodularity and the sharp
private-source bound

`private_A(a) <= d(a)-delta`.

This is an upper bound, not source existence. The exact gate checked 65,536
weighted incidence systems and 63,260 minimal shores. In the real fixture
`A={8,9}`, demands are `(9,10)`, source union is 17, defect is 2, and private
counts are `(7,6)` against bounds `(7,8)`; only one owner deletion is tight.

## Exact falsifiers

Smallest abstract falsifier to deriving legal transport from the listed facts:
one alternative; singleton minimal shore; old demand `2`, source `1`, outside
capacity `0`; one new demand in a persistent component disjoint from the old
shore component and avoiding changed rows. Collision delta is `-1`, exactly
the defect bound; HitNeed delta is `0`; ordinary target cardinality is `1`;
the legal neighborhood is empty. Total counted multiplicity is 4. Exhaustive
search over aggregate values `0..4` found 35 such models and none smaller.

Smallest multiplicity obstruction after component injection: one persistent
component, two new demands, one eligible source, no outside target (`2>1`).

No nonnegative scalar weighting of Hamming-one deltas can beat a Hamming-one
local minimum. An abstract two-coordinate score has singleton deltas `1,1`
but joint delta `-3`, so simultaneous support is genuinely necessary.

The order-10 real fixture has inclusion-minimal owner shore `{8,9}` with
owner demands `9,10`, source optimum `17`, and exact gap `2`; both singleton
shores are nondeficient. Alternative component systems exported by the LP
lane had zero positive-demand groups, so their successful transport tests are
vacuous.

## Missing theorem

The proof frontier is exactly CA-Hall, or its full-product analogue: for every
subset of new demand copies, shared eligible old-source capacity plus universal
outside capacity covers the subset. Changed-row locality and persistent
embedding classify where a demand may go, but do not control demand
multiplicity into shared sources. Inclusion-minimality must be combined with a
new graph-realizable capacity lemma; abstract incidence alone cannot close it.

## Key hashes

- Lead product gate: `2b7cc737f15f8bd0d2fd679ca18899c26c5b5aa684331268788bcb51443a2dcc`
- Lead N10-N11 result: `c986093a3af0cf1e85bae9cca97478bf4e6d775ec2d8ddc53fe3e54c2cac187b`
- Farkas verifier: `9847528ae650d1497ad0a6fb556c28d58d6434578fc3861a5ef8c0ae44da327e`
- Referee falsifier: `efd98f164ce433bf4000f26b4db7e50cce6c9c6d70853ec6225b0a08c7d01c66`
- Accounting exact tests: `dac6db2fed41e1eee622ea3f90c5ad76ffefac95924eb59d098e2e2161aa5d5a`
- Embedding exact gate: `52209a8395b3581a093cebbdb3ae54a3e7f8a741de9f006b567e674df325f3d7`
- Global exchange test: `2105cf67c4335722b4571ab489c08e98ed39297c0b5c8c94e82cbecd1fd09956`
- LP smallest real shore witness: `a95b719e35c23bb4363a4c59893f0efb668a7af7bc6a3ac79dedca723637ba8d`
- Minimal-shore gate result: `0a56c2b8872c23415bc4772968112a97463441898831352bc8a1f47174a0d445`
- Current production transport Lean: `6b10458bedd26b4d460fdd4ad034d55cb6b1dee16a2691f22460e562941dc272`
