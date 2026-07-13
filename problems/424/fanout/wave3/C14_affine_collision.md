# C14: exact 23-map affine support collision census through `10^8`

## Verdict

The complete, unthinned census was extended from `X=10^5` to
`X=10^8`.  At the new endpoint,

\[
Q=27{,}544{,}559,\quad M=28{,}619{,}857,\quad
U=21{,}651{,}987,\quad \Delta=6{,}967{,}870,
\quad \mathcal E_{\rm aff}=44{,}430{,}313.
\]

Both critical excesses are positive:

\[
\frac{\mathcal E_{\rm aff}}M-W
=\frac{1231824091334706060809}{2690680324911816837600}
=0.457811386930581\ldots,
\]

\[
\frac{\Delta}{M}-\left(1-\frac1W\right)
=\frac{7862087095043378650923}{50069550469295894079047}
=0.157023320987565\ldots.
\]

Thus the zero-excess versions of both C07 gates still fail at `10^8`.
The finite data do not disprove an eventual summable-excess bound, but they
show no decay of either excess from `10^5` through `10^8`.

## Definitions and method

The maps are exactly the C07 family

\[
F_a(n)=a(n-1),\quad
A=\{3,9,27,33,51,69,81,84,87,99\},
\]

\[
H_b(n)=b(2n-3),\quad
B=\{2,5,14,17,26,41,44,50,53,65,77,80,98\}.
\]

Their exact weight and collision-tax threshold are

\[
W=\frac{12246282477409697}{11187720423079200},\qquad
1-\frac1W=\frac{1058562054330497}{12246282477409697}.
\]

The program uses the accepted ascending divisor recurrence:
`n in G` iff `n` is a seed or `n+1=dq` for distinct
`2<=d<q<n` already in `G`.  It generates `G` through `X/2`,
which is sufficient because a product in `G0*G2` has factors at least
`2` and `3`.  It then enumerates every one of the
`59,668,569` cross-color pairs with product at most `10^8` and marks
their complete support.

For the affine census, each map is an increasing stream over the sorted
support.  A 23-way exact merge groups equal images and accumulates
`M=sum r`, `U=sum 1_{r>0}`, and
`E_aff=sum r^2`.  At every checkpoint the merged mass is asserted equal to

\[
\sum_{a\in A}Q(\lfloor X/a\rfloor+1)
+\sum_{b\in B}Q\left(\left\lfloor\frac{X+3b}{2b}\right\rfloor\right).
\]

No support point, parent, map, or image is sampled or thinned.  All
mathematical quantities and displayed decimals use integer arithmetic; the
decimals below are 15-place truncations of exact reduced fractions.  The run
used one CPU thread.  The largest named live arrays and vectors total under
400 MB, so external sorting was unnecessary.

## Exact census

| \(X\) | \(Q(X)\) | \(M\) | \(U\) | \(\Delta=M-U\) | \(\mathcal E_{\rm aff}=\sum r^2\) |
|---:|---:|---:|---:|---:|---:|
| \(10^3\) | 118 | 113 | 93 | 20 | 153 |
| \(10^4\) | 1,591 | 1,350 | 1,188 | 162 | 1,688 |
| \(10^5\) | 20,391 | 17,905 | 15,367 | 2,538 | 23,265 |
| \(10^6\) | 239,195 | 224,762 | 183,463 | 41,299 | 314,390 |
| \(10^7\) | 2,617,884 | 2,615,707 | 2,042,399 | 573,308 | 3,893,053 |
| \(10^8\) | 27,544,559 | 28,619,857 | 21,651,987 | 6,967,870 | 44,430,313 |

| \(X\) | \(\mathcal E_{\rm aff}/M\) | \(\mathcal E_{\rm aff}/M-W\) | \(\Delta/M\) | \(\Delta/M-(1-1/W)\) |
|---:|---:|---:|---:|---:|
| \(10^3\) | 1.353982300884955 | 0.259364093216234 | 0.176991150442477 | 0.090551689627884 |
| \(10^4\) | 1.250370370370370 | 0.155752162701649 | 0.120000000000000 | 0.033560539185406 |
| \(10^5\) | 1.299357721306897 | 0.204739513638176 | 0.141748115051661 | 0.055308654237068 |
| \(10^6\) | 1.398768475098103 | 0.304150267429382 | 0.183745472989206 | 0.097306012174612 |
| \(10^7\) | 1.488336805307322 | 0.393718597638601 | 0.219178982967128 | 0.132739522152535 |
| \(10^8\) | 1.552429594599302 | 0.457811386930581 | 0.243462781802159 | 0.157023320987565 |

The exact reduced excess fractions are:

```text
X=1e3: E/M-W = 327891304783821839/1264212407807949600
       tax excess = 125308137408847779/1383829919947295761
X=1e4: E/M-W = 1742511651595999/11187720423079200
       tax excess = 10274796073966666/306157061935242425
X=1e5: E/M-W = 8202525576983392643/40063226835046615200
       tax excess = 12127511344878262201/219269687758020624785
X=1e6: E/M-W = 9326932702735504523/30665541679660087200
       tax excess = 267834695579111909689/2752498942187558317114
X=1e7: E/M-W = 11521701756091862486821/29263798624691224994400
       tax excess = 4252003539112137251297/32032686800137886310779
X=1e8: E/M-W = 1231824091334706060809/2690680324911816837600
       tax excess = 7862087095043378650923/50069550469295894079047
```

## Verification

The independent `verify_c07.py` implementation uses direct trial divisors
instead of an SPF sieve and a Python `Counter` instead of the stream merge.
It exactly reproduced all C07 entries:

```text
X=1000   Q=118   M=113    U=93     Delta=20    E_aff=153
X=10000  Q=1591  M=1350   U=1188   Delta=162   E_aff=1688
X=100000 Q=20391 M=17905  U=15367  Delta=2538  E_aff=23265
matches_C07=true
```

The separate `audit_result.py` pass recomputed every stored ratio with
exact `Fraction` arithmetic.  It also matched all six `Q(X)` values and
the endpoint pair count against C00's `result_1e8.json`.

## Reproduction

```powershell
g++ -O3 -std=c++20 -Wall -Wextra -Wconversion -Wshadow problems/424/compute/wave3/C14_affine_collision/affine_collision.cpp -o problems/424/compute/wave3/C14_affine_collision/affine_collision.exe
problems/424/compute/wave3/C14_affine_collision/affine_collision.exe 100000000 problems/424/compute/wave3/C14_affine_collision/result_1e8.json
python problems/424/compute/wave3/C14_affine_collision/verify_c07.py
python problems/424/compute/wave3/C14_affine_collision/audit_result.py --result problems/424/compute/wave3/C14_affine_collision/result_1e8.json --hyperbola problems/424/compute/wave3/C00_hyperbola/result_1e8.json
```

The `10^8` run took 4,760 ms on this machine: 3,525 ms for closure
membership, 565 ms for the complete product support, and 669 ms for the
23-stream merge.

SHA-256:

- `affine_collision.cpp`: `6282D33DD4FD95AF83FA8E43228456AD2B1799460262F66E904FB6CB23EB8203`
- `verify_c07.py`: `168A17E377993D6A21F20865C4B464D971A970E866ED6B551F8CFDB716536711`
- `audit_result.py`: `53184C8CAD4ABD313AF6B74E6DFABBE1EB72A37C872214EDDC61C9B8F3FFCCDC`
- `result_1e8.json`: `93A9C144599FC0B213A935E2FB7EECDA4E499FF7D562E290ADD71813ABC4BFAE`
