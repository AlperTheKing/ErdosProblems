# C00: exact hyperbola pair/product census for Route R-C

## Definitions

Let `G` be the exact ascending divisor-recursion closure, `G0 = G cap 3N`, and `G2 = G cap {2 mod 3}`. For `X >= 1`, define

- `r_X(p) = #{(a,b) in G0 x G2 : ab=p<=X}`;
- `P(X) = sum_p r_X(p)`;
- `Q(X) = #{p<=X : r_X(p)>0}`;
- `E(X) = sum_p r_X(p)^2`;
- `kappa(X) = E(X) X / P(X)^2`.

The factors are automatically distinct. Every represented `p` gives `p-1 in G2`. Cauchy-Schwarz gives the exact finite inequality `Q(X) >= P(X)^2/E(X) = X/kappa(X)`.

## Exact results

| X | P(X) | Q(X) | E(X) | P/X | Q/X | E/P | kappa |
|---:|---:|---:|---:|---:|---:|---:|---:|
| 1e3 | 124 | 118 | 136 | 0.124000 | 0.118000 | 1.096774 | 8.844953 |
| 1e4 | 1,856 | 1,591 | 2,420 | 0.185600 | 0.159100 | 1.303879 | 7.025212 |
| 1e5 | 27,214 | 20,391 | 42,858 | 0.272140 | 0.203910 | 1.574851 | 5.786915 |
| 1e6 | 370,812 | 239,195 | 716,226 | 0.370812 | 0.239195 | 1.931507 | 5.208858 |
| 1e7 | 4,787,694 | 2,617,884 | 11,580,502 | 0.4787694 | 0.2617884 | 2.418806 | 5.052131 |
| 1e8 | 59,668,569 | 27,544,559 | 183,463,965 | 0.59668569 | 0.27544559 | 3.074717 | 5.152993 |

At `1e8`, represented products occupy `82.633677%` of the multiples of three up to `X` (`3 Q(X)/X`). This is a finite exact statement only. The small rise of `kappa` from `1e7` to `1e8` forbids claiming monotone convergence.

## Reproduction and independent check

```powershell
g++ -O3 -std=c++20 problems\424\compute\wave3\C00_hyperbola\hyperbola_pairs.cpp -o problems\424\compute\wave3\C00_hyperbola\hyperbola_pairs.exe
problems\424\compute\wave3\C00_hyperbola\hyperbola_pairs.exe 100000000 problems\424\compute\wave3\C00_hyperbola\result_1e8.json
```

The `1e8` run took 35.66 seconds on this machine. A separate Python trial-divisor generator and dictionary product counter reproduced `(P,Q,E)=(1856,1591,2420)` at `X=1e4` and verified `p-1 in G` for every represented product.

SHA-256:

- `hyperbola_pairs.cpp`: `ABA1E4D502F0543292B3100840327FFECADB5B37DFDD19E73CF1216CFCABDC93`
- `result_1e8.json`: `8686F8239D3EABD171384BC7080AD6F442611A4E79F911312CAC181400EDD9FF`

## Proof frontier exposed by the census

The all-hyperbola version cleanly separates two uniform estimates:

1. pair supply `P(X) >= c1 X`;
2. collision control `E(X) <= C P(X)^2/X`.

Together they give `Q(X) >= X/C`, hence positive lower density of `G`. The data support both through `1e8`, but prove neither asymptotically. Unlike a single dyadic rectangle, `P(X)` aggregates all unbalanced scales; this is the correct non-circular R-C quantity to target.
