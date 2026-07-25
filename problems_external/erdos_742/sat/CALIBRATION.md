# Calibration record

Date: 2026-07-23 (Europe/Istanbul).

All core artifacts were compiled with:

```text
g++ 16.1.0
-std=c++20 -O2 -Wall -Wextra -pedantic
```

`calibrate.py` used PySAT's bundled `cadical195` only on fully pinned small
instances.  The exact results were:

```text
CALIBRATED c4 SAT=True vars=68 clauses=250
CALIBRATED c5 SAT=True vars=152 clauses=634
CALIBRATED k33 SAT=True vars=311 clauses=1435
CALIBRATED k4_minus_edge SAT=False vars=70 clauses=258
CALIBRATED k33_plus_chord SAT=False vars=317 clauses=1459
CALIBRATED k33_missing_edge SAT=False vars=304 clauses=1407
CALIBRATED verifier_reject k33_plus_chord: noncritical edge 0-1
CALIBRATED verifier_reject k33_missing_edge: diameter exceeds two
CALIBRATED verifier_reject asymmetric_matrix: matrix is not symmetric
CALIBRATION_PASS
```

`audit_exhaustive.py` compared SAT under a complete assignment to an
independent direct graph predicate for every labelled graph of orders 3
through 6, and for every possible minimum-edge threshold.  It checked 33,864
distinct graphs and 536,032 SAT queries:

```text
EXHAUSTIVE_AUDIT_PASS orders=3..6 distinct_graphs=33864 sat_queries=536032
```

The target-order boundary audit additionally established:

```text
TARGET_BOUNDARY_AUDIT K12,13 at threshold 156 SAT=True
TARGET_BOUNDARY_AUDIT K12,13 at threshold 157 SAT=False
TARGET_BOUNDARY_AUDIT K12,13 plus one chord at threshold 157 SAT=False
TARGET_BOUNDARY_VERIFIER_PASS K12,13 accepted; chord mutant rejected
TARGET_BOUNDARY_AUDIT_PASS
```

The chord mutant has 157 edges and diameter two, but its added intra-part
edge is noncritical.  Thus it tests the criticality clauses precisely at the
production threshold rather than failing only the edge counter.

The production formula was generated but not solved:

```text
n=25 min_edges=157 vars=56156 clauses=513220
bytes=9667767
SHA256(d2c_n25_m157.cnf)=69268EE40EC01B17A039BBA3C33F0067AE53E574A887223FDCA4B7F385CC0E4F
SHA256(generate_d2c_cnf.cpp)=F6BD0191E6A398F4051E5025E093DAF1798B1ADBBF6750C98365C54862CD5485
SHA256(generate_d2c_cnf.exe)=FC0A2E0174528A65D2D6D225C50D689AFEAAC62EA2AE40E8826454A1EFE82B8F
SHA256(verify_b.cpp)=86547797A80B2BB38106E1977C1D3AC5AA04CB1572824A93955253CF3685C06F
SHA256(verify_b.exe)=5144935EDAD0FC7C66F075C7881AE242A6937125F7D7A9847EA2F3AB791C4C70
```

The earlier short labels `SHA256(generator)` and `SHA256(verifier-B)`
referred to the compiled `.exe` files, not to the `.cpp` sources.  The
apparent source-hash disagreement was therefore a label ambiguity, not
generator drift.  Before freezing, `verify_b.cpp` received one
semantics-neutral hardening edit: an explicit `#include <tuple>` replaced
reliance on a transitive standard-library include.  Its executable was
rebuilt, all three calibration suites were replayed, and the new source and
binary hashes above supersede the earlier verifier binary hash.

`SHA256SUMS.txt` is the frozen manifest for the formula, map, sources,
executables, audit scripts, encoding proof, and build instructions.


No production search, portfolio, or long-running solver was launched.
