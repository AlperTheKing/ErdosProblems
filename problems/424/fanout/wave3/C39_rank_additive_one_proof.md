# C39: actual-G rank additive-one proof lane

## Verdict

No proof and no actual-`G` falsifier was obtained for

\[
 H_{\le d}(X)\le Q_{\le d}(X)+1. \tag{AO}
\]

The sharp obstruction is not another Hall reformulation. The death
recurrence gives a canonical seed-2/seed-3 forest and the exact scalar
potential identity (8) below. At the hard source `74`, however, every
compatible terminal boundary in the source's own death component occurs
too late and at too high a rank. The two credits that make (AO) true at
that cutoff come from unrelated components. Thus a rank induction must
transport capacity globally between unrelated death components.

A canonical strengthening survives finite testing: retaining only the first
two healed seed-2 boundaries in each canonical hole component still leaves
only `362` of rank `2` unmatched through `10^7`. This is finite evidence,
not an extrapolation.

## 1. Definitions

Let

\[
 \mathcal A=\{n\ge2:n\not\equiv1\pmod3\},
\]

and let `G` be the least subset of `A` containing `2,3` and closed under
`a,b -> ab-1` for distinct `a,b`. Put `M=A\G`. For an allowed `n`, write

\[
 \mathcal P(n)=\{(a,b):2\le a<b,\ a,b\in\mathcal A,\ ab=n+1\}.
\]

For a hole, the obstruction rank is

\[
 \rho(n)=0\quad(\mathcal P(n)=\varnothing),
\]

and otherwise

\[
 \rho(n)=1+\max_{(a,b)\in\mathcal P(n)}
   \min\{\rho(x):x\in\{a,b\}\cap\mathcal M\}. \tag{1}
\]

A hard hole is a reducible even hole outside the usable seed-3 class,
exactly as in C31. The target attached to a missing `q` is counted at
its generated child `2q-1`. Thus

\[
 H_{\le d}(X)=\#\{n\le X:n\text{ hard},\ \rho(n)\le d\},
\]

\[
 Q_{\le d}(X)=\#\{q\in\mathcal M:2q-1\le X,\ 2q-1\in G,
                                      \rho(q)\le d\}. \tag{2}
\]

C31 proves that (1) is death rank minus one in the descending grounded
approximants. All arguments below use the actual least `G`.

## 2. Canonical seed forest

For a hole `n`, define a canonical parent when one of the following applies:

\[
 \pi(n)=\frac{n+1}{2}\quad\text{if }n>3\text{ is odd}, \tag{3}
\]

\[
 \pi(n)=\frac{n+1}{3}\quad\text{if }n\text{ is seed-3-easy even}. \tag{4}
\]

### Lemma 1

The parent in (3) or (4) is an allowed hole smaller than `n`, and

\[
                    \rho(\pi(n))<\rho(n).             \tag{5}
\]

Every hole with no canonical parent is either splitless or hard. Hence the
holes form a rooted forest under `pi`; its roots are precisely the
splitless holes and hard holes.

### Proof

If `n>3` is an allowed odd hole, `(n+1)/2` is allowed and distinct from
`2`. If it belonged to `G`, the pair `(2,(n+1)/2)` would generate `n`.
It is therefore a hole. This pair occurs in (1), so
`rho(n)>=rho((n+1)/2)+1`.

For a seed-3-easy even hole, the same argument uses the admissible distinct
pair `(3,(n+1)/3)`. The two parent rules cannot conflict because (3) has
an odd child and (4) an even child. An allowed odd nonseed always has the
parent (3). An even reducible hole without (4) is hard by definition; an
even irreducible hole is splitless. Values and ranks strictly decrease
along parent edges, so there are no cycles. QED.

The odd-parent restriction on seed-3 child edges is essential:
`23=3*8-1` is odd and has canonical seed-2 parent `12`, not seed-3 parent
`8`. This falsifies the unrestricted forest identity at `(X,d)=(23,1)`.

## 3. Exact rank-filtered potential

For `d>=0`, put

\[
 M_d(X)=\#\{n\in\mathcal M:n\le X,\ \rho(n)\le d\},
\]

and let `O_d(X)` count the odd members in this set. Let `E(X)` count
splitless holes. Set

\[
 Y=\left\lfloor\frac{X+1}{2}\right\rfloor,\qquad
 Z=\left\lfloor\frac{X+1}{3}\right\rfloor.
\]

Define the transient seed boundaries

\[
 A_{2,d}(X)=\#\{q\in\mathcal M:2q-1\le X,\
   \rho(q)\le d<\rho(2q-1)\},                       \tag{6}
\]

\[
 A_{3,d}(X)=\#\{q\in\mathcal M:q\text{ odd},\ 3q-1\le X,\
   \rho(q)\le d<\rho(3q-1)\},
\]

where the displayed children are holes. Finally, let

\[
 R_{3,d}(X)=\#\{q\in\mathcal M:q\text{ odd},\ 3q-1\le X,\
                              3q-1\in G,\ \rho(q)\le d\}. \tag{7}
\]

### Lemma 2 (potential identity)

For every integer `X` and every `d>=0`,

\[
\boxed{
 H_{\le d}(X)-Q_{\le d}(X)
 =M_d(X)-E(X)-M_d(Y)-O_d(Z)
  +A_{2,d}(X)+A_{3,d}(X)+R_{3,d}(X).
}                                                       \tag{8}
\]

### Proof

Let `U_d(X)` count odd holes of rank at most `d`, and let `V_d(X)`
count seed-3-easy even holes of rank at most `d`. Then

\[
 M_d(X)=E(X)+H_{\le d}(X)+U_d(X)+V_d(X).              \tag{9}
\]

For each rank-filtered hole `q<=Y`, its seed-2 child is exactly one of an
odd hole still in the rank prefix, a generated child counted by `Q`, or a
higher-rank transient counted by `A_2`. Lemma 1 gives the converse, hence

\[
 M_d(Y)=U_d(X)+Q_{\le d}(X)+A_{2,d}(X).              \tag{10}
\]

The seed-3-easy even holes have odd missing parents. The same trichotomy on
odd rank-filtered holes `q<=Z` gives

\[
 O_d(Z)=V_d(X)+R_{3,d}(X)+A_{3,d}(X).                 \tag{11}
\]

Substituting (10) and (11) in (9) proves (8). QED.

Consequently (AO) is the scalar potential bound

\[
 M_d(X)+A_{2,d}(X)+A_{3,d}(X)+R_{3,d}(X)
 \le E(X)+M_d(Y)+O_d(Z)+1.                            \tag{12}
\]

This exposes the missing sign without introducing a matching graph. The
death recurrence controls ranks on each seed edge, but supplies no
component-local cancellation of the three boundary terms in (12).

## 4. Exact obstruction at 74

The hard source `74` has the unique admissible split

\[
                         75=5\cdot15.
\]

Here `5` is generated and `15` is a rank-one hole, so `rho(74)=2`.
The canonical component of the blocker starts at the splitless root `8`.
The exact recurrence on its seed-2 spine is

\[
\begin{array}{c|rrrrrr}
q&8&15&29&57&113&225\\ \hline
\rho(q)&0&1&2&3&4&5.
\end{array}
\]

All six values are holes, while

\[
 449=2\cdot225-1=9\cdot50-1\in G.
\]

Thus the first healed seed-2 boundary in the entire canonical component
of the missing factor `15` is child `449`, with parent rank `5`. It is
incompatible with source `74` both in coordinate and rank.

Nevertheless the global prefix at `(X,d)=(74,2)` is exact:

\[
 \{\text{hard sources}\}=\{54,74\},
\]

\[
 \{\text{compatible targets}\}=\{41,69\}.
\]

The target `41` has parent `21`, rank `2`, and canonical root `6`; target
`69` has parent `35`, rank `1`, and canonical root `18`. Neither lies in
the component of blocker `15`. This proves the obstruction: descending the
death recurrence from a source and returning along the same component
cannot establish even the second hard cutoff. The needed credit is
genuinely cross-component.

## 5. Exact falsifiers to simpler inductions

Every row was recomputed on the least grounded set before it was used.

| proposed intermediate claim | exact falsifier |
|---|---|
| strict dominance at every odd cutoff | rank-2 excess one at every odd `X=1003,1005,...,1017` |
| `H_{<=d}(X)<=Q_{<=d-1}(X)` for `d>=3` | `X=186,d=3`: counts `6,5` |
| one healed boundary per canonical component suffices | first unmatched source `186`, rank `2` |
| `14a-1` generated always implies parent `7a` missing | `a=65`: `7a=455` is generated |
| generated-multiplier/factor-endpoint injection | `2088` zero-degree sources among `5108` through `10^5` |
| unrestricted seed-3 forest child | `q=8`: `23` has canonical seed-2 parentage |

For the multiplier falsifier, the memberships are grounded explicitly:
`65=2*33-1`, `152=3*51-1`, and `455=3*152-1`.

## 6. Strongest surviving finite gate

Order the healed seed-2 boundary children in each canonical hole component
by child coordinate, and retain only the first two. At a hard source of
rank `r`, the diagnostic consumes the largest available retained target
rank at most `r`. This is a finite diagnostic, not a proof conclusion.

| limit | hard sources | all targets | one-boundary unmatched | two-boundary unmatched |
|---:|---:|---:|---:|---:|
| `5,000` | `253` | `290` | `12` | `1` (`362`) |
| `100,000` | `5,108` | `6,783` | `20` | `1` (`362`) |
| `1,000,000` | `45,583` | `67,537` | `20` | `1` (`362`) |
| `10,000,000` | `392,961` | `637,270` | `20` | `1` (`362`) |

The independent trial-divisor replay through `5000` also constructs the
literal descending approximants. It reports zero membership, death-rank,
forest, or potential-identity mismatches. The first-two-boundary gate is
strictly stronger than the tested instance of (AO), but there is no proved
reason that every later global deficit can be paid by this subfamily.
Source `74` already shows that such a reason cannot be component-local.

## 7. Irreducible frontier

A proof must establish the sign in (12), or an equally global invariant,
by moving capacity between unrelated canonical components while respecting
both child coordinates and death ranks. The grounded recurrence supplies
only:

1. strict rank descent toward a splitless or hard root;
2. exact transient and terminal boundary terms in (8); and
3. no local relation between a hard blocker's component and the components
   supplying its compatible targets.

The concrete obstruction is `(74,15,449)`: local descent reaches rank `0`,
but the first return to `G` in that component occurs at rank `5` and
coordinate `449`, while the theorem needs unrelated credits `41,69` by
rank `2` and coordinate `74`. Any induction whose state records only the
current source, its critical factors, their death ranks, or their canonical
components loses exactly the global information needed here.

Thus the actual theorem remains open in this lane. The constant `1` is
forced by `H_{<=2}(362)=11` and `Q_{<=2}(362)=10`; no strengthening to
zero slack is claimed.

## 8. Reproduction

```powershell
python problems/424/compute/wave3/C39_rank_additive_one_proof/probe_seed_forest.py `
  --limit 10000000 `
  --output problems/424/compute/wave3/C39_rank_additive_one_proof/seed_forest_1e7.json

python problems/424/compute/wave3/C39_rank_additive_one_proof/verify_seed_forest_small.py `
  --limit 5000 `
  --output problems/424/compute/wave3/C39_rank_additive_one_proof/verify_5000.json

python problems/424/compute/wave3/C39_rank_additive_one_proof/probe_multiplier_targets.py `
  --limit 100000 --multiplier-cap 500 `
  --output problems/424/compute/wave3/C39_rank_additive_one_proof/multiplier_100k.json
```
