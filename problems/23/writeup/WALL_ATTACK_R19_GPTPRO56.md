# WALL ATTACK — R19: explicit 3892 transfer + the sound constructor; prune needs slot transport
# (GPT-5.6 Pro, 2026-07-11, HARVESTED VIA IN-APP BROWSER)

**[CLAUDE GATE HEADER:**
- **3892 FIXTURE PAYS EXPLICITLY (base transfers ONLY — no prune!)**: attachment (28,784,·,784,28) at v;
  every attachment row (v,d,e,a,b) has exactly one B_v vertex ⟹ B_v×B_v ordered pairs are PERMANENT Free
  (784·783 = 613,872 per attachment; total attachment Free ≥ 2,541,672 per (2)-(3)); local deficits
  F−C = −43K at 4, −38K at 8 [consistent with R18's −81K sum ✓]; 43+38 disjoint B-pairs supply exactly 81
  units; switch witness S = {b0,b1}: |B∩δ(S)| = 56, |Hbad∩δ(S)| = 2 ⟹ **loss = 54 ≥ 0** (valid c5Base
  terminal; tri-free kills b0b1, attachment isolation kills extra edges — isolation to become a Boolean
  assertion); explicit trace record given (source cell, half bit, owner, switch, boundaries, loss, kind
  c5Base, support {v}, cap 1/(2K), legal = active endpoint ports at v); the I-edge (4,8) is itself Free for
  every ω (A-scoped row-intersection lemma + attachments don't cross) ⟹ funds the two ½ hit-needs.
  Claimed checker SHA 6b78d9f5… — my gate queued.
- **SOUND GENERAL TRANSFER PATTERNS**: (a) same-first-coordinate cancellation (realizes F_v − C_v = K(N−T(v))
  pointwise; no token); (b) **common-bad-neighbour transfer**: Free (ω,x,y,ε) → owner v when x≠y, vx and vy
  ACTUAL bad edges, recomputed loss({x,y}) ≥ 0, destination in the checked active component — collision
  match cancels (no token), HitNeed match creates .c5Base (support {v}, cap 1/(2K), sourceId = Free-key).
- **PRUNE-AS-PROPOSED REFUTED**: from the Γ-MINIMAL chosen cut, zero-loss switches give other max cuts with
  Γ(original) ≤ Γ(switched) ⟹ forward strictly-Γ-decreasing steps CANNOT occur (contradiction branch, not
  traversable); reversing changes the row-cell universe. Local row ranks can orient same-cut row rewrites
  BUT each prune step must carry **move : incoming ↪ outgoing** (injective transport of affected half-slot
  keys, Boolean-recomputed via moveSound) — termination + individual reachability ⇏ μ (two obligations can
  share one reachable Free node). CheckedPruneStep record specified (oldRows/newRows shortest,
  rowsUnchangedOutside, switchLoss = 0, sameCutBadSet, localRankDecrease, moveSound, component preserved).
- **TRANSFER-AWARE FALSIFIER GATE**: relation R = traces via cancellation/base/prune; unit bipartite
  matching (orbit classes + integer multiplicities for large K); decisive falsifier = min-cut side Z with
  |Z| > |ReachFree(Z)| + full trace/rejection export. STRICTLY refines the scalar C+H ≤ F test.
- **LEAN STACK (full shapes given)**: FreeHalfKey/CollisionHalfKey/HitNeedKey/TransferObligation/
  CheckedC5BaseTerminal/CheckedTransferEdge (sameOwner | c5Base | prune)/CheckedTransferTrace/
  CheckedTransferMatching/transferToken (kind = prune iff trace hasPrune else c5Base) + soundness
  checkedTransferMatching_to_activeFullBank: matching ⟹ token family (nonneg, noDoubleSpend from sourceOf
  injectivity, noCrossComponent from trace component, legality from terminal, reserve from slot counts) ⟹
  EndpointReserveHall ⟹ activeFlowAndBoundaryDoors ⟹ ActiveComponentFullBankCert.
- **REMAINING LEDGER**: compiled (identity, mean reserve, EndpointReserveHall, active flow, boundary Doors,
  A-scoped lemma, half-layer); per-cage certificate (orbit tables, base transfers, prune transports,
  matching, generated terms); **GENUINE OPEN: every canonical cage passes the transfer-aware matching gate**
  — locally: Hall-violating obligation sets admit same-cut row-rewrite prune transports with injective slot
  maps + strict local rank decrease. "Maxcut/Γ-min validate or reject exchanges once proposed; THE SLOT MAP
  is the remaining mathematical content."
- **MY RECONCILIATION NOTE (vs Codex 23:19Z "route dead/circular")**: R19's form avoids the circularity —
  same-owner cancellation is the pointwise identity (no new content claimed), and DEFICIT vertices
  (T(v) > N) import REMOTE Free mass via common-bad-neighbour transfers (extra content, not Bank0). Codex's
  side-invariant reduction (NMC via two local one-step checks) and R19's transfer matching are COMPLEMENTARY
  layers of the same spine (corner separation vs active-component funding), both terminating in
  EndpointReserveHall. KEY OBSERVATION: the 3892 needed ZERO prune steps ⟹ the sharpest next question =
  is the BASE-ONLY transfer relation (cancellation + common-bad-neighbour) already Hall-complete on
  canonical cages? If yes, the slot-transport theorem evaporates and the wall = a census-checkable
  base-transfer Hall gate.**]
