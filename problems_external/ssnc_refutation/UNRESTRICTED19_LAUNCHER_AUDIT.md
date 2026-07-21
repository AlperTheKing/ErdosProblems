# Unrestricted order-19 native launcher audit

Status: **LAUNCHER ACCEPTED; PRODUCTION NOT LAUNCHED**.

This audit concerns only the Windows process wrapper and its black-box launch
contract.  It does not certify the search heuristic as mathematically complete,
and a bounded `NO_HIT` remains only a bounded heuristic failure.

## Immutable artifacts exercised

The following exact candidate build was compiled with MSYS2 `g++ 16.1.0` using

```text
g++ -std=c++20 -O3 -march=native -DNDEBUG -Wall -Wextra -Wpedantic -pthread unrestricted19_stochastic.cpp -o unrestricted19_stochastic.audit.exe
```

- native source: `engine/unrestricted19_stochastic.cpp`, SHA-256
  `625AAEEE1169ED484A337E18F3DBB9A5DE214A8A45F6F47822494E0BB8CE1906`;
- candidate executable: `engine/unrestricted19_stochastic.audit.exe`, SHA-256
  `01D998E9DFDD50184BCFE046FF40BCA0BFA04F56AED5499D54EEBF6BB60EE551`;
- launcher: `engine/run_unrestricted19_stochastic.ps1`, SHA-256
  `8B6937A75AE5692D8B4B533DC55BAA38F5C9DDB17D31DD10CB9E555E88079F93`;
- scalar verifier: `engine/verify_scalar.py`, SHA-256
  `71B9C070AEDAA563A16A4FD6B3BE5334C87B6AA3F876679DEB8C5D223A2EB443`;
- bitset verifier: `engine/verify_bitset.exe`, SHA-256
  `E6683BEA5B835B5BFD78464DAB21BA2EBEF0436218C468AF1A5EE933BAB439EC`.

The source hash was measured before and after compilation and agreed.  These
hashes authenticate the candidate audited here; they are not a declaration by
the engine author that the source will never change.  Any later byte change
requires a new executable hash and repetition of this gate.

## Exact engine CLI and file contract

The launcher invokes exactly these two modes:

```text
ENGINE --self-test --seed SEED
ENGINE --threads T --seconds S --seed SEED --output-dir DIR
```

The first command must exit zero, write nothing to stderr, and end stdout with
a JSON object satisfying all of

```text
status == SELF_TEST_PASS
production_run == false
failures == 0
```

The one-thread canary uses `T=1`.  It must exit zero, write nothing to stderr,
leave no candidate, and atomically write `DIR/summary.json` with
`status == NO_HIT` and `threads == 1`.  Only then can production be considered.

The production command is hard-coded to an eight-hour wall budget of 28,800
seconds unless the explicit internal `-TestMode` switch is present.  The wrapper
accepts only `1 <= T <= 64`; the intended production value is 64.  The wall
deadline begins before native process creation, and the wrapper forcibly stops
the native process at that deadline.  Production is launched with a hidden
window.

The native engine must atomically create `DIR/hit_candidate.json` with exactly
the legacy certificate keys `n` and `out_neighbors`.  The wrapper polls for the
file every 100 ms.  First appearance stops the search process.  It hashes the
unchanged bytes, invokes the Python scalar verifier and independently compiled
C++ bitset verifier, and hashes the bytes again.  Only two exit-zero ledgers
whose status is exactly `VERIFIED_COUNTEREXAMPLE`, with empty stderr and equal
before/after candidate hashes, produce wrapper status
`VERIFIED_COUNTEREXAMPLE` and `independently_verified=true`.

Any verifier split produces `VERIFIER_DISAGREEMENT`.  Two parser rejections
produce `INVALID_HIT_CANDIDATE`.  Neither status is a mathematical result.

## Windows and artifact safety properties

- Source, executable, and both verifier hashes are accepted before any run
  directory is created.
- The run directory is first built under a unique staging name with an initial
  state, then renamed to its canonical path.
- Every `state.json` and `summary.json` update uses a unique same-directory
  temporary followed by an atomic rename.
- Each native phase records its PID, phase, absolute deadline, stdout and stderr
  paths, exit/reason, and byte counts.
- Nonempty stderr stops the active native phase and prevents a verified status.
- A nonzero/malformed self-test or failed canary prevents production.
- A hard-deadline run with no accepted hit is recorded as
  `NO_HIT_HARD_DEADLINE`, never `UNSAT`.

## Adversarial launcher suite

The test source, script, and final fake executable hashes were:

- `engine/tests/launcher_fake_engine.cpp`:
  `3B0C2B851C49C78AE3EDF7C11F932EE08982A24B6E28958FF700B23E07922164`;
- `engine/tests/launcher_fake_engine.exe`:
  `3F21AB717C4EFC9E055EED6ADEE02A51B6FDAAB97DCBCDB1A507D821671D8E2C`;
- `engine/tests/launcher_fake_scalar_accept.py`:
  `2942D7258B5D896982CC02BFC739A338040439129A5C882B464205D9B6637A07`;
- `engine/tests/test_unrestricted19_launcher.ps1`:
  `B510C35D5CA7D27A21A73B17BA42355E3FCCDBFF8DF26632A69BF447030011F9`.

The canonical final test group is
`engine/logs/launcher-audit-20260721T181355676-*`.  All seven cases passed:

| injected condition | required result |
|---|---|
| bad executable hash | exit 1; no run directory |
| nonzero self-test | `SELF_TEST_FAILED`; no canary/search |
| one-thread overrun | `CANARY_TIMEOUT`; no production |
| partial raw candidate | two real parsers reject; `INVALID_HIT_CANDIDATE` |
| fake accept versus fake reject | `VERIFIER_DISAGREEMENT` |
| production wall overrun | process stopped; `NO_HIT_HARD_DEADLINE` |
| all gates with `-AuditOnly` | `AUDIT_PASS_NO_PRODUCTION` |

No case set `independently_verified=true`, and no atomic JSON temporary was
left in any final case directory.

## Native black-box calibration through the launcher

The nonproduction run directory is
`engine/logs/unrestricted19-native-audit-20260721T181523755`.
Its final wrapper summary has SHA-256
`6979EB1542E0517077156F894BD9EFD75535F8E87D63CA6F429BAD50F432F790`
and status `AUDIT_PASS_NO_PRODUCTION`.

The full native self-test used the exact build above and reported:

- all 59,809 oriented/missing labelled graphs through order five;
- 100,000 arbitrary mutation/revert pairs;
- 100,000 fixed-missing-count mutation/revert pairs over all 19 positive
  missing counts;
- 500,000 independent scalar-oracle comparisons;
- all six directed trit transitions;
- three malformed-state rejections;
- zero failures and zero stderr bytes.

The self-test JSON SHA-256 is
`A6AC822DA355F16F1E71F9A68BDB2AB686201FA8C0AFAE80A46C03F49270C2D1`.

The required one-thread, two-second canary completed 185,157 evaluations with
both counter partitions true, zero stderr bytes, and status `NO_HIT`.  Its
native summary SHA-256 is
`A4746740284150EFB11C84FC017729040E3C27B8882084B2BAB5AA215EB9DEC3`.
This `NO_HIT` is only a canary result.

## Exact production invocation contract

After a separate independent engine audit declares the same source/executable
pair frozen, a canonical production call has the following shape (with a new,
nonexistent child of `engine/logs` and a separately chosen fixed seed):

```powershell
pwsh -NoProfile -File engine/run_unrestricted19_stochastic.ps1 `
  -Source engine/unrestricted19_stochastic.cpp `
  -Engine engine/unrestricted19_stochastic.audit.exe `
  -RunDir engine/logs/unrestricted19-native-<UTCSTAMP> `
  -ExpectedSourceSha256 625AAEEE1169ED484A337E18F3DBB9A5DE214A8A45F6F47822494E0BB8CE1906 `
  -ExpectedEngineSha256 01D998E9DFDD50184BCFE046FF40BCA0BFA04F56AED5499D54EEBF6BB60EE551 `
  -ExpectedScalarSha256 71B9C070AEDAA563A16A4FD6B3BE5334C87B6AA3F876679DEB8C5D223A2EB443 `
  -ExpectedBitsetSha256 E6683BEA5B835B5BFD78464DAB21BA2EBEF0436218C468AF1A5EE933BAB439EC `
  -Threads 64 -CanarySeconds 5 -Seed <FIXED_UINT64>
```

Do not add `-TestMode` or `-AuditOnly` to production.  The launcher then fixes
the production wall budget at exactly 28,800 seconds.  This audit did not run
that command and does not authorize it until the separate engine audit and
source-freeze check pass.
