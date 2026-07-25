# Erdos #30 SKTC Shell-Graph Spectrum v4 Report

Date: 2026-05-02

## Verdict

```text
PROBE_STATUS: COMPLETED
C3_STATUS: NOT_ATTAINED
D1_STATUS: NOT_MUTATED
CLAIM_CEILING: finite shell-geometry and eigenvalue-spacing screening only
```

This run computes the graph-spectrum object missing from v3.

## Artifacts

```text
script:
/Users/kenbengoetxea/Downloads/Mendoza'sLimit-Maxwell-Godel-Ramujan/probes/erdos30_sktc_graph_spectrum_probe.py

input:
/Users/kenbengoetxea/Downloads/Mendoza'sLimit-Maxwell-Godel-Ramujan/results/erdos30_sktc_compression_shell_v3_RESULTS.json

results:
/Users/kenbengoetxea/Downloads/Mendoza'sLimit-Maxwell-Godel-Ramujan/results/erdos30_sktc_shell_graph_spectrum_v4_RESULTS.json

result_sha256:
88b05ed04d7cd6ed321aa9469eb0e645c96209ff62ab4cd54faed99ad135d8f9
```

Verification:

```text
python3 -m py_compile probes/erdos30_sktc_graph_spectrum_probe.py
shasum -a 256 -c results/erdos30_sktc_shell_graph_spectrum_v4_RESULTS.json.sha256
```

Both passed.

## Graph Definition

For each fixed `(k, D)` shell:

```text
nodes = canonical Sidon/Golomb rulers in that shell
edge  = one interior mark moves by +/- 1 and remains a valid canonical ruler
```

Reflection-equivalent rulers are quotient-identified by canonicalization.

The computed operator is the unnormalized graph Laplacian:

```text
L = degree_matrix - adjacency_matrix
```

## Main Result

The shell graphs are mostly fragmented:

```text
shells analyzed: 52
nontrivial shells with >=3 nodes: 35
disconnected shells: 34
```

For the largest shells:

| k | delta | D | nodes | edges | components | isolated nodes | zero modes |
|---:|---:|---:|---:|---:|---:|---:|---:|
| 8 | 3 | 37 | 48 | 1 | 47 | 46 | 47 |
| 8 | 4 | 38 | 91 | 3 | 88 | 85 | 88 |
| 8 | 5 | 39 | 192 | 5 | 187 | 182 | 187 |
| 9 | 4 | 48 | 40 | 1 | 39 | 38 | 39 |
| 9 | 5 | 49 | 96 | 1 | 95 | 94 | 95 |
| 10 | 5 | 60 | 14 | 0 | 14 | 14 | 14 |

The most important spectral fact:

```text
The near-optimal shell graphs have many zero modes.
```

That means the local one-mark transition graph is not a connected low-energy
manifold. It is mostly isolated islands.

## Interpretation

We are not yet seeing Wigner-style level repulsion or meaningful connected
eigenvalue spacing. Most shells are too disconnected. The spectrum is dominated
by zero modes, which encode component count.

Physics translation:

```text
near the Sidon optimum, the configuration space looks glassy/fragmented,
not fluid-connected.
```

This makes the strongest current analogy:

```text
density of states + zero-mode structure + fragmented low-energy landscape
```

not:

```text
single resonance, smooth band, or connected quantum chaotic spectrum
```

## Relation To EHP114 Tensor Program

The analogy to #114 is real but methodological.

In #114:

```text
radial direction: tractable by exact hypergeometric/Puiseux analysis
shape direction: hard, stratified, tensor-cone dominated
```

In #30:

```text
radial direction: shell delta D-D*
shape direction: graph of valid ruler rearrangements inside a shell
```

The v4 result says the #30 shape direction is highly fragmented under local
moves. That is the #30 analog of a hard shape-mode obstruction.

## What Does Not Transfer Directly

The Fejer-Riesz bridge from #114 does not directly apply to #30 shell graphs.

Fejer-Riesz is a statement about nonnegative trigonometric polynomials on the
unit circle. The #30 shell object is a finite combinatorial graph / incidence
complex. The correct analog would be:

```text
PSD graph Laplacian / Gram certificate
finite-state sum-of-squares certificate
interlacing or expansion certificate
```

Toeplitz/circulant structure may enter only after finding a symmetry-reduced
operator on differences, residues, or shell transitions. It should not be
assumed.

## Next Theorem-Shaped Target

The honest next mathematical target is:

```text
near-optimal Sidon shells have fragmented local transition geometry
```

The first finite theorem target could be:

```text
For fixed k and shell width s, the one-mark shell graph has at least m(k,s)
components or at most e(k,s) edges.
```

That is not Erdős #30, but it is a concrete geometry-of-feasible-states theorem
that could become a reusable SKTC certificate.
