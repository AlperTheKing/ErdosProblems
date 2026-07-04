# LOOP_STATE.md — volatile loop state (UPDATE EVERY TICK; the /loop text never changes)
# Last update: 2026-07-04T08:00Z (P(math)~86, P(Lean)~78)

## MAILBOX
- CODEX_TO_CLAUDE.md read marker (bytes): 1604720
- My outbox: coordination/CLAUDE_TO_CODEX.md (append-only)

## GPT-PRO THREADS (thread URLs stable; tab IDs go stale — find or recreate via tabs_context/tabs_create)
- MAIN    (theorem design):   https://chatgpt.com/c/6a450f06-be68-83eb-b6f4-5b855434e550  [last tab 1267096304]
- SIBLING (writeup + second): https://chatgpt.com/c/6a45e152-8de4-83eb-9aa3-87cb13427526  [last tab 1267096303]

## IN FLIGHT
- MAIN: O16/O18 EQ+SIB passive-AM master-cube emission spec (per-template inequality, tau map,
  BernsteinCube cells, 11 EQ + 13 SIB template enumeration, 27x fallback, verified-template reuse).
- SIBLING: paper section 3.1 (Branch-B head: Banked-UPO + Bank-L + CombinedHBD chain + packet exchange).
- CODEX: rung-2 chart builder + Bernstein triviality sweep over 300 charts (report stats); then O5-EMIT
  (T=1 REC artifacts from zeta-sweep instances per archived spec), B0-4 lens gates, SB-1, A1 six cones.

## RETASK QUEUES
- MAIN queue: review my Assembly.lean Bank0Statement skeleton (write it first); T=2 corridor cert
  emission spec detail (O6) if lens-gate work surfaces gaps; then per critical paths A-D.
- SIBLING queue: sections 3.2+ (Branch-B certificate details), 4.x (NCH/G1'), appendices
  (cert ledger, validation) per assembly plan.

## EXTRACTION QUEUE (landed in threads, not yet saved to files)
- sibling 1.1+1.2 (5618c)            -> problems/23/writeup/PAPER_SECTIONS_GPTPRO.md
- sibling 1.3 (7867c)                -> same
- sibling 2.1 (3914c; head captured) -> same
- sibling assembly plan (19210c)     -> problems/23/writeup/DOCUMENT_ASSEMBLY_PLAN_GPTPRO.md
- sibling E1-E7 errata (9738c)       -> problems/23/writeup/BRANCH_A_ERRATA_GPTPRO.md

## LEAN (14 files green; build: cd E:\Projects\ErdosProblems\formal-conjectures; lake env lean <abs path>)
- Done: Skeleton, Darts, Distances, Gamma, Row, BankL, BranchAInterface, PacketExchange, CDCore,
  PolyCert (NF+checkEq+PosCert+ConeCert), Bank0Algebra, CertGraph (L0-L3 incl nu0_append).
- NEXT: BankBlocks checker (BankBlock struct + obligations + wire bank algebra) -> CorridorPartition ->
  CrossCap -> ClosureTrace -> LensGates -> Seed10/SevenCutCone -> Assembly (Bank0Statement, strong
  induction on N per T=1/blueprint specs; T1Instance/RECCert structures now specified too).

## MASTER LEDGER (single source of open obligations)
- WRITEUP_REDTEAM_GPTPRO.md tail: Bank0 B0-B10 + ODL O0-O21 + chain T0-T3 + paths A-D + DoD.
- PROVEN: B0,B7,L7,L8,LemmaA,O1-O3,O8-O10,O12,O15,T0(cond), EQ-ODL1 equality stratum (end-to-end:
  my algebra gate + Codex digit-verified inputs). O5 design DONE (spec + verified micro-example).
- CERT-PENDING: B1-B6,B10,O4(O6),O5-EMIT,O11,O13,O14(rung-2 charts),O16-O21.  HUNT: O7.
- Certified negative datapoint: EQ-ODL1 restricted support F1-F4+B0 Farkas cert exact (ok=true).
- Full rung-1 cone = 1,755,182 columns (not launched; rung-2 primary).
