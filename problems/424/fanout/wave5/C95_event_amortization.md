# C95: quarter-scale event amortization

## Verdict

The global estimate

\[
 A_H(X)\le D(X)+A_H(\lfloor X/4\rfloor)+O(1)             \tag{QA}
\]

is not proved or falsified here.  What is proved is an exact birth-death
identity reducing `(QA)` to one signed event balance.  Exact all-cutoff
computation through `X=10^9` gives

\[
 \min_{2\le X\le10^9}
 \{D(X)+A_H(\lfloor X/4\rfloor)-A_H(X)\}=-1,             \tag{1}
\]

with the minimum first attained at `X=186`.  Thus the candidate `(QA)` with
constant `1` survives this range, and no smaller constant is possible.

There is, however, a rigorous obstruction to the natural local proof.  A
capacity-one matching which pays a hard root only from the seed-2 roots of
its missing factor endpoints already has Hall deficit four at `X=186`.
Moreover, the infinite family `11p-1` proves that charging each hard source
to a healed event on its own minimum-critical descent chain has unbounded
multiplicity.  Any proof of `(QA)` must therefore pool the bank globally
across arithmetically unrelated generation-DAG components; own-factor or
own-critical-chain accounting cannot prove it.

## 1. Exact event identity

Use the C91/C93 definitions.  Put `U(r)=2r-1`.  For a hard even root `r`,
write

\[
 b(r)=r,
 \qquad
 d(r)=\min\{U^j(r):U^j(r)\text{ is generated}\},
\]

with `d(r)=infinity` if the chain never reaches a generated value.  Hence

\[
 r\text{ is counted by }A_H(X)
 \quad\Longleftrightarrow\quad b(r)\le X<d(r).            \tag{2}
\]

For a structural splitless root `e`, let `tau(e)` be the first generated
member of its seed-2 chain, again allowing infinity.  Then

\[
 D(X)=\sum_e 1_{\tau(e)\le X}.                            \tag{3}
\]

Set `q=floor(X/4)` and define

\[
\begin{aligned}
 \operatorname{Fresh}_X
   &=\{r:q<b(r)\le X<d(r)\},\\
 \operatorname{Lost}_X
   &=\{r:b(r)\le q<d(r)\le X\}.
\end{aligned}                                             \tag{4}
\]

### Lemma C95.1 (birth-death identity)

For every integer `X>=2`,

\[
 A_H(X)-A_H(q)
 =|\operatorname{Fresh}_X|-|\operatorname{Lost}_X|,       \tag{5}
\]

and therefore

\[
\boxed{
 F(X):=D(X)+A_H(q)-A_H(X)
 =D(X)+|\operatorname{Lost}_X|-|\operatorname{Fresh}_X|.
}                                                         \tag{6}
\]

#### Proof

For each hard root compare its two indicators in (2), first at `q` and then
at `X`.  A contribution `+1` to `A_H(X)-A_H(q)` occurs exactly when the root
is born after `q` and is still alive at `X`, which is `Fresh_X`.  A
contribution `-1` occurs exactly when it is alive at `q` and dies by `X`,
which is `Lost_X`.  All other roots contribute zero.  This proves (5), and
adding `D(X)` proves (6).  QED.

Equivalently, each hard root contributes

\[
 1_{4b(r)\le X<4d(r)}-1_{b(r)\le X<d(r)}                 \tag{7}
\]

to `F`, while a splitless healing contributes `1` from its healing time
onward.  Thus the signed events are precisely

```text
hard birth at b             -1
hard death at d             +1
quarter-scaled birth at 4b  +1
quarter-scaled death at 4d  -1
splitless healing at tau    +1 permanently.
```

This is an identity, not a heuristic pairing.

### Corollary C95.2 (why `(QA)` closes Problem 424)

If `F(X)>=-C` for one absolute constant `C` and all `X`, then
`A_H(X)=o(X)`.  Consequently the least generated set has density `2/3`.

#### Proof

The hypothesis gives

\[
 A_H(X)\le D(X)+A_H(\lfloor X/4\rfloor)+C.               \tag{8}
\]

C13 gives `E(X)=o(X)`, and `0<=D(X)<=E(X)`, so `D(X)=o(X)`.  Iterate (8)
until the argument is bounded.  For every `epsilon>0`, once all unbounded
arguments satisfy `D(t)<=epsilon t`, the resulting geometric sum is at most

\[
 \epsilon X\sum_{j\ge0}4^{-j}+O(\log X)
 ={4\epsilon\over3}X+o(X).                               \tag{9}
\]

Letting `epsilon` tend to zero gives `A_H(X)=o(X)`.  C72 Theorem 1 then gives
the density conclusion.  QED.

## 2. A second exact decomposition

Let `B_3^{heal}(X)` count healed even root chains of the third C67 type:
neither hard nor structural splitless.  This notation is distinct from
C72's mature-factor-3 set.  Pure algebra gives

\[
 F(X)=A_H(q)-B_3^{heal}(X)
      -\bigl(A_H(X)-D(X)-B_3^{heal}(X)\bigr).             \tag{10}
\]

C67 identifies the expression in parentheses with the actual maximal-source
shell `H-Q`.  Therefore the two statements

\[
 A_H(X)-D(X)-B_3^{heal}(X)\le0,                           \tag{11}
\]

\[
 B_3^{heal}(X)\le A_H(\lfloor X/4\rfloor)+C              \tag{12}
\]

would imply `(QA)`.  Neither is proved here.  They are recorded because the
exact scan gives especially small residuals: (11) has no failure through
`10^9`, and the maximum of the left side of (12) minus its right side with
`C=0` is `8`, first attained at `X=3620`.

## 3. Exact all-cutoff scan through `10^9`

`C95_quarter_event_census.cpp` reconstructs the least generated set by exact
divisor enumeration.  It evaluates the quarter statistics at every integer
cutoff, not only at event cutoffs.  Acceptance uses integer arithmetic only.

At `X=10^9` the endpoint counts are

```text
A_H = 15,106,735
D   = 40,909,363
B_3^{heal} = 770,656
```

The exact extrema over every `2<=X<=10^9` are

| quantity | extremum | first cutoff |
|---|---:|---:|
| `F=D+A_H(floor(X/4))-A_H` | minimum `-1` | `186` |
| `7*A_H(floor(X/4))-2D` | maximum `0` | `2` |
| `7*A_H-9D` | maximum `0` | `2` |
| `A_H-D-B_3^{heal}` | maximum `0` | `2` |
| `B_3^{heal}-A_H(floor(X/4))` | maximum `8` | `3620` |

The first line says that `C=1` in `(QA)` has no finite falsifier in the
scanned range.  It is finite evidence only.  The third line is another
finite gate for the direct C91 estimate `A_H<=(9/7)D`, again not a proof.

Two complete C++ runs were byte-identical.  Their JSON SHA-256 is

```text
19912E10C765B881BBE04E07BB60F5795CB10F197939CAA40699AAFF5CD3B997
```

The classification digest is `ecefb1de7848e5d3`, exactly the C93 digest.
The event digest differs from C93 because C95 additionally treats seed-3
healings as events.

## 4. Finite factor-local Hall obstruction

Consider the following natural attempted proof of (6): join each fresh hard
root to the seed-2 root of every missing endpoint in one of its admissible
factor pairs, retain only targets in

\[
 D(X)\cup A_H(\lfloor X/4\rfloor),                        \tag{13}
\]

and seek a capacity-one matching.

At `X=186`, exact reconstruction gives

\[
 A_H(186)=\{54,74,114,144,174,186\},
\]

\[
 D(186)=\{6,18,20,38,66\},
 \qquad A_H(46)=\varnothing.                              \tag{14}
\]

Before intersecting with the bank, the missing-endpoint root neighborhoods
are

```text
54  -> {6}       from (5,11)
74  -> {8}       from (5,15)
114 -> {12}      from (5,23)
144 -> {8}       from (5,29)
174 -> {18}      from (5,35)
186 -> {6}       from (11,17).
```

After (13), all six sources have combined neighborhood `{6,18}`.  Hall's
condition fails by `6-2=4`.  Notice that the global bank has five elements:
the roots `20,38,66` which make the scalar count nearly work are unrelated
to every source under this factor-local relation.  This is the smallest
observed scalar deficit as well:

\[
 A_H(186)-D(186)-A_H(46)=1.                               \tag{15}
\]

`C95_local_obstruction.py` reconstructs (14)-(15) directly by trial-divisor
enumeration.  Normal and `python -O` outputs are byte-identical with SHA-256

```text
9FEF54B72D5AF76E05F19F2F4C6DC62E2F46416F243360FDE571E2FF8E713022.
```

Hence factor-endpoint-local unit matching is exactly false.  The finite
witness does not by itself falsify an `O(1)` scalar remainder.

## 5. Infinite critical-chain obstruction

The finite failure is not merely an initial irregularity for own-chain
charging.  C55 Proposition 5 gives an infinite forced star.  If `p=5`, or
if `p>11` is prime with `p=2 mod 3`, then

\[
 h_p=11p-1                                             \tag{16}
\]

is a hard root with the unique admissible pair `(11,p)`.  Its least critical
endpoint is `11`, and its selected descent is

\[
 h_p\longrightarrow11\longrightarrow6.                  \tag{17}
\]

The root `6` is structural splitless and its entire relevant seed-2 chain is

\[
 6\longrightarrow11\longrightarrow21\longrightarrow41,  \tag{18}
\]

where `41` is generated.  Thus (18) supplies one healed local event, shared
by every source (16), not one event per source.

For a cutoff `X`, take primes for which

\[
 (X+1)/2<h_p\le X.                                      \tag{19}
\]

Every such root is counted by `A_H(X)`, since its next seed-2 child exceeds
`X`.  The prime number theorem in arithmetic progressions gives

\[
 \#\{p:(19),\ p=2\pmod3\}
 \sim {X\over44\log X}.                                 \tag{20}
\]

Therefore any rule assigning a bounded number of sources to the healed
event on their own minimum-critical descent leaf has unbounded deficit.
Even if one additionally grants every earlier member of the same prime-star
family with `h_p<=X/4` as one capacity-one quarter-bank token, there are only

\[
 \sim {X\over88\log X}                                  \tag{21}
\]

such tokens.  The unmatched deficit in (20)-(21) is asymptotic to
`X/(88 log X)`, not `O(1)`.

This proves the following precise negative result.

### Proposition C95.3 (no own-critical-chain unit amortization)

There is no event proof of `(QA)` in which each fresh hard source is paid,
with capacity one and `O(1)` total exceptions, only by a healing event on its
selected minimum-critical descent chain, even after allowing earlier members
of the same `11p-1` star as quarter-bank tokens.

The proposition does not falsify `(QA)`: a global proof may match the star to
unrelated roots in `D` or to unrelated old hard roots.  It shows that this
nonlocal pooling is logically necessary.

## 6. Reproduction

From the repository root:

```powershell
g++ -std=c++20 -O3 -DNDEBUG -Wall -Wextra -Wconversion -Wshadow -march=native `
  -o problems/424/compute/wave5/C95_quarter_event_census.exe `
  problems/424/compute/wave5/C95_quarter_event_census.cpp

problems/424/compute/wave5/C95_quarter_event_census.exe `
  1000000000 `
  problems/424/compute/wave5/C95_quarter_event_1e9.json

python problems/424/compute/wave5/C95_local_obstruction.py
python -O problems/424/compute/wave5/C95_local_obstruction.py
```

Toolchain:

```text
g++.exe (Rev5, Built by MSYS2 project) 16.1.0
Python 3.12.4
```

Source SHA-256 values:

```text
EC7D3B3B3906DB44BC28F00F92C724897E7B9779B93D52F5E66A661B5E60EF47  C95_quarter_event_census.cpp
CAE5A2695B51B4E3A7A9AFB738A2422FB53BC50325105F29D9CE1F67F4A1D428  C95_event_amortization.py
4F3E08792EFF5C10A7CC4403D15A2685E4585B82F4576E31B6C4BA248FE6F5A2  C95_local_obstruction.py
```

## 7. Exact status

The quarter recurrence is a viable theorem target and is stronger than
needed because it alone implies `A_H=o(X)`.  It has no falsifier through
`10^9`, and the smallest possible constant is `1`.  No structural proof is
known.  The exact obstruction is that the available scalar bank is genuinely
global: local factor and selected critical-chain events do not have enough
capacity, finitely or asymptotically.
