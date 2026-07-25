# Erdős 742 verifier A

`verifier_a.cpp` is an exhaustive C++ verifier for a raw graph certificate.
It does not consume a solver assignment or trust precomputed witnesses.

## Canonical input

Edge format:

```text
p edge N M
e U V
```

The edge rows must be strictly lexicographically sorted, with
`0 <= U < V < N`, and there must be exactly `M` rows.

Adjacency format:

```text
p adj N M
a 0 : <strictly increasing neighbors>
...
a N-1 : <strictly increasing neighbors>
```

All rows are mandatory and the adjacency relation must be symmetric. Blank
lines and full-line comments beginning with `#` or `c ` are ignored.

## Semantics

For the original graph and separately for every deleted edge, verifier A runs
BFS from every vertex. The ledger contains every unordered pair at distance
greater than two (or `INF`) after each deletion. Acceptance requires:

- the requested order (default 25);
- the requested edge threshold (default 157);
- original diameter exactly two; and
- at least one distance-greater-than-two witness for every edge deletion.

Exit code 0 means all requested conditions hold, 1 means a parsed graph was
rejected, and 2 means usage, parser, or ledger-I/O failure.

## Build and calibration

From this directory:

```powershell
g++ -std=c++20 -O2 -Wall -Wextra -Wpedantic verifier_a.cpp -o verifier_a.exe
g++ -std=c++20 -O2 -Wall -Wextra -Wpedantic make_fixtures.cpp -o make_fixtures.exe
.\make_fixtures.exe .\fixtures
.\calibrate_a.ps1
```

The calibration includes `K_12,13`, the same graph under the 157-edge target
threshold, the star `K_1,4`, `C5` in both supported formats, `K25` minus one
edge, two one-edge corruptions of `K_12,13`, a disconnected graph, and five
malformed certificates. It also checks complete deleted-edge and witness-row
coverage, parser agreement on `C5`, and explicit `INF` witnesses.
