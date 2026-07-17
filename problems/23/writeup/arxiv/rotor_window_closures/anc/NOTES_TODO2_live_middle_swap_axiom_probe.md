# NOTES — TODO-2: rebuild + axiom probe of LiveMiddleSwapCrossOuter.lean

Agent notes, 2026-07-17. For the integrator; delete this file from anc/
before arXiv packaging (it is not a paper artifact).

## What was added (nothing else touched — no .tex, no CLAIMS_LEDGER.md,
## no SHA256SUMS edits, per hard rules)

- `anc/lean_axiom_probe/rebuild_and_probe.ps1` — reproducible honest
  rebuild + probe script (parameterized by Lake workspace and source
  root; per-module $LASTEXITCODE check + error/sorry log grep + axiom
  set gate; exits 0 only on PASS_AXIOM_PROBE). SHA-256
  `11713f2818718d1a3fc51c9d186cc285909aa1a46e842ee3fcca6c0cbde6b697`.
- `anc/lean_axiom_probe/probe_live_middle_swap.lean` — the probe file
  (`#print axioms` on the full theorem name). SHA-256
  `6f77cb14dc9f77cbe01be61e65014e43ef4953a1e1ec05dd1d8cab54f8d7337b`.
- `anc/lean_axiom_probe/probe_transcript_2026-07-17.txt` — full run
  record (environment, chain SHAs, both runs, negative control).
  SHA-256
  `ee25ada8c7179c5b24d9ee15712e66bb3f928bf1b0aa04c6dd1ccbc500f16d54`.

## Result (both runs green)

The deleted olean cache was NOT needed: the module's transitive import
chain is linear and only five files deep
(CertGraph <- CheckedC5BaseTransfer <- CheckedRowCompanionBaseTransfer
<- MinimumDemandRowSelection <- LiveMiddleSwapCrossOuter), sitting
directly on the formal-conjectures Mathlib olean cache (Lean 4.27.0,
mathlib rev a3a10db0e9d6). Full fresh elaboration of the chain plus the
probe takes ~2 minutes at 8 threads.

- All five modules: exit 0, no error/sorry token in any log.
- Probe (fresh process against the fresh oleans):
  `live_middle_swap_has_cross_outer depends on axioms:
  [propext, Quot.sound]` — strictly inside the accepted set
  {propext, Classical.choice, Quot.sound}. `PASS_AXIOM_PROBE`, exit 0.
- Source identity: production copy compiled = anc/lean copy,
  SHA 3dff7897... (checked inside the script).
- Negative control: sorry-mutated copy is rejected by two independent
  gates (log token, sorryAx in axiom set); plain exit code alone would
  NOT catch it (Lean exits 0 on sorry), which is why the script greps.

## Recommended integrator edits (probe PASSED, so the dual-attestation
## wording of CLAIMS_LEDGER assembly-fix 7 can be restored)

1. `main.tex`, Section Reproducibility (sec:repro), first paragraph — old:

   "for \texttt{LiveMiddleSwapCrossOuter.lean}
   this axiom audit is recorded in the acceptance ledger of the source
   archive rather than replayed (Proposition~\ref{prop:t4:swapgeometry})."

   new:

   "for \texttt{LiveMiddleSwapCrossOuter.lean}
   this axiom audit is attested twice: by the acceptance ledger of the
   source archive and by a fresh rebuild of its five-module import
   chain with a kernel \texttt{\#print axioms} probe, which reports
   axioms exactly \(\{\texttt{propext},\texttt{Quot.sound}\}\)
   (\texttt{anc/lean\_axiom\_probe/}, verdict
   \texttt{PASS\_AXIOM\_PROBE};
   Proposition~\ref{prop:t4:swapgeometry})."

2. `sections/sixteen_atom_closure.tex`, prop:t4:swapgeometry — old:

   "source SHA-256 prefix
   \texttt{3DFF7897}; its acceptance record lists axioms \texttt{propext},
   \texttt{Quot.sound}\textup{)}."

   new:

   "source SHA-256 prefix
   \texttt{3DFF7897}; axioms exactly \texttt{propext},
   \texttt{Quot.sound}, attested by both the acceptance record and a
   fresh rebuild-and-probe at assembly,
   \texttt{anc/lean\_axiom\_probe/}\textup{)}."

3. `anc/SHA256SUMS` — add three lines (paths relative to anc/):

   6f77cb14dc9f77cbe01be61e65014e43ef4953a1e1ec05dd1d8cab54f8d7337b  lean_axiom_probe/probe_live_middle_swap.lean
   ee25ada8c7179c5b24d9ee15712e66bb3f928bf1b0aa04c6dd1ccbc500f16d54  lean_axiom_probe/probe_transcript_2026-07-17.txt
   11713f2818718d1a3fc51c9d186cc285909aa1a46e842ee3fcca6c0cbde6b697  lean_axiom_probe/rebuild_and_probe.ps1

4. `CLAIMS_LEDGER.md` —
   (a) prop:t4:swapgeometry row: "axiom audit SINGLE-SOURCE, now stated
   as 'acceptance record lists' in text" -> "axiom audit DUAL: acceptance
   record + fresh rebuild-and-probe 2026-07-17
   (anc/lean_axiom_probe/, PASS_AXIOM_PROBE, axioms exactly
   propext, Quot.sound)".
   (b) Assembly fix 7: append "— superseded 2026-07-17: probe completed
   (anc/lean_axiom_probe/), dual-attestation wording restored."
   (c) Open TODO 2: mark DONE (rebuild took ~2 min against the
   formal-conjectures Mathlib cache; deleted tmp/ olean base not needed).

5. Optional: `sections/sixteen_atom_closure_claims.md` Proposition 14
   entry — same softening reversal as (2) if the claims manifests are
   kept in sync.

## Exact reproduction command (from any PowerShell 7)

  anc/lean_axiom_probe/rebuild_and_probe.ps1 `
      -LakeProject <formal-conjectures checkout with built Mathlib> `
      -SourceRoot  <problems/23/lean> [-Threads 8]

Expected final lines: "axioms = [propext, Quot.sound]",
"PASS_AXIOM_PROBE", exit 0.
