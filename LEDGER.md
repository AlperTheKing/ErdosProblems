# Erdos Hunter Ledger

Last updated: 2026-06-11 Europe/Istanbul

Status labels:

- ACTIVE: current target.
- SOLVED-PARTIAL-NOVEL: verified novel partial result, not full problem resolution.
- PARKED: useful work exists but not currently the easiest target.
- HARD: avoid unless a new concrete idea appears.
- DEAD: do not revisit without external new information.

## Entries

| Problem | Status | Reason |
|---|---|---|
| #23 | ACTIVE | Novel finite result `a(25)=25` proved and PR #4216 opened to formal-conjectures; resume now that #944 is parked, to test whether the method scales via `a(30)=36` certificate or a medium-density stability theorem. |
| #203 | DEAD | Seeded from prior work; do not revisit. |
| #488 | HARD | Seeded OPEN-HARD; avoid. |
| #617 | PARKED | Prior counterevidence exists; resume only if certificate/disproof path becomes clearer. |
| #835 | PARKED | Seeded parked. |
| #944 | HARD/PARKED | Dirac 1970 k=4 / 6-regular `(4,1)` existence. Verified partials: no target on n<=14; no nontrivial 6-edge-cut shore 2..14; Lean core lemmas compile. Verified global lemmas: whole-`H` terminal-list-criticality and boundary-support obstruction for mate Kempe components. GPT Pro and local C++ diagnostics show Kempe accounting/support-criticality do not close K6: support-to-multiplicity fails from current local ingredients, and the remaining trace-domination/synchronisation lemma is a genuine new hard bottleneck. Park unless a concrete proof idea for trace-domination appears. |
| #1212 | SOLVED-PARTIAL-NOVEL | Verified partial results published: formal-conjectures PR #4218 (statement + 7 proven cores); full resolution blocked by open rough-composite max-gap input (R1); teorth/erdosproblems PR #313 LIVE (comments field). |
| #993 | KNOWN | m=2,3 unimodality published (Li 2603.03025, Galvin 2502.10654); Lean artifact parked. |
| #742 | PARKED | n=25 Murty–Simon: open+unscooped but certified SAT search infeasible (~8972 profiles); resume only with structural collapse. |
| #700 | PARKED | Part(b) reduced; closing needs unavailable uniform multi-base carry estimate. |
| #677 | HARD | Infinitary believed-true; cex search negative; Cambie-crowded. |
| #307 | PARKED | Open but locally burned (MITM/GMP FOUND=0); search can only prove YES. |
| #1210 | PARKED | Crowded (May-2026 paper + public sketch); sharp constant = parity barrier. |
| #1206 | HARD | Active Konyagin-school program (arXiv:2602.08807). |
| #1146 | HARD | Ruzsa: "I do not even have a plausible guess". |
| #1145 | HARD | Contains Erdős–Turán as B=A special case. |
| #1100 #1106 #1107 #1108 #1110 #1097 #1101 | HARD/PARKED | See docs_newmath/tried_log.md memos (analytic/contains-famous/folklore-partial). |
| #19 #628 #699 #475 #366 #64 #647 | KNOWN/HARD/PARKED/DEAD | See tried_log.md (EFL proved; Tihany crowded; confirm-only universals; #647 dead). |
