# W144 ciliate endpoints: final direct audit

**Status.** This is not a proof of Conjecture 144 and it does not give a
counterexample to the conjecture.  It kills the ciliate endpoints as a
strictly smaller local augmentation route.  Two precise endpoint lemmas are
false, and after they are removed the exact remaining implication is the full
multi-component Lemma-M capacity assertion.

Throughout, `r=rad(G)`, `g=girth(G)`, `D=diam(G)`, `C=center(G)`,
`e=max_v d(v,C)`, and `tree(G)` is the largest order of an induced tree.
The cases `g<=4` are already closed.  The proved bound P2 is

    tree(G) >= D + ceil(g/2) - 1.

For a shortest cycle `K`, Lemma M says

    tree(G) >= g-1+M(K),

where `M(K)` is the largest order of an induced forest outside `K` whose
components, after one vertex `z` of `K` is deleted, each have exactly one edge
to `K-{z}`.

## 1. What Fajtlowicz's theorem actually supplies

Fajtlowicz's radius-critical theorem supplies an induced `r`-ciliate
`C(2t,r-t)`, `1<=t<=r`.  For `2<=t<=r-1`, deleting one cycle root and its
pendant path gives an induced tree of sufficient order; this is the closed
internal case.  The endpoints are

    t=1:  P_(2r),             t=r:  C_(2r).

The endpoint containment is only induced containment.  Distances within the
endpoint need not be ambient distances.  In particular an induced `P_(2r)`
need not be a geodesic, so its presence supplies no lower bound
`D>=2r-1` usable in P2.

## 2. The retain-the-path endpoint lemma is false

For every `r>=2`, let `L_r` be the odd cycle `C_(2r+1)` with one leaf `u`
attached at a cycle vertex `a`.  Exact parameters are

    (g,r,D,e) = (2r+1, r, r+1, 1).

The center consists of the cycle vertices at cycle distance at most `r-1`
from `a`, which proves `e=1`.  Delete `a` from the cycle and let `H` be the
remaining `2r` cycle vertices.  Then `G[H]=P_(2r)`, so `H` is precisely the
path endpoint ciliate.  Its endpoint distance inside `H` is `2r-1`, while
the ambient diameter is only `r+1`.

The target is `g-1+e=2r+1`.  Nevertheless no nonempty subset of
`V(L_r)-H={a,u}` can be appended while retaining all of `H`: adding `a`
closes the odd cycle, adding `u` leaves it isolated, and adding both leaves
the cycle.  Thus the exact lemma

> an induced endpoint `P_(2r)` can be enlarged, while retaining all of its
> vertices, to an induced tree meeting the W144 target

is false for every `r>=2`.  W144 itself holds here: delete a cycle vertex
other than `a` and keep `a,u`, obtaining an induced tree of order `2r+1`.
Equivalently, P2 is exact on this family:

    D+ceil(g/2)-1 = (r+1)+(r+1)-1 = 2r+1.

So an exchange, not monotone endpoint enlargement, is unavoidable.

## 3. One-component exchange is false for both endpoints

For `m>=1`, form `G_m` from `K=C_(10m)` by selecting roots `a,b` at cycle
distance `2m` and attaching a pendant path of `2m` edges at each root.  Direct
distance calculation gives

    g=10m,  r=5m,  D=7m,  e=3m.

For completeness, the central cycle vertices are the short `a`--`b` arc
together with the first `m` vertices from each root on the long arc.  The
complementary long-arc interval has length `6m`; its midpoint is at distance
`3m` from the center.  Pendant vertices are at distance at most `2m` from a
central root.  This proves `e=3m`; the same description gives radius `5m`,
and a pendant end to the antipodal cycle vertex gives diameter `7m`.

The graph contains both radius-`r` endpoint ciliates:

1. `K=C_(10m)=C_(2r)`.
2. Delete the cycle vertex immediately before `a` and append the first vertex
   of the pendant path at `a` to the remaining cycle path.  The resulting
   induced graph is `P_(10m)=P_(2r)`.

The exact W144 target is

    g-1+e = 13m-1,

whereas P2 supplies only

    D+ceil(g/2)-1 = 12m-1.

Thus this is a genuine P2-residual endpoint family, with deficit `m`.

For the cycle endpoint, deleting one cycle vertex leaves `10m-1` endpoint
vertices, and either outside component has only `2m` vertices.  Any exchange
using at most one outside component therefore has order at most
`12m-1<13m-1`.

For the path endpoint, the three components outside the displayed `P_(2r)`
have orders `1`, `2m-1`, and `2m`.  For `m>=2`, even retaining every endpoint
vertex and taking the largest one has order at most

    10m+2m = 12m < 13m-1.

Deleting endpoint vertices only lowers this cardinality bound.  Hence the
one-outside-component exchange lemma is false for both endpoint types.  The
unique `e`-realizer is the midpoint of the long cycle interval and lies in
both displayed endpoints, so restricting to the outside component of an
`e`-realizer contributes nothing and is false as well.

The conjecture again holds on `G_m`.  Delete a non-root cycle vertex and retain
both pendant paths.  The result is an induced tree of order `14m-1`.  In
Lemma-M language, take `F` to be the union of the two pendant paths.  It has
two components, each with exactly one edge to `K-{z}`, and

    |F|=4m >= e=3m.

This explicitly identifies the resource absent from both false endpoint
lemmas: compatible capacity distributed over several outside components.

## 4. Exact missing bridge and disposition

After P2, the residual case is `e>D-floor(g/2)`.  Sections 2--3 prove that an
endpoint proof cannot preserve a fixed endpoint and cannot use one outside
component or the component of an `e`-realizer.  The surviving statement is
exactly

> choose a shortest cycle `K`, a vertex `z in K`, and a compatible induced
> forest `F subseteq V(G)-V(K)` whose components each send exactly one edge
> into `K-{z}`, with `|F|>=e`.

This is `M(K)>=e`, the full residual admissible-forest lemma.  Fajtlowicz's
endpoint containment supplies no bound on the required sum of compatible
component capacities; `G_m` shows that no single summand can replace it, with
an unbounded deficit.  Consequently the endpoint route does not close an
independent augmentation lemma.  It returns verbatim to the existing global
capacity frontier and is **DEAD as a separate direct route**.  This does not
mark W144 or the global Lemma-M/Steiner routes dead.

## 5. Mechanical verification

`attack_ciliate_endpoints/verify_endpoint_families.py` checks all graph
parameters, induced-path/tree claims, outside-component orders, and Lemma-M
witnesses for

    L_r: r=2,...,30  (29 instances),
    G_m: m=1,...,30  (30 instances).

It compiles and returns

    {'L_r_instances': 29, 'G_m_instances': 30, 'failures': 0}.

The formulas above are symbolic in `r,m`; the bounded run is an independent
implementation check, not the justification for the infinite families.

Primary source for the ciliate theorem: S. Fajtlowicz, *A characterization of
radius-critical graphs*, Journal of Graph Theory 12 (1988), 529--532,
doi:10.1002/jgt.3190120409.
