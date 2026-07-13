# Worker 7 adversarial result

## Verdict

The claimed outsideAttachment reach `912600` and four-pattern reach `932525` are false under the literal canonical R23 transfer specification in `WALL_ATTACK_R23_GPTPRO56.md`, which requires `comp(a)=comp(v)=comp(b)`. All three owners lie in selected active-component `0`, of size `19`. Every relaxed attachment witness lies instead in one of selected active-components `14..26` or `40..52`. Thus component-scoped eligible outside vertices are `0` for each owner, not `676`.

With that R23 scoping clause enforced, outsideAttachment contributes `0` half-slots. After source deduplication and the three reservations, reach is `19925` against demand `19953`; the full owner shore has deficiency `28` and network cut capacity `19925`. Hence no full flow or valid min-cut certificate exists for the component-scoped four-pattern relation.

The larger counts are exactly reproducible only for the relaxed relation that omits the component equalities: `456300` ordered outside cells, `912600` new half-slots, total reach `932525`, and minimum cut `19953` at the empty shore.

## Independent reconstruction counts

- Tuple rows: `1383`; selector rows: `676`; tuple rows equal canonical anchor rows: yes.
- Selected vertices: `2127`; active vertices: `19`; active edges: `1370`; demanded active edges: `18`.
- Per owner: collision `6650`, HitNeed `1`, demand `6651`; total demand `19953`.
- Outside vertices: `816`; outside blue components: `704`; sizes: `676` of size `1`, `28` of size `5`.
- Old unique ordered cells after cross-pattern deduplication: `9964`.
- Reservations: `(0,55)`, `(1,2929)`, `(2,2930)`; capacity removed: `3` half-slots.
- Old capacity by owner mask: `1:5775`, `2:5775`, `4:5775`, `7:2600`; total `19925`.
- Relaxed eligible outside vertices per owner: `676`; component-scoped eligible outside vertices per owner: `0`.
- Component-scoped eight shore deficiencies, masks `0..7`: `0,-1724,-1724,-848,-1724,-848,-848,28`.
- Component-scoped eight network cut capacities, masks `0..7`: `19953,21677,21677,20801,21677,20801,20801,19925`.

## Exact commands and outcomes

From `E:\Projects\ErdosProblems`:

```powershell
python tmp\fanout\r29_fullbank\B_fourpattern\worker_7\audit.py
```

Exit `0`; wrote `audit.json`; produced all counts above using integer arithmetic only.

```powershell
python tmp\fanout\r29_fullbank\B_fourpattern\verify_certificate.py
```

Exit `1` at line `48`, where the verifier still asserts per-pattern half-slots `[17325,0,2600,912600]`. The current shared certificate instead records component-scoped `[17325,0,2600,0]` and full-shore deficiency `28`.

```powershell
Get-FileHash -Algorithm SHA256 tmp\fanout\r29_fullbank\B_fourpattern\worker_7\audit.py,tmp\fanout\r29_fullbank\B_fourpattern\worker_7\audit.json,tmp\fanout\r29_fullbank\B_fourpattern\certificate.json
```

## SHA256

- `audit.py`: `25d2767abdbbaadb89cda0596eb8d9cc7feeb0e8eaa411f23a6079702ddbef52`
- `audit.json`: `ac74aa38dfa6d6c8146d43dc1b807ece8627fbca06494f04a82b49e16a72dfc2`
- canonical lead: `5d29b1d6e35957405c53176fab1fb21660d727cb334a1e20462eb5ebe36678f6`
- all-anchor tuple: `93d5d64c55338186603b718b5d6bb162d907c4fc868ce276808e01822c395901`
- current shared certificate observed by final audit: `85e72f7775730fb559c6a441cc23e2d7f2df982f174c0330f83d5dfda6143ce9`
- R20 spec: `cc4f42d19203a91ca4663a67c51cb1cb01273c442eaee733bf9dce94bb3b29f5`
- R23 spec: `45e6533b1cb670ebb8476998bee9904ad0ec8f8943c2753b78a677827358c9d3`
- R29 gate text: `fff06d97f2e574fe2d66b9cea4f3bc4244037a92eb8ed5bd363eca73c8591b04`

During the audit the shared certificate changed from observed SHA256 `ec9526913e2cf7ae513ba83e0b423a989958f212e1764d085d5583c90ae2ac3e` to `85e72f7775730fb559c6a441cc23e2d7f2df982f174c0330f83d5dfda6143ce9`; worker 7 did not write outside its assigned directory.

## Narrowest defensible statement

For the reconstructed R29 all-anchor tuple and the R23 relation exactly as written with attachment-witness component equalities, the fourth pattern adds no legal source capacity and the three-owner shore retains exact Hall defect `28`. If those component equalities are intentionally deleted from the specification, the relaxed `932525` reach count is arithmetically correct, but it certifies a different relation.
