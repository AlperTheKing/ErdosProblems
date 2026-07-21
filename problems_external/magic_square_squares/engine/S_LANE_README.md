# Structural rational-identity S lane

`s_lane_reference.py` is the intentionally quadratic exact Python reference.
`s_lane_search.cpp` is the optimized, threaded C++ implementation. It uses
reduced 64-bit keys for each manifest `f(p,q)`, unsigned 128-bit intermediates
for exact sum/difference reduction, and Boost `cpp_int` for denominator
clearing and MSQ-D reconstruction.

Build:

```powershell
.\build_s_lane.ps1
```

Small complete lane:

```powershell
.\s_lane_search.exe --p-min 2 --p-max 128 --threads 4 `
  --scalar .\verify_scalar.py --independent .\verify_independent.exe
```

The output is JSONL. `EXHAUSTED` means every canonical pair and every exact
join in the requested closed max-P band was checked. A positive time limit can
instead produce `TIMEOUT_INCOMPLETE`; it is never reported as exhaustion.
Structurally valid hits are reconstructed as primitive MSQ-D certificates and
matrices, then sent to both exact verifiers. Candidate artifacts are written
only after such a hit.

Cross-calibration:

```powershell
$env:PYTHONDONTWRITEBYTECODE = '1'
python test_s_lane_calibration.py
```

The calibration independently enumerates every canonical `Fraction` value and
every `f1 > f2` join for P <= 64 in Python, compares the complete value map and
identity set with the C++ output, and checks that adjacent max-P bands partition
the full result. This proves no join is missed in the declared calibration
domain. It does not replace per-band exhaustion in a later search.

The join has worst-case quadratic complexity in the number of unique `f`
values. Higher manifest bands may therefore end as `TIMEOUT_INCOMPLETE` within
eight hours; this is an implementation limit, not mathematical evidence.
