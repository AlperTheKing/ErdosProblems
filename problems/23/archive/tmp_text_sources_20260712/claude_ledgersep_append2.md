
---

## UPDATE 2026-07-09T03:20Z — GPT-Pro verdict: EscapingClosureDichotomy (honest: localization, not strictly easier)

GPT-Pro's blunt verdict on `EscapingNeutralLens_absorbed_or_prunable`: **"a real localization, but not yet a proof — essentially the same remaining Hall/ledger difficulty concentrated into the smallest local survivor."** The right object is the
**escape closure**:
```
IsEscapingClosure(C,W,D):  D = least set with W ⊆ D ⊆ C.support closed under: every owned atom h whose support
                           meets BOTH D and C∖D has support ⊆ D.
EscapingClosureDichotomy: let D = EscClosure(C,W). Then either
  PROPER: D < C and D is ledger-separating/prunable  => minimality (no_ledgerSep_in_minNeg, COMPILED) kills it;
  FULL:   D = C and the full-bank Hall/absorption certificate for C exists  => SAME difficulty as the remaining
          full-bank Hall theorem for the minimal obstruction.
```
GPT-Pro's honest bottom line: *"It becomes strictly easier ONLY IF you can prove that in every minimal-negative cage
the escaping closure is always PROPER. Then minimality alone kills it. If the escaping closure can be all of C, you are
back to the full-bank Hall theorem."* Lean-ready `IsEscapingClosure` + `LedgerSeparatingSubcage` defs provided.

### The decisive synthesis (Claude's max-cut lever meets GPT-Pro's dichotomy)
The reframe becomes a genuine reduction iff **the escape closure is always proper at a max cut**. Claude's exact
finding is the candidate lever: an escaping atom is a NON-max-cut phenomenon — it creates an improving flip
(GPT-Pro's 14-vtx pattern: given cut 14, true max 15; escaping atom h=x-z yields flip U={a,w,x} with
|δ_M(U)|=3 > |δ_B(U)|=2). If the escaping-atom→improving-flip construction is GENERAL, then a MAXIMUM cut has NO
escaping atom, so `EscClosure=W` is proper, minimality kills it, the FULL case is VACUOUS, and gap#1 CLOSES.

**CAUTION (honest):** the improving flip in the concrete example used x as a SHARED endpoint of e and h (x incident to
2 bad edges), which absorbed the blue edge x-a. Whether this construction is available for EVERY escaping-atom structure
is UNPROVEN — that generality is exactly the decisive open point. GPT-Pro retasked (2026-07-09T03:20Z) on precisely
this: prove `NoEscapingAtomAtMaxCut` (escaping atom at a max cut ⇒ improving flip ⇒ contra MaxCutVertexIneq) OR exhibit
an escaping atom surviving at a genuine MAXIMUM cut (which keeps the full-closure hard case live).

**Net:** crux is the sharpest yet — reduced to the single crisp question "is the escape closure always proper at a max
cut?" with a concrete candidate lever (maximality) whose generality is the open point. Localization real + compiled
(no_ledgerSep_in_minNeg); decisive lemma genuinely uncertain. P(gap#1 math) ~50 (sharper, not closed). If GPT-Pro
proves NoEscapingAtomAtMaxCut => formalize via MaxCutVertexIneq + no_ledgerSep_in_minNeg => gap#1 closes; if it exhibits
a max-cut-surviving escaping atom => full-bank Hall is the honest irreducible core for GPT-5.6/Fable-5.
