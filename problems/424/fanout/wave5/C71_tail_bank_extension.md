# C71: exact tail-bank extension through `10^9`

## Verdict

An exact incremental C++ scan checked every cutoff

\[
2\le X\le 10^9
\]

using the C67 definitions. Neither scalar inequality failed:

\[
A_H(X)\le e^+(X),\qquad |K_X|\le e^+(X).
\]

There were zero failures of either inequality among the `999,999,999`
checked cutoffs. The largest ratios through `10^9` remain

\[
\max_X\frac{A_H(X)}{e^+(X)}=\frac{656}{1033}
\quad\text{at }X=16620,
\]

and

\[
\max_X\frac{|K_X|}{e^+(X)}=\frac{8846}{9907}
\quad\text{at }X=175956.
\]

This is finite verification through `10^9`; it proves neither inequality
for unbounded `X`.

## Exact generator

`C71_tail_bank_cpp.cpp` processes integers in ascending order. For every
allowed `n`, it factors `n+1`, enumerates all divisors, and admits exactly
the pairs

\[
2\le a<b,\qquad ab=n+1,
\qquad a,b\not\equiv1\pmod3.
\]

The value `n` is generated exactly when it is a seed `2,3` or an admitted
pair has both endpoints already generated. A nongenerated allowed value is
splitless exactly when it has no admitted pair. A reducible even hole is
hard exactly when it satisfies C67's `hard_shape` test.

A hard root enters the active count at its cutoff. It leaves at the first
generated odd seed-2 child on its chain. Thus the active count at each
cutoff is exactly `A_H(X)`. Simultaneously, prefix counts give

\[
e^+(X)=E(X)-E(\lfloor X/2\rfloor).
\]

Both inequalities and both ratio maxima are evaluated at every cutoff.
Acceptance and ratio comparison use integers only; cross products are at
most `10^18` under the enforced `LIMIT<=10^9` bound. The run uses one
thread. At `10^9` the two core arrays occupy `2,000,000,003` bytes.

## Results

| `X` | generated | `E(X)` | `A_H(X)` | `K(X)` | `e^+(X)` |
|---:|---:|---:|---:|---:|---:|
| `200,000` | `83,779` | `23,151` | `6,348` | `9,937` | `11,223` |
| `1,000,000` | `457,599` | `108,651` | `27,056` | `45,583` | `52,890` |
| `100,000,000` | `51,899,129` | `9,395,726` | `1,794,586` | `3,368,726` | `4,606,216` |
| `1,000,000,000` | `535,276,618` | `88,550,127` | `15,106,735` | `29,010,146` | `43,510,606` |

At `10^9`, exactly `13,903,411` hard-root chains have died before or at the
cutoff, and

\[
29,010,146=15,106,735+13,903,411.
\]

The deterministic `10^9` digests are:

```text
classification states, X=2..10^9: ECEFB1DE7848E5D3
(X,A_H,e^+,K) trajectory:           F2D0D1A6EAAA0452
```

## Independent replay

`C71_tail_bank_cpp.replay.py` independently scanned through `200,000`.
It finds factor pairs by direct trial division, imports no C67 code, and
uses no smallest-prime-factor table. It matched the C++ counts, both complete
per-cutoff audits, all checkpoints, the classification digest, and the
`(X,A_H,e^+,K)` trajectory digest. Its status is `exact_match`.

The replay also independently recovers both eventual ratio maxima, since
their first maximizing cutoffs are at most `175,956`.

## Reproduction

Commands were run from `E:\Projects\ErdosProblems` with `g++ 16.1.0`:

```powershell
& g++ -std=c++20 -O3 -DNDEBUG -Wall -Wextra -Wconversion -Wshadow -march=native -o problems/424/compute/wave5/C71_tail_bank_cpp.exe problems/424/compute/wave5/C71_tail_bank_cpp.cpp

python problems/424/compute/wave5/C71_tail_bank_cpp.replay.py --exe problems/424/compute/wave5/C71_tail_bank_cpp.exe --limit 200000 --cpp-output problems/424/compute/wave5/C71_tail_bank_cpp.small.json --output problems/424/compute/wave5/C71_tail_bank_cpp.replay.json

& problems/424/compute/wave5/C71_tail_bank_cpp.exe 100000000 problems/424/compute/wave5/C71_tail_bank_cpp.1e8.json

& problems/424/compute/wave5/C71_tail_bank_cpp.exe 1000000000 problems/424/compute/wave5/C71_tail_bank_cpp.1e9.json
```

Measured wall times and kernel times were:

| action | wall seconds | internal seconds |
|---|---:|---:|
| compile | `1.365` | n/a |
| replay command | `1.455` | C++ subprocess `0.040101`; Python `1.335688` |
| all cutoffs through `10^8` | `4.917` | `4.884347` |
| all cutoffs through `10^9` | `56.611` | `56.536399` |

## SHA-256

```text
73E27078A218F1A4EBDB9E8B6FA1766C9442174E59ABCD87DF2FCCDD319D29FC  C71_tail_bank_cpp.cpp
DB52578ADD8AD881BF98F633277DAC0FD0BF4C3B8D10E35D8B03B2AB464CD318  C71_tail_bank_cpp.replay.py
A4DCB5AB82ED63F8EF6893D693D4AB95B8466A0C3CBB48E6F247C56B87452B21  C71_tail_bank_cpp.exe
1DF67F75E204FC18B44B2008691C640787C2350F70933EC8D022C53C0052F937  C71_tail_bank_cpp.small.json
45292F29BE385D61498751A680F364BB3DA17137F93C3F1709006DB088F0FBE2  C71_tail_bank_cpp.replay.json
0AFD0411804D47446F3066229D897D82352891C5E9128D26B6E85B819BFECF53  C71_tail_bank_cpp.1e8.json
8D9592BC82C6D1E559663CFBB36BD8C5047781A5F44D285C510A65C3ABD68455  C71_tail_bank_cpp.1e9.json
```
