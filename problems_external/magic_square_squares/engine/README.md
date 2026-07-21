# Exact scalar verifier

`verify_scalar.py` verifies the actual integer values in a candidate square; it
does not interpret matrix entries as roots.

Examples:

```powershell
python verify_scalar.py --matrix '[[8,1,6],[3,5,7],[4,9,2]]' --pretty
python verify_scalar.py --msq-d 5 1 2 --pretty
python verify_scalar.py --input fixtures/sallows_7_of_8.json --pretty
Get-Content candidate.json | python verify_scalar.py --input -
```

Exit codes:

- `0`: all positivity, square, distinctness, and eight-sum checks passed;
- `1`: well-formed input failed at least one mathematical check;
- `2`: malformed input.

The Sallows calibration fixture is transcribed from Paul Pierrat, François
Thiriet, and Paul Zimmermann, *Magic Squares of Squares*, which attributes the
near-miss to Lee Sallows (1997):
<https://members.loria.fr/PZimmermann/papers/squares.pdf>.

Run the calibrations with:

```powershell
python -m unittest -v test_verify_scalar.py
```

## E-lane doubled-integral-precursor engine

`elliptic_integral_search.cpp` implements exactly the finite E domain frozen
in `../LANE_MANIFEST.md`.  For each selected positive squarefree `kappa` and
each integral `x` in the closed box, it tests

```text
y^2 = x (x^2 - kappa^2),  y > 0,
```

then computes `X = x(2P)` and the rational roots of `X-kappa`, `X`, and
`X+kappa` by exact formulas.  It deduplicates `X` within one curve, performs
an exact rational three-term-AP join, clears all nine root denominators, and
emits an MSQ-D certificate only after both existing verifiers return zero.

It does **not** enumerate nonintegral precursor points.  Therefore `NO_HIT`
means only that the selected doubled integral precursors in the stated box
did not emit a certificate; it says nothing about all of `E_kappa(Q)`.

Build with the local MinGW compiler:

```powershell
g++ -std=c++20 -O3 -DNDEBUG -Wall -Wextra -Wconversion `
  -o elliptic_integral_search.exe elliptic_integral_search.cpp
```

Self-test the two frozen doubling vectors:

```powershell
.\elliptic_integral_search.exe --self-test
```

Production-shaped examples (shown for interface documentation only):

```powershell
# One complete manifest lane, single chunk. The built-in ceiling is 8 hours.
.\elliptic_integral_search.exe --lane E01 --x-bound 1048576 `
  --chunk-count 1 --chunk-index 0 --max-seconds 28800 `
  --out-dir logs\E01-c00

# Split a lane across kappa values. Never run more than 64 aggregate chunks.
.\elliptic_integral_search.exe --lane E01 --x-bound 1048576 `
  --chunk-count 64 --chunk-index 7 --max-seconds 28800 `
  --out-dir logs\E01-c07
```

Chunking is by `kappa`, not by `x`, so every AP join retains the complete
point set for its curve.  `summary.json` is atomically replaced at process
completion.  `--emit-inventory` additionally writes an atomic canonical
`inventory.jsonl`, intended for small calibration domains.  Summary statuses
are:

- `HIT_VERIFIED`: reconstructed certificate; both verifiers exited zero;
- `NO_HIT`: the declared finite chunk was exhausted;
- `TIMEOUT_INCOMPLETE`: the wall clock fired before exhaustion;
- `FAILED_VERIFICATION`: an internally reconstructed candidate was rejected;
- `FAILED`: an arithmetic, I/O, or process error occurred.

Process exit codes are `0` for `NO_HIT` or `HIT_VERIFIED`, `4` for
`TIMEOUT_INCOMPLETE`, `3` for a failed candidate/run, and `2` for bad CLI
input.

### Independent reference calibration

`elliptic_reference.py` reimplements the same finite domain using Python
`Fraction` and `math.isqrt`; it does not import arithmetic from the C++
engine.  `calibrate_elliptic.py` compares the full canonical inventories and
all counters for `kappa <= 16` at `B = 16, 50, 100, 500`, and checks frozen
vectors on `E_5` and `E_6`:

```powershell
python calibrate_elliptic.py
```

The retained result is
`calibration/elliptic_k16/calibration_summary.json`.  This calibration is a
small implementation check, not an E-lane search or evidence about the open
problem.
