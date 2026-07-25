# Zero-Trust Audit of the Dilation-Compatible Skew-Kostka-to-LR Bridge

Date: 2026-07-22  
Verdict: **CONFIRMS**, subject to the mandatory interpolation rule below.  
Scope: this confirms the algebraic bridge and the tested counting/interpolation
contract. It is not the 50,000-instance gate, and it is not a proof of full KTT.

## 1. Audited objects

- Bridge statement:
  `KOSTKA_TO_LR_HOMOGENEOUS_BRIDGE.md`
- Independent audit program:
  `kostka_lr_bridge_zero_trust_audit.py`
- LR engine: `engine/lr_hive.exe`, the C++ Knutson--Tao hive counter
- Candidate Kostka engine: `vendor/kostka`, pinned at
  `cd199a4f2aeee261cf2c6e703bb432a5916717fe`

The Python auditor imports no code from `vendor/kostka` and no existing tableau
counter. Its skew-Kostka implementation is a fresh Young-lattice dynamic
program over chains of horizontal strips. The LR comparison uses the separately
implemented hive model.

## 2. Algebraic audit

Let `W=sum(w)`, let `s=ell(beta)`, and let
`T_j=w_j+...+w_k`. The proposed partitions are

```text
R=(W+beta_1,...,W+beta_s,T_1,...,T_k),
S=(W,...,W,T_2,...,T_k,0),
```

with trailing zeroes omitted.

The construction is correct for the following exact reasons.

1. `R` and `S` are weakly decreasing and `S` is contained in `R`:
   `W+beta_s>W=T_1`, while `T_j>=T_(j+1)`.
2. The size identity is

   ```text
   |R|-|S|=|beta|+T_1=|beta|+W=|lambda|.
   ```

   Hence `(lambda,S;R)` has the required LR size equality.
3. In the first `s` rows, `R/S` consists of the translate of `beta` in
   columns `W+1,...,W+beta_i`. In row `s+j`, it consists of the interval
   `T_(j+1)+1,...,T_j`, of length `w_j`.
4. These components have pairwise disjoint row sets and column sets. Tableau
   inequalities therefore do not couple them, giving

   ```text
   s_(R/S)=s_beta h_(w_1)...h_(w_k).
   ```

5. The Hall adjunction and iterated Pieri rule give

   ```text
   c^R_(lambda,S)
     = <s_lambda,s_(R/S)>
     = <s_(lambda/beta),h_(w_1)...h_(w_k)>
     = K_(lambda/beta,w).
   ```

   This remains valid for a composition `w`: the ordered horizontal-strip
   chain counts tableaux with labels `1,...,k`, and symmetry also shows that
   permuting the positive parts leaves the count unchanged.
6. For every positive integer `n`, `W` and every `T_j` scale by `n`, so the
   constructed pair is exactly `(nR,nS)`. At `n=0`, deletion of zero parts
   makes both constructions the empty pair and both sides equal one. Thus

   ```text
   K_(n lambda/n beta,n w)=c^(nR)_(n lambda,nS)
   ```

   holds for every `n>=0`.

The audit program checks the partition, containment, size, exact cell-set
decomposition, pairwise row/column disjointness, and `n=0,1,2,3` homogeneity
assertions on every test instance.

## 3. Independent numerical replay

The deterministic core corpus contains 128 nonempty genuinely skew instances:

- `3<=|lambda|<=8`, `ell(lambda)<=4`;
- `beta` is nonempty and properly contained in `lambda`;
- positive compositions `w` with `ell(beta)+ell(w)<=6`;
- 96 instances have base count greater than one and 32 have base count one;
- candidates are selected by a specified SHA-256 ordering in the audit code;
- 77 of the 128 selected weights are not partitions, so ordered compositions
  are tested rather than silently restricting to decreasing weights.

For each instance and each `n=1,2,3`, the audit compared:

1. the fresh Python horizontal-strip DP for
   `K_(n lambda/n beta,n w)`;
2. the C++ hive count for `c^(nR)_(n lambda,nS)`; and
3. the pinned Rust skew-Kostka counter.

Result:

```text
core base instances:             128
core dilation comparisons:       384
Python tableau = C++ hive:        384/384
Python tableau = Rust vendor:     384/384
core maximum bridge rank:         6
core maximum count:               396
core record SHA-256:
4341a3e659e22cce18796be8a79a8c2eb5e02be029feb9c42dd415f19181b6bf
```

The stale README example was then added as a 129th instance and replayed at
`n=1,2,3`, also with no mismatch. The final totals are:

```text
total base instances:            129
total dilation comparisons:      387
all three counters agree:         387/387
total maximum count:              3418
total record SHA-256:
1ed4128d9b10d74b0777f4b374e4d49dd3e9e20faf11f44af7c63a12c58e8219
```

## 4. Pinned repository and test-suite audit

The checkout was clean and resolved to:

```text
commit: cd199a4f2aeee261cf2c6e703bb432a5916717fe
tree:   3bdf89c0c9ca0452a5c0ed96dda9671aedc35df3
```

Commands:

```text
git rev-parse HEAD
git rev-parse 'HEAD^{tree}'
git status --short
cargo build --release --locked
cargo test --release --locked
```

Results:

```text
cargo build: PASS
library tests: 29 passed, 0 failed
binary tests:  0 failed
doc tests:     0 failed
```

Tool versions were Python 3.12.4, cargo 1.94.0, and rustc 1.94.0.

## 5. Degree, `P(0)`, and held-out audit

The vendor-reported degree was not assumed. For a skew shape with
`L=ell(lambda)` and `k=ell(w)`, the chain model has `(k-1)L` interior
coordinates. Each of its `k-1` interior levels has an independent prescribed
sum, so the rigorous ambient bound is

```text
deg P <= U := (k-1)(L-1).
```

For each of 64 deterministic test instances, including the stale README case,
the independent auditor did the following:

1. computed exact tableau counts at `n=0,...,U+2`;
2. independently interpolated from `n=0,...,U` in the ordinary monomial basis;
3. checked the two held-out values at `n=U+1,U+2`;
4. compared the exact polynomial with both the vendor's adaptive-reciprocity
   mode and its positive-only mode;
5. compared the inferred degree with the vendor `degree` command; and
6. checked that the constant coefficient is exactly one.

Result:

```text
instances:                        64
degree mismatches:                0
polynomial mismatches:            0
P(0) failures:                    0
held-out checks:                  128
held-out failures:                0
Ehrhart record SHA-256:
839d611fa8a573221e0352301f08b3f37f601c6494bbb6d8a05b921242fd4f58
```

This finite audit does not turn the vendor dimension routine into a theorem.
Therefore the bounded gate must use `U`, not the vendor `degree` output, to
choose the interpolation range. The vendor degree may be retained only as a
diagnostic unless its general correctness is proved separately. This rule
prevents an underestimated degree from hiding a coefficient or producing a
false negative screen.

## 6. Reconciliation of the stale README example

The README at the pinned commit claims, for

```text
lambda=(4,3,2,1), beta=(2,1), w=(2,2,2,1),
```

the cubic

```text
(8200 n^3 - 41616 n^2 + 70016 n - 36396)/6.
```

That displayed polynomial is impossible: it has `P(0)=-6066`. It gives
`P(5)=49714`, also the stale value printed in the README.

The current executable built from the same pinned checkout instead returns

```text
degree 8
P(n) = (1/45)n^8 + (85/336)n^7 + (19/15)n^6 + (89/24)n^5
     + (211/30)n^4 + (431/48)n^3 + (691/90)n^2 + (341/84)n + 1,
P(1..11) = 34, 462, 3418, 17102, 65556, 207432, 568164,
           1390851, 3112054, 6469606, 12650430.
```

The fresh tableau DP independently gives those values; the positive-only and
adaptive vendor modes give the same polynomial; and the bridge hive gives
`34,462,3418` at `n=1,2,3`. The values at `n=10,11` are independent held-outs
for the bound `U=9`.

Conclusion: this is a stale README bug, not a mismatch in the current counting
or interpolation engine. The README must never be used as certificate data.

## 7. Exact hashes

```text
KOSTKA_TO_LR_HOMOGENEOUS_BRIDGE.md
  ff85cad7484a9cd3e463057af3f2a798b61c843f8a777d5388a0abbb7d35626d
kostka_lr_bridge_zero_trust_audit.py
  e6bd2266ea33eedbd6c47f8d76b9ffa8e91dc5eeb26064e74f32cba702ac59db
engine/lr_hive.exe
  95d1fea3716756ffc48e662cfca117f04cc354ed598a638134163e50585b8cfc
vendor/kostka/target/release/kostka.exe
  9c2987d8d51d6163573c7f227a4409762dbf97fd54e727ac849e92c9cfee0ebd
vendor/kostka/src/ehrhart.rs
  29e3f755304998733f45d53f655b9a57632c7d243c9d30698d13c01e17efd911
vendor/kostka/src/gt_dim.rs
  0dfdba64b9a97ee741e635213cd2bf15c1ffb39c395812ecd170d76e03c9fd3e
```

Replay command:

```text
python problems_external\ktt_lr_negativity\kostka_lr_bridge_zero_trust_audit.py
```

Expected final status is `PASS` with zero tableau/hive/vendor mismatches, zero
degree or polynomial mismatches, zero `P(0)` failures, and zero held-out
failures.

## 8. Operational conclusion

The exact homogeneous bridge is valid. A verified negative coefficient in a
stretched skew-Kostka polynomial constructed this way is a literal KTT
counterexample, not merely an analogy.

No tested bug invalidates the current exact counters. The bounded gate is
authorized only with this correction:

```text
interpolate through U=(ell(w)-1)(ell(lambda)-1), trim exactly over Q,
then check n=U+1 and n=U+2 independently.
```

Every negative candidate must still be replayed through the hive LR engine at
all interpolation and held-out points. The 50,000-instance gate was not started
by this audit.
