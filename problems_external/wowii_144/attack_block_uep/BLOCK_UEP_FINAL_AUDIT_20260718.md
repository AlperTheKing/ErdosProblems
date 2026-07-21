# W144-MIN block-tree / UEP final audit

Date: 2026-07-18.

## Status

This note does **not** prove the W144-MIN characterization and does not prove
W144.  It isolates the exact global implication that remains after the
unique-eccentric-point argument, verifies that implication on the complete
girth-at-least-five corpus through order 13, and records a two-cycle-block
configuration showing why disjoint new-center fibers alone give no global
contradiction.  The proof attempt stops at the first unsupported inference.

## 1. Direct frontier

For a connected graph `G`, write

```text
r       = rad(G),
C       = C(G),
e       = eta(G) = max_x d_G(x,C),
R       = {x : d_G(x,C)=e}.
```

A vertex `v` is admissible when `H=G-v` is connected and cyclic.  For an
admissible `v` with `rad(H)<=r`, define the exact unique-eccentric-point fiber

```text
Q_v = {u in V(G)-C-{v} :
       ecc_G(u)=r+1 and v is the unique eccentric vertex of u in G}.
```

The remaining load-bearing statement is

```text
(UEP-COVER)
If beta(G)>=2 and girth(G)>=5, there are an admissible v and x in R-{v}
such that rad(G-v)<=r and Q_v intersect B_G(x,e-1) is empty.
```

This is an exact bridge, not an asymptotic proxy.  If it held, the lemma in
the next section would give `eta(G-v)>=eta(G)`.  Therefore a vertex-minimal
induced connected cyclic subgraph with nondecreasing eta could not be
multicyclic.  The proved unicyclic theorem would then give W144 exactly as in
the registered W144-MIN route.

## 2. Proved UEP-cover necessity

**Lemma.**  Let `H=G-v` be connected, suppose `rad(H)<=rad(G)`, and suppose
`eta(H)<eta(G)`.  Then for every `x in R-{v}`,

```text
Q_v intersect B_G(x,e-1) is nonempty.                    (2.1)
```

**Proof.**  Put `r'=rad(H)` and `e'=eta(H)`.  Since the parameters are
integral, `e'<=e-1`.  For a surviving `x in R`, choose a closest
`u in C(H)`.  Then

```text
d_G(x,u) <= d_H(x,u) <= e' <= e-1.                       (2.2)
```

The vertex `u` is not in `C`, because every old center has `G`-distance at
least `e` from `x`.

For every `y!=v`, centrality of `u` in `H` gives
`d_G(u,y)<=d_H(u,y)<=r'<=r`.  Since `u` is not central in `G`, its
eccentricity in `G` is at least `r+1`; hence only `v` can be eccentric to
`u`.  If `w` precedes `v` on a shortest `u-v` path, then

```text
d_G(u,v)-1 = d_G(u,w) <= d_H(u,w) <= r' <= r.
```

Thus `d_G(u,v)=r+1`, `r'=r`, and `v` is the unique eccentric vertex of
`u`.  Consequently `u in Q_v`, and (2.2) proves (2.1).  QED.

The contrapositive is the exact deletion certificate used in UEP-COVER: an
uncovered surviving eta-realizer forces `eta(G-v)>=eta(G)`.

## 3. Exact finite certificate

`verify_uep_cover_audit.py` generates the complete connected
girth-at-least-five corpus with `geng -ctfq`.  It independently recomputes
girth, cycle rank, every eccentricity, the full center, eta, every admissible
deletion, deletion radius, every `Q_v`, and the uncovered-realizer condition.
For every reported witness it also directly checks
`eta(G-v)>=eta(G)`.

The run through order 13 returned

```text
order       5  6  7   8    9    10    11     12      13
checked     0  0  1   7   38   202  1,087  6,192  38,066
```

In total, 45,593 multicyclic graphs were checked and no failure occurred.
The machine-readable result records

```text
corpus SHA-256:
be3f60c8462e440da7a159a21b2047a0db4471347ce13aa57c8836117e664fc8

canonical first-witness SHA-256:
1a7b0fb1e9dc4b29217ab5c3116276fcabc6e447f75700c0913ab36f22348e8f
```

File SHA-256 values are

```text
verify_uep_cover_audit.py
8A5AE09D3ADA0A488A59849A64219B077EC03AA1AA305BEC6CCF048CC8D17A91

verify_block_uep_obstruction.py
F4263867F02258B466C6FC5A18C2B607E795F912F81909AAFB51C07A8BCC0F50

uep_cover_audit_results.json
4F2E464573B47E739DB323553BC72853BF34C1CDF272EC7EB1D37DD3DE4E74DC
```

This is finite falsification evidence, not a proof of UEP-COVER.

## 4. Exact block-tree obstruction

The graph

```text
J??CAAoR@U?
```

has 11 vertices, 12 edges, girth 5, cycle rank 2, radius 3, eta 3,
and center `{10}`.  Its two cyclic blocks are

```text
{0,2,6,8,10},    {1,4,7,9,10},
```

and its two terminal bridges are `{3,8}` and `{5,9}`.  Thus its block-cut
tree consists of two 5-cycle branches meeting at the central cut vertex 10,
with one leaf attached inside each branch.

Deleting leaf 3 is bad and radius-nonincreasing:

```text
rad(G-3)=3, eta(G-3)=2,
C(G-3)-C(G)={4,7}.
```

Both 4 and 7 have 3 as their unique eccentric vertex in `G`.  Symmetrically,
deleting leaf 5 gives

```text
rad(G-5)=3, eta(G-5)=2,
C(G-5)-C(G)={2,6},
```

and both 2 and 6 have unique eccentric vertex 5.  The two new-center fibers
`{4,7}` and `{2,6}` are disjoint and occupy the opposite cyclic branches.
Thus the block tree permits exactly the pairwise-disjoint UEP allocation that
the local center lemma demands.

The graph is not eta-critical: the nonperipheral core deletions
`0,1,2,4,6,7` all preserve eta.  In particular, this record does not refute
W144-MIN.  It refutes the proposed intermediate inference that the UEP fibers
of the radius-nonincreasing bad deletions must clash merely because the graph
has two cyclic blocks.  Any complete proof must additionally force one of the
core deletions to have an uncovered realizer; that is precisely UEP-COVER.

The same record also refutes the selection rule that a good deletion can
always be chosen peripheral to an old center.  All its peripheral admissible
deletions are the two bad leaves.

## 5. Why the metric shortcut also stops

If `u in Q_v intersect B_G(x,e-1)`, the triangle inequality gives

```text
d_G(x,v) >= r-e+2.                                      (5.1)
```

It would therefore be enough to select an admissible radius-nonincreasing
`v` and a surviving realizer `x` with `d_G(x,v)<=r-e+1`.  This simpler
selection is false.  The exact graph

```text
I??ED`KI_
```

has order 10, girth 5, cycle rank 2, `r=e=3`, center `{6,9}`, and realizer
set `{3,5}`.  Every admissible radius-nonincreasing deletion `v` and every
surviving realizer `x` satisfy `d_G(x,v)>=2=r-e+2`.  Its good core deletions
instead work because their exact fibers `Q_v` are empty.  Hence the full
unique-eccentric-point condition cannot be replaced by a distance inequality.

Raw cardinality also does not force a contradiction: `FCR`o` has four
admissible radius-nonincreasing candidates and exactly four vertices outside
its center.  The required obstruction is coverage of every surviving
realizer by the correctly indexed fiber `Q_v`, not merely the number of
fibers.

## 6. First unsupported inference and stop

The valid block/center facts prove only the necessity (2.1) for each
radius-nonincreasing bad deletion.  Distinct `Q_v` are automatically
disjoint, but the graph `J??CAAoR@U?` shows that separate cyclic branches can
host those disjoint fibers without conflict.  Radius-increasing deletions do
not have UEP fibers at all.  No established block decomposition theorem
forces an admissible `v` and realizer `x` violating (2.1), and the
two-connected one-block case supplies no block-tree separation to exploit.

Therefore the first unsupported inference is exactly UEP-COVER.  Asserting
it would assert the load-bearing global deletion step.  This audit opens no
restricted selection hierarchy and stops without claiming the W144-MIN
characterization or W144.

## 7. Reproduction

From the repository root:

```text
python -m py_compile problems_external/wowii_144/attack_block_uep/verify_block_uep_obstruction.py problems_external/wowii_144/attack_block_uep/verify_uep_cover_audit.py
python problems_external/wowii_144/attack_block_uep/verify_block_uep_obstruction.py
python problems_external/wowii_144/attack_block_uep/verify_uep_cover_audit.py --min-n 5 --max-n 13
```

The final command exits zero exactly when no audited counterexample to
UEP-COVER is found.
