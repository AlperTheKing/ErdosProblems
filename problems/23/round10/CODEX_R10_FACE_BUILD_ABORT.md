# R10 D22 face-run resource abort

Command launched:

```text
python problems/23/round10/CODEX_R10_g11_d22_face_export.py --solve --solver CLARABEL --tol 1e-8 --max-iter 500
```

The command emitted no model or solver output before termination.  During face
construction, owned Python PID 84860 grew as follows:

```text
private memory: 147,749,982,208 -> 155,982,712,832 bytes
working set:     68,891,795,456 -> 88,686,813,184 bytes
```

The increase occurred within seconds and was still continuing.  To protect
the registered approximately 192 GB memory ceiling, only PID 84860 was
terminated:

```text
Stop-Process -Id 84860 -Force
```

The unified command then returned exit code 1 with no output.  Clarabel had
not reported a start, status, or iterate.  No
`CODEX_R10_g11_d22_face_numeric.pkl` and no
`CODEX_R10_D22_FACE_RUN.md` were written.

The build path uses whole-matrix SymPy exact RREF/determinant/inverse
operations for rational face projectors.  This is the suspected allocation
site, not a confirmed solver failure.  No alternative solver, degree, value
of `c`, or model was launched.
