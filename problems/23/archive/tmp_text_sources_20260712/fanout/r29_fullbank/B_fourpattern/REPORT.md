# R29 all-anchor exact four-pattern hub-shore audit

## Verdict

The defect `28` survives the exact R20/R23 four-pattern relation.

The decisive R23 condition is the attachment-witness component equality
`comp(a)=comp(owner)=comp(b)` in `WALL_ATTACK_R23_GPTPRO56.md:9-11`.
The existing Python gate
`_codex_r23_outside_attachment_full_obligation_gate.py` omits this condition.
Its relaxed relation produces 912,600 extra half-slots, but those sources are
not legal under the written R23 specification.

For the component-scoped relation, `outsideAttachment` contributes zero.
The hub shore `{0,1,2}` therefore retains demand 19,953, reach 19,925, and
defect 28. This lane makes no claim about Door, vertexSlack, c5Base, prune, or
the complete FullBank sink accounting.

## Canonical tuple

- Canonical payload SHA256:
  `fc4f3ab94bed810669976b1fdb21743fdd4ebe57eea15ef52afcfc2165e2fb1f`.
- Constructor SHA256:
  `5d29b1d6e35957405c53176fab1fb21660d727cb334a1e20462eb5ebe36678f6`.
- All-anchor tuple SHA256:
  `93d5d64c55338186603b718b5d6bb162d907c4fc868ce276808e01822c395901`.
- `N=2943`, blue edges `7039`, bad edges and rows `1383`.
- Selected vertices `2127`; selected off-support components `757`.
- Active vertices `19`; active edges `1370`; demanded active edges `18`.
- All-anchor active-scoped score `23115`.
- Outside vertices `816` in `704` components: `676` singletons and `28`
  components of size five.

Each hub has collision demand `6650` and HitNeed `1`, hence demand `6651`.
The hub component has root `0` and size `19`.

## Source decomposition

All counts are atomic ordered FreeHalf units. At `K=1`, each unit has rational
capacity `1/2`.

| Pattern | New ordered cells | New half-slots |
|---|---:|---:|
| sameFirst | 8,664 | 17,325 |
| commonBad | 0 | 0 |
| rowCompanion | 1,300 | 2,600 |
| outsideAttachment | 0 | 0 |
| Union | 9,964 | 19,925 |

The raw sameFirst capacity is `8664*2=17328`. Reservations remove half zero
from exactly `(0,55)`, `(1,2929)`, and `(2,2930)`, giving `17325`.
Row-companion cells are shared by all three owners and contribute 2,600 once,
not once per owner. The capacity histogram by owner mask is:

```text
mask 1: 5775
mask 2: 5775
mask 4: 5775
mask 7: 2600
```

Without the component test, each owner sees 676 singleton outside components
and `676*675*2=912600` half-slots. Every co-occurring attachment witness is in
a selected off-support component different from the hub component. With
`comp(a)=comp(owner)`, strict eligible outside vertices are `0,0,0`.

The exact rational hub-shore values at `K=1` are:

```text
demand = 19953/2
reach  = 19925/2
defect = 14
```

## Min-cut certificate

For shore mask `S`, the network cut is
`19953 - demand(S) + reach(S)`. Exhausting all eight masks gives:

| Mask | Demand | Reach | Deficiency | Cut |
|---:|---:|---:|---:|---:|
| 0 | 0 | 0 | 0 | 19953 |
| 1 | 6651 | 8375 | -1724 | 21677 |
| 2 | 6651 | 8375 | -1724 | 21677 |
| 3 | 13302 | 14150 | -848 | 20801 |
| 4 | 6651 | 8375 | -1724 | 21677 |
| 5 | 13302 | 14150 | -848 | 20801 |
| 6 | 13302 | 14150 | -848 | 20801 |
| 7 | 19953 | 19925 | 28 | 19925 |

Thus the minimum cut is the full hub shore, with capacity 19,925. The
certificate also gives an aggregate flow of value 19,925, proving the cut is
tight.

## Portfolio audit

Seven focused descendants were launched. Workers 1, 3, 4, 5, and 6 reproduced
the relaxed Python relation and reported 932,525 reach. Worker 2 documented the
same code/text mismatch but treated the component wording as bookkeeping.
Worker 7 enforced the literal R23 conjunct and independently obtained:

```text
strict outside reach = 0
total reach = 19925
minimum cut = 19925
maximum deficiency = 28
```

The corrected primary verifier and its separate certificate checker match
worker 7 exactly. The relaxed outputs are retained as negative audit evidence:
they show precisely what changes if the R23 component condition is deleted.

## Replay

Run from the repository root:

```powershell
python tmp/fanout/r29_fullbank/B_fourpattern/verify_fourpattern.py
python tmp/fanout/r29_fullbank/B_fourpattern/verify_certificate.py
python tmp/fanout/r29_fullbank/B_fourpattern/worker_7/audit.py
python -m py_compile tmp/fanout/r29_fullbank/B_fourpattern/verify_fourpattern.py tmp/fanout/r29_fullbank/B_fourpattern/verify_certificate.py
Get-FileHash -Algorithm SHA256 tmp/fanout/r29_fullbank/B_fourpattern/*
```

Primary verifier output:

```json
{"demand":19953,"four_pattern_reach":19925,"maximum_deficiency":28,"min_cut":19925,"old_defect":28,"old_reach":19925,"outside_reach":0,"score":23115}
```

Verifier SHA256:
`3d9ae4475a6cee19294a93ee1aa877719c79889d1aedf8c1abeff46284f55b64`.
Certificate checker SHA256:
`a172602dd873631b099889023a51d59c94abd06b2ba45776dd0e4f703b693d7b`.
Certificate SHA256:
`604493eab501d46b66eb23eeb3e8071bff12d9f21efd5eef3cb8bd0fda6d24ed`.
Independent worker-7 audit SHA256:
`25d2767abdbbaadb89cda0596eb8d9cc7feeb0e8eaa411f23a6079702ddbef52`.

## Smallest falsifier statement

Let `omega_A` be the canonical all-anchor R29 tuple on the payload above and
let `W={0,1,2}`. For the R20/R23 relation
`sameFirst union commonBad union rowCompanion union outsideAttachment`, with
the R23 attachment component equalities and active half-zero reservations,

```text
D_omega_A(W) = 19953 > 19925 = Reach_omega_A(W).
```

Hence no injective four-pattern FreeHalf transfer covers the hub obligations;
the exact Hall defect is 28 half-slots, or rational mass 14 at `K=1`.
