# Audit of the lower bound `S(13) >= 44`

Date: 2026-07-18 (Europe/Istanbul)

Scope: audit only. No 44-comparator search was started.

## Verdict

**PASS.** The registered lower-bound bridge is arithmetically and computationally correct:

```text
S(13) >= S(11) + P(2,13)
      >= 35 + ceil(log2(F(13)))
      = 35 + ceil(log2(392))
      = 44.
```

Since `2^8 = 256 < 392 <= 512 = 2^9`, the ceiling is exactly 9.

## Sources and theorem chain

1. D. C. Van Voorhis, *Toward a Lower Bound for Sorting Networks*, in
   *Complexity of Computer Computations* (1972), pp. 119--129,
   DOI: <https://doi.org/10.1007/978-1-4684-2001-2_12>.
2. Bert Dobbelaere's public 2025 recurrence implementation:
   <https://gist.github.com/bertdobbelaere/0a30f5321965732b59c102fa9e3250bb>.
   Its stated Van Voorhis consequence is
   `S(N) >= S(N-2) + P(2,N)` with
   `P(2,N) >= ceil(log2(F(N)))`.
3. Jannis Harder, *An Answer to the Bose-Nelson Sorting Problem for 11 and
   12 Channels*, <https://arxiv.org/abs/2012.04400>. The paper proves the
   lower bounds 35 and 39 using certificates checked by an Isabelle/HOL
   verified checker. Together with the known 35-comparator network this gives
   `S(11) = 35`; only the lower bound `S(11) >= 35` is needed here.
4. The maintained table records `S(11)=35` and `44 <= S(13) <= 45`:
   <https://bertdobbelaere.github.io/sorting_networks.html>.

## Exact recurrence reproduced

Writing infeasible states as infinity, the downloaded Python implements

```text
m(1,d) = 0,
m(s,0) = infinity for s > 1,
m(s,d) = min 2 * (m(a,e) + m(s-a,d-1) + 2^(e+d-1)),
F(n) = min_{0 <= d < n} m(n,d),
```

where the recurrence minimum is over
`1 <= a <= s-d` and `0 <= e < min(d,a)`.

The upstream memoized Python and a separately written bottom-up exact-integer
PowerShell implementation agree on:

| n | F(n) | ceil(log2(F(n))) |
|---:|-----:|-----------------:|
| 3 | 8 | 3 |
| 4 | 16 | 4 |
| 5 | 36 | 6 |
| 6 | 52 | 6 |
| 7 | 80 | 7 |
| 8 | 96 | 7 |
| 9 | 168 | 8 |
| 10 | 200 | 8 |
| 11 | 256 | 8 |
| 12 | 288 | 9 |
| 13 | **392** | **9** |
| 14 | 424 | 9 |
| 15 | 480 | 9 |
| 16 | 512 | 9 |
| 17 | 784 | 10 |

For `n=13`, the feasible depth-indexed values are

```text
d=4: 392; d=5: 496; d=6: 856; d=7: 1592; d=8: 3112;
d=9: 6172; d=10: 12300; d=11: 24580; d=12: 49152.
```

Thus 392 is the unique minimum among these states. A third implementation,
the independently published C++ program at
<https://gist.github.com/spaanse/4e4ad9410587570c73c71d52433a89a7>,
also outputs the increment 9 for `n=13`.

Replay the independent exact DP from the repository root with:

```powershell
& problems_external/sorting_network_13/audit/audit_lower44.ps1
```

Expected final line:

```text
AUDIT PASS: F(13)=392; ceil(log2(F(13)))=9; 35+9=44.
```

Downloaded/replay source hashes (SHA-256):

```text
53A6F257617CFF9D9F97611D60A9EB975142B628E1108157DF5484D1FD473511  lower_bound_upstream.py
6B87CCF605D50ACAD8058CFA368263DEDFC64C8B44049EE8032B0F65E7B55EA0  van_voorhis_independent.cpp
8FBA5365B8EFBB6530052AD3E7E4AD1708F63493085F8F1622B324256185C7AA  audit_lower44.ps1
```

## Formal Conjectures collision check

The current upstream `google-deepmind/formal-conjectures` main branch was
checked at commit
`c252a41054125b5fd9c8356e2137cd9b55337657`.

An exact full-tree scan of `FormalConjectures/` and
`FormalConjecturesForMathlib/` found no occurrence of sorting-network,
comparator-network, Bose--Nelson, Van Voorhis, compare-exchange, or the
zero--one principle. A broader Lean scan for `sort`, `comparator`, `sorter`,
and `size-optimal` produced only unrelated list/degree-sequence sorting code.

**Conclusion:** the current upstream main branch contains no sorting-network
statement and in particular no statement of `S(13)=44` or existence of a
44-comparator 13-channel sorting network.

## Audit boundary

This audit reproduces `F(13)=392`, verifies the integer/logarithmic inference,
checks the cited `S(11)` result, and checks the current Formal Conjectures tree.
It does not re-formalize the 1972 Van Voorhis theorem and does not search for a
44-comparator certificate.
