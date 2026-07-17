# C90: exact ordered-bank cut theorem and the cutoff-2064 obstruction

## Verdict

The full-flow statement is false. Its first failure occurs at the ambient
cutoff

\[
X=2064.
\]

There are 101 hard-hole source units, but an exact finite cut has capacity
100. More strongly, the source side of this cut is itself a Boolean
counterexample to the C56/C79 splitless-closed inequality:

\[
\#\{\hbox{selected hard shapes}\}=97,
\qquad
\#\{\hbox{seed-boundary edges}\}=96.
\]

Thus neither a different flow algorithm nor a non-greedy routing can prove
the proposed full-flow theorem. The underlying C56/C79 relaxation is false.
This does not falsify the more structured C75 image inequality, and it does
not resolve Problem 424.

## 1. Arithmetic network

Fix a cutoff `X`. Put

\[
V_X=\{n\in[2,X]:n\not\equiv1\pmod3\}.
\]

Only distinct-factor rows are allowed:

\[
n+1=ab,\qquad 2\le a<b,\qquad a,b\in V_X.       \tag{1}
\]

Let `G_X` be the least set generated from `2,3` using (1), let
`M_X=V_X\setminus G_X`, let `K_X` be the hard holes, and let `E_X` be the
structural splitless holes. For a hole `n`, put an infinite-capacity unary
arc

\[
n\longrightarrow p                                      \tag{2}
\]

whenever `n+1=gp`, `g in G_X`, and `p in M_X`. Put an infinite source arc
to every member of `E_X`, a unit source arc to every member of `K_X`, and a
unit seed arc from `p` to `2p-1`. If `2p-1` is generated, the latter arc
ends at the sink; otherwise it ends at the corresponding hole vertex.

For `U subseteq M_X`, define

\[
Q_X(U)=\#\{p\in U:2p-1\le X,\ 2p-1\in G_X\cup(M_X\setminus U)\}. \tag{3}
\]

### Lemma 1 (exact max-flow/min-cut condition)

The network admits a flow of value `|K_X|` if and only if

\[
Q_X(U)\ge |K_X\cap U|                                  \tag{4}
\]

for every `U subseteq M_X` satisfying

\[
E_X\subseteq U,
\qquad
n\in U,\ n\to p\Longrightarrow p\in U.                \tag{5}
\]

#### Proof

Let `U` be the hole vertices on the source side of a finite cut. An
infinite splitless arc forces `E_X subseteq U`, and an infinite unary arc
forces the closure condition in (5). Conversely, (5) ensures that no
infinite arc leaves the source side.

The finite arcs crossing this cut are exactly:

* the hard source arcs indexed by `K_X setminus U`; and
* the seed arcs counted by `Q_X(U)`.

Hence its capacity is

\[
|K_X\setminus U|+Q_X(U).                               \tag{6}
\]

Every finite cut has capacity at least `|K_X|` precisely when (4) holds.
The claim follows from integral max-flow/min-cut. QED.

This is the exact Hall condition requested in C90. It is not a canonical
greedy condition and does not prescribe a routing.

## 2. Ordered-bank form

For an allowed integer `n`, repeatedly replace an odd `n` by `(n+1)/2`
until it becomes even; call the result `r(n)`. The values with one fixed
root form a seed-2 chain.

### Lemma 2 (chain balance)

For any `U` satisfying (5), its intersection with each seed-2 chain is an
initial segment. If `R(U)` is the set of selected roots and `T(U)` is the
set of selected chains whose initial segment reaches the last value at most
`X`, then

\[
Q_X(U)=|R(U)|-|T(U)|.                                  \tag{7}
\]

If `H(U)=|K_X cap U|` and `N(U)` is the number of selected nonhard roots,
then

\[
Q_X(U)-H(U)=N(U)-|T(U)|.                               \tag{8}
\]

#### Proof

If the odd hole `2p-1` is selected, the factorization
`2p=(2)(p)` gives the unary arc `2p-1 -> p`; hence the selected portion of
each chain is an initial segment. Such a segment contributes one outgoing
seed edge unless it reaches the ambient top of its chain, in which case it
contributes zero. This proves (7). Every hard hole is even, so the selected
roots split into `H(U)` hard roots and `N(U)` nonhard roots. Substitution in
(7) gives (8). QED.

Therefore the full-flow condition is equivalently the ordered-bank
inequality

\[
|T(U)|\le N(U)                                         \tag{9}
\]

for every finite-cut set `U`.

## 3. Exact counterexample at 2064

The complete set `U` is stored in `C90_scan_20000.json` as the union of
`first_failure.hard_inside` and `first_failure.nonhard_inside`. Its exact
statistics are:

| quantity | value |
|---|---:|
| hard demand `|K_X|` | 101 |
| selected hole vertices `|U|` | 678 |
| hard holes in `U` | 97 |
| hard holes outside `U` | 4 |
| seed exits `Q_X(U)` | 96 |
| finite-cut capacity | `4+96=100` |
| selected roots | 424 |
| selected hard roots | 97 |
| selected nonhard roots `N(U)` | 327 |
| terminal roots `|T(U)|` | 328 |

The four hard holes outside the cut are

```text
354, 534, 594, 714.
```

The verifier checks every splitless source condition and every unary arc.
Consequently (6) gives the exact obstruction

\[
100<101.
\]

In ordered-bank form, the same obstruction is

\[
|T(U)|-N(U)=328-327=1.                                 \tag{10}
\]

This cut alone disproves full-flow existence; optimal-flow computation is
not needed for that conclusion. The exact Dinic run independently attains
flow 100, so the saved cut is also a minimum cut.

## 4. The same set falsifies C56/C79

Define `u_n=1` exactly on `U` and `u_n=0` otherwise. The exact replay
checks all of the following:

1. `u_2=u_3=0`;
2. every structural splitless nonseed has value one;
3. for every distinct-factor row `n+1=ab`,

   \[
   u_n\le u_a+u_b;                                     \tag{11}
   \]

4. the exact positive seed drops are the 96 seed exits in (3).

The saved list of violations of (11) is empty. Among the 154 hard-shaped
values through 2064, exactly 97 have `u_h=1`. Hence

\[
\sum_{h\ {\rm hard}}u_h-
\sum_{p:2p-1\le X}\max(0,u_p-u_{2p-1})
=97-96=1.                                             \tag{12}
\]

This is a Boolean, integer counterexample to C79. Under `t=1-u`, it is the
same counterexample to C56 `(SCB)`. A separate HiGHS discovery returned a
different Boolean optimum with values `99-98=1`; its saved set is replayed
row by row by `C90_c79_counterexample.py`. The companion exact C79 dual
also certifies that the optimum excess at 2064 is exactly one.

## 5. Exhaustive exact scan

The incremental scanner checks every hard arrival, which is sufficient:
between hard arrivals the demand is unchanged and the network only gains
arcs, so full flow cannot first fail there.

Through 20000 it checked 1063 hard cutoffs. The only failing cutoff was
2064, with margin `-1`; the flow recovered by cutoff 2100. The tight
cutoffs were

```text
54, 74, 114, 186, 362, 1710, 1734, 1794, 2000,
2022, 2046, 2058, 2100.
```

The independent scans to 10000 and 20000 have identical first 518 rows and
the same full counterexample. All arithmetic, capacities, closure checks,
and replays are integer-exact. The scripts use explicit exceptions, remain
active under `python -O`, use no `native_decide`, and use one CPU worker.

## 6. Reproduction

```powershell
python -O problems/424/compute/wave5/C90_ordered_bank.py `
  --verify problems/424/compute/wave5/C90_scan_20000.json

python -O problems/424/compute/wave5/C90_c79_counterexample.py `
  --verify problems/424/compute/wave5/C90_C79_boolean_2064.json
```

SHA-256:

```text
2979F60FD22186B2A43DEB94C0B7439E857C5E3D847C480824410EC6A1649FC9  C90_ordered_bank.py
437ABEF2E683DA28159166A280E38B4698C2D7F1EC0BBD98CC1432187EC78FFD  C90_scan_20000.json
D8DE6E3269157066F6DEE2FA2D6009B7C7FA5DFBDC6AE00B76A9EEB3A3106035  C90_c79_counterexample.py
32A7B5DC4B1052606F208E929E704EFF6ED8ABA2364372046CB2F69E81FF9DB8  C90_C79_boolean_2064.json
B9389DCB4121976719E7F22AB626B38BF3534B816DA400EA20F49E5BF4D03DCB  C90_C79_2064.json
```

The C56/C79 global arithmetic-bank frontier is therefore closed negatively:
the proposed inequality is false, with an exact one-unit obstruction at
2064.
