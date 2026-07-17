# C78: image-boundary audit and local-bank obstructions

## Verdict

C78 does not prove or falsify the C23 unconditional one-step image
inequality.  It verifies the exact transition identities on stored image
witnesses, isolates the remaining image-specific boundary statement, and
gives small exact failures of four stronger local payment rules.

For a forward-closed source `S`, write `F(S)` for its one-step supported
image.  If `V` is the complement of `S`, then a nonseed lies outside `F(S)`
exactly when every admissible factor pair meets `V`.  Thus the C23 image
problem may be stated as a blocker-cut problem.

For every audited image `T`, the shell identity is

\[
 Q_T(X)-H_T(X)
 = \#\{\text{healed nonhard roots}\}
 - \#\{\text{unhealed hard roots}\}.
\]

The remaining image-specific lemma is therefore

\[
 \#\{\text{unhealed hard roots through }X\}
 \le
 \#\{\text{healed nonhard roots through }X\}
\]

for every image-realizable self-blocking complement.  No uniform proof is
known.

## Exact guardrails

The following stronger mechanisms fail on stored exact image witnesses.

| mechanism | first guarded failure |
|---|---:|
| immediate healed-factor matching | `X=54`, size `0/1` |
| full local missing-chain matching | `X=74`, size `1/2`; both demands reach only root `6` |
| direct structural bank | `X=186`, size `5/6` |
| rank-two zero-slack dominance | `X=362`, `11` hard versus `10` boundary roots |

At `X=186`, the full forward flow needs the nonlocal transfer

```text
48 -> 95 -> 32 -> 63 -> 125.
```

Dropping the early nonhard helper term first fails at `X=74`.  Requiring
unsupported thresholds to pay themselves first fails at `X=54`.

## Independent replay and extension

The verifier uses explicit exceptions, so its checks remain active under
`python -O`.  Replaying the original audit at cutoff `500` produced a
byte-identical JSON file.  The image variant was then scanned at every hard
cutoff through `1000`: all `66` integer programs were `OPTIMAL`, none had
positive image excess, and the final tested cutoff was `984` with excess
`-4`.

This is a finite theorem only.  It supplies no cutoff-uniform augmentation
or asymptotic density proof.

## Reproduction

```powershell
python -O problems/424/compute/wave5/C78_minimal_image_audit.py `
  --output problems/424/compute/wave5/C78_minimal_image_audit_500_replay.json `
  --scan-stop 500 --workers 64 --time-limit 30

python -O problems/424/compute/wave5/C78_minimal_image_audit.py `
  --output problems/424/compute/wave5/C78_image_scan_1000.json `
  --scan-stop 1000 --variants image --workers 64 --time-limit 30
```

```text
5942AF0BB1E7E2A9DA6B41034ADFB6BFF64F6F87A979A7BBF67AE02AC691F591  C78_minimal_image_audit.py
1D3B84AB0591325E04550F73947352AD237A8DE59A0FA447C516A2A08AB50045  C78_minimal_image_audit_500.json
1D3B84AB0591325E04550F73947352AD237A8DE59A0FA447C516A2A08AB50045  C78_minimal_image_audit_500_replay.json
1D3823FD73128527B6FA9B0DBEEC35AB5F484EE684DE91FFBFCF98A51F094F98  C78_image_scan_1000.json
```
