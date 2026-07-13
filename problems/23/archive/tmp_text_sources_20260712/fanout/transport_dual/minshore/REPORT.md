# Inclusion-minimal deficient owner shores

## Exact abstraction

Fix `omega`. For an owner `a`, let

- `d(a) := #{d : Demand G c omega | demandOwner d = a}`;
- `N(A) := scopedOwnerSourceSet G c omega A`;
- `d(A) := sum_{a in A} d(a)`;
- `delta(A) := d(A) - |N(A)|` (an integer).

By `available_iff_of_demandOwner_eq`, availability depends only on the owner. Thus `scopedOwnerDemandSet A` is the disjoint union of the owner fibers and has cardinality `d(A)`, while `scopedOwnerSourceSet A` is exactly the union of their source neighborhoods. The following statements need no graph assumptions.

## Proved statements

**MS1 (supermodular uncrossing).** For all owner shores `A,B`,

`delta(A) + delta(B) <= delta(A union B) + delta(A intersection B)`.

Proof: `d` is modular. Also `N(A union B)=N(A) union N(B)` and `N(A intersection B)` is contained in `N(A) intersection N(B)`, so source-neighborhood cardinality is submodular.

**MS2 (proper-subshore/tight-subshore inequality).** If `A` is inclusion-minimal with `delta(A)>0`, then every proper `C subset A` satisfies `delta(C)<=0`, equivalently `d(C)<=|N(C)|`. In particular, for `a in A`,

`|N(A)| - |N(A\{a})| <= d(a)-delta(A)` and `delta(A)<=d(a)`.

The left side is the number `p_A(a)` of sources private to `a` relative to `A`. This is the sharp private-source conclusion. It is an upper bound; minimal deficiency does not supply a private source.

**MS3 (crossing amplification).** If `A` is inclusion-minimal deficient, `B` is deficient, and `A intersection B` is a proper subset of `A`, then

`delta(A union B) >= delta(A)+delta(B)-delta(A intersection B) >= delta(A)+delta(B)`.

Thus two crossing deficient shores force a more deficient union, not a smaller deficient intersection. This is the usable direction of uncrossing.

**MS4 (unweighted specialization).** If every owner fiber has size one, then every inclusion-minimal deficient `A` has `delta(A)=1` and `p_A(a)=0` for every `a in A`. Proof: MS2 gives `1<=delta(A)<=1` and `p_A(a)<=0`.

## Exact falsifiers

**F1: “each owner has a private source” is false, minimally.** Owners `{a,b}`, weights `d(a)=d(b)=1`, one source `s`, and `N(a)=N(b)={s}`. Then `delta({a,b})=1`; both singleton shores are tight; neither owner has a private source. This is also the sharp unweighted MS4 pattern.

**F2: “every one-owner deletion is tight” is false.** Abstract witness: `d(a)=d(b)=2`, `N(a)={x,y,z}`, `N(b)={x,y}`. The full shore has demand `4`, sources `3`, defect `1`, and is inclusion-minimal. Deleting `a` is tight, while deleting `b` leaves demand `2`, sources `3`, slack `1`.

The graph-derived fixture is stronger: shore `{8,9}`, owner demands `(9,10)`, union source capacity `17`, defect `2`. Owner `8` has `11` neighbors and `7` private sources, exactly its bound `9-2=7`; owner `9` has `10` neighbors and `6` private sources, below its bound `10-2=8`. Deleting `8` is tight; deleting `9` has slack `2`. Hence both “defect is always one” and “all deletions are tight” fail on an existing graph artifact.

**F3: changed-row demand/source invariance is not a consequence of locality.** Even if an owner lies on neither old nor new row, `selectedLoad_replaceOne_of_owner_not_mem_changed` preserves only its selected load, and `pairCount_replaceOne_of_owner_not_mem_changed` preserves its co-occurrence counts. `Demand` also depends on `ActiveOwner` and `activeDegree`; `Available` additionally depends on `ScopedReserved`, hence active-component connectivity. The proved component lemma is one-way: a new component avoiding the changed rows embeds into an old component. It does not say an old component persists. Abstract temporal falsifier: one unchanged owner of weight `1`, old neighborhood `{s}`, new neighborhood empty. This respects scalar owner-load locality but changes `scopedOwnerSourceSet`. A graph-realizable witness is not supplied.

## Transport consequence and limitation

MS2 does not construct the injection required by `CoordinateReplacementInjection`. It bounds private old source capacity from above:

`p_A(a) <= d(a)-delta(A)`.

Therefore minimal-shore structure alone cannot pay new demand owner-by-owner. Any transport proof must additionally use shared sources across owners and must prove graph-derived persistence/inheritance for sources under changed rows. MS3 can canonicalize competing deficient shores toward unions, but it supplies no legal `ComponentTransportSourceEligible` assignment.

The missing graph-realizability proof is precisely: under `TriangleFree`, `IsMaxCut`, `BConnected`, and `CompleteShortestRowDB`, show that changed-row component inheritance/touching gives enough shared old shore sources to inject every new coordinate-demand bundle. Neither inclusion-minimality nor current changed-row locality implies this statement.

## Exact tests

`check_minshore.py` used only Python integers and `fractions.Fraction`. It exhaustively checked `65,536` weighted incidence systems (three effective owners, four sources, weights `1` or `2`; the duplicated fourth weight coordinate is harmless and recorded by the count), containing `63,260` inclusion-minimal deficient shores. MS1 and MS2 passed every shore. It separately reconstructed source halves from the existing `default.json` fixture and obtained the exact `{8,9}` values above. No float acceptance was used.

Artifacts: `check_minshore.py`, `test_results.json`.

## SHA-256

- `b916318f53d69b4d9adff2c4a79b23c139513640f16550daea092ce3a9e77982`  `ActiveScopedMinimumExchange.lean`
- `6a4d47533d10e4b04eb19cda0d0554658abd434c94c04566a01916708a90e8f0`  `ActiveScopedOwnerHallReduction.lean`
- `6b10458bedd26b4d460fdd4ad034d55cb6b1dee16a2691f22460e562941dc272`  `ActiveScopedCoordinateTransport.lean`
- `f5c3fa45c9e9ccd9743d00feb3e5b08345ee957bf3f788a4f4216358c9cee978`  `tmp/fanout/transport_dual/accounting/default.json`
- `f4961fc7b10410baeda2a9d5c9ed3be772e207277c8f2608d1fd16d9b82ba8a6`  `check_minshore.py`
- `0a56c2b8872c23415bc4772968112a97463441898831352bc8a1f47174a0d445`  `test_results.json`
