# R42 graph-specific exclusion: first production invariant

## Exact exclusion of the proposed `t=3` active rotor window

The cut-tight active four-state geometry has a graph-level incidence cost
that is absent from the abstract rotor.

### Lemma (four-star bad-incidence bound)

Let `x,y,m,v` be the square vertices of a family-alternating rotor. Assume:

1. the four square edges and the four fixed spokes `xa,yb,mp,vq` are blue;
2. in four row states, respectively, each square edge is the unique missing
   square-support edge, while all four square vertices are `ActiveOwner`;
3. each square vertex is cut-tight, `sigma({z}) <= 1`;
4. the cut is maximum and the graph is triangle-free.

Then the graph has at least twelve bad edges.

Indeed, fix a square vertex `z` and use the state whose missing square edge is
opposite `z`. Both square edges incident with `z`, and its fixed spoke, are
selected-support edges. Since `z` is active, it has an active neighbour; that
neighbour is therefore external to these three vertices. Thus
`d_B(z) >= 4`. Cut-tightness gives

```text
d_M(z) >= d_B(z)-1 >= 3.
```

The bad-edge stars of `x,y,m,v` are pairwise disjoint. Adjacent square pairs
are already blue. Each opposite pair lies on one cut shore and has common
blue neighbours, so any edge between it would form a triangle. Hence the four
stars contain at least `4*3=12` distinct bad edges.

Consequently the R41 candidate window

```text
N=15, |M|=9, four cut-tight active rotor vertices
```

is empty. This is a proof, not a bounded search. It does not yet exclude
larger windows with at least twelve bad edges.

`CutTightActiveRotorIncidence.lean` compiles the exact finite incidence core:

```text
FourBadStars.twelve_le_ambient_card
FourBadStars.not_ambient_card_nine
three_le_badDegree_of_four_le_blueDegree_of_cutTight
```

Source SHA-256:
`3D7C194BEE84DF15C4CC5A73DD981AD69B7062BE95137DFF5BA24E66F604F242`.
The reported axioms are exactly `propext`, `Classical.choice`, and
`Quot.sound`; there is no `sorryAx` and no `native_decide`.

### Nonvacuous slack alternative

Dropping the cut-tight degree lower bounds gives a stronger graph-derived
alternative.  Let `s_z=dB(z)-dM(z)` be the nonnegative singleton cut loss at
the four square vertices.  The same opposite-state argument gives
`dB(z)>=4`, while pairwise disjointness gives

```text
|M| >= dM(x)+dM(y)+dM(m)+dM(v).
```

Consequently

```text
|M| + s_x+s_y+s_m+s_v >= 16.                 (RotorSlack)
```

For `|M|=9`, at least one square vertex has singleton loss at least two.
This is a genuine alternative, not the earlier cut-tight contradiction.  It
is compiled against the weaker `FourDisjointBadStars` carrier, which assumes
no star-cardinality lower bounds.  The first attempted formulation used the
stronger `FourBadStars` carrier and was discarded because it made the
nine-edge conclusion vacuous.

## Cut-tight star pigeonhole

`CutTightStarPigeonhole.lean` independently compiles the arithmetic core of
the R41 star theorem. For a blue-neighbour set `N(v)` of size at least two,
if

```text
2|N(v)| <= sigma(v) + sum_{z in N(v)} sigma(z),
sigma(v) <= 1,
```

then for every chosen active neighbour `x` there is another neighbour `y`
with `sigma(x)+sigma(y)>=2`. The proof is exact: otherwise every neighbour
has singleton loss at most one, contradicting the displayed star bound.
Triangle-freeness makes `xy` a nonedge. Thus `pairCount(x,y)=0` gives the
production-strength common-blue branch, while positive pair count enters the
complete-row detour branch.

Source SHA-256:
`DD6DA23C53E426F1EF10A7A1165508B2D519D562F99227B24BF19C823D860758`;
the only axioms are `propext`, `Classical.choice`, and `Quot.sound`.

## Live-surface correction

This directory excludes the literal abstract R42 `5/4` model and records two
conditional invariants.  It does **not** model the live R37 attachment
transition.  The exact N<=12 census in `r40_strong_probe_census` checks
7,600,710 genuine attachment detours and finds that `xv` is new while `vy` is
already selected support in every case.  Thus every live detour has one, not
two, genuinely new support edges, and

```text
supportDelta = 1 - 1[pairCount(m,x)=1] - 1[pairCount(m,y)=1].
```

The observed deltas are `-1/0/+1`; support monotonicity is false.  The 5/4
parity and P1/P3 lemmas below remain valid facts, but they do not exclude the
current four-state family-alternating rotor.  `search_outer_pair_exposure.py`
is retained only as a stronger-premise diagnostic and its interrupted N<=12
run produced no accepted result.

## Verdict

The exact abstract `5 obligations / 4 usable keys / defect 1` countermodel in
`r42_source_swap_proof` cannot itself arise from the production collision
carrier.  The first violated invariant is **physical-half closure**:

```text
ActiveCollisionHalf(G,c,omega)
  ~= ActiveCollisionStem(G,c,omega) x Fin 2.
```

`ActiveOwner` depends only on the collision owner, so active-scope filtering
keeps or removes both physical halves together.  Hence the complete production
collision-obligation set has even cardinality and in particular cannot have
cardinality five.

The same conclusion applies to the Hall core used by the production relation.
Every P1/P2/P3/P4/P5/common-blue arc depends on the obligation owner, not on
its `other/copy/half` fields.  If a Hall shore contains one obligation at an
owner, adjoining the rest of that owner's fiber does not enlarge the source
neighborhood and cannot decrease deficiency.  A maximum-deficiency shore may
therefore be chosen as a union of complete owner fibers; every such collision
fiber is even.  In particular, a saturated core with exactly four reachable
sources cannot have unit defect by the abstract `5-4=1` mechanism.

This is a precise exclusion of the displayed abstract model, not a proof of
`NoPositiveDefectSourceSwapRotor`.  A real analogue may have six collision
obligations, a persistent fifth usable source, or a Hall-deficient proper
shore of odd cardinality.  Those possibilities remain open.

`check_even_analogue.py` confirms that this warning is load-bearing.  Three
collision stems give six physical-half obligations.  Four source keys swap
between the two states and one key persists; the exact all-to-all matching has
`6P5=720` optima per state and constant defect one.  Thus parity removes the
literal R42 toy but leaves a parity-corrected abstract rotor.  Excluding that
object genuinely requires complete-row/max-cut geometry.

## Minimal one-owner parity-corrected rotor

The smallest one-owner realization of the 6/5 survivor is nevertheless
excluded by the displayed cut.  If the owner's collision demand six comes
from exactly two selected rows, the identity

```text
D_o = 2(5 r_o - |Comp(o)|)
```

forces `r_o=2` and `|Comp(o)|=7`; the two five-vertex rows share exactly the
three vertices `{o,a,b}`.  Eligibility in both rotor states requires the owner
to see `m,v,x,y`.  Turnover freeness forbids a row from containing one of
`m,v` together with one of `x,y`, so the rows must have vertex sets

```text
{o,a,b,m,v}  and  {o,a,b,x,y}.
```

The square puts `m,v` on one cut shore and `x,y` on the other.  If `k` of the
shared triple lie on the first shore, alternation of the first row requires
`k+2` to be 2 or 3, hence `k<=1`; alternation of the second requires `k` to be
2 or 3, hence `k>=2`.  Contradiction.

This excludes the minimal **one-owner, two-row** 6/5 repair.  It does not yet
exclude six obligations split among several owners, owners supported by three
or four rows, or background rows that add persistent sources and cover cross
pairs.

## Owner-filter consequence

For a support-constant target transition, the four gained usable keys are the
half-one orientations of the active blue edges `mx` and `my`:

```text
(m,x,1), (x,m,1), (m,y,1), (y,m,1).
```

Triangle-freeness rules out common-blue eligibility for either active-edge
base.  Their endpoints are selected and active, so the production outside and
quiescent component relations P4/P5 do not apply.  Thus only P1/P3 remain.
An obligation eligible for all four keys cannot be owned by `m`, `x`, or `y`:
turnover freeness makes the reverse orientation fail P3.  It must have an
external owner `o` satisfying

```text
pairCount(o,m)>0, pairCount(o,x)>0, pairCount(o,y)>0.
```

The exact finite audit `check_owner_filter.py` exhausts this four-owner,
three-incidence implication.  Therefore the abstract declaration that all
five obligations see all four keys silently assumes a common external
row-companion owner and omits every additional P1/P3 source forced by that
owner's complete selected-row companion set.

## Exact artifacts

- `ActiveCollisionHalfParity.lean` proves the production equivalence and the
  cardinality-five contradiction.  It also proves the exact P1/P3 turnover
  owner classification against `EligibleOwner`.
- `check_owner_filter.py` checks the P1/P3 owner classification with Boolean
  integer logic.
- `check_even_analogue.py` checks the sharp parity-corrected abstract survivor
  and prevents the parity lemma from being overinterpreted.
- `check_shared_triple_parity.py` exhausts all eight colorings of the shared
  triple; the arithmetic core is compiled as
  `shared_triple_opposite_pairs_impossible`.

The historical two-new-edge target below is superseded:

```text
NoPositiveDefectEvenSourceSwapRotor:
  exclude a real source-swap SCC after enforcing half-paired collision stems,
  owner-derived six-relation eligibility, and every companion source supplied
  by the complete selected-row database.
```

A bounded no-hit would not prove this target.

The current target is:

```text
NoPositiveDefectLiveAlternatingRotor:
  exclude a positive-defect four-state family-alternating attachment rotor
  using the one-new-edge support identity, even owner fibers, complete rows,
  and the production six-relation eligibility ledger.
```

## Live N=78 graft evaluation

`evaluate_n78_live_rotor.py` imports the independently checked R40 N=78
builder, reconstructs all four family-alternating states, builds the exact
P1/P2/P3/P4/P5 relation, and runs the component-coherent collision matcher.
The result is

```text
state collision demand/matched/defect/min owner margin
0     264 / 264 / 0 / 183
1     180 / 180 / 0 / 207
2     180 / 180 / 0 / 207
3     264 / 264 / 0 / 183
```

Payload `n78_live_rotor.json` has canonical SHA-256
`743326e6403fb2f7e5a1f564e2d005be96769ed75a61508414c03f1f011ff643`.
This exact graft collapses far before an SCC obstruction: P1/source
proliferation leaves every owner with a large positive reach margin.

The surviving real-cage shape must therefore be simultaneously cut-tight,
P1-starved, support-overlapping, and closed under the one-new-edge alternating
row transitions.  No such positive-defect cage is currently known.

## Independent R44 live-graft replay

The R44 family-alternating graft battery was replayed with exactly eight
workers.  The independent verifier recomputed both embedded canonical hashes
and compared the original and replay payloads after removing only the two
worker-count fields and each payload's own hash.  The normalized payloads are
identical, with semantic SHA-256

```text
799a50aa5d03bfbc42b4e46c5895763492c306ae68ed36e89815539fef1c914d
```

The exact verdict is `112 ACTIVE_PIN_REJECT`, `8 STRUCTURAL_REJECT`, and
`8 FULL_GRAPH_EVALUATED`; every fully evaluated graph has minimum production
collision defect zero and there are no hit SCCs.  Replay file SHA-256:

```text
af6f0e5348396d17436d58cf18af52d8235e499b1577c172872029ed21d6b5cd
```

This is a bounded no-hit and is not used as a proof outside the enumerated
graft family.

## High-slack square source-or-detour alternative

The quantitative escape has a graph-facing continuation.  Assume the same
fully active four-state rotor and let `z` be a square vertex with
`sigma({z})>=2`.  Choose a square neighbour `u` and the state in which `zu`
is the unique missing square-support edge.  The opposite rotor state, in
which no missing square edge is incident with `u`, forces an active neighbour
`w` of `u` outside its two square neighbours and fixed spoke.  Because only
the two central row families change, `uw` is active in every rotor state.
Thus `uz` and `uw` are both active in the chosen state.

Triangle-freeness makes `zw` a nonedge.  Maximum-cut optimality gives
`sigma({w})>=0`, and nonadjacent singleton switches add, so

```text
sigma({z,w}) = sigma({z}) + sigma({w}) >= 2.          (StrongPair)
```

There are now exactly two cases.

1. If `pairCount(z,w)=0`, both orientations and both physical halves are
   free.  The common blue owner `u` and `(StrongPair)` give a literal
   production P2/common-blue terminal; triangle-freeness excludes an active
   reservation.
2. If `pairCount(z,w)>0`, a selected shortest row contains `z,w`.  Their
   distance on that row is exactly two: distance one would make the triangle
   `z-u-w`, while distance greater than two is shortened by the blue path
   `z-u-w`.  The owner `u` is absent from the row because both incident edges
   are active/off-support.  Replacing the intervening row vertex by `u`
   therefore gives another checked shortest row, and completeness includes
   it.  This is a genuine two-active-edge detour, not one of the live
   one-new/one-supported rotor transitions.

Hence the nine-bad-edge fully active rotor necessarily exposes a production
P2 terminal or an additional two-active-edge row move.  The remaining
load-bearing step is matching-theoretic: prove that after exact common-blue
edge deductions the terminal is unused on a deficient shore, or that the
additional row move is nonincreasing in canonical defect/rank.  The present
lemma does not assume either conclusion.

The signed identity in `(StrongPair)` is kernel-compiled in
`SingletonPairSigma.lean`.  For a checked literal graph and a nonedge `uv`, it
proves

```text
sigma([u,v]) = sigma([u]) + sigma([v])
```

by separately adding the blue and bad boundary filters.  The same module now
also proves that two distinct blue neighbours are nonadjacent in a
triangle-free graph, that maximum-cut singleton loss is nonnegative, and the
combined production threshold

```text
sigma([left]) >= 2 -> sigma([left,right]) >= 2.
```

Source SHA-256 is
`E4060BCC9B8B92DC0F65D7C4022BF2D02A7E172C9210E3E5EE10B6E273383793`;
the reported axioms are `propext` and `Quot.sound` only.

## Bad-star vertex-cover freeness

The proposed `t=3` incidence shortcut has a kernel-checked row-local core.
Let `v` and both endpoints `u,w` of a checked bad row lie on one cut shore.
Let `x,s` be distinct blue neighbours of `v`, with `vx` absent from that
row's selected path support.  Assume the bad row is covered by the closed bad
star of `v`:

```text
v=u or v=w or vu is bad or vw is bad.
```

Then the row cannot contain both `x` and `s`.  Both neighbours must occupy the
two opposite-shore positions 1 and 3.  If the row is incident with `v`,
checked-row inducedness makes `vx` a selected path edge, contradicting the
off-support premise.  Otherwise a bad-neighbour endpoint of `v` is blue
adjacent along the row to `x` or `s`, forming a triangle with `v`.

This is `BadStarCoverFreeness.bad_star_cover_row_impossible` in
`BadStarCoverFreeness.lean`, source SHA-256

```text
AFD944EA407A6FB29A9E005C4827B7E8AF9E12EDC7DCC532A9BD523E083AE253
```

It compiles with axioms exactly `propext`, `Classical.choice`, and
`Quot.sound`.

The K3,3 production adapter is now compiled too.  Define a closed-bad-star
database at `v` by requiring every bad record's endpoints to lie on `v`'s
shore and requiring every bad edge to be incident with `v` or one of its bad
neighbours.  Then

```text
CompleteShortestRowDB G c bads
+ ClosedBadStarDB G c bads v
+ TriangleFree G
+ blue(v,x), blue(v,s), x != s
+ vx not in selectedSupport(omega)
=> pairCount(omega,x,s)=0.
```

This is
`K33BadStarPairCountZero.pairCount_eq_zero_of_closedBadStar`.  Its proof opens
a positive `pairCount` into an actual selected checked row and applies the
row-local obstruction above.  The source is
`K33BadStarPairCountZero.lean`, SHA-256

```text
8A8E5C9C08877CEE02ED99FB9802A0E75C2B83BE4DA15EF137936ABC98F23E01
```

and compiles with axioms exactly `propext`, `Classical.choice`, and
`Quot.sound`.  This completely excludes the canonical K3,3 double-star
realization: every active/support star pair is free, so a fully covered star
does not exist.

There is one important scope caveat.  The authoritative abstract t=3 window
assumes an inclusion-minimal nine-bad/eight-support circuit but does not define
its shape to be K3,3.  The K3,3 adapter therefore closes the canonical cage,
not every abstract 9/8 shape.

## Shape-independent t=3 closure

The first production invariant violated by every t=3 balanced rotor is the
cardinality of the complete-row support union, not source turnover.  Let
`F*` be the union of all blue path edges in the complete shortest-row
database of the nine bad atoms.  The 9/8 circuit hypothesis is

```text
|F*| = 8.
```

A fully covered profile owner has one active star edge and two supported star
edges.  The two covered-pair detours belong to the complete database, so all
three distinct owner-star edges lie in `F*`; hence its `F*`-degree is at
least three.

For two rotating owners `v,m`, both are on the same cut shore and have a
common blue neighbour.  Thus `vm` is neither blue nor bad (a bad `vm` would
form a triangle), so their incident `F*` edge sets are disjoint and contribute
six edges.  Let `b0,b1,b2` be the three distinct bad neighbours of `v`, and
choose a checked length-four blue row from `v` to each `bi`.

* If one chosen row avoids `m`, its final three blue edges avoid both owners
  and are distinct.
* Otherwise every chosen row contains `m`.  Since `v,m,bi` lie on the same
  shore, alternation puts `m` at the middle position; it cannot be the final
  endpoint because then `vm` would be bad.  The three final edges `qi-bi` are
  distinct and avoid both owners.

Either way `F*` has three further edges, giving `|F*|>=9`, a contradiction.
For three rotating owners, their three incident triples are already pairwise
disjoint, again giving `|F*|>=9`.  Four owners were previously excluded by
the independent `|M|>=12` bad-star count, while zero or one owner cannot make
a nontrivial detour cycle.  Therefore the entire t=3 balanced live rotor is
empty for every 9/8 shape.

The exact finite incidence core is kernel-compiled in
`R43SupportIncidence.lean`.  It contains the requested declarations

```text
fullyCoveredLiveStar_fullSupportDegree_ge_three
TwoRotatingOwners.twoRotatingOwners_force_nine_supportEdges
ThreeRotatingOwners.threeRotatingOwners_force_nine_supportEdges
no_t3_balancedDeficiencyRotor
```

with source SHA-256

```text
6664967000F45660BD82C9EA9304942257248FBCA5BB88482C45F6397D184CEA
```

All four compile with axioms exactly `propext`, `Classical.choice`, and
`Quot.sound`; the forbidden-token scan is empty.  The module records the
finite support-incidence conclusion, while the two-case checked-row argument
above is the graph adapter producing its `external` triple.

This closes only the t=3/N=15/|M|=9 balanced-rotor window.  It does not prove
the full live-wall theorem for t>=4.  At t=4, `|F*|=15`; four owners are
excluded by incidence, three owners need one more external edge, and the
two-owner window remains the next graph-specific target.

## First t=4, k=2 reduction

Let `v,m` be the two rotating owners.  Their fully covered stars give two
disjoint four-edge incident subsets of `F*`.  For each owner's four distinct
bad neighbours, choose one checked length-four blue row.  The final edge of
each row avoids both owners: same-shore parity puts the other owner either at
the middle position or outside the row, and a bad-neighbour endpoint cannot
equal the other owner because `v,m` have a common blue neighbour.  The four
final edges for one owner are distinct because their same-shore endpoints are
distinct.  Thus each owner supplies a four-edge external tail family.

If the two tail families were disjoint, `F*` would contain

```text
4 + 4 + 4 + 4 = 16
```

edges, contradicting the t=4 cap `|F*|<=15`.  Therefore every surviving
t=4,k=2 cage has a support edge that is final for rows from both owners.  Cut
parity identifies the same-shore endpoint of that common edge uniquely, so
the two owners share a bad neighbour.  Together with their two square blue
neighbours, the survivor contains the graph-theoretic `K_{2,3}` core

```text
{v,m} -- {x,y,b},
```

where the `x,y` edges are blue and the `b` edges are bad.

The finite cardinality statement is kernel-compiled as
`K2TailIncidence.exists_common_tail_of_support_card_le_fifteen` in
`R44K2TailOverlap.lean`, source SHA-256

```text
12DFB92724F36BEAC1F11EBA529023F0445893CA6E60376B09B2403C0E64066A
```

with axioms exactly `propext`, `Classical.choice`, and `Quot.sound`.  This is
a structural reduction, not a t=4 exclusion: the shared-bad-neighbour core
can exist in a triangle-free graph and now has to be attacked using complete
row families and the production Hall ledger.

Minimal-circuit dual Hall supplies the first such complete-family consequence.
For a minimal defect-one circuit, every nonempty support set `W` touches at
least `|W|+1` bad atoms.  Apply this to the union of the two four-edge owner
stars.  The eight bad atoms incident with the two owners touch those edges,
but they cannot be the whole incident family: there is a ninth bad atom,
incident with neither owner, whose complete row family uses an owner-star
edge.  Any checked row witnessing that incidence contains the owner internally
and therefore uses two owner-star edges.  Depending on the bad edge's shore,
the owner occurs at position 1, 2, or 3; it can never be an endpoint because
the atom is outside both bad stars.

The finite extraction is compiled as
`t4_two_owner_stars_have_external_atom` in `R44OwnerStarDualHall.lean`,
SHA-256

```text
A8D39A65198FD42B298A07C932805379C5262DBA870D7178C5E03DE874BB06D3
```

with axioms exactly `propext`, `Classical.choice`, and `Quot.sound`.  This
shows that the abstract even source-swap rotor is still missing a mandatory
external complete-row atom.  It does not yet prove that the atom creates a
globally unused production key: one atom may touch both owner stars through
different rows, so the exact P1/P3/P4/P5 eligibility effect remains open.

The row adapter is independently compiled as
`CheckedRowInternalOwner.internal_vertex_has_two_path_edges`: in an explicit
nodup five-row, any occurring vertex distinct from the two bad endpoints has
two distinct path neighbours and both normalized incident edges belong to the
row support.  Source SHA-256 is
`A815A9A13CE1E32DB1082FC5632EDAFAB4C15B1FF68D5857CF840A231E3B1315`;
its only reported axiom is `propext`.

## Exact limit of support-incidence arguments at t=4

The support constraints above do not themselves exclude the t=4 window.  The
artifact `t4_support_circuit_hit.json` gives an explicit 16-atom/15-support
family with:

* four fixed `v`-bad rows and four fixed `m`-bad rows;
* a common four-edge tail family, realizing the forced overlap;
* eight further four-edge atoms, including the dual-Hall external atoms;
* every support edge incident with at least two atoms;
* full deficiency one; and
* `|N(X)|>=|X|` for every one of the 65,534 nonempty proper atom subsets.

The canonical payload SHA-256 is

```text
5b386cd90b795bf1e6f8f174e21aa559e37c9f682e5dff373dae6bf74f3b9641
```

`verify_t4_support_circuit.py` independently recomputes that hash, all edge
degrees, the fixed shared-tail rows, and every proper-subset Hall inequality.
It reports 19 tight proper subsets and minimum support-edge degree two.

This is a complete falsifier to any proposed t=4 proof using only four-uniform
support sets, inclusion-minimal defect one, no-private-edge, owner-star
cardinality, shared tails, and dual strict Hall.  It is not a graph cage: the
eight added four-sets have not been realized as length-four paths in one
triangle-free graph, and no maximum cut, complete row database, active scope,
or production matching has been supplied.  The live frontier is therefore
the realizability/eligibility of this abstract support circuit, not another
support cardinality inequality.

## Exhaustive path-realizable t=4 exclusion

The graph-specific gate removes every abstract support survivor before the
matching ledger.  The exact census uses the following complete reduction.

1. `F*` is a connected simple bipartite graph with 15 edges.  The forced four
   blue square edges give a cycle, so `F*` is not a tree and has at most 15
   vertices.  Sixteen triangle-free bad edges require at least eight endpoint
   vertices by Mantel, so the complete support-vertex range is 8 through 15.
2. `geng -c -b n 15:15` generates all 153,978 unlabeled support graphs in
   that range.  Exactly 34 graphs/owner embeddings have two same-shore
   degree-four owners with at least two common blue neighbours, at least four
   distance-four same-shore candidates per owner, and a common distance-four
   candidate.
3. For each embedding, choose exactly four bad neighbours at each owner and
   eight further distance-four pairs.  Reject triangles.  For each bad atom,
   compute the union of all shortest four-edge paths.  Check full support,
   support-edge multiplicity at least two, and all sixteen deletion SDRs.
   The latter are equivalent to Hall on every proper atom subset.  Exactly
   576 atom circuits survive, on four 15-vertex support isomorphism types.
4. Inspect every complete shortest-row family, then enumerate all 16,288 row
   tuples.  No bad-atom family contains two rows of the live form

   ```text
   (a,x,m,y,b) and (a,x,v,y,b).
   ```

   Hence the required raw one-middle transition is absent in every circuit,
   independently of `r`, activity, coverage, or matching.  Additionally, no
   owner can have `r=4`: for every one of the 576 circuits, at least eight
   bad-atom families have the property that every shortest row contains `v`,
   and independently at least eight have the same property for `m`.  Thus
   every row choice satisfies

   ```text
   r(v) >= 8 and r(m) >= 8,
   ```

   contradicting the prescribed minimal-scalar t=4 profile requirement
   `r(v)=r(m)=4` before active
   degree, coverage, max-cut, or Hall-ledger checks are needed.

The stage counts are:

```text
support graphs                         153978
coarse owner embeddings                   34
bad-edge extra choices                 74920
triangle-free choices                   2299
full-union/multiplicity choices          862
minimal defect-one circuits              576
complete row tuples                    16288
fully covered owner profiles                0
middle-swap profile transitions             0
raw one-middle swaps                         0
```

Canonical artifacts:

```text
t4_support_graph_census.json    40f16a84559ace4827e366f152026f2b7868bdaed31ff9afb36184a29b48046d
t4_atom_circuit_census.json     302e04ef5ff14c78cbe9dc5800ac0226e730ed0baca123585dc6469a82d66652
t4_profile_transition_census    b464682b4142a9db2396dc39ac9a0ffd8ff638aba1b9270734667c8f0a543114
```

`verify_t4_profile_exclusion.py` independently reconstructs every complete
row family in the 576 emitted circuits and obtains the forced-through-owner
histogram, identically for `v` and `m`:

```text
r_min = 8: 255 circuits
r_min = 9: 193
r_min = 10: 101
r_min = 11: 26
r_min = 12: 1
```

The same verifier checks every pair of rows in every bad family and obtains
zero raw `v<->m` middle swaps.  This is therefore an exhaustive finite
exclusion of the unconditional t=4 two-owner live rotor, not a bounded no-hit.
It does not use the erroneous R44 claim that there are
at most four vertices outside `F*`; in fact all 576 circuits have 15 support
vertices and hence five ambient vertices outside.  The contradiction occurs
inside the complete row database, so no assumption about how those five
vertices repair max-cut is needed.

Two independent implementations replay the enumeration boundary:

* `verify_t4_support_census.py` uses
  `networkx.from_graph6_bytes`, NetworkX bipartition, and NetworkX all-pairs
  distances.  It independently reruns `geng` without residue splitting and
  exactly reproduces 153,978 graphs, 34 candidate graphs, all 34 owner
  embeddings, and the complete candidate payload set.
* `verify_t4_atom_census.py` uses `networkx.all_shortest_paths` and
  `networkx.bipartite.maximum_matching`.  It independently reproduces every
  stage count and exactly the same set of 576 atom circuits.

Thus neither the primary graph6 decoder, the bitmask shortest-path footprint,
nor the custom augmenting-path SDR checker is a single point of acceptance.

Audit note: the first `profileMiddleTransitions=0` count was conditioned on
the full profile predicate and therefore on `r=4`; that first interpretation
was retracted.  The corrected gate quantifies directly over every pair of rows
in every complete family and finds zero raw middle swaps.  This corrected
statement is r-independent and is the actual unconditional exclusion.

## Production row invariant behind the t=4 exclusion

The first production invariant violated by the live t=4 rotor can be stated
without any matching terminology.  If two checked shortest rows have the
live middle-swap form

```text
(a,x,m,y,b)  and  (a,x,v,y,b),
```

then `x,y` are distinct common blue neighbours of `v,m`; `a` is a blue
neighbour of `x` outside `{v,m}`; `b` is a blue neighbour of `y` outside
`{v,m}`; and `a,b` are the distinct bad endpoints of both shortest rows.
Consequently the support graph contains the cross-outer distance-four pair
`a,b`, witnessed by both displayed paths.

The row-local part is kernel-compiled as

```text
LiveMiddleSwapCrossOuter.live_middle_swap_has_cross_outer
```

in `LiveMiddleSwapCrossOuter.lean`, SHA-256

```text
3DFF7897F65112F4F8177B84AB28F631C85BC6F50F7F5D920ED06F033B7F9275
```

with axioms exactly `propext` and `Quot.sound`.

`verify_t4_cross_outer_exclusion.py` independently applies this necessary
condition at graph level.  The 576 complete atom circuits project onto four
support-graph/owner types, with multiplicities `180,190,190,16`.  NetworkX
decodes each graph6 support and exhausts every ordered choice of common
neighbours `x,y` and outer neighbours `a,b`.  All four candidate sets are
empty, so the total number of live cross-outer pairs is zero.  The artifact
`t4_cross_outer_exclusion.json` has canonical SHA-256

```text
79db75b95e8401064f1b6159bb980ee0149f0fb3a602a607306a7f0e501a5d49
```

and verdict `PASS_NO_LIVE_MIDDLE_SWAP_GEOMETRY`.  This is not a generic
bounded no-hit: it is the final finite check after the complete 8--15 vertex,
15-support-edge, 16-atom minimal-circuit enumeration above.  It uses neither
two-new-edge turnover nor support monotonicity.

## t=5 path-realizable countermodel to the t=4 invariant

The t=4 cross-outer obstruction does not extend to t=5.  The rooted exact
CP-SAT harness `rooted_t5_support_cp_sat.py` fixes the live rows

```text
(a,x,v,y,b) and (a,x,m,y,b),
```

two degree-five owners, and a shared distance-four bad neighbour.  It then
requires a connected 24-edge bipartite support graph and selects 25 distinct
distance-four bad atoms.  The selected bad graph is triangle-free; every
support edge has multiplicity at least two; and, for each selected atom, the
other 24 atoms have an explicit SDR onto all 24 support edges.

At bipartition sizes `10+8`, the second support graph produced an exact hit:

```text
support vertices                         18
support edges                            24
available distance-four atoms            29
selected triangle-free bad atoms         25
minimum support-edge multiplicity         3
deletion SDR sizes                 24 (all 25)
live middle-swap rows                      2
```

Payload `t5_rooted_smoke_l10_r8.json` has canonical SHA-256

```text
a8eeca69b1b674deeff88bf2e6b70cf5750e0781d626f7c2fd56e0685a7719c7
```

and graph6 support

```text
Q???????F?Y?E{d?KOE??B?B???
```

`verify_t5_rooted_hit.py` independently recomputes every shortest row and
footprint with NetworkX, checks the full graph for triangles, and recomputes
all 25 deletion matchings.  It returns
`PASS_PATH_REALIZABLE_T5_MINIMAL_CIRCUIT`, canonical SHA-256

```text
65bc9f52a2bff779184068136d64996c7abdfa78a03c1aa6135cf73bedff1586
```

This is a complete falsifier to extending the t=4 exclusion using only the
support graph, complete shortest rows, triangle-freeness, owner degrees,
shared bad neighbour, and transversal-circuit axioms.  It is **not** a real
production cage: on the 18 displayed vertices the designated cut has 24
blue edges, whereas exact exhaustive max-cut has 45 of the 49 graph edges.
The seven ambient vertices available at `N=25` have not been attached, and
positive scope, P1--P5 eligibility, and the neutral four-state ledger have
not been realized.

More importantly, `check_t5_two_owner_profiles.py` shows that this circuit
does not realize the fully covered selected-row profile assumed by the live
window.  It chooses one row per atom and exhausts all five possible active
neighbours at each owner under the exact requirements `r(owner)=5`, one
incident active edge, all other star edges selected, and every active/support
pair covered by a selected row.  Neither owner has such a profile even
individually, hence no simultaneous two-owner state exists.  The profile
artifact has canonical SHA-256

```text
fda5e079dffa0fd6c480c4a1814c02ea900bd939fd737eff50afdf4da3630540
```

Thus the proposed `no_t5_triangleFree_twoOwnerCoveredCircuit` lemma is not
falsified by this hit.  The hit only proves that bare support incidence,
complete rows, triangle-freeness, owner degrees, and a raw middle swap are
insufficient; the fully-covered tuple condition is already load-bearing.

### Exact ambient verdict for this countermodel

The displayed support countermodel cannot be completed to a maximum-cut cage
while keeping the 25-atom complete row database unchanged.
`extend_t5_hit_maxcut.py` assigns the seven ambient vertices to the two cut
shores in all eight possible split sizes.  For each split it allows **every**
missing cross-shore blue edge, including edges between two old support
vertices.  It imposes only mixed-triangle exclusions; connectivity is
deliberately omitted, so the model is a superset of all connected blue
extensions.  Same-shore additions are excluded because they would be new bad
edges and violate the exact `|M|=25` window.

Whenever a candidate creates a new length-four row for a selected bad atom,
the script emits the concrete path clause forbidding all new edges of that
row simultaneously.  Whenever the designated cut is not maximum, an exact
minimum-sigma switch is separated.  The decisive switches cross 24 bad edges
and only three fixed support edges, requiring 21 added blue crossings.
After 21--63 valid row-path clauses and one or two switch inequalities,
CP-SAT proves every shore split infeasible.  No iteration limit is reached.

The unrestricted master artifact is
`t5_rooted_maxcut_extension_full.json`, canonical SHA-256

```text
7896ae9480673fa850f86a35b433cd04dc5826b618f665e13a1f4b021c212795
```

`verify_t5_maxcut_extension_unsat.py` independently validates every emitted
path witness, reconstructs all triangle clauses and switch cardinality
constraints, and solves the resulting Boolean formulas with CaDiCaL 1.9.5.
All eight split formulas are UNSAT; their sizes range from 468 variables /
2,420 clauses to 1,054 variables / 6,779 clauses.  Its artifact has canonical
SHA-256

```text
ada85054d6a4d5b2848b5c92d9965d6e07d02d3b937daa810a6309c2ba9d969a
```

and verdict `PASS_ALL_EIGHT_SPLITS_UNSAT`.

Therefore this exact t=5 support/row countermodel has two independently
checked failures, in the following order:

1. it does not admit even one fully covered owner profile with `r=5`;
2. even after that profile requirement is dropped, complete-row preservation
   is incompatible with maximum-cut domination for every ambient split.

The first production invariant it violates is the fully-covered selected-row
condition, not maximum-cut.  This is still a one-candidate exclusion, not the
general t=5 theorem.

## Exact falsifier to the R48 triangle-forcing profile lemma

The stronger proposed support statement

```text
triangle-free 25/24 circuit + a degree-five local owner profile
  -> a triangle in the selected atom graph
```

is false.  The R48 four-number classifier was encoded directly in
`rooted_t5_support_cp_sat.py`: for one owner and one chosen active neighbour it
requires `Forced(v)=Inc(v)`, no incident atom with an empty nonactive first
step, a size-four first-step matching, and a size-four owner-avoiding coverage
matching.  With the shared-bad-neighbour restriction removed, support number
298 in the `9+9` rooted order has classifier vector

```text
(e_forced, i_step, d_step, d_cov) = (0,0,0,0).
```

The exact source artifact is `t5_classifier_v_l9_r9_1000.json`, canonical
SHA-256

```text
c1d474d7dc295ae99cf93d11f515fc3db4bd622ebf75b125c16dfee7472afec1
```

and support graph6

```text
Q??????wE_[?EGs?D_@A?C_B???
```

`verify_t5_local_classifier_hit.py` is an independent NetworkX replay.  It
recomputes the complete shortest-row database, all 25 exact distance-four
atoms, every deletion SDR, support multiplicities, and the triangle count.  It
also reconstructs one row choice from the two classifier matchings and checks

```text
d_B(v)=d_M(v)=5,
r(v)=5,
exactly one v-star edge is absent from selected support,
the active endpoint occurs in a selected row,
all four active/support pairs have positive pairCount.
```

The selected atom graph is triangle-free, every deletion SDR has size 24, and
the minimum complete-support multiplicity is two.  The verification artifact
`t5_classifier_v_l9_r9_hit_verification.json` has canonical SHA-256

```text
48ce163829eeb916ac5fd489b8e3e8464a576d122721ea9557cc29430d91f4f9
```

This is not a production cage.  The next graph-derived invariant fails
exactly: the active component at the owner is the two-vertex set `{0,17}` and
contains the endpoints of no selected bad atom.  A second CP-SAT gate varies
all 25 row choices and asks for two active-edge flows from the owner to both
endpoints of one selected bad atom; it is exact `INFEASIBLE`.  Its artifact
`t5_classifier_v_l9_r9_active_scope.json` has canonical SHA-256

```text
f5c0cbcad47419b0e88faeaf17a754bae9e767176fee3e2f2e8185b86e97190c
```

The displayed cut also fails maximum-cut domination, with minimum switch
sigma `-20`.  Consequently the R48 triangle-forcing lemma is refuted, while
the weaker live target remains:

```text
t5_triangleFree_localProfile_is_scopeVacuous:
  every triangle-free 25/24 local profile has owner outside every
  bad-containing active component.
```

The first 350 no-shared `9+9` supports have no positive-scope classifier hit
under the staged exact row/flow gate (`f0cd4403eb5e898186c4d1aa808da9374e0c0723ff952465025d233d7d01807d`).
That last statement is only a bounded no-hit, not a proof of the fallback.

### Exact degree-two scope filter

One stratum of the fallback is excluded without enumeration.  Let `v` have
exactly one incident active edge `vx`, assume `x` occurs in a selected row,
and suppose the blue degree of `x` is two.  The selected row containing `x`
uses a blue edge at `x`; it cannot use `vx`, since `vx` is active and hence
absent from selected support.  Therefore the unique other blue edge at `x`
is selected.  Every other blue edge at `v` is selected by the degree-one
active-star hypothesis.  The active component of `v` is consequently exactly
`{v,x}`.  No selected bad atom has those two vertices as endpoints because
`vx` is already a blue edge, and loops are excluded.  Thus `v` is not an
`ActiveOwner`.

In particular every positive-scope t=5 local-profile falsifier has

```text
d_B(x) >= 3
```

at its active endpoint.  The long staged sweep uses this as a necessary
filter; it is not an additional conjectural assumption.

### Live-active zero-vector countermodel and its tail blanket

Fixing the classifier's active neighbour to the actual rooted middle-swap
vertex still does not restore a support-level contradiction.  At support
number 264 of the no-shared `9+9` run, the exact circuit selector finds a
triangle-free zero-vector profile at the rooted active vertex `x=9`:

```text
t5_live_x_classifier_v_l9_r9_5000.json
SHA-256 6595501f532577c3475d29e2a3c7e9f318debecd5e1014d0793e1b462d07494f
graph6  Q??????wE_Bws?s?DCD??@?@???
```

The selected atom `(2,3)` has complete middle-swap rows

```text
(2,9,0,y,3)  <->  (2,9,1,y,3),   y in {10,12,13}.
```

Thus the active edge is genuinely on the live attachment geometry.  The
independent verifier again obtains a triangle-free 25/24 minimal circuit and
constructs an exact `r(v)=5` local-profile tuple.  Its artifact SHA-256 is

```text
d9e7341330eb9b816c7147d726405676d9e685b6f2ff64f46d1df80cae29e1b4
```

This stronger countermodel still violates `ActiveOwner`.  CP-SAT over every
row choice is infeasible for positive active scope (`79471ef0...`), and an
independent CaDiCaL encoding is UNSAT on 1,645 variables and 5,140 clauses:

```text
c7fbcc70e59246681f448eea3a8c694ffe556ab63384fd53507b071cc010f059
```

The exact local reason is a two-edge tail blanket.  Here

```text
N_B(9) = {0,1,2},
```

with `09` the active owner edge.  Under the full local-profile constraints,
forcing `19` absent is UNSAT, and forcing `29` absent is independently UNSAT.
Hence every profile tuple selects the whole cut `delta(9)\{09}` and the
active component is exactly `{0,9}`.  The CaDiCaL tail artifact has SHA-256

```text
3720a8c272ab4c8de1923615d22d187c62b9a051d9fd2530d327cfb3ffb96041
```

The canonical source row uses the live orientation through owner `1` with
`y=13`.  Replacing it by the row through owner `0` leaves both edges `19` and
`1-13` selected elsewhere, so no target owner activates.  The candidate also
fails max-cut with minimum switch sigma `-21`.  It therefore falsifies both
the generic and live-active support-only triangle lemmas, but not the
production rotor: its first failure is positive active scope.

### Scope correction and graph-specific exclusion of the live-x countermodel

The preceding intrinsic-scope sentence is only a statement about the fixed
24-edge support graph `F*`.  It is not by itself a production exclusion:
an ambient blue edge can enlarge the active component without belonging to
any selected shortest row.  The production gate must therefore quantify over
all row-safe ambient blue extensions.

For this exact live-x source, that stronger gate is empty.  Let `F*` and `M*`
be the fixed 24 blue support edges and 25 same-shore bad edges encoded by

```text
t5_live_x_classifier_v_l9_r9_5000.json
canonical SHA-256 6595501f532577c3475d29e2a3c7e9f318debecd5e1014d0793e1b462d07494f.
```

Add seven vertices and place any `k` of them on the old left shore and the
other `7-k` on the old right shore.  Permit every missing cross-shore blue
edge, including edges between two old vertices.  There is no resulting blue
edge set `B` satisfying all three conditions:

1. `F* subset B`, and the full graph `(B union M*)` is triangle-free;
2. no selected bad edge acquires a new length-four blue row outside its
   original complete shortest-row footprint;
3. the displayed cut is maximum, equivalently
   `|delta_B(W)| >= |delta_M*(W)|` for every vertex set `W`.

Connectivity is not assumed, so this excludes a superset of production
extensions.  The exact extension artifact

```text
t5_live_x_maxcut_extension.json
canonical SHA-256 6bd2c4e89c9912cb3acbf76938436f5acadbc204bcec5b7f0bbf60fcbf7989bf
```

is independently rebuilt as Boolean CNF by
`verify_t5_maxcut_extension_unsat.py`.  CaDiCaL 1.9.5 returns UNSAT for all
eight shore splits.  The independent verification artifact has canonical
SHA-256

```text
8618fe18d5539b7fdc702c9700c121e0b443d27eadec3935821ffd9d280b16a3
```

and verdict `PASS_ALL_EIGHT_SPLITS_UNSAT`.

The obstruction has a small fixed switch.  Put

```text
S = {4,5,6,7,8,11,14,16}.
```

It crosses 23 edges of `M*` and only two edges of `F*`.  Maximum-cut
domination therefore requires at least 21 added blue edges crossing `S`.
The exact triangle/row-safe capacities are:

```text
k = number of new vertices on the old left shore

k                  0      1   2   3   4   5   6   7
capacity across S  21     19  17  15  13  11   9   7
required           21     21  21  21  21  21  21  21
```

For `k=1,...,7`, the single switch already contradicts maximum-cut.  At
`k=0`, the second switch `S union {18,...,24}` also separately requires 21;
although each switch alone has capacity 21, their exact joint safe capacity
is only 28, below the required sum 42.

`analyze_t5_live_x_switch_capacity.py` independently reconstructs every
mixed-triangle clause and validates every forbidden new-row witness before
performing exact cardinality SAT.  Its source SHA-256 is

```text
C45C1B47CB0AFC32E84E5E44209FF141474DF077E18F3ABAE37F4FFF6203913E
```

and `t5_live_x_switch_capacity.json` has canonical SHA-256

```text
ddc0376f8de231fa8f86753aac6340e4aa5ca7930b9841b40dbd0f69342524ba.
```

Thus the first production invariant violated by this live-x abstract
countermodel is the R47 graph-level gate
`TriangleFreeRowPreservingMaximumCutExtension` (equivalently
`CheapGeometry`).  The intrinsic active-scope failure is diagnostically true
but is not the production proof.  This is an exact exclusion of this fixed
countermodel, not an exhaustive proof for every t=5 local-profile circuit.
