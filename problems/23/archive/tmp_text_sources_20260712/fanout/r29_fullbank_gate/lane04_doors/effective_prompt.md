# R29 FullBank exact audit - common contract

Workspace: `E:\Projects\ErdosProblems`.

We audit the deterministic 2,943-vertex R29 all-anchor row tuple. The auxiliary
`Gamma/ActiveScoped*` matching has hub owner shore `{0,1,2}` with demand 19,953,
reachable `FreeHalf` sources 19,925, defect 28. This is not yet a falsifier to
the production FullBank architecture because the auxiliary relation may omit
production source classes.

Authoritative inputs:

* `GOAL_LOOP.md`
* `problems/23/writeup/R29_GLOBAL_MIN_SCOPED_HALL_FALSIFIER.md`
* `tmp/fanout/r29_gate/lead/r29_lead_gate.py`
* `tmp/fanout/r29_gate/d05/retry2/rebuild_owner_hall.py`
* `tmp/fanout/r29_gate/d05/retry2/cut_certificate.json`
* production Lean modules under `problems/23/lean/Erdos23Delta0/`, especially
  `Ell5*FullBank*`, `Gamma/FullBank*`, and any compiled transfer definitions
* transfer-design writeups/scripts `WALL_ATTACK_R18...R23*` and matching gates.

Rules:

1. Exact integer or `fractions.Fraction` arithmetic only. Floats are not evidence.
2. Match implemented definitions. Clearly label prose-only/unimplemented notions.
3. Do not edit production files, mailboxes, progress files, or sibling lanes.
4. Write only inside your assigned lane directory.
5. Reconstruct or import the deterministic cage; do not trust copied totals alone.
6. Every quantitative claim needs a replayable script and output JSON where feasible.
7. Report source classes incrementally with overlaps removed; do not sum capacities
   that can double-spend the same token/sink.
8. Final `REPORT.md` must state PASS/FAIL/UNDEFINED precisely and list commands,
   exact values, source paths/line numbers, and SHA256 hashes.
9. Do not spawn descendants.

The decisive question is whether the complete implemented production
transfer/bank relation absorbs the 28-unit HUB-shore defect, or whether a fully
verified Hall/LP defect remains under every production source class.



ASSIGNED LANE DIRECTORY: tmp/fanout/r29_fullbank_gate/lane04_doors/

Role: Door-capacity auditor.

Read `../COMMON.md`. Trace the exact production Door definitions and the own-Door
routing interface from Lean. Determine what a Door is for the real active component
and hub shore on R29. Implement exact enumeration/capacity accounting if the extractor
is operationally defined; report raw and incremental reachable capacity after the
four-pattern transfer sources, including incidence and no-double-spend checks. If the
real extractor/provider is absent, prove that absence by source-path audit and state
the minimal missing data instead of assigning speculative Doors. Emit scripts/JSON/
report/hashes.


