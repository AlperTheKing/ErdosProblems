# Worker 6: ActiveScoped versus R20/R23 four-pattern audit

## Falsifiable conclusion

The published R29 `28`-unit Hall defect is a counterexample only to the compiled two-pattern `ActiveScopedMinimumExchange.EligibleOwner`, not to the real R20/R23 four-pattern relation.  Recomputing the same all-anchor tuple with the R23 `outsideAttachment` pattern changes hub-shore reach from `19925` to `932525`; all eight owner shores then have nonpositive deficiency, the maximum deficiency is `0`, and an explicit integral flow of `19953` exists.  This conclusion is falsified by any exact replay, on the hashes below, that either (a) finds one of the eight four-pattern shore deficiencies positive, or (b) fails to route the listed `28` added outside half-slots.

## Line-by-line relation trace

| Concern | Existing ActiveScoped falsifier | Real R20/R23 relation | Exact comparison |
|---|---|---|---|
| Active scope | `tmp/fanout/r29_gate/d05/retry2/rebuild_owner_hall.py:52-97` rebuilds selected support, off-support blue components, active vertices, collision halves, and HitNeed. | `problems/23/writeup/_codex_r23_outside_attachment_full_obligation_gate.py:152-220` performs the same reconstruction; the independent R29 replay is `tmp/fanout/r29_fullbank/B_fourpattern/verify_fourpattern.py:72-138`. | No demand mismatch: each hub owner has collision `6650`, HitNeed `1`, demand `6651`; total `19953`.
| Same-owner | Old `rebuild_owner_hall.py:110-119`: ordered `(owner,y,half)` when `pair[owner,y]=0`. | R23 gate `:281-284`; replay `verify_fourpattern.py:226-229`. | Same edges.  The replay represents a cell once with capacity instead of materializing each half.
| Common-bad | Old code has no separate loop. | Replay `verify_fourpattern.py:231-235` names the pattern: both endpoints are bad-neighbors of the owner, unused together, and nonnegative two-vertex switch loss. | Omitted as a *label*, not as reach: R23 gate says commonBad is a row-companion subcase at `:286-287`; on R29 it contributes `0` new cells/capacity after row-companion deduplication.
| Row-companion | Old `rebuild_owner_hall.py:120-134`: both endpoints co-occur positively with owner, are unused together, and have nonnegative signed pair loss. | R23 gate `:286-295`; replay `verify_fourpattern.py:237-242`. | Same edges and loss convention.  Adds `2600` half-slots beyond same-owner on R29.
| Outside attachment | Entirely absent from old `owner_sources` (`rebuild_owner_hall.py:100-135`). | R23 gate `:229-265,297-311`; replay `verify_fourpattern.py:140-190,244-254`.  An owner may use ordered outside vertices from components whose attachment contains a positive owner companion, provided switching the union of their outside components has nonnegative loss. | This is the decisive omitted edge family.  R29 has `676` eligible singleton outside components per hub owner, `676*675=456300` ordered pairs, switch loss exactly `8` for all such pairs, and `912600` new half-slots after deduplication.  It supplies far more than the missing `28`.
| Extra edges | Old source universe contains only same-owner and row-companion (`rebuild_owner_hall.py:110-134`). | The compiled Lean relation at `problems/23/lean/Erdos23Delta0/Gamma/ActiveScopedMinimumExchange.lean:134-147` also contains only `sourceX=owner` or the two companion predicates plus nonnegative sigma. | The old falsifier has no edge class extra relative to compiled `EligibleOwner`.  Relative to the named four-pattern presentation it merely folds commonBad into row-companion.  Conversely, compiled production omits outsideAttachment entirely.
| Reservations | Old `rebuild_owner_hall.py:114-118,129-133` deletes half `0` when the ordered cell lies on an active edge and its first endpoint is active. | Lean `ActiveScopedMinimumExchange.lean:125-147` states exactly half `0`, active adjacency, active `sourceX`.  R23 active-scope gate uses capacity `1` on demanded active cells and `2` otherwise (`full_obligation_gate.py:267-277`). | Same active-scoped reservation.  Exact R29 reserved ordered cells are `(0,55)`, `(1,2929)`, `(2,2930)`, removing one half-slot each.  Outside cells are never active, hence retain capacity `2`.
| Multiplicity | Old code materializes keys `(x,y,h)` (`rebuild_owner_hall.py:114-119,129-134`), so `(x,y)` and `(y,x)` are distinct and each normally has halves `0,1`; a source is globally deduplicated by key while owner eligibility is an owner bit mask. | R23 uses ordered cell key `(x,y)` (`full_obligation_gate.py:272-277`) with capacity `2` or reserved capacity `1`; owner-cell arcs are a set and a single cell-to-sink arc enforces global no-double-spend (`:279-329`). Replay uses the same masks/capacities (`verify_fourpattern.py:201-223,256-274`). | Conventions agree exactly.  Demand counts collision *halves* as `2*(multiplicity-1)` and HitNeed as integral units; no unordered-pair collapse and no per-owner duplication of physical capacity is allowed.

## Required recomputation and result

The required recomputation is not another selector minimization: retain the already verified global-minimum all-anchor tuple, rebuild active-scoped demand unchanged, rebuild the full owner-to-ordered-cell relation with all four pattern labels, reserve half zero on demanded active ordered edges, deduplicate cells globally, and recompute all eight owner-shore cuts plus an integral max flow.

The exact implementation is `tmp/fanout/r29_fullbank/B_fourpattern/verify_fourpattern.py`.  It reports old reach `17325+2600=19925`, old defect `28`, outsideAttachment new reach `912600`, full reach `932525`, maximum four-pattern deficiency `0`, and minimum cut/max flow `19953`.  Its emitted certificate is independently checked by `verify_certificate.py`, including all eight cuts and `28` concrete outside repair halves.

Command run from repository root:

```text
python tmp/fanout/r29_fullbank/B_fourpattern/verify_certificate.py
```

Exact output:

```json
{"certificate_sha256":"ec9526913e2cf7ae513ba83e0b423a989958f212e1764d085d5583c90ae2ac3e","cuts_checked":8,"explicit_repair_halves_checked":28,"full_flow":19953,"maximum_deficiency":0,"minimum_cut":19953}
```

No floating-point arithmetic is used: the replay declares integer/`fractions.Fraction` arithmetic, and the verifier rejects inconsistent rational text, cuts, reservations, or repair multiplicities.

## SHA-256 inputs and executables

```text
13243e061b11c8f44ff18039795a8516c84c1198f40df85e635f3b43cce4a8ac  tmp/fanout/r29_fullbank/B_fourpattern/verify_fourpattern.py
ec9526913e2cf7ae513ba83e0b423a989958f212e1764d085d5583c90ae2ac3e  tmp/fanout/r29_fullbank/B_fourpattern/certificate.json
a0912540f653945eed1eddbc74b191ea2a6ab90ccd075b1395cab552ff574dc0  tmp/fanout/r29_gate/d05/retry2/rebuild_owner_hall.py
dd1f1a2cff0886e6eaf8ed6487d7a5f308e51446b2ffbc284d6caac3f797e1ce  tmp/fanout/r29_gate/d05/retry2/cut_certificate.json
668f427042c4666e21ec41ee454136aefce789a8cba8adacf703853ef373347c  tmp/fanout/global_min_proof/lead/verify_r29_global_min_hall_falsifier.py
6aa3fdd19d15a4a5231494c6b92f3659bfcf13cfa1f2d900b6f3857ec1cf019d  problems/23/lean/Erdos23Delta0/Gamma/ActiveScopedMinimumExchange.lean
26838f666e3c567d8396a89ec4e6540fb1b1fa321eaa434b12f18710a113ace1  problems/23/writeup/_codex_r23_outside_attachment_full_obligation_gate.py
```
