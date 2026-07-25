# Erdos #30 SKTC Compression-Shell v3 Probe Report

Date: 2026-05-02

## Verdict

```text
PROBE_STATUS: COMPLETED
C3_STATUS: NOT_ATTAINED
D1_STATUS: NOT_MUTATED
CLAIM_CEILING: exact finite compression-gradient screening only
```

This run replaced loose random Sidon controls with exact compression shells:

```text
D*, D*+1, D*+2, ..., D*+5
```

where `D*` is the optimal diameter for fixed `k`.

## Artifacts

```text
script:
/Users/kenbengoetxea/Downloads/Mendoza'sLimit-Maxwell-Godel-Ramujan/probes/erdos30_sktc_compression_shell_probe.py

results:
/Users/kenbengoetxea/Downloads/Mendoza'sLimit-Maxwell-Godel-Ramujan/results/erdos30_sktc_compression_shell_v3_RESULTS.json

result_sha256:
83ecd2436640e8bc5fd8609e35192b8177afe4a643d313e7652d1212c952faeb
```

The run used the v2 exact optimality receipts for `D*`, then exact-enumerated
all canonical Sidon/Golomb rulers at each positive shell diameter.

## Run Size

```text
max_k: 10
shell_width: 5
Sidon shell records: 1408
same-shell non-Sidon negative controls: 129
negative controls rejected by collision certificate: 129 / 129
```

The collision-certificate gate remains healthy.

## Compression-Shell Counts

| k | D* | counts at D*..D*+5 |
|---:|---:|---|
| 2 | 1 | `[1, 1, 1, 1, 1, 1]` |
| 3 | 3 | `[1, 1, 2, 2, 3, 3]` |
| 4 | 6 | `[1, 3, 4, 9, 8, 15]` |
| 5 | 11 | `[2, 7, 14, 21, 38, 50]` |
| 6 | 17 | `[4, 4, 20, 35, 86, 101]` |
| 7 | 25 | `[5, 7, 20, 60, 147, 190]` |
| 8 | 34 | `[1, 9, 14, 48, 91, 192]` |
| 9 | 44 | `[1, 4, 4, 21, 40, 96]` |
| 10 | 55 | `[1, 0, 0, 1, 2, 14]` |

The strongest new signal is not a Fourier/tensor defect. It is state-space
scarcity near the optimal boundary, especially the `k=10` vacancy at
`D*+1` and `D*+2`.

## Centered Observable Result

For `k = 8, 9, 10`, as shell delta increases and the ruler is loosened:

| k | pair-load slope | diff-hist L2 slope | tensor slope | dyadic slope | residue slope | Bohr slope |
|---:|---:|---:|---:|---:|---:|---:|
| 8 | -0.0211 | +0.00258 | +0.00022 | -0.00262 | +0.00665 | +0.01048 |
| 9 | -0.0167 | +0.00185 | +0.00021 | +0.00561 | +0.00127 | +0.00288 |
| 10 | -0.0137 | +0.00143 | +0.00007 | +0.02373 | +0.00083 | +0.00507 |

Interpretation:

- Pair load decreases as expected when diameter loosens.
- Centered difference-histogram L2, residue, and Bohr discrepancies rise
  slightly as the shell loosens.
- Centered tensor spectral norm is almost flat.
- This is the opposite of the naive "over-compression causes a visible
  centered discrepancy spike" expectation.

## Scientific Read

The v3 result weakens the simple SKTC-as-defect story.

It suggests this better formulation:

```text
The shadow near the Sidon boundary may be state-space scarcity / shell
geometry, not a large centered Fourier or tensor defect.
```

That is still compatible with a tensor-geometric program, but the object must
change. The target should be the geometry and entropy of feasible shells, not
one observable that spikes at `D*`.

## Next Gate

The useful v4 is not another centered-discrepancy run. It should be:

```text
compression-shell entropy and vacancy probe
```

For each `k`, measure:

- exact shell counts for wider `D*..D*+s` where feasible,
- vacancies/gaps such as `k=10`, `D*+1`, `D*+2`,
- birth rate of new canonical rulers per shell,
- graph connectivity of rulers under small mark moves,
- whether shell-count profiles stabilize after normalization.

This becomes theorem-relevant only if it yields a clean finite statement:

```text
Sidon + near-optimal diameter imposes a constrained shell geometry
that can be bounded independently of brute force enumeration.
```

Until then:

```text
SKTC_FOR_30: useful exploratory geometry, not C3 theorem machinery.
```
