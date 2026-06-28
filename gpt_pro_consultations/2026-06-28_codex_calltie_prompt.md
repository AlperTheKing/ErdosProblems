We are working on Erdős Problem #23 in a graphon/blow-up proof pipeline. Please do not propose finite SAT/census enumeration; the finite certificate is already done. I need one concrete proof idea for the isolated lemma below.

Setting:

Let G be triangle-free on N vertices. Fix a maximum cut whose cut-edge graph B is connected, and among those cuts minimize

    Gamma = sum_{f in M} ell(f)^2,

where M is the set of same-side edges ("bad edges") and ell(f)=dist_B(a,b)+1 for f=ab in M.

For each bad edge f=ab, let P_f be the set of shortest B-geodesics from a to b, and define

    p_f(v) = (# shortest B-geodesics in P_f containing v) / |P_f|.

The load is

    T(v) = sum_{f in M} ell(f) p_f(v).

Define a positive-K graph on vertices with T>0 by putting v~w iff there is some bad edge f whose shortest-geodesic support contains both v and w. Let O={v:T(v)>N}.

For a B-edge e, define geodesic traffic

    mu(e)=sum_f sum_{P in P_f: e is consecutive in P} ell(f)/|P_f|.

So mu(e)=0 means no shortest odd-cycle geodesic uses e.

What is already proven/reduced:

Schur condition (1) for the spectral proof is equivalent to excluding a critical Q-only positive-K component: no positive-K component C disjoint from O may have T(v)=N for every v in C. If such a critical component existed, every B-boundary edge of C would have mu=0 and the endpoint inside C would have T=N.

Claude exact-verified the following split over every Gamma-min connected-B maximum cut in the full census N<=10, a full N=11 scan on Codex's side, the N=12 tie-caveat, blowups, Mycielskians, and glued adversarial constructions:

Lemma A-alltie:
    If uv is a B-edge with mu(uv)=0 and T(u)=N, then T(v)=0.

Lemma C-alltie:
    If O is nonempty, z is B-adjacent to v, T(z)=0, and T(v)=N, then the positive-K component of v intersects O.

A-alltie + C-alltie imply the needed SAT-ZMU-CONN lemma, hence Schur condition (1).

The target for this consult is C-alltie, which is mu-free:

    In a connected-B maximum cut minimizing Gamma, if O is nonempty and a B-edge zv has T(z)=0 and T(v)=N, then v is positive-K-connected to some overloaded vertex o in O.

Equivalent contradiction form:

    Suppose O is nonempty, T(z)=0, T(v)=N, zv in B, and the positive-K component C of v is disjoint from O. Derive a contradiction to maxcut+Gamma-minimality.

Known facts/caveats:

- T(z)=0 means z is not on any shortest bad-edge geodesic and is not an endpoint of any bad edge. All bad-geodesic traffic through z is zero.
- The zero-load region need not be a leaf or deletable. In an O-empty N=10 example, the T=0 subnetwork has B-degree-2 vertices and deleting it changes the recomputed Gamma, so deletion is not stable.
- C-alltie is false if "positive-K component intersects O" is replaced by "O is empty" under arbitrary equal-Gamma cuts: a leaf tie-caveat has a zero-load leaf adjacent to a saturated vertex that is nevertheless K-connected to O.
- The likely mechanism is gamma-minimality/maxcut forcing, not local counting.

Useful identity:

    sum_{B-edges e incident to x} mu(e) = 2*T(x) - D(x),

where D(x)=sum_{bad edges f incident to x} ell(f). This may help A-alltie, but C-alltie should ideally avoid mu.

Request:

Give one concrete route to prove C-alltie. I want a lemma with a proof skeleton that uses gamma-minimality of the maximum cut. For example, a switching/coarea argument: flip or slide a zero-load B-subnetwork adjacent to a saturated Q-only K-component, preserve maxcut size, and strictly reduce Gamma unless that component is K-connected to O.

Please state any proposed intermediate inequality or switching operation explicitly enough that we can exact-test it on the census. Avoid broad surveys, finite checking, generic nonnegative-matrix arguments, and the already-false deletion/pedant claims.
