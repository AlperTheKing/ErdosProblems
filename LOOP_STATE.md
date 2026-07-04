# LOOP_STATE.md — volatile loop state (UPDATE EVERY TICK; the /loop text never changes)
# Last update: 2026-07-04T08:50Z (P(math)~86, P(Lean)~79)

## MAILBOX
- CODEX_TO_CLAUDE.md read marker (bytes): 1604720
- My outbox: coordination/CLAUDE_TO_CODEX.md (append-only)

## GPT-PRO THREADS (thread URLs stable; tab IDs go stale — find or recreate via tabs_context/tabs_create)
- MAIN    (theorem design):   https://chatgpt.com/c/6a450f06-be68-83eb-b6f4-5b855434e550  [last tab 1267096304]
- SIBLING (writeup + second): https://chatgpt.com/c/6a45e152-8de4-83eb-9aa3-87cb13427526  [last tab 1267096303]

## IN FLIGHT
- MAIN: ASSEMBLY THEOREM REVIEW (my A/B/C decisions: RowsComplete Prop-vs-checker; IsMaxCut/
  GammaMinimal Prop forms + the flip-counting lemma blueCount(flip) = blueCount - dB + dM proof
  sketch; T0/T1 Lean statement shapes + final statement list to type).
- SIBLING: paper section 4.1 (NCH/pruning: Bank0-vs-ODL roles, NCH-def, Terminal-Hall T=1/T=2,
  AmbientPrune, hunt status + contingency).
- CODEX: rung-2 chart sweep (300 charts, stats pending); then O5-EMIT (T=1 REC artifacts),
  O16/O18-EMIT (master cubes, order EQ V2 -> V1 -> V3 -> SIB V2 -> V1 -> V3), B0-4 lens gates,
  SB-1, A1 six cones.

## RETASK QUEUES
- MAIN queue: T=2 corridor cert emission spec detail (O6) if gaps surface; O11 2Door / O13 Seed3
  emission spec refresh if Codex hits ambiguity; per critical paths A-D.
- SIBLING queue: sections 3.2+ (Branch-B cert details), 5.x appendices (cert ledger, validation),
  definitions-table finalization per assembly plan.

## EXTRACTION QUEUE (landed in threads, not yet saved to files)
- sibling 1.1+1.2 (5618c)            -> problems/23/writeup/PAPER_SECTIONS_GPTPRO.md
- sibling 1.3 (7867c)                -> same
- sibling 2.1 (3914c; head captured) -> same
- sibling 3.1 (4541c)                -> same
- sibling assembly plan (19210c)     -> problems/23/writeup/DOCUMENT_ASSEMBLY_PLAN_GPTPRO.md
- sibling E1-E7 errata (9738c)       -> problems/23/writeup/BRANCH_A_ERRATA_GPTPRO.md

## LEAN (14 files green; build: cd E:\Projects\ErdosProblems\formal-conjectures; lake env lean <abs path>)
- Done: Skeleton, Darts, Distances, Gamma, Row, BankL, BranchAInterface, PacketExchange, CDCore,
  PolyCert (NF+checkEq+PosCert+ConeCert), Bank0Algebra, CertGraph (L0-L3 + B6 BankBlocks checker:
  checkBankBlock + product/disjointness fact-extraction).
- NEXT: CorridorPartition checker (O1-O5 obligations over lists; additivity already proven as
  nu0_append) -> CrossCap -> ClosureTrace -> LensGates -> Seed10/SevenCutCone -> Assembly
  (await main-thread review verdicts on A/B/C before typing Bank0Statement).

## MASTER LEDGER (single source of open obligations)
- WRITEUP_REDTEAM_GPTPRO.md tail: Bank0 B0-B10 + ODL O0-O21 + chain T0-T3 + paths A-D + DoD.
- PROVEN: B0,B7,L7,L8,LemmaA,O1-O3,O8-O10,O12,O15,T0(cond), EQ-ODL1 equality stratum end-to-end.
- DESIGN DONE (specs archived, emission pending): O5 (T=1 REC + verified micro-example),
  O16/O18 (master cubes, 3x11 EQ + 3x13 SIB templates explicit). PROGRAM 100% SPECIFIED.
- CERT-PENDING: B1-B6,B10,O4(O6),O5-EMIT,O11,O13,O14(rung-2 charts),O16-O21-EMIT.  HUNT: O7.
- Certified negative datapoint: EQ-ODL1 restricted F1-F4+B0 Farkas cert exact.
- Full rung-1 cone = 1,755,182 columns (not launched; rung-2 primary).
