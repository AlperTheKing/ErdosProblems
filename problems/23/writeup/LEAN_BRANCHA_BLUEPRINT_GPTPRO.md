# Lean Branch-A Blueprint (GPT-Pro, 2026-07-04, sibling thread; full text 19k chars —
# essentials archived, full reread available in thread 6a45e152)

DESIGN RULE: NO Lean quotient types for the weighted quotient layer. Indexed bags +
certificate records: cls : V -> ZMod 5; bag10 : V -> Fin 10; w : Fin 10 -> Q.
All checkers reflective/data-driven like the Branch-B layer.

MODULE TREE: Erdos23/BranchA/{Interface, RowBounds, TerminalHall, DoorTree,
Quot/{C5Hom, Seed10, SevenCutCone, EQ, Sibling},
Cert/{Poly, ConeCert, BernsteinSimplex, BernsteinCube, Corridor},
Data/{ConeData, SimplexData, CubeData, CorridorData,...}}.

KEY OBJECTS:
- StrongActive5Bound S Q : I(Q) - N <= (2/3) eta as a separate leaf; theorem
  strongActive5_implies_gersh (0 <= eta).
- C5HomSupport structure {supp, cls, supp_closed, row_mem, edge_adj: adjacent =>
  cls differs by +-1}; C5_RS as predicate over CutState/Row (len = 5).
- SevenCutSpec generic; named slacks SIB.s1..s7 exposed but checker uses generic spec.
- Cert/Poly: small reflective AST — inductive Var (N | w Fin10 | mu34..mu56 | rho |
  simplex Nat | aux Nat), inductive Poly (const Q | var | add | mul | pow); evalPoly;
  soundness eval_add/eval_mul/eval_pow_nonneg; Poly.checkEq reflective equality with
  checkEq_sound. NOT MvPolynomial for large data.
- CorridorCert {C, kind in {nonneg, cross, label, osc}, payload} + per-kind soundness
  (nonneg via integer check; cross needs nuK_nonneg; label needs NonC5Hom; osc local
  gate) + CorridorCertSet.T2_sound global.
- Z5LabelCert {label : V -> ZMod 5, edge_check C5Adj}; RISK: ZMod simp loops —
  decidable checkC5Adj : Bool + checkC5Adj_sound proven once; avoid ring_nf on ZMod 5.
- Bernstein data risk: chunk by row and chart (EQ_cube_R0_sound .. R10, then combine).
- **CORRECTION (Claude)**: blueprint item 8 suggests native_decide for seed-row
  membership — FORBIDDEN by our rules; substitute plain decide / rfl on literal data
  (rows are tiny). Everything else respects the kernel-only constraint.

IMPLEMENTATION ORDER: Interface.lean (GershBound, GERSH_L5, semantic predicates) ->
Quot/C5Hom (C5Adj, C5HomSupport, checkC5Adj) -> SevenCutCone -> Cert/Poly ->
ConeCert/BernsteinSimplex/BernsteinCube -> Corridor -> Data -> DoorTree assembly
(ten-assumption conditional theorem from the audit as SeedDoorTreeCoverageCert +
leaf soundness; coverage = boolean finite data, soundness = semantic).
