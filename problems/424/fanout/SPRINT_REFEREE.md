# Sprint Referee

## Solved / Not Solved

**NOT SOLVED.** No report proves either

\[
\liminf_{X\to\infty}\frac{|A\cap[1,X]|}{X}>0
\]

or upper density zero for the distinct-value closure from `2,3`. The finite
censuses, declining densities, modular counts, and model fits have no
asymptotic force by themselves.

## Every Proved New Lemma

1. **Closure normalization.** The iterative union is the unique least set
   containing `2,3` and closed under `xy-1` for distinct integer values
   `x != y`. Every non-seed child is larger than both parents.

2. **Semantic exclusions.** `1,8,24` are absent from the distinct-value
   closure. A duplicate-preserving, distinct-index process can generate `24`
   from two positions carrying `5`, so it is a genuinely different process.

3. **Modulo 3 obstruction.** Every target-set member is `0` or `2 (mod 3)`.
   Hence
   \[
   |A\cap[1,X]|\le X-\left\lfloor\frac{X+2}{3}\right\rfloor,
   \qquad \overline d(A)\le\frac23.
   \]
   This disproves the later density-one / "almost all" formulation, but not
   positive lower density.

4. **Exact ascending membership recurrence.** For `n >= 4`, `n in A` iff
   `n+1=dq` for distinct `2 <= d < q < n` with `d,q in A`. Thus membership
   through `X` is independent of values above `X`. The priority-queue and
   divisor algorithms were each proved terminating, sound, complete, and
   increasing implementations of this recurrence.

5. **Admissible fixed-alphabet suborbits.** If finite `D subset A` and
   `t_0>max D`, every word in `f_d(t)=dt-1`, `d in D`, is licensed and remains
   in `A`. Under `u=t-1`, these become `g_d(u)=du+(d-2)`.

6. **Subcritical affine-orbit bound.** If
   `alpha_D(sigma)=sum_{d in D} d^(-sigma)<1`, then
   \[
   |O_D(t_0)\cap[1,X]|\le
   \frac{(X-1)^\sigma}
        {(1-\alpha_D(\sigma))(t_0-1)^\sigma}.
   \]
   In particular, the fixed `{2,3}` orbit from `5` is `o(X)`.

7. **No induced exact covering system.** For every `d,e >= 2`, the images
   `g_d(Z)=dZ-2` and `g_e(Z)=eZ-2` meet in `lcm(d,e)Z-2`. Thus no alphabet of
   at least two Problem-424 maps satisfies the cited disjoint exact-cover
   hypothesis.

8. **Conditional finite-field obstruction.** If `p=1 (mod d)`, `d>=2`, and
   the nonzero residue closure `R_p^*` lies in the subgroup of `d`th powers,
   then
   \[
   |R_p^*|\le \sqrt{2(p-1)/d}+4.
   \]
   This is conditional and local to one modulus.

9. **Large-seed zero-density bounds.** For two seeds `s,t >= 9`,
   \[
   |A_{s,t}\cap[1,X]|<\frac7{15}(X-1)^{\log_8 7},
   \]
   so the `{9,10}` closure has density zero. More generally, for `k` seeds
   all at least `m`, if `m-m^(-1)>4k`, their restricted closure is
   `O_S(X^theta)`, where
   `theta=log(4k)/log(m-m^(-1))<1`.

10. **Frozen `{2,3,5}` subsystem reduction.** If `B` is closed only under
    the licensed maps `T_k(x)=kx-1`, `k in {2,3,5}`, then `B subset A` and
    \[
    B=\{2,3,5\}\cup\{T_w(9)\}\cup\{T_w(14)\}.
    \]
    For `n>=6`, its exact reverse recurrence is
    \[
    b_n=\bigvee_{k\mid n+1,\ k\in\{2,3,5\},\ (n+1)/k\ne k}
        b_{(n+1)/k}.
    \]
    For `n>=25` this is also the stated eight-mask mod-30 transducer.

11. **Exact collision recurrence for `B`.** For `X>=24`, with
    `M_k=floor((X+1)/k)` and
    \[
    \Delta=P_{23}+P_{25}+P_{35}-P_{235},
    \]
    inclusion-exclusion gives
    \[
    C(X)=C(M_2)+C(M_3)+C(M_5)-1-\Delta(X).
    \]
    Equivalently, for `F=C-1/2`,
    `F(X)+Delta(X)=F(M_2)+F(M_3)+F(M_5)`.

12. **Summable-collision implication.** If, uniformly on every dyadic layer,
    \[
    \Delta(X)\le(1/30+\varepsilon_j)F(X),
    \qquad \sum_j\varepsilon_j<\infty,
    \]
    then `B`, and therefore `A`, has positive lower density. Only the
    implication is proved; the displayed hypothesis is not.

13. **Modular gate for `B`.** For the exact orbit `R_a (mod 30^a)`,
    \[
    \overline d(B)\le |R_a|/30^a.
    \]
    The reductions `R_(a+1) -> R_a` are onto, and with
    `e_a=1-|R_(a+1)|/(30|R_a|)`,
    \[
    |R_a|/30^a=(|R_1|/30)\prod_{j<a}(1-e_j).
    \]
    Thus `|R_a|=o(30^a)` would prove upper density zero for `B`, while
    positive lower density for `B` forces `sum e_a<infinity`.

14. **Global residue-decoder obstruction.** For every finite block automaton
    whose states are whole residue classes and whose incoming affine images
    are globally disjoint, the exponent-one weighted transition matrix
    satisfies `rho(A(1))<1`. Continuity then gives some `sigma<1` for which
    the uniquely decoded language has `O(X^sigma)` values. Hence this entire
    certificate class cannot prove positive density. The proof uses the
    invariant `F_w(x)=a_w x-b_w`, `a_w>=2`, `1<=b_w<a_w`, and a largest
    negative element contradiction in a recurrent periodic class.

## Every Exact Computation

- **Source artifacts:** the audited Erdos 1977 PDF has `2,794,180` bytes and
  SHA-256 `8fc7f48707af5c2536e792226c9e14505fc05cd46078e0c6e05a00810f8229ea`;
  the audited Erdos-Graham PDF has `5,253,644` bytes and SHA-256
  `0cbf0c32f0ab1e1c71db5121a88bac905bf976c4a6ab6bb6d7d9cf9ddd184ed3`.

- **Full target set `A`:** at `X=10^4`, the exact closure has `3,207`
  members after `12` fixed-point rounds, residue counts `(1314,0,1893)`, and
  maximum `9,999`. At `X=10^5`, two independent generators agree on `39,843`
  members. At `X=10^7`, independent wave-1 generators agree bit-for-bit on
  `4,952,270` members. At `X=10^8`, `A(X)=51,899,129` and the maximum observed
  gap is `21`.

- **Priority-generator census:**

  | `X` | count | exact fraction | canonical SHA-256 |
  |---:|---:|---:|---|
  | 10 | 4 | 2/5 | `df96c726842c0826692d9a0762a042522a4602e350698430eef4d369eb5699f4` |
  | 100 | 23 | 23/100 | `5e2046e576568fe61a86971b63efc80d4f9553bdf07c94f3af58ef17dd249612` |
  | 1,000 | 250 | 1/4 | `e48f2273cd087855176ae345df7ac830f0f6d333012668a605ba529430545a5c` |
  | 10,000 | 3,207 | 3207/10000 | `936fc959fb34ba2e77477b66bc7e1d6d381e13b7abe378a08e5b7f3f56e8794f` |
  | 100,000 | 39,843 | 39843/100000 | `8ea540464d0ef4ec231847fc3a7fc1aeca20da3332a6860be119fef27d29132c` |
  | 1,000,000 | 457,599 | 457599/1000000 | `cf19538b78162ed2bf89f1b99f99fc2eaad86b4f28607a8d4ead7451fed3098b` |

  Five unit tests passed; every cutoff `1..300` and the complete set at
  `5,000` matched a literal fixed-point oracle. At `100,000`, the independent
  divisor implementation matched element-for-element and matched the hash.

- **Divisor-generator replay at `10^7`:** `member_count=4,952,270`, forward
  and divisor outputs equal, the first `55` terms equal OEIS A005244, and
  `8:false,24:false`. The membership-bytearray SHA-256 is
  `7f5f29e1d5733d623c514c98c183796c3ab15a99d9ad9e5f0c9ff6ea627d85a0`;
  the last ten members are `9999981,9999983,9999984,9999986,9999987,9999989,`
  `9999993,9999995,9999998,9999999`.

- **Frozen subsystem `B` census:**

  | `X` | `C(X)` | `C(X)/X` |
  |---:|---:|---:|
  | `10^3` | 212 | 0.212000000000 |
  | `10^4` | 2,061 | 0.206100000000 |
  | `10^5` | 20,192 | 0.201920000000 |
  | `10^6` | 197,450 | 0.197450000000 |
  | `10^7` | 1,938,458 | 0.193845800000 |
  | `10^8` | 19,072,023 | 0.190720230000 |
  | `10^9` | 187,749,502 | 0.187749502000 |
  | `10^10` | 1,849,014,105 | 0.184901410500 |
  | `10^11` | 18,222,202,754 | 0.182222027540 |

  Maximum gaps reported are `180` below `10^5` and `16,436` below `10^10`.
  These are finite facts only.

- **Collision census at `10^11`:** parent-mask counts for
  `2,3,23,5,25,35,235` are respectively
  `8,586,937,317`, `5,659,661,598`, `294,443,090`, `3,249,663,656`,
  `270,627,676`, `160,436,579`, `432,836`. Hence
  `Delta=726,373,017`, `Delta/C=0.039861976447`, and its excess over `1/30`
  is `0.006528643114`. The exact-run ratios `Delta/C` at
  `10^8,10^9,10^10,10^11` are `0.040753568722`, `0.040526280597`,
  `0.040217274600`, `0.039861976447`; the corresponding excesses are
  `0.007420235389`, `0.007192947264`, `0.006883941267`, `0.006528643114`.

- **Moment and collision diagnostics:** the exact integer moment recurrence
  produced `R1^2/(X R2)=0.1507571,0.1427721,0.1356460` at
  `10^7,10^8,10^9`. The words `255232` and `322255` exactly induce the same
  map `x -> 600x-381`. The reported local exponent `1.088`, renewal root
  `1.032812265771883...`, and log-power fit `0.1431` are numerical diagnostics,
  not exact asymptotic results.

- **Exact modular orbit of `B`:** for `a=1,...,7`, the pairs
  `(30^a,|R_a|)` are `(30,16)`, `(900,389)`, `(27000,10144)`,
  `(810000,274958)`, `(24300000,7587398)`, `(729000000,212613518)`,
  `(21870000000,6011481468)`. The exact fractions therefore decrease from
  `16/30` to `6011481468/21870000000`; this finite decrease proves no limit.
  The derived values of `a e_a` are
  `0.18958,0.26153,0.28945,0.32070,0.32968,0.34516`.

- **Finite automaton searches:** modulo `30`, the one-letter search found
  `22` colorable and `8` ambiguous residues and exhaustively checked `384`
  policies; every recurrent core was empty (`24` after three deletion rounds,
  `360` after four). Exact-cover-tree fixed-point sizes were
  `30,22,15,7,0` for each block cap `c=1,2,3`. The direct orbit counts were
  `212,2061,20192` at `10^3,10^4,10^5`. Four tests passed and `3,279` block
  coefficient invariants were checked.

- **Other exact checks:** the large-seed proof uses
  `69/175<2/5` and `80/9>8`; `{2,3,5}` has reciprocal-slope sum `31/30`.
  The B02 suite's four tests passed, including every cutoff through `500`,
  supplied counts through `10^5`, sentinels `8,24`, and the first three
  modular orbit counts.

## Dead Route Mechanisms

- **Density one:** rigorously dead because the class `1 (mod 3)` is absent.
- **Finite-data extrapolation:** dead as a proof method; neither rising full-set
  counts nor falling frozen-subsystem and modular ratios control a liminf.
- **Large-seed transfer:** dead because its tree-value lower bound requires
  leaves at least `9`; the target seeds `2,3` are load-bearing.
- **Fixed `{2,3}` affine orbit:** rigorously sublinear by the subcritical
  affine-orbit bound.
- **Disjoint exact covering systems:** dead because all induced whole-class
  images overlap in residue `-2` modulo the relevant lcm.
- **Global residue-class exact decoding:** rigorously dead by
  `rho(A(1))<1`; every such language is sublinear. Orbit-relative uniqueness
  is not ruled out.
- **Unweighted second moment for `{2,3,5}`:** does not close because its
  observed `R2` growth exponent is about `1.088`, above the required
  `2 sigma-1=1.0656245315...`; this is a failure of the tested estimate, not a
  zero-density theorem.
- **Frozen `{2,3,5}` positive-density certificate:** no proof survives the
  collision and modular gates. Its collision excess is not shown summable and
  its modular lift deficits are not shown summable. The subsystem itself is
  not proved to have zero density, so the route is obstructed, not
  mathematically refuted.
- **Fixed-modulus power-subgroup transfer:** unavailable without the strong
  subgroup-containment hypothesis and cannot by itself control integer
  density.

## Smallest Remaining Load-Bearing Lemma

For the sprint's most concrete subsystem route, prove the **summable
excess-collision bound**: there exist `epsilon_j >= 0` with
`sum_j epsilon_j < infinity` such that, uniformly for
`2^j <= X < 2^(j+1)`,

\[
\Delta(X)\le\left(\frac1{30}+\varepsilon_j\right)
             \left(C(X)-\frac12\right).
\]

The proved induction then gives positive lower density for `B subset A`.
Nothing in the finite data proves this lemma; the observed collision excess
and modular lift deficits currently point against its simplest expected forms.
If this frozen-subsystem frontier fails, the remaining full-set frontier is a
self-improving factor-sieve inequality that uses newly generated multipliers.

## Novelty Caveat

The modulo-3 obstruction is not novel: the current Erdos Problems page records
it and attributes it to Stefan Steinerberger. Green already states the
large-seed `{9,10}` zero-density phenomenon; the sprint supplies quantitative
distinct-input proofs. The affine bounds apply published theorems and are not
new general theorems.

The checked primary sources and citation trails contain no solution or theorem
controlling the target lower density, but this is not an exhaustive novelty
certificate. `LITERATURE.md` itself still says the novelty search remains
open. In particular, the global residue-decoder theorem, exact collision
identity, and large finite censuses should be described as sprint results
pending a broader prior-art search, not as globally novel results.

Finally, the 1977 source says "positive density" without fixing the liminf
interpretation; Green's displayed closure omits distinctness; and later
sources use distinct indices without fully specifying duplicate suppression.
This referee verdict concerns the repository's frozen distinct-value,
positive-lower-density formulation. None of the sprint lemmas was reported as
Lean-checked.
