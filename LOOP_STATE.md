# LOOP_STATE.md — volatile loop state (UPDATE EVERY TICK; the /loop text never changes)
# Last update: 2026-07-04T07:05Z (commit 569a605a0; P(math)~86, P(Lean)~78)

## MAILBOX
- CODEX_TO_CLAUDE.md read marker (bytes): 1603048
- My outbox: coordination/CLAUDE_TO_CODEX.md (append-only)

## GPT-PRO THREADS (thread URLs stable; tab IDs go stale — find or recreate via tabs_context/tabs_create)
- MAIN    (theorem design):   https://chatgpt.com/c/6a450f06-be68-83eb-b6f4-5b855434e550  [last tab 1267096304]
- SIBLING (writeup + second): https://chatgpt.com/c/6a45e152-8de4-83eb-9aa3-87cb13427526  [last tab 1267096303]

## IN FLIGHT (what each worker is doing right now)
- MAIN: O5 T=1 REC formal artifact spec (inventory, checker obligations, |T|=1 assembly, worked micro-example)
- SIBLING: paper section 2.1 (Branch-A head: C5-RS + mask trichotomy + GERSH_L5 derivation)
- CODEX: EQ-ODL1 rung-2 chart builder + Bernstein triviality sweep over 300 charts; Farkas replay of restricted
  infeasibility; full-cone sizing probe; digit-verify seed-ray inputs. Then: B0-4 lens gates, SB-1 SIB provenance,
  A1 six cones, CombinedHBD re-gate, ambient-eta audit.

## RETASK QUEUES (feed a new task the moment a worker goes idle)
- MAIN queue: O16/O18 AM master-cube emission spec refresh; review my Assembly.lean Bank0Statement skeleton
  (write it first); T=2 corridor cert emission spec (O6); next per critical paths A-D.
- SIBLING queue: paper sections 2.2 (Bank0 integration), then 3.x Branch-B head, then appendices per assembly plan.

## EXTRACTION QUEUE (replies landed in sibling thread, not yet saved to files)
- 1.1+1.2 (5618c, ~4 replies back)  -> problems/23/writeup/PAPER_SECTIONS_GPTPRO.md
- 1.3 (7867c, ~2 back)              -> same file
- assembly plan (19210c)            -> problems/23/writeup/DOCUMENT_ASSEMBLY_PLAN_GPTPRO.md
- E1-E7 Branch-A errata (9738c)     -> problems/23/writeup/BRANCH_A_ERRATA_GPTPRO.md

## LEAN (14 files, all green; build: cd E:\Projects\ErdosProblems\formal-conjectures; lake env lean <abs path>)
- Done: Skeleton, Darts, Distances, Gamma, Row, BankL, BranchAInterface, PacketExchange, CDCore,
  PolyCert (NF+checkEq+PosCert+ConeCert), Bank0Algebra (bank_amgm+blocks_to_global), CertGraph (L0-L3).
- NEXT (blueprint order): BankBlocks checker -> CorridorPartition -> CrossCap -> ClosureTrace -> LensGates ->
  Seed10/SevenCutCone -> Assembly (Bank0Statement, strong induction on N).

## MASTER LEDGER (the single source of open obligations)
- WRITEUP_REDTEAM_GPTPRO.md tail: Bank0 B0-B10 + ODL O0-O21 + chain T0-T3 + critical paths A-D + DoD.
- PROVEN: B0,B7,L7,L8,LemmaA,O1-O3,O8-O10,O12,O15,T0(cond), EQ-ODL1 equality stratum.
- CERT-PENDING: B1-B6,B10,O4(O5,O6),O11,O13,O14(rung-2 live),O16-O21.  HUNT: O7 (clean N<=11).
