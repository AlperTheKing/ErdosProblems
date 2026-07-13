# RESULT — canonical N=2943 all-anchor R29 fixture

## Verdict

Recovered and replayed exactly. The canonical object is the deterministic return value of `tmp/fanout/r29_gate/lead/r29_lead_gate.py:build()`, not the absent historical `00186166...` artifact. Its canonical payload SHA256 is `fc4f3ab94bed810669976b1fdb21743fdd4ebe57eea15ef52afcfc2165e2fb1f`.

`fixture.json` is the full recovered fixture: all 1,383 selected rows, all 676 labelled selector anchor rows and atoms, all 2,127 selected vertices, the 2,943-bit maximum-cut shore, all active/demanded edges and components, all 704 outside components with attachments, scoped demands, reservations, and hub shore. SHA256: `b8a9b57d5a37918f1b5ee1b33266d3c74fe86e461b6715ca0d47252e2018b05c`.

## Exact constructor

- Vertices `0,1,2` are `r,c_l,c_r`; traffic leaves are `3..28` and `29..54`; anchor is `55`.
- Traffic contributes all `26*26=676` rows `(u,1,0,2,v)` and all 676 left/right bad pairs.
- For each of the 52 traffic leaves, 26 arms `(leaf,x,y,55)` are added: 1,352 arms and 2,704 arm vertices `56..2759`.
- Each side splits its 676 arms into two blocks of 338. For cyclic `j`, the displayed selector path is `(q,xF_j,yF_{j+1},xD_j,yD_{j+1})`, its bad atom is `{q,yD_{j+1}}`, and its stored baseline row is the reversal. Here `q=2760,2761`.
- The all-anchor replacement is exactly `(yD_{j+1},55,yF_{j+1},xF_j,q)` for every one of the 676 selectors (row indices `676..1351`).
- `add_circuit` starts at 2762 and ends at 2928; cable vertices are 2929,2930; three 4-vertex seed paths end at `N=2943`.
- Total: blue `7039`, bad `1383`, graph edges `8422`, rows `1383 = 707 rigid + 676 selector`.

## Recovered counts

- All-anchor tuple: 1,383 rows, 2,127 selected vertices, exact scoped score 23,115 (`collision=23,108`, `HitNeed=7`).
- Maximum cut: exactly 7,039. Disjoint upper/attaining classes: traffic 4,110; selectors 2,704; seeds 12; circuit 207; cable 6. The verifier enumerates 11,664 traffic quotient cases.
- Selected active-edge graph: 1,370 edges and 757 components; exactly one component is active, containing the 19 active vertices `[0,1,2,55,2762,2763,2764,2765,2766,2771,2772,2773,2774,2780,2781,2782,2783,2929,2930]`.
- Demanded active edges: 18.
- Outside selected scope: 816 vertices in 704 components; size histogram `{1:676,5:28}`.
- Hub shore is owners `{0,1,2}`. Each owner has collision 6,650 and HitNeed 1, hence demand 6,651 half-slots; total demand is 19,953.
- Reservations are exactly ordered cells `(0,55)`, `(1,2929)`, `(2,2930)`, removing 3 half-slots under the rule “capacity 1 on a demanded active ordered edge; capacity 2 otherwise.”
- Old three-pattern reach is 19,925 half-slots, deficiency 28. Four-pattern reach is 932,525 half-slots: sameFirst 17,325; commonBad 0; rowCompanion 2,600; outsideAttachment 912,600. All eight owner shores have maximum deficiency 0.

## Input artifacts and SHA256

| Bytes | SHA256 | Path |
|---:|---|---|
| 17,640 | `5d29b1d6e35957405c53176fab1fb21660d727cb334a1e20462eb5ebe36678f6` | `tmp/fanout/r29_gate/lead/r29_lead_gate.py` |
| 88,771 | `93d5d64c55338186603b718b5d6bb162d907c4fc868ce276808e01822c395901` | `tmp/fanout/r29_gate/d09/retry2/best_tuple.json` |
| 2,944 | `82b0dee91fdb5e2eaf56b2790c9f14631bad44e3c43d0b00b6d6439c9a6e9755` | `tmp/fanout/r29_gate/d03/retry2/attaining_cut_bits.txt` |
| 1,619 | `6870d083833f1ef354572636d9d9335c202b77e9ff150f8b4b64b5389122035d` | `tmp/fanout/r29_gate/d03/retry2/certificate.json` |
| 9,017 | `ec9526913e2cf7ae513ba83e0b423a989958f212e1764d085d5583c90ae2ac3e` | `tmp/fanout/r29_fullbank/B_fourpattern/certificate.json` |
| 18,779 | `13243e061b11c8f44ff18039795a8516c84c1198f40df85e635f3b43cce4a8ac` | `tmp/fanout/r29_fullbank/B_fourpattern/verify_fourpattern.py` |
| 5,738 | `bc1d7f26c4042c4b7918509574c051d5251e4db0303ef5e77220d52e47c8a020` | `tmp/fanout/r29_fullbank/B_fourpattern/verify_certificate.py` |

These are every external file read by `audit_fixture.py`. The constructor generates graph incidence in memory; there is no separate canonical graph file.

## Exact replay commands

Run from repository root in PowerShell:

```powershell
python tmp/fanout/r29_fullbank/B_fourpattern/worker_1/audit_fixture.py
python tmp/fanout/r29_fullbank/B_fourpattern/verify_certificate.py
python tmp/fanout/r29_gate/d03/retry2/verify_maxcut.py
Get-FileHash -Algorithm SHA256 tmp/fanout/r29_fullbank/B_fourpattern/worker_1/fixture.json
```

Observed first-command counts:

```json
{"active_components":1,"active_edges":1370,"active_vertices":19,"bad_edges":1383,"blue_edges":7039,"demanded_active_edges":18,"fixture_sha256":"b8a9b57d5a37918f1b5ee1b33266d3c74fe86e461b6715ca0d47252e2018b05c","four_pattern_reach_half_slots":932525,"hub_demand_half_slots":19953,"maxcut":7039,"n":2943,"outside_components":704,"outside_vertices":816,"reservations":3,"rigid_rows":707,"rows":1383,"selected_components":757,"selected_vertices":2127,"selector_rows":676}
```

The certificate replay checked 8 shores, 28 explicit repair half-slots, integral flow 19,953, minimum cut 19,953, and maximum deficiency 0. All computations use integers (the pre-existing certificate checker parses displayed rationals with `fractions.Fraction`); no floating-point operations are used.
