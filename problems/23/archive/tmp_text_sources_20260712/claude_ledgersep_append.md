
---

## UPDATE 2026-07-09T02:40Z — BOTH CHANNELS CONVERGE: crux is a LEDGER theorem, not local geometry

**Workflow `wf_99893989-218` (9 angles, 23 agents, 5009s) INDEPENDENTLY converged on the ledger-separation reframe**
(three angles: reducedness-forbids, classification, novel) and went further: it pinpointed the residual obstruction as
the **PROPERNESS of the pruned complement C'** (whether deleting the two doors yields a C' that is a MAXIMUM cut of its
induced subgraph = the `cProper` field of `LedgerSep`). Exact n=14 witness: `C'={0,1,3,4,5,6,7}` has induced cut 6 but
induced MAX cut 7, so `cProper` is NOT automatic; the global max-cut condition re-enters here. **NO refutation survived**
— every Demand(W)>Door(W) attempt (sunflower, book B(k,L) up to +2678, sunburst) was a NON-maximum cut collapsing to a
reducible base-leaf odd cycle. Crux **true-leaning**. Confidence 0.82. (Workflow also produced a superb 14-constraint
canonical statement C1–C14 + 11 subtleties — see wipw0z2ac.output / journal.jsonl.)

**GPT-Pro (retask on NoEscapingAtom) CONVERGED to the identical conclusion:** the local `NoEscapingAtom` lemma is
**FALSE** without the ledger. Explicit 14-vertex escaping-atom pattern (sides Red={x,z,y,w,b,r2,r4,r6},
Blue={a,c,r1,r3,r5,r7}; B = x-a,a-b,b-c,c-y,z-c,a-w and the 8-path x-r1-...-r7-z; bad e=x-y, f=z-w, h=x-z). With
`W={a,b,c,y,w}`: `deltaB(W)={x-a,z-c}`, `deltaM(W)={x-y,z-w}`, and **h=x-z escapes** (endpoints x,z OUTSIDE W, shortest
geodesic x-a-b-c-z passes through W-interior a,b,c). So the ledger split `Balance(C)=Balance(W)+Balance(C')+rem` does
NOT follow. **But this is not a deficient-minimal cage, so it does NOT refute the full theorem** — it proves local
geometry alone cannot close the lemma.

**CLAUDE EXACT VERIFICATION** (`_claude_verify_escaping_atom.py`, integer BFS, 0 float): CONFIRMED — triangle-free,
`e,f,h` all monochromatic with blue-dist 4 (ell=5), door signature exact, `h` escaping (`support-cap-W={a,b,c}`). The
escaping-atom obstruction is REAL and independent of the AI channels.

### The new open core (both channels agree)
```
EscapingNeutralLens_absorbed_or_prunable:
  In a REDUCED MINIMAL-NEGATIVE-BALANCE cage, the escaping-atom configuration cannot persist:
  it either yields a proper prunable subcage (=> contradiction by no_ledgerSep_in_minNeg, COMPILED)
  OR its full-bank balance is nonnegative
  (legal banks ONLY: Door=25/interior-cut-edge + vertexSlack=max(0,N-T(v)) + certified proper-descendant Prune
   + base-leaf density; NEVER the cage's own reserve eta_C=N^2/25-m).
```
This is a genuine **ledger** theorem (uses minimal-negativity + the banks), NOT provable from triangle-free +
shortestness + neutral-theta geometry. **OPEN QUESTION (retasked to GPT-Pro 2026-07-09T02:40Z):** is it a genuine
reduction (strictly easier than the original impure-lens crux) or a reformulation of equal difficulty? Both channels
flag that the LP-dual/discharging (`col_U<=1`) route "re-encodes" the same content — so caution.

**Net:** the surplus-sign wall is DISSOLVED (compiled `no_ledgerSep_in_minNeg`); the crux is sharpened to a ledger
theorem about escaping atoms; the escaping atom is a real, exact-verified local phenomenon; no counter-pattern exists in
the real regime (crux true-leaning). P(gap#1 math) ~48-50 (wall dissolved; new ledger core unproven, possibly
reformulation-hard). Escalate `EscapingNeutralLens_absorbed_or_prunable` to GPT-5.6/Fable-5.
