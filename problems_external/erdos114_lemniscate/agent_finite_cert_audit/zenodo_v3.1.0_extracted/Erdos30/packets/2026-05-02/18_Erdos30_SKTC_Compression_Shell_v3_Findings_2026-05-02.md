# Erdos #30 SKTC Compression-Shell v3 Findings

Date: 2026-05-02

## Bottom Line

The compression-shell probe has now been run.

```text
PROBE_STATUS: COMPLETED
C3_STATUS: NOT_ATTAINED
D1_STATUS: NOT_MUTATED
CLAIM_CEILING: exact finite compression-gradient screening only
```

The important result is not the one we hoped for, but it is useful:

```text
The obvious centered discrepancy/tensor observables do not spike at optimal
compression. The stronger signal is shell scarcity near the boundary.
```

## New Artifacts

```text
script:
/Users/kenbengoetxea/Downloads/Mendoza'sLimit-Maxwell-Godel-Ramujan/probes/erdos30_sktc_compression_shell_probe.py

results:
/Users/kenbengoetxea/Downloads/Mendoza'sLimit-Maxwell-Godel-Ramujan/results/erdos30_sktc_compression_shell_v3_RESULTS.json

report:
/Users/kenbengoetxea/Downloads/Mendoza'sLimit-Maxwell-Godel-Ramujan/results/erdos30_sktc_compression_shell_v3_REPORT.md

result_sha256:
83ecd2436640e8bc5fd8609e35192b8177afe4a643d313e7652d1212c952faeb
```

## What Was Tested

For each `k = 2..10`, the probe compared all canonical Sidon/Golomb rulers at:

```text
D*, D*+1, D*+2, D*+3, D*+4, D*+5
```

where `D*` is the optimal diameter.

The v2 exact receipt supplied `D*`; v3 then exact-enumerated every positive
shell. It generated:

```text
Sidon shell records: 1408
same-shell non-Sidon negative controls: 129
negative controls rejected: 129 / 129
```

## Main Signal

The shell counts are the most interesting result:

| k | D* | counts at D*..D*+5 |
|---:|---:|---|
| 8 | 34 | `[1, 9, 14, 48, 91, 192]` |
| 9 | 44 | `[1, 4, 4, 21, 40, 96]` |
| 10 | 55 | `[1, 0, 0, 1, 2, 14]` |

For `k=10`, the first two shells above optimum are empty. That is a real
geometric feature of the finite state space in this probe.

## What Failed

The naive SKTC prediction would be:

```text
as compression approaches D*, centered tensor/residue/Bohr defects should
increase or phase-change.
```

That did not appear.

For `k=8..10`, centered difference-histogram L2, residue discrepancy, and
Bohr discrepancy generally rise slightly as the shell loosens. Centered tensor
spectral norm is nearly flat.

So the easy story is wrong:

```text
over-compression is not showing up as one obvious centered discrepancy spike.
```

## Better Story

The better SKTC object may be:

```text
state-space scarcity / shell geometry
```

not:

```text
large global Fourier coefficient or large centered tensor norm
```

That still fits the broader "defects as shadows" theme, but the shadow is
combinatorial-geometric: whole shells thin out or vanish near the optimum.

## Next Move

The next useful probe is v4:

```text
compression-shell entropy and vacancy probe
```

Measure:

- wider shell counts where feasible,
- vacancy/gap patterns,
- birth rate of new canonical rulers per shell,
- graph connectivity under one-mark moves,
- normalized shell-count profiles across `k`,
- whether the `k=10` vacancy behavior persists at larger `k` via cluster/table
  input.

The first theorem target would then be modest and orthodox:

```text
near-optimal Sidon rulers have constrained shell geometry
```

not:

```text
Erdos #30 is solved
```

This keeps SKTC alive as a geometry-of-feasible-states program, but it does not
yet justify C3 or public theorem-pressure language.
