# CDC wave 1: corrected grouped-cap row exchange

## Verdict

The requested universal graph-side theorem is **not proved or falsified** in
this lane.  The corrected coherence-free model survives every exact gate run
here.  The strongest new result is an exact finite exchange theorem on the
complete canonical `N<=11` battery plus the named N12 fixture, together with a
general finite-descent lemma showing exactly why that exchange would prove the
selector theorem.

The key correction is essential: P4 outside attachment is coherence-free.  It
does not require the owner and attachment vertex to have the same active
component.  With this corrected P4, the apparent N89 counterexample vanishes:
the exact flow is `776/776`.  The old strict-P4 fork remains a useful negative
guardrail (`774/776`) but is not the model of record.

## Exact model

For a row choice `w`, let

```text
C(w) = global collisionUnits
D(w) = 2*C(w) - maximum corrected grouped flow
```

The flow has:

- all global `CollisionHalf` identities as demand;
- only actual off-diagonal `FreeHalf(x,y,h)` sinks;
- unit capacity per literal half key;
- aggregate capacity two over the four keys of each active undirected edge;
- the union P1 same-first, P2 common-bad, P3 row-companion, corrected
  coherence-free P4 outside attachment, component-scoped P5 quiescent
  attachment, and common-blue;
- integer Dinic max flow only.  There is no float acceptance path.

For an exact minimum-cut owner shore `U`, write `d_w(U)` for its demand and
`k_w(U)` for its grouped neighbor capacity.  An exchange `w -> e` is counted
as corrected only when

```text
Hamming(w,e) <= 2
C(e) <= C(w)
D(e) < D(w)
[d_w(U)-k_w(U)] > [d_e(U)-k_e(U)]
```

The gate checks the exact decomposition

```text
oldGap - newGap
  = (oldDemand - newDemand) + (newCapacity - oldCapacity)
  = deletedDemand + gainedCapacity.
```

Thus demand deletion may pay for a capacity loss.  Requiring capacity gain
alone, or requiring both terms to be nonnegative, is too strong.

## Strongest true lemma

**Finite corrected-exchange descent.**  Let `Omega` be a nonempty finite set
and `C,D : Omega -> Nat`.  Suppose every `w` with `D(w)>0` has an `e` with
`C(e)<=C(w)` and `D(e)<D(w)` (the Hamming bound may be added but is not needed
for this implication).  Then some global minimizer of `C` has `D=0`.

**Proof.**  Choose `w` minimizing `D` among the global minimizers of `C`.  If
`D(w)>0`, the exchange gives `C(e)<=C(w)`, hence `C(e)=C(w)` by global
minimality, while `D(e)<D(w)`, contradicting the choice of `w`.  Therefore
`D(w)=0`.

This is the precise finite-minimum argument needed by the proposed universal
one/two-row exchange theorem.  It proves no graph-side exchange by itself.

## Exhaustive battery

`exchange_gate.py` exhausts every row tuple for the canonical Gamma-minimum
connected maximum-cut configuration returned by the production census loader,
restricted to all-ell-5 databases.

| Scope | systems | row tuples | flow failures | corrected R1 | corrected R<=2 | collision minima | failing minima |
|---|---:|---:|---:|---:|---:|---:|---:|
| N=5..10 | 6,421 | 50,104 | 4,070 | 3,950 | 4,070 | 24,601 | 56 |
| N=11 | 64,287 | 1,035,476 | 1,333 | 1,333 | 1,333 | 309,464 | 0 |
| N12 `K??E@cyjFgWk` | 1 | 2,400 | 0 | 0 | 0 | 27 | 0 |
| **total** | **70,709** | **1,087,980** | **5,403** | **5,283** | **5,403** | **334,092** | **56** |

Every tested graph has at least one feasible global collision minimizer.  All
5,403 failing tuples have a corrected exchange at Hamming distance at most
two; 120 require two rows.

Only 2,176 of the 5,403 failures have an at-most-two-row capacity-only repair.
Only 4,523 have a repair where deleted demand and gained capacity are both
nonnegative.  The full corrected inequality, allowing demand deletion to
outweigh capacity loss, is the strongest tested form with zero exceptions.

The shared corrected global gate independently exhausts graph-level existence
through full order 12.  At N12 it covers 921,910 eligible systems and
39,142,819 available row tuples, examining 921,911 tuples before exact zeros;
failed graph minima: 0.  Artifact:
`tmp/fanout/r53_global_softcap_gate/census_n12.json`, canonical payload SHA-256
`05c39e0ca3716cd86e66ddd165d97162b71aa86df413c358eed437365f9ddd32`.

## Sharp guardrails

### Not every collision minimizer works

For `I?rFf_{N?` (the N10 balanced equality configuration), `Cmin=18` and
there are 96 collision-minimizing choices: 40 pass and 56 fail.  Hence the
claim must be existential among collision minimizers.

The failing minimizer `[0,3,7,4]` has `D=4`.  The two-row exchange
`[0,3,7,4] -> [0,3,5,6]` preserves `C=18` and changes `D: 4 -> 0`; on the old
full owner shore demand stays 36 while capacity changes `32 -> 36`.

### One row is not enough

On the same graph, `[0,1,6,7]` has `C=26`, `D=4`, and no one-row corrected
descent.  The two-row exchange `[0,1,6,7] -> [0,3,6,5]` has `C: 26 -> 18` and
`D: 4 -> 0`.  On the old full shore:

```text
demand       52 -> 36   deletedDemand = 16
capacity     48 -> 36   gainedCapacity = -12
gap           4 ->  0   improvement = 16 + (-12) = 4
```

This is an exact witness that demand deletion and capacity loss must be
allowed simultaneously.

`n10_rectangle_gate.py` classifies all 4,096 tuples of this graph.  Exactly
120 flow failures have no one-row corrected descent.  All 120 admit a
two-row repair preserving, at each of the five row positions, the unordered
pair of vertices across the changed rows.  Thus the whole finite two-row-only
class is the column-preserved rectangle pattern already suggested by the
production exchange interface.

### Capacity-only exchange is false

For N8 graph ``G?bF`w``, tuple `[0,0]` has `C=16`, `D=2`, and no capacity-only
repair within two rows.  Its one-row corrected repair `[0,0] -> [0,3]` has
`C:16 -> 4`, `D:2 -> 0`, deleted demand 20, gained capacity 12, and shore
improvement 32.  Deleting obligations is part of the certificate, not an
optional presentation choice.

## R35 N24 Hamming-two gate

`r35_exchange_gate.py` exhausts all 19,630 states at Hamming distance at most
two from each of two real-cage centers (row radices `10^9 * 45^3`).

For the original displayed state, `C=156` and `D=24`:

```text
corrected descents:        13,212  (81 one-row, 13,131 two-row)
zero-defect descents:       6,084  (all two-row)
best: C 156 -> 128, D 24 -> 0
old shore: demand 144 -> 116, capacity 120 -> 160
```

The best state is `[0,0,0,0,0,0,0,3,5,15,31,44]`.

For the previously reported one-row defect minimum
`[0,0,0,0,0,0,0,0,0,0,31,44]`, `C=165` and `D=6`:

```text
corrected descents:        13,021  (81 one-row, 12,940 two-row)
zero-defect descents:      11,246  (54 one-row, 11,192 two-row)
best: C 165 -> 136, D 6 -> 0
old shore: demand 72 -> 52, capacity 66 -> 58
```

The second best exchange again needs the corrected sign convention: it
deletes 20 demand units while losing 8 capacity units.  The R35 cage therefore
does not falsify the one/two-row theorem.

## N89 scope audit

`n89_referee.py` reconstructs the 89-vertex graph, checks triangle-freeness,
blue connectivity, all 20 singleton shortest-row families, the exact maximum
cut 125 by 4,096 quotient assignments, and all 4,095 demand-owner shores.

```text
strict component-scoped P4: demand 776, flow 774, defect 2
corrected unscoped P4:       demand 776, flow 776, defect 0
```

For strict P4 the unique deficient shore `{0,1,2}` has demand 528 and capacity
526.  Corrected P4 raises that shore capacity to 12,230.  Therefore N89 is an
exact counterexample only to the obsolete strict-P4 fork, not to the corrected
coherence-free selector.

## Status and limitation

The finite data strongly isolates a plausible universal theorem:

```text
D(w)>0 -> exists e,
  Hamming(w,e)<=2 and C(e)<=C(w) and D(e)<D(w),
```

with the shore improvement proved by the deleted-demand plus gained-capacity
identity.  No universal graph-theoretic proof of that implication is supplied
here, and no corrected-model counterexample was found.  Consequently this
lane does not close Erdos #23.

## Replay

From the repository root:

```powershell
python -B tmp/fanout/cdc_wave1/exchange/exchange_gate.py --n-min 5 --n-max 10 --workers 16 --p4-scope unscoped
python -B tmp/fanout/cdc_wave1/exchange/exchange_gate.py --n-min 11 --n-max 11 --workers 32 --p4-scope unscoped
python -B tmp/fanout/cdc_wave1/exchange/exchange_gate.py --n12 --workers 1 --p4-scope unscoped
python -B tmp/fanout/cdc_wave1/exchange/n89_referee.py
python -B tmp/fanout/cdc_wave1/exchange/n10_rectangle_gate.py
python -B tmp/fanout/cdc_wave1/exchange/r35_exchange_gate.py --center displayed --workers 16
python -B tmp/fanout/cdc_wave1/exchange/r35_exchange_gate.py --center one-row-minimum --workers 16
```

Owned script SHA-256:

```text
exchange_gate.py  0CC9DC3567D3A9B21FCD6DE1D9CE31415774022BADCB513F58652A2B34F3B86D
n89_referee.py    33E9D03756D189D815285682AF21AA84B58916D3ACA0AC916CD119F702BA74FD
r35_exchange_gate.py ECEC15738556B2096C0A884FEAF738692345116ED08F1D3718A91DD42DABC162
n10_rectangle_gate.py E1DBC21A54C82EB6509A7C404304C40C7329827316BC9DAC5CFEDECF0B90C52F
```

Pinned dependency hashes used for the final replay:

```text
global_softcap.py                         32C7F9BC0C4D2921D3B1FA5D8557ADA0088EEE8A024FDB90330023060101AC13
_codex_r19_global_base_census.py          B49E9A2ADD265052605AC412449B9FB12B1B879CC67E254B68189DB7B831A737
_codex_r20_two_row_exchange_gate.py       73697B12B1E22A30E320FB970415E79FA90D88D1A6DB27F42022CF9FFD9C6D83
tmp/fanout/p5_fixtures/gate.py            E50054EC3EC6E9AD91191B20F65CAE3D52DC7B888DD6A77E4FAD5C1FE78D466F
```
