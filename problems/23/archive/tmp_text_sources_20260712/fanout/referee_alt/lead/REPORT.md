# referee_alt lead report

## Accepted exact facts

1. R29's displayed arithmetic is internally consistent: `4110+2704+12+207+6=7039`, `707+676=1383`, `34575/25=1383`, Hall gap `19953-(17325+2600)=28`, score `19953+52*200+458=30811`, and selector count `676*(680-1)=459004`.
2. These equalities do not verify the 2943 graph, its max-cut decomposition, row database, Hall relation, or replacement deltas. No original constructor or full artifact matching claimed SHA prefix `00186166` is present under `problems/23/writeup`; separate fanout lanes later created independent reconstruction/audit artifacts, which are not the claimed source certificate.
3. `CompleteShortestRowDB.rowVerts_nodup` excludes duplicate ordered vertex lists within each bad edge. `checkRow5` separately enforces length 5, in-range vertices, vertex `Nodup`, fixed `u`/`v` orientation, four blue steps, and a bad closing edge. Thus reversed orientation and repeated internal vertices are not hidden survivors of this repair.
4. The repair does not prove that any external/generated database satisfies `rowVerts_nodup`; that remains a constructor obligation. It also does not quotient rows across distinct bad edges, which is correct because `badKeys_nodup` identifies one record per undirected bad edge and row choices are owner-indexed.
5. `MinimumActiveScopedHall` asks only for a matching at the opaque `scopedCanonicalChoice`. R29 prose's “every global minimizer is Hall-good” is strictly stronger. Exact two-state countermodel: scores `(0,0)`, Hall flags `(true,false)`, canonical index `0`.
6. On a finite nonempty choice space, “no Hall-failing global minimizer” is equivalent to “every Hall-failing choice has some strictly lower-score choice.” `exact_audit.py` exhausts all 36 two-state score/Hall models. This equivalence is about all global minimizers, not just the opaque canonical choice.
7. The current Lean API exposes only `scopedCanonicalChoice_optimal`; it exposes no deterministic tie-break. Therefore a proof that merely constructs one Hall-good minimizer cannot discharge the current canonical target. A canonical-minimizer route must either prove every minimizer Hall-good or redefine/select a Hall-good minimizer with a proved tie-break.
8. `ActiveScopedVariationReduction.lean` rebuilt with Lean 4.27.0 against `tmp/claude_lean_o_base_v1`, exit code 0, producing the lane-local olean. The three inspected source files contain no `sorry` or `native_decide` token.

## Dead-list consistency

- R25's three-active internal-killer route, R26's radius-three bridge implication from deficiency, and R27's alternating producer indicator bound are recorded dead by R28. R29 additionally claims the universal Hamming-one scoped-score descent is false.
- R29's local-minimum claim does not falsify the all-global-minimizers Hall theorem unless score `30811` is globally minimal. It also does not falsify `MinimumActiveScopedHall` unless the opaque canonical minimizer is shown Hall-failing.
- No finite LP/Farkas, potential-compression, or component-contraction proof is presently certified in this lane. Active-component deactivation makes the score non-additive across row coordinates; any LP relaxation needs an exact disjunctive encoding or a proved contraction invariant.

## Descendant outcomes

Exactly ten descendants were launched on distinct subproblems. All ten were blocked before file access because the copied CLI could not find sibling `codex-code-mode-host.exe`. Their `final.md` files assert no mathematical claims and are retained verbatim; hashes are in `CHILD_HASHES.txt`. They made no shared-file edits.

## Proof gaps

1. Supply the full 2943 constructor/certificate and full SHA, then independently verify graph validity, max-cut `7039`, Gamma `34575`, row histogram, Hall gap `28`, and all `459004` deltas.
2. Optimize the complete selector-trade space or give a checkable lower-bound certificate. Archive prose is insufficient to decide whether `30811` is global.
3. State the replacement frontier precisely: all-minimizers Hall, existence of a Hall-good minimizer with a new selector, or a deterministic canonical tie-break. These are different Lean interfaces.

## Source hashes

- R25 `50DEB44485A439DC5810AC22FEF972C792CEAC46674A13C3B62789C76F88DC23`
- R26 `80069DDFA9EC0F87098772F914E8B043F431D1AA5E3E7E6B43E51DD96E7AB05E`
- R27 `45986DFD341AB818D41122957C6B6BBD050907C4E585FF6C9E58CF8C7B010991`
- R28 `819D6A3BB2DA534BEB7AC86F8B50E9AB936942893671BCA12C61E027069E42B9`
- R29 `FFF06D97F2E574FE2D66B9CEA4F3BC4244037A92EB8ED5BD363ECA73C8591B04`
- `MinimumDemandCollisionHall.lean` `EA36FC95B8FAD743DC8C11DB510284F6C109CE77319378E47CA56EF40C3EB1A7`
- `ActiveScopedMinimumExchange.lean` `B916318F53D69B4D9ADFF2C4A79B23C139513640F16550DAEA092CE3A9E77982`
- `ActiveScopedVariationReduction.lean` `F3FFD8B22EDD2DE55D53664F20B77651DF4B35033BA3E1ECB5D029AA11F8A921`
