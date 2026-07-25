# Erdos #30 SKTC Exact Small-k Probe Report

Date: 2026-05-02

## Scope

This run exactly enumerated one optimal Golomb ruler for each `k = 2..8` by
increasing diameter, then computed lightweight SKTC-style observables:

- pair-load and pigeonhole slack,
- global Fourier max for marks modulo `diameter + 1`,
- global Fourier max for positive differences modulo `diameter + 1`,
- residue discrepancy for small moduli,
- interval discrepancy over a small window set.

Claim ceiling:

```text
hypothesis-screening only; not asymptotic theorem evidence
```

## Artifacts

```text
script:  /Users/kenbengoetxea/Downloads/Mendoza'sLimit-Maxwell-Godel-Ramujan/probes/erdos30_sktc_probe.py
results: /Users/kenbengoetxea/Downloads/Mendoza'sLimit-Maxwell-Godel-Ramujan/results/erdos30_sktc_exact_small_k_RESULTS.json
sha256:  1229a065f45554858ebf730c10b8fc78a61cfb99797079e58572e7bca8240164
```

## Result

The probe found no strong smoking-gun signal in the naive global Fourier
observables. For `k = 5..8`, the mark-Fourier maxima are nonmonotone and the
difference-Fourier maxima decrease gently:

```text
k=5: mark 0.447, diff 0.200
k=6: mark 0.441, diff 0.166
k=7: mark 0.451, diff 0.148
k=8: mark 0.392, diff 0.144
```

## Interpretation

This does not refute SKTC. It refutes the cheapest version:

```text
over-compression is visible as one large global Fourier coefficient
```

The next useful probe should move to centered multiscale observables:

- dyadic interval discrepancy,
- residue discrepancy over primes and prime powers,
- Bohr-cell discrepancy,
- centered spectral norms of difference-incidence tensors,
- all optimal rulers where available, not one representative.

## Status

```text
C3_STATUS: NOT_ATTAINED
NEXT_GATE: build a multiscale/tensor defect probe and test against controls
```
