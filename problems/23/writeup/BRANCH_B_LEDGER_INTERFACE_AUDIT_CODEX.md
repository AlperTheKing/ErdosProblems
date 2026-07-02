# Branch-B Ledger Interface Audit

Date: 2026-07-02

Status: literal `(3.1)` from `PEEL_INVARIANT_SHPRIME_GPTPRO.md` cannot be the
full rowwise `R_Q` ledger with `k` equal to an integer count of selected
protected UNIT-FLAT5 cells and `d` the external blue boundary of their peeled
union.

Claude/GPT-Pro sharpened target:

```text
(3.1)  R_Q <= N - Sigma_L + k - d,
Sigma_L = (L^2-25)/50.
```

But `ROWWISE_SPLIT_PACKAGE_CODEX.md` defines

```text
R_Q = sum_{v in Q} Tw_C(v)
```

as the full rowwise quantity.  With this definition, pure odd cycles give an
immediate calibration obstruction to literal `(3.1)`.

## Exact C7 calibration

For `G=C7` with a connected gamma-minimum maximum cut:

```text
N = 7
m = 1
eta = N^2/25 - m = 24/25
L = 7
Sigma_L = (49-25)/50 = 12/25
R_Q = 7
```

There are no length-5 UNIT-FLAT5 protected cells in this graph, hence the
literal protected-cell interpretation gives

```text
k = 0
d = 0.
```

Then `(3.1)` gives

```text
R_Q <= N - Sigma_L = 7 - 12/25 = 163/25,
```

with exact margin

```text
163/25 - 7 = -12/25.
```

So literal `(3.1)` is false.

The final long-surplus target remains exactly tight:

```text
N + eta/2 - Sigma_L
= 7 + 12/25 - 12/25
= 7
= R_Q.
```

## Consequence

The peel-side ledger must be one of:

1. A residual/excess statement after subtracting the pure odd-cycle baseline,
   not a full `R_Q` statement.
2. A statement with an additional fractional baseline bank term, e.g. the
   existing Banked-UPO bank

   ```text
   bank(Q) = eta/2 - Sigma_L.
   ```

3. A statement where `k-d` is not merely an integer protected-cell count minus
   an integer door boundary, but includes the pure-odd-cycle deficit baseline.

The current local gates:

```text
_codex_slack_cage_rowunion_unit_gate.py
_codex_slack_cage_unit_peel_gate.py
_codex_slack_cage_unit_shape_catalog.py
```

certify the UNIT-FLAT5 protected-cell/precharge structure.  They do not output
a full-row ledger of the form `(3.1)`.

This is an interface correction, not a disproof of the long-surplus route.
The correct global target is still:

```text
R_Q <= N + eta/2 - Sigma_L.
```

