# R37 FULL-TEXT EXTRACT (verbatim Lean blocks + case tree) — for Codex N1 compilation
# Source: GPT-5.6 Pro reply "Worked for 9m 0s", 14,381 ch, harvested from thread offsets 16324-30705.
# ⚠ CORRECTION OVERLAY (post-R37, gated): the commonBlue branch below concludes only sigma>=0 sources;
# the PRODUCTION CommonBlueOwner (TerminalData.Valid) needs dM+2<=dB i.e. sigma>=2 — Codex N=20 CE gated
# PASS by me (_claude_n20_sigma_gap_gate.py). Compile the CORRECTED ActiveAttachmentProbeResult (free branch
# carries hsigma : 0 <= sigma) per r36_freepair_proof/REPORT.md; the detour branch below is UNAFFECTED.

## Verbatim: local dichotomy proof body (section 1)
Fix a tuple ω. Let v be the owner of a scoped collision obligation. Because v belongs to an active I_ω-component:
v has an active internal neighbour x (vx ∈ I_ω); v ∈ U_ω, so v occurs in some selected row P = ω(g); choose a
row neighbour y of v in P, so vy ∈ E(P) ⊆ S_ω. Since vx ∈ I_ω and vy ∈ S_ω, x ≠ y. Both x and y are blue
neighbours of v, so they lie on the same side of the displayed cut.
- Case 1: n_ω(x,y) = 0. Both ordered-pair keys (ω,x,y,0),(ω,x,y,1) are genuine FreeHalfKeys. Because x,y are
  on the same cut side, xy is not a blue edge ⟹ neither key is an orientation of an active internal edge ⟹
  neither half is edge-reserved. The common-blue switch is S={x,y}; maximum-cut optimality gives
  |B∩δ(S)|−|M∩δ(S)| ≥ 0. [⚠ production terminal needs ≥ 2 — see overlay.]
- Case 2: n_ω(x,y) > 0. Choose the least selected atom h whose selected row Q=(q0..q4) contains both x and y.
  Same side ⟹ positions differ by an even number: 2 or 4. Not 4: x,y would be the endpoints of h, but x−v−y
  is a blue path of length two, contradicting d_B(x,y)=4. So positions differ by exactly two: q_i=x, q_{i+2}=y
  (after possibly reversing Q), i ∈ {0,1,2}. Also v ∉ V(Q): Q contains x, vx ∈ I_ω; the compiled
  row-intersection theorem forbids a selected row from containing both endpoints of an internal off-support
  edge. Replace q_{i+1} by v: Q′ = (x,v,y,q3,q4) / (q0,x,v,y,q4) / (q0,q1,x,v,y) for i=0/1/2. Every edge of Q′
  is blue (xv active internal; vy selected support; other two inherited). Five vertices distinct (v ∉ V(Q)).
  Endpoints unchanged, four edges, atom endpoints at blue distance 4 ⟹ Q′ ∈ Geo4(h) ⟹ completeness gives
  Q′ ∈ D.shortestRows(h). And Q′ ≠ Q.

## Verbatim: position table (section 2)
equal → impossible (x≠y); distance 1 or 3 → impossible (same-side, odd blue subpath); distance 4 → impossible
(x−v−y shortens bad pair to ≤2); distance 2 {0,2}/{1,3}/{2,4} → replace position 1/2/3 by v.
Maxcut inequalities are NOT needed to forbid pure-{1,3}; used only for the common-blue terminal's switch loss.

## Verbatim: off-cable owners (section 3)
Every scoped collision obligation stores an owner in the active scoped vertex set. An active I_ω-component
contains two distinct endpoints of a bad atom ⟹ nontrivial ⟹ every vertex has an I_ω-neighbour. So every
scoped owner has an active internal neighbour x, a selected row through it, and a support neighbour y.

## Verbatim: matching/coherence case tree (section 4)
k=(ω,x,y) the base key. Normalize: baseOwner(k)=none whenever neither half used (changes no matching edge).
4.1 Base unassigned ⟹ both halves unused ⟹ either half = coherent augmenting terminal.
4.2 Base assigned to the owner's active component ⟹ if one half unused: augment; if both used: follow the
    least matched half to its matched obligation (ordinary alternating transition).
4.3 Base assigned to ANOTHER active component ⟹ by normalization ≥1 half matched to an obligation in that
    component; follow the least matched half there. (= joined-5886 handling; base label never changes.)
4.4 Reservation cannot block both halves: x,y same cut side ⟹ xy not blue ⟹ neither half an active-edge
    orientation ⟹ edge-exclusive reservations do not affect the pair.

## Verbatim: detour classification (section 5)
ω′ = ω[h↦Q′]; recompute exactly: active scoped graph, obligations, all six source relations, the
coherence-constrained optimal matching, Δ(ω′). Strict descent ⟹ CheckedCollisionDefectTrade. Equal defect ⟹
neutral realization transition (retained; lex-consumable only with verified rank decrease). Uphill ⟹ ignored.

## Verbatim Lean (section 6) — WITH ⚠ overlay: add hsigma to commonBlue per the gated CE
```lean
inductive ActiveAttachmentProbeResult
    (D : CanonicalRealEll5FullBankData)
    (ω : D.RowTuple)
    (owner : D.Vertex)
  | commonBlue
      (left right : D.Vertex)
      (left_ne_right : left ≠ right)
      (leftAdj : D.blueAdj owner left)
      (rightAdj : D.blueAdj owner right)
      (free : D.n ω left right = 0)
      (half0_unreserved : ¬ D.freeHalfReserved ω ⟨left, right, 0, free⟩)
      (half1_unreserved : ¬ D.freeHalfReserved ω ⟨left, right, 1, free⟩)
      -- ⚠ ADD (gated): (hsigma : 0 ≤ D.sigma [left, right])  — sigma≥2 NOT derivable, weak-free 0≤σ<2 exists
  | twoEdgeDetour
      (atom : D.BadEdge)
      (oldRow : D.shortestRows atom)
      (newRow : D.shortestRows atom)
      (old_selected : oldRow = ω atom)
      (new_ne_old : newRow ≠ oldRow)
      (activeEdgeUsed : ∃ e ∈ newRow.edges, e ∈ D.activeInternalEdges ω)

theorem activeOwner_commonBlue_or_twoEdgeDetour
    (D : CanonicalRealEll5FullBankData)
    (htri : D.G.CliqueFree 3)
    (ω : D.RowTuple)
    (owner : D.Vertex)
    (hactive : owner ∈ D.activeVerts ω) :
    Nonempty (ActiveAttachmentProbeResult D ω owner) := by
  obtain ⟨x, hx⟩ := D.activeInternalNeighbour_exists hactive
  obtain ⟨g, pos, hpos⟩ :=
    D.selectedRowOccurrence_exists (ω := ω) (v := owner)
      (D.activeVerts_sub_selectedVerts hactive)
  let y := D.canonicalAdjacentRowVertex (ω g) pos
  by_cases hfree : D.n ω x y = 0
  · exact ⟨.commonBlue x y
      (D.internal_ne_support_neighbour hx hpos)
      hx.blueAdj
      (D.canonicalAdjacentRowVertex_adj hpos)
      hfree
      (D.commonBlue_half0_unreserved hx hpos hfree)
      (D.commonBlue_half1_unreserved hx hpos hfree)⟩
  · obtain ⟨h, Q, hxQ, hyQ⟩ :=
      D.selectedRow_contains_of_n_pos (Nat.pos_of_ne_zero hfree)
    exact ⟨.twoEdgeDetour h Q
      (D.twoEdgeDetourRow owner x y Q hxQ hyQ)
      rfl
      (D.twoEdgeDetour_ne_current htri hx hxQ)
      (D.twoEdgeDetour_uses_activeEdge hx)⟩
```
(Consumes the compiled row-intersection result + complete anchored row database.)

## Verbatim Lean (section 7) — step totality (⚠ weak-free branch must be ADDED per the gated CE)
```lean
inductive CheckedAttachmentStepResult
    (D : CanonicalRealEll5FullBankData)
    (S : CollisionTraceState D)
  | augment (cert : CheckedCoherentAugmentation D S)
  | followMatched (next : CollisionTraceState D) (cert : CheckedMatchedSourceStep S next)
  | followCoherenceConflict (next : CollisionTraceState D) (cert : CheckedBaseConflictStep S next)
  | detour (candidate : CheckedTwoEdgeDetour D S.ω)
  -- ⚠ ADD (gated): | weakFree (…)  — free pair with 0 ≤ σ < 2: NOT a production source; class analysis
  --   must absorb it (WeakProbeClassTightness reduction) or a global compensation theorem is required.

theorem attachmentStep_total
    (D : CanonicalRealEll5FullBankData)
    (S : CollisionTraceState D)
    (hownerActive : S.owner ∈ D.activeVerts S.ω) :
    Nonempty (CheckedAttachmentStepResult D S)
```

## Verbatim Lean (section 8) — the sink-class lemma (unchanged target; consumer of Exposure)
```lean
theorem realSinkNeutralAttachmentClass_hasAugment
    (D : CanonicalRealEll5FullBankData)
    (htri : D.G.CliqueFree 3)
    (hblueConnected : D.blueGraph.Connected)
    (hmax : D.cut.IsMaximumCut)
    (hrowsComplete : D.completeShortestRows)
    (hrowsAnchored : D.SelectedRowEndpointAnchoring)
    (hrowsNodup : D.SelectedRowsNodup)
    (hminimal : D.supportFamily.IsInclusionMinimalDefectOne)
    (C : CheckedSinkNeutralAttachmentClass D)
    (hpositive : 0 < C.defect) :
    Nonempty (CheckedCoherentAugmentation D C)
```
Sink neutral attachment class = nonempty sink SCC of the finite graph over states (defect-δ tuple ω, optimal
coherent matching, least unmatched obligation + alternating cursor) with edges: matched-source transitions,
coherence-conflict transitions, equal-defect two-edge-detour replacements.

## Verbatim Lean (section 10) — conditional main
```lean
theorem canonicalCollisionFeasibleTuple_exists
    (D : CanonicalRealEll5FullBankData)
    (hcanonical : D.CanonicalHypotheses)
    (hneutral : ∀ C : CheckedSinkNeutralAttachmentClass D,
        0 < C.defect → Nonempty (CheckedCoherentAugmentation D C)) :
    ∃ ω : D.RowTuple, D.collisionDefect ω = 0
```
Skeleton: δ = min Δ; suppose δ>0; enumerate defect-δ tuples × optimal matchings × trace states; add the three
edge types; pick sink SCC C; local theorem per cursor (unused source → augment vs optimality; matched/conflict
→ successor; lower detour → contra minimality; equal-defect → in C; uphill → ignored); hneutral(C) →
augmentation → contra optimality → δ=0. Typed Doors + vertexSlack + prune discharge HitNeed microcopies.

## Section 9 (one unit suffices)
Integer defect; augmentation lowers defect by ≥1; strict trade likewise; the global-minimizer contradiction
needs only ONE strict unit.

## LIVE UNION RULING (Claude, answering the Codex ASK)
The frozen LIVE source union for the wall = P1 sameFirst + P2/common-blue (TerminalData.Valid, σ≥2 embedded)
+ P3 rowCompanion + P4 outsideAttachment (strict comp-equality) + P5 quiescentAttachment, with base-key
component coherence imposed. The no-common-blue P1/P3/strictP4/P5 adapter remains a STRONGER DIAGNOSTIC
surface (its zero-failure results transfer to the production union) — keep it for censuses; the wall statement
and Exposure computations use the production union. R38/R39 superseding note: the sink-class lemma is now
consumed via noPositiveDefectActiveAlternatingMiddleRotor (R39 archive) — Exposure > 0 on sink classes.
