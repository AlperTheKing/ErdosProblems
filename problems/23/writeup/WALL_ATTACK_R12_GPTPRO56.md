# WALL ATTACK — R12 (first of a multi-reply batch): IES FALSE — 118-vtx traffic-booster CE
# (GPT-5.6 Pro, 2026-07-10/11, RELAYED VERBATIM BY USER — GATE PENDING)

**[CLAUDE GATE HEADER — status: UNGATED (gate script queued: _claude_r12_ies_gate.py; the reply carries its
own checker SHAs 96dd47c6… / 5d41b8189… but the artifacts were not attached — I build my own per discipline).**
- VERDICT: **IES (Internal Endpoint Slack: deg_I(v)/2 ≤ max(0, N − T(v))) is FALSE** in genuine cages.
  118-vtx triangle-free completion of a 16-vtx core: displayed cut is a connected-B, Γ-minimal MAXIMUM cut;
  C = {0..15}, the only induced-blue non-support edge I = {(0,9)}; **T(9) = 120 > N = 118** ⟹ RHS = 0 while
  LHS = deg_I(9)/2 = 1/2. So internal off-support blue load at v cannot in general be charged to
  vertexSlack(v) — traffic boosters can drive T(v) past N.
- Construction (support-preserving; no synthetic ports/terms): core 16 vtx (18 old atoms; 16 retained =
  all but (3,14),(3,15); |A|=16 > |F|=15, unique deficient subfamily = A itself, all 65,535 proper
  subfamilies Hall-satisfying — histogram given); **max-cut lock** = private-path lock q =
  (2,4,4,5,0,0,0,0,0,0,2,4,3,3,2,2), 31 paths v–x–y–c_* (62 private vtx, 93 lock edges), certificate
  g(S) ≤ q(S) for ALL 2^16 core switch sets (max g−q = 0); **traffic booster** = C₅ blow-up
  (P₀={9}, |P₁|=16, |P₂|=4, |P₃|=4, |P₄|=16; c_* ∈ P₃), E(P₀,P₁) bad (16 new atoms 9a, each with 256
  shortest paths ALL through 9 ⟹ T(9) = 8·5 + 16·5 = 120). Totals N=118, E=303, |B|=269, |H|=34;
  maxcut = 269 exact (core 16+g(S) + locks ≤ 93−q(S) + booster ≤ 160 [twin-class monochromatic + weighted C₅
  leaves ≥16 uncut] ⟹ ≤ 269 + g−q ≤ 269); Γ-min automatic (every conn-B max cut has all bad ℓ≥5 ⟹ Γ ≥ 850 =
  displayed). Old rows preserved (lock detours ≥5, booster path c_*–P₄–9 length 2 ⟹ no new ≤4 core paths);
  (0,9) on NO shortest row of any of the 34 atoms.
- Minimality-in-class: lock lower bound 62 private vtx via disjoint switch sets S₁,S₂,S₃ (gains 13/9/9);
  booster class (1,a,b,c,d): needs d≥a, bc≥a, 3a > 38+b+c ⟹ a=16,b=c=4,d=16 exactly ⟹ N=118, T(9)=120.
- Claimed checker output: IES 118 CE PASS; N=118 E=303 blue=269 bad=34 maxCut=269 Gamma=850 |A|=16 |F|=15
  I={(0,9)} T(9)=120 N−T(9)=−2 lhs=1/2 rhs=0.
- CONSEQUENCE (pending my gate): the NMC/corridor route (and any bookkeeping) must NOT rely on
  vertexSlack(v) absorbing internal-edge load — the ½-load of an internal blue edge needs a different sink
  (its own Door if exposed — but (0,9) is INTERNAL: both endpoints in C ⟹ no restriction-exit Door!). This
  sharpens exactly what the innermost-corner construction may charge: internal off-support blue edges are
  the dangerous class (cf. internal_offSupport_boundary_empty: they never cross quotient shores — but they
  DO carry half-layer load in corner cuts). Await the batch's remaining replies before re-pivoting.**]
