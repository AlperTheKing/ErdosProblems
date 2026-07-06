# Erdős #23 δ=0 — Honest Ledger Status (2026-07-06T16:25Z)

Grounded status of every terminal-condition component. Each row cites the verifiable
evidence (compiled Lean theorem name in `CertGraph.lean`, or exact artifact/manifest).
**Distinction enforced:** a *checker soundness theorem* being PROVEN-in-Lean means the
checker is sound; it does NOT by itself certify any particular graph — the per-graph
certificate DATA (bank blocks, route trees, chart rows) is supplied separately and must
be exact-verified. This is the anti-fake-progress boundary.

## CONJUNCT 4 — Lean skeleton (MOST ADVANCED)

| Component | Status | Evidence |
|---|---|---|
| Official FC-shape bridge | **PROVEN** | `erdos23_fcForm_of_bipartization` (FCBridge.lean), unconditional, commit 075a5c0c6 |
| betaSimple → bipartite subgraph | **PROVEN** | `SimpleGraphBridge.beta_bipartization`, commit 641315eda |
| Whole-chain axioms | **CLEAN** | `#print axioms erdos23_fcForm_of_bipartization = [propext, Classical.choice, Quot.sound]` |
| erdos23_delta0 (given package) | **PROVEN** | `erdos23_delta0` / `erdos23_delta0_simpleGraph_from_package` |
| Assembly stages 1–7 | **GREEN** | encoding-facts total, CutFn bridge total, BConnected discharge, good-cut assembly, finite max-cut existence |
| **Package `good` (TRUE-max cut) for a GENERAL graph** | **OPEN (M6)** | needs general provider via `checkOddCyclePacking_sound` (checker PROVEN; general construction open) |
| **Package `delta` (Branch-A/B bundles) for a GENERAL graph** | **OPEN (M7)** | needs chart certs (Conjunct 1) instantiated as bundle data |

## CONJUNCT 1 — Branch A (L=5)

### Bank0 checker program (B-nodes) — checker PROVEN-in-Lean
| Node area | Status | Evidence (compiled theorem) |
|---|---|---|
| Bank0 dispatch capstone | **PROVEN** | `bank0_of_maxcut` (checkers + top-level σ≥0 ⟹ 25·badCount ≤ n²) |
| Bank0Cert soundness | **PROVEN** | `bank0Cert_sound` |
| GlobalC5 (C5-hom bank) | **PROVEN** | `globalC5_bound` (25·badCount ≤ n², self-closing AM-GM) |
| BankBlock cover | **PROVEN** | `coverBound` (unconditional 25m ≤ n²) |
| NCH bank routing | **PROVEN** | `nchBank_sound` |
| CrossCap / partition | **PROVEN** | `crossCap_sound`, `partition_crossCap_sound`, `bank0Cross_sound` |
| ClosureTrace | **PROVEN** | `bankClosureTrace_sound` |
| Peel + SigmaChain | **PROVEN** | `sigmaChain_of_sigmaNonneg` (structural recursion; no per-level hyps) |
| etaNonneg from Bank0 | **PROVEN** | `etaNonneg_of_bank0` |
| **Per-graph bank certificate DATA** | supplied by `delta` | chart rows / seed bank certs (see chart batch) |

### ODL checker layer (O-nodes)
| Node area | Status | Evidence |
|---|---|---|
| Full-mask ⟹ C5-RS | **PROVEN** | `fullMaskBound_of_odlFull` |
| OddCyclePacking (TRUE-max) | **PROVEN** | `checkOddCyclePacking_sound` ⟹ IsMaxCut, unconditional |
| Lens switch/primitive/label/forbid/OSC | **PROVEN** | `checkLensSwitch_sound`, `checkPrimitiveLens_sound`, `checkLabelCert_sound`, `checkForbidCert_sound`, `checkOSCCert_sound` |
| LensGates dispatch | **PROVEN modulo geometry** | `checkLensGates_sound` takes `LensGateGeomSound` hypothesis |
| **LensGateGeomSound (4 fields)** | **OPEN** | cross/label/forbid/osc geometry — MAIN designing NOW (retasked 16:20Z) |
| Seed3 route tree | **PROVEN** | `checkSeed3RouteTree_sound`, `checkSeed3RouteTree_case_resolved`, coverage/shape lemmas |

### Chart batch (108 rows)
| | Count | Status |
|---|---|---|
| Certified (exact artifact + SHA) | **45** | ledger v43, exact_ok=true manifests |
| Pending (all hybrid-class) | **63** | Codex Farkas-pricing CG in flight (k6/F6 calibration) |
| Falsified | **0** | no chart row shown false |
| O14 chart-cover assembly | SPEC | archived (EQ_ODL1_O14_ASSEMBLY_GPTPRO.md); blocked on full 108 |
| Seed3 completeness | design PROVEN | width bounds certificate-backed (SEED3_COMPLETENESS_GPTPRO.md) |

## CONJUNCT 2 — Branch B (L>5)
| Component | Status | Evidence |
|---|---|---|
| M3 transpiler (dictionary audit) | **audit-green** | 14247 rows, 29 shards in repo, 0 forbidden tokens |
| M4 bridge (RowPilot → BranchBInputs) | **PROVEN** | `branchBInputs_of_rowPilot` (Cert/BranchBBridge.lean, cf00bd268) |
| Banked-UPO / CombinedHBD / CD telescope / 24-sig dictionary | SPEC/design | archived (BRANCH_B_ERRATA_GPTPRO.md E2–E7); per-node PROVEN/CERTIFIED status = **NOT yet closed** |

## CONJUNCT 3 — Exact verification + anti-fake gate
| | Status |
|---|---|
| Per-row exact re-verification (repaired/hard + ~1-in-10) | ONGOING (10+ personal re-verifies logged) |
| **Full aggregate re-verification from SHA-pinned manifests** | **NOT DONE** (endgame step; requires 108/108) |
| Anti-fake gate (M6/M7 via compiled lemmas only) | ENFORCED |

## HEADLINE
- Conjunct 4 Lean **skeleton + official bridge**: DONE (sorry-free, axioms clean).
- Bank0 + most ODL **checkers**: PROVEN-in-Lean.
- **Genuinely open**: (a) LensGateGeomSound geometry [MAIN, in flight]; (b) 63 hybrid chart
  certs [Codex Farkas-CG, in flight]; (c) Branch-B per-node closure; (d) M6/M7 general
  package construction; (e) full aggregate manifest re-verification (endgame).
- No falsifier. The bottleneck is certificate DATA (Conjuncts 1–3), not the deductive skeleton.
