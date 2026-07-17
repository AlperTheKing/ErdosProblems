# Adversarial review — section "An eight-vertex neutral square rotor" (claude_eight_vertex_rotor.tex)

Reviewer: referee pass, 2026-07-17.
Files reviewed:
- `problems/23/writeup/arxiv/rotor_window_closures/sections/claude_eight_vertex_rotor.tex`
- `problems/23/writeup/arxiv/rotor_window_closures/sections/claude_eight_vertex_rotor_claims.md`

Sources opened and compared:
- **S1** `problems/23/writeup/WALL_ATTACK_R39_GPTPRO56.md` (full file; claims trace to §4-5, gate header, verdict)
- **S2** `problems/23/writeup/_claude_r39_8vtx_rotor_gate.py` (read in full, SHA-256 recomputed, rerun)
- `problems/23/writeup/arxiv/shortest_support_obstructions/main.tex` (preamble lines 1-14; supp/Hall definition lines 76-97)
- `problems/23/writeup/arxiv/rotor_window_closures/sections/support_circuits.tex` (def:circuit line 53-61, thm:circuit(i) line 71 — for the "support union one edge smaller" cross-reference)

Verifier reruns (2026-07-17, this session):
- **S2 rerun: PASS**, exit 0, output `CLAUDE-GATE=PASS (exhaustive)` + G1-G6 lines, exactly as the manifest reports.
- **SHA-256 recomputed: MATCH** — `6d74bcbd1bab12948c5e1a498f62a7185b03743a2b701ec5aeba6f54b01b2aeb`, equal to the full hash in the tex header comment and the `6d74bcbd` prefix quoted in rem:rotor8-verification.
- **Referee's independent script** (session scratchpad `referee_rotor_checks.py`, exit 0, ALL PASS): (C1) sigma=(x m y v)(a p b q) is an order-4 automorphism, swaps the shores, maps A_m->B_y->A_v->B_x->A_m, and advances each state to the next; (C2) exhaustive 2^8 cut census: maxcut=8 attained by **11 distinct cuts** (incl. the manifest's ax,pm-monochromatic example); (C3) each of the 10 edges lies in exactly two of the four pentagons; (C4) BFS gives d_B(a,b)=d_B(p,q)=4, supports 6/6, union = B; (C5) all four table rows of thm:rotor8-states (owner pair, |S_omega|=7, opposite unselected square edge).
- **LaTeX**: no TeX engine on this machine (pdflatex/tectonic/latexmk absent; consistent with the two prior reviews), so no compile. Static structural audit (scratchpad `latex_audit.py`): all environments balanced and properly nested (2 definition, 2 proposition, 1 lemma, 1 theorem, 2 remark, 4 proof, enumerate/center/tabular); 139/139 inline and 9/9 display math delimiters, zero interleaving errors; brace balance 0; every macro either standard kernel/amsmath (`\leftrightarrow`, `\mathbin{\dot\cup}`, `\H`) or defined in the companion preamble (`\supp`, `\mc`, `\bip`); booktabs rules and `enumitem` key `label=\textup{(\roman*)}` are covered by the companion's `\usepackage{...,booktabs,enumitem,...}`. **PASS** modulo the actual-compile caveat. (Nit: the header comment's assumption list names booktabs but omits enumitem, which the section also needs; the companion does load it.)

## Per-claim verdicts

### Definition def:rotor8 (graph, cut, B, M) — CONFIRMED
Vertices, the ten edges, bipartition {x,y,p,q}|{m,v,a,b}, B = the 8 crossing edges, M = {ab,pq}: verbatim match with S1 §4-5 ("Blue: ax, yb, pm, vq + square xm, my, yv, vx. Bad: ab, pq. Bipartition {x,y,p,q} | {m,v,a,b}"). "Opposite corners" is accurate (x,y and m,v are antipodal on the 4-cycle x-m-y-v). S2 G1 (rerun PASS) checks edge/side sanity. No strengthening.

### Proposition prop:rotor8-maxcut — CONFIRMED
- Statement matches S1 ("Triangle-free, blue-connected", "Maxcut 8 certificate: four C5's; EVERY edge lies in exactly TWO; each C5 caps at 4 => 2*cut <= 16 => cut <= 8 = displayed"). bip(R)=2 is the immediate 10-8; correctly phrased as "**a** maximum cut" — essential, since my C2 census finds 11 distinct maximum cuts (uniqueness would be FALSE; the manifest's exclusion is not merely honest, it dodges an actual error).
- Proof complete: triangle must use exactly one of the disjoint edges ab,pq (B bipartite); N(a)∩N(b)=∅, N(p)∩N(q)=∅ — both neighbourhoods recomputed and correct. Pentagon incidence table recomputed edge-by-edge (C3 PASS: ab,ax,yb in C1,C2; pq,pm,vq in C3,C4; xm:C1,C3; my:C1,C4; yv:C2,C4; vx:C2,C3). Double-count inequality sound (odd cycle crosses <=4). Machine side: S2 G2 verifies mc=8 by full 2^8 enumeration (stronger conclusion; note it does not itself check the pentagon certificate — the remark's itemization states this correctly).

### Lemma lem:rotor8-geodesics — CONFIRMED
- Matches S1 "Row DB (complete): ab -> A_m, A_v; pq -> B_x, B_y. No others" and "both bads at blue distance 4".
- Proof complete: unique B-neighbours of a,b,p,q; length-2 and length-3 paths excluded by explicit empty intersections; length-4 form forced through the unique first/last steps, middle in N_B(x)∩N_B(y)={m,v} resp. N_B(m)∩N_B(v)={x,y} (all four neighbourhoods recomputed — correct). Support sizes 4+4-2=6, union = all of B (C4 PASS). Hall strictness against the companion's condition (2) |supp_B(S)|>=|S|: 6>1, 6>1, 8>2 — "strictly for every nonempty subset" is exact.
- Two nits, neither a gap: (i) length 1 is not explicitly excluded (trivial: ab,pq in M and B∩M=∅; parity also kills it); (ii) S2's G3 enumerates 4-edge blue paths only — the archived script never checks that no *shorter* B-path exists, so "d_B=4" rests on the in-text proof (and my C4 BFS), not on S2. Feeds the rem:rotor8-verification finding below.

### Definition def:rotor8-selection — CONFIRMED
Clean rendering of S1's selected rows / two-edge detours / owners; "disjoint = no owners = pairwise vertex-disjoint" is internally consistent. No verifier needed (manifest: n/a). No hidden strengthening.

### Theorem thm:rotor8-states — CONFIRMED
- Exactly four selections follows from exactly-two-geodesics (lemma). (i) the 4-cycle w_mx w_my w_vy w_vx matches S1's orbit including the transition labels; completeness of the state graph (no diagonal edges) is correctly derived from the one-coordinate characterization. (ii)-(iii): all four table rows recomputed independently (C5 PASS): owner pairs {m,x},{m,y},{v,y},{v,x} (each square edge exactly once — hence no disjoint selection), |S_omega|=7 with unselected edge yv/vx/xm/my = the square edge vertex-disjoint from the owner pair. Matches S1 "Unselected square edge per state: yv / xv / xm / my" (xv=vx).
- S2 G4 (missing edge + one-middle-swap transitions in-family), G5 (support/active-edge: proves |S_omega|=7 since the only blue edge outside support is the tabled one), G6 (shared vertex pairs) — all rerun PASS.
- Proof completeness: one row fully expanded, other three declared "identical checks" backed by the printed table. Acceptable for a 4-row finite check; every entry has been re-verified here.

### Proposition prop:rotor8-neutral — CONFIRMED (mathematics); see MISMATCH below for its verification status
- The manifest's honesty flag is accurate: **S1 contains no automorphism** — sigma is the drafter's in-text formalization of S1's verified "four-state orbit / collision mass ROTATES", and this is exactly how the manifest labels it.
- In-text proof complete and correct: all ten edge images listed and recomputed (ax->pm, yb->vq, pm->yb, vq->ax; square rotates xm->my->yv->vx->xm; ab<->pq); order 4 visible from the cycle type (sigma^2 = (xy)(mv)(ab)(pq) != id); sigma(V_0)=V_1; the four path images (two reversed, correctly flagged "(reversed)") give A_m->B_y->A_v->B_x->A_m; state action w_mx->w_my->w_vy->w_vx->w_mx recomputed. Independently machine-verified this session (C1 PASS) — replicating the manifest's ad-hoc check, which is NOT archived anywhere in the repo.

### Remark rem:rotor8-scope — CONFIRMED
- "A support circuit has support union one edge smaller than its atom set" is exactly thm:circuit(i) (|F*|=m-1) of support_circuits.tex — correct cross-section usage; here |M|=2, |supp_B(M)|=8, selected support 7: not remotely deficient. Unselected edge's endpoints lie on the square {x,m,y,v}, disjoint from {a,b,p,q} — correct.
- The open graft question is stated with no numbers or gate conditions imported from S1 §7-8 (the unverified blueprint) — matches the manifest's exclusion, and matches S1's own framing ("NOT a falsifier by itself... open content is ENTIRELY in the graft").
- bip(R)=2 < 64/25 and the no-bearing closing sentence: correct and honest.

### Remark rem:rotor8-verification — MISMATCH (overclaim; the section's one real defect)
Two false components in an otherwise honest remark:
1. **"every numbered statement of this section is machine-verified by an exhaustive script"** — false for Proposition rem:rotor8-neutral. The archived script contains no automorphism check whatsoever (grep for `sigma`/`automorph` over S2: 0 hits). The manifest itself concedes the only machine check of sigma was an **unarchived throwaway session script**. The same universal overclaim appears in the section intro (lines 28-31: "all of them have in addition been verified exhaustively by machine"). The itemized list after the colon (G1-G6 content) is accurate — it is precisely the universal quantifier that outruns it. Secondary looseness: for lem:rotor8-geodesics the script verifies 4-path completeness but never that d_B=4 (no shorter-path check), so even there "machine-verified" holds only for the completeness half of the lemma.
2. **"included in the ancillary archive"** — no `anc/` directory exists under `rotor_window_closures/`; the script lives at `problems/23/writeup/_claude_r39_8vtx_rotor_gate.py`, outside any arXiv package. Currently an unfulfilled packaging claim.

**Fix (either resolves item 1):** (a) reword both sentences to "every numbered statement except the automorphism of Proposition~\ref{prop:rotor8-neutral}, whose finite check appears in full in the text"; or (b) archive a sigma-checking script (the referee's C1 block is a ready template) alongside the gate and cite both. For item 2: create `rotor_window_closures/anc/`, copy the gate script in, add SHA256SUMS — before any version of this section ships.

### Manifest exclusion list — CONFIRMED (all eight)
Grep of the tex for `Gamma|50|halves|Lean|Checked|covered star|unique max`: **0 hits**. Specifically: Gamma_min=50 absent; max-cut uniqueness never claimed (and is in fact false — 11 maximum cuts, C2); cascade refutations absent; blueprint absent except the one-sentence open question; pair-mass absent; Lean structure names absent; "8 halves" absent; "covered stars" absent. The exclusions are exactly right, and the uniqueness exclusion prevented an outright false statement.

## Minor wording items (no verdict change)
- Intro line ~27: "the natural local repair walk ... **cycles with period four**" — what is proved is: the state graph is a 4-cycle, every state has a collision, hence the walk **never terminates**; a nondeterministic walk may backtrack (period 2) rather than rotate. Same slight overstatement in rem:rotor8-scope ("perpetual rotation"). Suggest "never terminates: the states form a four-cycle and every state carries a collision".
- "no canonical tie-break can halt the walk" (before prop:rotor8-neutral): defensible prose (no disjoint selection exists, so nothing can halt at success regardless of tie-break), but the sentence leans on the automorphism for "canonical"; consider "no isomorphism-invariant tie-break distinguishes the states".
- Header comment: add `enumitem` to the assumed-preamble list.

## Verdict summary

| Claim | Verdict |
|---|---|
| def:rotor8 | CONFIRMED |
| prop:rotor8-maxcut | CONFIRMED |
| lem:rotor8-geodesics | CONFIRMED |
| def:rotor8-selection | CONFIRMED |
| thm:rotor8-states | CONFIRMED |
| prop:rotor8-neutral | CONFIRMED (math; verification-status caveat) |
| rem:rotor8-scope | CONFIRMED |
| rem:rotor8-verification | **MISMATCH** (overclaims scope + archive location of machine verification) |
| Exclusion list (8 items) | CONFIRMED |

**Most serious issue:** rem:rotor8-verification (and the echo in the intro) claims *every numbered statement* is machine-verified by the archived exhaustive script, but the automorphism content of Proposition rem:rotor8-neutral is not checked by that script at all (its only machine check was an unarchived ad-hoc session script), and the script is not yet in any ancillary archive. The mathematics itself survived full adversarial re-derivation and independent machine re-verification without a single error.
