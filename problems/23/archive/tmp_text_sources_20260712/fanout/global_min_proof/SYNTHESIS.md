# global_min_proof synthesis

## Verdict

**FALSIFIED.** A global minimizer of the active-scoped
`scopedObligationScore` can have scoped Hall failure.

The R29 2943-vertex instance has an all-anchor row tuple with:

- globally minimum scoped score `23115`;
- owner shore `A={0,1,2}`;
- scoped demand `19953`;
- available-source neighborhood `19925`;
- exact Hall defect `28`.

The tuple changes all 676 selector rows from the old strict local cage.  The
old score `30811` therefore was not global; the coordinated trade lowers it by
`7696`.  This answers the lane's theorem with a falsifier, not a proof.

## Certificate chain

1. R29's reconstructed graph has 2943 vertices, 7039 blue edges, 1383 bad
   edges, and selector family shape `676 x (676 anchor + 4 local)`.
2. The d09 independent integer verifier checks all `339^2=114921` left/right
   local-count cells.  Its unique minimizing count cell is `(0,0)`, attained
   by all-anchor tuples, with exact scoped score `23115`.
3. The d05 independent owner-Hall reconstruction uses that same all-anchor
   tuple.  Its certificate contains 19925 distinct source triples and checks
   all eight shores of the three hub owners.  The maximum deficiency shore is
   `{0,1,2}` with `19953-19925=28`.
4. `lead/verify_r29_global_min_hall_falsifier.py` checks that d09's 676 chosen
   rows are exactly the constructor's 676 anchor rows, recomputes score 23115,
   checks the global-minimum certificate fields, and replays every Hall cut.

The exact cross-check output is
`lead/r29_global_min_hall_falsifier.json`.

## PHT conventions and verdict

`Omega` is the full Cartesian product of the complete shortest-row families.
Each literal row index occurs once; semantic duplicate rows are excluded by
the row-Nodup database contract.  Rigid families have size 1.  In R29,
`|Omega|=680^676`.

`S(eta)` is the cardinality of active collision halves plus active `HitNeed`
units.  Collision demands retain ordered-pair and half multiplicity.  A source
is one distinct `FreeHalf=(x,y,half)` with `x!=y` and pairCount zero.  Half zero
is removed on a scoped-reserved active edge.  Eligibility is same owner or
row companion, including both positive co-occurrences and exact `sigma>=0`.
The shore defect is demand cardinality minus the cardinality of the union of
these available sources.

PHT states

`sum_eta S(eta) <= |Omega| * (S(omega)-defect(A))`.

Exact tests:

- N10/11: 705/705 failures pass; minimum normalized residual `451/27`.
- Heavy N12: 4,801,067 tuples, 7,144 Hall failures, 7,144/7,144 pass; minimum
  residual `754312/100000 = 94289/12500` at graph6 `K?ABBBwerwBw`, choice
  `(7,4,6,4,8)`, shore owner `{8}`, score 18, defect 6.
- R29 global minimizer: PHT is impossible.  Global minimality gives
  `sum_eta S(eta) >= 680^676*23115`, while PHT would give at most
  `680^676*(23115-28)=680^676*23087`.  The exact contradiction gap is
  `28*680^676`.

Thus the N12 evidence is a finite-size pattern; PHT is not universal.

## Ten routes

1. **Augmenting cycles:** N5-9 exact gate found zero failing minima, but no
   Hall-to-simultaneous-trade construction.  Score-difference cycles cannot
   help without non-potential reduced costs.
2. **M-convexity:** false on graph6 `I?`fBO]]?` at N=10.  Exact exchange
   scores are `0+0 < 19+0`; orders 5-9 had no failure.
3. **Submodularity:** false on graph6 `I?`cjVo{?` at N=10.  A trade square has
   scores `F(empty)=F({i})=F({j})=0`, `F({i,j})=10`.
4. **Min-cost flow duality:** the exact prefix-state DAG is integral but its
   dual is tautological global optimality.  The compact activated-component
   LP has exact fractional witness `(flow,active)=(1,1/2)` and gap 2.
5. **Exchange graph:** exact score-difference weights telescope to zero on
   every cycle.  A two-bit toy has local deltas `+2,+2` and joint delta `-1`,
   so the viable object is an open path, not a negative score cycle.
6. **Component split:** established a component accounting identity for the
   older collision-plus-active-edge score, but did not derive the scoped
   theorem.  R29 supplies the terminal split and also the final falsifier.
7. **Owner-shore transport:** `AmortizedOwnerShore.lean` now compiles two
   endpoint bank lemmas with only the allowed axiom triple.  They are valid
   conditional arithmetic, but the universal trade premise is false at the
   certified R29 global minimizer.
8. **Valuated matroid:** unrestricted valuation exchange fails on the exact
   table `f(00)=1,f(01)=2,f(10)=2,f(11)=0`; the proposed delta-matroid family
   also fails symmetric exchange.
9. **Exact ILP:** gives an instance-wise formulation for the older
   `obligationScore`, not the active-scoped target.  It also found that the C5
   prototype omitted the mandatory `sigma>=0` row-companion filter.
10. **Separator topology:** produced no mathematical result because its
    worker's patch/process sandbox failed.  No claim from this route is used.

## Lean status

`lead/GlobalScopedMinimum.lean` proves, with no forbidden markers, that
unbounded global descent is equivalent to every global scoped minimizer
passing Hall.  Its allowed axioms are exactly `propext`,
`Classical.choice`, and `Quot.sound`.  R29 now falsifies both equivalent
statements.

`owner_shore_transport/AmortizedOwnerShore.lean` was repaired and rebuilt;
both endpoint theorems also use only the allowed axiom triple.

The remaining formal gap is to encode and kernel-check the 2943 counterexample
without `native_decide`: graph assumptions, complete row database, the
global-minimum lower bound, and the explicit Hall cut certificate are not yet
assembled into a sorry-free Lean counterexample theorem.

## Key hashes

- Cross-check JSON: `BACFCF5364AD7765365D43045145B8CB3BC9DB1A5A6E1DA636DADA154D161148`
- Cross-check script: `668F427042C4666E21EC41EE454136AEFCE789A8CBA8ADACF703853EF373347C`
- R29 best tuple: `93D5D64C55338186603B718B5D6BB162D907C4FC868CE276808E01822C395901`
- R29 global certificate: `5F61D53AF12B3ABB47E31841C31EE70A563E09C16FEC32EF744C1E07C0F5B63F`
- R29 Hall certificate: `DD1F1A2CFF0886E6EAF8ED6487D7A5F308E51446B2FFBC284D6CAAC3F797E1CE`
- N12 PHT result: `AE8B70250ABA6F7CF1ABB80EF026C3B252F48E7FEB0640D26B4C37FDDAC46303`
- N12 PHT script: `83A2C1E97B6C69B0EA876FF6E00ECA7B9BAABE0A2CAB23C2FEBA45C8A5119292`
- Global Lean wrapper: `5A6B8B41407061CAC35FA56A8A319A55C84DE670A04AA7B1F2E419FAD19CF03F`
- Amortized Lean endpoint: `0CDD6FB48CEB6144AC4CF3B168CFF49806F3ED1E6E3FBDD054B7D55E489AFA5C`
