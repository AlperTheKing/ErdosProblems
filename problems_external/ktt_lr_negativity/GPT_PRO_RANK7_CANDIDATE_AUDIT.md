# Audit of the GPT Pro rank-seven KTT candidate

Date: 2026-07-22

Status: **the displayed degree-13 polynomial is independently confirmed and
has strictly positive monomial coefficients.**  It is not a KTT
counterexample.  The report's aggregate claim of 14,814 completed
polynomials is not audited because no manifest or per-instance record file was
provided.

## Normalized LR convention

The external report writes the outer partition first.  In the convention
`c^outer_(inner_left,inner_right)`, the candidate is

```text
outer       = (8,7,5,4,3,2,1),
inner_left  = (5,4,3,2,1),
inner_right = (5,4,3,2,1).
```

It lies exactly on the FrontierMath bounds:

```text
|outer|=|inner_left|+|inner_right|=30,
maximum partition length=7.
```

## Independent current lrcalc-rs replay

The current public repository was cloned at commit

```text
17efa93108512abb4cbb8db721060e8819639f77.
```

Only two Windows portability changes were made in the temporary build:
the library crate type was restricted to `rlib`, and the otherwise missing
Windows `optind` symbol was defined.  The mathematical sources were unchanged:

```text
SHA256(lr_ehrhart.rs)=fb3a370fef2301b7970e933dc84a752df996f306aed69b4017aa8e0ff2d6ade2
SHA256(lrcoef.rs)    =60bddb9876a310544e960269b8aa0b9bc291dec73a0f165c31e3912cb31fb538
```

The exact `lr-stretch-hvector` command returned

```text
dimension: 13
h_vector: [1,146,7901,128152,765137,1903918,2084165,
           1000574,197101,13426,201,0,0,0]
sample_points:
[(0,1),(1,160),(-1,0),(2,10050),(-2,0),(3,254656),(-3,0),
 (4,3473010),(-4,201),(5,30852404),(-5,16240),
 (6,200925962),(-6,406170),(7,1035303314)]
```

For negative labels the command displays the positive interior count; degree
13 Ehrhart reciprocity supplies the negative sign in the interpolating
polynomial.  This h-vector reconstructs exactly every rational coefficient
printed in the external report.

Two positive dilations outside the 14-point interpolation set were then
counted directly by the same current Buch-style counter:

```text
P(8)=4,444,160,280,
P(9)=16,481,696,710.
```

Both equal the values predicted by the displayed polynomial.

Under the project's linear-coefficient cancellation ratio, this candidate has

```text
R_1=64842736/65468479 = 0.9904420721...
```

so it is not closer to the sign boundary than the previously validated
high-volume champion (`R_1=0.998087...`).  The phrase "most sensitive" is
therefore meaningful only relative to the external report's own search set.

## Independent hive-engine cross-check

The separately implemented exact hive counter returned

```text
P(1),...,P(5)
=160, 10050, 254656, 3473010, 30852404,
```

again matching the polynomial.  At `P(6)` this engine exceeded the deliberately
set two-billion-node cap, so no value was inferred from that run.  The older
vendored tableau program also returned `160` at stretch one with agreement
between its GT-DP and Kostka-inversion methods.  Its stretch-two inversion was
terminated after failing to finish promptly; it is not counted as a completed
second polynomial reconstruction.

## Arithmetic replay

Run

```text
python problems_external/ktt_lr_negativity/gpt_pro_rank7_candidate_arithmetic_audit.py
```

Expected output begins

```text
PASS
payload_sha256=9fd6ae6d2457e581781a22a4c6ed3ea66f48a5a25a652b4bb0fab28df5a39f44
```

The checker verifies the size/length bounds, the exact h-vector identity, all
signed interpolation samples, both held-out values, integrality, and strict
positivity of every monomial coefficient.

## Decision

The candidate polynomial is confirmed and is strictly coefficient-positive.
It adds a useful exact high-rank near-boundary test, but it proves no infinite
family.  Without the external run manifest, schedule, per-instance records,
and hashes, the reported aggregate counts remain unverified finite-search
metadata and are not merged into the project's certified census totals.

Primary live references checked during the audit:

- Warut Thawinrak, *A Short Proof for the Polynomiality of the Stretched
  Littlewood--Richardson Coefficients*, arXiv:2211.06810.
- Epoch AI, *Stretched Littlewood--Richardson Coefficients* (status displayed
  as `Unsolved` on 2026-07-22).
- Per Alexandersson, `lrcalc-rs`, commit
  `17efa93108512abb4cbb8db721060e8819639f77`.
