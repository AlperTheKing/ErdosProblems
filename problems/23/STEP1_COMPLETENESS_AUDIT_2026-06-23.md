# Step-1 a(30)<=36 — Adversarial Completeness+Soundness Audit (2026-06-23)

8-agent workflow (wf_5551348b-806), ~1M tokens, adversarial mandate (project has 3 prior false closures).
VERDICT: **a(30)<=36 is NOT proven.** Sound reduction skeleton, materially INCOMPLETE case split, one default cut over-cuts. No beta>=37 witness found anywhere (a(30)=36 not contradicted).

## Per-dimension ledger
| # | Dimension | Status | Sev |
|---|---|---|---|
| 1 | Edge-window 112<=e<=143 (blow-up+BCL) | **PROVEN** | low |
| 2 | Min-degree delta>=8 (exclude r=4,5,6,7) | **GAP** | **fatal** |
| 3 | Rooting/reroot completeness | **GAP** | **fatal** |
| 4 | t=2 K2/T2 387-manifest cert | COMPUTATION_INCOMPLETE | med |
| 5 | t=1 / t=3 branch closure | **GAP** | high |
| 6 | Cut soundness (state_count_6195_cpsat.py) | **GAP** | high |
| 7 | FEASIBLE/UNKNOWN inventory | COMPUTATION_INCOMPLETE | med |

## The decisive findings (corrections to prior optimism)
- **delta>=8 is NOT closed.** The GPT hand-lemmas have real holes: delta_2=2/r=4 written bound **drops the v-A, size-4, and B-B terms** (beta<=25 unproven as written); delta_2=3/r=7 reaches beta<=36 with **ZERO margin** on an unproven "triple-state lemma"; delta_2=1 four-witness cert and delta_2=2 r=6,7 cert are **NOT BUILT**. The only direct campaign (campaign_rooted_r4_9, Jun18-19) produced **0 UNSAT**: c20k = 149/149 INCONCLUSIVE, c200k = 149/149 ERROR (CaDiCaL factor-API crash). So my earlier "r=4,5 closed, gap shrinks to r=6,7" was OVER-OPTIMISTIC.
- **The 387-manifest is delta_2=2 AND min-degree>=8 ONLY** (hardcoded in k2_four_label_profiles.cpp). It gives ZERO coverage of delta_2=1, delta_2=3, and min-degree r in {4,5,6,7}. The K2/T2 reroot also *assumes existence* of an exact-codegree-2 nonedge (false when delta_2=1, absent when delta_2=3). The q=15 work is the t=3 branch (conditional on the V14 setup whose siblings were retracted), not t=1.
- **H14 anti-tightness cut OVER-CUTS and is ON BY DEFAULT** (state_count_6195_cpsat.py ~line 411, `if not args.disable_anti_tightness: ... >= 17`). Genuine extremal witness deg=8,|U_c|=6,d_R=2 gives LHS=16<17 -> wrongly INFEASIBLE; correct bound is >=16. The batch runner does NOT pass --disable-anti-tightness by default. Recent K2/T2 closure runs (e.g. idx97) DID pass it (safe), but every counted INFEASIBLE must be confirmed produced with the flag. This would MASK a witness (not create a false a(30)<=36), but recorded INFEASIBLE are only trustworthy with the flag.
- **No FEASIBLE/SAT primary-model witness anywhere** (9,067,820 INFEASIBLE, 733 UNKNOWN, 2 OPTIMAL[resolved], 0 FEASIBLE). a(30)=36 is not contradicted. (The 29 SAT tokens are in retracted p14_z8 screening files, not the beta>=37 model.) Necessary but not sufficient.
- Even the covered t=2 branch is ~1/3 done: 124/387 closed, 263 residual (q11:48,q12:80,q13:58,q14:77), ~733 UNKNOWN rows (incl idx100's 10 hard-tail 900s timeouts). [Note: q10 idx95/96/97 ARE finalized all-INFEASIBLE as of this session; the audit's "idx96 in-progress" was a stale read.]
- ASYMPTOTIC-at-finite-n still flagged: WYZ "min common degree > floor(n/8) => hom C5" applied at finite n=30 founds the whole delta_2 in {1,2,3} restriction — not independently re-audited vs arXiv:2408.05547. (Edge-window's BCL use is now correct via t->inf blow-up.)

## Complete remaining-work list for a gap-free Step-1
1. Build+run the delta_2=1 (t=1) four-witness UNSAT certificate, r=4,5,6,7 (NOT BUILT).
2. Audit+formalize delta_2=3 (t=3) closure (r=7 zero-margin + unproven triple-state lemma); re-audit q=15 V123 standalone.
3. Close min-degree r in {4,5,6,7}: fix the un-audited r=4,5 hand-lemmas (esp. r=4 dropped terms) + build the r=6,7 cert; the direct campaign returned 0 UNSAT (fix CaDiCaL crash).
4. Prove existence of an exact-codegree-2 nonedge wherever K2/T2 reroot is invoked (or justify t=2 manifold applies; it doesn't when delta_2 in {1,3}).
5. Finish t=2: close 263 residual q11-q14 + resolve all ~733 UNKNOWN to all-INFEASIBLE (incl idx100's hard tail — needs a band-top cut, brute+quotient already failed at 1200s).
6. Re-run every counted INFEASIBLE with --disable-anti-tightness (or prove >=16 bound + reroot premises); make batch runner pass the flag by default; per-file confirm.
7. Build one re-runnable manifest-wide zero-UNKNOWN union certificate (MA/MB branch-and-cover) instead of scattered scalar+grid+superseded files.
8. Independently audit the WYZ finite-n application (delta_2>=4 => C5 at n=30).
9. Housekeeping: purge artifacts keyed to the superseded 109..139 window (sound window is 112..143).

Full agent output: tasks/wqo9gfaig.output (run wf_5551348b-806).
