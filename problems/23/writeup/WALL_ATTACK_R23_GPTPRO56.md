# WALL ATTACK — R23: THE FOURTH PATTERN (outside-component attachment transfer) — NON-LOCAL,
# repairs the 89 falsifier to FULL matching; VERIFIED by my gate on 89 + 311
# (GPT-5.6 Pro, 2026-07-11; exit (a) of my repair question)

**[CLAUDE GATE VERDICT — _claude_r23_outside_attachment_gate.py SHA
6147ac4c7b501f8ab46597ef210838e1138f0b7cb15910a4712dc5efac844cec, ALL PASS rc=0:**
- **PATTERN 4 (outsideAttachment)**: fix tuple ω; U_ω = union of selected row vertices; for x ∉ U_ω,
  K_ω(x) = blue component of x in B[V∖U_ω], Att_ω(x) = N_B(K_ω(x)) ∩ U_ω (nonempty by B-connectedness).
  Free ordered pair (x,y), x≠y, BOTH outside U_ω, is a source for owner v iff ∃ a ∈ Att(x), b ∈ Att(y)
  with n_ω(v,a) > 0 ∧ n_ω(v,b) > 0 (+ component equalities comp(a)=comp(v)=comp(b)). Switch set =
  K(x) ∪ K(y); loss ≥ 0 recomputed (automatic at max cut). Capacity = the FreeHalf unit 1/(2K) — switch
  loss is NEVER spent; the same switch set may annotate many sources. Outside pairs can never be
  active-edge orientations (active ⊆ U×U) ⟹ both half-bits available. **Deliberately NON-LOCAL**
  ("contract the entire blue region outside the selected row union") — exactly the escape from the
  bounded-locality trap the 89 CE exposed.
- **MY GATE, 89**: outside = ONE 77-vtx component (via anchor), Att = the 9 leaves, loss(S) = 38;
  all 77·76 ordered pairs eligible for every hub (+11,704 halves at W; old 526 + new = 12,230 vs 528);
  **global max-flow now 776/776 — FULL matching, falsifier repaired.** Explicit first transfer (13,14)
  matches GPT's.
- **MY GATE, 311 (fixed lex-least tuple)**: owner-9 demand = 636 halves ✓; eligible outside vertices for
  owner 9 = **191** — my decomposition 63 P3 + 63 P1 + 65 lock vertices of atoms a₁..a₁₃ (endpoints
  co-occurring with 9) ⟹ +2·191·190 = 72,580 halves ✓ exactly GPT's number; **global max-flow 3606/3606.**
- **MONOTONE EXTENSION**: R_new ⊇ R_old ⟹ every previously passing fixture (24/167/175/3892) remains
  passing unchanged — pattern 4 cannot break a passing certificate.
- **TIE-BREAKING** (three hubs share one pool): lexicographically least full injection — for the least
  remaining obligation take the least unused eligible source whose removal keeps residual max-flow =
  remaining obligations (12); deterministic, finite; injectivity of sourceIds ⟹ no double spend; destination
  component ⟹ no cross spend. Shared ELIGIBILITY never creates shared CAPACITY.
- **LEAN SHAPES GIVEN**: CheckedOutsideAttachmentBaseTerminal (outside/attach/path/companion/component/
  switch fields; FreeHalfKey already carries isFree + bit), .term (kind c5Base, sourceId = encoded key,
  support {owner}, capQ 1/(2K)), computed legal relation, outsideAttachmentTerminal_sound (rfl/positivity/
  simp/exact — no new axioms), wrapper checkedMatching_withOutsideAttachment_sound :=
  checkedTransferMatching_to_activeFullBank (the compiled consumer is UNCHANGED — soundness inherited;
  matching existence was the only open part).
- **FALSIFIER GATE (14)**: old ∪ outsideAttachment relation, exact integer max-flow; decisive failure =
  obligation set Z with |Z| > |Reach(Z)| + full export (tuple ID, U mask, component IDs+masks, attachment
  boundaries, witnesses, losses, gap). Claimed artifact SHA da87c2cb… (gate queued vs Codex re-run).
- **NEW SHARP QUESTION (R24)**: is the FOUR-pattern relation Hall-complete on all canonical cages?
  A future falsifier now needs outside components whose attachment boundaries systematically AVOID the
  overloaded owners' co-occurrence sets — while those same owners carry heavy row traffic. Codex census
  lane re-armed with pattern 4; GPT gets the prove-or-break.**]
