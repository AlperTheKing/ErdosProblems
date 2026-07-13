Referee verdict: **UNDEFINED as a FullBank residual; TRUE only as an ActiveScoped/FreeHalf residual.** The four-pattern defect `28` cannot currently be promoted to either a FullBank failure or a FullBank absorption claim.

Independent reconstruction passed:

- `N=2943`, `|B|=7039`, `|M|=1383`, `|E|=8422`.
- Triangle-free; every bad edge has blue distance exactly `4`.
- Shortest-row histogram: `707×1 + 676×680 = 460387`.
- All-anchor selected tuple has `1383` rows.
- Canonical incidence SHA-256: `7f3c69376e074adefe505f709643bdf14a9a5c5b18e9816d8b88e24d7b59f087`.

Exact ActiveScoped replay:

- Hub shore `A={0,1,2}`.
- Per hub: collision-half demand `6650`, HitNeed `1`, total `6651`.
- Total demand `19953 = 19950+3`.
- Sources: sameFirst `17325`; rowCompanion-only `2600`; overlap `0`.
- Deduplicated reach `19925`; defect `28`.
- All other seven shores have nonpositive defect.
- All `459680` selector rows were checked; none touches a hub. Demand and reach are selector-invariant.

Adversarial findings:

- **Unit mismatch:** `28` is in Hall half-slot units. `TypedFullBankSources.hallCapQ = capQ/25`, so absorbing it requires `capQ ≥ 700`, not capacity `28`.
- **Door:** `19925` graph-derived FreeHalf triples are not compiled Door tokens. No R29 `OwnEdgeDoorSourceData.Checked` plus wall-adapter instantiation exists. Admissible compiled R29 Door capacity: `0`.
- **vertexSlack:** natural half-singleton reconstruction fails at vertices `0,1,2,55`. At each hub, `T(v)=5·676=3380>N`, residual capacity is `0`, but off-support load is `1/2`. Vertex `55` has `T=3385`, capacity `0`, load `2`. Thus this source class cannot absorb the defect under that core.
- **c5Base:** no independent concrete provider. Relabelling FreeHalf keys as c5Base gives the same `19925` keys; summing both would duplicate capacity to `39850`. Additional justified capacity: `0`.
- **prune:** all-anchor is the certified global scoped-score minimizer `23115`; selector rewrites provide no strict vertex-set descendant or ledger split. Concrete prune capacity: `0`.
- **Graph semantics:** the FullBank Lean APIs type abstract tokens, capacities, and adapters but do not construct legal R29 token incidence from the graph. Consequently the exact FullBank flow instantiated from current providers has zero usable tokens. This is missing semantics, not a certified negative FullBank cut.
- **Core choice:** using the entire selected union `C` gives `|C|=2127`, support `|F|=2797`, off-support `|O|=4242`; it exposes the four overloaded vertices above. Any smaller alternative core must be separately justified and must preserve coverage, ownership, and no-double-spend. No such provider exists.
- **No false source survives:** Door, vertexSlack, c5Base, and prune each fail either eligibility, capacity, uniqueness, or graph-to-token construction.

Replay identities:

- Builder: `5d29b1d6e35957405c53176fab1fb21660d727cb334a1e20462eb5ebe36678f6`
- Hall replay result: `548d0ca4801165ce216f60b4cd2e504600d2928307e9e1fe36a9508b97d83d73`
- Selector-demand result: `d7d657519b922e2a9e7ef7c6f8cdefef33b5df35c5a7febc065595f61eda44e8`
- FullBank-to-surplus Lean source: `f4806742bdff61e0e3a15637c25d796b0abf0803936aaabc82a77de2a1da40cd`
- Typed sources Lean source: `6ab920d11b983848a46d95e9477a4bf4b1b948992a3aef5f158aff4dc1820fbd`

Exact claim permitted by the evidence:

> R29 has a selector-invariant 28-unit defect in the ActiveScoped ordered-FreeHalf matcher. Current implemented FullBank APIs neither absorb nor refute that defect because no complete graph-derived R29 provider exists.

Therefore, calling the four-pattern defect a “FullBank residual” is presently false as a statement of implementation status; calling it “not a FullBank residual” is also unproved.