# R39 weak-free global compensation: exact boundary obstruction

## Verdict

The requested compensation theorem is not proved, and it cannot be derived
from the current canonical-trace/graph-adapter interface.  Exact boundary
accounting identifies the missing datum: interactions between weak switches
are signed edge terms, while P1/P3/strict-P4/P5/bank realization is not linked
to those terms by any production theorem.

There is no exact real **positive-defect canonical** counterexample in the
checked artifacts.  The sharp real 20-vertex witness has the required weak
attachment and no alternate source/detour, but its collision demand is zero.
Thus it refutes compensation without the positive-defect hypothesis, not the
frozen positive-defect statement.  The positive-defect saturated square rotor
in `WALL_ATTACK_R38_GPTPRO56.md` is only an abstract obstruction; its real
realizability remains open.

Two concurrent R39 audits close two proposed subroutes exactly:

* `r39_weak_free_switch` gives a 40-vertex lex-canonical real cage with two
  weak pairs and proves every nonempty subfamily has aggregate surplus exactly
  one per pair, never the two per terminal required by common-blue.
* `r39_weak_free_bank` compiles a minimal Lean interface model with the two
  raw free halves present and every Door/vertexSlack/prune/c5Base bank column
  zero.  Hence bank payment is not available from a weak pair in the current
  production types.

Neither artifact has positive real collision defect, so neither is promoted
to a counterexample to the full requested theorem.

## Exact boundary identity

Give each cut edge weight `+1` and each bad edge weight `-1`, and write

```text
sigma(S) = sum_e w(e) 1[e crosses S].
```

For arbitrary vertex sets `A,B`, edgewise XOR gives

```text
sigma(A) + sigma(B)
  = sigma(A xor B)
    + 2 W(A\B, B\A)
    + 2 W(A inter B, V\(A union B)),                 (1)
```

where `W(X,Y)` is the signed sum of edges between `X` and `Y`.  For disjoint
switches this specializes to

```text
sigma(A union B) = sigma(A) + sigma(B) - 2 W(A,B).   (2)
```

The checker verifies (1) on all 16 endpoint-membership patterns and both edge
signs.  These are all possible per-edge contributions, so summing proves the
identity for every graph.

For an attachment pair `{x,y}` with a common blue owner, triangle-freeness
forces `xy` to be a nonedge.  Therefore

```text
sigma({x,y}) = sigma({x}) + sigma({y}).               (3)
```

Maximum-cut optimality gives only nonnegativity of the three quantities.  If
the pair has sigma 0 or 1, the endpoint losses are respectively `(0,0)` or
`(0,1)` up to order.  There is no hidden extra unit.  For two weak pairs,
(2) shows that a blue interaction subtracts two units and a bad interaction
adds two units.  Max-cut only requires the combined result to remain
nonnegative; it does not force result at least two, an unused source half, or
a legal terminal reservation.

## Production-interface boundary

`CollisionDefectGraphAdapter.NoCommonBlueSourceRelations` stores `p1`, `p3`,
`strictP4`, and `p5` as caller-supplied propositions.  The adapter proves no
implication from `sigma`, (1), or maximum-cut validity to any of those fields.
It also contains no bank-capacity predicate and no canonical trace/SCC type.
Consequently a theorem saying a weak attachment is paid by one of those
sources is false at that interface: all four relations may legally be
`False`, independently of the signed boundary data.

The common-blue API does not repair this gap.  Its checked terminal requires
`sigma >= 2`; `sigma >= 0` is exactly two units weaker.  Combining weak
attachments cannot supply those units without an additional hypothesis
controlling the signed interaction terms in (1) and the reservation ledger.

## Real fixture separation

The 20-vertex R36 carrier replays exactly as follows at its displayed state:

```text
collision demand = 0, defect = 0
attachment probes = 9 with sigma>=2, 1 with sigma=1
P1/P3/strict-P4/P5 source keys = 0
detours = 0
```

The sole weak probe is `(owner,x,y)=(7,0,5)`, with `dB=3`, `dM=2`,
`sigma=1`.  It is not globally paid, but there is no unmatched obligation to
pay.  This proves the positive-defect hypothesis is load-bearing.

The real 24-vertex positive state separates the other direction:

```text
collision demand = 240, matched = 172, defect = 68
attachment probes = 153 with sigma>=2, 0 weak
first checked one-row trade lowers defect 68 -> 51
```

Hence the available real examples do not combine into a counterexample to
the requested positive-defect theorem.

## Exact aggregate-switch counterexample

The concurrent `r39_weak_free_switch` cage joins two R36 copies by one blue
bridge whose endpoints avoid the weak pairs.  Exact replay gives

```text
N=40, edges=49, triangle-free, maximum cut=41
row family sizes=(2,1,1,1,2,1,1,1), lex-first tuple rank=0
weak pairs=(0,5),(20,25), individual sigma=(1,1)
cross interaction=0, union sigma=2, required terminal budget=4
```

The eight edge-disjoint displayed 5-cycles certify the maximum-cut upper
bound `49-8=41`.  For every nonempty subfamily `J` of the two weak pairs,

```text
sigma(union J) = |J| < 2|J|.
```

Tree-joining `k` copies gives the same equality for every `k>=1`.  Therefore
no uncrossing, simultaneous switch, or pairing argument based only on global
signed surplus can provide the common-blue terminal budget.

Replay:

```powershell
python tmp/fanout/r39_weak_free_switch/check_cage.py
```

The separate Lean audit at
`tmp/fanout/r39_weak_free_bank/InterfaceCountermodel.lean` proves the type
boundary: two raw free halves do not construct any production bank term.

## Consequence

The only non-circular exact strengthening currently visible is precisely the
R38 exposure hypothesis: every positive-defect sink class has positive
`neutralExposure`, where exposure explicitly counts unused compatible probe
sources and unused detour-created sources in target matchings.  Assuming that
quantity is positive yields augmentation; proving it from real maximum-cut
geometry is the frozen `noPositiveDefectSaturatedNeutralSquareRotor` wall.

Replacing that wall by a statement that weak attachments are "paid" does not
shorten the proof unless the statement includes an independently proved map
from each signed interaction term in (1) to a concrete unused P1/P3/P4/P5 or
bank key, with base-component coherence and reservation deductions included.

## Replay

```powershell
python tmp/fanout/r39_weak_free_comp/verify_boundary.py
```

Expected output:

```text
BOUNDARY_IDENTITY=PASS patterns=32
CAGE20={'defect': 0, 'demand': 0, 'weak': 1, 'sigma1': 1, 'otherSources': 0, 'detours': 0}
CAGE24={'defect': 68, 'demand': 240, 'matched': 172, 'weak': 0, 'sigmaGe2': 153, 'trade': [68, 51]}
```
