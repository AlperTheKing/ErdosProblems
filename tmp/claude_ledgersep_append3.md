
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
