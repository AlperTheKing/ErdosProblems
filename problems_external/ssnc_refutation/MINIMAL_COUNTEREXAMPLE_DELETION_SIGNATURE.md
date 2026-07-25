# Minimal-counterexample deletion signature and the failed degree-collapse count

## Scope

This note records one exact lemma for a hypothetical vertex-minimal
counterexample to Seymour's Second Neighborhood Conjecture, audits the natural
safe-arc double count, and gives an explicit family showing why that count does
not force minimum outdegree at most seven. It is not a proof or disproof of
SSNC.

Throughout, `N++(u)` denotes the new second out-neighborhood: vertices outside
`{u} union N+(u)` having a directed two-edge witness from `u`.

## Exact deletion signature

Let `D` be a vertex-minimal counterexample. Fix `v`, and let `u` be any vertex
with the second-neighborhood property in `D-v`, which exists by minimality. Put

```text
d = |N+_{D-v}(u)|,
s = |N++_{D-v}(u)|,
a = 1 if u->v, and 0 otherwise.
```

Every old two-edge witness in `D-v` persists in `D`, and adding `v` does not
make an old target a direct out-neighbor. Hence
`N++_{D-v}(u) subseteq N++_D(u)`. Define

```text
g = |N++_D(u) setminus N++_{D-v}(u)| >= 0.
```

Then `|N+_D(u)|=d+a` and `|N++_D(u)|=s+g`. The SNP inequality in `D-v` gives
`s>=d`, while failure at `u` in `D` gives `s+g<d+a`. If `a=0`, these inequalities
contradict each other. Thus `a=1`; integrality now gives

```text
d <= s <= s+g < d+1,
```

so `s=d` and `g=0`. Therefore every SNP vertex `u` of `D-v` satisfies all of

```text
u->v,
|N++_{D-v}(u)| = |N+_{D-v}(u)|,
N++_D(u) = N++_{D-v}(u),
d+_D(u)-d++_D(u) = 1.
```

There is also an exact containment. For `x in N+(v)`, either `u->x`, or the
path `u->v->x` and `g=0` put `x` in `N++_{D-v}(u)`. The two sets are disjoint,
so

```text
N+(v) subseteq N+_{D-v}(u) disjoint-union N++_{D-v}(u),
d+(v) <= 2 d+_D(u)-2.
```

## Safe-arc characterization

For any vertex `u`, define its positive deficit

```text
epsilon(u) = d+(u)-d++(u) >= 1.
```

For `w in N++(u)`, let its witness-middle set be

```text
W_u(w) = N+(u) intersect N-(w).
```

For an arc `u->v`, define

```text
L_u(v) = {w in N++(u): W_u(w)={v}}.
```

Deleting `v` removes exactly `L_u(v)` from the new second neighborhood of `u`
and decreases `d+(u)` by one. Consequently

```text
u is SNP in D-v  iff  epsilon(u)=1 and L_u(v)=empty.
```

If `u` does not point to `v`, deletion leaves its outdegree fixed and can only
remove second targets, so it cannot turn a failing `u` into an SNP vertex.

Let

```text
C = {u: epsilon(u)=1},
P = {u->v: u in C and L_u(v)=empty}.
```

Vertex minimality says that every `D-v` has an SNP vertex, hence

```text
d^-_P(v) = #SNP(D-v) >= 1,
n <= |P|.
```

For fixed `u`, let `E_u={u->v: L_u(v) nonempty}`. The nonempty sets `L_u(v)`
are pairwise disjoint: a second target cannot have two different unique
witnesses. Choosing one target from each set injects `E_u` into `N++(u)`, so

```text
|E_u| <= d++(u),
r_u := d+(u)-|E_u| >= epsilon(u).
```

The complete count is therefore only

```text
n <= |P| = sum_{u in C} r_u <= sum_{u in C} d+(u).
```

The useful inequality points in the wrong direction for an upper bound on
minimum outdegree. Equality `|E_u|=d++(u)` means every second target has exactly
one witness and every essential middle owns exactly one target. Equality
`|P|=n` means every `D-v` has exactly one SNP vertex. Even simultaneous equality
produces only a functional safe-arc incidence and no degree bound.

## Explicit high-degree multiplicity family

For `k>=2`, define a tournament `F_k` on

```text
V = {u} union A union B,
|A|=k,
|B|=k-1.
```

Orient all cross pairs by

```text
u -> A,
A -> B,
B -> u.
```

Inside each part choose a near-regular tournament with minimum internal
outdegree `floor((m-1)/2)`. For odd `m` use a regular tournament; for even `m`,
delete one vertex from a regular tournament of order `m+1`. The cross-cycle
makes `F_k` strongly connected.

The degrees are

```text
d+(u) = k,
d+(a) = (k-1)+d_A+(a) >= k-1+floor((k-1)/2),
d+(b) = 1+d_B+(b) >= 1+floor((k-2)/2),
```

with equality for some `b`. Hence

```text
delta+(F_k) = 1+floor((k-2)/2) = floor(k/2).
```

Exactly `N++(u)=B`, so `d++(u)=k-1` and `epsilon(u)=1`. For every `a in A`,
after deleting `a` one still has

```text
N+_{F_k-a}(u)=A setminus {a},
N++_{F_k-a}(u)=B,
```

because every remaining `A` vertex points to every `B` vertex. Thus `u` is an
equality SNP of `F_k-a` for all `k` choices of `a`, and every `u->a` is safe:
`r_u=k=d+(u)`.

At `k=16`, the minimum outdegree is eight and the degree classes are

```text
u: 16,
A: 22 or 23,
B: 8.
```

One deficit-one vertex therefore witnesses sixteen deletions at minimum
degree eight. The family is not an SSNC counterexample—it is a tournament—and
its role is precise: it falsifies any bound on deletion-witness multiplicity
derived only from the deletion signature, high minimum degree, and strong
connectivity.

## Exit

A theorem-closing proof would need a genuinely counterexample-global coupling
that upper-bounds `P` strongly enough to contradict `|P|>=n`, or proves that
some vertex has `d^-_P(v)=0`. No such bound follows from the audited identities,
and the `F_k` family excludes the local multiplicity shortcut. Therefore the
registered route exits with

```text
DEAD: reformulation maze - no degree-collapse inequality
```

The degree-at-most-seven result used by the registered bridge is
https://arxiv.org/abs/2606.30588.
