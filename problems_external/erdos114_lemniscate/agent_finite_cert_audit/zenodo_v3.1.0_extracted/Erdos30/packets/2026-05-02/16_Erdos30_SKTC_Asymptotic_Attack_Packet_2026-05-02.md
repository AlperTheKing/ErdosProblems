# Erdos #30 SKTC Asymptotic Attack Packet

Date: 2026-05-02

## Verdict

```text
MATH_STATUS: OPEN
D1_STATUS: NOT_MUTATED
C3_STATUS: NOT_ATTAINED
CLAIM_CEILING: asymptotic attack program plus exact small-k hypothesis probe
```

The useful reframe is not:

```text
Use SKTC to prove h(N) = sqrt(N) + o(sqrt(N)).
```

That statement is too weak for the prize-level target, because the known
`sqrt(N) + O(N^(1/4))` upper-bound family already implies an `o(sqrt(N))`
error term.

The real target is:

```text
h(N) = N^(1/2) + O_epsilon(N^epsilon)
```

Equivalently, in diameter language, a Sidon/Golomb ruler with `k` marks should
need diameter

```text
D(k) >= k^2 - O_eta(k^(1 + eta))
```

for every `eta > 0`. The current record is still an `N^(1/4)`-scale error in
the `h(N)` formulation, or a `k^(3/2)`-scale deficit in the diameter
formulation.

## Feynman-Orthogonal Reframe

If Stratified Koopman-Tensor Certification helps #30, it will not help by
renaming the pigeonhole argument. The C2 Lean layer already captures that
finite collision-channel spine:

```text
source pairs P       = strict upper triangle of A x A
channel phi(a,b)    = a - b
codomain C          = {1, ..., N}
Sidon condition     = injective channel / fiber size <= 1
B2[g] extension     = bounded fiber size <= g
```

To become asymptotically interesting, SKTC has to expose why too much
compression forces a defect that cannot coexist with extremal Sidon structure.

The attack sentence:

```text
Compression must leave a shadow; the theorem program is to prove that the
shadow cannot be hidden below the N^(1/4) barrier.
```

## The Key Obstruction

The naive version is probably false or too weak:

```text
Over-compressed Sidon sets have one large global Fourier coefficient.
```

That collides with the known orthodox direction that extremal Sidon sets are
Fourier-pseudorandom / Fourier-uniform. So the SKTC version should not bet on a
single global coefficient.

The better hypothesis is stratified:

```text
Over-compression forces a defect in at least one local/residue/Bohr/tensor
stratum, even when global Fourier coefficients look uniform.
```

This keeps the bridge to standard additive combinatorics rather than asking
orthodox readers to accept a new vocabulary first.

## SKTC Objects For #30

Use the C2 artifact as the formal backbone:

```text
/Users/kenbengoetxea/container-projects/apps/H2/Math/erdos-experiments/Erdos30/lean/Erdos30_CollisionChannel.lean
```

Interpret the ingredients as follows:

| SKTC name | Orthodox object | What it should measure |
|---|---|---|
| Collision channel | difference map `(a,b) -> a-b` | uniqueness or bounded multiplicity of differences |
| Tensor layer | incidence tensor `T_A(x,d)=1_A(x)1_A(x+d)` | where the allowed difference mass sits |
| Koopman layer | translation / phase action on `1_A` | how structure moves under shifts and characters |
| Stratification | intervals, residue classes, Bohr cells, scale bands | where global uniformity hides local pressure |
| Certificate | finite inequality with explicit defect term | a route from compression to contradiction |

The target theorem shape should be:

```text
If A is Sidon, |A|=k, diam(A)=N, and N <= k^2 - M,
then some certified stratified tensor defect is at least F(M,k).
```

Then compare that lower bound with known upper bounds for extremal Sidon
uniformity. If the lower and upper bounds cross before `M ~ k^(1+eta)`, the
approach has real theorem pressure.

## Falsifiable Predictions

These are deliberately framed so the program can fail cleanly.

1. A single global DFT coefficient will not be enough. If the only signal is
   `max_r |sum_a exp(2 pi i r a / m)|`, the route probably stalls.
2. A multiscale tensor/residue defect should strengthen as diameter deficit
   `k^2 - D(k)` increases, after controlling for `k`.
3. The defect should survive across multiple optimal rulers, not only one
   chosen representative.
4. The signal should weaken or change predictably in B2[g] / `g`-thin variants.
5. Random non-Sidon controls should fail the collision certificate rather than
   falsely looking like positive evidence.
6. If exact optimal rulers through the feasible range and Singer-style
   constructions show no stable stratified defect, SKTC should be demoted for
   #30 and kept only as a formal-certificate vocabulary.

## Exact Small-k Probe Run

I created and ran a small exact laptop probe:

```text
script:  /Users/kenbengoetxea/Downloads/Mendoza'sLimit-Maxwell-Godel-Ramujan/probes/erdos30_sktc_probe.py
output:  /Users/kenbengoetxea/Downloads/Mendoza'sLimit-Maxwell-Godel-Ramujan/results/erdos30_sktc_exact_small_k_RESULTS.json
sha256:  1229a065f45554858ebf730c10b8fc78a61cfb99797079e58572e7bca8240164
```

Scope:

```text
exact enumeration of one optimal Golomb ruler for each k = 2..8
hypothesis-screening only
not asymptotic evidence
```

Summary table:

| k | diameter | marks | pair load | slack | max mark Fourier | max diff Fourier | max residue discrepancy |
|---:|---:|---|---:|---:|---:|---:|---:|
| 2 | 1 | `[0,1]` | 1.000 | 0 | 0.000 | 1.000 | 0.000 |
| 3 | 3 | `[0,1,3]` | 1.000 | 0 | 0.333 | 0.333 | 0.333 |
| 4 | 6 | `[0,1,4,6]` | 1.000 | 0 | 0.354 | 0.167 | 0.333 |
| 5 | 11 | `[0,1,4,9,11]` | 0.909 | 1 | 0.447 | 0.200 | 0.309 |
| 6 | 17 | `[0,1,4,10,12,17]` | 0.882 | 2 | 0.441 | 0.166 | 0.275 |
| 7 | 25 | `[0,1,4,10,18,23,25]` | 0.840 | 4 | 0.451 | 0.148 | 0.286 |
| 8 | 34 | `[0,1,4,9,15,22,32,34]` | 0.824 | 6 | 0.392 | 0.144 | 0.232 |

Immediate read:

```text
No smoking gun appears in the naive global Fourier observables.
```

That is actually useful. It pushes the program away from "look for one big
coefficient" and toward centered multiscale/tensor observables, which is more
consistent with the Fourier-uniformity literature.

## Next Technical Step

Build the C3 probe in this order:

1. Replace "one optimal ruler per k" with all optimal rulers available for
   `k <= 10`, then trusted table/certificate imports through `k <= 18`.
2. Add controls:
   - greedy Sidon sets at same `k`,
   - random Sidon sets inside same diameter where available,
   - non-Sidon negative controls rejected by the collision certificate.
3. Add centered stratified observables:
   - interval discrepancy over dyadic windows,
   - residue discrepancy over primes and prime powers,
   - Bohr-cell discrepancy,
   - spectral norm of centered difference-incidence matrices.
4. Promote only stable signals into Lean theorem targets.
5. Keep public language at:

```text
finite collision-channel certification and exploratory asymptotic obstruction search
```

Do not publicly call this a proof strategy for solving #30 until one of the
defect inequalities is mathematically stated and survives computation.

## Sources Checked

- T. F. Bloom, [Erdos Problem #30](https://www.erdosproblems.com/30), accessed 2026-05-02. The page states the open target and records the current `0.98183 N^(1/4)` error term.
- Carter, Hunter, and O'Bryant, [On the Diameter of Finite Sidon Sets](https://arxiv.org/abs/2310.20032), arXiv:2310.20032.
- Ortega and Prendiville, [Extremal Sidon Sets are Fourier Uniform, with Applications to Partition Regularity](https://www.numdam.org/articles/10.5802/jtnb.1239/), Journal de theorie des nombres de Bordeaux 35 (2023), 115-134.
