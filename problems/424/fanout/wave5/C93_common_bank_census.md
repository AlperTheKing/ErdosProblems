# C93 exact common-bank census

## Scope and finite verdict

This lane supplies finite exact evidence only.  It does not prove a uniform
counting lemma.

Every event cutoff through

```text
X = 1,000,000,000
```

was scanned exactly.  No event satisfies `6 D(X) < 5 A_H(X)`, and no event
satisfies `D(X) / A_H(X) <= 3/4`.  The exact minimum over all events with
`A_H(X)>0` is

```text
D(X) / A_H(X) = 5/6 at X = 186.
```

Thus the strict inequality `6D<5A_H` has no falsifier in the scanned range;
equality occurs at `X=186`.

## Definitions implemented

The allowed values are `n>=2` with `n mod 3 != 1`.  For an allowed `n`, an
admissible pair is `2<=a<b`, `ab=n+1`, with both factors allowed.  Generated
values are the ascending closure of the seeds `{2,3}`.

For an even root `r`, put `U(r)=2r-1` and let `top_X(r)` be the largest member
of its `U`-chain not exceeding `X`.

* `A_H(X)` counts hard even roots `r<=X` for which `top_X(r)` is not generated.
* `D(X)` counts structural splitless even roots `r<=X` for which `top_X(r)` is
  generated.

The fast counter records exactly three event types: a hard-root birth, the
first generated member of a hard-root chain, and the first generated member
of a structural-splitless-root chain.  Between these events both `A_H` and `D`
are constant, so checking every event checks every possible value of their
ratio.

If an odd generated value `x>3` has hole parent `(x+1)/2`, then it is the
first generated member of one seed-2 chain.  Its even root is exactly

```text
r = ((x-1) >> v_2(x-1)) + 1.
```

If `r` is structural splitless, this event increments `D`.  Consequently the
simple exact identity is

```text
D(X) = E_even(X) - U_E(X),
```

where `E_even(X)` counts structural splitless even roots and `U_E(X)` counts
those whose visible seed-2 chain is still entirely ungenerated.  C71 prints
the first count (as `E`) but not `U_E`; the new chain-healing counter is
therefore required.

## Exact census

| X | events | A_H(X) | D(X) | minimum D/A_H through X |
|---:|---:|---:|---:|---:|
| 10,000 | 1,019 | 391 | 374 | 5/6 at 186 |
| 200,000 | 22,256 | 6,348 | 8,730 | 5/6 at 186 |
| 1,000,000 | 108,381 | 27,056 | 44,271 | 5/6 at 186 |
| 100,000,000 | 9,185,868 | 1,794,586 | 4,243,002 | 5/6 at 186 |
| 1,000,000,000 | 83,822,920 | 15,106,735 | 40,909,363 | 5/6 at 186 |

At `X=10^9` there are `83,822,919` events with positive demand.  The exact
counts of `6D<5A_H` and `4D<=3A_H` events are both zero; both first-failure
fields are null.

The `10^9` core allocation was `2,000,000,003` bytes and the run used one CPU
thread.  The two full runs took 40.123 and 39.434 seconds.

## C87 definition regression

The independent verifier reconstructed the literal endpoint sets and matched
the saved C87 `hard_roots` and `common_neighbors` lists, not merely their
sizes.

| cutoff | C87 A_H | C87 D | set comparison |
|---:|---:|---:|:---|
| 54 | 1 | 1 | exact |
| 74 | 2 | 2 | exact |
| 186 | 6 | 5 | exact |
| 362 | 11 | 10 | exact |
| 1,000 | 34 | 34 | exact |
| 2,000 | 83 | 72 | exact |
| 5,000 | 196 | 186 | exact |
| 10,000 | 391 | 374 | exact |

The Python verifier additionally recomputed the endpoint definitions directly
from every even root and `top_X(root)` through `X=10^6`; these static counts
equaled the incremental counters.

## C71 counter comparison

The C93 classifier independently reproduced C71's `A_H`, `K`, `E`, and full
classification digest at `2*10^5`, `10^8`, and `10^9`.  The natural existing
C71 aggregates are not equal to `D`:

| X | D | E | e_plus | E-e_plus | hard deaths |
|---:|---:|---:|---:|---:|---:|
| 200,000 | 8,730 | 23,151 | 11,223 | 11,928 | 3,589 |
| 100,000,000 | 4,243,002 | 9,395,726 | 4,606,216 | 4,789,510 | 1,574,140 |
| 1,000,000,000 | 40,909,363 | 88,550,127 | 43,510,606 | 45,039,521 | 13,903,411 |

No expression for `D` using only the printed C71 aggregates was found.  The
exact additional state needed is `U_E`, the number of still-unhealed
structural splitless chains.

## Independent verification

Two implementations were used:

1. `C93_common_bank_census.cpp`: odd-SPF factorization and exact divisor
   enumeration, with explicit runtime exceptions and integer cross-products.
2. `C93_common_bank_verify.py`: direct trial-divisor pair enumeration, static
   endpoint reconstruction, and set-by-set comparison with C87.

The verifier was run normally and with `python -O` through `X=10^6`.  Both
outputs were byte-identical:

```text
SHA-256 C92BE27F848070C8016F1BE2B4BCD280C6DE9543532EA567E5A523CFBBC0BFC6
```

The C++ `10^9` census was run twice.  The JSON files were byte-identical:

```text
SHA-256 0A664FC7BBC126C79D7068EBED8B632E0DFE2E6DA85AC76BFA2B2611A4E93CE6
classification digest ecefb1de7848e5d3
event trajectory digest 5179ddea62743c74
```

Toolchain:

```text
g++.exe (Rev5, Built by MSYS2 project) 16.1.0
Python 3.12.4
```

Source hashes:

```text
C93_common_bank_census.cpp
EDF422029D4EA4DE4288530EEE9A0FAC84A53CEE464981A40D38999EF7593412

C93_common_bank_verify.py
E206F7EE24002BDDD05F85393492AD333CC6D9A384117B0BB07072DD9B775ED2
```

## Replay commands

```powershell
g++ -std=c++20 -O3 -DNDEBUG -Wall -Wextra -Wconversion -Wshadow -march=native `
  -o problems/424/compute/wave5/C93_common_bank_census.exe `
  problems/424/compute/wave5/C93_common_bank_census.cpp

problems/424/compute/wave5/C93_common_bank_census.exe `
  1000000000 `
  problems/424/compute/wave5/C93_common_bank_1000000000_a.json

python problems/424/compute/wave5/C93_common_bank_verify.py `
  --limit 1000000 `
  --cpp-output problems/424/compute/wave5/C93_common_bank_1000000.json `
  --output problems/424/compute/wave5/C93_verify_1000000_normal.json

python -O problems/424/compute/wave5/C93_common_bank_verify.py `
  --limit 1000000 `
  --cpp-output problems/424/compute/wave5/C93_common_bank_1000000.json `
  --output problems/424/compute/wave5/C93_verify_1000000_O.json
```

## Finite conclusion

The census supplies exact finite evidence for

```text
6 D(X) >= 5 A_H(X)
```

at every event cutoff through `10^9`, with observed minimum ratio `5/6` first
attained at `X=186`.  It is not a proof beyond the scanned range.
