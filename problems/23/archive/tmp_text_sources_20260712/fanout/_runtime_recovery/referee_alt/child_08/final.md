Strongest surviving lemma: a lexicographic minimizer of

`(scoped score, active vertices, active components, union size, row signature)`

exists and excludes any competitor preserving earlier coordinates while reducing the next. An injective row signature makes it unique.

This does not force Hall in the finite abstract model. Exact falsifier: one tuple, one demand, no sources, empty availability; metrics `(1,1,1,1,0)`. The tuple is the unique canonical minimizer, while the shore `{d}` has `1 > 0` neighbors.

Artifacts:

- [canonical_minimizer_report.md](E:/Projects/ErdosProblems/tmp/fanout/_runtime_recovery/referee_alt/child_08/canonical_minimizer_report.md)
- [verify_falsifier.py](E:/Projects/ErdosProblems/tmp/fanout/_runtime_recovery/referee_alt/child_08/verify_falsifier.py)

Verification command:

```powershell
python tmp/fanout/_runtime_recovery/referee_alt/child_08/verify_falsifier.py
```

Exact output includes `|X|=1, |N(X)|=0`.

SHA256:

- Report: `f30eff63178fbc097d852d74bf4d77647d6e08da56552054d7c9b306c778688d`
- Verifier: `7af8c738f261625c08e55a650c01b056b11f64a374c0f7e39646138c2f74a62a`

Explicit gap: the realizable graph model still requires a graph-specific simultaneous-row exchange improving one lexicographic coordinate. R29 rules out obtaining this from a one-row exchange; canonical tie-breaking alone supplies no such exchange.