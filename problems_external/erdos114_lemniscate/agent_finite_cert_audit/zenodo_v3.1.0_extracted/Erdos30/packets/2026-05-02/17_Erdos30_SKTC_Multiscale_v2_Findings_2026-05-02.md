# Erdos #30 SKTC Multiscale v2 Findings

Date: 2026-05-02

## Bottom Line

The proposed next step was correct, and it has now been run in a bounded,
reproducible form.

```text
PROBE_STATUS: COMPLETED
C3_STATUS: NOT_ATTAINED
D1_STATUS: NOT_MUTATED
CLAIM_CEILING: exact finite hypothesis screening only
```

The result is disciplined:

```text
The collision certificate works as a gate, but the current centered
multiscale observables do not yet give a clean asymptotic obstruction signal.
```

## New Artifacts

```text
script:
/Users/kenbengoetxea/Downloads/Mendoza'sLimit-Maxwell-Godel-Ramujan/probes/erdos30_sktc_multiscale_probe.py

results:
/Users/kenbengoetxea/Downloads/Mendoza'sLimit-Maxwell-Godel-Ramujan/results/erdos30_sktc_multiscale_v2_RESULTS.json

report:
/Users/kenbengoetxea/Downloads/Mendoza'sLimit-Maxwell-Godel-Ramujan/results/erdos30_sktc_multiscale_v2_REPORT.md

result_sha256:
61f8570bc935987eca9d9a9950a83acfe57732cebed0b5161bf93223afc59587
```

## What Was Actually Tested

The v2 probe computed:

- exact all-optimal canonical rulers for `k = 2..10`,
- centered dyadic interval discrepancy,
- centered prime/prime-power residue discrepancy,
- centered Bohr-cell discrepancy,
- centered difference-histogram L2,
- centered spectral norm of a difference-incidence tensor,
- greedy Sidon controls,
- random Sidon controls,
- random non-Sidon negative controls.

The optimal-ruler data was not imported. The script exhausted smaller
diameters locally, then enumerated all canonical optimal rulers at the first
diameter where a ruler exists.

## Key Search Receipt

```text
k=10
optimal diameter: 55
canonical optimal ruler count: 1
search nodes: 13,971,019
elapsed: 36.330 seconds
optimality verified by exhausting smaller diameters: true
```

This is still small finite evidence, but it is real evidence for the local
probe surface.

## Signal Assessment

The good news:

```text
random non-Sidon negative controls rejected: 21 / 21
```

The collision-certificate part is behaving.

The more important news:

```text
No centered observable in v2 cleanly separates optimal Sidon compression from
ordinary Sidon controls.
```

The closest weak signal is:

- exact optimal rulers have lower mean centered difference-histogram L2 than
  random Sidon and non-Sidon controls;
- residue and Bohr discrepancies are higher on average for random controls;
- centered tensor spectral norm is not yet a clean discriminator.

This does not kill SKTC. It kills the overly easy version of SKTC.

## Why This Matters

The v2 controls are not sharp enough. Random Sidon controls often have much
larger diameter and lower pair load than optimal rulers. That means the probe
is partly comparing dense compressed rulers against loose rulers, not isolating
the compression boundary itself.

The right next object is:

```text
compression shells
```

For each `k`, compare Sidon rulers at:

```text
D*, D*+1, D*+2, ..., D*+s
```

where `D*` is the optimal diameter.

That tests the actual Feynman question:

```text
As the ruler is forced toward optimal compression, does a centered
tensor/residue/Bohr defect appear, strengthen, or phase-change?
```

## Strategic Read

SKTC remains useful for #30 only if it becomes a compression-defect theorem
program. The theorem target should not be the full Erdős conjecture yet.

The first serious theorem target is:

```text
Sidon + diameter deficit M
=> lower bound on a centered stratified defect.
```

Then compare that defect lower bound against orthodox Fourier-uniformity or
equidistribution upper bounds.

If the compression-shell probe does not show a stable defect through the exact
small range, demote SKTC for #30 asymptotics and keep it as a reusable
finite-collision certification framework.
