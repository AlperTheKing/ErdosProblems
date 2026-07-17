# Claims manifest — Section "An eight-vertex neutral square rotor"

Section file: `problems/23/writeup/arxiv/rotor_window_closures/sections/claude_eight_vertex_rotor.tex`
Drafted 2026-07-17 by Claude (Fable 5).

Sources (the only ones used):
- **S1** = `problems/23/writeup/WALL_ATTACK_R39_GPTPRO56.md` (secs. 4-5, GPT-5.6 Pro R39, gated by Claude header)
- **S2** = `problems/23/writeup/_claude_r39_8vtx_rotor_gate.py` — exhaustive verifier, single script, re-run 2026-07-17 with output `CLAUDE-GATE=PASS (exhaustive)`.
  SHA-256 `6d74bcbd1bab12948c5e1a498f62a7185b03743a2b701ec5aeba6f54b01b2aeb` (prefix `6d74bcbd` quoted in the tex).

No dual (second independent) verifier exists for this section; the tex therefore claims one exhaustive script PLUS complete in-text hand proofs, not dual verification.

## Numbered claims

| # | Claim (summary) | Status | Source(s) | Verifier |
|---|---|---|---|---|
| Definition `def:rotor8` | Graph R: 8 vertices a,b,p,q,x,y,m,v; edges ax,yb,pm,vq + square xm,my,yv,vx + bad ab,pq; cut V0={x,y,p,q}, V1={m,v,a,b}; B = 8 crossing edges, M = {ab,pq} | construction (definition) | S1 sec. 4-5 | S2 gate G1 (edge/side sanity) |
| Proposition `prop:rotor8-maxcut` | R triangle-free, B connected, MaxCut(R)=8, bip(R)=2; proof by common-neighbour check + four-pentagon double count (each edge in exactly two C5s, each C5 caps at 4) | proved (full proof in text) + computer-assisted | S1 sec. 4-5 ("Maxcut 8 certificate: four C5's, every edge in exactly TWO") | S2 gates G1, G2 (exhaustive 2^8 cuts), SHA prefix 6d74bcbd |
| Lemma `lem:rotor8-geodesics` | d_B(a,b)=d_B(p,q)=4; complete geodesic families A_m,A_v (for ab) and B_x,B_y (for pq); each support has 6 edges; supp_B(M)=B; Hall condition strict | proved (full proof in text, unique-B-neighbour argument) + computer-assisted | S1 sec. 4-5 ("Row DB (complete) ... No others") | S2 gate G3 (exhaustive DFS over blue 4-paths) |
| Definition `def:rotor8-selection` | Selection, selected support S_omega, detour move, owner, disjoint selection | definition (clean-language rendering of S1's "selected rows / two-edge detours / owners") | S1 sec. 4-5 | n/a |
| Theorem `thm:rotor8-states` | Exactly 4 selections; (i) state graph under detour moves = 4-cycle; (ii) each state's geodesics intersect in exactly the tabled square-edge pair {m,x},{m,y},{v,y},{v,x} — hence no disjoint selection exists; (iii) each state has \|S_omega\|=7, unselected edge = square edge opposite the owner pair (yv/vx/xm/my) | proved (finite table, full proof in text) + computer-assisted | S1 sec. 4-5 ("Four-state orbit ... Unselected square edge per state: yv/xv/xm/my ... Collision mass ROTATES") | S2 gates G4, G5, G6 (per-state supports, missing edge, shared pairs, one-middle-swap transitions) |
| Proposition `prop:rotor8-neutral` | sigma=(x m y v)(a p b q) is an order-4 automorphism of R exchanging the shores, mapping A_m→B_y→A_v→B_x and advancing the rotor by one state | proved (direct check on 10 edges, full proof in text). NOTE: the automorphism itself is NOT stated in S1; it is the in-text formalization of S1's verified "collision mass rotates / four-state orbit" claim. Additionally machine-checked ad hoc this session (throwaway script, output: automorphism True, shore swap True, all four geodesic images True) | S1 sec. 4-5 (rotation claim) + in-text proof | in-text finite check (+ ad-hoc session check, not archived) |
| Remark `rem:rotor8-scope` | Rotor is NOT a Hall violation (\|M\|=2, \|supp\|=8, selected support 7); unselected edge meets no bad edge; kills disjoint-representative / terminating-repair arguments; embedding a rotor so the collision couples to a support deficiency is OPEN; no bearing on the n^2/25 conjecture | proved facts restated + explicit open question | S1 verdict + gate header ("NOT a falsifier by itself ... open content is ENTIRELY in the graft") | S2 gate G5 |
| Remark `rem:rotor8-verification` | Verification statement: one exhaustive script, what it checks, SHA prefix | meta (honest reporting) | S2 | S2, SHA 6d74bcbd... |

## Claims EXCLUDED for verification reasons

- **"Gamma_min = 2*25 = 50"** (S1): only the fixed-cut value Gamma=50 follows from the proved distance-4 facts; the minimum over all maximum cuts is not verified by S2. Excluded entirely.
- **Uniqueness of the maximum cut**: not claimed in S1 and not verified by S2 (S2 only proves the maximum value 8). In fact other 8-edge cuts exist (e.g. making ax,pm monochromatic), so the section deliberately never says "unique maximum cut".
- **Cascade refutations (S1 secs. 1-2)**: `saturatedPair_preservesSelectedEdge` etc. are marked "compile-ready" (i.e. NOT compiled Lean) and verified only "by inspection" in S1; engine-internal. Excluded.
- **Active-grafted rotor family blueprint (S1 secs. 7-8)**: ~400-800-vertex falsifier blueprint with gate conditions — explicitly a conjecture/experiment plan in S1, unverified. Excluded except as the one-sentence open question in `rem:rotor8-scope`.
- **Pair-mass counting discussion (S1 sec. 6)**: heuristic non-exclusion argument, no verifier. Excluded.
- **Lean structures (S1 secs. 9-10)** `CheckedAlternatingMiddleSquare`, `CheckedActiveNeutralSquareRotor`, `noPositiveDefectActiveAlternatingMiddleRotor`: named as compile-ready obligations, no compiled module exists, so nothing in the section is labeled Lean-verified. Excluded.
- **"8 halves" collision-mass bookkeeping (S1/S2 G6 unit count)**: engine-specific weighting; replaced by the equivalent clean statements actually verified (shared pair = tabled square edge in every state; pattern constant across states via the automorphism).
- **"Covered stars" terminology** (mentioned in the drafting brief): absent from S1/S2, so not introduced.
