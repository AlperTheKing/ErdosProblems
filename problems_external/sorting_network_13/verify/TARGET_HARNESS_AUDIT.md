# SN13 target harness referee audit

Audit time: 2026-07-18T14:22:00+03:00

Verdict: FAIL — do not launch this revision.

No target search was launched. The only harness execution was the unarmed dry
plan, which started no SorterHunter process and created no target run
directory.

## Scope

Reviewed artifacts:

- engine/run_target44_64.ps1
- engine/TARGET44_PLAN.md
- engine/sorterhunter_entry.cpp
- engine/build_target.ps1
- the four N13L45 seed fixtures named by the harness
- the upstream configuration and mutation handling in SorterHunter.cpp

PowerShell parsed run_target44_64.ps1 with zero syntax errors. The reviewed
harness SHA-256 was
8c670de0fe06e0701c76049516074609a76f99bd99e1fa8a7f2463d250b6016e.

## Findings

| Requirement | Result | Evidence |
|---|---|---|
| At most 64 workers | PASS | The dry plan produced exactly 64 specifications; the allocation was 16,16,16,16. Seeds were unique. Guards require 64 specifications and 64 launched runners and reject more than 64 SorterHunter processes. |
| Four verified L45 families | PASS | Dobbelaere, END13, SENSO13, and cal131016 each contain 45 comparators. An independent scalar replay and the C++ verifier each tested all 8,192 inputs with zero failures for every family. All four actual SHA-256 values equal the pinned harness values. |
| Nondegenerate mutation profiles | PASS | There are four distinct profiles and four replicates per family/profile cell. Their mutation-weight sums are 6, 9, 8, and 12; each enables five or six mutation types. Escape, uphill, maximum-mutation, and restart settings differ. SorterHunter.cpp reads every rendered key. |
| Unarmed invocation | PASS | Process IDs before and after the dry plan were both empty; target44 run-directory counts were both zero. The dry plan reported armed=false and returned before preflight, directory creation, or Start-Process. |
| Stdout buffering | PASS for reviewed source | sorterhunter_entry.cpp sets stdout to unbuffered before calling the upstream main. The current executable timestamp follows the wrapper source timestamp. The harness does not pin the executable hash, so this property is not protected against a stale or replaced binary. |
| Absolute 21:57:27+03 deadline | FAIL | The deadline is checked once before fixture preflight and the sequential 64-process launch, not before every launch. The monitoring loop always sleeps 1,000 ms; entering it 1 ms before the deadline permits the next check 999 ms after the deadline. |
| Stop all on the first L44 | FAIL as an end-to-end property | The finally block does stop all tracked runners after hitEvidence is set, but hit detection can miss a real line or trigger on an incomplete/non-target line as described below. |
| High-volume log detection | FAIL | Each one-second poll examines only the last 256 lines and keeps no per-file offset. A synthetic 600-line stream with the L44 line at index 100 and more than 256 later lines produced TailDetects=false. Such a line is lost permanently. |
| Complete-certificate detection | FAIL | The pattern tests only the literal fragment 'L':44 followed by comma or brace. It matched both an incomplete header and a wrong-N garbage string in the referee test. With unbuffered stdout, the header is written before printnw finishes the 44 pairs, so the controller can kill the producer while the certificate line is partial. |
| No false target | FAIL | On a text match the harness immediately sets target_found, stops all workers, and saves the raw line. It does not require N=13, parse exactly 44 bounded pairs, require the closing network syntax, or run an exhaustive verifier on the emitted candidate. The verifier is used only for the four initial fixtures. |

## Fixture evidence

| Fixture | SHA-256 | Scalar failures | C++ failures |
|---|---|---:|---:|
| n13_45_dobbelaere.net | 4ca03000a09042e6c6be79a9dc667176dfcf0056e37e2a2c3e28f8916703fc30 | 0/8192 | 0/8192 |
| n13_45_end13.net | fb65e2171ed8d696a261a29824b019dc410f86b7527c48739dc6d3bdf7f03698 | 0/8192 | 0/8192 |
| n13_45_senso13.net | 7299a538f2a9ec4d7380f1d2afa6aeba25fc44fdb62036ec3c5f4fa49f54696d | 0/8192 | 0/8192 |
| n13_seed131016_45.net | 2bf0aaba84a7488d7dcbe0c8883e8c0b7a817365b1631826adab063c81dfec72 | 0/8192 | 0/8192 |

## Required changes before PASS

1. Track a persistent byte or line offset for every stdout file and inspect all
   newly appended complete lines. Do not use a fixed tail window.
2. Treat a hit as pending until a complete N13/L44 record is available. Parse
   exactly 44 ordered comparator pairs, enforce 0 <= low < high < 13, serialize
   a canonical candidate, and require the exhaustive verifier to return zero.
   Only a verified candidate may set target_found and trigger global success.
3. Recheck the absolute deadline before every Start-Process. In the monitor,
   cap every wait by the positive time remaining and stop all workers at or
   before the registered deadline.
4. Pin the target executable SHA-256, or build and hash it as part of a
   recorded preflight, so the unbuffered wrapper cannot silently be replaced.

Until items 1–3 are implemented and re-audited, the harness does not satisfy
the registered target-run safety contract.
