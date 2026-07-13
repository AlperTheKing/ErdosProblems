# Wave 4 rotor-specific C5-core extraction

## Verdict

The requested extraction is **not proved** by the present M3 interface.  No
rotor/transport field in `CheckedBalancedDeficiencyRotor` supplies a bounded
exception set, and the balanced ledger is exactly orthogonal to such a bound.

The smallest exact adversarial object in the accepted fixture battery is the
live-x `t=5` support circuit, padded by seven isolated vertices to order 25.
It satisfies every graph/row/circuit M3 field that can be instantiated without
asserting a production rotor:

```text
checkGraph                         true
checkCut                           true
TriangleFree                       true
window                             5
G.n = 5*window                     25 = 25
bads.length = window^2             25 = 25
CompleteShortestRowDB              true (76/76 rows, exact enumeration)
|completeRowSupport|+1=|bads|      24+1=25
dB(owner)=dM(owner)=rowCount       5=5=5
live middle swap                   present at atom (2,3), owner x=9
```

Nevertheless it has neither extraction outcome:

```text
G -> C5                            UNSAT (DRAT verified)
aligned complete C5 core, q >= 2  UNSAT for both cut complements
maximum aligned q                  1, hence K=5-q=4
```

The first missing production field is exactly `max_cut`.  The switch

```text
S = {4,5,6,7,8,11,14,16}
```

crosses 23 bad edges and only two blue edges, so `sigma(S)=2-23=-21`.
Thus the displayed cut is not maximum.  The source's stronger eight-split
extension gate also proves that no triangle-free, row-preserving ambient
blue completion on the seven missing vertices repairs this fixed circuit.

This is therefore an exact counterexample to the proposed extraction with
`max_cut` removed, not a full `CheckedBalancedDeficiencyRotor` and not a
counterexample to Erdos #23.  It identifies the load-bearing field: bounded
`K`, if true, must come from the interaction

```text
max_cut + complete_rows + circuit_cardinality + triangle_free,
```

not from any current neutral-transport field.

## Quantified counterlemma

Let `P` be the graph on `Fin 25` obtained from the accepted live-x source

```text
tmp/fanout/r42_graph_specific_exclusion/
  t5_live_x_classifier_v_l9_r9_5000.json
```

by retaining its 18-vertex blue support and 25 selected bad atoms and adding
vertices `18,...,24` as isolates.  Give vertices `0,...,8` cut side zero,
vertices `9,...,17` cut side one, and the isolates side zero.  Let `bads`
list the 25 selected atoms with the source's full row lists.

Then:

1. `P` is simple and triangle-free, and the displayed cut classifies all 24
   support edges as blue and all 25 atoms as bad.
2. The atom keys are distinct and cover every bad edge exactly once.
3. Direct DFS enumeration gives exactly the 76 listed simple four-edge blue
   paths, with no missing or extra row.  Their union is the declared 24-edge
   support.
4. There is no homomorphism `P -> C5`.
5. There do not exist disjoint `X_0,...,X_4`, each of cardinality at least
   two, compatible with either aligned cut pattern, for which all five cyclic
   pairs are complete.
6. The displayed cut is not maximum, witnessed by the switch `S` above.

Items 4 and 5 are independently replayable UNSAT claims.  The core CNFs use
variables `x[v,i]`, at-most-one class per vertex, the two patterns
`(0,0,1,0,1)` and `(1,1,0,1,0)`, five exact `>=2` cardinality constraints,
and one binary exclusion for every missing cyclic adjacency.  Rotation moves
the unique same-side cyclic block to `X_0-X_1`; reflection is a relabeling;
the two CNFs cover global cut complementation.  Hence the gate includes all
aligned cores with `K<=3` at `t=5`.

The construction is smallest in the available production-facing battery:
the `t=3` and `t=4` windows are already excluded by the accepted incidence
and catalogue modules, while every accepted `t=5` support hit has support
order 18 and pads to the required production order 25.

## Exact fixture battery

### Accepted t=5 circuits

Every distinct accepted 25/24 support hit was independently reconstructed,
padded to `N=25`, row-enumerated, C5-tested, switch-optimized, and core-
optimized.  In all six rows below, `q*=1` is optimal and the homomorphism CNF
is UNSAT.

| source fixture | complete rows | min sigma | beta | C5 hom | q* | K* |
|---|---:|---:|---:|:---:|---:|---:|
| `t5_classifier_v_l9_r9_1000` | 87 | -20 | 5 | no | 1 | 4 |
| `t5_live_x_classifier_v_l9_r9_5000` | 76 | -21 | 4 | no | 1 | 4 |
| `t5_rooted_l12_r6` | 72 | -23 | 2 | no | 1 | 4 |
| `t5_rooted_l9_r9` | 50 | -22 | 3 | no | 1 | 4 |
| `t5_rooted_l9_r9_mindef` | 49 | -22 | 3 | no | 1 | 4 |
| `t5_rooted_smoke_l10_r8` | 67 | -21 | 4 | no | 1 | 4 |

Here `beta=25+min sigma` is the actual edge-bipartization number of the
padded fixed graph.  Therefore none has `D_ext=0`; this is the same failure
as `max_cut`, expressed globally.

### Real rotor/cage fixtures

All real cage fixtures named by the accepted fixture regate were checked for
the M3 scalar window before applying the extraction conclusion.  None is an
M3-window object.

| fixture | N | bads | selected support | C5 hom | first scalar mismatch |
|---|---:|---:|---:|:---:|---|
| R41 saturated cage | 33 | 9 | 38 complete support | yes | `33 != 5*3` |
| R40 grafted cage | 78 | 27 | 82 complete support | no | bad count not square |
| P5-24 | 24 | 9 | 8 | yes | `24 != 5*3` |
| P5-167 | 167 | 28 | 27 | no | bad count not square |
| P5-175 | 175 | 29 | 31 | no | `29 != 35^2` |
| P5-311 | 311 | 92 | 45 | no | bad count not square |
| P5-3892 | 3892 | 1581 | 128 | no | bad count not square |
| P5-89 | 89 | 20 | 11 | yes | bad count not square |
| P5-2943 | 2943 | 1383 | 2797 | no | bad count not square |

For R41, the displayed cut was independently optimized with minimum switch
zero and `beta=9`; its graph maps to `C5`.  The R40 source script independently
replayed all four defect-zero states, all 27 distance-four bads, and the row
histogram, but its order/counts prevent it from testing the M3 extraction.

## Guardrails

### Deleted matching

For `C5[8]` with one perfect matching deleted from the bad cyclic block, the
exact core optimizer gives

```text
q*=4, K*=4,
```

while the graph still maps to `C5`.  Thus this family passes the homomorphism
branch but refutes any attempt to get `K<=3` from ordinary additive stability.
The general vertex-cover calculation is `K>=ceil(t/2)`.

### Glued block

The one-vertex sum of `C5[5]` and `C5` maps to `C5`; its largest aligned core
is the untouched `C5[5]` block (`q*=5`).  The small glued island is invisible
to connectedness and row visibility, so component deletion is not a valid
route to bounded `K`.

### Neutral transport

The exact two-state, one-label-fiber countermodel has two obligations and one
usable physical key in each state, disjoint obligations/keys between states,
rank one, and defect one.  Both transitions have

```text
(B,U,L,A_reopt)=(2,1,0,1),
B+L=U+A_reopt,
Delta(new)-Delta(old)=0.
```

It satisfies the complete `ledger_balanced` arithmetic around a nontrivial
cycle but carries no vertex partition at all.  Consequently
`ledger_checked`, `ledger_balanced`, and `support_balance` cannot by themselves
bound `K`.

## Field audit

No existing rotor/transport field supplies bounded `K`:

* `ledger` and `ledger_checked` compare obligation/source persistence for one
  row detour.  They contain no map from graph vertices to five classes.
* `ledger_balanced` is the coboundary identity
  `B+L=U+A_reopt`; the neutral `(2,1,0,1)` cycle satisfies it exactly.
* `support_balance` is a telescoping equality of selected-support cardinality
  changes.  It controls neither complete-row support geometry nor ambient
  vertices.
* `profile_degree` gives only the local equality `degree=window` at rotating
  owners.  The live-x fixture has the degree-five numerical profile and still
  has `q*=1`.
* `profile.owner_active` is stronger than the numerical profile, but still
  only roots an active component.  The live-x candidate fails this field
  intrinsically; ambient edges could repair scope, which is why the accepted
  production exclusion uses the max-cut/row-preservation extension gate.

The only M3 field with global cut content is

```lean
max_cut : IsMaxCut G c
```

and the exact live-x switch identifies it as the first load-bearing failure.
Therefore an honest future lemma must be stated as a maximum-cut/complete-row
rigidity theorem.  Calling its conclusion a consequence of the balanced
neutral ledger would be unsupported by the current interface.

## Replay

Build the independent CNFs:

```powershell
python tmp/fanout/wave4_rotor_c5_core/build_live_x_cnf.py
```

Canonical CNF/proof pairs:

```text
live_x_c5_hom.cnf          125 vars, 1010 clauses
live_x_c5_hom_text.drat    SHA256 082D405553C54B54170086529A451A31BA30428EA831233E87F76CAD0A58B5C9

live_x_core_q2_c0.cnf      125 vars, 2885 clauses
live_x_core_q2_c0_text.drat
  SHA256 0AEDBC42E3C8C239FDF02DBECC335764DF71F06466D04B9DFAA67F32ECEA73BB

live_x_core_q2_c1.cnf      125 vars, 2885 clauses
live_x_core_q2_c1_text.drat
  SHA256 AFB20552E7F96325F268C1CE8C06998274D688D6CDBF72AAD34FA3C3F76D7426
```

Replay each with the accepted independent checker:

```powershell
tmp/fanout/r51_independent_t5_verifier/drat-trim.exe `
  tmp/fanout/wave4_rotor_c5_core/live_x_c5_hom.cnf `
  tmp/fanout/wave4_rotor_c5_core/live_x_c5_hom_text.drat

tmp/fanout/r51_independent_t5_verifier/drat-trim.exe `
  tmp/fanout/wave4_rotor_c5_core/live_x_core_q2_c0.cnf `
  tmp/fanout/wave4_rotor_c5_core/live_x_core_q2_c0_text.drat

tmp/fanout/r51_independent_t5_verifier/drat-trim.exe `
  tmp/fanout/wave4_rotor_c5_core/live_x_core_q2_c1.cnf `
  tmp/fanout/wave4_rotor_c5_core/live_x_core_q2_c1_text.drat
```

All three commands return `s VERIFIED`.  `audit_extraction.py` contains the
independent row enumerator, maximum-switch CP-SAT model, C5 CNF encoder, core
optimizer, real-fixture adapters, and the deleted-matching/glued-block/neutral-
ledger constructors.  Because the dynamically loaded P5 fixture module uses
runtime dataclasses, invoke the full harness through `run_audit.py`.

## Conclusion

The wave does not yield the requested all-M3 proof or a full M3 counterexample.
It yields the sharpest exact boundary currently available:

> Complete rows, the 25/24 circuit, triangle-freeness, the live degree-five
> profile, and balanced neutral transport do not force either extraction
> outcome.  The accepted live-x projection has no C5 homomorphism and needs
> `K=4`.  Its first production failure is `IsMaxCut`, and the fixed circuit
> has no row-preserving maximum-cut completion.

Accordingly, no present rotor/transport field can honestly be named as the
source of `K<=3`; the missing ingredient is global maximum-cut versus
complete-row rigidity.
