# C51: image-stage capacity and factor-component obstruction

## Verdict

No capacity map proving

\[
H_{F(S)}(X)\le Q_{F(S)}(X)+1
\]

or the C43 terminal first-two-exit gate was obtained.

There is, however, an exact obstruction inside a genuine image set.  Put

\[
S_0={\cal A},\qquad S_{j+1}=F(S_j),\qquad T=S_3=F(S_2),
\]

where every product witness has distinct inputs.  At `X=318`, no injection
can send each hard hole to an arrived `T`-boundary lying in a canonical C43
component of any missing factor endpoint.  The Hall set is

\[
\{54,74,186,318\}\quad\hbox{versus}\quad\{41,57,63\}. \tag{1}
\]

This allows every missing endpoint, every depth in its canonical component,
and every active exit, not merely a selected parent or the first two exits.
The critical-endpoint restriction already fails on

\[
\{54,186,318\}\quad\hbox{versus}\quad\{41,63\}.       \tag{2}
\]

Thus the image condition supplies local exits but not unit capacity.  A
proof must transport capacity from components unrelated to all factor
endpoints of the hard source.  This is stronger than the CX-R5 warning that
mere forward closure is insufficient: `S_3` is literally an image.

## 1. Conventions

Let

\[
{\cal A}=\{n\ge2:n\not\equiv1\pmod3\},
\]

and use

\[
F(S)=\{2,3\}\cup\{ab-1:2\le a<b,\ a,b\in S\}.         \tag{3}
\]

The strict inequality `a<b` is used in every proof and computation below.
For a hole of the least fixed point `G`, let `rho` be the C31 obstruction
rank.  Then

\[
\rho(n)=r\quad\Longleftrightarrow\quad
n\in S_r\setminus S_{r+1}.                             \tag{4}
\]

For rank cutoff `d`, write

\[
T_d=S_{d+1}.
\]

Thus the holes of `T_d` are exactly the `G`-holes with rank at most `d`.
A seed-2 boundary of `T_d` is an edge

\[
q\notin T_d,\qquad U(q)=2q-1\in T_d.                  \tag{5}
\]

It contributes to `Q_(T_d)` at child coordinate `U(q)`.

Canonical components are those of C39/C43: an odd hole has seed-2 parent
`(n+1)/2`, a seed-3-easy even hole has seed-3 parent `(n+1)/3`, and
splitless and hard holes are roots.

## 2. What the image condition does give

### Lemma 1 (two-step birth exit)

Let `h` be a hard hole of rank `r`, and let `p` be a critical missing
endpoint in an admissible factorization

\[
h+1=pq,\qquad \rho(p)=r-1.                              \tag{6}
\]

In the genuine image `T_r=S_(r+1)`, either `U(p)` is a boundary child or
`U^2(p)` is a boundary child.  In both cases the child is at most `h`.

### Proof

The parent `p` is absent from `T_r`.  If `U(p)` belongs to `T_r`, then
`p -> U(p)` is the required boundary.  Otherwise seed-2 rank increase gives

\[
\rho(U(p))\ge r.
\]

Absence from `T_r` gives the reverse inequality, so `rho(U(p))=r`.  A second
seed-2 step has rank at least `r+1` if it is a hole, and hence belongs to
`T_r`; generated values also belong to `T_r`.  Therefore
`U(p) -> U^2(p)` is a boundary.

Since `h` is even, both factors in (6) are odd.  Neither factor can be `3`,
because that would be a usable distinct seed-3 factorization of the hard
integer `h`.  Hence `q>=5`, and

\[
U^2(p)=4p-3\le pq-1=h.                                 \tag{7}
\]

This proves the lemma. QED.

The exact scan checked all `52,777` critical endpoint uses through
`10^6` and found no violation of Lemma 1.  The lemma is availability only:
at rank two, the birth boundary `41` is selected by `7,043` distinct hard
sources through `10^6` (first sources `54,186,252,318,362`; last `999822`).

## 3. Broad local capacity rule

For a hard `T_d`-hole `h`, define `E_d(h)` to contain every endpoint `p`
which is itself absent from `T_d` and occurs in any admissible distinct
factorization `h+1=pq`.  This is broader than the source-blocker set: an
endpoint may lie in `S_d` and still be absent from `T_d`.

Let `C(p)` be the canonical C43 component of `p`.  Give `h` every arrived
boundary whose parent is in one of these components:

\[
N_d(h)=\{2m-1\le h:m\notin T_d,\ 2m-1\in T_d,
 C(m)=C(p)\text{ for some }p\in E_d(h)\}.               \tag{8}
\]

Rule (8) has no depth bound and no first-two cap.  Any factor-local or
factor-component capacity injection is a subgraph of (8).

### Proposition 2 (exact Hall falsifier)

Rule (8) has no matching at `(d,X)=(2,318)`.

### Exact certificate

Literal trial division and literal synchronous approximants give

| value | rank | canonical component | fact |
|---:|---:|---:|:---|
| `6` | `0` | `6` | splitless root |
| `8` | `0` | `8` | splitless root; `3*3` is forbidden |
| `11` | `1` | `6` | seed-2 child of `6` |
| `15` | `1` | `8` | seed-2 child of `8` |
| `21` | `2` | `6` | seed-2 child of `11` |
| `29` | `2` | `8` | seed-2 child of `15` |
| `32` | `2` | `6` | seed-3 child of `11` |
| `41` | generated | - | boundary child of `21` |
| `57` | `3` | `8` | boundary child of `29` in `S_3` |
| `63` | `3` | `6` | boundary child of `32` in `S_3` |

The four hard rank-two holes have complete admissible pair lists

\[
55=5\cdot11,\quad 75=5\cdot15,\quad
187=11\cdot17,\quad 319=11\cdot29.                    \tag{9}
\]

There are no other `S_3` seed-2 boundaries through `318` in components `6`
or `8`.  Consequently

| hard source | endpoint components | full neighborhood from (8) |
|---:|:---:|:---|
| `54` | `{6}` | `{41}` |
| `74` | `{8}` | `{57}` |
| `186` | `{6}` | `{41,63}` |
| `318` | `{6,8}` | `{41,57,63}` |

The union of the four neighborhoods has size three, proving (1) by Hall's
theorem.  If only critical rank-one endpoints are admitted, the sources
`54,186,318` all use component `6`, whose complete arrived boundary set is
`{41,63}`.  This proves (2).

The same computation gives the first failures of four rules:

| proposed capacity neighborhood | first failure | exact Hall defect |
|:---|:---:|:---|
| critical endpoint's seed-2 chain | `(d,X)=(2,186)` | `{54,186}` / `{41}` |
| every endpoint's seed-2 chain | `(2,186)` | `{54,186}` / `{41}` |
| critical endpoint components | `(2,318)` | `{54,186,318}` / `{41,63}` |
| every missing endpoint component | `(2,318)` | (1) |

These are failures of capacity maps, not failures of the global image
inequality.

## 4. Further exact gates through one million

`C51_image_capacity.py` independently computes exact divisors, `G`, ranks,
canonical components, and every `T_d` boundary.  It then separately builds
the literal synchronous sets `S_0,S_1,...` through `10^6`.  Stabilization
occurs after 17 updates, and all `11,333,322` literal stage-membership checks
agree with (4).

The terminal census is

~~~text
limit                  1,000,000
generated                457,599
holes                    209,067
hard holes                45,583
terminal seed-2 exits     67,537
maximum hole rank             15
maximum hard rank             14
~~~

At every hard cutoff `X<=10^6` and every `d=0,...,15`:

1. the full genuine-image count satisfies
   `H_(T_d)(X) <= Q_(T_d)(X)`;
2. retaining only the first two active `T_d` boundaries in each canonical
   component still satisfies the strict inequality;
3. C43's first two terminal exits satisfy additive one.

All three are finite checks only.  The first two have maximum excess zero,
first attained at `X=54`; the C43 terminal gate has maximum excess one at
`(X,d)=(362,2)`.

A smaller proposed reservoir is exactly false.  If only boundaries in
splitless-root components are retained, then for `T_6=S_7` at `X=956`,

\[
H_{T_6}(956)=40,\qquad Q^{\rm splitless}_{T_6}(956)=38. \tag{10}
\]

Thus even additive one requires exits from hard-root components.  Combined
with Proposition 2, the capacity must use both hard-root components and
cross-component transport not determined by the factor endpoints of the
current source.

## 5. Precise obstruction

The image hypothesis has a rigorously identified local effect: every new
hard hole has an arrived boundary within two seed-2 steps of a critical
endpoint (Lemma 1).  What it does not provide is capacity.  The same endpoint
can support thousands of hard outputs, and even the union of all endpoint
components has a finite Hall defect in the third descending image.

Therefore none of the following data can support the requested injection:

* the chosen critical factor;
* all missing factor endpoints;
* their full seed-2 chains;
* their full canonical C43 components; or
* splitless-root components alone.

Any proof of the global image inequality or C43 gate must specify a global
transport rule that reaches unrelated hard-root components.  This is the
obstruction returned by C51; no inequality or density theorem is claimed.

## 6. Reproduction

From the repository root:

~~~powershell
python problems/424/fanout/wave5/C51_image_capacity.py `
  --limit 1000000 --literal-limit 1000000 --summary
~~~

The command uses one process and writes no auxiliary artifact.

~~~text
C51_image_capacity.py
8E0AFFCAB63FDB7B9DD5B7887CD7B4A372F0F4F76DC70C8BF5EA309E5A924730
~~~
