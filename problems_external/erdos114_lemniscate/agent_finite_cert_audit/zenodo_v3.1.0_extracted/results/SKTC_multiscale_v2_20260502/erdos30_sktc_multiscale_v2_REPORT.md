# Erdos #30 SKTC Multiscale v2 Probe Report

Date: 2026-05-02

## Verdict

```text
PROBE_STATUS: COMPLETED
C3_STATUS: NOT_ATTAINED
D1_STATUS: NOT_MUTATED
CLAIM_CEILING: exact finite hypothesis screening only
```

This v2 probe upgrades the prior one-representative run into an exact
small-range multiscale screen. It does not provide asymptotic theorem evidence
for Erdős #30.

## Artifacts

```text
script:  /Users/kenbengoetxea/Downloads/Mendoza'sLimit-Maxwell-Godel-Ramujan/probes/erdos30_sktc_multiscale_probe.py
results: /Users/kenbengoetxea/Downloads/Mendoza'sLimit-Maxwell-Godel-Ramujan/results/erdos30_sktc_multiscale_v2_RESULTS.json
sha256:  61f8570bc935987eca9d9a9950a83acfe57732cebed0b5161bf93223afc59587
```

Verification:

```text
python3 -m py_compile probes/erdos30_sktc_multiscale_probe.py
shasum -a 256 -c results/erdos30_sktc_multiscale_v2_RESULTS.json.sha256
```

Both passed.

## What Changed From v1

v1 asked whether one naive global Fourier signal was obvious. It was not.

v2 adds:

- exact all-optimal canonical rulers for `k = 2..10`,
- centered dyadic interval discrepancy,
- centered residue discrepancy over primes and prime powers,
- centered Bohr-cell discrepancy,
- centered difference-histogram L2,
- centered spectral norm of a difference-incidence tensor,
- greedy Sidon controls,
- random Sidon controls,
- random non-Sidon negative controls.

## Exact Optimal Search Receipt

The script did not import an optimal-ruler table. It exhausted smaller
diameters locally, then enumerated all canonical optimal rulers at the first
admissible diameter.

| k | optimal diameter | canonical optimal rulers | search nodes | seconds |
|---:|---:|---:|---:|---:|
| 2 | 1 | 1 | 2 | 0.000 |
| 3 | 3 | 1 | 5 | 0.000 |
| 4 | 6 | 1 | 17 | 0.000 |
| 5 | 11 | 2 | 167 | 0.000 |
| 6 | 17 | 4 | 1,463 | 0.002 |
| 7 | 25 | 5 | 17,389 | 0.035 |
| 8 | 34 | 1 | 173,630 | 0.319 |
| 9 | 44 | 1 | 1,601,873 | 3.544 |
| 10 | 55 | 1 | 13,971,019 | 36.330 |

## Main Read

The negative controls worked:

```text
random_non_sidon_negative_control rejected: 21 / 21
```

That means the collision-certificate layer is behaving as a sanity gate.

The centered multiscale observables are informative but not yet decisive:

| family | count | mean pair load | mean dyadic | mean residue | mean Bohr | mean diff-hist L2 | mean centered tensor |
|---|---:|---:|---:|---:|---:|---:|---:|
| exact optimal | 17 | 0.883 | 0.281 | 0.263 | 0.376 | 0.065 | 0.509 |
| greedy Sidon | 9 | 0.766 | 0.313 | 0.270 | 0.357 | 0.080 | 0.486 |
| random Sidon | 26 | 0.525 | 0.323 | 0.335 | 0.472 | 0.138 | 0.544 |
| non-Sidon negative | 21 | 0.870 | 0.280 | 0.325 | 0.469 | 0.181 | 0.551 |

Interpretation:

- The difference-histogram L2 observable separates exact optimal rulers from
  random non-Sidon controls in this small run.
- Residue and Bohr discrepancies are higher on average for random Sidon and
  non-Sidon controls than for exact optimal rulers.
- The centered tensor spectral norm does not cleanly separate exact optimal
  from Sidon controls.
- Dyadic interval discrepancy is not a reliable discriminator at this scale.

## Important Limitation

The current random Sidon controls are too loose. They often have much larger
diameter and lower pair load than optimal rulers. That confounds the question
we actually care about:

```text
What changes as a Sidon set is forced toward optimal compression?
```

So v2 is useful, but it is not yet the right C3-level control surface.

## Next Gate

The next probe should be a compression-shell probe:

```text
For each k, compare Sidon rulers at diameters
D*, D*+1, D*+2, ..., D*+s
where D* is the optimal diameter.
```

This isolates the compression gradient. The useful question becomes:

```text
Do centered tensor/residue/Bohr defects change monotonically or sharply as
diameter approaches D*?
```

If no stable compression-shell signal appears through `k <= 10`, SKTC should
be demoted for #30 asymptotic attack and retained only as a formal
collision-certificate framework.

If a stable compression-shell signal appears, the first theorem target is not
the Erdős conjecture. It is a finite inequality of this shape:

```text
Sidon + diameter deficit M => lower bound on a centered stratified defect.
```

Only after that inequality exists should we talk about a C3 theorem program.
