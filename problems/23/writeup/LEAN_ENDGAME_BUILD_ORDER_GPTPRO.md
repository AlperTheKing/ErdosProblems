# LEAN ENDGAME BUILD-ORDER CHECKLIST (GPT-Pro MAIN, 2026-07-07) — the definitive dependency DAG

Delivered by MAIN (fresh thread https://chatgpt.com/c/6a4c8b1a-439c-83eb-8f49-427107d01d61,
last assistant message, 23298 chars; full per-module Imports/Depends/Emits specs in-thread — extract
each module's spec at its build time). Build RULE (strict layering):

  green base modules
    -> reusable certified checker/soundness modules
    -> O14 emitted data modules
    -> O14 chart-cover -> odl_full
    -> delta=0 assembly
    -> FCBridge to official erdos_23

  INVARIANT: No checker module imports emitted data. Data modules import checkers only.
  Final assembly imports data. (This is the anti-circularity / anti-fake-progress guard.)

## Section 0 — Existing green base modules (00-18) [DONE, treated as fixed green deps]
00 Skeleton, 01 Darts, 02 Distances, 03 Gamma, 04 Row, 05 BankL, 06 BranchAInterface,
07 PacketExchange, 08 CDCore, 09 PolyCert, 10 Bank0Algebra, 11 CertGraph, 12 ODLFull,
13 GammaAggregation, 14 CSPResolution, 15 FCBridge, 16 Seed3Door, 17 A1MaskSymmetry, 18 A1ProperWrapper

## Section 1 — New reusable checker/soundness modules  [BUILDABLE NOW, not 108-gated]
19 NCHMultiTermCert   (imports CSPResolution, PolyCert, ODLFull; deps checkCSPResolutionCert, ConeCert, ...)
20 Seed3RouteTree

## Section 2 — New Branch-B checker stack  [BUILDABLE NOW, not 108-gated]  (conjunct 2)
21 BranchB.Basic
22 BranchB.Dict24
23 BranchB.CombinedHBD
24 BranchB.CDTelescope
25 BranchB.BankedUPO
26 BranchB.Provider
27 BranchB.ODLBridge   <-- WRITTEN by Claude (Erdos23Delta0/BranchB/ODLBridge.lean), source-correct vs real API, build queued

## Section 3 — ODL provider stack  [BUILDABLE NOW]
28 ODLFullProvider

## Section 4 — O14 chart-cover -> odl_full stack  [coverage/assembly theorems conjunct-1 requires; AT-RISK node]
29 O14.EQODL1CoverCert       (STRUCTURAL coverage, must NOT be census/enumeration)
30 O14.ChartCoverToODLFull

## Section 5 — O14 emitted data modules  [GATED ON 108 CERTS]
31 O14.Data.Context, 32 O14.Data.BranchACones, 33 O14.Data.NCHCerts, 34 O14.Data.M6ChargeCerts,
35 O14.Data.BranchB.Dict24, 36 O14.Data.BranchB.HBD, 37 O14.Data.BranchB.CD, 38 O14.Data.BranchB.UPO,
39 O14.Data.BranchB.Provider, 40 O14.Data.Seed3RouteTrees, 41 O14.Data.ODLProvider,
42 O14.Data.Coverage, 43 O14.Data.All

## Section 6 — O14 odl_full theorem
44 O14.O14ODLFull

## Section 7 — Delta=0 assembly
45 Delta0.Assembly

## Section 8 — FC bridge to official Erdos 23
46 Official.Erdos23   (betaSimple => official exists-bipartite-subgraph form; = existing FCBridge shape)

## Sections 9-10 (in-thread): full dependency DAG (compact) + minimal final theorem chain.

### STRATEGY NOTES (Claude)
- Buildable NOW without the 108 certs: modules 19-30 (checkers + Branch-B stack + providers + chart-cover
  cert TYPES). Their per-row/per-instance DATA (section 5) is what waits for 108. So the checker+soundness
  layer can be fully compiled+axiom-audited in parallel with Codex's chart-8 finish.
- Module 27 (ODLBridge) already written; needs 21-26 below it for hBankedUPO. Real API surface (env-based,
  NOT GPT's invented Ctx) documented in BRANCH_B_LEAN_LAYERS_GPTPRO.md.
- CRITICAL at-risk node: 29 EQODL1CoverCert must be STRUCTURAL coverage (memory: census-only => residual
  infinite obligation). This is the conjunct-1 coverage theorem the /goal demands.
- Honest builds only: compile in dep order into a tmp olean tree; EXIT=0 + empty log + sorry/axiom grep.
