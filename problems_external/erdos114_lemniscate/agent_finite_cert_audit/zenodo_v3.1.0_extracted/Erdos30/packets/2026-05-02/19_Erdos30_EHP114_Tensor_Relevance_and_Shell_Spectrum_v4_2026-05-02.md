# Erdos #30, EHP114, and Shell-Spectrum v4

Date: 2026-05-02

## Short Answer

Yes. The #114 tensor-cone approach is relevant to #30, but not because the
same theorem transfers.

It is relevant because both problems are now showing the same architecture:

```text
easy radial parameter
+ hard shape space
+ positivity / certification question on a stratified object
```

For #114:

```text
radial mode     = lemniscate bifurcation / Puiseux / hypergeometric anchor
shape mode      = quotient tangent cone at the regular root polygon
certificate     = tensor cone / Toeplitz / Fejer-Riesz where applicable
```

For #30:

```text
radial mode     = shell delta D-D*
shape mode      = valid Sidon rearrangements inside a fixed shell
certificate     = collision channel + finite shell graph / Laplacian geometry
```

## v4 Result

The graph-spectrum probe has now been run.

```text
script:
/Users/kenbengoetxea/Downloads/Mendoza'sLimit-Maxwell-Godel-Ramujan/probes/erdos30_sktc_graph_spectrum_probe.py

results:
/Users/kenbengoetxea/Downloads/Mendoza'sLimit-Maxwell-Godel-Ramujan/results/erdos30_sktc_shell_graph_spectrum_v4_RESULTS.json

report:
/Users/kenbengoetxea/Downloads/Mendoza'sLimit-Maxwell-Godel-Ramujan/results/erdos30_sktc_shell_graph_spectrum_v4_REPORT.md

result_sha256:
88b05ed04d7cd6ed321aa9469eb0e645c96209ff62ab4cd54faed99ad135d8f9
```

Summary:

```text
shells analyzed: 52
nontrivial shells with >=3 nodes: 35
disconnected shells: 34
```

For the high-end local shells:

| k | delta | D | nodes | edges | components | isolated nodes | zero modes |
|---:|---:|---:|---:|---:|---:|---:|---:|
| 8 | 5 | 39 | 192 | 5 | 187 | 182 | 187 |
| 9 | 5 | 49 | 96 | 1 | 95 | 94 | 95 |
| 10 | 5 | 60 | 14 | 0 | 14 | 14 | 14 |

The spectral signal is not level repulsion. It is zero-mode abundance.

Physics language:

```text
near the Sidon optimum, the feasible-state landscape is fragmented/glassy,
not fluid-connected.
```

## How #114 Helps

The useful import from #114 is the discipline:

```text
do not force a smooth-Hessian story onto a stratified boundary problem
```

For #30, the analog is:

```text
do not force a single Fourier/tensor observable to carry the theorem.
```

The shell graph says the state space itself is the object. The certificate
should describe scarcity, fragmentation, and zero modes, not just discrepancy
amplitudes.

## What Does Not Transfer

The #114 Fejer-Riesz bridge is not directly available for #30.

Fejer-Riesz gives:

```text
PSD trigonometric polynomial on |z|=1
=> square modulus factorization
```

The #30 object is:

```text
finite shell graph / collision incidence complex
```

So the correct analog is more likely:

```text
PSD graph Laplacian certificate
Gram / finite-state SOS certificate
interlacing or expansion/fragmentation bound
```

Toeplitz structure may still appear, but only after a real symmetry-reduced
operator is found. It should not be asserted up front.

## Best Unified Framing

The shared method is:

```text
Stratified positivity certification
```

or, in your vocabulary:

```text
SKTC = Stratified Koopman-Tensor Certification
```

But the orthodox public name should be narrower:

```text
stratified finite-state certificate / shell-geometry certificate
```

## Next Move

For #30, the next target is no longer eigenvalue spacing in the Wigner sense.
The graph is too disconnected. The target is zero-mode geometry:

```text
Can we bound the number of components or isolated states in near-optimal Sidon
shells from first principles?
```

That would be the real #30 analog of the #114 tensor-cone certificate.
