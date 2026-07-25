# Minimal-counterexample deletion-signature audit

Status: **deletion signature PASS; proposed double-count BLOCKED**.

This note audits only the route registered in `APPROACH_REGISTRY.md`. It is
not a proof of SSNC and it makes no bounded-search claim.

## Exact deletion signature

Let `D` be a vertex-minimal counterexample to SSNC, fix `v in V(D)`, and put
`H=D-v`. Since `H` is smaller, it has an SNP vertex `u`, meaning

`|N2_H+(u)| >= |N_H+(u)|`.

Then all of the following hold:

1. `u -> v`;
2. `|N2_H+(u)|=|N_H+(u)|`;
3. `N2_D+(u)=N2_H+(u)`;
4. `N_D+(v) subseteq N_H+(u) union N2_H+(u)`.

The first three conclusions hold for every SNP vertex of `D-v`, not merely
for one chosen witness.

### Proof

Every two-step path already present in `H` remains present in `D`. If
`u -> v` is absent, reinserting `v` does not increase the first outdegree of
`u`, while it cannot remove any old new second out-neighbor. Therefore

`|N2_D+(u)| >= |N2_H+(u)| >= |N_H+(u)|=|N_D+(u)|`,

contradicting that `D` is a counterexample. Hence `u -> v`.

Write

`a=|N2_D+(u) setminus N2_H+(u)|`.

Now

`|N_D+(u)|=|N_H+(u)|+1`

and

`|N2_D+(u)|=|N2_H+(u)|+a`.

The strict failure of the SNP at `u` in `D`, integrality, and the SNP
inequality in `H` give

`|N2_H+(u)|+a <= |N_H+(u)| <= |N2_H+(u)|`.

Consequently `a=0` and equality holds in `H`, proving items 1--3.

For item 4, take `w in N_D+(v)`. The path `u -> v -> w` exists. Also
`w != u`, because `w=u` would make a digon with `u -> v`. If `u -> w`, then
`w in N_H+(u)`. Otherwise `w in N2_D+(u)=N2_H+(u)`. This proves the
containment.

## Consequences available for a double-count

Let

`P={(u,v): u is an SNP vertex of D-v}`.

The signature gives

- every fibre over `v` is nonempty, so `|P|>=n`;
- `P subseteq A(D)`, the directed arc set;
- for `(u,v) in P`, writing `d_u=d_D+(u)`,

  `|N_H+(u)|=|N2_H+(u)|=d_u-1`;

- hence

  `d_D+(v) <= 2d_u-2`;

- and the literal unreachable set

  `R(u)=V(D) setminus ({u} union N_D+(u) union N2_D+(u))`

  has exact size

  `|R(u)|=n-2d_u`;

- for every `(u,v) in P` and every `w in R(u)`, the arc `v -> w` is absent.

Thus the natural forbidden-triple set

`F={(u,v,w):(u,v) in P and w in R(u)}`

satisfies the exact identity

`|F|=sum_{(u,v) in P}(n-2d_u)`.

## Why the current double-count does not collapse the degree

The forced-arc count alone yields only

`n <= |P| <= |A(D)|`,

which provides no upper bound on the minimum outdegree. The forbidden-triple
count also lacks the required upper bound: a fixed absent ordered pair
`v -> w` may be represented by many different signature sources `u`. The
deletion signature supplies no constant bound on this multiplicity and does
not ensure that a selected source `u` has minimum outdegree.

The sharp packing parameter cell makes the deficit explicit. Set

`n=2 delta+3`, `d_x=delta` for every vertex, and use only one signature pair
over each deleted vertex. The available counts are then

`|P|=n`, `|A(D)|=n delta`, `|R(u)|=3`, and `|F|=3n`.

Even a balanced orientation with missing degree two has
`n(delta+2)` absent ordered pairs between distinct vertices, so the numerical
requirements

`n <= n delta` and `3n <= n(delta+2)`

are compatible for every `delta>=1`. At the first target cell
`(n,delta)=(19,8)`, they read `19<=152` and `57<=190`.

This is a parameter-feasibility obstruction, not an assertion that such an
orientation satisfies the complete deletion signature. It proves that the
registered forced-arc count and the unweighted forbidden-pair count, by
themselves, cannot yield `delta<=7`.

## Exact missing lemma

To continue this route, one needs at least one new load-bearing statement of
one of the following forms:

1. a bounded multiplicity theorem for
   `{u:(u,v) in P and w in R(u)}` for each absent ordered pair `(v,w)`;
2. a lower bound on the number of SNP vertices in every `D-v` strong enough
   to make `|P|` exceed the arc capacity;
3. a theorem selecting signature sources of controlled outdegree together
   with an overlap restriction on their unreachable sets.

No such statement follows from the deletion signature proved above. Without
one, the proposed double-count has no explicit bridge to `delta+(D)<=7`.
