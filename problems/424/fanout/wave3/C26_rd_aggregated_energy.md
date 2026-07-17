# C26: exact aggregated energy for the R-D reservoir

## Result

I computed the R2 gate-(E) reservoir exactly on the supercritical rays
`(3,2,1)` and `(2,1,1)`. Every product representation from every central
source block is retained. In particular, the off-diagonal entries of the
source-block collision matrices below count collisions between different
values of `k`.

The finite data do not falsify gate (E):

- `(3,2,1)`: `E_K/N_K = 1.001543209877, 1.005084915228,
  1.006166320928` for `K=2,3,4`.
- `(2,1,1)`, choosing `G0` at its sole tie: `E_K/N_K = 1, 1,
  1.000523703398, 1.002421692548, 1.003455937733` for `K=2,...,6`.

These are finite values only. They neither prove a uniform bound nor support
an asymptotic extrapolation.

## Exact convention and the missing R2 formulas

Write the offset *set* as

\[
  \mathcal D_{a,b,c}
  =2\mathcal D_{a-1,b,c}\ \cup\
   (3\mathcal D_{a,b-1,c}+1)\ \cup\
   (5\mathcal D_{a,b,c-1}+3),\qquad
  \mathcal D_{0,0,0}=\{0\}.
\]

For a ray `(va,vb,vc)`, put `Q=2^va 3^vb 5^vc`,
`M_k=Q^k`, `O_k=mathcal D_{va*k,vb*k,vc*k}`, and

\[
 H_k=\{8M_k+d+1:d\in O_k\}.
\]

The archived [R2 section 5](../../writeup/R2_GPTPRO56.md) refers to (57)-(59)
but does not contain their displayed text. The only reconstruction determined
by its stated "color split + maps `2c-1 / 3c-1`" is as follows. Let

\[
 C_k^0=H_k\cap G_0,\qquad C_k^2=H_k\cap G_2.
\]

Choose a color class of size at least `|O_k|/2`. Then

\[
 (U_k,V_k)=
 \begin{cases}
   (C_k^0,\ 3C_k^0-1),&C_k^0\text{ chosen},\\
   (2C_k^2-1,\ C_k^2),&C_k^2\text{ chosen}.
 \end{cases}
\]

Thus `U_k subset G0`, `V_k subset G2`, and the two sizes agree. The exact
range implications are

\[
\begin{array}{c|cc}
\text{chosen color}&U_k&V_k\\ \hline
G_0&(8M_k,9M_k]&(24M_k,27M_k)\\
G_2&(16M_k,18M_k)&(8M_k,9M_k].
\end{array}
\]

For exact finite work I used
`I_K = Z intersect [K/4,3K/4]`, hence
`ceil(K/4) <= k <= floor(3K/4)`.

### Exact ambiguities in the archive

1. Equations (57)-(59) are referenced but absent from the archived R2 file.
2. R2 defines `D_k := |D_{...}|` as a cardinality, then writes `H_k` using an
   unbound offset `d`; the set/cardinality notation is overloaded.
3. A tied color split has no stated rule. This occurs for `(2,1,1), k=1`,
   where `|C_1^0|=|C_1^2|=6`, and it changes the finite energy.
4. The phrase `k in [K/4,3K/4]` does not explicitly state integer rounding;
   the convention above is the literal integer intersection.

No arithmetic error was found in the displayed part of section 5. In
particular, the reconstructed ranges give `uv <= 18*27*Q^K=486Q^K`.
Under gate (M), the central sum gives `N_K >= (c^2/8)Q^K`; Cauchy and the
next-scale loss by `Q` then give exactly
`c^2/(8*486*C_E*Q)=c^2/(3888*C_E*Q)`, as stated in R2. The literal missing
text of (57)-(59), however, cannot be audited beyond this reconstruction.

## Membership and color proof

Every offset word was independently replayed from `x=9`. If the current
value is `x>5`, each of

\[
  x\mapsto2x-1,\qquad x\mapsto3x-1,\qquad x\mapsto5x-1
\]

is licensed because `2,3,5 in G` and the multiplier differs from `x`.
Writing `t=x-1` gives exactly `2t`, `3t+1`, and `5t+3`. Therefore a word with
slope `M_k` and offset `d` ends at `8M_k+d+1 in G`. Every intermediate and
terminal value has residue `0` or `2 mod 3`. For terminal `c>5`:

- `c in G2` implies `2c-1 in G0` by a licensed product with `2`;
- `c in G0` implies `3c-1 in G2` by a licensed product with `3`.

The independent verifier checks these facts at every edge of every enumerated
word, rather than trusting the support recurrence used by the main probe.

## Offset and block data

The fingerprint is FNV-1a-64 over the strictly increasing support, with each
offset encoded as eight little-endian bytes.

### Ray `(3,2,1)`, `Q=360`

| k | `(a,b,c)` | `M_k` | words `W_k` | `|O_k|` | offset range | `H: G0/G2` | chosen | FNV-1a-64 |
|---:|:---:|---:|---:|---:|:---:|:---:|:---:|:---:|
| 1 | (3,2,1) | 360 | 60 | 60 | [23,248] | 24/36 | G2 | `dbe7bc98d2324fbc` |
| 2 | (6,4,2) | 129600 | 13860 | 13068 | [1018,95872] | 5289/7779 | G2 | `5814728b927c2d62` |
| 3 | (9,6,3) | 46656000 | 4084080 | 3542949 | [45593,34898432] | 1431609/2111340 | G2 | `e528de65b8f31e81` |

| k | exact `U_k` range | exact `V_k` range | `|U_k|=|V_k|` |
|---:|:---:|:---:|---:|
| 1 | [5811,6249] | [2906,3125] | 36 |
| 2 | [2075637,2265345] | [1037819,1132673] | 7779 |
| 3 | [746587287,816292353] | [373293644,408146177] | 2111340 |

### Ray `(2,1,1)`, `Q=60`

| k | `(a,b,c)` | `M_k` | words `W_k` | `|O_k|` | offset range | `H: G0/G2` | chosen | FNV-1a-64 |
|---:|:---:|---:|---:|---:|:---:|:---:|:---:|:---:|
| 1 | (2,1,1) | 60 | 12 | 12 | [8,40] | 6/6 | G0 tie rule | `dc77c1d5a2f64edb` |
| 2 | (4,2,2) | 3600 | 420 | 409 | [118,2656] | 176/233 | G2 | `648f582ee67c829d` |
| 3 | (6,3,3) | 216000 | 18480 | 17215 | [1718,161536] | 7418/9797 | G2 | `b13911004f51e928` |
| 4 | (8,4,4) | 12960000 | 900900 | 796473 | [25468,9714688] | 342157/454316 | G2 | `5f241daa7f86aa13` |

| k | exact `U_k` range | exact `V_k` range | `|U_k|=|V_k|` |
|---:|:---:|:---:|---:|
| 1, G0 tie | [489,519] | [1466,1556] | 6 |
| 1, G2 tie | [981,1041] | [491,521] | 6 |
| 2 | [57837,62913] | [28919,31457] | 233 |
| 3 | [3459537,3779073] | [1729769,1889537] | 9797 |
| 4 | [207410937,226789377] | [103705469,113394689] | 454316 |

## Global energy and collision decomposition

For a fixed `K`, define

\[
 r_{K,k}(n)=\#\{(u,v)\in U_k\times V_{K-k}:uv=n\},\qquad
 r_K(n)=\sum_{k\in I_K}r_{K,k}(n).
\]

The `U_k` are pairwise disjoint (verified exactly), so the Cartesian pair
sets are disjoint and

\[
 N_K=\sum_{k\in I_K}|U_k||V_{K-k}|=\sum_n r_K(n).
\]

Let `M_K(k,l)=sum_n r_{K,k}(n)r_{K,l}(n)`. Then

\[
 E_K=\sum_n r_K(n)^2=\sum_{k,l\in I_K}M_K(k,l).
\]

With

\[
 C_{\rm within}=\sum_k\sum_n {r_{K,k}(n)\choose2},\qquad
 C_{\rm cross}=\sum_{k<l}M_K(k,l),
\]

the exact audit identity is

\[
 E_K=N_K+2(C_{\rm within}+C_{\rm cross}).
\]

Thus every cross-`k` collision is present, and contributes twice to `E_K` as
required by the square.

### Ray `(3,2,1)`

| K | `I_K` | `N_K` | distinct products | `E_K` | exact `E_K/N_K` | `C_within` | `C_cross` | max `r_K` |
|---:|:---:|---:|---:|---:|:---:|---:|---:|---:|
| 2 | {1} | 1296 | 1295 | 1298 | 649/648 | 1 | 0 | 2 |
| 3 | {1,2} | 560088 | 558665 | 562936 | 70367/70011 | 323 | 1101 | 3 |
| 4 | {1,2,3} | 212529321 | 211876871 | 213839845 | 213839845/212529321 | 102162 | 553100 | 4 |

For `K=4`, rows and columns ordered by source `k=1,2,3`, the complete matrix is

```text
76063652   172778   177717
  172778 60587875   202605
  177717   202605 76082118
```

The next available block combination is `K=5`, `I_5={2,3}`, with the exact
pair count

\[
 N_5=2(7779)(2111340)=32848227720.
\]

It was not product-expanded: one raw `uint64` product array would require
262785821760 bytes, already above the 192 GB lane RAM cap before radix-sort
scratch space. The exact `N_5` is recorded with status `skipped_pair_cap`.
Hence all in-memory feasible `K` for this support depth, `K=2,3,4`, were
counted exactly.

### Ray `(2,1,1)`, choose G0 at the `k=1` tie

| K | `I_K` | `N_K` | distinct products | `E_K` | exact `E_K/N_K` | `C_within` | `C_cross` | max `r_K` |
|---:|:---:|---:|---:|---:|:---:|---:|---:|---:|
| 2 | {1} | 36 | 36 | 36 | 1 | 0 | 0 | 1 |
| 3 | {1,2} | 2796 | 2796 | 2796 | 1 | 0 | 0 | 1 |
| 4 | {1,2,3} | 171853 | 171808 | 171943 | 171943/171853 | 45 | 0 | 2 |
| 5 | {2,3} | 4565402 | 4559887 | 4576458 | 2288229/2282701 | 1654 | 3874 | 3 |
| 6 | {2,3,4} | 307692465 | 307162614 | 308755831 | 308755831/307692465 | 98162 | 433521 | 4 |

For `K=6`, rows and columns ordered by source `k=2,3,4`, the complete matrix is

```text
105921098   143677   140370
   143677 96042639   149474
   140370   149474 105925052
```

### Tie sensitivity on `(2,1,1)`

Both color choices at `k=1` satisfy the R2 size condition. They give different
finite reservoirs:

| K | G0-tie `E_K` | G0-tie `C_cross` | G2-tie `E_K` | G2-tie `C_cross` |
|---:|---:|---:|---:|---:|
| 2 | 36 | 0 | 36 | 0 |
| 3 | 2796 | 0 | 2806 | 5 |
| 4 | 171943 | 0 | 172823 | 452 |

For the G2 tie and `K=4`, the matrix is

```text
58790   137   162
  137 54329   153
  162   153 58800
```

For the G0 tie, the same matrix is diagonal with entries
`58818,54329,58796`. For `K=5,6`, `I_K` excludes `k=1`, so both tie choices
give exactly the same data as the preceding full table without another
product expansion.

## Implementation and verification

The main probe is
[`rd_energy_probe.cpp`](../../compute/wave3/C26_rd_aggregated_energy/rd_energy_probe.cpp).
It evaluates the set recursion by sorted three-way unions. For each source
rectangle it materializes every integer product, radix-sorts it, run-compresses
equal products, and merges the run lists while retaining the source index.
All counts, matrix entries, and energies are integer (`uint64` or `uint128`);
floating point is used only to print the decimal copy of an exact fraction.

The independent verifier is
[`verify_membership.py`](../../compute/wave3/C26_rd_aggregated_energy/verify_membership.py).
It does not use the support DP. It enumerates every multiset word, replays every
licensed map from `x=9`, and independently reconstructs each support and color
split. It also independently recounts products for:

- `(3,2,1)`: `K=2,3`;
- `(2,1,1)`, G0 tie: `K=2,3,4,5`;
- `(2,1,1)`, G2 tie: `K=2,3,4`.

For larger product runs it independently checks every matrix, histogram,
pair-count, reduced-fraction, and `E=N+2C` identity from the output. All checks
pass in `verify_*.json`.

Build and principal runs:

```powershell
g++ -std=c++20 -O3 -march=native -fopenmp rd_energy_probe.cpp -o rd_energy_probe.exe
.\rd_energy_probe.exe 3 2 1 3 400000000 g0 result_321_g0.json 32
.\rd_energy_probe.exe 2 1 1 4 400000000 g0 result_211_g0.json 32
.\rd_energy_probe.exe 2 1 1 4 1000000 g2 result_211_g2.json 8
python verify_membership.py result_321_g0.json verify_321_g0.json --max-energy-pairs 1000000
python verify_membership.py result_211_g0.json verify_211_g0.json --max-energy-pairs 5000000
python verify_membership.py result_211_g2.json verify_211_g2.json --max-energy-pairs 1000000
```

SHA-256:

```text
rd_energy_probe.cpp  c463a677021c087a7561878543b88de77dda6a45bc18eb90bdf2fdf75acc7a7a
verify_membership.py 7f040739fc59131a75e0d8ac9c9cfb350f01ffff27918f61d6f3379fbad5fa29
result_321_g0.json   2a8332e7761edfd87291e3d76fed3f80aa878e48bc794d1be1969ce2eb51a366
result_211_g0.json   c9ec7c7e0a2a87924fed6bcb4e0a60b9549c3757614b737b40b79ef5ee4b406b
result_211_g2.json   259dab3db4408dba4598aaf210eeab7ed8693d38bcad55e0f73bd7ebce55a36a
verify_321_g0.json   4c8cffe5f3ee3ffd2f59c12ded31090887835089974755b151ff0fec44e54784
verify_211_g0.json   9c353f4ef160a529e87d84e1f53dbb4db86ac0382e3577e187d315b617546d17
verify_211_g2.json   e7efb408533d4936905d0566f0535486e8dff756ffe4a609d4292a6371884608
```

## Finite-only conclusion

The exact collision ratios rise mildly over the computed ranges, and the
off-diagonal collision mass is already larger than the within-rectangle mass
at the largest aligned cases. Nevertheless, the observed maxima are only
`1.006166320928` on `(3,2,1)` and `1.003455937733` on the full `(2,1,1)`
comparison. This is neither the gate-(E) falsifier
`limsup E_K/N_K=infinity` nor evidence of a uniform asymptotic bound. No claim
is made beyond the exact finite tables.
