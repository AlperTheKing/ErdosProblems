# C5-HOM Sharp Branch Reduction Notes

Status: live proof-frontier notes, not a proof.

## Context

Claude's C5-RS split shows all tightness in census `N<=11` lies in C5-HOM K-components. The exact tight branch is weighted pentagonal/C5-HOM stability; the non-C5-HOM branch is separate and still needs a genuine bound or superstructure reduction.

The census overloaded rows occur in two `N=10` seeds:

```text
I?BD@g]Qo    equality seed, covered by seven-cut algebra.
I?`FAo]]?    sibling seed.
```

The sibling seed contains the equality seed as a spanning subgraph plus one extra blue edge for 14 of its 16 overloaded rows. The remaining 2 rows are residual-low rows with `I=152/15`.

## Dead Subtarget: Simple Blue-Edge Monotonicity

Proposed but now exact-falsified:

```text
If a sibling overloaded row is an equality-row supergraph with one extra blue edge, then the weighted row-overlap I_sib is always <= I_eq under the pulled-back weights.
```

New gate:

```text
python problems/23/writeup/_codex_ocpms_sibling_weighted_monotonicity.py \
  --mode exhaustive --max-weight 3 --require-qmax --require-over-sib
```

Counterexample:

```text
weights_sib = [3,1,3,3,1,3,3,3,3,3]
eq_side = 0101111000, eq_P = (7,5,8,6,9)
sib_side = 1111000010, sib_P = (4,8,6,1,9)
extra blue edge = (3,7)
I_eq  = 232/9
I_sib = 1651/63
gap   = I_eq - I_sib = -3/7
```

The counterexample is a valid weighted quotient case under the gate filters:

```text
both quotient cuts are maximum,
sibling row is overloaded: I_sib - N = 13/63 > 0.
```

But it is very far from the desired PMS/C5-LIFT boundary:

```text
N = 26,
m = 15,
eta = 301/25,
I_sib - N = 13/63,
C5-LIFT margin = (2/3)eta - (I_sib-N) = 12317/1575.
```

So the simple monotonicity lemma is too strong and false, but the failing region is low-ratio / high-slack. The sibling proof should not try to dominate every sibling row by an equality row. It should instead prove a separate sibling stability inequality, or use monotonicity only after adding a near-tightness hypothesis.


## Direct Weighted C5-LIFT Quotient Gate

After simple monotonicity failed, I added a direct quotient gate that computes the actual row loads `s_i` and C5-LIFT margin for every length-5 quotient row under weighted blow-ups.

Gate file:

```text
problems/23/writeup/_codex_c5lift_weighted_quotient_gate.py
```

Commands and results:

```text
python problems/23/writeup/_codex_c5lift_weighted_quotient_gate.py --graph sib --mode exhaustive --max-weight 2 --require-qmax --only-length5
# checked_rows=43286, min_lift=1/3, first_fail=None

python problems/23/writeup/_codex_c5lift_weighted_quotient_gate.py --graph eq --mode exhaustive --max-weight 2 --require-qmax --only-length5
# checked_rows=45710, min_lift=0 at equality atom, first_fail=None

python problems/23/writeup/_codex_c5lift_weighted_quotient_gate.py --graph sib --mode random --samples 5000 --max-weight 30 --require-qmax --only-length5
# checked_rows=69271, min_lift=534006463/7368348, first_fail=None

python problems/23/writeup/_codex_c5lift_weighted_quotient_gate.py --graph eq --mode random --samples 5000 --max-weight 30 --require-qmax --only-length5
# checked_rows=59664, min_lift=5646213811/71550600, first_fail=None
```

Interpretation:

```text
simple monotonicity: false,
direct sibling weighted C5-LIFT stability: exact-supported so far,
equality seed: tight only at the expected equality atom in the tested range.
```

The next proof target for the sibling branch should be direct weighted stability, not domination by the equality atom.

## Surviving Sharp-Branch Split

1. Equality seed: seven-cut algebra remains the tight equality-atom route.
2. Sibling strict-supergraph rows: simple monotonicity is false; need either
   - a near-tight monotonicity statement, or
   - a direct weighted sibling stability certificate.
3. Sibling residual-low rows: already have explicit denominator pattern `(5,5,3)` and unweighted margin; need weighted version or a structural coarse bound.
4. Non-C5-HOM rows: separate branch; current small census shows no exact tightness, but Claude scale stress shows the margin can shrink, so constant-slack closure is not available.

## Current Gate Files

```text
_codex_ocpms_sibling_embedding.py        # 14/16 strict supergraph rows
_codex_ocpms_sibling_delta.py            # unweighted contribution deltas
_codex_ocpms_residual_low_dump.py        # two residual-low rows
_codex_ocpms_sibling_weighted_monotonicity.py  # weighted monotonicity gate; false globally
```




## 2026-07-01 direct weighted quotient stress update

Script:
`problems/23/writeup/_codex_c5lift_weighted_quotient_gate.py`

Candidate checked:
`row_sum(Q) + inactive_deficit(Q) <= N + (2/3) eta`, where `tau=5m/N`, `eta=N^2/25-m`, and `inactive_deficit=sum_{i:s_i<=tau}(tau-s_i)`.

Random stress, qmax cuts only, length-5 rows only, 20,000 random weight vectors with weights in `[1,100]`:

Equality seed `I?BD@g]Qo`:
- command: `python problems\23\writeup\_codex_c5lift_weighted_quotient_gate.py --graph eq --mode random --samples 20000 --max-weight 100 --require-qmax --only-length5`
- checked rows: 225070
- first_fail: None
- min_lift: `16472865450719201/35314116871905`
- verdict: PASS

Sibling seed `I?`FAo]]?`:
- command: `python problems\23\writeup\_codex_c5lift_weighted_quotient_gate.py --graph sib --mode random --samples 20000 --max-weight 100 --require-qmax --only-length5`
- checked rows: 265027
- first_fail: None
- min_lift: `6654143672464094509/11657460740256975`
- verdict: PASS

This does not prove C5-LIFT-PMS, but it supports the direct weighted stability target after simple equality-to-sibling monotonicity was exact-falsified.

## 2026-07-01 exhaustive max-weight-3 direct quotient stress

Same script and candidate as above, qmax cuts only and length-5 rows only.

Equality seed `I?BD@g]Qo`:
- command: `python problems\23\writeup\_codex_c5lift_weighted_quotient_gate.py --graph eq --mode exhaustive --max-weight 3 --require-qmax --only-length5`
- checked weights: 59049
- checked rows: 1604900
- first_fail: None
- min_lift: `0`
- tight case: all weights 1, side `0001111000`, row `(7,5,8,6,9)`, `N=10`, `m=3`, `eta=1`, `tau=3/2`, `s=[2,34/15,32/15,34/15,2]`, row_sum `32/3`, inactive_deficit `0`.
- verdict: PASS

Sibling seed `I?`FAo]]?`:
- command: `python problems\23\writeup\_codex_c5lift_weighted_quotient_gate.py --graph sib --mode exhaustive --max-weight 3 --require-qmax --only-length5`
- checked weights: 59049
- checked rows: 1635313
- first_fail: None
- min_lift: `1/3`
- min case: all weights 1, side `0001111000`, row `(1,6,8,4,9)`, `N=10`, `m=3`, `eta=1`, `tau=3/2`, `s=[2,11/5,34/15,28/15,2]`, row_sum `31/3`, inactive_deficit `0`.
- verdict: PASS
