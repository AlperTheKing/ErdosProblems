# R29 exact four-pattern transfer audit — lane 02

## Verdict

**UNDEFINED for the decisive production question.** The complete implemented production transfer/bank relation cannot be evaluated because the fourth class, `outsideAttachment`, has no definition in the production Lean surface. The FullBank modules expose abstract certificate/package interfaces, not a compiled graph-derived provider for this R29 tuple.

**PASS for the executable R23 four-pattern gate specification.** Under the exact outside-component predicate implemented by the R23 Python gates, the old 28-unit HUB-shore defect is absorbed. The full shore `{0,1,2}` has demand `19,953`, cumulative unique reach `932,525`, and signed defect `demand - reach = -912,572` (surplus `912,572`). All seven nonempty owner shores satisfy Hall.

These verdicts are intentionally separate. The gate PASS is not promoted to a production PASS because doing so would invent the missing compiled constructor/provider.

## Exact reconstruction

`verify.py` imports and executes the deterministic constructor in `tmp/fanout/r29_gate/lead/r29_lead_gate.py`, then independently replaces all 676 selector rows by `selectorMeta[*].anchorRow` and rebuilds pair counts, selected support, active components, collision demand, HitNeed, reservations, and sources.

- `N = 2,943`, blue edges `7,039`, bad edges/rows `1,383`.
- Selected vertices `2,127`; outside vertices `816`.
- Active vertices `19`; active edges `1,370`; demanded active edges `18`.
- Hub owner demand per owner: collision `6,650` plus HitNeed `1`, total `6,651`.
- Hub shore demand: `3 * 6,651 = 19,953`.
- Rebuilt-incidence SHA256 (the convention of `rebuild_owner_hall.py:43-49`): `7f3c69376e074adefe505f709643bdf14a9a5c5b18e9816d8b88e24d7b59f087`.
- Canonically serialized all-anchor row-list SHA256: `ab37d295364a110795388fbb8bb695f5ae849514348ff84bc29edf8ca57493f9`.

The reconstruction source is `r29_lead_gate.py:129-276`; the independent active-scope formulas being matched are `rebuild_owner_hall.py:52-97`.

## Staged source ledger

Every count below is a count of literal ordered `FreeHalf` slots `(x,y,half)`. A half-zero slot on an active ordered cell is removed before unioning classes. Owner eligibility is stored as a bit mask on each literal slot, so shared eligibility never becomes shared capacity.

| Added class | Raw unique slots | Overlap with prior | New unique slots | Cumulative reach | HUB defect |
|---|---:|---:|---:|---:|---:|
| sameFirst / sameOwner | 17,325 | 0 | 17,325 | 17,325 | 2,628 |
| commonBad | 0 | 0 | 0 | 17,325 | 2,628 |
| rowCompanion | 2,600 | 0 | 2,600 | 19,925 | 28 |
| outside-component attachment | 912,600 | 0 | 912,600 | 932,525 | -912,572 |

Reservation details: sameOwner rejected exactly three half-zero candidates (one with owner multiplicity for each hub); rowCompanion and outsideAttachment rejected none. The outside class is disjoint from all earlier classes because both outside endpoints lie outside the selected-row union, while every earlier retained source endpoint lies in that union.

The pre-outside result exactly reproduces the authoritative auxiliary certificate: demand `19,953`, reach `19,925`, defect `28`.

## Predicate verification

- **sameOwner:** `x = owner`, `x != y`, `pairCount(owner,y)=0`; the active-edge half-zero reservation is removed. This matches `MinimumDemandCollisionHall.lean:64-87` and the R29 gate implementation at `rebuild_owner_hall.py:110-119`.
- **commonBad:** both source vertices are distinct actual bad neighbours of the owner, the ordered pair is free, and `loss({x,y}) >= 0`. The three hub owners have no such source cells, so the exact contribution is zero. This is the named R19/R20 gate class (`WALL_ATTACK_R19_GPTPRO56.md:15-18`, `_claude_r20_staged_matching_gate.py:169-183`), but it has no same-named Lean definition.
- **rowCompanion:** `pairCount(owner,x)>0`, `pairCount(owner,y)>0`, `x!=y`, `pairCount(x,y)=0`, and exact switch loss is nonnegative. All 2,600 unique slots are eligible for all three hubs; the minimum verified loss is `2`. The compiled predicates are `MinimumDemandCollisionHall.lean:89-109` and `CheckedRowCompanionBaseTransfer.lean:70-85`; the R29 reconstruction being reproduced is `rebuild_owner_hall.py:120-135`.
- **outsideAttachment:** components are those of the blue graph induced on `V \ U`; attachment boundaries are their blue neighbours in `U`. An owner is eligible on a component exactly when an attachment vertex has positive owner co-occurrence. For a component pair, the exact switch is the union and its loss is recomputed. This matches `_claude_r23_outside_attachment_gate.py:52-145` and the corrected full-obligation gate at `_codex_r23_outside_attachment_full_obligation_gate.py:229-311`.

The outside induced graph has 704 components: 676 singletons and 28 components of size 5. Exactly the 676 singleton components are eligible for each hub. Every ordered pair of distinct eligible components passes, giving

`2 * 676 * 675 = 912,600`

literal half-slots, all with owner mask `7`. All `456,976 = 676^2` ordered component pairs were checked (same-component cells contribute zero because the components are singletons); no component pair was rejected for negative loss, and the minimum loss was `4`. Component-union losses are evaluated exactly from component boundary losses and the signed cross-component edge correction, with each single-component loss independently replayed from graph edges.

## Production-surface audit

The following distinctions prevent an overclaim:

1. `SameOwner` and `RowCompanion` are compiled (`MinimumDemandCollisionHall.lean:82-109`), and rowCompanion has a literal terminal checker (`CheckedRowCompanionBaseTransfer.lean:70-130`).
2. The compiled R19 C5 terminal is **common blue**, not commonBad: `CheckedC5BaseTransfer.lean:35-43` requires two blue owner edges and adjusted loss at least two. Its own module states that permanent freeness and global matching are separate layers (`:13-15`).
3. As a supplemental exact check, adding this corrected common-blue terminal to the pre-outside source relation supplies 216 new unique slots, raises full-shore reach to `20,141`, and gives full-shore defect `-188`; all seven shores pass. This is numerical evidence under the natural FreeHalf ownership relation, not a compiled global matching provider.
4. No `OutsideAttachment`/`outsideAttachment` identifier occurs in the 27 scanned production `Gamma/*.lean` and `*FullBank*.lean` files. The R23 writeup says only “Lean shapes given” (`WALL_ATTACK_R23_GPTPRO56.md:29-34`).
5. `FullBankRelaxedCoverCert` is parameterized by arbitrary legal incidence/capacity data (`Ell5FullBankInterface.lean:23-40`), while `FullBankGlobalPackage.Checked` assumes token ledger and reserve identities (`FullBankToLengthSurplusCharge.lean:174-220`). Neither constructs the missing outside source relation from this graph/tuple.

Therefore the R29 tuple is **not a four-pattern gate falsifier**, but the claim that the **complete implemented production** relation absorbs it remains **UNDEFINED** until a compiled global matching/provider specifies the source classes and includes (or replaces) outsideAttachment.

## Replay commands

From `E:\Projects\ErdosProblems\tmp\fanout\r29_fullbank_gate\lane02_transfer`:

```powershell
python -B verify.py
Get-FileHash verify.py,RESULT.json,REPORT.md -Algorithm SHA256
```

The replay uses integer arithmetic only and exits nonzero on any failed assertion. `RESULT.json` contains every owner-shore cut, owner-mask histogram, overlap/reservation count, component histogram, input hash, and supplemental common-blue cut.

## Artifact and input hashes

- `verify.py`: recorded in `SHA256SUMS.txt`.
- `RESULT.json`: recorded in `SHA256SUMS.txt`.
- `REPORT.md`: recorded in `SHA256SUMS.txt`.
- Authoritative input hashes are recorded both in `RESULT.json.input_sha256` and `SHA256SUMS.txt`.

The two key authoritative identities at replay were:

- `r29_lead_gate.py`: `5d29b1d6e35957405c53176fab1fb21660d727cb334a1e20462eb5ebe36678f6`.
- `cut_certificate.json`: `dd1f1a2cff0886e6eaf8ed6487d7a5f308e51446b2ffbc284d6caac3f797e1ce`.
