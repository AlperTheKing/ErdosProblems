# Rowwise Split Package Candidate

Status: exact gate alive. This is not a proof.

## Target

Fix a connected-B, Gamma-minimum maximum cut. Let `M` be the bad edges,
`m=|M|`, and

```text
eta = N^2/25 - m.
```

For a positive K-component `C`, define

```text
Tw_C(v) = sum_{g in M_C} p_g(v).
```

For `f in M_C` and `Q in cyc[f]`, set

```text
R_Q = sum_{v in Q} Tw_C(v).
```

The corrected ROWWISE-GERSH target is

```text
R_Q <= N + eta.
```

The candidate sufficient split package is:

```text
1. if |cyc[f]| > 1, then
       R_Q <= N + (2/3) eta.

2. if |cyc[f]| = 1 and |Q| = 5, then
       R_Q <= N.

3. if |cyc[f]| = 1 and |Q| > 5, then
       R_Q <= N + eta/2 - (|Q|^2 - 25)/50.
```

Each branch implies `R_Q <= N+eta`. The third branch is the Banked-UPO /
LONG-SURPLUS branch. The first branch contains the pentagonal multi-row
coefficient threat, tight at the N=10 atom `I?BD@g]Qo`. The second branch is a
small but useful old-ceiling statement for unique pentagonal rows.

## Exact Gate

Script:

```text
problems/23/writeup/_codex_rowwise_split_gate.py
```

Mixed battery:

```text
python problems/23/writeup/_codex_rowwise_split_gate.py \
  --max-n 10 --max-cuts 4 --two-lane-max 40 --k-lane-max 20
```

Result:

```text
cuts=15570
rows=67945
branch_fail=0
corrected_fail=0
branch_counts:
  unique-long-surplus: 203
  unique-p5-old: 2992
  multi-2eta3: 64750
```

Branch minima:

```text
multi-2eta3:
  margin=0 at graph6 I?BD@g]Qo,
  N=10, m=3, eta=1, row_sum=32/3.

unique-long-surplus:
  margin=0 at graph6 FCp`_,
  N=7, m=1, eta=24/25, row_sum=7.

unique-p5-old:
  min margin=1 at graph6 I?AAD@wF_,
  N=10, m=2, row_sum=9.
```

Census `N=11` slice:

```text
python problems/23/writeup/_codex_rowwise_split_gate.py \
  --skip-direct --skip-named --min-n 11 --max-n 11 --max-cuts 2
```

Result:

```text
cuts=108730
rows=665101
branch_fail=0
corrected_fail=0
branch_counts:
  unique-p5-old: 12524
  multi-2eta3: 652293
  unique-long-surplus: 284
```

Branch minima:

```text
multi-2eta3:
  margin=109/150 at graph6 J?BEF_m}@{?,
  N=11, m=4, eta=21/25, row_sum=65/6.

unique-long-surplus:
  margin=0 at graph6 J?AEB?oE?W?,
  N=11, m=1, eta=96/25, row_sum=11.

unique-p5-old:
  min margin=10/7 at graph6 J??E@ekNeY?,
  N=11, m=3, row_sum=67/7.
```

## Relation To Previous Notes

`MULTI_DEBT_STABILITY_CODEX.md` records branch 1 separately. This note packages
it with the unique-row branches into a single sufficient route to
ROWWISE-GERSH.

`ROWCAP_SPLIT_PROOF_TARGET_CODEX.md` records the older length-based split:
LONG-SURPLUS for all non-5 rows and PMS-5 for all length-5 rows. The present
package is a more refined observed split:

```text
multi rows       -> coefficient 2/3;
unique length 5  -> old ceiling N;
unique long      -> Banked-UPO/LONG-SURPLUS.
```

If exact tests find a positive-debt row outside this split's expected shape,
the split should be revised before proof effort.
