# EHP114: The Nature Exemplar for Stratified Fourier Deficit

**Date:** 2026-05-02  
**Status:** Story/proof-framing note, not a proof claim  
**Use:** Mendoza Limit / Erdos Atlas / Paper V or VI candidate material

## One-Sentence Claim

EHP114 may be the polynomial/equipotential version of a very old natural pattern: a maximally symmetric singular configuration looks impossible in Euclidean perturbation coordinates, but becomes legible when the perturbations are decomposed into spectral modes and tensor selection rules.

## The Story

There has to be an exemplar in nature for this dynamic.

And there is.

The object is not a generic crystal, not a smooth bead rolling down a smooth bowl, and not a classical Euclidean perturbation problem. The right exemplar is a symmetric field configuration sitting at a singular threshold: a charged droplet, a fluid cylinder, or a regular polygon of equal line charges.

In the wrong coordinates, perturbations look like a mess. They look quixotic. They look like dozens of unrelated Euclidean directions, each bending the object in its own private way.

But nature does not see those perturbations as a coordinate spreadsheet.

Nature decomposes them into modes.

A liquid cylinder does not decide whether to break by checking arbitrary pointwise dents. The Plateau-Rayleigh instability decomposes the surface into Fourier modes and asks which wavelengths lower surface energy. A charged droplet does not lose stability by arbitrary deformation first; at the Rayleigh limit, spherical-harmonic modes decide how the symmetric sphere unfolds. The old symmetric object is not merely perturbed. It bifurcates through the modes that the geometry allows.

That is the pattern we are seeing in Erdos #114.

For a monic polynomial

```text
p(z) = product_j (z - z_j),
```

the identity

```text
log |p(z)| = sum_j log |z - z_j|
```

is not a metaphor. It is the two-dimensional electrostatic or gravitational potential of equal line charges placed at the roots.

So the lemniscate

```text
|p(z)| = 1
```

is an equipotential curve.

For the conjectured extremizer

```text
p(z) = z^n - 1,
```

the charges sit at the regular `n`-gon. The symmetry is maximal. The potential is maximally organized. But the configuration is also singular: the origin is a multiple critical point of the field and lies on the limiting structure that controls the lemniscate.

That is the key.

The reason the proof becomes hard near `n = 15` is not only that the search space grows from dimension `25` to dimension `27`. The deeper reason is representational. In coefficient coordinates, the lemniscate length functional looks like a high-dimensional nonlinear landscape. In the natural Hilbert/Fourier coordinates of the regular root polygon, the same perturbation space should decompose into spectral modes and cyclic tensor couplings.

The function we want is not just the length:

```text
L(p) = length({z : |p(z)| = 1}).
```

The function we want is the deficit:

```text
D_n(p) = L(z^n - 1) - L(p).
```

Near the regular polygon, write the roots as

```text
root_j = omega_j + u_j
omega_j = exp(2*pi*i*j/n),
```

where `u_j` is a perturbation field on the cyclic group `Z/nZ`.

Now lift that field into a finite Hilbert space and Fourier transform:

```text
u_j -> u_hat_k.
```

The hoped-for local structure is

```text
D_n(u)
  = sum_k lambda_k |u_hat_k|^2
    + cyclic tensor interaction terms
    + higher-order remainder.
```

And the cyclic symmetry should impose selection rules:

```text
only tensor terms with k1 + k2 + ... = 0 mod n survive.
```

This is the proof-language shift:

```text
raw Euclidean coefficient search
  -> Hilbert/Fourier mode decomposition
  -> cyclic tensor deficit
  -> stratified singular-unfolding certificate
```

The word `stratified` matters. The `z^n - 1` lemniscate is not behaving like an ordinary smooth interior maximum. It is closer to a singular symmetric extremizer. Small perturbations may unfold a central degeneracy rather than move smoothly along a regular manifold. So a naive Hessian theorem is probably the wrong target. The right target is a stratified deficit theorem: every allowed unfolding away from the symmetric singular configuration pays positive deficit.

## What The First Probe Found

The current diagnostic probe for `n = 15` built a Fourier/Hilbert perturbation basis of rank `27`, matching the expected reduced dimension `2n - 3`.

Artifact:

```text
/Users/kenbengoetxea/container-projects/apps/H2/Math/erdos-experiments/results/erdos-114/
  EXP-MATH-EHP114-N15-FOURIER-HESSIAN-20260502-02_RESULTS.json
  EXP-MATH-EHP114-N15-FOURIER-HESSIAN-20260502-02_REPORT.md
  EXP-MATH-EHP114-N15-FOURIER-HESSIAN-20260502-02_RESULTS.sha256
```

Result:

```text
degree: 15
basis rank: 27 / expected 2n - 3 = 27
tested eps: 0.02, 0.01, 0.005
positive deficit curvature rows: 27/27
worst tested mode: m7_sin_tangent
```

This is encouraging, but it is not a proof.

The same probe also flagged a real numerical and mathematical caution: the marching-squares estimate for the singular reference curve is rough, and the radial perturbation family unfolds the singularity sharply. That means the signal should be read as a stratified-unfolding signal, not as a certified smooth Hessian.

In plain language:

> The mode story is alive. The naive Hessian story is too weak.

Follow-up exact calculation:

```text
/Users/kenbengoetxea/container-projects/apps/H2/Math/erdos-experiments/results/erdos-114/
  EXP-MATH-EHP114-RADIAL-HYPERGEOMETRIC-20260502-01_RESULTS.json
  EXP-MATH-EHP114-RADIAL-HYPERGEOMETRIC-20260502-01_REPORT.md
  EXP-MATH-EHP114-RADIAL-HYPERGEOMETRIC-20260502-01_RESULTS.sha256
```

For the radial family `p_a(z) = z^n - a`, the exact length is:

```text
L_n(a) = integral_0^(2 pi) |a + exp(i t)|^(1/n - 1) dt.
```

For `n = 15`, this gives:

```text
L_15(1) = 32.847443161592574796553537519096796108161302188611.
```

The inward radial deficit scales like `eps^(1/15)`, not like `eps^2`. So the
right story is not "finite Hessian around a smooth optimum." It is a singular
boundary layer around a symmetric extremizer.

## The Nature Exemplar

The cleanest physical exemplars are:

1. **Two-dimensional electrostatics**

   The exact EHP114 mapping is already electrostatic:

   ```text
   log |p(z)| = sum_j log |z - z_j|.
   ```

   The roots are equal line charges. The lemniscate is an equipotential curve. The regular polygon is the maximally symmetric charge configuration. Perturbing the roots unfolds the equipotential geometry.

2. **Plateau-Rayleigh instability**

   A liquid cylinder is symmetric, but surface tension tests Fourier modes of the surface. Long-wavelength perturbations lower surface energy, grow, and break the cylinder into droplets. The key lesson is that nature does not treat arbitrary dents equally; the instability is mode-selected.

3. **Rayleigh charged-droplet instability**

   A charged sphere is symmetric until electrostatic repulsion overwhelms surface tension. At the Rayleigh limit, spherical-harmonic perturbation modes decide how the drop bifurcates into non-spherical shapes. This is very close to the EHP114 pattern: symmetric field object, spectral mode decomposition, singular threshold, allowed unfolding.

The common structure is:

```text
maximally symmetric object
  + singular or threshold geometry
  + spectral mode decomposition
  + energy/length/deficit functional
  + allowed perturbations governed by tensor selection rules
```

That is the natural exemplar class for #114.

## Paper-Safe Language

Safe:

> EHP114 has an exact potential-theoretic interpretation: the logarithm of the polynomial modulus is the two-dimensional potential of equal charges at the roots. This makes the regular-root configuration analogous to a symmetric field object whose perturbations are naturally decomposed into Fourier modes.

Safe:

> The `n = 15` diagnostic suggests that the correct local language is not raw coefficient search but a Hilbert/Fourier deficit expansion. Because the regular lemniscate is singular, the target should be a stratified Fourier/tensor deficit certificate rather than a naive smooth Hessian proof.

Unsafe:

> The Fourier probe proves EHP114 for `n = 15`.

Unsafe:

> Nature proves the conjecture.

Better:

> Nature supplies the right mathematical grammar: symmetric singular objects are tested by modes, not by arbitrary Euclidean coordinate perturbations.

## Next Mathematical Target

The next proof target should be:

```text
For perturbations u of the regular n-gon root configuration,
the deficit functional D_n(u) admits a stratified Fourier/tensor expansion
whose leading allowed terms are positive in every non-symmetry direction.
```

Then:

```text
local singular regime:
  stratified Fourier/tensor deficit

far regime:
  Tao-style dispersion deficit

middle regime:
  interval-certified finite patch
```

If this works, `n = 15` is no longer merely the next brute-force certificate. It becomes the first place where the proof changes language.

## References

- Plateau-Rayleigh instability overview and experiments: [Nature Communications](https://www.nature.com/articles/ncomms8409)
- Fluctuating hydrodynamics treatment with Fourier-mode analysis: [PMC](https://pmc.ncbi.nlm.nih.gov/articles/PMC10372655/)
- Charged drops and Rayleigh limit: [NASA NTRS](https://ntrs.nasa.gov/citations/19890052006)
- Variational models of charged drops and Rayleigh's 1882 stability analysis: [PMC](https://pmc.ncbi.nlm.nih.gov/articles/PMC4841488/)
- 2D electrostatics and complex-variable methods: [University of Virginia notes](https://galileoandeinstein.phys.virginia.edu/Elec_Mag/2022_Lectures/EM_14_2D_Electrostatics_Complex_Var_1.html)
