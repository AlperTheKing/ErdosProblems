# Small-order calibration for Erdős 156

This file records only bounded calibration data.  It is not evidence for the
asymptotic statement.

## Engine

- Source: `small_maximal_search.cpp`
- Source SHA-256:
  `404D35AD74C3C7904FED6A865A1906F366D3A98165541678E5713237799C93CF`
- Executable SHA-256:
  `8C9E0D91B945525B3037FE0157D46DBAA1C8A5AC9851B322A1F3D52B428E8FB9`
- Compiler: MinGW-w64 `g++ -O3 -std=c++20 -pthread`
- Threads: 4

The engine enumerates \(k\)-subsets, rejects repeated positive differences,
and then checks every omitted point by independently rebuilding all new
differences.

## Runs

| \(N\) | \(k\) | result | witness / leaves |
|---:|---:|:---|:---|
| 10 | 3 | HIT | `{2,5,6}` |
| 22 | 4 | HIT | `{4,7,12,13}` |
| 42 | 5 | HIT | `{10,18,19,25,30}`; 349413 leaves before hit |
| 43 | 5 | NO_HIT | 490164 Sidon leaves exhausted |
| 72 | 6 | NO_HIT | 60083562 Sidon leaves exhausted |

The \(N=42\) witness agrees with one of the two witnesses listed independently
in OEIS A382396.  The \(N=43\) transition agrees with OEIS A382397.  The
\(N=72,k=6\) result is a bounded exclusion only and does not justify any
formula for the transition points.

## Independent witness replay

- Pair-sum verifier source SHA-256: `24C88082FA22A2B13DDC3B8BD6C037C4C5B481D8440BFEECA336E8D470165CFE`
- Executable SHA-256: `D5824EBC45AFFEE1D023B6C56FBC2F4AA38DF88ED4F1355168BF0F3E1ADB7976`
- Results: `VERIFIED` for the witnesses at N=10, 22, and 42.

This verifier reconstructs unordered pair sums for every attempted extension and shares no difference-bitset logic with the search engine.
