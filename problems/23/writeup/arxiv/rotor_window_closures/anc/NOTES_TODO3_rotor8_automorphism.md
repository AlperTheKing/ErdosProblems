# NOTES — TODO-3: automorphism verifier for prop:rotor8-neutral

Agent notes, 2026-07-17. For the integrator; delete this file from anc/
before arXiv packaging (it is not a paper artifact).

## What was added

- `anc/verify_rotor8_automorphism.py` — new, stdlib-only, exact
  set/integer arithmetic, ASCII output. SHA-256
  `756cc65aa366103420d6ac965a0869689641ad81906358b498b71fa306d0eb4d`.
- Nothing else was touched. No .tex, no CLAIMS_LEDGER.md, no SHA256SUMS
  edits (per hard rules).

## What it verifies (Proposition prop:rotor8-neutral,
sections/claude_eight_vertex_rotor.tex)

- CHECK1 sigma = (x m y v)(a p b q) is a graph automorphism of R:
  adjacency preserved on all 28 unordered vertex pairs; sigma(E) = E.
- CHECK2 order exactly 4: sigma^4 = id, sigma^k != id for k = 1,2,3.
- CHECK3 cut compatibility: sigma(V0) = V1, sigma(V1) = V0,
  sigma(B) = B, sigma(M) = M (setwise).
- CHECK4 states recomputed from scratch: d_B(a,b) = d_B(p,q) = 4 by BFS
  in B; ALL B-geodesics re-enumerated (layered exhaustive search:
  exactly 2 per bad edge); exactly 4 selections; sigma maps selections
  to selections and acts as a single 4-cycle, hence transitively.
  Nothing hard-coded: geodesics, selections, and the action are all
  derived from the edge list.
- CHECK5 the paper's explicit orbit: A_m -> B_y -> A_v -> B_x -> A_m
  (paths up to reversal) and w_mx -> w_my -> w_vy -> w_vx -> w_mx.

## Run record (2026-07-17, this machine, python 3.x)

```
PASS CHECK1_automorphism | all 28 vertex pairs adjacency-preserved; sigma(E)=E
PASS CHECK2_order_four | sigma^4=id; sigma^k!=id for k=1,2,3
PASS CHECK3_shore_swap_cut_preserved | sigma(V0)=V1, sigma(V1)=V0, sigma(B)=B, sigma(M)=M
PASS CHECK4_states_recomputed_transitive | d_B(p,q)=4 #geodesics=2; d_B(a,b)=4 #geodesics=2; 4 selections; sigma-action = single 4-cycle (transitive)
PASS CHECK5_paper_orbit_labels | sigma: A_m->B_y->A_v->B_x->A_m and w_mx->w_my->w_vy->w_vx->w_mx
PASS_ROTOR8_AUTOMORPHISM
```
Exit code 0.

Negative controls (mutated copies in session scratchpad, not archived):
wrong second cycle (a b p q) -> CHECK1/3/4/5 FAIL, exit 1; deleted
square edge -> input-sanity assertion, exit 1; sigma^2 (a genuine
order-2 shore-fixing automorphism) -> CHECK1 PASS but CHECK2/3/4 FAIL,
exit 1. The verifier is falsifiable and discriminates the three claim
components.

Also rerun from anc/: `_claude_r39_8vtx_rotor_gate.py` -> 
`CLAUDE-GATE=PASS (exhaustive)`, exit 0 (SHA unchanged 6d74bcbd...).

## Recommended integrator edits (all checks PASSED, so the
CLAIMS_LEDGER TODO-3 wording restoration is warranted)

1. `sections/claude_eight_vertex_rotor.tex`, intro paragraph — old:

   "elementary finite check, proved in full below; all of them except the
   automorphism of Proposition~\ref{prop:rotor8-neutral}, whose finite
   check appears in full in the text, have in
   addition been verified exhaustively by machine
   (Remark~\ref{rem:rotor8-verification})."

   new:

   "elementary finite check, proved in full below; all of them have in
   addition been verified exhaustively by machine
   (Remark~\ref{rem:rotor8-verification})."

2. `sections/claude_eight_vertex_rotor.tex`, rem:rotor8-verification — old:

   "All proofs above are complete and elementary. Independently, every
   numbered statement of this section except the automorphism of
   Proposition~\ref{prop:rotor8-neutral}, whose finite check appears in
   full in the text, is machine-verified by an exhaustive
   script included in the ancillary archive
   (\texttt{\_claude\_r39\_8vtx\_rotor\_gate.py}, SHA-256 prefix
   \texttt{6d74bcbd}): triangle-freeness, bipartiteness and connectivity
   of \(B\); \(\mc(R)=8\) by enumeration of all \(2^8\) cuts; completeness
   of the two geodesic families by exhaustive search over four-edge
   crossing paths (the value \(d_B=4\) itself is the short in-text
   argument); and, for each
   of the four states, the selected support, the unselected edge, the
   owner pair, and the one-coordinate structure of the four detour
   transitions."

   new:

   "All proofs above are complete and elementary. Independently, every
   numbered statement of this section is machine-verified by two
   exhaustive scripts included in the ancillary archive. The first
   (\texttt{\_claude\_r39\_8vtx\_rotor\_gate.py}, SHA-256 prefix
   \texttt{6d74bcbd}) checks triangle-freeness, bipartiteness and
   connectivity of \(B\); \(\mc(R)=8\) by enumeration of all \(2^8\)
   cuts; completeness of the two geodesic families by exhaustive search
   over four-edge crossing paths; and, for each of the four states, the
   selected support, the unselected edge, the owner pair, and the
   one-coordinate structure of the four detour transitions. The second
   (\texttt{verify\_rotor8\_automorphism.py}, SHA-256 prefix
   \texttt{756cc65a}) checks the automorphism of
   Proposition~\ref{prop:rotor8-neutral}: that \(\sigma\) preserves
   adjacency on all vertex pairs, has order exactly four, exchanges the
   shores and fixes \(B\) and \(M\) setwise, and---after recomputing
   \(d_B=4\) by breadth-first search and re-enumerating the geodesic
   families and the four selections from scratch---maps the geodesics
   and the states in the stated four-cycles, in particular acting
   transitively on the states."

   (The dropped parenthetical "(the value \(d_B=4\) itself is the short
   in-text argument)" is superseded: the second script now recomputes
   \(d_B=4\) by BFS, closing the referee's secondary-looseness nit in
   review_rotor-construction.md.)

3. `anc/SHA256SUMS` — add (alphabetical position: before
   `verify_t4_atom_census.py`):

   756cc65aa366103420d6ac965a0869689641ad81906358b498b71fa306d0eb4d  verify_rotor8_automorphism.py

4. `CLAIMS_LEDGER.md` — Section 4 table, prop:rotor8-neutral row:
   "proved | in-text finite check ONLY (not covered by the archived gate
   script — now stated correctly in text)" -> "proved + CA | in-text
   finite check + anc/verify_rotor8_automorphism.py (SHA 756cc65a...,
   PASS 2026-07-17: automorphism, order 4, shore swap, BFS d_B=4,
   states recomputed, transitive 4-cycle action)". Mark remaining-TODO
   item 3 done ("every numbered statement" phrasing restored).
