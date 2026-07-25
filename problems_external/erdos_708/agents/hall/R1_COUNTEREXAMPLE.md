# R1 counterexample

## Certificate

\[
M=3,\qquad A=\{2,3\},\qquad I=\{5,6,7\}.
\]

Both members of \(A\) are prime.  Hence every factorization \(2=uv\)
allowed by R1 contributes the single nonunit occurrence \(2\), and every
factorization \(3=uv\) contributes the single nonunit occurrence \(3\).
Inside \(I\),
\[
N(2)=\{6\},\qquad N(3)=\{6\}.
\]
Thus the two occurrences have only one possible representative:
\[
|N(\{2,3\})|=1<2.
\]
Hall's condition fails, so no choice of two-splits has distinct
representatives in \(I\).

This is minimal in \(M\).  For \(M=2\), the only nonempty choice is
\(A=\{2\}\), and every interval of two consecutive integers contains a
multiple of \(2\).

## Independent replays

- `checker_dp.cpp` enumerates placement masks and performs subset dynamic
  programming.  It exhausts all interval residue classes and all nonempty
  \(A\subseteq[2,M]\), passes \(M=2\), and reports the certificate above as
  the first failure at \(M=3\).
- `verify_failure.cpp` independently enumerates every ordered divisor split
  and every injective representative assignment for the raw certificate.
  It reports four ordered split combinations and `two_split_SDR=UNSAT`.

Commands:

```text
g++ -O3 -std=c++20 checker_dp.cpp -o checker_dp.exe
checker_dp.exe 10
g++ -O2 -std=c++20 verify_failure.cpp -o verify_failure.exe
verify_failure.exe
```

