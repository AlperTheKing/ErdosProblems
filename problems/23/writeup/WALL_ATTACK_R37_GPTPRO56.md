# WALL ATTACK — R37: LOCAL ATTACHMENT DICHOTOMY PROVED (compile-ready); DEAD ENDS ELIMINATED;
# THE LAST MATHEMATICAL OBLIGATION = realSinkNeutralAttachmentClass_hasAugment
# (GPT-5.6 Pro, 2026-07-12; harvested 14,362 ch)

**[CLAUDE GATE HEADER — the local case analysis is verified by inspection (parity + row-intersection + completeness
arguments are elementary and consume only compiled facts); the two compile-ready theorems go to Codex for production
compilation THIS TICK; the conditional skeleton (canonicalCollisionFeasibleTuple_exists GIVEN hneutral) is
compilable NOW; my falsifier-gate + N=94 reconstruction gates queue. The wall is now ONE named finite lemma.]**

## Proven this round (local, complete)
1. **activeOwner_commonBlue_or_twoEdgeDetour** (compile-ready WITH proof body): every scoped collision owner v has an
   active internal neighbour x (nontrivial active component) and a selected-row support neighbour y; x≠y, same cut
   side. Case n(x,y)=0: both ordered keys (x,y,0/1) are genuine FreeHalves, and **reservation CANNOT block them**
   (same-side ⟹ xy not blue ⟹ not an active orientation); switch S={x,y} has σ≥0 by maxcut ⟹ checked common-blue
   sources. Case n(x,y)>0: in the least covering row Q, positions of x,y differ by EXACTLY 2 (odd distances = parity;
   distance 4 would make x−v−y shorten the atom to ≤2); v ∉ V(Q) (row-intersection theorem); replace the middle by v ⟹
   **Q′ is a genuine alternative shortest row** (completeness) with Q′≠Q. POSITION TABLE EXHAUSTED — {0,4}/{1,3}
   attachments are NOT exceptional; maxcut needed only for the σ≥0 annotation.
2. **Off-cable owners resolved**: every scoped owner is in a nontrivial active component ⟹ has an internal neighbour ⟹
   the probe applies. No least-min-cut argument needed.
3. **Matching/coherence case tree (4.1-4.4)**: base-label normalization (none when unused); unassigned base ⟹ augment;
   assigned-to-own-component ⟹ augment or follow matched half; assigned-elsewhere ⟹ follow (join-5886 handled — label
   never changes); reservation can't block both halves. **attachmentStep_total: the deadEnd branch is REMOVED.**
4. **Detour classification**: strict descent ⟹ CheckedCollisionDefectTrade; equal defect ⟹ NEUTRAL (retained in the
   state graph; lex-consumable only with verified rank decrease); uphill ⟹ ignored.
5. **One unit suffices**: integer defect + argmin ⟹ a single augmentation or strict trade is a contradiction.

## THE LAST MATHEMATICAL OBLIGATION (frozen, finite-checkable)
`realSinkNeutralAttachmentClass_hasAugment`: hypotheses (tri-free, blue-connected, maxcut, complete+anchored+nodup
rows, minimal-defect-one) + a CheckedSinkNeutralAttachmentClass C (sink SCC of the finite neutral graph over
defect-minimal tuples: matched-source edges + coherence-conflict edges + equal-defect detour edges) with 0 < defect ⟹
Nonempty (CheckedCoherentAugmentation D C). Equivalently: **no positive-defect sink neutral attachment class exists.**
Strictly narrower than realNeutralTraceComponent_progress (dead ends gone; tuple-changing equal-defect detours
internalized; strict detours are trades; ONLY source expansion inside a closed neutral class remains).

## Conditional main theorem (compilable NOW)
`canonicalCollisionFeasibleTuple_exists (hcanonical) (hneutral : ∀ C, 0 < C.defect → Nonempty (…Augmentation…)) :
∃ ω, collisionDefect ω = 0` — full skeleton: δ=min Δ; suppose δ>0; build the finite neutral graph over defect-δ
tuples + optimal matchings + occurrence-level states; pick sink SCC; local theorem gives per-cursor source-or-detour;
unused source ⟹ contra optimality; lower detour ⟹ contra minimality; equal-defect ⟹ stays in C; apply hneutral ⟹
augmentation ⟹ contra optimality ⟹ δ=0. Doors/vertexSlack/prune then discharge HitNeed microcopies.

## Exact falsifier gate for the final lemma (spec recorded)
δ>0 global min + all defect-δ tuples + optimal matchings + full neutral transition graph + sink SCC + per-state:
every probe, every generated key (reservation/base status), every detour row + updated defect; proof that no unused
source, no lower detour, all equal-defect detours internal. Such a certificate refutes BOTH the lemma and the wall.

## The exact unresolved question
**"Can maximum-cut lock geometry support a positive-defect sink neutral attachment SCC?"** — all locality,
coherence, reservation, and termination issues are REMOVED from it. R38 = attack this (prove-or-engine-falsifier).
