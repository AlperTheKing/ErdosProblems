# C40: least-grounded rank additive-one red team

## Verdict

No falsifier was found for

\[
 H_{\le d}(X)\le Q_{\le d}(X)+1                         \tag{AO}
\]

on the least grounded set `G`.  An integer-only C++ implementation using
explicit products `a<b` checked every hard event and every rank through
`X=100,000,000`.  It found maximum excess one, first at `(X,d)=(362,2)`,
and no excess above one.  An independent Python implementation using trial
divisors and literal descending approximants agreed through `100,000`, with
zero membership, rank, count, or event-sweep mismatches.

This is finite evidence, not a proof of (AO).  No structural infinite
obstruction to (AO) was constructed.

The red team did find structural obstructions to the most plausible local
proofs.  At `X=74`, the hard source `74` has no compatible target on any
arrived boundary of any of its missing-factor chains.  Through `10^8`,
`1,123,563` hard sources have this zero-degree property.  There is also a
unique-split fiber of size `308,779` over the single missing parent `11`.
Neither is a Hall obstruction to (AO), because (AO) pools all targets of
compatible rank rather than requiring derivation-local edges.

A strictly weaker sufficient condition is isolated in Section 7.  Its
sufficiency is proved; the condition itself is not claimed for `G`.

## 1. Exact object and conventions

Put

\[
 \mathcal A=\{n\ge2:n\not\equiv1\pmod3\}.
\]

The set `G` in this audit is the least subset of `A` containing `2,3` and
closed under

\[
                 a,b\longmapsto ab-1,\qquad 2\le a<b.       \tag{1}
\]

Every parent in (1) is smaller than its output.  Consequently, membership in
the actual least `G` is decided exactly in one increasing pass.  No optional
members of a forward-closed superset are present.

For an allowed hole `n`, let

\[
 \mathcal P(n)=\{(a,b):ab=n+1, 2\le a<b, a,b\in\mathcal A\}.
\]

The obstruction rank used here is

\[
 \rho(n)=0\quad\text{if }\mathcal P(n)=\varnothing,
\]

and otherwise

\[
 \rho(n)=1+\max_{(a,b)\in\mathcal P(n)}
       \min\{\rho(x):x\in\{a,b\}\setminus G\}.             \tag{2}
\]

A hard source is a reducible even hole outside the usable seed-3 class.  In
particular, if `3 | n+1`, the factor `(n+1)/3` must be allowed and distinct
from `3` for the source to be seed-3 easy.

A target is a missing parent `q` whose seed-2 child is generated.  Its event
coordinate and rank are

\[
                 c=2q-1,qquad \rho(q),                     \tag{3}
\]

not `q` and not a rank attached to `c`.  Thus

\[
 Q_{\le d}(X)=\#\{q\notin G:2q-1\le X, 2q-1\in G,
                                      \rho(q)\le d\}.       \tag{4}
\]

## 2. Independent exact computation

The C++ checker does not factor each successor with the C31 SPF algorithm.
It enumerates every allowed product `ab<=LIMIT+1` with `a<b`, stores the
result at `ab-1`, and then performs the increasing least-`G` recursion.  All
square-root decisions use integer binary search.  It computes (2), records
hard events and child-coordinate targets, and sweeps all rank prefixes at
every hard event.

The Python verifier is independent at the relevant points: it finds pairs
by trial division and separately constructs

\[
 S_0=\mathcal A,\qquad
 S_{t+1}=\{2,3\}\cup\{ab-1:a<b, a,b\in S_t\}.              \tag{5}
\]

Through `100,000`, (5) stabilized after 14 updates.  For every allowed value,
its limiting membership agreed with the increasing recursion, and every
hole removed in `S_r\setminus S_{r+1}` had recursive rank `r`.  There were
zero mismatches.

| limit | admissible pairs | hard | targets | max hole rank | max prefix excess | `>1` failures |
|---:|---:|---:|---:|---:|---:|---:|
| `100,000` | `226,818` | `5,108` | `6,783` | `12` | `1` at `(362,2)` | `0` |
| `100,000,000` | `380,416,996` | `3,368,726` | `5,948,614` | `20` | `1` at `(362,2)` | `0` |

At `10^8`, strict zero-slack dominance was positive at three hard-event
tests, `(362,2)`, `(1002,2)`, and `(1014,2)`.  These are event tests, not
three isolated integer cutoffs: the deficit at rank two remains unchanged
between a source and the next target.  The last such deficit is repaired by
the rank-zero target at child `1019`.

The event sweep covers every integer cutoff.  Hard events are even and
target children are odd, so there are no same-coordinate ties.  Between two
hard events, targets can only decrease `H_{<=d}-Q_{<=d}`.

## 3. Parity and the two automatic rank gates

### Lemma 1

Every hard source has obstruction rank at least two.  Hence, for every `X`,

\[
 H_{\le0}(X)=H_{\le1}(X)=0.                                \tag{6}
\]

### Proof

If `n` is even, every factor of `n+1` is odd.  A missing endpoint of an
admissible pair for a hard source is therefore an allowed odd hole `m>3`.
But every allowed odd `m>3` has the distinct admissible pair

\[
                  m+1=2\cdot\frac{m+1}{2};
\]

allowedness of the second factor follows in both possible residues of `m`
modulo three.  Thus no such `m` is splitless, so `rho(m)>=1`.  Every
admissible pair for a hard hole has a missing endpoint of rank at least one.
Equation (2) gives `rho(n)>=2`.  QED.

This lemma explains a major repair mechanism.  Targets of ranks zero and one
are compatible with every hard source; exact death layers must not be
compared separately.

At `X=10^8`, the relevant terminal counts are

\[
\begin{aligned}
 H_{=2}&=1,249,101, & Q_{=2}&=580,294,\\
 Q_{\le1}&=3,946,924, & Q_{\le2}&=4,527,218.
\end{aligned}
\]

Thus the exact rank-two layer has deficit `668,807`, while the correct rank
prefix has surplus `3,278,117`.

## 4. Convention audit

### Event coordinate

Retiming each known target from its child `2q-1` to its parent `q` removes
all positive prefix tests through `10^8`.  This is an artificially easier
model.  The tight source `362` occurs before the rank-zero target at child
`363`; crediting its parent `182` would erase precisely the delay that makes
the additive constant necessary.

### Distinct parents

All real factor pairs were enumerated with `a<b`.  Allowing `a=b` first
changes membership at

\[
                         8=3^2-1.                           \tag{7}
\]

In the real problem, `8` is a rank-zero hole because `3*3` is forbidden.
The square-leak model therefore computes a different generated set and
cannot falsify or verify (AO) for `G`.

For a target, the potential seed-2 pair `(2,q)` is automatically distinct:
`q` is missing while `2` is a seed, so `q!=2`.  For the seed-3 easy class,
the explicit exclusion `q=3` is essential for the same reason as (7).

### Rank convention

The literal-stage replay had no discrepancies with (2).  Rank zero means
removal in the first transition `S_0 -> S_1`; equivalently, obstruction rank
is death stage minus one when stages are numbered starting at one.  Shifting
only one side would be a convention error.  Shifting both sides consistently
does not change a rank-prefix comparison.

### Groundedness

Arbitrary forward-closed supersets may retain unsupported values such as
`8`.  The least grounded recursion removes them and all membership depending
only on such unsupported choices.  The C40 computations contain no
superset-selection variables: the increasing recursion and the descending
intersection (5) agree exactly on the verified prefix.

## 5. Why the local countermodels do not falsify (AO)

### Exact-layer model

At `X=74`, the hard rank-two sources are `54,74`.  The targets through that
cutoff are child `41` of rank two and child `69` of rank one.  Exact layers
see only one rank-two target and fail; rank-prefix Hall sees both and has
equality.  At `10^8`, the exact-layer maximum excess is `668,807`, as above.

### Missing-factor chains

The direct missing-endpoint model already has degree zero at `54`: its only
split is `55=5*11`, while `2*11-1=21` is missing.  Walking one more step
finds the arrived target `41`, so this first defect is repaired.

The stronger local model fails at `74`.  Its only split is

\[
                         75=5\cdot15.
\]

The seed-2 chain beginning at the missing endpoint is

\[
 15,29,57,113,225,449,
\]

where the first five values are holes of ranks `1,2,3,4,5`, and `449` is
the first generated boundary.  No target on this chain has arrived by `74`,
regardless of how many formal steps are allowed.  Nevertheless, global
rank-prefix capacity at `74` is exactly the two targets `41,69`, so (AO)
does not fail.

Through `10^8`, the exact zero-degree counts are:

| local target rule | first zero | zero-degree hard sources |
|---|---:|---:|
| immediate missing endpoint | `54` | `3,218,791` |
| at most two seed-2 steps | `74` | `1,182,776` |
| any chain boundary that has arrived | `74` | `1,123,563` |

These are obstructions to derivation-local matching, not to the complete
rank-dominance graph represented by (AO).

### Repeated one-parent fibers

Among hard sources having one admissible split and one missing endpoint, the
largest exact fiber through `10^8` is over `11`, with size `308,779`.  A
capacity-one map from each source to its own missing endpoint is therefore
impossible.  The fiber still does not constrain global Hall matching: all
rank-zero, rank-one, and rank-two targets can serve its rank-two sources.

An infinite family of local sources over one blocker would remain only a
local obstruction.  To falsify (AO), one must make the total number of hard
sources in some rank prefix outrun all compatible boundary targets by at
least two at the same child-coordinate cutoff.  No construction doing this
was found.

## 6. The tight additive constant

At `(X,d)=(362,2)`, the exact source and target prefixes are

\[
                     H_{\le2}(362)=11,
                     \qquad Q_{\le2}(362)=10.              \tag{8}
\]

Thus zero slack is false and the constant in (AO) cannot be reduced.  The
next integer, `363`, is a generated target child with missing parent `182`
of rank zero, restoring equality.  This is a genuine child-coordinate
parity delay, not a same-coordinate ordering choice.

No later hard event through `10^8` raises the excess above one.  This does
not preclude a later actual-`G` counterexample.

## 7. A strictly weaker sufficient inequality

This section proves sufficiency only; it does not establish a new estimate
for `G`.

Let `M(X)` count allowed holes, `E(X)` splitless holes, and `S(X)` the
seed-3-easy reducible even holes.  Put

\[
 Y=\left\lfloor\frac{X+1}{2}\right\rfloor,
 \qquad Z=\left\lfloor\frac{X+1}{3}\right\rfloor.
\]

The exact odd/seed-3/hard partition gives

\[
 M(X)=E(X)+M(Y)-Q(X)+S(X)+H(X),                            \tag{9}
\]

and the seed-3 parent map gives `S(X)<=M(Z)`.  Therefore the one-sided
terminal defect

\[
 D(X)=\bigl(H(X)-Q(X)\bigr)_+
\]

satisfies the unconditional recurrence

\[
 M(X)\le E(X)+M(Y)+M(Z)+D(X).                             \tag{10}
\]

### Proposition 2

The strictly weaker condition

\[
                         H(X)\le Q(X)+o(X)                 \tag{SC}
\]

is sufficient for `M(X)=o(X)` and hence for density `2/3` of `G`.

### Proof

Condition (SC) says exactly that `D(X)=o(X)`.  The splitless theorem gives
`E(X)=o(X)`.  If

\[
 L=\limsup_{X\to\infty}\frac{M(X)}{X},
\]

divide (10) by `X` and take limsups to obtain

\[
                         L\le\frac12L+\frac13L=\frac56L.
\]

Thus `L=0`, proving the claim.  QED.

This is strictly weaker than (AO).  For fixed `X`, taking `d` above every
finite rank in (AO) gives `H(X)<=Q(X)+1`, hence (SC).  Conversely, (SC)
allows unbounded sublinear terminal deficits and places no restriction on
intermediate rank prefixes.  It therefore cannot prove (AO) and does not
duplicate the open C39 proof task.

An even weaker spare-capacity version follows directly from (9): it is
enough that

\[
 H(X)-Q(X)\le M(Z)-S(X)+o(X).
\]

Again, no such asymptotic estimate is claimed here.

## 8. Reproduction

From the repository root:

```powershell
g++ -O3 -std=c++20 -Wall -Wextra -pedantic `
  problems/424/compute/wave3/C40_rank_additive_one_redteam/redteam_rank_prefix.cpp `
  -o problems/424/compute/wave3/C40_rank_additive_one_redteam/redteam_rank_prefix.exe

problems/424/compute/wave3/C40_rank_additive_one_redteam/redteam_rank_prefix.exe `
  100000000 `
  problems/424/compute/wave3/C40_rank_additive_one_redteam/cxx_100m.json

problems/424/compute/wave3/C40_rank_additive_one_redteam/redteam_rank_prefix.exe `
  100000 `
  problems/424/compute/wave3/C40_rank_additive_one_redteam/cxx_100k.json

python problems/424/compute/wave3/C40_rank_additive_one_redteam/verify_stage_model.py `
  --limit 100000 `
  --cpp-json problems/424/compute/wave3/C40_rank_additive_one_redteam/cxx_100k.json `
  --output problems/424/compute/wave3/C40_rank_additive_one_redteam/stage_100k.json
```

SHA-256:

```text
redteam_rank_prefix.cpp  8679394D45E3EB3CFC8E442EA670D6AF9B4B402C39A5410180C1DBA4C6E233EB
verify_stage_model.py    AB77F26379CBEC6A9D64DF49569EE515069AF5E50E225BE059E33E1D9A4D3657
cxx_100m.json            0270F2AAE3348279BDF15C8A5F5F7BF2366566B0EE4C83D87CEC07B4709F096D
cxx_100k.json            B842D12B32E2B6176997708070EF463FB05AAAA940EDD7923C90B1A308522944
stage_100k.json          6FC78424A0954DB1E758C280BB5743C152474419E4E11171F02C568B64E9FD54
```

## Final status

The actual least-grounded additive-one inequality survives the independent
exact gate through `10^8`, but remains unproved.  Strict zero slack, exact
rank layers, bounded or unbounded arrived-chain localization, repeated
missing-parent charging, equal-factor generation, parent-coordinate timing,
and arbitrary-superset substitutions are all either exactly falsified or
shown not to model (AO).
