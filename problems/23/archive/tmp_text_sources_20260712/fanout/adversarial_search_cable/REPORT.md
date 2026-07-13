# Adversarial short-cable search report

## Exact claims

The search enumerated every tree on the four labeled terminals `(r,m,cL,cR)` with zero through three indistinguishable Steiner vertices, hence 3 through 6 cable edges. Steiner relabelings were quotiented canonically. The required max-cut bipartition was `r,m` on side 0 and `cL,cR` on side 1. Every retained cable is a tree, hence triangle-free, and its unique bipartition matches those prescribed terminal sides.

Counts by edge count were: 3 edges: 4 topologies and 4 seed sets; 4 edges: 24 topologies and 48 seed sets; 5 edges: 121 topologies and 484 seed sets; 6 edges: 524 topologies and 4192 seed sets. Total: 673 topologies and 4728 topology/seed-set pairs. Exactly 673 pairs are stable under the stated adversarial selector model: for each topology the unique stable seed set contains every Steiner vertex.

The R29 cable occurs at record 671 with canonical edges
`r-a, m-a, cL-zL, cR-zR, a-zL, a-zR`, terminal distances from `r` equal to `(0,2,3,3)`, and unique stable internal seed set `{a,zL,zR}`.

Structural invariant (proved directly from the scoped-state definition): let C be a connected set of blue edges. If (i) every vertex of C belongs to every selected union, (ii) no edge of C belongs to any selected row support, and (iii) C contains both endpoints of a selected bad atom, then C lies in an active component under every simultaneous selector trade. If C also meets each hub, every hub remains in that active component. This is independent of Hamming radius.

All arithmetic in the enumerator is integer arithmetic. No float, solver tolerance, Lean `native_decide`, `sorry`, or `admit` occurs.

## Explicit falsifiers

Dropping any internal seed falsifies unconditional cable persistence: an adversarial joint choice may omit that Steiner vertex from the selected union, deleting every incident cable edge from the internal off-support graph. For R29, the first recorded falsifier has no internal seeds and omits `a`; the same construction applies separately to omitted `zL` or `zR`.

Dropping the off-support hypothesis also falsifies persistence: if a selected alternative row contains a cable bridge edge, that edge is removed from the internal graph; choosing a bridge of C disconnects the corresponding terminal shore. Thus seed coverage alone cannot certify stability.

The four smallest compatible cables use no Steiner seeds. Their edge sets are records 0–3 in `results.json`. They are topology candidates only: the full graph must separately exclude new length-4 bad-edge rows and prove the chosen cut maximum.

## Exact global scoped-score status

No exact global scoped-score landscape for the claimed 2943-vertex R29 object can be evaluated from the workspace. The wall archive contains no graph serialization, cut assignment, bad-atom list, 676 selector row banks, or selected baseline tuple. Exact scoped score depends on ordered row-pair multiplicities, row counts, selected support, active components, and HitNeed; cable topology and seed placement do not determine these quantities.

Therefore this lane certifies cable-component persistence under the explicit invariant, but does not certify that Hall failure persists, that 30811 is globally minimal, or that every globally favorable joint selector trade retains a Hall-failing shore. Any such claim would be a surrogate-model error.

## Tested ranges

- Cable edges: every size 3, 4, 5, 6.
- Total cable vertices: every size 4, 5, 6, 7.
- Steiner seed placements: all `2^(n-4)` subsets for every topology.
- Canonical topology records: 673.
- Topology/seed pairs: 4728.
- Terminal side pattern: exactly `(0,0,1,1)` for `(r,m,cL,cR)`.
- Global selector tuples of the actual R29 graph: 0, because the row banks are absent.

## Proof gaps

A graph-realizable candidate still needs: the canonical full graph; proof/check of triangle-freeness after attaching seeds; exact maximum-cut upper certificate; proof that cable edges occur in no admissible shortest row; proof that rigid seed rows remain mandatory; complete row-bank enumeration; exact scoped Hall evaluation after each relevant joint trade; and exact global score minimization. The structural invariant does not force Hall deficiency and does not bound collision or HitNeed changes.

## Reproduction and hashes

Run `python tmp/fanout/adversarial_search_cable/enumerate_cables.py`.

- `enumerate_cables.py`: `7FDFEA42E9E5E06624B43C232C76E1BD80A1E17169040377A21B67D5C8F36060`
- `results.json`: `D72826C3F1B2A2440D088C368F1CF206B670677E6EDCE34551DC49563D2C0B38`
