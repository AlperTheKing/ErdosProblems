# Worker 3 exact four-pattern certificate

`verifier_a.py` independently rebuilds the labelled R29 graph through the canonical constructor, replaces all 676 selector rows by their anchor rows, and checks that these rows equal every row in `best_tuple.json`. It then recomputes row multiplicities, the active component, obligations, reservations, all four R20/R23 source patterns, outside blue components, switch losses, and all eight owner shores using integers only (`Fraction` is used only for exact display). No external solver is called.

## Canonical tuple and demand

- `N=2943`, blue edges `7039`, bad edges `1383`, selected rows `1383`, selector rows `676`.
- Selected vertices `2267`; outside vertices `676`, forming `676` singleton blue components.
- Active scoped score `23115`.
- Hub owners are `0,1,2`. Each has collision demand `6650` and HitNeed `1`, hence `6651` half-slots each and total hub-shore demand `19953`.

## Source decomposition (new capacity at each ordered stage)

| pattern | new ordered cells | new owner-cell arcs | new half-slots | exact Q capacity at K=1 |
|---|---:|---:|---:|---:|
| sameFirst | 8664 | 8664 | 17325 | 17325/2 |
| commonBad | 0 | 0 | 0 | 0 |
| rowCompanion | 1300 | 3900 | 2600 | 1300 |
| outsideAttachment | 456300 | 1368900 | 912600 | 456300 |

The final capacities by owner-support mask are mask `1:5775`, `2:5775`, `4:5775`, and shared mask `7:915200`, totaling `932525` half-slots. For pattern 4, every owner is eligible for all `676*675=456300` ordered outside pairs. Every pair has exact switch loss `8`, and its two half-slots give `912600` new capacity.

## Reservations, reach, and defect

The demanded-active ordered cells `(0,55)`, `(1,2929)`, `(2,2930)` reserve one of their two halves, so their capacities are one; every other free ordered cell has capacity two. Thus sameFirst has `8664*2-3=17325` half-slots.

- Old three-pattern hub shore: demand `19953`, reach `17325+0+2600=19925`, defect `28`.
- Full four-pattern hub shore: demand `19953`, reach `932525`, defect `-912572`.
- Maximum deficiency over all eight shores is `0`; therefore Hall holds.

An explicit integral repair assigns `5775` private sameFirst halves to each owner, shared rowCompanion halves `876,876,848` to owners `0,1,2`, and the lexicographically first 28 distinct outside half-sources to owner `2`. Receipts are exactly `6651,6651,6651`.

## Deterministic min-cut certificate

For shore mask `S`, the verifier computes
`cut(S)=19953-demand(S)+reach(S)` and enumerates masks `0..7`. Capacities are respectively:

`[19953, 934277, 934277, 933401, 934277, 933401, 933401, 932525]`.

Lexicographic minimization of `(cut capacity, shore mask)` therefore returns mask `0`, capacity `19953`, exactly the total demand. This is an exhaustive deterministic max-flow/min-cut certificate for three owners, not a solver result. Full details, all shore demands/reaches/deficiencies, and the 28 concrete source halves are in `certificate_a.json`.

## Replay commands and SHA256

Run from repository root:

```powershell
python tmp/fanout/r29_fullbank/B_fourpattern/worker_3/verifier_a.py
Get-FileHash tmp/fanout/r29_fullbank/B_fourpattern/worker_3/verifier_a.py -Algorithm SHA256
Get-FileHash tmp/fanout/r29_fullbank/B_fourpattern/worker_3/certificate_a.json -Algorithm SHA256
```

- `verifier_a.py`: `1c896d2c79814eb2d67a0b60a7aa88665b3837f7676361f87f97602c724739f0`
- `certificate_a.json`: `5a201a8a8037aa2b620c9c8ba3b91c97302338a45bb45f7dfa59c53342db2007`

Expected verifier summary:

```json
{"certificate_sha256":"5a201a8a8037aa2b620c9c8ba3b91c97302338a45bb45f7dfa59c53342db2007","demand":19953,"four_pattern_reach":932525,"maximum_deficiency":0,"min_cut":19953,"old_defect":28,"old_reach":19925,"outside_reach":912600,"score":23115}
```
