# R29 lane03 reconstruction audit

## Verdict

**PASS** for the assigned reconstruction/invariant lane. The deterministic R29 cage and all-anchor row tuple replay with every requested structural invariant and with the implemented `Gamma/ActiveScoped*` hub-shore demand/reach values.

**UNDEFINED** for the common contract's decisive FullBank question. This lane verifies only the auxiliary `ActiveScoped` relation; it does not enumerate the additional production FullBank source classes and therefore neither proves absorption of 28 nor a FullBank Hall/LP defect.

`constructor.py` is a lane-local immutable transcription of the authoritative indexed constructor (identical SHA256); `verify.py` imports only that local incidence builder and independently rebuilds every derived row, graph, component, demand, companion, and source-mask invariant. It does not read or wrap `cut_certificate.json` or any copied result total at runtime.

## Replay

From `tmp/fanout/r29_fullbank_gate/lane03_reconstruct`:

```powershell
python -m py_compile constructor.py verify.py
python verify.py
```

The second command deterministically rewrites `STRUCTURAL_ORACLE.json`, `RESULT.json`, and `HASHES.json`; it exits nonzero on any mismatch. Only Python integers are used.

## Exact results

- Cage: `N=2943`, `|B|=7039`, `|M|=1383`, `|E|=8422`; cut shores have sizes `1499,1444`.
- Integrity: `B∩M=∅`; every B edge crosses and every M edge is monochromatic; no triangle; B reaches all 2,943 vertices from 0.
- All 1,383 bad atoms have B-distance 4. Shortest-row histogram is `707×1 + 676×680`, by class: traffic `676×1`, selector `676×680`, circuit `28×1`, seed `3×1`.
- Row checks: all 1,383 selected rows are members of their atom families, each row has five distinct vertices, and the selected tuple has no duplicate row.
- All-anchor selection: 676/676 selector choices lie in the 676-row anchor subfamily of their 680-row family; every family also has four local rows. Exactly 676 baseline rows change; 677 selected rows contain vertex 55 (676 selectors plus one seed row).
- Selected support: 2,127 vertices and 2,797 support edges. The 1,370 off-support active edges form 757 components with size histogram `730×1, 26×53, 1×19`.
- There is one active component: vertices `[0,1,2,55,2762,2763,2764,2765,2766,2771,2772,2773,2774,2780,2781,2782,2783,2929,2930]`; it has 18 active edges and internal bad atom `(2762,2766)`. The other 1,352 active edges lie in inactive components.
- Global active-scoped obligations are collision `23108` plus HitNeed `7`, total `23115`.
- Each hub owner 0,1,2 has the exact companion set `{0,...,54}` (55 vertices), pair multiplicities `52×26 + 3×676`, collision demand 6,650, HitNeed 1, total 6,651.
- Hub shore `{0,1,2}` demand is `3×6651=19953`. Incremental distinct source classes are same-first-only `17325`, row-companion-only `2600`, overlap `0`; their union/reach is `19925`, hence auxiliary defect `19953-19925=28`.
- Owner-mask source histogram is `{1:5775,2:5775,4:5775,7:2600}`. All eight owner shores are recorded in the oracle.

## Implemented-definition match

- Constructor and anchor formula: `constructor.py:129-227`, especially `anchorRow` at line 191.
- Selected rows/support, ordered `pairCount`, and active edges: `Gamma/MinimumDemandRowSelection.lean:59-101`.
- `FreeHalf`, reservation, same-owner, row-companion, eligibility and availability: `Gamma/MinimumDemandCollisionHall.lean:66-109`.
- `sigma=dB-dM`: `CertGraph.lean:78-87`.
- Active graph/component scope, degree, selected load, HitNeed, scoped reservation, eligibility and availability: `Gamma/ActiveScopedMinimumExchange.lean:30-147`.
- Owner demand/source shores: `Gamma/ActiveScopedOwnerHallReduction.lean:22-32`.
- Independent recomputation: `verify.py:40` (scope), `verify.py:56` (sources), `verify.py:82-172` (audit/output).

The notions checked above are implemented. “Complete production FullBank absorbs the defect” and “defect remains under every FullBank source class” are not established by this lane and are therefore explicitly **UNDEFINED**, not prose-level assumptions.

## Identities and hashes

- Baseline canonical incidence: `fc4f3ab94bed810669976b1fdb21743fdd4ebe57eea15ef52afcfc2165e2fb1f`.
- Canonical all-anchor row list: `ab37d295364a110795388fbb8bb695f5ae849514348ff84bc29edf8ca57493f9`.
- Auxiliary source stream: `a409dd9641b47594c485254e0eb4852195dc4817ed979cbba8ab0be74e667e8a`.
- `RESULT.json`: `9e18b62af1607d99166cadda8bb7d08883ecd55601489808b0c99af09b4edd05`.
- `STRUCTURAL_ORACLE.json`: `1f40f3e4da29dd469d41af5d38b7c141b260f2e48c7669f3c630c1e765018719`.

`HASHES.json` records full SHA256 hashes for the common contract, constructor, prior Hall evidence, exact Lean semantic sources, verifier, oracle, result, and this report.
