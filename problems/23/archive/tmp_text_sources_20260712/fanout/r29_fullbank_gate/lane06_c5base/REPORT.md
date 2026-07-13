# R29 c5Base / banked-token exact audit

## Verdict

**Implemented production c5Base absorption: UNDEFINED.** The compiled production surface checks individual common-blue and row-companion terminals and consumes abstract ledgers/capacities, but it contains no graph-derived `BaseKey` extractor, no checked transfer matching, and no transfer-to-bank adapter that constructs R29 c5Base tokens. Therefore the abstract `c5BaseCapQ` field is not counted as supplied capacity.

Two non-production relations can be replayed, and they disagree:

- **FAIL — component-scoped R23 prose relation:** demand `19,953`, unique reachable slots `19,925`, residual Hall defect `28`.
- **PASS — archived R23 Python-gate relation:** it omits the prose component equality, adds `912,600` unique outside-attachment slots, and gives `932,525` unique slots total; the full-shore surplus is `912,572`.

Thus the looser archived gate absorbs the defect, but the complete *implemented production* transfer/bank relation cannot be said to do so because that relation/conversion is absent.

## Exact reconstruction

`audit_c5base.py` imports only `build()` from the authoritative lead, copies the returned incidence into plain containers, installs all 676 anchor rows, and independently rebuilds pair counts, support, active components, collision demand, HitNeed, FreeHalf reservations, and source eligibility.

The replay checks:

- `N = 2943`, blue edges `7039`, bad edges `1383`, total edges `8422`;
- zero triangles; all `1383` rows are length-5 bad-endpoint paths with four blue edges;
- canonical lead payload SHA256 `fc4f3ab94bed810669976b1fdb21743fdd4ebe57eea15ef52afcfc2165e2fb1f`;
- all-anchor selected vertices `2127`, active vertices `19`, active edges `1370`, demanded active edges `18`;
- each hub owner has collision `6650`, HitNeed `1`, total demand `6651`; full shore demand `19953`.

The independently generated `19,925` records equal `cut_certificate.json` record-for-record: zero missing/extra records and zero owner-mask/reason-mask mismatches.

## Source classes with double spending removed

The unit is one distinct ordered `FreeHalf` key `(x,y,half)`. Shared owner eligibility does not multiply capacity.

| Class, in order | Per-owner eligible | Sum if wrongly owner-summed | Unique raw | Overlap with prior | New unique | Cumulative |
|---|---:|---:|---:|---:|---:|---:|
| `sameFirst` | `5775,5775,5775` | 17325 | 17325 | 0 | 17325 | 17325 |
| `commonBad` | `0,0,0` | 0 | 0 | 0 | 0 | 17325 |
| `rowCompanion` | `2600,2600,2600` | 7800 | 2600 | 0 | 2600 | 19925 |
| `outsideAttachment`, prose component equality | `0,0,0` | 0 | 0 | 0 | 0 | 19925 |

All pairwise class overlaps are zero. Final owner-mask counts are mask `1:5775`, `2:5775`, `4:5775`, and shared mask `7:2600`.

`commonBad` is empty because every hub has zero bad neighbours. For outside attachment, `V \ U` has `816` vertices in `704` blue components: 676 singleton components with attachment size 4 and 28 five-vertex components with attachment size 2. The archived gate finds the same 676 singleton vertices eligible for each hub. The R23 prose requirement `comp(a)=comp(owner)=comp(b)` rejects all of them, so its legal count is zero.

The archived Python implementation at `_claude_r23_outside_attachment_gate.py:97` and the corrected full-obligation gate at `_codex_r23_outside_attachment_full_obligation_gate.py:257` test only positive attachment co-occurrence; neither tests the component equality stated in `WALL_ATTACK_R23_GPTPRO56.md:10`. Under that implemented gate relation, all `676*675` ordered outside pairs have exact switch loss `8`, both half bits are free, hence

`2 * 676 * 675 = 912600`

new unique slots, shared by all three owners and disjoint from the prior `19,925`.

## Token-conversion audit

The writeup conversion is only a proposed semantic rule: R19 says a collision match cancels and a HitNeed match creates a `.c5Base` token (`WALL_ATTACK_R19_GPTPRO56.md:18`). R29 has only three hub HitNeed units, one per owner. This audit constructs zero production tokens because no full checked matching or compiled converter exists.

Compiled evidence:

- `Gamma/CheckedC5BaseTransfer.lean:14` says permanently-Free ownership and global matching are separate; lines 36 and 51 implement only `Valid` and its Boolean checker.
- `Gamma/CheckedRowCompanionBaseTransfer.lean:12-13` says the source-slot/global-matching layers are separate and no synthetic `TransferData` is assumed; lines 71 and 108 implement the terminal predicate/proof object.
- `Gamma/TypedFullBankSources.lean:14` explicitly calls the wall-sink adapter a separate obligation; lines 24-28 merely define generic typed constructors, including `c5Base (base : BaseKey)`.
- `Gamma/FullBankToLengthSurplusCharge.lean:7` says it does not assert certificate existence. Its `c5BaseCapQ` is an input field at line 38; the global `Checked` package begins at line 177.
- `Gamma/FullBankPortSinks.lean:80` states that legal edge-to-token incidence is absent, so its finite capacities do not assert Hall.
- `Ell5FullBankInterface.lean:7` identifies certificate existence as remaining open; lines 27-40 accept arbitrary `inc`, `kap`, and certificate proofs.
- No production Lean module implements the R23 outside-attachment terminal; `WALL_ATTACK_R23_GPTPRO56.md:29-32` labels it as a supplied Lean *shape*.

## Replay commands

From `E:\Projects\ErdosProblems\tmp\fanout\r29_fullbank_gate\lane06_c5base`:

```powershell
python audit_c5base.py *> audit_console.txt
python -m json.tool audit_result.json > $null
Get-FileHash -Algorithm SHA256 audit_c5base.py,audit_result.json,audit_console.txt,REPORT.md
```

The first command exits `0`; every assertion in `audit_result.json` is `true`. No floating-point arithmetic is used.

## SHA256 identities

Generated artifacts before this report:

- `audit_c5base.py`: `95f0396926892a8401db31e837ed160af29d912593527d81481b0bf36305c496`
- `audit_result.json`: `10953c85f3fd3e97482fa1e7e858e29d5deebdc7ae1a23134733c77c1f16e482`
- `audit_console.txt`: `10953c85f3fd3e97482fa1e7e858e29d5deebdc7ae1a23134733c77c1f16e482`

Authoritative/relevant inputs (also embedded in `audit_result.json`):

- `r29_lead_gate.py`: `5d29b1d6e35957405c53176fab1fb21660d727cb334a1e20462eb5ebe36678f6`
- `rebuild_owner_hall.py`: `a0912540f653945eed1eddbc74b191ea2a6ab90ccd075b1395cab552ff574dc0`
- `cut_certificate.json`: `dd1f1a2cff0886e6eaf8ed6487d7a5f308e51446b2ffbc284d6caac3f797e1ce`
- `WALL_ATTACK_R19_GPTPRO56.md`: `bfb75636d5e11b7f3d251cb20a64a5227f5b870938f1d1b715f38d400903adfc`
- `WALL_ATTACK_R20_GPTPRO56.md`: `cc4f42d19203a91ca4663a67c51cb1cb01273c442eaee733bf9dce94bb3b29f5`
- `WALL_ATTACK_R23_GPTPRO56.md`: `45e6533b1cb670ebb8476998bee9904ad0ec8f8943c2753b78a677827358c9d3`
- `_claude_r23_outside_attachment_gate.py`: `6147ac4c7b501f8ab46597ef210838e1138f0b7cb15910a4712dc5efac844cec`
- `_codex_r23_outside_attachment_full_obligation_gate.py`: `26838f666e3c567d8396a89ec4e6540fb1b1fa321eaa434b12f18710a113ace1`
- `CheckedC5BaseTransfer.lean`: `12451978d18a455b312ef292aa249f7f6d5a1c950e3112ec03a0d4ed86d17ee0`
- `CheckedRowCompanionBaseTransfer.lean`: `84b632c5329ea1205729ff0b95ab124fc573f119f17c50d4aa2f02ac9afdf09a`
- `TypedFullBankSources.lean`: `6ab920d11b983848a46d95e9477a4bf4b1b948992a3aef5f158aff4dc1820fbd`
- `FullBankToLengthSurplusCharge.lean`: `f4806742bdff61e0e3a15637c25d796b0abf0803936aaabc82a77de2a1da40cd`
- `FullBankPortSinks.lean`: `ec03183e2dd9c1ee5578d589558e5400d9d4c8260a056fbbc5da483b8614a4f6`
- `Ell5FullBankInterface.lean`: `8d02d032507152301ee7bc01b0a64b7614dfc0c754152be343aa3a3a3a9dd104`
- `Ell5FullBankHall.lean`: `0ac01cf28b2e7dc6770da7f71b147cedec47671a4c672e1434fd7dc372f1bae1`
