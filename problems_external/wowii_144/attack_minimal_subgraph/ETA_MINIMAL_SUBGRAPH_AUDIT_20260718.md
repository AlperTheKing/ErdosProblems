# W144-MIN eta-minimal induced-subgraph audit

Date: 2026-07-18.

## Status

This route is **not a proof of W144**.  The exact characterization below has
no counterexample in the complete girth-at-least-five corpus through order 13,
but the global block/ear implication needed to prove it is unsupported.  This
note stops at that implication and opens no weaker witness hierarchy.

## 1. Exact direct route

For a finite connected graph `X`, put

```text
C(X)   = {vertices of minimum eccentricity},
eta(X) = max_x d_X(x,C(X)),
beta(X)= |E(X)|-|V(X)|+1.
```

Given a connected cyclic `G`, choose an induced connected cyclic subgraph `H`
of minimum order subject to

```text
eta(H) >= eta(G).                                             (MIN)
```

The required characterization is

```text
girth(G)>=5 and H satisfies (MIN) minimally  ==>  beta(H)=1. (C)
```

The bridge to W144 is exact.  Induced subgraphs cannot have smaller girth, so
`girth(H)>=girth(G)`.  If (C) holds, the proved unicyclic theorem supplies an
induced tree in `H`, hence in `G`, of order at least

```text
girth(H)-1+eta(H) >= girth(G)-1+eta(G).
```

Thus (C) would prove precisely W144, without a girth or eta loss.

A minimum `H` is cyclic eta-critical: every proper induced connected cyclic
subgraph `J` of `H` has `eta(J)<eta(H)`.  Indeed it has `eta(J)<eta(G)`, while
`eta(H)>=eta(G)`.  Consequently, if `H` were multicyclic, every vertex `v`
for which `H-v` stays connected and cyclic would satisfy
`eta(H-v)<eta(H)`.

## 2. Exact finite certificate

`verify_eta_minimal_audit.py` generates graphs using `geng -ctfq`, recomputes
girth, cycle rank, every vertex eccentricity, the full center set, and eta,
and tests the stronger one-step statement

```text
beta(G)>=2 and girth(G)>=5
  ==> exists v, G-v connected cyclic and eta(G-v)>=eta(G).     (S)
```

Statement (S) implies (C) on the same corpus: apply (S) to a hypothetical
multicyclic minimum `H`; then `H-v` is a smaller feasible subgraph.

The complete run for orders 5 through 13 returned:

```text
order       5  6  7   8    9    10    11     12      13
checked     0  0  1   7   38   202  1,087  6,192  38,066
tight       0  0  1   3   23    95    435  2,242  12,709
```

In total, 45,593 multicyclic graphs were checked, the minimum over graphs of
the best deletion delta was zero, and there was no failure.  The exact result
file records

```text
corpus SHA-256:
be3f60c8462e440da7a159a21b2047a0db4471347ce13aa57c8836117e664fc8

canonical first-witness SHA-256:
b0f332424c866136a118964dc68869b30b40fb27e9db36d271b5a10ba389d573
```

The second hash covers, in generator order, the graph6 code, first
eta-nondecreasing deletion vertex, old girth and eta, and new girth and eta.
The verifier itself has SHA-256
`20e2d6fc4cf9b4e87a10ff58b7c83a9e097bdaa300733294d64c0b368ec96c43`.

A supplementary seeded search tested 2,000 subdivided multicyclic cores with
attached trees (`seed=14420260718`), all of girth at least six.  It found no
failure of (S); the minimum best eta change was zero and 272 instances were
tight.  A separate exact theta-family check covered all 320
`Theta(a,b,c)` with `1<=a<=b<=c<=12` and girth at least five, again with no
failure.  These additional runs are falsification evidence, not a proof.

## 3. The same-girth assertion is not the route

The older `probe_eta_critical_structure.py` asserts the strictly stronger
selection rule that the deletion preserve the old girth.  Its first assertion
failure is the already known graph

```text
K??CA?_sDOEg
```

with `n=12`, `girth=5`, `eta=3`, and center `{2,10}`.  Its same-girth
admissible deletions `v=4,5,6,8` all have eta 2.  This does not falsify (S) or
(C): deleting `v=3` gives `(girth,eta)=(7,3)`, and deleting `v=7` gives
`(6,3)`.  Girth is allowed to rise, and this rise is automatically favorable
in the final W144 bridge.

## 4. Exact center-expansion consequence

Let `X` be cyclic eta-critical, let `Y=X-v` remain connected and cyclic, and
write `e=eta(X)`, `e'=eta(Y)`, `r=rad(X)`, and `r'=rad(Y)`.  Suppose `e'<e`.
For every eta-realizer `x!=v`, there is a vertex `u in C(Y)-C(X)` with

```text
d_X(x,u) <= d_Y(x,u) <= e' < e.                         (4.1)
```

Indeed a closest new center to `x` satisfies the two distance inequalities;
it cannot be an old center because `d_X(x,C(X))=e`.

If also `r'<=r`, then every `u in C(Y)-C(X)` satisfies

```text
r'=r,  ecc_X(u)=r+1,  and v is the unique eccentric vertex of u. (4.2)
```

For `y!=v`, `d_X(u,y)<=d_Y(u,y)<=r'<=r`.  Since `u` is not central in `X`,
only `v` can give eccentricity above `r`.  If `w` precedes `v` on a shortest
`u-v` path, then

```text
d_X(u,v)-1=d_X(u,w)<=d_Y(u,w)<=r'<=r,
```

forcing all equalities in (4.2).  Hence for distinct such deleted vertices
`v,w`, the genuinely new center sets are disjoint:

```text
(C(X-v)-C(X)) intersection (C(X-w)-C(X)) = empty.
```

This is a proved necessary condition, not the missing contradiction.

## 5. Why the block/ear step does not presently close

A proof of (C) would have to show that a multicyclic girth-at-least-five graph
cannot support all the center changes in Section 4.  The following exact
records rule out the obvious local selections.

1. **An exterior or girth-preserving deletion need not work.**  The graph
   `K??CA?_sDOEg` above has only bad eta deletions among the vertices whose
   deletion preserves its chosen shortest cycle.  A successful deletion must
   hit that cycle and increase girth.
2. **A degree-two ear vertex need not work.**  In ``I?`acgwg_`` (`n=10`,
   `girth=5`, `beta=5`, `eta=2`), both degree-two deletions lower eta to 1;
   all eta-preserving deletions have degree three.
3. **Deleting an old peripheral vertex need not work.**  In
   ``I??ED`KI_`` (`n=10`, `girth=5`, `eta=3`, center `{6,9}`), the admissible
   vertices `3` and `5` eccentric to an old center both lower eta to 2.
   Eta is preserved instead by core vertices `0,1,2,4`.
4. **Radius monotonicity does not cover every deletion.**  The proved
   unique-eccentric-point description (4.2) applies when `r'<=r`, but exact
   bad deletions also occur with `r'>r`.  Therefore a Fajtlowicz
   radius-critical argument cannot simply be applied to every bad deletion.

The first unsupported implication is therefore the following exact global
statement:

> In a cyclic eta-critical graph of girth at least five, the pairwise-disjoint
> unique-eccentric-point witnesses from all radius-nonincreasing admissible
> deletions, together with the unrestricted center shifts from the remaining
> radius-increasing deletions, force cycle rank one.

No block decomposition or ear argument proving this statement is currently
available.  The examples above show that neither the noncentral-block side nor
the two-connected ear side can be discarded or handled by a fixed local
vertex class.  Asserting the displayed implication would simply assert the
load-bearing characterization (C), so this audit stops here.

## 6. Reproduction

From the repository root:

```text
python -m py_compile problems_external/wowii_144/attack_minimal_subgraph/verify_eta_minimal_audit.py
python problems_external/wowii_144/attack_minimal_subgraph/verify_eta_minimal_audit.py --min-n 5 --max-n 13
```

The machine-readable result is `eta_minimal_audit_results.json` in the same
directory.  Exit code zero means no counterexample was found; on a failure the
file includes graph6, edges, center, eta, and every admissible deletion row.

