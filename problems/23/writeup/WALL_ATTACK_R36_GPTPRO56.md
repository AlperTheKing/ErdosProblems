# WALL ATTACK — R36: LEX-ORIENTATION FALSE (orbit-minimum obstruction) + R35 CORE REALIZED AT N=94 AND
# KILLED BY REAL GEOMETRY; wall = realNeutralTraceComponent_progress; two compile-ready real lemmas
# (GPT-5.6 Pro, 2026-07-12; harvested 12,397 ch)

**[CLAUDE GATE HEADER — my gate queue: (i) reconstruct the N=94 realization from the spec and verify structurals
(tri-free; maxcut 108 = 30 core-blue + 13×6 lock caps, attaining cut; Γ=325 min; the three alternative rows
Q_0j = (ℓ0,z1,v,cR,rj); activeComponents(ω[f00↦Q00]) = ∅; the 20 forced common-blue halves > abstract deficit 10);
(ii) CheckedCollisionLexTrade PATCH REQUIRED — soundness needs an EXPLICIT tupleRank(ω′) < tupleRank(ω) check with
the INJECTIVE mixed-radix rank (additive/multiset rowCodes are degenerate); reversibility proves NOTHING about
direction (orbit-minimum: at the least element of a finite exchange orbit, EVERY nontrivial move is code-increasing).
Codex lex idea = REFUTED as a global tie-break; the neutralExchange class survives every well-order.]**

## Substance
1. **LEX-ORIENTATION CLAIM FALSE**: 3-atom period-3 orbit CE — ω=(0,0,0), orientations give (1,1,1)/(2,2,2), ranks
   0 < 13 < 26: BOTH orientations increase the current code. Reversibility only orders the exchange's two endpoints;
   the code-decreasing exchange starts at the OTHER tuple. Statuses: strictDefectTrade / explicitLexTrade (requires
   verified rank decrease) / **neutralExchange** (cannot be discarded by any tie-break — every well-order has orbit
   minima). Correct injective code = mixed-radix tupleRank (1).
2. **R35 CORE REALIZED**: N=94, |B|=108, |M|=13, |E|=121; maxcut certificate: non-lock blue core 30 edges + each
   bad edge's private length-6 lock path caps at 6 ⟹ every cut ≤ 30+78=108, displayed cut attains; Γ=13·25=325
   minimal. THEN KILLED three ways: (a) the selected active cable ℓ0−z1−v−z2−z3−z4−r0 creates the 2-edge detour
   ℓ0−z1−v ⟹ Q_0j = (ℓ0,z1,v,cR,rj) are genuine shortest rows for THREE atoms — singleton fiat impossible (2A+2S);
   (b) replacing f00's row by Q00 removes ℓ0z1,z1v from I_ω ⟹ **activeComponents = ∅** — one row replacement
   vacuates the entire scoped obligation set; (c) at owner v: N_B(v) ⊇ {cL,cR,z1,z2}, five Free unordered pairs ⟹
   **20 common-blue halves** (unreserved: both endpoints same side ⟹ not an active orientation) ≫ abstract Δ=10.
   Common-blue = "the first graph-derived mechanism invalidating an abstract sterile cycle" ⟹ RETAINED.
3. **TWO COMPILE-READY LEMMAS** (Lean bodies in reply): `twoEdgeDetour_shortestRow` (blueAdj R0 x + blueAdj x R2 +
   nodup ⟹ the detour 5-tuple is a member of the complete row family) + `commonBlue_of_free_blueNeighbours`
   (two Free blue neighbours of an owner give both halves eligible; non-reservation from same-side argument).
4. **CORRECTED SKELETON**: select argmin(Δ(ω), tupleRank(ω)); contradictory outcomes = augment (vs optimality) /
   strict defect trade (vs primary argmin) / EXPLICIT lex trade (vs secondary argmin, rank-checked). STILL OPEN =
   neutral tuple-changing cycles + tuple-identical cycles (general) + dead ends. **THE WALL (new name):
   `realNeutralTraceComponent_progress`** — from any CheckedClosedOrDeadTraceComponent at positive defect produce
   CheckedCoherentAugmentation ⊕ CheckedCollisionDefectTrade ⊕ CheckedCollisionLexTrade. Finer plausible form:
   CheckedUnusedCommonBlueSource ⊕ CheckedTwoEdgeDetourTrade ⊕ CheckedGlobalCollisionDefectTrade (the N=94 case
   lands in the first two).
5. Frozen global wall statement unchanged (6-relation union; common-blue retained).

## Candidate proof mechanism (mine, for R37)
The N=94 kill generalizes suspiciously well: ANY active component must ATTACH to selected rows (blue-connectivity +
its endpoints lie in selected rows); every attachment vertex adjacent to a row's position-0/2 pair creates a 2-edge
detour row (twoEdgeDetour lemma) ⟹ non-singleton families along the cable; AND every owner inside an active
component has ≥2 blue neighbours on the cable whose pairs are Free-or-covered ⟹ common-blue/detour supply. R37 asks
GPT to make this the actual proof of realNeutralTraceComponent_progress (or find the real cage where attachment
geometry avoids both).
