# Canonical unrestricted order-19 native launcher audit

Status: **PRODUCTION-READY LAUNCHER; PRODUCTION NOT LAUNCHED**.

This is the canonical final launcher record and supersedes preliminary launcher
hashes in `UNRESTRICTED19_LAUNCHER_AUDIT.md`.  It certifies process containment,
hash pinning, calibration gates, result replay, and exact run semantics.  It
does not turn a bounded search failure into a proof and does not itself certify
the mathematical search heuristic.

## 1. Frozen source and deterministic executable

The engine author froze this exact source identity:

- `engine/unrestricted19_stochastic.cpp`;
- 57,009 bytes;
- SHA-256 `625AAEEE1169ED484A337E18F3DBB9A5DE214A8A45F6F47822494E0BB8CE1906`.

Default MinGW PE builds were found not to be byte-reproducible because their
linker timestamp changed.  The production candidate was therefore built twice
with timestamp insertion disabled:

```text
C:\msys64\mingw64\bin\g++.exe -std=c++20 -O3 -march=native -DNDEBUG -Wall -Wextra -Wpedantic -pthread -Wl,--no-insert-timestamp engine/unrestricted19_stochastic.cpp -o engine/unrestricted19_stochastic.exe
```

Compiler: MSYS2 `g++ 16.1.0`.

Both independent rebuild paths produced the same 275,422-byte executable:

- `engine/unrestricted19_stochastic.exe`;
- `engine/unrestricted19_stochastic.deterministic-rebuild.exe`;
- common SHA-256
  `D0171F7E8E790A1DE5520CA18853C9F29A453D4D23F7227334BDA06283E321AF`.

The frozen source hash agreed before and after both builds.

## 2. Frozen launcher and verifier identities

- `engine/run_unrestricted19_stochastic.ps1`:
  `238824EF7A8A4B0B978D836FADC832731C6BA63B2CED8D09F249A9691D473537`;
- `engine/verify_scalar.py`:
  `71B9C070AEDAA563A16A4FD6B3BE5334C87B6AA3F876679DEB8C5D223A2EB443`;
- `engine/verify_bitset.exe`:
  `E6683BEA5B835B5BFD78464DAB21BA2EBEF0436218C468AF1A5EE933BAB439EC`.

The launcher validates all four expected SHA-256 values before creating a run
directory.  Its thread parameter is restricted to `1..64`.  Outside explicit
test mode, the production search duration is not configurable: it is exactly
28,800 wall seconds.

## 3. Exact process and output contract

Preflight invokes:

```text
ENGINE --self-test --seed SEED
ENGINE --threads 1 --seconds CANARY_SECONDS --seed SEED+1 --output-dir CANARY_DIR
```

Self-test acceptance requires exit zero, empty stderr, and a final JSON line
with `status=SELF_TEST_PASS`, `production_run=false`, and `failures=0`.
Canary acceptance requires exit zero, empty stderr, no candidate, and an atomic
native `summary.json` with `status=NO_HIT` and `threads=1`.

The canary engine request remains exactly the configured number of seconds.
The outer canary deadline has a 60-second process-scheduling allowance because
an authenticated two-second canary was observed to miss a four-second outer
deadline while the 128-thread host was saturated.  This allowance affects only
preflight scheduling; it does not extend the 28,800-second production wall
deadline.

Production invokes a hidden process with:

```text
ENGINE --threads THREADS --seconds 28800 --seed SEED --output-dir SEARCH_DIR
```

The outer production deadline begins before process creation.  At the deadline
the process is forcibly stopped and the result is only
`NO_HIT_HARD_DEADLINE`, never `UNSAT`.

The wrapper polls atomic `hit_candidate.json` creation every 100 ms.  First
appearance stops the native process.  The unchanged candidate bytes are hashed,
replayed through the Python scalar verifier and independently compiled C++
bitset verifier, and hashed again.  Only two exit-zero, empty-stderr ledgers
whose status is exactly `VERIFIED_COUNTEREXAMPLE`, with equal before/after
candidate hashes, set `independently_verified=true`.  Any split is
`VERIFIER_DISAGREEMENT`; two parser rejections are `INVALID_HIT_CANDIDATE`.

Run directories are created under a unique staging name and renamed into
place.  Every wrapper `state.json` and `summary.json` replacement uses a unique
same-directory temporary and atomic rename.  Live state records wrapper PID,
native PID, phase, deadline, exact paths, and all authenticated hashes.

## 4. Isolated adversarial suite: 7/7

The canonical suite is
`engine/tests/test_unrestricted19_launcher_isolated.ps1`, SHA-256
`DD674E892EB1B21B8F6B0326A0B94A9A2E18BD37550C3EC09FCF7C757FDF6284`.
It copies every fake source/verifier into a PID-specific build directory and
compiles a uniquely named private executable, eliminating the shared-fake hash
race observed between independent referees.

Canonical private build directory:

```text
engine/tests/launcher-audit-build-20260721T184742709-74576
```

Private identities:

- copied fake engine source:
  `507705E4157DFD6C96EDFA4B290899BCC8049D9B122D5A96CDE5812FBCEFCBDC`;
- private fake executable:
  `F3AFB5B481C53E1408430FBBCF3E4B678CC831E7F48777317EC8610D8FEE9EC4`;
- copied fake scalar acceptor:
  `2942D7258B5D896982CC02BFC739A338040439129A5C882B464205D9B6637A07`.

The output was:

```text
PASS unrestricted19 isolated launcher adversarial cases=7
```

The canonical run prefix is
`engine/logs/launcher-isolated-audit-20260721T184742709-74576-*`.
The seven asserted outcomes were:

1. bad executable hash: exit 1 and no run directory;
2. nonzero self-test: `SELF_TEST_FAILED`, no search;
3. canary overrun: `CANARY_TIMEOUT`, no production;
4. partial candidate: both real parsers rejected it,
   `INVALID_HIT_CANDIDATE`;
5. fake scalar acceptance versus fake bitset rejection:
   `VERIFIER_DISAGREEMENT`;
6. production overrun: process stopped at the test wall deadline,
   `NO_HIT_HARD_DEADLINE`;
7. all gates with `-AuditOnly`: `AUDIT_PASS_NO_PRODUCTION`.

All six created final summaries had `independently_verified=false`, their final
state status agreed with their summary status, and no atomic JSON temporary was
left.  The bad-hash case correctly created no directory.

## 5. Exact frozen AuditOnly gate

Canonical run directory:

```text
engine/logs/unrestricted19-native-frozen-audit-20260721T185100590-66520
```

Invocation:

```powershell
pwsh -NoProfile -File engine/run_unrestricted19_stochastic.ps1 `
  -Source engine/unrestricted19_stochastic.cpp `
  -Engine engine/unrestricted19_stochastic.exe `
  -RunDir engine/logs/unrestricted19-native-frozen-audit-20260721T185100590-66520 `
  -ExpectedSourceSha256 625AAEEE1169ED484A337E18F3DBB9A5DE214A8A45F6F47822494E0BB8CE1906 `
  -ExpectedEngineSha256 D0171F7E8E790A1DE5520CA18853C9F29A453D4D23F7227334BDA06283E321AF `
  -Threads 64 -CanarySeconds 2 -Seed 2026072101 -AuditOnly
```

Final wrapper status was `AUDIT_PASS_NO_PRODUCTION`; elapsed wall time was
871.848 seconds.  `summary.json` and final `state.json` are byte-identical,
each with SHA-256
`5EC00E787768C6C521737C21D3BF60A544CF69B2A4035AEA2B29D25AAF5973CD`.

The exact frozen executable self-test had exit code zero, 922 stdout bytes,
zero stderr bytes, and SHA-256
`A6AC822DA355F16F1E71F9A68BDB2AB686201FA8C0AFAE80A46C03F49270C2D1`.
It reported:

- all 59,809 labelled oriented/missing graphs through order five;
- 100,000 arbitrary mutation/revert pairs;
- 100,000 fixed-missing-count mutation/revert pairs over all positive values
  `q=1..19`;
- 500,000 bitset-versus-scalar oracle checks;
- all six ordered trit transitions;
- malformed loop, digon, and out-of-range-bit rejections;
- zero failures.

The exact one-thread, two-second canary had exit code zero and zero stderr
bytes.  Native summary SHA-256:
`10C4D1A934A1B85C24284BEE831C6E120914511FB2EFACAB502A0B4A3FB1BF0D`.
It recorded 156,289 evaluations, minimum outdegree eight, both counter
partitions true, no candidate, and status `NO_HIT`.  This two-second result is
only a calibration outcome.

After completion, all owned wrapper/self-test/canary/command PIDs
`66520, 36832, 5100, 68884` were closed.  No private fake-engine process from
the isolated build directory remained.  No unrelated KTT or referee process
was changed.

## 6. Production launch form

The launcher is ready for a separately authorized production run using a new,
nonexistent child of `engine/logs`, the exact frozen identities above, a fixed
recorded seed, and `-Threads 64`.  The production call must omit `-TestMode` and
`-AuditOnly`.  This audit did not start that run and makes no claim about the
existence or nonexistence of an SSNC counterexample.
