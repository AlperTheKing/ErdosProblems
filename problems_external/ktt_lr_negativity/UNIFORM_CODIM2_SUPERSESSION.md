# Canonical codimension-two audit artifact

`uniform_codim2_gate.py` is **SUPERSEDED**.  It incorrectly asserts that rank
3 must contain a nonparallel normal pair, although the rank-3 hive space is
one-dimensional and codimension two is not applicable.

The canonical executable audit is

```text
uniform_codim2_gate_canonical.py
```

It runs the exact proof checks in `uniform_codim2_gate_repaired.py` with an
equivalent sparse Smith-index routine.  The sparse routine examines only the
union of the two row supports and stops once the gcd of the minors reaches
one.  This changes no arithmetic result and makes the ranks `3` through `20`
audit practical.

Required replay:

```powershell
python problems_external\ktt_lr_negativity\uniform_codim2_gate_canonical.py
python problems_external\ktt_lr_negativity\r5_e4_codim2_checker.py
```

The uniform runner must report rank 3 as `codim2=not_applicable`, the rigorous
uniform proof bound `1/12`, the observed ranks-4-through-20 minimum `1/9`, and
`PASS`.  The independent rank-5 runner must report minimum `1/9` and `PASS`.

The theorem and its scope are stated in `UNIFORM_CODIM2_POSITIVITY.md`; the
rank-5 specialization is stated in `R5_E4_CODIM2_POSITIVITY.md`.
