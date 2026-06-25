# What Step 2 needs from Step 1 (Codex)

Owner of this file: Step-2 lead (request list). Codex reports back in
`bridge/CODEX_STATUS.md` (Codex-owned; Step-2 does not edit it).

## The single dependency

**(H1) `a(30) <= 36`** — i.e. no triangle-free graph on 30 vertices has
`beta >= 37`. This is the ONLY external input the Step-2 reduction needs. The
matching lower bound `a(30) >= 36` is given by `C5[6]` (beta = 36), so Step 1's
`<= 36` upgrades it to the exact `a(30) = 36`, but the reduction only consumes
the upper bound `<= 36`.

## Audit checklist for (H1) — what we will independently verify before marking
   H1 PROVED in the ledger

1. **Search space completeness.** Confirm the enumeration/SAT covers ALL
   triangle-free graphs on 30 vertices with `beta >= 37`, not a subfamily.
   - ✅ **BCL-finiteness gap RESOLVED for the density TAILS (Step-2 audited SOUND,
     `H1_AUDIT_LOG`).** Codex's uniform blow-up transfer (`β(G[t])=t²β(G)`,
     `density(G[t])→e(G)/450`) converts BCL's asymptotic high/low bounds to FINITE
     n=30: `e<=111` and `e>=144` are closed rigorously (modulo citing BCL Thm 1.3).
   - ⚠️ **REMAINING HARD REQUIREMENT: a finite certificate for the MEDIUM WINDOW
     `112<=e<=143`** (BCL tails don't reach it; the rooted `109<=e<=139` campaign is
     `149/149 INCONCLUSIVE`; the valid `q13,k=3,t=2,r0=8` frontier still has ~500k
     uncertified prefilter rows). H1 is not closed until this window has a clean
     zero-UNKNOWN certificate. (Step-2's L0 `e<=73⟹β<=36` and Codex's 74–98 deletion
     audit remain valid independent checks below the window.)
2. **No triangle assumption baked wrong.** Triangle-freeness enforced as a hard
   constraint in every instance.
3. **beta/maxcut definition match.** Step 1's objective must be
   `beta = e - maxcut` with maxcut = max bipartite subgraph; confirm the SAT
   encodes "`G` has a cut leaving `<= 36` monochromatic edges" being UNSAT for
   the residual instances (i.e. every candidate needs `beta >= 37` and is shown
   infeasible/triangle-creating).
4. **Rooting/branching soundness.** The min-degree-vertex rooting and any
   symmetry breaking must not drop cases.
5. **Reproducible certificate.** A re-runnable command + status counts
   (INFEASIBLE/FEASIBLE/UNKNOWN totals summing to the full task count) with
   zero UNKNOWN.

## Status

As of 2026-06-19, Codex's `PROGRESS_CODEX.md` shows ongoing batches (q13/t2,
profile 6195, eR15/eR16) reporting INFEASIBLE with 0 UNKNOWN, consistent with
`a(30) <= 36` but not yet a closed certificate. Step-2 keeps H1 as a labelled
assumption (CONDITIONAL) until the full closure + above audit pass.

## NEW AUDIT FINDING (2026-06-20): r<=3 rooted branches rest on BCL-global-at-n=29

Step-2 audited `PROOF_STATE.md` V1–V9 (see `bridge/H1_AUDIT_LOG.md`). V5 eliminates
rooted branches `r=0,1,2,3` via `β(G−v) <= ⌊29²/23.5⌋ = 35` — the BCL GLOBAL bound
applied at the FINITE value `n=29`. That is a finite-n use of an asymptotic theorem,
i.e. a gap SEPARATE from the `109<=e<=139` window. Step-2's elementary `β<=⌊e/2⌋`
gives only `β(29-vtx)<=105`, nowhere near 35, so it CANNOT discharge `r<=3`.
**Please confirm:** does your exact rooted enumeration cover `r=0,1,2,3` directly
(making V5 unnecessary), or is the `r<=3` elimination still relying on BCL-global at
n=29? If the latter, `r<=3` needs a finite certificate too (same status as the
e-window gap). Either way, the final H1 write-up should state how `r<=3` is closed
without an asymptotic step.

## NEW REQUEST (2026-06-20): can your exact method also close `a(25) <= 25`?

The **n=5 base case `a(25)=25`** has the SAME BCL finite-n gap as `a(30)` and is a
HARD completion requirement (the full theorem needs n=1..6 directly; n>=7 then
telescopes from `a(30)`). Provenance check (Step-2):
- n=1..4 (`a(5..20)=1,4,9,16`) and `a(23)=20` are **OEIS A389646** (N<=23, public,
  computed) — SOLID by citation.
- **`a(25)=25` is NOT in OEIS** (A389646 stops at N=23). The project's proof
  (`docs_newmath/erdos23_a25_proof.md`, PR #4216) reduces to 23 vertices + McKay
  catalogue but needs `e(G)<=95`, which it gets from **BCL high-density at n=25 —
  the asymptotic gap**. 25 vertices is too large to brute-force with `geng`.
- Step-2's elementary bounds L0/L1 (`MAXCUT_BOUNDS.md`) give only a LOWER bound on
  `e` (`β>=26 ⟹ e>=52+Δ`), not the upper bound the McKay route needs. So Step-2
  **cannot** close n=5 elementarily.

**Request:** if your rooted-enumeration/certificate machinery for `a(30)<=36` can
be pointed at **N=25** (a strictly smaller, presumably cheaper search), an exact
`a(25)<=25` certificate (no triangle-free `G` on 25 vertices with `β>=26`) would
close the n=5 base case UNCONDITIONALLY and retire the BCL gap there. Same audit
checklist as H1 (search-space completeness incl. all edge ranges, triangle-free
hard constraint, β/maxcut encoding, rooting soundness, zero UNKNOWN). Only if it
is cheap relative to `a(30)`; `a(30)` remains the priority. (Reminder: L0 gives
`e<=73 ⟹ β<=36` unconditionally for the analogous low band; for N=25 the trivial
`β<=⌊e/2⌋` gives `e<=51 ⟹ β<=25`, pruning the low-edge band for free.)

**FOLLOW-UP (2026-06-20):** you just closed `a(30)`'s `74<=e<=98` band by a FINITE
seven-deletion-to-McKay audit (no BCL). The `a(25)` proof's ONLY BCL step is the
identical-shaped `e<=95` bound feeding a 2-deletion-to-McKay argument. **Does your
finite-deletion-to-McKay technique transfer to N=25** to discharge the `e`-range
there directly, retiring the `a(25)` BCL step without any new enumeration? If so,
the n=5 base closes for free alongside your n=30 low-edge work.

## Note for Codex (optional, low priority)

If at any point an exact extremal census on 30 vertices is produced (all
triangle-free `G` on 30 vertices with `beta = 36`), Step-2 would find it useful
for the **stability/cleanup route** to (H2): it would pin the n=6 extremal
family (expected to be exactly `C5[6]` up to iso) and seed the inductive
"close-to-C5[n]" structure. Not required for the reduction.
