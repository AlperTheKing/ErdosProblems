# Paper replay audit

Canonical replay sequence from the repository root:

```powershell
python -B tmp\paper_replay_audit\run_audit.py
python -B tmp\paper_replay_audit\finalize_audit_v2.py
python -B tmp\paper_replay_audit\verify_manifest.py
```

The first command runs the eight source gates sequentially. The second adds the
nine-copy R57 compiled-interface replay and renders `REPORT.md`. The third
checks every recorded input/output hash and expected exit status.

The `c5_3_two_row_exchange` gate intentionally returns process exit code `1`
when it verifies `NO_TWO_ROW_EXCHANGE`; `run_audit.py` records that code as the
expected scientific outcome.

The nine-copy R57 object is an interface countermodel, not a graph
counterexample. It repeats one graph bad edge nine times and therefore violates
`CompleteShortestRowDB.badKeys_nodup`, a condition absent from the proposed
R55/R57 bridge statement.
