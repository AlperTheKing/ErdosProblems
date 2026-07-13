# R29 FullBank source search synthesis

## Verdict

The canonical `N=2943` all-anchor tuple is **not** a falsifier after restoring the already compiled R19 common-blue `c5Base` eligibility predicate from `CheckedC5BaseTransfer.TerminalData.Valid`.

The old relation has demand `19953`, reach `19925`, and defect `28`. Exact enumeration finds `2824` valid owner-terminal half instances, giving `216` genuinely new global FreeHalf keys and `8` owner-mask upgrades. The full union has `20141` keys.

## Minimum absorber

Use owner `2`, `zR=2930`, leaves `x=29,...,42`, and both half bits:

```text
A = {(x,2930,h) : 29 <= x <= 42, h in {0,1}}.
```

For every key in `A`, literal edge counting gives `dB({x,2930})=30`, `dM({x,2930})=27`, hence the checked adjusted surplus is `30-27-2=1`. Both vertices are blue neighbors of owner `2`, the ordered pair occurs in no selected row, and it is not an active-edge reservation.

The 28 source IDs under `id(x,y,h)=2*(2943*x+y)+h` are:

```text
176554,176555,182440,182441,188326,188327,194212,194213,
200098,200099,205984,205985,211870,211871,217756,217757,
223642,223643,229528,229529,235414,235415,241300,241301,
247186,247187,253072,253073
```

They are pairwise distinct and absent from the old `19925`-key certificate. Assign them to 28 owner-2 collision obligations. Per R19, collision matches cancel and create no FullBank token spend; only `HitNeed` matches create a `c5Base` token. Thus raw `capQ/25` scaling is irrelevant to these 28 cancellations.

The repaired shore margins for masks `0..7` are:

```text
0, 1724, 1724, 848, 1752, 876, 876, 0
```

The full injective assignment has SHA-256 `43e50aee99b019df6804aa173ba5456f4de2e5ec08b540e13f08349f1398012a`.

## Minimality

Any repair using new unit FreeHalf keys needs at least 28 keys because the full owner shore has exact defect 28. The displayed family has exactly 28 keys, so it is minimum in half-slot cardinality. It uses 14 ordered source pairs and both independent half bits.

## Portfolio audit

- `c5base`: independently found the symmetric 28-key owner-2 absorber and the same source IDs.
- `vertex_slack`: exact all-anchor core has `C=2127`, `F=2797`, `O=4242`; margins fail only at `0,1,2,55` by `-1/2,-1/2,-1/2,-2`.
- `doors`: found 56 restriction exits with total load 28 but zero realized typed Door tokens; no Door repair is claimed.
- `prune`: no compiled prune trace, decreasing rank, injective transport, or graph-to-token adapter; justified prune universe empty.
- `flow_dual`: its defect-28 dual is conditional on zero proved arcs and labels `c5Base` unknown, so the explicit checked c5Base terminals supersede it.
- `semantics`: rejected. It used baseline selector rows as the all-anchor tuple (`C=2803` instead of `2127`) and licensed every off-support edge as a Door without a graph-derived typed-token instance.
- `referee`: its unit warning applies to token-spending `HitNeed`, not collision cancellation; its core/vertexSlack diagnostics remain valid.

## Replay

```powershell
python tmp\fanout\r29_gate\lead\r29_lead_gate.py
python tmp\fanout\r29_gate\d05\retry2\rebuild_owner_hall.py
python tmp\fanout\r29_fullbank\E_source_search\lead\r29_c5base_absorber.py
python tmp\fanout\r29_fullbank\E_source_search\lead\verify_c5base_absorber_independent.py
python tmp\fanout\r29_fullbank\E_source_search\vertex_slack\replay.py
python tmp\fanout\r29_fullbank\E_source_search\doors\audit_doors.py
python tmp\fanout\r29_fullbank\E_source_search\flow_dual\check_certificate.py
```

## Smallest statement

> On the canonical `N=2943` all-anchor R29 tuple, extending `Available` by `CheckedC5BaseTransfer.TerminalData.Valid` yields an injective owner-demand matching. Exactly 28 new FreeHalf keys are necessary and sufficient; `(x,2930,h)` for `29 <= x <= 42` and `h in {0,1}` is a minimum witness. Assigning these keys to collision demands creates no FullBank token spend.

This closes only the R29 auxiliary obstruction. It is not a proof of the universal FullBank provider or Erdos #23.
