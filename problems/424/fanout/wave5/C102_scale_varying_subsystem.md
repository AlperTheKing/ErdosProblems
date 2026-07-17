# C102: a scale-varying light-multiplicity decoder

## Verdict

There is an explicit nonperiodically decoded subset of `G` whose positive
lower density follows from two finite, scale-indexed gates.  The collision
gate is strictly weaker than the bounded-energy gate: it controls only a
fixed positive fraction of edges and permits the other products to have
unbounded multiplicity and unbounded second moment.

The gates are not proved here.  Exact growing-block experiments on the rays
`(2,1,1)` and `(3,2,1)` retain more than `0.999998` of all tested edges at
multiplicity at most two.  The largest census has `60,512,841` edges.  This is
finite evidence, not a positive-density theorem for `G`.

## 1. Exact growing blocks and distinct inputs

Use the translated coordinate `t=x-1`.  Multiplication by the generated
elements `2,3,5` gives the maps

\[
 L_2(t)=2t,\qquad L_3(t)=3t+1,\qquad L_5(t)=5t+3.       \tag{1}
\]

Fix positive integers `a,b,c` and put

\[
 Q=2^a3^b5^c.
\]

Let `D_k` be the set of offsets of all words containing exactly `ak` copies
of `L_2`, `bk` copies of `L_3`, and `ck` copies of `L_5`.  Thus every word is
`t -> Q^k t+d`, with `d in D_k`, and the finite sets satisfy the exact union
recursion

\[
 D_{A,B,C}=2D_{A-1,B,C}\mathbin\cup(3D_{A,B-1,C}+1)
              \mathbin\cup(5D_{A,B,C-1}+3).           \tag{2}
\]

Starting from `x=9`, define

\[
 H_k=\{8Q^k+d+1:d\in D_k\}.                            \tag{3}
\]

Every member of `H_k` is in `G`.  This assertion respects distinct inputs:
the starting value is greater than `5`, and each map `x -> mx-1` with
`m in {2,3,5}` strictly increases a current value greater than `5`.

Every member of `G` is `0` or `2 (mod 3)`.  Choose
`rho_k in {0,2}` for which

\[
 C_k=\{h\in H_k:h\equiv\rho_k\pmod3\}
\]

is larger, breaking ties in favor of `2`, and write `s_k=|C_k|`.  Then
`s_k >= |D_k|/2`.  Define two color-separated generated sets by

\[
 U_k=
 \begin{cases}
   \{2h-1:h\in C_k\},&\rho_k=2,\\
   \{4h-3:h\in C_k\},&\rho_k=0,
 \end{cases}
 \qquad
 V_k=\{3h-1:h\in C_k\}.                               \tag{4}
\]

If `rho_k=0`, the first set in (4) is made by the two legal steps
`h -> 2h-1 -> 4h-3`.  Hence

\[
 U_k\subseteq G\cap3\mathbb N,\qquad
 V_k\subseteq G\cap(3\mathbb N+2),\qquad
 |U_k|=|V_k|=s_k.                                      \tag{5}
\]

All steps in (4) have unequal inputs because `h>5`.  Moreover, an input from
`U_k` can never equal one from `V_j`, by (5).  Thus every final product below
also satisfies the distinct-value convention.

The crude bounds needed later are

\[
 \max U_k\le36Q^k,\qquad \max V_k\le27Q^k.             \tag{6}
\]

## 2. The light-multiplicity gates

For `K>=2`, put

\[
 I_K=\{i:\lceil K/3\rceil\le i\le\lfloor2K/3\rfloor\}
\]

and form the labelled, scale-varying edge family

\[
 \mathcal E_K=\bigsqcup_{i\in I_K}U_i\times V_{K-i},
 \qquad
 N_K=|\mathcal E_K|=\sum_{i\in I_K}s_i s_{K-i}.        \tag{7}
\]

For a positive integer `z`, let

\[
 r_K(z)=\#\{(i,u,v):i\in I_K, u\in U_i,
                     v\in V_{K-i}, uv=z\}.            \tag{8}
\]

Fix an integer `L>=1`.  The decoder keeps a product only when its actual
finite representation multiplicity is at most `L`:

\[
 P_K(L)=\{z-1:1\le r_K(z)\le L\},\qquad
 P(L)=\bigcup_{K\ge K_0}P_K(L).                        \tag{9}
\]

This is nonperiodic and scale-varying.  It uses neither whole residue classes
nor a fixed finite state space.

### Theorem 1 (averaged mass plus light edges)

Suppose there are constants `c_0>0`, `eta>0`, an integer `L>=1`, and `K_0`
such that, for every `K>=K_0`, the following two exact finite inequalities
hold:

\[
 N_K\ge c_0Q^K,                                         \tag{A}
\]

\[
 \sum_{z:r_K(z)\le L}r_K(z)\ge\eta N_K.                \tag{T}
\]

Then `P(L)` is an explicit subset of `G` and

\[
 \boxed{\underline d(P(L))\ge
        \frac{c_0\eta}{972LQ}>0.}                       \tag{10}
\]

#### Proof

By (5), every edge joins distinct generated values, so closure gives
`uv-1 in G`.  This proves `P(L) subset G`.

Each retained product accounts for at most `L` edges.  Therefore (A)-(T)
give

\[
 |P_K(L)|\ge {1\over L}\sum_{z:r_K(z)\le L}r_K(z)
             \ge {c_0\eta\over L}Q^K.                  \tag{11}
\]

Equations (6)-(7) place `P_K(L)` below `972Q^K`.  Given sufficiently large
`X`, choose `K` with

\[
 972Q^K\le X<972Q^{K+1}.
\]

Then the single finite set `P_K(L)` is contained in `P(L) cap [1,X]`, and
(11) yields

\[
 { |P(L)\cap[1,X]|\over X}
 \ge {c_0\eta Q^K\over LX}
 > {c_0\eta\over972LQ}.
\]

Taking the lower limit proves (10).  QED.

## 3. Why these gates are weaker

Gate (A) asks only for the central convolution of the finite support sizes.
It does not ask for a pointwise estimate
`|D_k| >= c Q^k/sqrt(k)`.  Logically, a sequence can obey the latter scale
away from a sparse set such as the powers of two, vanish on that sparse set,
and still have a uniformly positive central convolution.  Thus (A) can hold
while every pointwise lower gate fails infinitely often.

Gate (T) is strictly weaker than a global energy estimate

\[
 \sum_z r_K(z)^2\le C N_K.                              \tag{12}
\]

Indeed, (12) implies

\[
 \sum_{z:r_K(z)>L}r_K(z)
 \le {1\over L+1}\sum_zr_K(z)^2
 \le {C\over L+1}N_K,                                  \tag{13}
\]

so a sufficiently large fixed `L` gives (T).  The converse is false: put
`eta N` edges on distinct products and all remaining edges on one product.
Then (T) holds with `L=1`, while the energy divided by `N` grows linearly in
`N`.

This route therefore survives an arbitrarily bad high-multiplicity tail.  It
also lies outside the three frozen barriers:

1. The decoder depends on the exact reachable products at scale `K`, not on
   a finite global residue automaton.
2. The edge family is a union over a linearly growing number of incompatible
   block scales, not a fixed Cartesian window.
3. The word depth grows with `K`, and no bounded-depth product closure is
   used.

The final step `uv-1` is nonlinear in two growing affine blocks.  It is not a
claim about, or a census of, the frozen affine orbit using only multipliers
`{2,3,5}`.

## 4. Exact finite experiments

`C102_truncated_decoder.cpp` constructs every offset by (2) with integer
bitsets, forms (3)-(8), sorts every product edge, and records the full exact
multiplicity histogram.  No membership census for `G` is imported.

Two rays were audited:

| ray | `Q` | exact offset supports `|D_k|` | selected sizes `s_k` |
|---|---:|---:|---:|
| `(2,1,1)` | `60` | `12, 409, 17215, 796473` | `6, 233, 9797, 454316` |
| `(3,2,1)` | `360` | `60, 13068, 3542949` | `36, 7779, 2111340` |

The majority residue was `2` at every tested layer.  With the central index
set in (7), the exact product results are:

| ray | `K` | `N_K` | product support | multiplicity histogram | `N_K/Q^K` | edge fraction with `r<=2` |
|---|---:|---:|---:|---|---:|---:|
| `(2,1,1)` | 2 | 36 | 36 | `1:36` | 0.0100000000 | 1 |
| `(2,1,1)` | 3 | 2796 | 2796 | `1:2796` | 0.0129444444 | 1 |
| `(2,1,1)` | 4 | 54289 | 54284 | `1:54279, 2:5` | 0.0041889660 | 1 |
| `(2,1,1)` | 5 | 4565402 | 4563576 | `1:4561752, 2:1822, 3:2` | 0.0058711445 | 0.9999986858 |
| `(3,2,1)` | 2 | 1296 | 1296 | `1:1296` | 0.0100000000 | 1 |
| `(3,2,1)` | 3 | 560088 | 559577 | `1:559066, 2:511` | 0.0120046296 | 1 |
| `(3,2,1)` | 4 | 60512841 | 60496906 | `1:60480975, 2:15927, 3:4` | 0.0036027783 | 0.9999998017 |

The last row retains exactly `60,512,829/60,512,841` edges at `L=2`.
The finite values are compatible with (A) and (T), but they do not establish
either eventual inequality.

An independent Python implementation uses ordinary sets and `Counter`, and
agrees on every layer, edge count, support count, energy, light-edge count,
and multiplicity histogram for the `(2,1,1)` ray through `K=3`.  Normal and
`python -O` outputs are byte-identical.  Two runs of the C++ census are also
byte-identical.

SHA-256 values for the final artifacts are:

```text
AF0097538EA94EAB4E94CF26EE0B21C19490D2247B747F5ED77EDA2B05E471CE  C102_truncated_decoder.cpp
E4925A29021BED9555C9D911854D637B09FECCDA563733B25B9FB337D34503BA  C102_truncated_decoder.json
3D68885E2C52B091DDAD15F87B628D165405D7D640B4D330AB78C583229B41AF  C102_truncated_decoder_verify.py
A8F2BF3B1C9231E5F92837B7706F265F064B39FC3EC7B548554B01A0F0D10EF4  C102_truncated_decoder_verify.json
```

Reproduction:

```powershell
g++ -std=c++20 -O3 -fopenmp `
  problems/424/compute/wave5/C102_truncated_decoder.cpp `
  -o problems/424/compute/wave5/C102_truncated_decoder.exe

problems/424/compute/wave5/C102_truncated_decoder.exe `
  problems/424/compute/wave5/C102_truncated_decoder.json 32

python problems/424/compute/wave5/C102_truncated_decoder_verify.py `
  --output problems/424/compute/wave5/C102_truncated_decoder_verify.json
```

## 5. Precise frontier

For either explicit ray, the remaining statements are exactly:

\[
 \liminf_{K\to\infty}{N_K\over Q^K}>0,                 \tag{14}
\]

and, for some fixed finite `L`,

\[
 \liminf_{K\to\infty}{1\over N_K}
       \sum_{z:r_K(z)\le L}r_K(z)>0.                   \tag{15}
\]

Equation (14) is an averaged growing-block support gate.  Equation (15) is a
truncated collision gate and remains meaningful even when the global energy
ratio diverges.  Proving (14)-(15) would make (9) a proved positive-density
subset of `G`; the present exact census does not prove those limits.
