# R32 join-5886 independent exact gate

## Scope

This lane independently reconstructs the doubled R29 cage and tests the
component-ownership issue for static Pattern 5.  It uses integers only.  It
does not prove or claim the main Erdos #23 theorem.

The checker does not import:

- `doubled_cage_falsifier.py`;
- `r29_lead_gate.py`;
- `_claude_r29_pattern5_gate.py`.

Instead, `independent_gate.py` rebuilds the R29 graph from its five explicit
edge classes, duplicates it, complements the displayed cut on the second
copy, and adds the blue bridge `(3,2946)`.

## Integrity and identity

The source `MANIFEST.sha256` in
`tmp/fanout/common_blue_universal/pattern5_static_token/` has seven entries.
All seven hashes match their current files.  Its own SHA-256 is
`03d6e7277339cd4832856a9f454a5bea448ee8ebfac621bc09a0677b8837403c`.

The standalone base reconstruction has canonical SHA-256
`fc4f3ab94bed810669976b1fdb21743fdd4ebe57eea15ef52afcfc2165e2fb1f`,
equal to the R29 lead artifact.  The doubled all-anchor instance has canonical
SHA-256
`6aa2958727dda2a1323e43ed8b9a0331b12839149b7129f61d7fafe55c0b4914`.

## Exact graph gate

- `n = 5886`, `|B| = 14079`, `|M| = 2766`, `|E| = 16845`.
- Every edge has zero common neighbors, so the graph is triangle-free.
- BFS in `B` reaches all 5886 vertices, so `B` is connected.
- Every bad edge has exact blue distance 4.  Thus every associated cycle
  length is 5 and `Gamma = 2766 * 25 = 69150`.

The base MaxCut upper bound is the sum of five independently checked class
bounds:

| class | edges | upper bound | attaining cut |
|---|---:|---:|---:|
| traffic | 4786 | 4110 | 4110 |
| selectors | 3380 | 2704 | 2704 |
| seeds | 15 | 12 | 12 |
| circuit | 235 | 207 | 207 |
| cable | 6 | 6 | 6 |

The traffic bound exhausts all `16 * 27 * 27 = 11664` quotient cases.  The
selector and seed bounds are edge-disjoint odd-cycle bounds.  The circuit
bound is 39 core blue edges plus 28 edge-disjoint 7-cycles, each bounded by 6.
Hence one copy has MaxCut 7039.  Any joined cut has value at most
`7039 + 7039 + 1 = 14079`, and the displayed cut attains 14079.

## Relation-level falsifier

At the doubled all-anchor state:

- the active scope has 38 vertices in roots 0 and 2943;
- the blue quiescent component containing vertices 3 and 56 has size 2758;
- its active boundary is `{1,55,2944,2998}`;
- its switch boundary is 1404 blue versus 1352 bad, so loss is `52 >= 0`;
- `pairCount(3,56) = 0`, and both endpoints are quiescent;
- both halves are unreserved;
- the base key `(3,56)` is P5-eligible for owners
  `{0,1,2,2943,2944,2945}`, hence for active roots 0 and 2943.

Assigning half 0 to owner 0 and half 1 to owner 2943 is injective on full
half keys but sends one base key to two components.  Therefore
`RelationBaseComponentUnique` is false on this exact cage.

## Coherent repair

The stronger relation-level uniqueness property is unnecessary for this
fixture.  A chosen matching can impose `BaseKeyComponentCoherent`.

For each root, the copy-local old relation has 19,925 source half-keys.  Its
mask histogram is `{1:5775, 2:5775, 4:5775, 7:2600}`.  R32 sends collision
debits, not hit debits, to FreeHalves.  Each hub has collision demand 6650, so
the three-owner shore has demand 19,950 and old reach 19,925, a deficit of 25.

Allocate the 28 P5 half-keys based at `(3,56+2j)` to root 0 and the translated
28 keys to root 2943.  Every one of these keys is globally eligible for both
roots, but the chosen allocation uses each base key in only its designated
root.  All seven Hall shores then have nonnegative slack; the full shore has
reach 19,953 and slack 3.

The checker constructs deterministic integral flows of 19,950 in each root.
Their union contains 39,900 assignments, is injective on full half-keys, and
has exactly one destination root per ordered-pair base key.  The explicit
assignment is `coherent_assignment.json`, SHA-256
`688522373338d36e65fbe96c5fd32675408d42771e0de2483d589fd826c52451`.

As an auxiliary stress test, the checker restores the isolated-2943 hit unit
at each hub.  The demand becomes 19,953 per copy, and both coherent flows still
saturate exactly.  This is labeled auxiliary because the joined graph uses
global `N = 5886`, where those hit needs are zero.

## Verdict

- Structural and exact numeric gate: **PASS**.
- `RelationBaseComponentUnique`: **FALSIFIED**.
- Coherence-constrained repair of each active component: **PASS**.
- Main theorem: **NOT CLAIMED**.

Reproduce from the repository root with:

```powershell
python tmp/fanout/r32_join5886/independent_gate.py
python tmp/fanout/r32_join5886/verify_manifest.py
```
