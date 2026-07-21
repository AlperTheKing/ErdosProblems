# Frozen 64-lane tranche harness

`tranche_supervisor.py` is the production supervisor for the single eight-hour
tranche declared in `../LANE_MANIFEST.md`. It starts no process unless the
frozen manifest hash and all three search engines plus both exact verifiers are
present. A successful preflight starts exactly 64 search processes: 16 G, 16
E, 16 N, and 16 S. Every search process is single-threaded. Thread-pool
environment variables are also fixed to one.

The common deadline is one absolute Unix time. It is passed directly to both
Gaussian families and enforced by the supervisor for every owned process.
The E and S engines retain their internal 28,800-second ceilings, but the
supervisor's common absolute stop is authoritative.

Each canonical run directory is created atomically and may not already exist.
It contains:

- `RUN_ONCE.json`, which records the non-resumable run reservation;
- `portfolio_state.json`, an atomically replaced live state containing all
  owned PIDs and commands;
- `portfolio_summary.json`, the atomically replaced final portfolio result;
- `lanes/<ID>/process.stdout.txt` and `process.stderr.txt`; and
- each engine's own summaries, checkpoints, and verification artifacts.

The supervisor stops all still-live owned process trees on the first retained
dual-verifier hit or at the common deadline. It also stops with `FAILED` on a
nonempty lane stderr stream, a failed engine status, an absent completed-lane
summary, or an unrecognized result. It does not enumerate or stop unrelated
processes.

Portfolio results are limited to:

- `HIT_VERIFIED`;
- `NO_HIT_DECLARED_DOMAINS`, only if all 64 finite domains exhaust;
- `TIMEOUT_INCOMPLETE`;
- `INTERRUPTED`; or
- `FAILED` / `FAILED_PREFLIGHT`.

Every state and summary sets `proof_claim` to false. In particular, no-hit and
timeout results concern only the finite manifest domains and are not an
impossibility proof.

Production launch is deliberately explicit and hidden:

```powershell
.\run_tranche.ps1 -Launch
```

The launcher uses the single fixed canonical directory
`logs/tranche64-frozen-manifest-v1` and prints the supervisor PID and path.
Running the wrapper or Python supervisor after that directory exists is
rejected; the production harness does not resume, overwrite, or rerun the
frozen tranche.

The process-level self-test uses 64 deterministic dummy workers and performs
three cases: complete finite exhaustion, a dual-verifier-shaped hit that stops
the remaining owned workers, and a common-deadline stop. It launches no search
engine:

```powershell
python -m unittest -v test_tranche_supervisor.py
```

Self-test artifacts are retained under `calibration/harness_selftest/`.
