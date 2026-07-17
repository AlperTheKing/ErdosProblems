# C65: seed-chain reduction and the ordered descending-bank frontier

## Verdict

The uniform C60 min-cut statement was **not proved or falsified**.  What can
be proved is an exact seed-chain reduction that turns every admissible cut
into a comparison between unhealed seed chains and selected nonhard roots.
This isolates a stronger, ordered arithmetic bank inequality whose truth
would imply C60.

The most obvious number-theoretic injection is false.  At ambient cutoff
`X=186`, the first six hard roots have only five directly healed source
chains.  The sixth unit is supplied by the genuine unary transfer

```text
48 -> 95 -> 32 -> 63 -> generated 125.
```

Thus any proof must allow global transfer between seed chains.  This is not
the local obstruction at `h=74`: that obstruction is paid by the unrelated
splitless roots `18` and `6`.  The historical rerouting at `X=377` is also
accounted for: it occurs only when the old recurrence saturates all three
reserve units, whereas the ordered construction below carries exactly the
12 demanded units and uses no reverse arc.

The smallest surviving constructive frontier is the **forward ordered-bank
lemma** in Section 6.  It uses arbitrarily many strictly descending unary
transfers; no bounded-depth claim is made.

## 1. Distinct-factor convention

Write

\[
 V_X=\{n\in[2,X]:n\not\equiv1\pmod 3\}.
\]

All factorizations in this note are admissible distinct-factor
factorizations

\[
 n+1=ab,\qquad 2\le a<b,\qquad a,b\in V_X.
\tag{1}
\]

In particular, a square factorization `a*a=n+1` is never used.  The program
implements (1) by the strict loop guard `a*a < n+1`.  Let `G_X` be the least
generated set from the seeds `2,3`, let `M_X=V_X\G_X`, and use the C60
definitions of hard holes `K_X` and structural splitless holes `E_X`.

For a hole `n`, a unary arc

\[
 n\longrightarrow p
\tag{2}
\]

exists when `n+1=gp` with `g in G_X`, `p in M_X`, and `g != p`.

## 2. Exact seed-chain lemma

For an allowed integer `n`, define its seed root by

\[
 r(n)=n\quad(n\text{ even}),\qquad
 r(n)=r((n+1)/2)\quad(n\text{ odd}).
\tag{3}
\]

For each even root `r`, its seed-2 chain is

\[
 C_r=(r,2r-1,4r-3,\ldots).
\tag{4}
\]

Let `W_X(r)` be the last member of this chain not exceeding `X`.

### Lemma 2.1 (prefix and balance identity)

Let `S subseteq M_X` contain every splitless hole and be closed under all
unary arcs (2).  Then:

1. `S cap C_r` is an initial segment of `C_r` for every root `r`;
2. every selected chain contributes exactly one outgoing seed arc unless
   `W_X(r) in S`, in which case it contributes zero; and
3. for every even allowed cutoff `Y<=X`,

\[
 Q_Y(S)-H_Y(S)=N_Y(S)-U_Y(S).                 \tag{5}
\]

Here `Q_Y` is the number of seed arcs leaving `S` on chains with root at
most `Y`, `H_Y` is the number of selected hard roots at most `Y`, `N_Y` is
the number of selected nonhard roots at most `Y`, and `U_Y` is the number
of selected roots at most `Y` for which `W_X(r) in S`.

### Proof

If an odd hole `c=2m-1` belongs to `M_X`, then `m` is also a hole.  Indeed,
`m in G_X` would generate `c` from the distinct factors `2,m`; holes are
larger than the exceptional equal-factor case `m=2`.  Hence `c->m` is a
unary arc with generated factor `2`.  Unary closure therefore gives

\[
 c\in S\Longrightarrow m\in S.                \tag{6}
\]

Repeatedly applying (6) proves the initial-segment assertion.  Conversely,
generation is upward closed on every seed-2 chain, again using the distinct
factors `2,m`.  Thus a chain containing a hole has a hole root.

An empty chain contributes nothing.  A nonempty proper initial segment has
one last selected vertex and therefore one seed edge leaving it.  If the
initial segment reaches `W_X(r)`, its next seed edge lies beyond `X`, so it
contributes zero.  Thus

\[
 Q_Y=(H_Y+N_Y)-U_Y,
\]

which is (5).  No equal-factor factorization was used.  QED.

At `Y=X`, (5) proves that the C60 assertion is equivalent to

\[
 U_X(S)\le N_X(S).                              \tag{7}
\]

## 3. Ordered strengthening

For fixed `X,Y`, form `N_{X,Y}` from the C60 network as follows:

* retain all infinite splitless source arcs and all unary arcs;
* retain hard source arcs only for hard roots `h<=Y`; and
* retain unit seed arcs only on chains with root at most `Y`.

Let `kappa_{X,Y}` be its integral max-flow value.

### Lemma 3.1 (ordered cut equivalence)

The following are equivalent:

\[
 \kappa_{X,Y}\ge |K_X\cap[2,Y]|,               \tag{8}
\]

and

\[
 U_Y(S)\le N_Y(S)                               \tag{9}
\]

for every splitless-containing unary-closed `S subseteq M_X`.

### Proof

No finite minimum cut crosses an infinite arc, so its source side is exactly
such a set `S`.  Its finite capacity is

\[
 |(K_X\cap[2,Y])\setminus S|+Q_Y(S).
\]

The max-flow/min-cut theorem says that this is at least
`|K_X cap [2,Y]|` for every `S` exactly when `Q_Y(S)>=H_Y(S)`.  Equation
(5) turns the latter inequality into (9).  QED.

Consequently, (8) for every `Y<=X` is stronger than C60 and gives an
order-preserving injection from the unhealed roots to selected nonhard
roots: after sorting, the matched nonhard root is no larger than its
unhealed target.

There is additional arithmetic structure. A seed arc preserves `r(n)`,
whereas every unary arc `n->p` strictly decreases the integer, because

\[
 p=(n+1)/g\le(n+1)/2<n.                         \tag{10}
\]

The integer descent does **not** imply seed-root descent. The first exact
counterexample is the valid selector

```text
89 -> 18, because 90 = 5*18,
r(89)=12 < 18=r(18).
```

Here `5` is generated and `89,18` are holes. Thus cross-chain transport is
acyclic in vertex value, but not ordered by seed root. Any proof of the
ordered cut statement must not use root-monotonicity.

## 4. Exact obstruction to direct chain payment

Call a source root direct if it is splitless or hard and its own seed chain
reaches a generated child by cutoff `X`.  The tempting prefix estimate

\[
 \#\{\text{direct source roots}\le Y\}
 \ge |K_X\cap[2,Y]|                              \tag{11}
\]

is false.

### Proposition 4.1 (first direct-bank failure)

The smallest failure found by exhaustive exact scanning through ambient
cutoff `5000` occurs at `X=Y=186`.  The hard roots are

```text
54, 74, 114, 144, 174, 186
```

but the only directly healed source roots at most `186` are

```text
6, 18, 20, 38, 66.
```

Hence (11) has values `5<6`.

The full ordered network pays the missing unit by

```text
48 --seed--> 95 --unary(96=3*32)--> 32
   --seed--> 63 --seed--> generated 125.
```

All factors are distinct.  The root `48` is splitless because `49=7^2`
does not give a distinct allowed pair.  The unary step uses the generated
factor `3`, and `125` is generated by `126=9*14` with distinct generated
factors.  This proves that a global cross-chain discharge is genuinely
necessary; direct endpoint or direct seed-chain accounting cannot prove
C60.

## 5. The two required guardrails

### The local failure at `h=74`

The hard factorization

\[
 75=5\cdot15
\]

only descends from `74` to the hole chain `15,29,57`; that chain has no
paying exit by `X=74`.  The exact ordered certificate instead uses two
unrelated splitless banks:

```text
18 -> 35 -> generated 69       (pays the prefix ending at hard root 54),
 6 -> 11 -> 21 -> generated 41 (pays the prefix ending at hard root 74).
```

The roots `18` and `6` are splitless because `19` and `7` are prime.  This
is the global payment missing from the chain-local mechanism in C62.

### The reroute at `X=377`

The full C60 network at `X=377` has 12 hard holes and exact maximum flow
15, hence reserve 3.  The cutoff-ordered saturated recurrence reroutes via

```text
s -> 144 -> 287 -> 32 -> 95 -> 189 -> z,
```

where `32->95` is the reverse of the unary arc `95->32` coming from
`96=3*32`.

The ordered-demand construction activates roots in increasing order and
carries only the demanded units.  At `X=377` it carries all 12 units with
12 forward paths, no unary edge and no reverse edge.  It deliberately does
not saturate the three reserve units.  Therefore the known reroute is not a
counterexample to the ordered frontier; it explains why saturating the full
flow is the wrong induction invariant.

## 6. Smallest surviving frontier

The exact proof target left by this task is:

### Forward ordered-bank lemma

Fix `X` and list its hard holes increasingly as

\[
 h_1<h_2<\cdots<h_k.
\]

For each `i`, activate all seed arcs on roots at most `h_i`, all splitless
source arcs, all unary arcs, and the first `i` hard source arcs.  Then there
is an integral flow of value `i`.  Moreover, the flows may be chosen
nested: the flow for `i` is obtained from that for `i-1` by one forward
source-sink path, without cancelling an earlier seed arc.

This is a concrete number-theoretic discharging statement. Every path
consumes previously unused unit seed edges and may reuse unlimited unary
edges. Unary edges strictly decrease the current vertex value by (10), but
may increase the seed root, as `89 -> 18` shows. Its first clause is precisely
(8) at the only cutoffs where demand changes and hence proves C60. The nested
clause is stronger, but a proof still needs an invariant that tolerates these
root increases; root order alone is not an induction mechanism.

No bounded number of unary descents is included.  The deterministic exact
certificate at `X=5000` contains

```text
282 -> 563 -> 188 -> 63 -> generated 125,
```

with two unary descents (`564=3*188` and `189=3*63`).  This does not prove
that every certificate needs two, but it invalidates treating a one-unary
normal form as established.

## 7. Exact gates

All arithmetic is integer arithmetic.  The tests preserve distinct factors
and use an integral Dinic implementation or unit residual BFS.

| Gate | Exact result |
|---|---:|
| every ambient `2<=X<=500`, every even root cutoff | 41,667 cuts, no failure |
| ambient `318,362,377,500,1000,2000,5000`, every root cutoff | 3,186 cuts, no failure |
| ordered forward augmentation at `X=5000` | 253/253 demands, 0 reversals |
| ordered forward augmentation at `X=100000` | 5,108/5,108 demands, 0 reversals |
| exhaustive direct-bank scan through `X=5000` | first failure `(X,Y)=(186,186)` |

These are finite falsification gates, not a proof of the forward
ordered-bank lemma.

## 8. Reproduction

```powershell
python -m py_compile problems/424/fanout/wave5/C65_cut_arithmetic.py

python problems/424/fanout/wave5/C65_cut_arithmetic.py `
  --max-limit 500 `
  --output problems/424/fanout/wave5/C65_root_prefix_500.json

python problems/424/fanout/wave5/C65_cut_arithmetic.py `
  --ambient 318 362 377 500 1000 2000 5000 `
  --output problems/424/fanout/wave5/C65_root_prefix_selected.json

python problems/424/fanout/wave5/C65_cut_arithmetic.py `
  --incremental-limit 74 `
  --output problems/424/fanout/wave5/C65_root_paths_74.json

python problems/424/fanout/wave5/C65_cut_arithmetic.py `
  --incremental-limit 186 `
  --output problems/424/fanout/wave5/C65_root_paths_186.json

python problems/424/fanout/wave5/C65_cut_arithmetic.py `
  --incremental-limit 377 `
  --output problems/424/fanout/wave5/C65_root_paths_377.json

python problems/424/fanout/wave5/C65_cut_arithmetic.py `
  --incremental-limit 5000 `
  --output problems/424/fanout/wave5/C65_root_paths_5000.json

python problems/424/fanout/wave5/C65_cut_arithmetic.py `
  --incremental-limit 100000 `
  --output problems/424/fanout/wave5/C65_root_incremental_100k.json

python problems/424/fanout/wave5/C65_cut_arithmetic.py `
  --direct-scan-limit 5000 `
  --output problems/424/fanout/wave5/C65_direct_bank_failure.json

python problems/424/fanout/wave5/C60_large_flow.py `
  --limits 377 `
  --output problems/424/fanout/wave5/C65_full_flow_377.json
```

SHA-256:

```text
A5013066CD84BD27C25F12D60B25EA343494ADF4376E22F849500FB3EC56DA7B  C65_cut_arithmetic.py
DEBA29254DB34C88066D6EC2B675260304D97FC35AC3F2D75B36CA7E40B5D893  C65_root_prefix_500.json
329FFC254FE76EBC25872D4E3FCA4FFE6EF1DFD49B5EC1C0D22B70DC863B2F5E  C65_root_prefix_selected.json
A08D219B6F567742745756A935D52E68CACEEAEB76E13381396FB6E868E235B2  C65_root_paths_74.json
15B48F2273A863AC15AADCB634F08F35D8ABDCC14936BE1C10F04DE70C710D9D  C65_root_paths_186.json
DE477076404DD7C0349C79C53E553B63523002C330919EF19366E7195D9943B4  C65_root_paths_377.json
01D7D254DEA11AA03870D83E33CFBB3E3D84C25C935EB3A73378E223EF37817C  C65_root_paths_5000.json
44ADBFE157508164A5AE5145894DE01B1D8DEEAEE93A49AA3613A9D47DACDB6A  C65_root_incremental_100k.json
E388F73CAD0949AB814E5B75C90F3F8EABA012F40C0CEC30421CD5E00005DFBF  C65_direct_bank_failure.json
893C96EFE59B795E9DE4D9111158FF865664DEF1F88F6655D66F12843F51FBFD  C65_full_flow_377.json
```
