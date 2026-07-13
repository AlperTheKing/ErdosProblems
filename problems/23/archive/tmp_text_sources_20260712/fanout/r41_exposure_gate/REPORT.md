# R41 corrected production neutralExposure gate

## Verdict

The four requested available canonical fixture states all have exact defect
zero under the P1/P3/strict-P4/P5 subset, hence also under the full production
P1/P2/P3/P4/P5/common-blue relation. Their minimum Exposure is zero by the
empty positive-defect sink-SCC convention.

| fixture | defect | minimum Exposure | positive sink SCCs |
|---|---:|---:|---:|
| 89 | 0 | 0 | 0 |
| 2943 | 0 | 0 | 0 |
| 3892 | 0 | 0 | 0 |
| join-5886 | 0 | 0 | 0 |

The SHA-pinned available N<=12 corpus contains 992,618 canonical states. All
have defect zero. Therefore no positive-defect occurrence graph is generated,
there are no equal-defect detours or sink SCCs to expand, and no full replay
certificate is required.

## Corrected exposure

Common-blue is admitted only through the production `TerminalData.Valid`
condition

```text
dM({x,y}) + 2 <= dB({x,y}), equivalently sigma({x,y}) >= 2.
```

The census contains 55 sigma-0 probes and 174 sigma-1 probes. All 229 are
classified as weak and contribute zero exposure. The sigma-1 N=20 control is
also pinned in the manifest.

## Monotone support

For a genuine two-edge detour

```text
Q:  x-m-y   ->   Q': x-v-y,
```

the new edges `xv,vy` are active and absent from the old selected support, so

```text
|support'|-|support|
  = 2 - 1[pairCount(m,x)=1] - 1[pairCount(m,y)=1] >= 0.
```

Equality holds exactly when both old support edges have unique selected-row
occurrences. Otherwise support grows strictly. A directed neutral cycle must
therefore have equality on every transition; every transition is fully
unsaturated and creates both orientations and both halves on the old-middle
endpoints. The multiplicity-saturated R38 rotor is impossible. Any surviving
zero-exposure object must be a source-swap rotor consuming every created
eligible key.

The bounded real-cage audit checks 32 multiplicity-saturated producer swaps:
all retain an old square support edge and none forms an inverse-active pair.

## Replay

```powershell
python -m py_compile tmp/fanout/r41_exposure_gate/*.py
python tmp/fanout/r41_exposure_gate/exposure_gate.py --workers 8
python tmp/fanout/r41_exposure_gate/verify_manifest.py
```

All arithmetic is integer/set arithmetic. The worker cap is enforced at 8.
