# gap#1 crux — LEDGER-SEPARATION reduction (GPT-Pro, 2026-07-09) + Claude verification

**Status: genuine sharpening. The balance-sign wall is DISSOLVED. Crux reduced to `NoEscapingAtomThroughBalancedNeutralLens`. The minimality lever is COMPILED in Lean (`NeutralLensLedger.lean`, axiom-clean).**

## The move
The impure-lens wall was: extra owned atoms in the lens `W` make `Balance(W)` uncontrolled in sign, so we cannot prove
`Balance(W) ≥ 0`. GPT-Pro's fix: **don't**. Show `W` is a proper *ledger-separating* prunable subcage; then minimality
kills it regardless of `Balance(W)`'s sign.

### Sign-error correction (Claude's angle-2 was backwards — CONFIRMED)
`Surplus(W) = Σ_owned (ℓ² − 25) ≥ 0` (each owned atom has ℓ≥5). `Balance(W) = Bank(W) − Surplus(W)`. So extra owned
atoms **subtract** — they make `Balance(W)` SMALLER. Pure lens: `Surplus=0 ⇒ Balance(W)≥0` immediate. Impure lens:
`Surplus>0 ⇒ Balance(W)` any sign. The "owned surplus makes W nonnegative" idea is sign-wrong. **Verified.**

### Balance-sign-agnostic minimality lemma (EXACT-verified + COMPILED)
Let `C` be minimal-negative-balance: `Balance(C) < 0` and no proper descendant has negative balance. Let `W` be a
proper prunable ledger-separating subcage with pruned complement `C'` and `Balance(C) = Balance(C') + Balance(W) + rem`,
`rem ≥ 0`. Then `W` is impossible:
- both `W` and `C'` are proper descendants ⇒ minimality forces `Balance(W) ≥ 0` and `Balance(C') ≥ 0`;
- so `Balance(C) = Balance(C') + Balance(W) + rem ≥ 0`, contradicting `Balance(C) < 0`.

(GPT-Pro's case-split on `sign(Balance(W))` is equivalent; the direct form above is cleaner.) Arithmetic airtight:
`a<0, w≥0, r≥0, a=c'+w+r ⇒ c' ≤ a < 0`. **Compiled:** `NeutralLensLedger.no_ledgerSep_in_minNeg` (linarith,
axiom-clean `{propext,Classical.choice,Quot.sound}`), plus the reduction wrapper
`NeutralLensLedger.book_of_book_or_ledgerSep` (`Book ∨ LedgerSep ⇒ Book` inside a min-neg cage).

## The reduced crux (the new open core)
```
BalancedNeutralTheta_book_or_ledgerSep:
  e,f ell=5 rows, balanced neutral non-book theta lens W in a reduced minimal-neg-balance cage C
  ⇒ C5BookParallel(e,f)  ∨  W is a proper ledger-separating prunable subcage of C.
```
Then `LedgerSep ⇒ False` by `no_ledgerSep_in_minNeg`, so `book_or_ledgerSep ⇒ book_or_reducible`. **DONE modulo the one
open local lemma.**

`LedgerSeparatingSubcage(C,W)` data (LS1–LS5): LS1 proper support `∅≠W.support⊂C.support`; LS2 `B[W]` and `B[C∖W]`
connected; LS3 exact boundary `δ_B(W)={d0,d1}`, `δ_M(W)={e,f}`, no other bad edge crosses `W`; LS4 every owned atom
classified inside/outside/neutral-boundary/remainder (no straddling atom); LS5 pruning identity with `PruneRemainder≥0`.

## The irreducible obstruction (now open)
```
NoEscapingAtomThroughBalancedNeutralLens:
  in a reduced minimal-neg-balance cage, a non-book balanced-neutral ell=5 theta lens has NO ESCAPING ATOM
  (an atom h≠e,f whose support/ownership straddles the lens in a non-boundary way).
  ⇒ W is ledger-separating (LS4), and minimality kills it.
```
Failure pattern to search for = an **escaping atom** h≠e,f with support crossing the lens in a non-boundary way while
avoiding triangle / shorter-row / proper-prunable-sublens / book. GPT-Pro's decisive questions (retasked): does an
escaping atom FORCE (triangle) ∨ (ℓ<5 shorter row) ∨ (proper prunable sub-lens) ∨ (book-compat)? Enumerate the finite
incidence patterns of h against the 5+5 lens vertices; rule each out or exhibit the survivor.

## Angles NOT the route (GPT-Pro verdict)
- Angle 1 (non-Γ monovariant): a plausible Φ = lex(#escaping atoms, total crossing number, book-defect, min non-book
  lens size) exists but no proof it strictly decreases under every neutral recut; more global, likely harder than
  ledger-separation. Do not lead with it.
- Angle 3 (reducedness ⇒ purity): FALSE literally — reducedness allows impure atoms if `W` is not ledger-separating.
  Correct form: reduced + neutral theta ⇒ any impure `W` must contain an escaping atom (= restatement of NoEscapingAtom).
- Angle 4 (Farkas/LP-dual): equivalent to the Hall expansion; per-instance certificates only; reduces to the same local
  lens problem.

## Next
GPT-Pro retasked (2026-07-09T02:15Z) on `NoEscapingAtomThroughBalancedNeutralLens` (prove or escaping-atom
counter-pattern). Workflow `wf_99893989-218` (9-angle assault) still running — cross-check its verdict against this
reframe. Formalize `LedgerSep` at the real rowDB/cage level + wire to `book_of_book_or_ledgerSep`; the only remaining
mathematical content is NoEscapingAtom. P(gap#1 math): nudged up (wall dissolved, cleaner open core) but NoEscapingAtom
itself unproven — hold ~48-50 pending its resolution.

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


---

## UPDATE 2026-07-09T04:00Z — NoEscapingAtomAtMaxCut REFUTED (verified); direct-maximality path DEAD

GPT-Pro produced an explicit **escaping atom at a genuine Γ-minimal MAXIMUM cut**, refuting the direct-maximality
shortcut. **CLAUDE EXACT-VERIFIED** (`_claude_verify_maxcut_escaping.py`, brute-force max cut 2^11): 11 vertices
p,q,a,b,b',c,y,w,r1,r2,r3; Red={p,q,b,b',y,w,r2}, Blue={a,c,r1,r3}; B = p-a,a-b,b-c,c-y,q-c,c-b',b'-a,a-w,
p-r1,r1-r2,r2-r3,r3-q; bad e=p-y, f=q-w, h=p-q. CONFIRMED: triangle-free; given cut size 12 = TRUE max (74 distinct max
cuts); all three bad edges ell=5; W={a,b,b',c,y,w} with δ_B(W)={p-a,q-c}, δ_M(W)={p-y,q-w} (balanced-neutral, Γ 75→75);
h=p-q ESCAPING (endpoints outside W, geodesic p-a-b-c-q through W-interior {a,b,b',c}). β=3, Γ=75, N=11, N²=121 =>
NON-deficient (conjecture holds for it — it is a counterexample to the LEMMA, not the conjecture).

**Decisive difference from Claude's 14-vtx pattern:** here h has an ALTERNATE outside geodesic p-r1-r2-r3-q (length 4)
that keeps ell(h)=5 after the W-flip, so no improving flip exists and the cut stays maximum. Claude's 14-vtx pattern
lacked this, which is why it was sub-maximal. **So maximality ALONE does not forbid escaping atoms.**

**DEAD ANGLE (do NOT re-chase): NoEscapingAtomAtMaxCut / direct-maximality close.** The compiled corollary
`MaxCutVertexIneq.not_isMaxCut_of_improving_flip` (improving flip ⟹ ¬max) is TRUE and stands, but the link
"escaping atom ⟹ improving flip" is FALSE, so it does not close the crux. (Only the true corollary was formalized; the
false lemma was never compiled — falsifier-first held.)

**PERMANENT GAINS retained:** surplus-sign wall dissolved + compiled (`no_ledgerSep_in_minNeg`); the escape-closure
dichotomy is the correct localization; `EscapingClosureDichotomy` (proper ⟹ killed by minimality; full ⟹ full-bank Hall).

**REMAINING CORE (genuine, hard):** the FULL escape-closure branch = the full-bank Hall / absorption theorem for the
whole minimal obstruction — GPT-Pro: "not a local max-cut theorem; the remaining full-bank/Hall obstruction in local
form." Last reduction hope (retasked 04:00Z): does DEFICIENCY (Γ>N², which the counterpattern LACKS) + REDUCED +
MINIMAL-NEGATIVE-BALANCE force the escape closure PROPER? If yes ⟹ minimality closes it; if a deficient full-closure can
be constructed ⟹ full-bank Hall is the honest irreducible core for GPT-5.6/Fable-5.

**P(gap#1 math): ~45–47** (down from ~50–52; the promising shortcut is refuted; back to the genuine full-bank-Hall core,
now precisely localized). Net of the night: real permanent gains (wall dissolved, right formalization, 2 compiled
ledger/maximality levers) but the crux is NOT closed; the direct path is a documented dead end.


---

## UPDATE 2026-07-09T04:30Z — DEFINITIVE: no local shortcut; core = FullBankHall / ShortestSupportExpansion

GPT-Pro final verdict on "does deficiency+minimality force the escape closure proper?": **NO.** *"The full-closure
branch is genuinely live and is not killed by reducedness or minimal negative balance."* Deficiency is a SCALAR
condition (`Balance(C)<0` = demand exceeds bank); it does not create a separator. Reducedness removes separators but
does not guarantee one exists. Proving `EscClosure(C,W)=C is impossible` would itself be the full-bank Hall theorem.

**Exact equivalence (the definitive localization):**
```
EscapingClosureDichotomy(C,W):  D = EscClosure(C,W).
  PROPER (D<C, ledger-separating)  => killed by minimality (no_ledgerSep_in_minNeg, COMPILED).
  FULL   (D=C)                     => the only contradiction is FullBankHall(C) i.e. Balance(C) >= 0,
                                      = the full mixed-bank Hall theorem for the whole closure.
```
GPT-Pro: for the ell=5 multi-atom full-support part, FullBankHall SPECIALIZES to `∀ ell=5 row subset S, |S| <= |E_short(S)|`
= **ShortestSupportExpansion** (the original gap#1 core). So *full escape closure absorption ⟺ ShortestSupportExpansion*.

**Sharpest Lean-ready core (GPT-Pro):**
```lean
def FullBankHall (rowDB) (C) : Prop :=
  ∀ A : Finset SurplusAtom, A ⊆ OwnedAtoms rowDB C →
    Demand rowDB A ≤ DoorCap rowDB C A + VertexSlackCap rowDB C A + C5BaseCap rowDB C A + PruneCap rowDB C A
-- DoorCap = 25·σ-neighborhood; VertexSlackCap = support-constrained max(0,N−T(v)); C5BaseCap = independent base-density
-- tokens (single full-support leaves from ell ≤ |V_D|), NEVER the top cage's eta_C; PruneCap = balances of strict proper
-- descendants.  Then FullBankHall.balance_nonneg + hMin.balance_neg discharges the full branch.
```

### Honest endpoint of the 2026-07-08→09 deep sequence
- PERMANENT GAINS (real, compiled): surplus-sign wall DISSOLVED (`no_ledgerSep_in_minNeg`); the ESCAPE-CLOSURE DICHOTOMY
  is the correct localization; the maximality lever (`not_isMaxCut_of_improving_flip`) compiled; the |S|<=5 base case +
  aggregation arithmetic + rigidity compiled (8 axiom-clean modules).
- ALL LOCAL SHORTCUTS RULED OUT (exact counterpatterns): surplus-nonneg (sign error); NoEscapingAtomAtMaxCut (11-vtx
  max-cut escaping atom, CLAUDE-verified); deficiency/minimality-forces-proper (full closure genuinely live).
- THE CORE IS UNCHANGED: `FullBankHall / ShortestSupportExpansion` for the full escape closure = the original gap#1
  difficulty, now PRECISELY stated and cleanly localized (proper case compiled-away). No reduction in essential
  difficulty; the night reframed + de-walled + mapped, it did not close.

**NEXT (escalation): attack `ShortestSupportExpansion` / `FullBankHall` DIRECTLY** with the stronger models
(GPT-5.6/Fable-5) + a focused ULTRACODE workflow. This is the honest irreducible core. P(gap#1 math) ~45 (core =
original ShortestSupportExpansion; reframe + compiled levers are genuine but the essential theorem is the same).

