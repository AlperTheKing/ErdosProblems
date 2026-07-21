# SN13 target harness V3 — independent final audit

Audit time: 2026-07-18T14:46:29+03:00

Verdict: PASS.

Canonical launcher audited:
engine/run_target44_offset100.ps1

Launcher SHA-256:
a025a57b86d53772ddd801e936231b1ede6dffadd711d545b37f63707107b224

No SorterHunter target process was started. The dry plan started zero
processes and created zero target-run directories. The monitor self-test used
three hidden PowerShell sleep processes only; all three were stopped and no
new process remained.

## Direct theorem bridge

The registry has all five required DIRECT ROUTE fields. A verified ordered
list of 44 comparators sorting every one of the 8,192 binary inputs proves
S(13) <= 44 by the zero-one principle. The independent lower-bound audit
establishes S(13) >= 35 + ceil(log2(392)) = 44. Therefore a V3 hit accepted by
the exhaustive gate closes the exact theorem S(13)=44.

The lower-bound report audited here is audit/LOWER44_AUDIT.md, SHA-256
acd355136e5d929484843d82d43ebdf1f58b9077b9092fcfd7d9185761bb12dd.

## Allocation and launch latch

| Check | Result |
|---|---|
| PowerShell parse errors | 0 |
| Dry-plan armed flag | false |
| Worker specifications | exactly 100 |
| Unique deterministic seeds | 100 |
| Unique log/config stems | 100 |
| Family allocation | 16,16,16,16,18,18 |
| Profile allocation | 25,25,25,25 |
| Extra cells | 4 |
| Prefix policy | PrefixType=0 for every rendered worker |
| SorterHunter processes before/after dry plan | 0 / 0 |
| Target directories before/after dry plan | 0 / 0 |

The production branch requires ConfirmRun, rejects any pre-existing
SorterHunter process, checks the count and seed uniqueness before launch,
checks the global process ceiling after every launch, and requires exactly
100 tracked runners after launch.

## Six seed fixtures

Each fixture contained exactly 45 bounded comparators. An independently
written scalar replay and the pinned C++ verifier both checked all 8,192
binary inputs.

| Fixture | SHA-256 | Scalar | C++ |
|---|---|---:|---:|
| n13_45_dobbelaere.net | 4ca03000a09042e6c6be79a9dc667176dfcf0056e37e2a2c3e28f8916703fc30 | 0/8192 | 0/8192 |
| n13_45_end13.net | fb65e2171ed8d696a261a29824b019dc410f86b7527c48739dc6d3bdf7f03698 | 0/8192 | 0/8192 |
| n13_45_senso13.net | 7299a538f2a9ec4d7380f1d2afa6aeba25fc44fdb62036ec3c5f4fa49f54696d | 0/8192 | 0/8192 |
| n13_seed131016_45.net | 2bf0aaba84a7488d7dcbe0c8883e8c0b7a817365b1631826adab063c81dfec72 | 0/8192 | 0/8192 |
| n13_45_low_avg_swaps.net | a133374d57e2b056b3574bffc734ff2306c8aa44f326bc32a779d851e63e9397 | 0/8192 | 0/8192 |
| n13_45_max32.net | 46ec4e448dbde975e94a7bc95a8e90d75a222399fda249b7e8eabadafde56aa6 | 0/8192 | 0/8192 |

The harness pins every fixture hash and reruns the exhaustive C++ check before
rendering workers.

## Adversarial detection tests

The append-only byte reader recovered one candidate line split across two
reads even when the completed half was followed by 600 decoy lines. The first
read exposed zero complete characters; the second consumed 18,848 bytes and
recovered exactly 44 pairs. This removes the former fixed-tail loss mode.

The strict candidate parser rejected all of these inputs:

- wrong N;
- a partial line;
- a malformed pair;
- 43 pairs;
- 45 pairs;
- an out-of-range channel;
- noncanonical separator whitespace.

A canonical N13/L44-shaped record with exactly 44 bounded pairs passed the
parser. The same record used the first 44 comparators of a known L45 sorter
and was deliberately not a sorter: the production path invoked the real
verifier, obtained exit 1 with 216 failing inputs, returned null, and did not
set a hit. Thus parsing alone cannot trigger success. In production,
Test-CandidateLine returns a candidate only after verifier exit zero; only
then does the monitor set target-hit and break to the global stop.

## Pins, deadline, and stop-all

The actual pinned values matched:

| Artifact | SHA-256 / commit |
|---|---|
| SorterHunter.exe | 4d0dd968d4252039451fe84e6b2fcd2595ee406d203b13d7551486ace8b26789 |
| verify_bitslice.exe | e67746909f6fad2dd3d33baa1259ed6988d894c22cbe1889db0a54bc48ced4b6 |
| sorterhunter_entry.cpp | 4565a76562ec87026651c175f85d4010c449cd63e9dc17adab43c0b738dabee4 |
| upstream SorterHunter | 392762f916688756242d90febced98ad157bc6d2 |

The fixed deadline is 2026-07-18T21:57:27+03:00. It is checked before
preflight, before every individual process launch, and before every log read.
Monitor sleeps are capped by the positive milliseconds remaining. Every exit
path passes through finally and invokes one batch Stop-AllRunners call. The
three-process stop test ended with live_processes_after_stop=0.

## Final decision

V3 satisfies the registered exact-100 ceiling, six-family fixture gate,
complete offset-based log capture, strict parser, verifier-before-hit rule,
pinned-artifact checks, fixed-deadline controls, and stop-all policy.

PASS authorizes only the registered run of this exact launcher and pinned
artifacts. It does not authorize either superseded 64-worker launcher or any
deadline extension.
