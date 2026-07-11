# R29 global-minimum scoped-Hall falsifier

## Verdict

The reconstructed 2,943-vertex R29 cage falsifies both of the following
auxiliary claims for the current active-scoped obligation score:

1. every Hall-failing row tuple has a lower-scoring row tuple;
2. the full-product heat-bath inequality
   `sum_eta S(eta) <= |Omega| * (S(omega) - defect(A))`.

This is a falsifier to the selector/matching route, not to Erdos Problem #23.

## Exact witness

The deterministic reconstruction has:

- `N = 2943`;
- `|B| = MaxCut = 7039`;
- `|M| = 1383`;
- `Gamma = 34575`;
- 707 rigid row families of size 1 and 676 selector families of size 680.

Choose the anchor row in every selector family.  The resulting tuple has:

- global active-scoped score `23115 = 23108 + 7`;
- owner shore `A = {0,1,2}`;
- shore demand `19953`;
- source-neighborhood cardinality `19925`;
- exact Hall defect `28`.

The global lower-bound reduction uses the two counts `L_L,L_R` of local
selector rows.  Each side has 338 selector families.  At most 27 local
families can touch one D-leaf, so at least `ceil(L_s/27)` D-leaves remain
active, each carrying fixed collision score 200.  Together with the permanent
hub/circuit contribution and the anchor collision at vertex 55, every tuple
has score at least

```text
20411
+ 2 * ((338-L_L)+(338-L_R)
       + max(0,337-L_L)+max(0,337-L_R))
+ 200 * (ceil(L_L/27)+ceil(L_R/27))
+ 4 * [L_L=L_R=0].
```

All `339^2 = 114921` count cells were checked with integer arithmetic.  The
unique minimizing cell is `(0,0)`, with value `23115); the next cell lower
bound is `23203`.  The all-anchor tuple attains the bound.

The owner-Hall reconstruction independently replaces all 676 selector rows
by those same anchor rows, then rebuilds pair counts, selected support, active
components, collision demand, HitNeed demand, and source eligibility.  It
checks all eight shores and emits 19,925 distinct source triples.  The full
three-owner shore has defect 28.

## Replay

```powershell
python tmp\fanout\r29_gate\lead\r29_lead_gate.py
python tmp\fanout\r29_gate\d09\retry2\verify.py
python tmp\fanout\r29_gate\d05\retry2\rebuild_owner_hall.py
python tmp\fanout\r29_gate\d05\retry2\verify_cut_certificate.py
python tmp\fanout\global_min_proof\lead\verify_r29_global_min_hall_falsifier.py
```

The local replay returned:

```text
global score = 23115
Hall demand = 19953
Hall neighborhood = 19925
Hall defect = 28
```

## Artifact identities

- canonical reconstructed payload:
  `fc4f3ab94bed810669976b1fdb21743fdd4ebe57eea15ef52afcfc2165e2fb1f`;
- all-anchor tuple:
  `93d5d64c55338186603b718b5d6bb162d907c4fc868ce276808e01822c395901`;
- current global-minimum certificate:
  `12640695a44ee155302942b82cde78cdf8597152adce2ffbfb335c2ee5b76359`;
- Hall certificate:
  `dd1f1a2cff0886e6eaf8ed6487d7a5f308e51446b2ffbc284d6caac3f797e1ce`.

The historical R29 artifact advertised only by prefix `00186166...` is not
present.  The falsifier therefore applies to the deterministic reconstruction
above, which matches all advertised structural invariants.

## Consequence

`HallFailureHasScopedScoreGlobalDescent` remains a valid abstract Lean
interface, but its real-graph provider is false for this score.  The live wall
must use either a different deterministic selector or the full-bank capacity
that is absent from the active-scoped FreeHalf matching.
