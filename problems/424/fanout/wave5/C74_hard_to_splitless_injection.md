# C74: obstruction to a hard-to-upper-splitless injection

## Verdict: (iii) precise obstruction and weakest corrected statement

No proof or counterexample was found for

\[
 K(X)\le E(X)-E(\lfloor X/2\rfloor).                    \tag{T}
\]

The finite gate below independently verifies (T) at every cutoff through
`10^6` and agrees with C71, but this is not used as a proof.

There is an unconditional canonical arithmetic target for every hard hole.
If `p(h)` is the least prime `2 mod 3` dividing `h+1`, then

\[
 \boxed{\sigma(h)=p(h)^2-1\text{ is a splitless hole and }
        \sigma(h)\le h.}                                \tag{1}
\]

This is the weakest corrected version of the prime-stripping injection that
survives: its target is not always in the upper half and the map is not
injective.  Both failures are grounded and immediate.  At `X=54`, the hard
hole `54` maps to `24<=27`; at `X=74`, the two hard holes `54,74` both map
to `24`.

Broader factor-local relations also fail.  At `X=114`, the hard holes
`54` and `114` have only the common upper-half splitless target `90` under
the union of prime-square, prime-free-core, and obstruction-leaf lifts.
Thus this union has an exact Hall deficit `2>1` even though (T) has ample
scalar slack there.

A genuinely nonlocal, cutoff-dependent core-replacement relation has no
Hall failure through every cutoff `X<=2000` and at selected cutoffs through
`10^6`.  It does not yield a proof: its total-set Hall inequality is exactly
(T).  Moreover, the corresponding structure-only semigroup count is false.
Its first exact failure is at `Y=26989`, or structural cutoff
`X=3Y-1=80966`, with `1215` sources and `1214` targets.  Therefore any proof
of (T) must use grounded membership in the least closure, not just residues,
prime support, a fixed arithmetic substitution, or local obstruction leaves.

## 1. Exact definitions

Put

\[
 \mathcal A=\{n\ge2:n\not\equiv1\pmod3\}.
\]

For `n in A`, let

\[
 \mathcal P(n)=\{(a,b):n+1=ab, 2\le a<b, a,b\in\mathcal A\}. \tag{2}
\]

Let `G` be the least subset of `A` containing `2,3` and closed under
`(a,b)->ab-1` for distinct inputs.  Since every endpoint in (2) is less
than `n`, the exact ascending recursion is

\[
 n\in G\iff n\in\{2,3\}
 \quad\text{or}\quad
 \exists(a,b)\in\mathcal P(n),\ a,b\in G.              \tag{3}
\]

A **hole** is a member of `M=A\G`.  A hole is **splitless** when
`P(n)` is empty.  Write `E(X)` for the number of splitless holes at most
`X`.

A **hard hole** is a hole `h` such that

1. `h` is even;
2. `P(h)` is nonempty; and
3. it has no usable seed-3 pair: it is not the case that `3|(h+1)`,
   `(h+1)/3` is allowed, and `(h+1)/3 != 3`.

Write `K(X)` for the number of hard holes at most `X`.  These are exactly
the C67/C71 definitions.  In particular, hardness includes actual absence
from the least closure; a merely hard-shaped generated integer is not
counted.

## 2. Structural classifications

Let `N=n+1`, and call an ordinary prime `p` a minus prime when
`p=2 mod 3` and a plus prime when `p=1 mod 3`.

### Lemma 1 (splitless successors)

For an allowed `n`, the following characterize `P(n)=empty`.

1. If `N=1 mod 3`, then either `N` has no minus-prime divisor, or
   `N=p^2` for one minus prime `p`.
2. If `3|N`, write `N=3^a R` with `3` not dividing `R`.  Then either
   `a=1` and `R` has no minus-prime divisor, or `N=9`.

### Proof

Suppose first that `N=1 mod 3`.  Every admissible factor pair must have
both factors `2 mod 3`.  If a minus prime `p` divides `N`, then
`p*(N/p)` is such a pair unless the factors are equal, which occurs only
when `N=p^2`.  Conversely, without a minus-prime divisor no divisor can be
`2 mod 3`.  The square `p^2` has only the equal candidate `(p,p)` and is
therefore splitless under the distinct-input rule.

Now suppose `3|N`.  If `a>=2`, the pair `3*(N/3)` is admissible and
distinct except at `N=9`.  If `a=1` and a minus prime `p` divides `R`, then
`p*(3R/p)` is admissible and cannot have equal factors.  If no such `p`
exists, every divisor not divisible by `3` is `1 mod 3`, so no admissible
pair exists.  This proves both directions.  QED.

### Lemma 2 (hard-shape residues)

An even reducible allowed integer is hard-shaped exactly in residues

\[
                         0,2,3,6\pmod9.                  \tag{4}
\]

For such an integer, its successor contains either no factor `3`, or
exactly one factor `3` and the remaining cofactor is `1 mod 3`.

### Proof

If `3` does not divide `N`, then `n=0 mod 3`, giving residues `0,3,6`
modulo `9`, and no seed-3 pair exists.  If `3|N`, the seed-3 cofactor is
forbidden exactly when `N/3=1 mod 3`, equivalently `N=3 mod 9` and
`n=2 mod 9`.  The exceptional cofactor `3` gives `n=8`, whose successor
is `9=3^2`; it is splitless and hence not reducible.  QED.

## 3. Proved corrected canonical charge

### Theorem 3 (prime-square shadow)

Let `h` be any hard hole.  Let `p(h)` be the least minus prime dividing
`h+1`.  Then (1) holds.  More strongly, the colored map

\[
 h\longmapsto
 \left(p(h)^2-1,{h+1\over p(h)}\right)                 \tag{5}
\]

is injective.  Consequently, for every `X`,

\[
 K(X)\le
 \sum_{\substack{p\le\sqrt{X+1}\\p\equiv2\ (3),\ p\ge5}}
 \left(\left\lfloor{X+1\over p}\right\rfloor-p+1\right), \tag{6}
\]

where the sum is over ordinary primes.

Equivalently, (6) gives the splitless prime-square target `p^2-1` the
explicit capacity `floor((X+1)/p)-p+1`.  It is therefore a proved
variable-capacity splitless-bank inequality.  Capacity one and upper-half
location are exactly the two properties removed from (T).

### Proof

Put `N=h+1`.  By Lemma 2, after deleting the possible single factor `3`,
`N` is `1 mod 3`.  Hence the number of minus-prime factors of `N`, counted
with multiplicity, is even.  It is positive because Lemma 1 would otherwise
make `h` splitless.  It is therefore at least two.

The integer `N` is odd, so its least minus prime `p=p(h)` is at least `5`.
The product of all minus-prime factors is at least `p^2` and divides `N`;
hence `p^2<=N`.  The value `p^2-1` is allowed, is not a seed, and has no
distinct admissible factor pair because its successor is the prime square
`p^2`.  It is therefore a splitless hole and is at most `N-1=h`.

In (5), the first coordinate recovers `p` and the second recovers `N`, so
the map is injective.  For fixed `p`, its second coordinate is an integer
between `p` and `floor((X+1)/p)`.  Counting these possible colors and then
summing over `p` proves (6).  QED.

The color in (5) has unbounded range, so (6) is not a capacity-one charge
to `E`.  The next two exact examples show that neither missing property in
(1) can simply be restored.

### First loss of upper-half location

The values `6` and `8` are splitless: their successors are respectively
the prime `7` and the equal square `3^2`.  Thus `11` is a hole because its
only admissible pair is `(2,6)`.  Since `5=2*3-1` is generated,

\[
                         54+1=5\cdot11                  \tag{7}
\]

is the unique admissible pair of a hole.  The value `54=0 mod 9` is hard.
But `p(54)=5`, so

\[
                         \sigma(54)=24\le27=54/2.       \tag{8}
\]

### First collision

The value `15` is a hole because its only admissible pair is `(2,8)`.
Moreover,

\[
                         74+1=5\cdot15                  \tag{9}
\]

is its only admissible pair: `3*25` is forbidden because `25=1 mod 3`.
Thus `74` is a hard hole in residue `2 mod 9`.  Equations (7)-(9) give

\[
                         \sigma(54)=\sigma(74)=24.      \tag{10}
\]

These are statements about the actual least closure, not abstract closed
supersets.

## 4. Exact Hall obstruction to factor-local repairs

For a hard successor `N`, define its **plus core**

\[
 c(N)=N/\prod_{p\equiv2\ (3)}p^{v_p(N)}.                \tag{11}
\]

For a hole, use the C38 all-lower splitless shadow `L(n)`: rank-zero holes
have shadow `{n}`, and a reducible hole takes the union of the shadows of
all lower-rank missing blockers in every admissible pair.  The rank is

\[
 \rho(n)=1+\max_{(a,b)\in\mathcal P(n)}
 \min\{\rho(x):x\in\{a,b\}\cap\mathcal M\}.            \tag{12}
\]

At cutoff `X`, join a hard hole `h` to an upper-half splitless hole `e` if
at least one of the following holds:

1. `e=p^2-1` for a minus prime `p|h+1`;
2. `c(h+1)>1` and `c(h+1)|(e+1)`; or
3. `l+1|e+1` for some `l in L(h)`.

This relation contains the canonical square targets, completion after
stripping all minus primes while retaining a nontrivial core, and every
multiplicative lift of a grounded splitless obstruction leaf.

### Proposition 4 (first Hall deficit for the union)

At `X=114`, the hard source set `{54,114}` has neighborhood `{90}`.
Therefore this factor-local union admits no injection.

### Proof

The complete upper-half splitless set is

```text
{60,66,72,78,90,92,96,102,108,110}.
```

Its successor factorizations are

```text
61, 67, 73, 79, 7*13, 3*31, 97, 103, 109, 3*37.
```

For `54`, equation (7) gives minus primes `5,11`, core `1`, and
`L(54)={6}`.  Its square targets are `24,120`, outside the shell, and the
only listed successor divisible by `6+1=7` is `91`; hence its only neighbor
is `90`.

The value `23` is a hole: the admissible pairs of `24` are `(2,12)` and
`(3,8)`, blocked by the splitless holes `12` and `8`.  Therefore

\[
                         114+1=5\cdot23                 \tag{13}
\]

makes `114` a hard hole, with core `1` and `L(114)={8,12}`.  Its square
targets are `24,528`.  Among the listed successors, only `91` is divisible
by either `9` or `13`.  Thus its neighborhood is also `{90}`, proving the
Hall deficit.  QED.

The obstruction-leaf relation alone fails even earlier: at `X=74`, the
source `74` has `L(74)={8}`, but no upper-half splitless successor is
divisible by `9`.

## 5. Prime-pair substitutions still collide

A more global candidate pairs the minus-prime factors of `h+1` in sorted
order and replaces each pair product `y` by either

1. the largest prime `q<=y`, `q=1 mod 3`; or
2. the largest integer `s<=y` all of whose prime factors are `1 mod 3`.

The plus core is retained.  Both rules always produce a splitless successor
not exceeding the source successor.  Exact testing found no source-shell
location failure through `2000`, but both rules first collide at hard holes
`444` and `450`:

\[
 444+1=5\cdot89,
 \qquad
 450+1=11\cdot41.                                      \tag{14}
\]

The largest replacement below both `445` and `451` is `439`, so both maps
send (14) to the splitless hole `438`.

These sources are grounded.  The value `41` is generated via
`5=2*3-1`, `14=3*5-1`, and `41=3*14-1`, while `11` is the hole above.
For `89`, the complete admissible pairs are

```text
(2,45), (3,30), (5,18), (6,15).
```

Here `6,18,30` are splitless, `15` is blocked by `8`, `45` is blocked by
`23`, and `23` is blocked by `8,12`.  Hence `89` is a hole.  The products
in (14) are unique admissible pairs, and residues `3,0 mod 9` make both
outputs hard.

There is also a general scale obstruction.

### Proposition 5 (a fixed injection cannot serve all cutoffs)

No cutoff-independent map `f` from a nonempty hard-hole set to splitless
holes can satisfy

\[
 f(h)\in(\lfloor X/2\rfloor,X]
 \quad\text{for every }X\ge h.                          \tag{15}
\]

### Proof

Fix `h`.  If `f(h)<=h/2`, (15) already fails at `X=h`.  Otherwise it fails
at `X=2f(h)`, where `h<=X` but `f(h)=X/2` is outside the open upper shell.
QED.

For example, the two prime-pair rules send `54` to `42` and `48`; those
targets expire at cutoffs `84` and `96`.  Any successful injection family
must therefore depend on `X` and globally rematch old hard holes.

## 6. The surviving nonlocal Hall relation

Allow the core `c=1` in (11), and at each cutoff define

\[
 h\sim_X e
 \iff h\le X,quad \lfloor X/2\rfloor<e\le X,quad
 e\text{ splitless},quad c(h+1)\mid e+1.              \tag{16}
\]

When `c=1`, every upper-shell splitless hole is available.  Grouping sources
with equal nontrivial core gives an exact integral max-flow test.  The
relation saturates all hard sources at every cutoff through `2000`.  Selected
larger probes are:

| `X` | `K(X)` | upper `E` | core-1 demand | nontrivial demand | flow |
|---:|---:|---:|---:|---:|---:|
| `5,000` | `253` | `335` | `155` | `98` | `98` |
| `100,000` | `5,108` | `5,772` | `2,833` | `2,275` | `2,275` |
| `200,000` | `9,937` | `11,223` | `5,441` | `4,496` | `4,496` |
| `500,000` | `23,768` | `27,095` | `12,808` | `10,960` | `10,960` |
| `1,000,000` | `45,583` | `52,890` | `24,442` | `21,141` | `21,141` |

This is finite survival only.  Hall's inequality for the set of all hard
sources in (16) is precisely `K(X)<=e^+(X)`.  Thus proving saturation does
not bypass (T); it adds divisibility constraints to the same total count.

## 7. Exact failure of the structure-only count

The natural core-by-core proof of (16) would compare two multiplicative
semigroups.  Define

\[
 B_-(Y)=\#\{b\le Y:b>1, p\mid b\Rightarrow
 p\equiv2\pmod3,\ p\ge5,\ \Omega(b)\text{ even}\},     \tag{17}
\]

and

\[
 B_+(Y)=\#\{Y/2<s\le Y:s>1, p\mid s\Rightarrow
 p\equiv1\pmod3\}.                                    \tag{18}
\]

The exact first failure is

\[
 B_-(26989)=1215>1214=B_+(26989).                       \tag{19}

This is a literal Hall obstruction for hard-shaped core `3`.  Put
`X=3Y-1=80966`.  Every `b` counted by (17) makes `3b-1` an even reducible
hard-shaped integer: `b=1 mod 3`, the seed-3 cofactor is forbidden, and a
minus prime divisor gives a distinct admissible pair.  Conversely, the
splitless successors in the upper shell that are divisible by `3` are
exactly `3s` with `s` counted by (18).  The floor endpoints agree because
`X=3Y-1`.

The sources in (19) are structural candidates, not necessarily holes.
Thus (19) is not a counterexample to (T).  It proves that a core-counting
argument must use which candidates survive the least grounded closure.
At `Y=10^6`, the same structural counts are `41762` and `39264`; the
deficit does not disappear on the tested range.

## 8. Exact finite gate

`C74_injection_gate.py` is independent of C67 and C71.  It uses an SPF
table only to enumerate exact divisors; all closure states follow (3) in
ascending order.  Hopcroft-Karp and grouped Dinic flows use integer
capacities.  It checks:

1. the two characterizations in Lemmas 1 and 2;
2. the prime-square theorem for every tested hard hole;
3. every cutoff for (T) through the requested limit;
4. first Hall failures for the explicit local relations;
5. first collisions and expiry cutoffs for the substitution maps;
6. every cutoff through `2000` for (16), plus selected grouped probes; and
7. every `Y` for the semigroup comparison (17)-(18).

At `10^6`, it reports zero predicate or prime-square failures, no scalar
failure, and the C71 counts

```text
generated = 457599, E = 108651, K = 45583, e^+ = 52890.
```

The maximum scalar ratio is again `8846/9907` at `X=175956`.

From the repository root:

```powershell
python -m py_compile problems/424/compute/wave5/C74_injection_gate.py

python problems/424/compute/wave5/C74_injection_gate.py `
  --limit 1000000 --hall-limit 2000 `
  --kernel-probes 5000 10000 20000 50000 100000 200000 500000 1000000 `
  --output problems/424/compute/wave5/C74_injection_gate_1e6.json

python -O problems/424/compute/wave5/C74_injection_gate.py `
  --limit 1000000 --hall-limit 2000 `
  --kernel-probes 5000 10000 20000 50000 100000 200000 500000 1000000 `
  --output problems/424/compute/wave5/C74_injection_gate_1e6_replay.json
```

The ordinary and optimized JSON files are byte-identical.  SHA-256:

```text
B67495E0B7EF38762DCD9F848314352AAF088008C28FE038751DDBC9EBD7A516  C74_injection_gate.py
6BCD58A82CE471F7E27F592BF99DA841E1CA40D8475C89A2628C1B7A53F1F5DE  C74_injection_gate_1e6.json
6BCD58A82CE471F7E27F592BF99DA841E1CA40D8475C89A2628C1B7A53F1F5DE  C74_injection_gate_1e6_replay.json
```

The conclusion is therefore (iii): (T) remains open, and the weakest proved
canonical replacement is the variable-capacity splitless square shadow
(1), (5), and (6).  An upper-shell capacity-one proof must be cutoff-dependent,
nonlocal, and grounded in the actual least closure.
