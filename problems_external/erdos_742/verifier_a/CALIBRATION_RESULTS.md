# Verifier A calibration results

Date: 2026-07-23

Compilers:

- `g++.exe (Rev5, Built by MSYS2 project) 16.1.0`
- `clang version 22.1.4`

Commands executed from this directory:

```powershell
g++ -std=c++20 -O2 -Wall -Wextra -Wpedantic verifier_a.cpp -o verifier_a.exe
g++ -std=c++20 -O2 -Wall -Wextra -Wpedantic make_fixtures.cpp -o make_fixtures.exe
.\make_fixtures.exe .\fixtures
.\calibrate_a.ps1
clang++ -std=c++20 -O2 -Wall -Wextra -Wpedantic verifier_a.cpp -o verifier_a_clang.exe
.\verifier_a_clang.exe .\fixtures\k12_13.edge --expect-n 25 --min-edges 156 --ledger .\calibration_ledgers\k12_13_clang.ledger
```

Observed result:

```text
FIXTURES_A_OK directory=.\fixtures count=13

case                            exit checks
k12_13_structural                  0      4
k12_13_target_threshold            1      3
star_disconnecting_deletions       0      4
c5_edge                            0      4
c5_adjacency                       0      4
dense_noncritical                  1      4
corrupted_positive_plus_edge       1      4
corrupted_positive_missing_edge    1      3
disconnected_infinite_distance     1      4
parser_duplicate                   2      2
parser_loop                        2      2
parser_reversed                    2      2
parser_count                       2      2
parser_asymmetry                   2      2

CALIBRATION_A_OK cases=14 ledger_checks=9
```

The `K_12,13` ledger has exactly 156 deleted-edge rows and 156 witness
rows. Every deleted edge has exactly its endpoints as one distance-3
witness. The dense noncritical graph has 299 deleted-edge rows and zero
witness rows. Every deletion in `K_1,4` is recorded with diameter `INF`.
The edge-list and adjacency-list parses of `C5` produce identical ledgers.

SHA-256:

```text
0A9B974E37DCFBF596510D50F3943744BF6989CF23DAE0CD7A0120F017AB6921  verifier_a.cpp
01F58CDFA2E5282146E1BA16DA406CA4DB578CA7C8612884A6375025B6668D86  verifier_a.exe
0F2226092FDFD07DA98D0DB5751E0AA011DF2B51E20C7834E80B2C027119CD9E  verifier_a_clang.exe
C2BBBD4516F751C32A6F84E28D3A62EDED2633A9BCCD53D872D42D2D59DF9509  make_fixtures.cpp
B9CEE8420ADF7F39AE25EC3DD1A041369DF037BCBA5AAC865EE7AC6D7FD5A130  make_fixtures.exe
A9D41F4CE89C1648D1D07E50E187683606B8A6BEDFA0ECB67B1297AC621F5F86  calibrate_a.ps1
738A231FE9C60DBDECD03BC7836688D140E3A8C952EF442DEC6F0658D8C7B658  k12_13_structural.ledger
738A231FE9C60DBDECD03BC7836688D140E3A8C952EF442DEC6F0658D8C7B658  k12_13_clang.ledger
```
