# R8 — entropy and counting (Erdős #23)

Lane R8, mechanism: **entropy inequalities and counting arguments**, nothing else.
All acceptance-path arithmetic is exact (Python `int` / `fractions.Fraction`); floats appear
only in guidance searches, and every claim they suggested was re-derived exactly.
Every headline claim is computed by **two independently written implementations**
(`R8_entropy_core.py` + `R8_entropy_rigidity.py` versus `R8_entropy_verify.py` +
`R8_entropy_survivors.py`, different data structures: vertex-side arrays versus edge
bitmasks, BFS 2-colouring versus cut enumeration).

Nothing here contradicts the accepted base. No counterexample to Erdős #23 was found;
every graph appearing below satisfies `25·bip ≤ N²` with room to spare. What dies here
are *certificates*, not the conjecture.

---

## 0. Scoreboard

| item | outcome |
|---|---|
| (a) **PRGM** — the `x`-adapted `Z₅`-rotation geometric-mean certificate (the object f3 §5 asked for and G8 §6.3 left open) | **DEAD, exact.** Fails at uniform weights on the **Wagner graph** (`5¹⁰·162 = 1582031250 > 8¹⁰ = 1073741824`), on **Grötzsch** (`3750 > 2656`), on **And(4)** (`3456 > 2656`). Uniform rotation weights are *forced* (Lemma R8-1b), so no reweighting repairs it. |
| (b) **THEOREM R8-2 (aggregator rigidity)** | **NEW.** *Every* fixed distribution over cuts, aggregated by *any* strictly monotone mean — arithmetic, weighted geometric, power means, **and the Gibbs free energy `−β⁻¹log E[e^{−βm}]` at every `β>0`**, which is the sharpest form the entropy method takes — must be supported on **rainbow-1 cuts**: cuts whose monochromatic edge set meets **every induced `C₅` exactly once**. Proof in §3, four lines. |
| (c) **LEMMA R8-3 (pentagon-degree counting obstruction)** | **NEW, and it gives a counting *proof*, not a computation.** In `And(4)` every edge lies in `5` or `10` induced pentagons while there are `33` of them; `5 ∤ 33`, so no edge set meets every pentagon exactly once. Hence `R(And(4)) = ∅` and **no averaging certificate of any kind exists for `And(4)`**. |
| (d) **THEOREM R8-4 (star kill)** | **NEW.** If some vertex `v` meets every rainbow-1 cut and `|R| ≤ 6`, then `max_a min_{S∈R} m_S(a) ≥ 1/(4|R|) > 1/25`. Kills **Grötzsch** (apex, exact witness, value exactly `1/20`) and the **Clebsch graph** (every vertex, value exactly `1/20`) — two graphs that *pass* the G8 §6.3 test. |
| (e) unification of the recorded `1/20` barrier | The dead fact A6 (`≥ 1/20` on `C₅[n]`) and the new kills are **the same phenomenon**: Motzkin–Straus gives total edge weight `≤ 1/4` on a triangle-free graph, and a 5-fold symmetry splits it into `1/4 ÷ 5 = 1/20`. §6. |
| (f) exhaustive verdicts on the structured graphs | `And(4)`, `And(5)`, `And(6)`, the `N=14` extremal graph `M?AE@bH{AYN_LgBs?`: `R = ∅`. Grötzsch, Clebsch: star kill. **Survivors: `C₅`-blow-ups, Petersen, Wagner only** — and the two non-blow-up survivors are 3-regular, while a minimal counterexample has `δ ≥ 7`. |
| (g) census, `δ ≥ 4`, `n ≤ 12`, and all connected triangle-free `n ≤ 9` | no kill below `n = 11`; kills appear exactly when the graph becomes pentagon-rich. Numbers in §7. |

**Bottom line for the mechanism.** Entropy/averaging over a fixed cut family is now dead in
the strongest available sense: not merely "the arithmetic mean is too weak" (A6) and not merely
"the geometric mean has an empty active-cut intersection on `And(4)`" (G8 §6.3), but *no
monotone aggregator whatsoever*, killed on `And(4)` by a two-line divisibility count and on
Grötzsch/Clebsch by an explicit star weighting that hits exactly `1/20`. The one shape left
open by the prior entropy rounds — choose the cut family as a function of `x`, geometric mean,
`Z₅` rotations — is (a), and it is dead too.

---

## 1. Notation

`H` is triangle-free, `x ≥ 0` on `V(H)` with `Σx = 1` (integer weights `a` are used for exact
sweeps, with `Σa = q`). For a cut (bipartition) `S` of `V(H)`,

```
m_S(x) = sum over monochromatic edges uv of S of x_u x_v ,     psi(H,x) = min over cuts S of m_S(x).
```

Accepted base (not re-derived): the conjecture is `max_x psi(H,x) ≤ 1/25` for every
triangle-free `H`; `psi` is monotone under induced subgraphs, so every `H` of odd girth 5 has
`max_x psi ≥ 1/25`; `bip(H[a]) = min_S Σ_{mono} a_u a_v`.

**Calibration fact used throughout.** If `K` is an *induced* `C₅` of `H` and `x_K` is uniform
on `V(K)` (weight `1/5`, zero elsewhere), then for every cut `S`

```
m_S(x_K) = |mono(S) ∩ E(K)| / 25 ,
```

because the only edges of `H` inside `supp(x_K)` are the five edges of `K`. Every cut of an odd
cycle has an odd number of monochromatic edges, so `m_S(x_K) ≥ 1/25`, with equality iff `S` has
**exactly one** monochromatic edge inside `K`; and such a cut always exists. Hence
`psi(H,x_K) = 1/25` exactly: every induced pentagon is a maximiser.

---

## 2. (a) The `Z₅`-rotation geometric-mean certificate PRGM — DEAD

### 2a. The exact rotation identity

For `φ: V(H) → Z₅` and `r ∈ Z₅` let `B_r = φ^{-1}({r, r+2, r+4})`, `S_r = φ^{-1}({r+1, r+3})`.
This is a genuine bipartition of `V(H)`; write `m_r(φ,x)` for its monochromatic weight. Put

```
E1[p] = weight of edges between class p and class p+1     (the "good" edges)
E2[p] = weight of edges between class p and class p+2
Z     = weight of edges inside classes.
```

**Identity (proved, and re-verified against the raw bipartition for every `φ` used):**

```
m_r  =  E1[r-1] + Z + E2[r] + E2[r+1] + E2[r+2].
```

*Proof.* An edge with `φ`-values `(a, a+1)` is monochromatic iff `a, a+1` lie in the same part;
consecutive elements of `{r,r+2,r+4}` occur only for `(r+4, r)`, and `{r+1,r+3}` contains no
consecutive pair, so this happens iff `r = a+1`. An edge with `φ_u = φ_v` is always
monochromatic. For `(a,a+2)`: the monochromatic pairs at distance 2 are `(r,r+2)`, `(r+1,r+3)`,
`(r+2,r+4)`, i.e. `r ∈ {a, a-1, a-2}`. ∎

If `φ` is a homomorphism `H → C₅` then `Z = E2 = 0`, `m_r = E1[r-1] ≤ X_{r-1}X_r`
(`X_i` = weight of class `i`) and

```
psi ≤ min_r m_r ≤ (Π_r m_r)^{1/5} ≤ (Π_i X_i)^{2/5} ≤ 1/25,
```

which is f3's Theorem A re-derived as a pure AM–GM/entropy statement. The point of PRGM is that
`φ` may be chosen **as a function of `x`**, so the certificate is not a fixed cut family and is
not killed by G8 §6.3.

```
PRGM(H,x) := min over φ: V→Z5 of ( Π_{r∈Z5} m_r(φ,x) )^{1/5}   ≥   psi(H,x).
```

### 2b. Uniform rotation weights are forced

**Lemma R8-1b (the class load must have maximum entropy).** Suppose one uses
`min_r m_r ≤ Π_r m_r^{w_r}` with a probability vector `w` and wants `≤ 1/25` for every weighting
of every `C₅`-coloured graph. Then `w_r = 1/5` for all `r`.

*Proof.* On a `C₅`-blow-up with class weights `X` on the simplex,
`Π_r (X_{r-1}X_r)^{w_r} = Π_i X_i^{c_i}` where `c_i = w_i + w_{i+1}` is the *load* of class `i`
and `Σ_i c_i = 2`. By Lagrange the maximum of `Π_i X_i^{c_i}` over the simplex is at
`X_i = c_i/2`, with value

```
Π_i (c_i/2)^{c_i} = exp( 2 Σ_i d_i log d_i ) = exp( -2 H(d) ),        d := c/2 a probability vector.
```

So the requirement `≤ 1/25 = exp(-2 log 5)` is exactly `H(d) ≥ log 5`. Since `d` is a
probability vector on the five classes, `H(d) ≤ log 5` with equality **iff `d` is uniform**.
Hence `c_i = 2/5` for every `i`, and on `Z₅` the system `w_i + w_{i+1} = 2/5` has the unique
solution `w ≡ 1/5`. ∎

(The certificate therefore spends its entire entropy budget: the load distribution is forced to
be the maximum-entropy one. This is the same "`1/5` of the available entropy" phenomenon that
Q1's Theorem Q1-A recorded on the cut side, now on the class side.)

So PRGM (uniform weights) is the *only* candidate in the rotation family: no reweighting repair
exists.

### 2c. Exact failure

`R8_entropy_prgm.py` (numpy, exhaustive over all `5^{n-1}` maps, `φ(v₀)=0` by the rotation
invariance of the product) cross-checked against the pure-Python exhaustive
`prgm_bruteforce` in `R8_entropy_core.py`. The certificate claim is
`5¹⁰ · Π_r m_r ≤ q¹⁰` where `q = Σa`.

| graph | `n` | `bip` | `min_φ Π_r m_r` | best `(m_0..m_4)` | `q¹⁰/5¹⁰` | verdict |
|---|---|---|---|---|---|---|
| `C5` | 5 | 1 | **1** | (1,1,1,1,1) | 1 | OK (equality) |
| `C7` | 7 | 1 | 3 | (1,3,1,1,1) | 28.93 | OK |
| `K₃,₃` | 6 | 0 | 0 | (0,9,0,0,0) | 6.19 | OK |
| `C5[2]` | 10 | 4 | **1024** | (4,4,4,4,4) | 1024 | OK (equality) |
| `C5[3,1,2,2,1]` | 9 | 2 | 144 | (3,3,2,4,2) | 357.05 | OK |
| `C5[3,1,2,2,0]` | 8 | 0 | 0 | (0,9,0,0,0) | 109.95 | OK |
| `Petersen` | 10 | 3 | 972 | (6,6,3,3,3) | 1024 | OK |
| **`Wagner = And(3)`** | 8 | 2 | **162** | (3,3,3,3,2) | 109.95 | **FAILS** |
| **`Grötzsch`** | 11 | 4 | **3750** | (5,6,5,5,5) | 2655.99 | **FAILS** |
| **`And(4)`** | 11 | 4 | **3456** | (4,6,6,6,4) | 2655.99 | **FAILS** |

**Smallest exact falsifier: the Wagner graph at uniform weights.**
`5¹⁰·162 = 1 582 031 250 > 1 073 741 824 = 8¹⁰`, i.e. `(Π m_r)^{1/5} = 162^{1/5} = 2.76632…`
against the required `8²/25 = 2.56` (overshoot `1.0806`; Grötzsch overshoots by `1.0714`,
`And(4)` by `1.0541`). Note `min_r m_r = 2 = bip(Wagner)`, so the *rotation cuts
are optimal* — the entire loss is the step `min ≤ geometric mean`, which is exact only when the
five values are equal, and on `Wagner` they cannot be (`8` vertices do not split into five equal
`Z₅`-classes, and `Wagner ↛ C₅` forces `Z + E2 > 0`).

**Verdict: PRGM is DEAD.** The mechanism that both prior entropy rounds pointed at —
"non-linear in the class statistics, a min or a geometric mean" (f3 §5) with the family chosen
as a function of `x` (G8 §6.3) — fails on the smallest non-`C₅`-colourable triangle-free graph.

---

## 3. (b) THEOREM R8-2 — rigidity of every averaging certificate

**Definition.** An *aggregator* is `Φ: R_{≥0}^k → R_{≥0}` with (i) `min_j t_j ≤ Φ(t)`,
(ii) `Φ(c,…,c) = c`, (iii) `Φ` strictly increasing in every coordinate.
An *averaging certificate* for `H` is a probability distribution `ν` over cuts of `H`
(independent of `x`) together with an aggregator such that
`Φ((m_S(x))_{S ∈ supp ν}) ≤ 1/25` for all `x` on the simplex. By (i) this proves
`max_x psi(H,x) ≤ 1/25`.

Examples of aggregators: the arithmetic mean (`= A6`, dead), every weighted geometric mean
(`= G8 §6.1`), every power mean, and — the sharpest form available to the entropy method — the
**Gibbs / free-energy aggregator**

```
Φ_β(t) = -(1/β) · log ( Σ_j ν_j e^{-β t_j} ),      β > 0,
```

which satisfies (i) because `E[e^{-βm}] ≤ e^{-β min m}`, satisfies (ii) by inspection, is
strictly increasing in each `t_j`, tends to the arithmetic mean as `β → 0` and to `min` as
`β → ∞`. (This is exactly the exponential-moment/annealed-free-energy upgrade of the
first-moment method; it is the natural place to look after A6 killed `β = 0`.)

> **THEOREM R8-2.** Let `H` be triangle-free and `x*` a weighting with `psi(H,x*) = 1/25`.
> If an averaging certificate holds at `x*`, then `m_S(x*) = 1/25` for **every** `S ∈ supp(ν)`.
>
> *Proof.* `psi(H,x*) = 1/25` means `m_S(x*) ≥ 1/25` for every cut `S`. If some `S₀ ∈ supp(ν)`
> had `m_{S₀}(x*) > 1/25`, strict monotonicity (iii) and (ii) give
> `Φ((m_S(x*))) > Φ(1/25,…,1/25) = 1/25`, contradiction. ∎

> **COROLLARY (rainbow-1).** Every `S ∈ supp(ν)` has **exactly one** monochromatic edge inside
> **every** induced `C₅` of `H`. Call such cuts *rainbow-1* and write `R(H)` for their set.
> Consequently, writing `psi_R(H,x) = min_{S ∈ R(H)} m_S(x)`,
>
> ```
> an averaging certificate exists for H   ⟹   max_x psi_R(H,x) ≤ 1/25 ,
> ```
> and if `R(H) = ∅` no averaging certificate exists at all.

This subsumes A6 and G8 §6.3 and extends them to the whole exponential family: **the entropy
method's extra freedom (`β > 0`) buys nothing here.** Combined with Q1's Theorem Q1-A (the
entropy budget on `C₅[n]` is `log(10(2ⁿ−1))`, a fifth of `N log 2`), the fixed-distribution
side of the entropy mechanism is closed from two independent directions.

### Exact computation of `R(H)`

`R8_entropy_rigidity.py` (vertex-side sets) and `R8_entropy_verify.py` /
`R8_entropy_targets.py` (edge bitmasks, `np.bitwise_count`) agree everywhere:

| graph | `n` | `|E|` | `bip` | #induced `C₅` | `|R(H)|` | classes partition `E`? | verdict |
|---|---|---|---|---|---|---|---|
| `C5` | 5 | 5 | 1 | 1 | 5 | yes (5×1) | survives |
| `C5[2]` | 10 | 20 | 4 | 32 | 15 | no | survives |
| `C5[3]` | 15 | 45 | 9 | 243 | 35 | no | survives |
| `Petersen` | 10 | 15 | 3 | 12 | **5** | yes (5×3) | survives |
| `Wagner = And(3)` | 8 | 12 | 2 | 8 | **5** | yes (2,2,2,4,2) | survives |
| **`And(4)`** | 11 | 22 | 4 | 33 | **0** | — | **DEAD** |
| **`And(5)`** | 14 | 35 | 6 | 98 | **0** | — | **DEAD** |
| **`And(6)`** | 17 | 51 | 9 | 238 | **0** | — | **DEAD** |
| **`Grötzsch = M(C₅)`** | 11 | 20 | 4 | 31 | **5** | yes (5×4) | **DEAD (star)** |
| **`Clebsch`** | 16 | 40 | 8 | 192 | **5** | yes (5×8) | **DEAD (star)** |
| **`N=14 extremal`** `M?AE@bH{AYN_LgBs?` | 14 | 32 | 7 | 92 | **0** | — | **DEAD** |
| `M(C7)` | 15 | 28 | — | 28 | 57 | no | survives |

Two structural observations, verified exactly on the graphs in the table (stated as
observations, not theorems — `M(C7)`, which is pentagon-poor for its order, has `|R| = 57` and
no partition, so neither statement is universal):

* on the pentagon-rich graphs with `R(H) ≠ ∅` — `C₅`, Petersen, Wagner, Grötzsch, Clebsch —
  there are **exactly five** rainbow-1 cuts and their
  monochromatic sets **partition** `E(H)`; each class is then an odd-cycle edge transversal
  (`E∖F_j` bipartite, checked by 2-colouring), so `E(H)` splits into five transversals and every
  induced pentagon is *rainbow* — one edge in each class;
* the recorded G8 §7 five-cut family for `And(3)` is reproduced exactly (up to the labelling
  `C8(1,4)` vs `3·circdist>8`): four antipodal pairs of cycle edges plus the four rungs.

The Petersen partition is new and pretty: **the 15 edges of the Petersen graph split into five
3-edge matchings, each a minimum odd-cycle transversal (`bip = 3`), each meeting all 12 induced
pentagons exactly once.** Likewise **Clebsch splits into its five coordinate perfect matchings**
and **Grötzsch into five 4-edge transversals**.

---

## 4. (c) LEMMA R8-3 — a counting proof that `R(And(4)) = ∅`

Let `P` be the number of induced `C₅`s of `H` and `p(e)` the number of them through the edge `e`.
A rainbow-1 set `F` meets every induced pentagon exactly once, so the pentagon sets of distinct
edges of `F` are disjoint and cover everything:

> **LEMMA R8-3.** If `F` is the monochromatic set of a rainbow-1 cut then `Σ_{e∈F} p(e) = P`.
> Hence if `P` is not a sub-multiset sum of `{p(e) : e ∈ E(H)}`, then `R(H) = ∅` and no
> averaging certificate exists for `H`.

`R8_entropy_pentcount.py` (exact subset-sum by bitset DP; the identity `Σ_e p(e) = 5P` is
asserted for every graph):

| graph | `P` | pentagon-degree multiset | `P` a subset sum? |
|---|---|---|---|
| `Wagner` | 8 | `2⁴, 4⁸` | yes |
| **`And(4)`** | **33** | **`5¹¹, 10¹¹`** | **NO** |
| `And(5)` | 98 | `8⁷, 11¹⁴, 20¹⁴` | yes |
| `And(6)` | 238 | `14¹⁷, 21¹⁷, 35¹⁷` | yes |
| `And(7)` | 504 | `20¹⁰, 24²⁰, 36²⁰, 56²⁰` | yes |
| `Petersen` | 12 | `4¹⁵` | yes |
| `Grötzsch` | 31 | `7¹⁰, 8⁵, 9⁵` | yes |
| `Clebsch` | 192 | `24⁴⁰` | yes |

> **COROLLARY (And(4), two lines).** In `And(4)` every edge lies in `5` or in `10` induced
> pentagons and `P = 33`. Every sub-multiset sum of `{5,10}` is divisible by `5`, and `5 ∤ 33`.
> Therefore `And(4)` has no rainbow-1 cut, and **no averaging certificate — arithmetic,
> geometric, power-mean or Gibbs at any `β` — can certify `max_x psi(And(4),x) ≤ 1/25`.**

This replaces G8's exhaustive "intersection of active cut sets over 33 induced `C₅`s is empty"
by a divisibility count, i.e. by the assigned mechanism. (For `And(5)`, `And(6)` and the `N=14`
extremal graph the counting obstruction alone is not enough; there `R = ∅` was established by
exhaustive cut enumeration in both implementations.)

---

## 5. (d) THEOREM R8-4 — the star kill, and two graphs that pass G8's test but die

> **THEOREM R8-4.** Let `H` be triangle-free, `R = R(H)` with `|R| = k ≥ 1`, and suppose some
> vertex `v` has a monochromatic edge in **every** `S ∈ R`. Then
>
> ```
> max_a  min_{S∈R} m_S(a) / (Σa)²   ≥   1/(4k).
> ```
> In particular if `k ≤ 6` then `1/(4k) ≥ 1/24 > 1/25`, and by THEOREM R8-2 **no averaging
> certificate exists for `H`**.
>
> *Proof.* `H` is triangle-free, so `N(v)` is independent and the only edges of `H` inside
> `{v} ∪ N(v)` are the star edges at `v` — the support induces `K_{1,d}`, which is **bipartite**,
> so the true `psi` there is `0`. For each `S ∈ R` pick `u_S ∈ N(v)` with `v u_S ∈ mono(S)`. Put
> `a_v = k`, `a_u = #{S : u_S = u}` for `u ∈ N(v)`, and `0` elsewhere; then `Σa = 2k` and
> `m_S(a) ≥ a_v a_{u_S} ≥ k`, so `min_S m_S(a)/(Σa)² ≥ k/(2k)² = 1/(4k)`. ∎

### Grötzsch — exact witness (both implementations)

`R(Grötzsch)` consists of five cuts whose monochromatic sets partition the 20 edges into five
4-edge odd-cycle transversals; the apex `c` (degree 5) has exactly one edge in each class. Take

```
a = (0,0,0,0,0, 1,1,1,1,1, 5)      (weight 1 on each shadow, 5 on the apex),  Σa = 10.
```

The support induces the star `K_{1,5}`, which is **bipartite**, so `psi(Grötzsch, a) = 0`
(verified exactly over all `2¹⁰` cuts). Yet

```
m_S(a) = 5 for all five S ∈ R,     min/(Σa)² = 5/100 = 1/20  >  1/25 = 4/100.
```

So every averaging certificate for `Grötzsch` is off by the factor `25/20 = 5/4` on a weighting
where the truth is `0`. **`Grötzsch` passes the G8 §6.3 test (`R ≠ ∅`) and still dies.**

### Clebsch — exact witness

The Clebsch graph (folded 5-cube, 16 vertices, 5-regular, triangle-free, `bip = 8`, 192 induced
pentagons) has exactly five rainbow-1 cuts, whose monochromatic sets are its **five coordinate
perfect matchings** (8 edges each). Every vertex has degree 5 and meets all five classes. With

```
a(0) = 5,  a(u) = 1 for u ∈ N(0) = {1,2,4,8,15},  0 elsewhere,   Σa = 10,
```

the support again induces `K_{1,5}` (bipartite, `psi = 0`), while `m_S(a) = 5` for all five
`S ∈ R`, i.e. `1/20 > 1/25`. **Clebsch dies for the same reason.**

Both witnesses are exact integers and were recomputed independently in
`R8_entropy_survivors.py` from an edge-bitmask rainbow-1 routine.

---

## 6. Why the value is always `1/20`: one unified explanation

Motzkin–Straus for triangle-free `H` gives `max_x Σ_{uv∈E} x_u x_v = 1/4` (`ω = 2`), attained on
any complete bipartite subgraph with mass `1/2` on each side — a single edge, or the star
`K_{1,d}` with `1/2` on the centre and `1/2` spread on the leaves. If a certificate's value at
`x` is forced to be at least a `1/5`-share of the total edge weight `W(x)`, it is at least
`(1/4)/5 = 1/20 > 1/25` and dies. Three previously separate facts are this one fact:

* **A6** (recorded dead): on `C₅` at `x = (½,½,0,0,0)` the total weight `1/4` sits on one edge,
  and the 5-fold symmetry forces some cut to make it monochromatic with probability `≥ 1/5`.
* **f3 §5**: every rotation-invariant distribution over bipartitions of `Z₅` gives `≥ |E|/5`;
  on `K_{m,m}` that is `N²/20`.
* **THEOREM R8-4 here**: the five rainbow-1 classes each receive exactly a `1/5`-share of the
  star's weight `1/4`.

The geometric mean escapes this only when some class receives weight `0`, i.e. when the
*unbalanced* configurations are the dense ones. On `C₅` they are (`x = (½,½,0,0,0)` gives four
zero classes, `GM = 0`). On `Grötzsch` and `Clebsch` a degree-5 vertex makes them perfectly
balanced, and the geometric mean is then equal to the arithmetic one. **The obstruction is
exactly a degree-5 star whose edges are spread over all five classes**, and a minimal
counterexample has `δ > (4N−2)/25` with `N ≥ 41`, hence `δ ≥ 7`: such stars are unavoidable
there, only their class-spread is not forced.

---

## 7. What survives, and why it does not help

Survivors of the rigidity + kill tests: `C₅`-blow-ups, **Petersen**, **Wagner**. For those the
route reduces to a single explicit polynomial inequality (`R8_entropy_partition.py`, exact
integer sweeps over all `a ≥ 0` with `Σa ≤ 22` resp. `≤ 20`, plus continuous search):

```
Wagner   : max_a 25·min_j q_j /(Σa)² = 1   and   max_a 5¹⁰·Π_j q_j /(Σa)¹⁰ = 1   (equality at a = (0,1,0,1,1,0,1,1))
Petersen : max_a 25·min_j q_j /(Σa)² = 1   and   max_a 5¹⁰·Π_j q_j /(Σa)¹⁰ = 1   (equality at a = (0,0,0,0,0,1,1,1,1,1))
```

with `q_j(a) = Σ_{uv ∈ F_j} a_u a_v` over the canonical partition. The Wagner instance is
exactly the terminal lemma recorded in G8 §7 (still unproved); the **Petersen instance is new**:

```
(TERM_Petersen)   q₁q₂q₃q₄q₅ ≤ (Σa)¹⁰/5¹⁰ ,
   F₁={01,38,79}, F₂={12,49,58}, F₃={16,34,57}, F₄={05,23,69}, F₅={04,27,68}
```

(Petersen labelled: outer `C₅` `0..4`, inner pentagram `5..9`, spokes `i ~ 5+i`.)

**But proving either is now of limited value**: both graphs are 3-regular, and both fail to
extend — `And(4)`, `Grötzsch` and `Clebsch` show the fixed-family route cannot be continued past
them. In the `psi` formulation the conjecture must be proved for *every* triangle-free `H`,
including `And(4)`; the route is therefore closed.

### Census (`R8_entropy_census.py`, `R8_entropy_census2.py`)

| class | #graphs with an induced `C₅` | `R = ∅` | star kill | alive |
|---|---|---|---|---|
| all connected triangle-free, `n = 5..9` | 1, 2, 14, 83, 632 | 0 | 0 | all |
| connected triangle-free `δ ≥ 4`, `n = 10` | 1 | 0 | 0 | 1 |
| connected triangle-free `δ ≥ 4`, `n = 11` | 8 | 1 | 0 | 7 |
| connected triangle-free `δ ≥ 4`, `n = 12` | 124 | 1 | 4 | 119 |

Kills begin exactly where the graphs become pentagon-rich; every small survivor has a large
`R(H)` (20–35 admissible cuts) and reaches the ratio `1` only at induced-`C₅` concentrations,
i.e. it survives for the trivial reason that it is far from extremal.

---

## 8. Ideas tried and killed in this lane (with the falsifier)

| idea | status | falsifier |
|---|---|---|
| `Z₅`-rotation geometric mean with `φ` chosen from `x` (PRGM) | **DEAD** | Wagner, uniform: `162 > 109.95` (exact: `5¹⁰·162 > 8¹⁰`) |
| reweighting the five rotations to repair PRGM | **DEAD** | Lemma R8-1b: uniform weights are forced |
| Gibbs / exponential-moment (free-energy) certificates, `β > 0` | **DEAD** | THEOREM R8-2 + And(4) (`5 ∤ 33`) |
| fixed geometric-mean certificate on a pentagon-rich graph | **DEAD** | `Grötzsch` and `Clebsch` star witnesses at exactly `1/20` |
| `bip^{5/2} ≤ #C₅` (pentagon counting) | already recorded dead (Q1 §6) | `C₇`: `bip = 1 > 0 = c₅`. Re-derived, not re-tried. |
| bounding `bip` by `min_I e(G − N(I))` | already recorded dead (Q1 §3) | Grötzsch: `5 > 4` |

---

## 9. Files (all in `problems/23/round8/`)

| file | content |
|---|---|
| `R8_entropy_core.py` | graphs, exact `bip`/`psi` over all cuts, the rotation identity, pure-Python exhaustive PRGM |
| `R8_entropy_prgm.py` | numpy exhaustive PRGM over all `5^{n-1}` maps + double re-derivation of `m_r` |
| `R8_entropy_rigidity.py` | THEOREM R8-2, rainbow-1 cut enumeration (vertex-side implementation) |
| `R8_entropy_verify.py` | **independent** re-implementation (edge bitmasks, BFS 2-colouring): Grötzsch kill, And(4) emptiness, Wagner/Petersen partitions |
| `R8_entropy_partition.py` | canonical 5-partition extraction, terminal inequalities, exact integer sweeps |
| `R8_entropy_targets.py` | the structured-graph table (Andrásfai, Mycielskians, Clebsch, `N=14` extremal) |
| `R8_entropy_survivors.py` | second-implementation star kills (Grötzsch, Clebsch) + survivor sweeps |
| `R8_entropy_pentcount.py` | LEMMA R8-3, pentagon degrees and the exact subset-sum test |
| `R8_entropy_census.py`, `R8_entropy_census2.py` | `geng`-fed censuses |

Reproduce the two headline items:

```
python R8_entropy_prgm.py                 # PRGM table; Wagner/Grotzsch/And(4) FAIL
python R8_entropy_verify.py               # Grotzsch kill 1/20 vs 1/25; And(4) has no rainbow-1 cut
python R8_entropy_pentcount.py            # And(4): degrees 5,10 vs P=33  ->  5 does not divide 33
python R8_entropy_survivors.py            # Clebsch kill, survivor sweeps
```

---

## 10. Honest summary

The assigned mechanism produced **no new upper bound on `bip`**. What it produced is a complete
and exactly-witnessed closure of the fixed-distribution branch of the mechanism:

1. every averaging certificate must live on rainbow-1 cuts (THEOREM R8-2), including the whole
   Gibbs/exponential-moment family that the entropy method would naturally reach for;
2. those cuts do not exist for `And(4)` — by a divisibility count, `5 ∤ 33` (LEMMA R8-3) — nor
   for `And(5)`, `And(6)`, nor for the `N=14` extremal graph;
3. where they do exist they are killed by a degree-5 star at exactly the recorded `1/20`
   barrier (THEOREM R8-4: Grötzsch, Clebsch);
4. and the one `x`-adapted repair the previous entropy rounds pointed to — geometric mean over
   the five `Z₅` rotations of a weight-dependent `φ` — fails already on the 8-vertex Wagner graph
   (Lemma R8-1b shows it cannot be reweighted).

Any surviving proof of Erdős #23 must therefore choose its cut **as a function of the weights**
and be **exactly optimal at every induced-pentagon weighting simultaneously** — the rotation
family is not such a rule, and no fixed family is.
