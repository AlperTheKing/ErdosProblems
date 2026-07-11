# WALL ATTACK — R39: CASCADE FAILS (saturation preserves the support edge); EXACT 8-VTX 4-STATE NEUTRAL
# SQUARE ROTOR CONSTRUCTED ON A GENUINE CAGE; wall = noPositiveDefectActiveAlternatingMiddleRotor;
# route hinges on the ACTIVE-GRAFTED ROTOR FAMILY EXPERIMENT (falsifier blueprint, ~400-800 vtx)
# (GPT-5.6 Pro, 2026-07-12, "worked 12m54s"; harvested ~12.6k ch)

**[CLAUDE GATE HEADER — my full exhaustive gate of the 8-vtx rotor runs THIS TICK (tiny graph: 2^8 cuts,
DFS row families, 4-state detour cycle, scoped defect per state); the two cascade-refutations are verified by
inspection (both are direct consequences of the detour cell identity + the definition of selected support:
n(m,x)>=2 means >=2 selected rows USE blue edge xm, so removing one keeps xm in support — saturation prevents
exactly the activation it would need). The active-grafted family blueprint goes to Codex as the NEW TOP
FALSIFIER LANE; R40 asks GPT to make the parameter-3 instance fully explicit. The 8-vtx rotor is NOT itself
a falsifier (its lone off-support square edge is an inactive component, no bad endpoints => no scoped
obligations); the open content is ENTIRELY in the graft.]**

## Verdict
Middle-saturation cascade does not close. The alternation CAN close finitely on a real cage: an exact
8-vertex four-state neutral square rotor exists with every canonical local hypothesis satisfied. The
remaining question is a GLOBAL ACTIVE-GRAFTING question, not local saturation counting.

## 1-2. The two false cascade implications
- **Saturated middles need not be owners**: for retained x with old selected edge xm blue, n_ω(m,x) ≥ 2 means
  ≥2 selected rows use edge xm; removing Q leaves another producer ⟹ xm ∈ S_ω′ (support). Saturation prevents
  precisely the edge that might pull m into the active component. Compile-ready:
  `saturatedPair_preservesSelectedEdge (hxm : blueAdj x m) (hcurrent : edgeMem (ω f) x m) (hmult : 2 ≤ n ω x m) :
  edgeMem (selectedSupport (update ω f Q′)) x m`. Even active m's obligations need not join the same alternating
  core (closure follows eligibility edges, not vertex membership).
- **New middle not symmetrically saturated**: vx was internal off-support ⟹ n_ω(v,x)=0 (compiled co-occurrence
  theorem) ⟹ n_ω′(v,x)=1 — no collision at the generating pair; no termwise n_ω′(v,z) ≥ 2.
- **Opposite-middle (m,v)**: Free ⟹ two common-blue sources for owners x,y — may simply be matched (+2/+2,
  unit defect survives). Covered ⟹ m,v at distance 2 in a selected row (distance 4 impossible: m−x−v is a blue
  2-path) ⟹ another two-edge detour — may be equal-defect, stays in the SCC. No unbounded chain.

## 4-5. THE 8-VERTEX ROTOR (exact, canonical)
Vertices a,b,p,q,x,y,m,v. Blue: ax, yb, pm, vq + square xm, my, yv, vx. Bad: ab, pq. Bipartition
{x,y,p,q} | {m,v,a,b}. Triangle-free, blue-connected.
- Row DB (complete): ab → A_m=(a,x,m,y,b), A_v=(a,x,v,y,b); pq → B_x=(p,m,x,v,q), B_y=(p,m,y,v,q). No others.
- **Maxcut 8 certificate**: rows+bad edges form four C5's; EVERY edge lies in exactly TWO of them; each C5 caps
  at 4 cut edges ⟹ 2·cut ≤ 16 ⟹ cut ≤ 8 = displayed. Γ_min = 2·25 = 50 (both bads at blue distance 4, ℓ≥5).
- **Four-state orbit** (each transition a two-edge detour across the same square):
  ω_{m,x}={A_m,B_x} →(B_x→B_y)→ ω_{m,y} →(A_m→A_v)→ ω_{v,y} →(B_y→B_x)→ ω_{v,x} →(A_v→A_m)→ ω_{m,x}.
  Unselected square edge per state: yv / xv / xm / my. Collision mass ROTATES (total 8 halves each state).
- NOT a falsifier by itself: the lone unselected square edge is an inactive one-edge component (no bad
  endpoints ⟹ no scoped obligations). The rotor proves the canonical hypotheses do NOT forbid finite rotors.

## 6. Why pair-mass counting cannot exclude rotors
Σ_{u,z} n(u,z) = 25|M| total; saturation gives only Σ_{S*} ≥ 8|S*|; no canonical |M|-vs-|S*| inequality
(double-star blocks make |M| quadratic with fixed hubs); one row satisfies several saturation requirements at
once (requirements do NOT consume disjoint mass).

## 7-8. ACTIVE-GRAFTED ROTOR FAMILY (the falsifier blueprint — NEW TOP LANE)
Core = 8-vtx rotor. **Active pin**: blue I-spine length ≥6 between endpoints of a fixed bad atom
(s−u1−u2−c−u3−u4−t); attach each of x,y,m,v by a PRIVATE blue branch (length 2 same-side-as-c; 1 or 3
opposite; private interiors avoid triangles); all spine/branch edges internal off-support in every rotor state
⟹ all four square vertices in ONE active component in all 4 states. **Symmetric collision pressure**: identical
endpoint-anchored traffic blocks at x,y,m,v (first target: four K3,3 double-star blocks) — make each rotating
owner collision-heavy, keep the 4 states defect-symmetric. **Support family**: optionally attach the known
28/27 minimal circuit at spine midpoint c (certifies inclusion-minimal defect one independently).
**Maxcut locks**: private even length-6 lock path per bad edge; selector-C5 construction if lock vertices must
be selected. Parameter-3 instance: ~60-70 bad atoms before selector closure, ~300-350 lock vertices, total
~400-800 vertices.
**Gate conditions (decisive only if ALL verified)**: four tuples same globally-minimal POSITIVE defect; sink
SCC; checked detours; every probe FreeHalf matched or label-blocked; every transition-created half matched/
blocked in target; no P4/P5 exposure from locks/selector residues; NO tuple outside the orbit with smaller
defect. **Likely blockers** (what the gate must report): unintended shortest rows from the pin; common-blue
proliferation from branch neighbours; quiescent attachment from private locks; selector alternatives lowering
defect outside the orbit.

## 9-10. Compile-ready structures + the new honest obligation
`CheckedAlternatingMiddleSquare` (8 named vertices, square, two atoms, four named rows) and
`CheckedActiveNeutralSquareRotor` (states : Fin 4 → RowTuple; optimalMatching; positive_equal_defect;
globally_minimal; sinkTransitions; zeroExposure). A checked value = decisive falsifier of
canonicalCollisionFeasibleTuple_exists. **NEW FINAL OBLIGATION:
`noPositiveDefectActiveAlternatingMiddleRotor (hcanonical) (R : CheckedActiveNeutralSquareRotor D) : False`**
— equivalently every active graft exposes: unused common-blue source ⊕ outside/quiescent attachment source ⊕
lower-defect tuple outside the orbit. No current theorem proves that disjunction. The falsifier gate on the
structured family is now MORE INFORMATIVE than further local counting: a hit kills the selection route; a
systematic failure names the final graph lemma.
