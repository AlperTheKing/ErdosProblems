# W144-MIN: rooted radius-critical audit

Date: 2026-07-18.

## Result

Fixing an `eta`-realizer and minimizing its distance from the new center does
**not** force a unicyclic induced subgraph, even at girth five.  The exact
order-eight graph below is multicyclic and is the only induced connected
cyclic subgraph containing the fixed root that retains the required rooted
center distance.

Fajtlowicz's radius-critical characterization does not repair this failure.
Ordinary radius preservation can retain the radius while the distance to the
center, and even `eta`, collapses.  The weaker condition that the fixed root
merely remain present in an `eta`-feasible subgraph has no counterexample in
the complete audit through order 11, but no implication from ordinary
radius-criticality to that condition is proved here.  This note therefore is
not a proof or a disproof of W144 or of the unrooted W144-MIN lemma.

## 1. Exact fixed-root counterexample

Let

```text
G = G?`e_w
E(G) = {04,06,15,16,25,36,37,47,57}.
```

Thus `G` is a theta graph with the three `6`--`7` paths

```text
6-3-7,  6-0-4-7,  6-1-5-7,
```

and one additional leaf `2` at `5`.  Direct calculation gives

```text
|V(G)|=8, |E(G)|=9, beta(G)=2, girth(G)=5,
rad(G)=2, C(G)={7}, eta(G)=2.
```

Fix the `eta`-realizer `x=1`.  For an induced connected cyclic subgraph `J`
containing `x`, put

```text
rho_x(J)=d_J(x,C(J)).
```

There are exactly eleven such subgraphs.  They are listed below; `S` is the
vertex set and `beta`, `r`, `eta`, and `rho` are evaluated in `G[S]`.

| `S` | `beta` | `r` | `C(G[S])` | `eta` | `rho` |
|---|---:|---:|---|---:|---:|
| `13567` | 1 | 2 | `13567` | 0 | 0 |
| `013467` | 1 | 2 | `036` | 1 | 1 |
| `013567` | 1 | 2 | `136` | 1 | 0 |
| `014567` | 1 | 3 | `014567` | 0 | 0 |
| `123567` | 1 | 2 | `157` | 1 | 0 |
| `134567` | 1 | 2 | `357` | 1 | 1 |
| `0123567` | 1 | 2 | `1` | 2 | 0 |
| `0124567` | 1 | 3 | `14567` | 1 | 0 |
| `0134567` | 2 | 2 | `367` | 1 | 1 |
| `1234567` | 1 | 2 | `57` | 2 | 1 |
| `01234567` | 2 | 2 | `7` | 2 | 2 |

Consequently the full graph is the unique subgraph satisfying

```text
rho_x(J) >= eta(G)=2.
```

It is therefore vertex-minimal for the rooted condition but has cycle rank
two.  This disproves the proposed implication

```text
fixed eta-realizer + rooted minimality + girth at least five
    ==> unicyclic.
```

Notice that this is stronger than a failed one-vertex deletion rule: the
table enumerates every proper induced vertex subset, so a two-step recovery
of the rooted condition is also excluded.

## 2. Why ordinary radius-criticality loses the exact bridge

Fajtlowicz defines a graph to be radius-critical when every proper induced
connected subgraph has smaller radius, and proves that every connected graph
of radius `r>=1` contains an induced `r`-ciliate.  See S. Fajtlowicz,
*A characterization of radius-critical graphs*, Journal of Graph Theory 12
(1988), 529--532, Theorem 2, DOI `10.1002/jgt.3190120409`.

That theorem has no prescribed-root or center-distance conclusion.  The same
counterexample makes the loss exact in both natural minimizations.

1. The induced path on `{0,1,4,6}` is `4-0-6-1`.  It contains `x=1`, has
   radius two, and every proper connected induced subgraph has radius below
   two.  Thus a vertex-minimal connected radius-preserving subgraph containing
   `x` can be acyclic.  Its `eta` is one, below `eta(G)=2`.
2. If cyclicity is imposed, the induced cycle on `{1,3,5,6,7}` is a bare
   `C5`.  It contains `x`, has the same radius two, and is inclusion-minimal
   among connected cyclic induced subgraphs.  Nevertheless every cycle vertex
   is central, so its `eta` and its rooted depth are both zero.

For the second subgraph, the proved unicyclic theorem supplies only a tree of
order

```text
girth(C5)-1+eta(C5)=4,
```

whereas the ambient W144 target is

```text
girth(G)-1+eta(G)=6.
```

Hence preserving radius, even while preserving the chosen root and
cyclicity, does not preserve the load-bearing W144 quantity.  Applying the
ordinary radius-critical theorem would require an additional assertion that
the selected ciliate contains the prescribed root and retains either
`d(x,C)>=eta(G)` or `eta>=eta(G)`.  The fixed-root example above falsifies the
first assertion, and radius preservation alone does not imply the second.

## 3. What remains open

Two weaker statements were exhaustively tested on every connected
multicyclic girth-at-least-five graph through order 11 (`1,335` graphs).

* Some ambient `eta`-realizer belongs to an induced connected unicyclic `J`
  with `d_J(x,C(J))>=eta(G)`.
* For each ambient `eta`-realizer `x`, every inclusion-minimal induced
  connected cyclic `J` containing `x` and satisfying `eta(J)>=eta(G)` is
  unicyclic.

Neither audit found a failure.  These are finite observations, not proofs.
Fajtlowicz's theorem does not prove either statement because it controls only
ordinary radius and does not preserve a prescribed root or `eta`.  Establishing
one of the displayed center-distance assertions would be a new global
center-change theorem, not a consequence of radius-criticality.  That is the
first unsupported step, so no further rooted surrogate is opened.

## 4. Reproduction

Run

```text
python -m py_compile problems_external/wowii_144/attack_rooted_radius/verify_rooted_radius_counterexample.py
python problems_external/wowii_144/attack_rooted_radius/verify_rooted_radius_counterexample.py
python problems_external/wowii_144/attack_rooted_radius/probe_rooted_unicyclic_witness.py --max-n 11
python problems_external/wowii_144/attack_rooted_radius/probe_contained_root_minimality.py --max-n 11
```

The dedicated verifier reconstructs the graph from graph6, checks every
invariant, enumerates all rooted connected cyclic induced subgraphs, and
writes `rooted_radius_counterexample.json`.  Its SHA-256 is
`180d673ea7440345bb3652bbc3077ce93357d3f0b78158363c7bf17b0e632ce0`;
the JSON SHA-256 is
`09aedf23891f2e2d78012e8860201ef4a9ce1579429a5228be154b9e2cd14ddc`.
