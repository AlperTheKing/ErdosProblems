# Frozen-Tranche Recovery Harness

`recovery_supervisor.py` is a run-once continuation of
`tranche64-frozen-manifest-v1`; it is not a second search tranche.

## Coverage accounting

- E01--E16 and S01--S03 retain their exact completed `NO_HIT` results.
- Every G/N checkpoint is immutable prefix evidence. The recovery child starts
  at that checkpoint's `next_m`, writes only to the sibling recovery tree, and
  searches through the original `range_end`.
- N14 remains `FAILED` in the original tree and in copied provenance. Its new
  child searches the explicit suffix; no failed summary is rewritten or
  passed to `--resume`.
- S04--S16 had no checkpoint and restart their exact original full P bands.
- At most 45 single-thread children run. Their absolute stop remains Unix
  `1784614650` (`2026-07-21T09:17:30+03:00`); the S relative limit is only the
  remaining time at launch.

## Fail-closed launch gates

Production execution is refused unless all of the following hold:

1. the original summary/state match only the recorded N14 atomic-replace
   anomaly and the 45/19 interrupted/completed signature;
2. the original supervisor and all recorded owned worker commands are absent;
3. the current manifest, engines, and verifiers have approved hashes;
4. the patched Gaussian Win32 concurrent reader/writer stress test passes;
5. all retained and prefix artifacts pass exact domain/counter validation;
6. the sibling recovery directory does not exist; and
7. the original deadline has not passed.

The original tree is hashed before execution and compared again at final
summary generation. Shutdown is restricted to recovery `Popen` roots and
process descendants captured with both PID and creation time. Every Windows
`taskkill /T` result is recorded; on failure the owned root is suspended, the
tree is re-snapshotted to stability, descendants are killed bottom-up, and the
root is killed last. A final result is refused unless every captured identity
and every root is independently absent. The old N14 stderr is provenance and
is never counted as new recovery stderr.

Recovery state publication uses a unique same-directory temporary file,
`fsync`, and `os.replace`. Windows errors 5, 32, and 33 receive at most 128
jittered retries; exhaustion fails closed and removes the temporary file. The
test suite covers first publication, a fixed exclusive lock, concurrent JSON
readers, persistent-lock exhaustion, and an owned child-grandchild shutdown.

Candidate acceptance requires the candidate matrix to equal the scalar
MSQ-D expansion. The scalar matrix verifier and independent compiled verifier
then check the same nine values again; all three checks must return zero and
emit `valid=true`.

## Commands

Read-only preflight (launches zero search workers):

```powershell
python .\recovery_supervisor.py
```

Bounded tests (dummy workers only):

```powershell
python -m unittest -v test_recovery_supervisor.py
```

Production entry point, for the root supervisor only after final audit:

```powershell
python .\recovery_supervisor.py --execute-recovery
```

The production entry reserves
`logs\tranche64-frozen-manifest-v1-recovery-v1`. Repeating it is refused.
