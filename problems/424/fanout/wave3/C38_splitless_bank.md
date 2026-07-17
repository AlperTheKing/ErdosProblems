# C38: splitless-bank asymptotic contraction lane

## Verdict

No asymptotic proof and no true-`G` counterexample to

\[
 H(X)\le Q(X)+E(X)                                      \tag{T}
\]

was found.  The exact census verifies (T) at every integer cutoff through
`10^7`; there is no finite failure in that range.  At the endpoint,

\[
 (H,Q,E)=(392961,637270,1004961),
 \qquad H-Q-E=-1249270.
\]

This is finite evidence, not a proof.  In particular, the natural
death-rank bank DAG with one unit of capacity at each splitless leaf, which
would prove (T), is false.  Its first exact failure is `X=1536`: an explicit
set of `61` hard sources has only `60` local resources (`14` splitless leaves
and `46` healed boundary targets).  Thus the bank DAG does **not** prove (T).

The same local DAG with splitless capacity `C` fails for every tested
`C<=40`; for `C=40` the first failure is `X=3236496`, with exact
max-flow/min-cut `137043` against `137044` hard sources.  The finite statement
with `C=1000000` survives every cutoff through `10^7`, matching all `392961`
hard sources.  This leaves the explicit arithmetic shadow-expansion lemma in
Section 7 as the smallest surviving theorem target.  Any absolute `C` in
that lemma would give `H(X)<=Q(X)+C E(X)` and close the density problem.

## 1. Definitions

Let

\[
 \mathcal A=\{n\ge2:n\not\equiv1\pmod3\},
\]

and let `G` be the least subset of `A` containing `2,3` and closed under
`(a,b) -> ab-1` for distinct allowed parents `a<b`.  Put

\[
 \mathcal M=\mathcal A\setminus G,
 \qquad M(X)=|\mathcal M\cap[1,X]|.
\]

For an allowed `n`, let

\[
 \mathcal P(n)=\{(a,b):2\le a<b,\ a,b\in\mathcal A,\ ab=n+1\}.
\]

A hole `n in M` is **splitless** if `P(n)` is empty.  Let `E_X` be the set
of splitless holes through `X` and `E(X)=|E_X|`.  As proved in C13,
`E(X)=o(X)`.

A reducible even hole is **hard** unless it is seed-3 easy, meaning
`3|(n+1)` and `(n+1)/3` is allowed and different from `3`.  Let `H_X` be
the hard holes through `X` and `H(X)=|H_X|`.

Write `T(q)=2q-1` and define the healed seed-2 boundary set by parents

\[
 \mathcal Q_X=\{q\in\mathcal M:T(q)\le X,\ T(q)\in G\},
 \qquad Q(X)=|\mathcal Q_X|.                              \tag{1}
\]

Equivalently, a target may be labelled by its child `T(q)`; the cutoff is
always the child coordinate.

For a hole, use the obstruction rank from C31:

\[
 \rho(n)=0\quad\text{if }\mathcal P(n)=\varnothing,
\]

and, for a reducible hole,

\[
 \rho(n)=1+\max_{(a,b)\in\mathcal P(n)}
 \min\{\rho(x):x\in\{a,b\}\cap\mathcal M\}.             \tag{2}
\]

This is death rank minus one in the descending grounded approximants.

## 2. The all-lower obstruction shadow

For a reducible hole `n`, set

\[
 B(n)=\bigcup_{(a,b)\in\mathcal P(n)}
 \{x\in\{a,b\}\cap\mathcal M:\rho(x)<\rho(n)\}.         \tag{3}
\]

Define its splitless shadow recursively by

\[
 L(n)=
 \begin{cases}
 \{n\},&\rho(n)=0,\\
 \displaystyle\bigcup_{q\in B(n)}L(q),&\rho(n)>0.
 \end{cases}                                             \tag{4}
\]

This follows every lower-rank missing endpoint in every admissible factor
pair, rather than choosing one critical parent.

**Lemma 2.1 (grounded shadow).**  For every hole `n`, `L(n)` is a nonempty
finite subset of `E_n`.  Every path in (4) strictly decreases obstruction
rank and integer value.

**Proof.**  Every pair for a hole is blocked by at least one missing
endpoint.  In (2), the minimum for each pair is at most the maximum of those
minima, namely `rho(n)-1`.  Hence every pair contributes a member of `B(n)`,
so `B(n)` is nonempty.  Every factor is smaller than its output and every
edge in (3) lowers rank.  Iteration therefore terminates at rank zero, which
is exactly a splitless hole.  This proves nonemptiness, finiteness, and the
claimed containment.  QED.

Lemma 2.1 is the theorem-grade content supplied by the death-rank recurrence.
It does not control how many hard holes can share the same leaves.

## 3. The splitless-bank DAG

For fixed `X` and an integer `C>=1`, form the directed capacitated network
`D_C(X)`:

1. Add a source node `s_h` for each `h in H_X`, with capacity `1` from the
   super-source.
2. Add a leaf node `r_e` for each `e in E_X`; join `s_h` to `r_e` with
   capacity `1` when `e in L(h)`.
3. Give each leaf a direct edge `r_e -> sink` of capacity `C`.
4. For each `q in Q_X`, add a target node `t_q`; join `r_e` to `t_q` with
   capacity `1` when `e in L(q)`, and give `t_q -> sink` capacity `1`.

Thus a hard hole is charged either to one of its splitless obstruction
leaves or to a healed seed-2 chain whose missing parent has a common leaf.
All edges are determined by actual factor obstructions and the grounded
rank recurrence.

**Proposition 3.1 (bank implication).**  If `D_C(X)` has an integral flow of
value `H(X)`, then

\[
 H(X)\le Q(X)+C E(X).                                    \tag{5}
\]

**Proof.**  Decompose the integral flow into unit source-to-sink paths.  A
path ending directly at a leaf uses one of at most `C` units assigned to
that member of `E_X`.  Every other path ends through a distinct target in
`Q_X`, because its sink edge has capacity one.  Counting the two path types
gives (5).  QED.

Flattening the paths gives a derivation-local bipartite graph: `h` is
adjacent to `C` copies of each leaf in `L(h)`, and to `q in Q_X` precisely
when \(L(h)\cap L(q)\ne\varnothing\).  This is strictly stronger than the
scalar inequality (5); its edges are not complete rank-dominance edges.

## 4. Exact scalar and rank census through `10^7`

The ascending generator reconstructs the least grounded set exactly, uses
trial-divisor factor pairs for (2), and audits every hard-source event.
Between hard-source events the left sides below are constant while `Q` and
`E` can only increase, so this checks every integer cutoff.

| exact gate | result for all `X<=10^7` |
|---|---|
| `H(X)<=Q(X)+E(X)` | no failure |
| `H(X)<=Q(X)` | no failure |
| `H(X)<=E(X)` | no failure |
| `H_{<=d}(X)<=Q_{<=d}(X)` | false first at `(X,d)=(362,2)`, `11>10` |
| `H_{<=d}(X)<=Q_{<=d}(X)+1` | no failure |
| `H_{<=d}(X)<=Q_{<=d+1}(X)` | no failure |
| `H_{<=d}(X)<=Q_{<=d}(X)+E(X)` | no failure |

The terminal census is

| quantity | value |
|---|---:|
| allowed integers | 6,666,666 |
| generated integers | 4,952,270 |
| holes `M(X)` | 1,714,396 |
| splitless holes `E(X)` | 1,004,961 |
| hard holes `H(X)` | 392,961 |
| healed targets `Q(X)` | 637,270 |
| maximum obstruction rank | 17 |

Consequently the requested weaker target (T) is true in the full census,
with no first failure to report.  The failed `C=1` DAG below is a
counterexample only to a stronger local charging formulation; it is not a
counterexample to (T).

## 5. Exact local falsifiers

The expanded Python matcher and compact C++ residual network agree on the
first failures for `C=1,2,3,4`.  The first hard-source failure for each exact
integer flow is:

| leaf capacity `C` | first failing `X` | flow deficit |
|---:|---:|---:|
| 1 | 1,536 | 1 |
| 2 | 6,000 | 1 |
| 3 | 35,300 | 1 |
| 4 | 111,620 | 1 |
| 5 | 188,658 | 1 |
| 6 | 252,096 | 1 |
| 7 | 331,002 | 1 |
| 8 | 397,902 | 1 |
| 9 | 483,180 | 1 |
| 10 | 563,640 | 1 |
| 20 | 1,425,522 | 1 |
| 40 | 3,236,496 | 1 |

For `C=1`, `dag_1e4.json` contains the complete canonical Hall witness:
`61` listed hard holes have a neighborhood of `60`, consisting of `14`
listed splitless leaves and `46` listed `Q` targets.  This proves that the
one-unit bank DAG cannot prove `H<=Q+E`.

For `C=40`, the compact exact network has

\[
 H=137044,\qquad \operatorname{maxflow}
 =\operatorname{mincut}=137043.                          \tag{6}
\]

The residual cut certificate, node counts, and its first `100` reachable
vertices of each type are stored in `dag_cpp_C40_1e7.json`.  Monotonicity in
leaf capacity makes (6) an exact falsifier for every `C<=40`, independently
of the earlier first-failure table.

Three deterministic one-parent forests fail much earlier.  At `X=144`, the
root-8 component already has three rank-filtered hard sources against one
healed target, so a unit bank is insufficient.  By `10^7`, the maximum
component deficits are `70762` (minimum critical endpoint), `77400`
(minimum critical root), and `54727` (online minimum-balance choice).  A
fixed canonical parent choice therefore loses the multi-leaf expansion that
the full DAG retains.

## 6. Finite survivor

The exact statement

\[
 \mathsf{SB}(10^7,10^6):\quad
 D_{1000000}(X)\text{ saturates }H_X
 \text{ for every }X\le10^7                            \tag{7}
\]

is certified.  The streaming run inserted each source at its integer
coordinate, found an augmenting path every time, and ended with flow
`392961/392961`.  The largest all-lower shadow had `144` splitless leaves;
the final network had `2,035,194` nodes and `16,863,214` directed residual
edges.

No claim is made that `10^6` is the least surviving capacity.  The exact
information currently available is only

\[
 C\le40\text{ fails by }X=3236496,
 \qquad C=10^6\text{ passes through }X=10^7.              \tag{8}
\]

In particular, (7) proves only the finite inequality
`H(X)<=Q(X)+10^6 E(X)` on this range.  It does not prove (T), and it cannot be
extrapolated asymptotically.

## 7. Smallest surviving explicit lemma and falsifier gate

For \(U\subseteq E_X\), define

\[
 \begin{aligned}
 \mathcal H_X(U)&=\{h\in H_X:L(h)\subseteq U\},\\
 \mathcal Q_X(U)&=\{q\in\mathcal Q_X:L(q)\cap U\ne\varnothing\}.
 \end{aligned}
\]

The remaining arithmetic statement is:

> **Arithmetic shadow expansion (`ASE_C`).**  There is an absolute finite
> `C` such that, for every `X` and every \(U\subseteq E_X\),
> \[
>  |\mathcal H_X(U)|\le C|U|+|\mathcal Q_X(U)|.           \tag{9}
> \]

This is not a matching reformulation of the scalar target.  It asserts that
every concentration of actual death-rank shadows either expands into
splitless leaves or forces healed seed-2 chains to enter those leaves.  It is
strictly stronger than `H<=Q+C E`.

Equation (9) supplies Hall's inequalities for `D_C(X)`: for any source set
`S`, take \(U=\bigcup_{h\in S}L(h)\).  Then

\[
 |S|\le|\mathcal H_X(U)|
 \le C|U|+|\mathcal Q_X(U)|,
\]

which is exactly the available local resource count.  Hence `ASE_C` implies
flow saturation and Proposition 3.1.  Conversely, the finite flow
certificate (7) verifies (9) for `C=10^6` and `X<=10^7`.

The exact falsifier gate for any proposed `C` is:

1. Generate `G`, ranks, and all shadows through `X`.
2. Insert `H`, `E`, and child-coordinate `Q` events into `D_C(X)`.
3. Stop at the first source with no augmenting path.
4. Emit the residual min-cut.  A cut below `H(X)` is an independently
   checkable counterexample to (9).

The recurrence alone cannot prove (9).  An abstract rank-one star may have
one splitless leaf, `N` hard vertices each descending to that leaf, and no
`Q` exit.  It obeys the bare rule that every reducible vertex has a
lower-rank missing factor, yet has `(H,Q,E)=(N,0,1)` for arbitrary `N`.
This is not a counterexample inside `G`; it proves that any successful
argument must use arithmetic fan-in control or forced seed-2 exits in
addition to rank descent.

## 8. Why any absolute bank constant closes density

C23 proves, with

\[
 Y=\left\lfloor\frac{X+1}{2}\right\rfloor,
 \qquad Z=\left\lfloor\frac{X+1}{3}\right\rfloor,
\]

that the reducible-hole count `R(X)=M(X)-E(X)` satisfies

\[
 R(X)\le M(Y)-Q(X)+M(Z)+H(X).                            \tag{10}
\]

If `H(X)<=Q(X)+C E(X)` for one absolute `C`, then

\[
 M(X)\le M(Y)+M(Z)+(C+1)E(X).                           \tag{11}
\]

Let `delta=limsup M(X)/X`.  C13 gives `E(X)=o(X)`.  Divide (11) by `X`
and take limsups to obtain

\[
 \delta\le\frac12\delta+\frac13\delta=\frac56\delta.
\]

Thus `delta=0`, so

\[
 |G\cap[1,X]|=\frac{2X}{3}+o(X).
\]

In particular, the exact weaker target (T), corresponding to `C=1`, is
sufficient via C13/C16, as is `ASE_C` for any fixed absolute `C`.

## 9. Verification and reproducibility

The independent verifier reconstructs `G` by trial division through
`10000`, compares ranks with literal descending approximants through `500`,
replays the expanded `C=1,2` failures, checks the compact `C=1,...,4`
artifacts, and cross-checks the `10^7` census against C23.  It reports
`status: PASS` in `verify_result.json`.

From the repository root:

```powershell
g++ -O3 -std=c++20 -Wall -Wextra -pedantic `
  problems/424/compute/wave3/C38_splitless_bank/splitless_bank.cpp `
  -o problems/424/compute/wave3/C38_splitless_bank/splitless_bank.exe

problems/424/compute/wave3/C38_splitless_bank/splitless_bank.exe `
  10000000 problems/424/compute/wave3/C38_splitless_bank/result_1e7.json

g++ -O3 -std=c++20 -Wall -Wextra -pedantic `
  problems/424/compute/wave3/C38_splitless_bank/dag_bank_flow.cpp `
  -o problems/424/compute/wave3/C38_splitless_bank/dag_bank_flow.exe

problems/424/compute/wave3/C38_splitless_bank/dag_bank_flow.exe `
  10000000 40 `
  problems/424/compute/wave3/C38_splitless_bank/dag_cpp_C40_1e7.json

python problems/424/compute/wave3/C38_splitless_bank/verify_small.py `
  --output problems/424/compute/wave3/C38_splitless_bank/verify_result.json
```

Key SHA-256 values:

| file | SHA-256 |
|---|---|
| `splitless_bank.cpp` | `E7832708301990B183B6201857742964B0EBDF5DF8B22F0E895A0B6FB9228C37` |
| `dag_bank_flow.cpp` | `49B0C34D7499C12917CEA17E739986796F170B94ADCEE242CFEF28196D2675F1` |
| `verify_small.py` | `07264E862277BF8C750DFD2F438B51AD930E1C2C8B83B73C3D3C166C785B6A16` |
| `result_1e7.json` | `BA9E8E159EF6766E6F8F4710C0025B9A26BDFD461BC42A34BF660320DF30E0AA` |
| `dag_1e4.json` | `2424ADED2C326EB54CFE56719353FD0FF6C52D2B027209A379C8B54612D20BD1` |
| `dag_cpp_C40_1e7.json` | `A5CF97DB0B6D6D257B80B843A75BB39F499A85FCF4AB24A91B6A4C6EA28A947D` |
| `dag_cpp_C1000000_1e7.json` | `A5885689663D5292AA6D58414F6C621076FB9A9213A86955ED9015ABA5E43B76` |
| `verify_result.json` | `49EF6A264E8DFDFFF510413D279EF259F8F925C79A2248D460654DC37C2EE723` |

## 10. Novelty gate and scope

The 2026-07-13 novelty check remains negative for prior resolution: the
[Erdos Problems page](https://www.erdosproblems.com/424) records Problem 424
as open, and the local `A04_modern_literature.md` audit found no theorem for
this dynamically expanding restricted product closure.  The present output
is therefore a finite exact audit and a new local frontier formulation, not
a claim that the density problem has been solved.
