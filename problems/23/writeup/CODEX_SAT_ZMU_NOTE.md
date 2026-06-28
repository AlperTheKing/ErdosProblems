# SAT-ZMU route to Schur condition (1)

This note records the current Codex/Claude state for the Schur condition (1)
subproblem. It is not a proof of the final conjecture.

## Definitions

For the gamma-minimum connected-B maximum cut:

- `B` is the cut-edge graph.
- `M` is the bad-edge set.
- `p_f(v)` is the shortest-B-geodesic incidence fraction for bad edge `f`.
- `K=PP^T`.
- `T(v)=sum_w K[v,w]`.
- `O={v:T(v)>N}`, `Q={v:T(v)<=N}`.

For a cut edge `e in B`, define its geodesic traffic

```text
mu(e) = sum_f sum_{P shortest geodesic for f, e consecutive in P}
        ell(f) / #(shortest geodesics for f).
```

The edge-load identity is

```text
sum_{e incident v} mu(e) = 2T(v)-E(v),
```

where `E(v)=sum_{bad f incident to v} ell(f)`.

## Candidate lemmas

The original candidate was:

```text
SAT-ZMU:
If O is nonempty and mu(e)=0 for a cut edge e=uv, then neither endpoint is
saturated.
```

This is now superseded. It is too strong unless one fixes a selected/tie-broken
Gamma-min cut. The current tie-invariant target is:

```text
SAT-ZMU-CONN:
If O is nonempty and a zero-mu B-edge uv has T(u)=N, then the positive-K
component of u intersects O.
```

There is also a weaker pooled inequality that still proves Schur condition (1):

```text
SAT-BOUNDARY-DEFICIT:
For every positive-K component C disjoint from O,

  deficit(C) = N*|C| - sum_{v in C} T(v)

is at least

  sat_boundary(C) =
  # {B-boundary edges xy : x in C, y outside C, and T(x)=N}.
```

This is weaker than the old full boundary-deficit conjecture
`deficit(C)>=dB(C)`, but it still excludes a critical Q-only component.

## Why SAT-ZMU-CONN or SAT-BOUNDARY-DEFICIT proves Schur condition (1)

Schur condition (1) reduces to excluding a critical K-component contained in
`Q` when `O` is nonempty.

Let `C` be a full K-component. If a B-edge crossing `C | V\C` had positive
geodesic traffic, then some shortest bad-edge support would intersect both
`C` and `V\C`, creating a positive K-edge across the full-component boundary.
Thus every B-boundary edge of a full K-component has `mu=0`.

If `C` is critical, then `T(v)=N` for every `v in C`. Since `B` is connected and
`O` is nonempty, a proper critical component has at least one B-boundary edge.
That edge is zero-mu and is incident to a saturated vertex. SAT-ZMU-CONN would
force the endpoint in `C` to lie in a positive-K component meeting `O`, but its
positive-K component is exactly `C`, contradiction.

Alternatively, SAT-BOUNDARY-DEFICIT gives

```text
0 = deficit(C) >= sat_boundary(C) >= 1,
```

again a contradiction. Hence no critical Q-only component exists, so
`N I - K_QQ` is a nonsingular Stieltjes M-matrix.

## Exact evidence

Claude exact-tested SAT-ZMU-CONN with 0 violations on:

- every Gamma-min connected-B maximum cut in the full census through N=11;
- the explicit N=12 leaf tie-caveat graph, all 11 Gamma-min cuts;
- selected loads cuts for named graphs, Mycielskians, blowups, and glued-island
  adversarial constructions.

SAT-ZMU-CONN is non-vacuous and tie-invariant. It survives the graph
`J?AADBWM_}?` plus leaf at vertex 8, where the stronger untied
SAT-ZMU-CLASS fails.

Claude also exact-tested SAT-BOUNDARY-DEFICIT with 0 violations on:

- glued island constructions (`C5/C7` islands against `Myc(C7)`,
  Grotzsch, and Myc(Grotzsch), up to `N<=24`);
- named graphs;
- Mycielskians;
- blowups including `J?AADBWeay?[2]`, `J???E?pNu?[2]`, `I?BD@g]Qo[2]`,
  and `G?bF\`w[3]`;
- census loads-cut `N=7..10`, with Codex independently checking full
  `N=11` selected loads cuts.

The old SAT-ZMU selected-tie evidence is still useful historically. The first
non-vacuous real-graph evidence occurred at N=11: three graphs contain both
saturated vertices and zero-mu edges, but the zero-mu edges do not touch the
saturated vertices.

Those N=11 witnesses are:

```text
J?AADBWeay?   sat={0}, O={10}, zero-mu={(2,7)}
J?ABBBWVCu?   sat={1}, O={10}, zero-mu={(2,7),(2,6)}
J?`D@_w{EB?   sat={0}, O={9},  zero-mu={(1,5)}
```

In each case the saturated vertex has strictly positive traffic on every
incident B-edge. The zero-mu edges instead attach to a load-free vertex.

Claude also verified the non-vacuous blow-up `J?AADBWeay?[2]` at `N=22`:
two saturated vertices and four zero-mu edges, with 0 SAT-ZMU violations.

Codex also tested small unequal blowups of those N=11 witnesses:

```text
224 unequal blowups, N<=15, 0 SAT-ZMU failures.
```

## Known false stronger claims

Full ZMU is false. In the glued construction

```text
C5 island + Myc(C7), bridge (0,5), N=20,
```

we have `O={19}`, `mu(0,5)=0`, and endpoint loads `T(0)=5`,
`T(5)=15/2`, both positive.

Two simple proof routes are also false:

- saturated vertices need not have singleton-CD equality;
- zero-mu edges need not be B-bridges.

Thus a proof of SAT-ZMU needs a genuinely geodesic or gamma-minimality argument.

## Handshake identity

For every vertex `v`,

```text
sum_{e incident to v, e in B} mu(e) = 2T(v) - D(v),
```

where

```text
D(v)=sum_{bad edge f incident to v} ell(f).
```

This is exact: a geodesic through an interior vertex uses two incident B-edges,
while a geodesic ending at `v` uses one.

For a saturated vertex this gives total incident traffic

```text
sum_{e incident v} mu(e) = 2N-D(v).
```

The identity does not prove SAT-ZMU by itself because a positive total does not
force every incident edge to have positive traffic.

## Tie-breaking caveat

SAT-ZMU-CLASS is not invariant over all equal-Gamma connected-B maximum cuts.
It may still be useful if the reduction permits an additional tie-breaker among
Gamma-min cuts, but the untied statement is false.

Counterexample to the untied version:

Start with `J?AADBWM_}?` on `N=11`, whose selected cut has a vertex `8` with
`T(8)=12=N+1` and another vertex `10` with `T(10)=25/2>N+1`. Add a new leaf
`11` adjacent to vertex `8`.

The extended side

```text
[1,0,1,1,1,0,1,0,0,0,0,1]
```

is a connected-B maximum cut with `Gamma=75`, equal to the `loads()` selected
Gamma for the extended graph. Under this equal-Gamma cut,

```text
T=[7,5,3,7,7,5,6,5,12,11/2,25/2,0],
O={10},
mu(8,11)=0,
T(8)=N=12,
T(11)=0.
```

Thus ZERO-SAT-ADJ and SAT-ZMU-CLASS fail for an allowed gamma-min cut. The
`loads()` helper chooses another equal-Gamma cut where the would-be saturated
vertex drops to load `10`, so all previous exact tests are tests of that
particular tie choice.

Open audit question: does the reduction allow us to choose a Gamma-min cut with
a secondary tie-breaker that enforces SAT-ZMU-CLASS, or must every Gamma-min cut
satisfy the intended Schur condition?

## Better tie-invariant target

The tie counterexample suggests a weaker statement that is exactly tailored to
condition (1) and survives all equal-Gamma cuts tested so far:

```text
SAT-ZMU-CONN:
If O is nonempty and a zero-mu B-edge uv has T(u)=N, then u lies in a positive-K
component that intersects O.
```

This directly proves condition (1). If `C` were a critical Q-only K-component,
then every B-boundary edge of `C` would have zero traffic and its endpoint in
`C` would have load `N`; SAT-ZMU-CONN would force that endpoint's K-component to
meet `O`, contradicting that `C` is a Q-only K-component.

Local all-Gamma-min exact check:

```text
N=7..10 census: failures=0 over all Gamma-min connected-B max cuts.
J?AADBWM_}?+leaf(8): failures=0 over 11 Gamma-min connected-B max cuts.
```

In the explicit `J?AADBWM_}?+leaf(8)` cut that refutes untied
SAT-ZMU-CLASS, the saturated endpoint `8` of the zero-mu edge `(8,11)` lies in
the large positive-K component containing the overloaded vertex `10`.

This makes SAT-ZMU-CONN preferable to SAT-ZMU-CLASS: it is not trying to forbid
all saturated zero-mu incidences, only those isolated from overload in K.

## Secondary tie-broken target

If SAT-ZMU-CONN is still too hard, an existential/tie-broken replacement remains
available:

```text
Among connected-B maximum cuts minimizing Gamma, choose one with the minimum
number of saturated zero-mu incidences. Then, if O is nonempty, this minimum is
0.
```

Local check:

```text
N=7..10 census: existential failures=0.
J?AADBWM_}?+leaf(8): 11 Gamma-min cuts; best has 0 violations, worst has 1.
```

The proof target is now a tie-switch lemma:

```text
If a Gamma-min cut has O nonempty and a saturated zero-mu incidence, then there
is another connected-B maximum cut with the same Gamma and fewer such incidences.
```

## Current proof targets

Primary:

```text
SAT-ZMU-CONN:
mu(uv)=0, T(u)=N, and O nonempty imply Kcomp(u) intersects O.
```

New stronger route to the C-alltie half:

```text
ZCOMP-BOUNDARY-O:
Let Z be a connected component of the cut graph B induced by the zero-load
vertices {v:T(v)=0}. If O is nonempty and Z has a positive-load B-boundary
vertex, then every positive-load B-boundary vertex of Z lies in a single
positive-K component, and that component intersects O.
```

This implies C-alltie immediately: if `T(z)=0`, `zv in B`, `T(v)=N`, and
`O` is nonempty, then `v` is a positive-load boundary vertex of the zero-load
B-component containing `z`, so `Kcomp(v)` intersects `O`.

Exact evidence:

```text
Codex selected loads() census N=7..11:
  O-nonempty zero-load B-components with positive boundary = 115,
  violations = 0.
  O-empty cases include 22 multi-K-boundary examples, so the O hypothesis is
  substantive.

Codex all-tie smoke:
  N=12 leaf tie-caveat: 10 cases, 0 violations.
  all gamma-min cuts N=7..10: 140 cases, 0 violations.

Claude broad gate:
  all gamma-min cuts N=7..10 + N=12 leaf caveat + Myc(Grotzsch) N=23:
  0 violations.
```

Claude also caught and corrected a useful bug in his first N=11 run: if the
`O nonempty` premise is removed, the single-boundary-component conclusion is
false. Explicit O-empty witness:

```text
g6 = J?AAD@OJ?s?
side = [1,1,1,1,1,0,0,0,0,0,0]
T = [5,5,5,5,0,5,5,5,5,5,5]
M = [(5,9),(6,10)]
Z = {4}
positive B-boundary of Z = {9,10}
9 and 10 lie in two different positive-K components.
```

Thus the overload hypothesis is essential. Dead zero-load connectors can bridge
two separate live K-components in capacity-subcritical/O-empty configurations;
`ZCOMP-BOUNDARY-O` says exactly that this bridge pattern is incompatible with
the existence of overload elsewhere.

Further structural handle:

```text
MULTI-ZCOMP-EXTREMAL:
If a zero-load B-component Z has positive boundary meeting at least two
distinct positive-K components C_1,...,C_m, then every touched component is
internally extremal:
    T(v)=|C_j| for all v in C_j.
```

Codex selected loads() census:

```text
N=7..10: no multi-boundary zero-load components.
N=11: 22 multi-boundary zero-load components; 0 violations.
All-tie smoke N=7..10 and N=12 leaf caveat: no multi-boundary cases.
```

Claude exact gate:

```text
MULTI-ZCOMP-EXTREMAL: 0 violations.
N=12 leaf caveat, all gamma-min cuts: 0.
O-empty witness J?AAD@OJ?s?: 0; both touched islands have T=5=|C|.
N=7..10 all gamma-min cuts: 0.
```

This explains the explicit O-empty witness above: the two bridged live
components are internally C5-like islands with load equal to their own size.
It does not by itself prove `ZCOMP-BOUNDARY-O`, because an overload component
could a priori coexist elsewhere; the missing step is to show that a
multi-boundary internally-extremal dead bridge cannot coexist with any overload
under gamma-minimality.

Do not overgeneralize this to arbitrary cut edges between distinct positive-K
components. That broader direct-edge analogue is false locally; for example,
`J?AAD@WXCs?` has a B-edge `(0,10)` between two distinct positive-K components,
and the component containing `10` has size `6` but loads
`[5,5/2,5/2,5,5,5]`.

The likely proof target is therefore a zero-load corridor switching lemma:
a zero-load B-component whose positive boundary touches either multiple live
K-components or a live K-component disjoint from `O` can be used to alter an
equal-size maximum cut and reduce `Gamma`, contradicting the chosen
Gamma-minimal cut.

GPT-Pro proposed a concrete version of this as a zero-moat prefix switch:
take a shortest bad-geodesic prefix through a saturated boundary vertex, add a
connected zero-load moat containing the zero neighbor, and seek a switch
`S` with `Delta_beta(S)=0`, connected switched `B`, and smaller `Gamma`.

Codex implemented:

```text
problems/23/writeup/_codex_zero_moat_prefix.py
```

The first exact scan used all connected maximum cuts, not only gamma-min cuts,
so the test would not be vacuous merely because C-alltie is already known on
gamma-min cuts. Result:

```text
N=7..11 full census, all connected maximum cuts:
counterconfiguration premises = 0.
named overloaded graphs: premises = 0.
```

Thus the prefix-switch certificate has not yet been exercised. The stronger
candidate now waiting on Claude's gate is:

```text
ALLMAX-ZERO-SAT-CONN:
For every connected maximum cut, if O is nonempty, T(z)=0, zv in B,
and T(v)=N, then Kcomp(v) intersects O.
```

If true, the proof of C-alltie may not need gamma-minimality. If false, the
first counterexample is the right place to test the zero-moat prefix-switch
certificate.

An even stronger candidate emerged from the same scan:

```text
O-K-SUPPORT:
If O is nonempty, every positive-K component intersects O.
```

Equivalently, overload anywhere forces all positive geodesic-support
components to be attached to overload. This implies C-alltie immediately.

Local exact checks:

```text
loads() selected cuts, full census N=7..11:
  Ographs = 824, components disjoint from O = 0.

all gamma-min connected-B maxcut ties, census N=7..10:
  gamma_min_cuts_with_O = 555, components disjoint from O = 0.

N=12 leaf tie-caveat, all 11 gamma-min cuts: 0 failures.
Grotzsch selected cut: 0 failures.
Myc(Grotzsch) selected cut: 0 failures.
```

This is now waiting on Claude's broader exact gate. A proof of O-K-SUPPORT
would subsume the zero-moat part of the cond(1) proof. If it fails, the witness
should show exactly how an underloaded/extremal K-island can coexist with an
overload component, and then the weaker zero-moat or boundary-deficit lemmas
remain the fallback.

False strengthening: all-maxcut connectedness evidence:

```text
O-K-CONNECTED:
If O is nonempty, the positive K-support has exactly one component.

all connected maximum cuts, full census:
  N=8:  O-cuts=27,   component-counts={1:27}
  N=9:  O-cuts=356,  component-counts={1:356}
  N=10: O-cuts=290,  component-counts={1:290}
  N=11: O-cuts=9800, component-counts={1:9800}
```

The N=11 all-maxcut check is implemented in:

```text
problems/23/writeup/_codex_ok_connected_allmax.py
```

This finite-gate strengthening is false globally. It is killed by a scalable
C5-bouquet construction:

```text
Take m copies of C5 sharing one common vertex 0:
  0-a_k-b_k-c_k-d_k-0.
Add one disjoint C5:
  e0-e1-e2-e3-e4-e0.
Add one bridge d_1-e0.

Use the cut side pattern:
  side(0)=1,
  side(a_k,b_k,c_k,d_k)=(0,1,0,0),
  side(e0,e1,e2,e3,e4)=(1,0,1,0,0).
```

The cut is maximum because each odd cycle forces at least one bad edge, and the
displayed cut has exactly one bad edge per C5 and cuts the bridge. It is also
gamma-min among maximum cuts because every bad edge has length 5.

For `m=7`, `N=34`, the shared vertex has load `T(0)=35>N`, so `O` is
nonempty. But the separate C5 is a positive K-component disjoint from `O`.
Thus `O-K-SUPPORT` and `O-K-CONNECTED` are false globally.

This does not contradict condition (1), because the disjoint C5 component is
low-load, not critical. The proof target must distinguish critical/Q-dangerous
components from harmless positive islands.

False scale-invariant route to O-K-CONNECTED:

```text
DISCONNECTED-K-SELFCAP:
If the positive K-support has at least two components, then every positive
K-component C satisfies T(v) <= |C| for all v in C.
```

This would have implied O-K-CONNECTED, but it is also false in the same
C5-bouquet construction: for `m=2`, the bouquet component has size `9` and
central load `10`; for `m=7`, the bouquet component has size `29` and central
load `35`.

Local exact checks:

```text
loads() selected cuts, full census N=5..11:
  multi-positive-K selected graphs: N10=7, N11=72; violations=0.

all connected maximum cuts:
  N7..9: multi=0;
  N10: multi-positive-K cuts=87, violations=0;
  N11: multi-positive-K cuts=717, violations=0.

N=12 leaf caveat, all connected maxcuts: multi=0.
Grotzsch and Myc(Grotzsch) selected cuts: multi=0.
```

Implementation:

```text
problems/23/writeup/_codex_disconnected_selfcap_allmax.py
```

This is no longer a proof target. The fallback below is the correct level of
generality.

Fallback:

```text
SAT-BOUNDARY-DEFICIT:
for every positive-K component C disjoint from O,
sum_{v in C}(N-T(v)) >= sat_boundary(C).
```

Both are verified and both imply condition (1). The current task is proof, not
more enumeration.

The likely lever is gamma-minimality: a zero-mu edge is invisible to all current
shortest odd-cycle geodesics, while a saturated endpoint has no Schur slack.
For the pooled version, every saturated B-boundary edge of a K-component must be
paid by underload somewhere in that same component. The real missing step is a
switching/discharging argument that converts maxcut-plus-Gamma minimality into
that payment.

An equivalent strengthened phrasing suggested by the data:

```text
if T(v)=N and v is incident to a zero-mu B-edge, then O is empty.
```

This is false without the `O empty` conclusion: O-empty census examples do have
saturated vertices incident to zero-mu edges.

The sharper classification through the exact gate is:

```text
mu(uv)=0 and T(u)=N  =>  T(v)=0 and O is empty.
```

Codex observed 146 such incidences at `N=10` and 1 at `N=11`; Claude stressed
the same statement on the full gate, glued islands, named graphs, Mycielskians,
and blowups including `J?AADBWeay?[2]` and `J???E?pNu?[2]`, with 0
violations.

A first tempting strengthening is false: the load-free endpoint need not be a
B-leaf. In the `N=10` graph

```text
I??CF@wFo
```

there is a saturated zero-mu incidence `(7,0)` with `Bdeg(0)=2`. Here all
incident edges of the load-free endpoint have zero traffic, and the endpoint has
no bad-edge degree. This follows formally from `T=0`: if a vertex were an
endpoint of a bad edge, it would contribute positively to its own load; then the
traffic handshake forces every incident B-edge to have zero traffic.

The right picture is therefore a zero-load, zero-traffic B-subnetwork, not
necessarily a pendant vertex. Deleting that subnetwork is not directly stable:
for `I??CF@wFo`, deleting all `T=0` vertices changes the recomputed gamma-min
value from `50` to `25`. Thus the obstruction is genuinely about
gamma-minimality under max-cut constraints, not simple deletion.

## False route: single-bad-edge island

The tempting proof target for `DISCONNECTED-K-SELFCAP` was:

```text
ONE-BAD-EDGE-ISLAND:
If a connected maximum cut has disconnected positive K-support, then every
positive K-component contains geodesic support from exactly one bad edge.
```

This implies `DISCONNECTED-K-SELFCAP` immediately. If component `C` contains
only bad edge `f`, then for every `v in C`

```text
T(v) = ell(f) p_f(v) <= ell(f) <= |C|.
```

The last inequality holds because `C` contains every vertex of at least one
shortest `f`-geodesic, which has `ell(f)` vertices.

This is false outside the small census gate. A 14-vertex glued construction
gives a counterexample:

```text
G = (two C5 cycles sharing one vertex) + (one disjoint C5),
with one B-bridge between the two pieces.

Edges:
  0-1-2-3-4-0,
  0-5-6-7-8-0,
  9-10-11-12-13-9,
  bridge 4-9.
```

On the `loads()` cut, the bad edges are `(3,4)`, `(7,8)`, `(12,13)`.
The positive K-support has two components:

```text
C1={0,1,2,3,4,5,6,7,8}, bad edges {(3,4),(7,8)},
T on C1 = [10,5,5,5,5,5,5,5,5].

C2={9,10,11,12,13}, bad edge {(12,13)},
T on C2 = [5,5,5,5,5].
```

Thus `ONE-BAD-EDGE-ISLAND` is false, and the stronger
`DISCONNECTED-K-SELFCAP` (`T(v)<=|C|`) is also false: `10>|C1|=9`.
This does **not** contradict `O-K-CONNECTED`, because here `N=14` and
`O` is empty (`max T=10<N`).

The earlier local exact checks, before this counterexample, were:

```text
loads() selected cuts:
  N5..N10: selected multi-positive-K cuts=7 by N10, first_bad=None.
  A previous serial selected N<=11 diagnostic saw multi=79, max
  badedges/component=1, first count>1=None.

all connected maximum cuts:
  N7..9: multi=0;
  N10: multi-positive-K cuts=87, first_bad=None;
  N11: multi-positive-K cuts=717, first_bad=None.

selected named/blowup stress:
  G?bF`w, G?bF`w[2], I?BD@g]Qo, I?BD@g]Qo[2],
  I?ABCc]}?, I?ABCc]}?[2], Grotzsch, Myc(Grotzsch):
  no bad; canonical J???E?pNu\? and J???E?pNu\?[2] have multi=0.
```

Implementation:

```text
problems/23/writeup/_codex_disconnected_onebad_allmax.py
```

If this lemma is true, the proof of the cond(1) side reduces to proving that
two distinct bad edges cannot live in the same positive K-component unless the
entire positive K-support is connected. Equivalently, once two bad geodesic
supports overlap through a shared vertex, the overlap graph should be able to
carry every positive geodesic-support island in that connected maximum cut.

## Rejected candidate: anchored surplus with overload coefficient 2

The zero-moat prefix-switch consult suggested an anchored surplus inequality.
The raw form

```text
T(v) + e_B(v,V0) <= N + sum_{x in Kcomp(v)} max(T(x)-N,0)
```

is false. On the N=12 leaf caveat, a gamma-min cut has a witness

```text
v=8, T(v)=12, e_B(v,V0)=1, overload(Kcomp(v))=1/2,
lhs=13, rhs=25/2.
```

The coefficient `3/2` version still fails on the same leaf. The coefficient
`2` version survived the smaller local gates in the saturation-gated form:

```text
AS2-gated:
if O is nonempty, T(v)=N, and e_B(v,V0)>0, then
T(v)+e_B(v,V0) <= N + 2 sum_{x in Kcomp(v)} max(T(x)-N,0).
```

This would have implied C-alltie immediately. If `Kcomp(v)` missed `O`, the
overload term would be zero, while `T(v)=N` and `e_B(v,V0)>0` would give
`N+1 <= N`.

Local exact checks:

```text
problems/23/writeup/_codex_anchored_surplus.py

AS2-gated, coefficient 2:
  glued battery loads: 24 cases, violations=0
  named/blowup selected cuts: violations=0
  N=12 leaf caveat, all gamma-min cuts: violations=0
  census loads N=7..11: violations=0
  all-gamma-min census N=7..10: violations=0
```

The saturation-gated coefficient-2 form is false on the full all-gamma N=11
gate. It fails on the same witness that kills `DIRECT-OVERLOAD-ZERO` and
`ZM-LEAK`:

```text
python _codex_hpzm.py --mode leak --all-gamma-parallel --nmin 11 --nmax 11 --workers 60

first: J?AAF@c{Ct?, side_index=4, v=10,
T(10)=11=N, zbd=1, O={0}, T(0)=34/3,
over(Kcomp(10))=1/3.
```

Thus

```text
T(10)+zbd(10)=12 > 11+2/3 = N+2*over(Kcomp(10)).
```

A broader O-gated all-vertex coefficient-2 inequality is false. At census
`N=11`, graph `J??ED?qEuw?` has

```text
v=10, T(v)=35/3, e_B(v,V0)=1,
overload(Kcomp(v))=2/3,
lhs=38/3, rhs=37/3.
```

So saturation `T(v)=N`, not merely `O` nonempty, is still load-bearing.

## Sharper live candidate: direct overloaded co-support

The coefficient-2 AS2 inequality appears to have a simpler qualitative core.

```text
DIRECT-ZERO-SAT-O:
If O is nonempty, T(v)=N, and v has a B-neighbour z with T(z)=0,
then v shares a shortest bad-edge geodesic with some o in O.
```

Equivalently, `K[v,o]>0` before taking transitive closure, not merely
`Kcomp(v)=Kcomp(o)`.

This immediately implies C-alltie, since direct co-support puts `o` in the
same K-component as `v`.

Local exact checks:

```text
tester: problems/23/writeup/_codex_direct_zero_sat_o.py

glued battery loads: violations=0
named/blowup selected cuts: violations=0
N=12 leaf caveat, all gamma-min cuts: violations=0
census loads N=7..11: violations=0
all-gamma-min census N=7..10: violations=0
all-gamma-min census N=11: gamma_min_sides=171182, violations=0
all connected maxcuts census N=7..10: premise=0, violations=0
all connected maxcuts census N=11: connected_maxcuts=199191,
  premise=22, violations=0
```

The N=11 all-gamma premise set is small:

```text
premise records=22
zbd distribution={1: 22}
|O| distribution={1: 22}
|direct_O(v)| distribution={1: 22}
quantitative slack 2*direct_over-zbd:
  -1/3: 10, 1/3: 1, 1: 9, 5/2: 2
```

In the N=12 leaf tight AS2 case, the saturated zero-gate vertex `v=8` shares
shortest bad-edge geodesics directly with the overloaded vertex `o=10`.

On the all-gamma N=11 witness that refutes the quantitative overload and
leakage variants, the qualitative statement still holds: `v=10` is directly
co-supported with overloaded vertex `o=0`.

This is now the cleanest proof target for C-alltie. It should be attacked as a
gamma-minimality statement: a zero-load gate at a saturated vertex must be paid
by overload on a bad-geodesic support that actually passes through that vertex.

## Rejected candidate: direct overload pays zero ports

The qualitative direct co-support candidate appears to have a rational
strengthening:

```text
DIRECT-OVERLOAD-ZERO:
If O is nonempty, T(v)=N, and zbd(v):=e_B(v,V0)>0, then
2 * direct_over(v) >= zbd(v),
```

where

```text
direct_over(v) =
  sum_{o in O, o shares a shortest bad-edge geodesic with v} (T(o)-N).
```

This implies `DIRECT-ZERO-SAT-O`: if `zbd(v)>0`, then `direct_over(v)>0`, so
some overloaded vertex shares a shortest bad-edge geodesic with `v`.

Exact tester:

```text
problems/23/writeup/_codex_direct_overload.py
```

Local exact checks:

```text
N=12 leaf caveat, all gamma-min cuts:
  violations=0
  four records have v=8, zbd=1, direct_over=1/2, slack=0

glued battery loads:
  cases=24, violations=0

named/blowup stress:
  Grotzsch, Myc(Grotzsch), Myc(C7),
  J?AADBWeay?[2], J???E?pNu\?[2], I?BD@g]Qo[2], G?bF`w[3]:
  violations=0

census loads N=7..11:
  violations=0

all-gamma census N=7..10:
  violations=0
```

This strengthening is false on the full all-gamma N=11 gate. Exact command:

```text
python _codex_direct_overload.py --all-gamma-parallel --nmin 11 --nmax 11 --workers 60
```

Result:

```text
gamma_min_sides=171182, violations=10.
first: J?AAF@c{Ct?, side_index=4, v=10,
T(10)=11=N, zbd=1, O={0}, T(0)=34/3,
direct_over=1/3, slack=2/3-1=-1/3.
```

The qualitative `DIRECT-ZERO-SAT-O` survives this witness because `v=10`
does directly share a shortest bad-edge geodesic with the overloaded vertex
`o=0`. Only the coefficient-2 direct-overload payment is false.

## Rejected candidate: half-port zero-moat prefix charge

GPT-Pro suggested an averaged zero-moat prefix charge of the form

```text
k(v) + sum_A lambda_A m_v(A) <= 2 over(Kcomp(v)),
```

where `k(v)=e_B(v,V0)`, `m_v(A)` is the minimum cut-loss
`Delta_beta(A union Z)` over zero-load moats containing all zero ports of `v`,
and the prefixes are weighted by `ell(f)/(2*N*|P_f|)`.

Under that direct interpretation the candidate is false on the N=12 leaf
caveat. Exact tester:

```text
problems/23/writeup/_codex_hpzm.py
python _codex_hpzm.py --n12-leaf --verbose
```

First violation:

```text
v=8, k=1, over(Kcomp(v))=1/2,
sum lambda_A m_v(A)=59/16,
lhs=75/16, rhs=1.
```

The four N=12 leaf gamma-min violations indicate that the averaged moat term
cannot enter with this sign/object. Any repaired prefix-switch charge must be
tested against this leaf before being sent to the full gate.

## Rejected candidate: zero-moat leakage charge

GPT-Pro's corrected version replaces the positive moated cut-loss by the
uncompensated leakage after subtracting the prefix-only cut-loss and the
forced zero-port saving:

```text
Leak_v(A) = max(0, m_v(A) - Delta_beta(A) + k(v)),
```

where

```text
k(v) = e_B(v,V0),
m_v(A) = min_{Z subset V0, N_B(v) cap V0 subset Z} Delta_beta(A union Z).
```

The repaired scalar was

```text
k(v) + sum_A lambda_A Leak_v(A) <= 2 over(Kcomp(v)).
```

This would imply AS2 and hence C-alltie. On the N=12 leaf, the old moated loss
is positive but all leakage terms vanish:

```text
v=8, k=1, over=1/2,
weighted_m=59/16, weighted_raw=75/16, weighted_leak=0,
lhs=1, rhs=1.
```

Exact tester:

```text
problems/23/writeup/_codex_hpzm.py --mode leak
```

Local exact checks:

```text
N=12 leaf caveat, all gamma-min cuts: violations=0
glued battery loads: violations=0
named/blowup stress: violations=0
census loads N=7..11: violations=0
all-gamma census N=7..10: violations=0
```

The repaired leakage charge is false on the full all-gamma N=11 gate. Exact
command:

```text
python _codex_hpzm.py --mode leak --all-gamma-parallel --nmin 11 --nmax 11 --workers 60
```

Result:

```text
all_gamma_parallel mode=leak N=11 graphs=90842
gamma_min_sides=171182 violations=10.
first: J?AAF@c{Ct?, side_index=4, v=10,
k=1, over=1/3, weighted_leak=0,
lhs=1, rhs=2/3, slack=-1/3.
```

## Rejected candidate: O-hit-or-descend single-port rotation

GPT-Pro next suggested a binary alternative: for every saturated zero-port
vertex `v`, find a shortest-geodesic prefix `A` and connected zero moat `Z`
through one zero port such that

```text
pdef_v(A,Z)=0,
Delta_beta(A)=e_B(v,Z),
B^(A union Z) is connected,
and either the chosen geodesic meets O or Gamma drops.
```

Exact tester:

```text
problems/23/writeup/_codex_ohit_descend.py
python _codex_ohit_descend.py --n12-leaf --stress --verbose
```

Result:

```text
N=12 leaf: premise=4, violations=3.
stress battery/named: premise=0, violations=0.
```

Failure mode on the N=12 leaf:

```text
v=8, zports=(11,), O=(10,), direct_O=(10,)
best candidates have pdef=0, but Delta_beta(A)-e_B(v,Z) is 1 or 2.
```

So the direct O-hit may exist while the additional cut-tight prefix condition
fails. The qualitative `DIRECT-ZERO-SAT-O` remains live; this particular
binary switch certificate is too strong.

## Tested status: zero-moat prefix-switch certificate

GPT-Pro proposed a sharper certificate:

```text
If O is nonempty, T(z)=0, zv is a cut edge, T(v)=N, and the positive
K-component C(v) is disjoint from O, then some switch
S = prefix_through(v) union Z
```

with `Z` a connected zero-load moat containing `z` should satisfy

```text
Delta_beta(S)=0,
B^S connected,
Gamma^S < Gamma.
```

Exact testers:

```text
problems/23/writeup/_zeromoat.py
problems/23/writeup/_codex_zero_moat_prefix.py
```

The older `_zeromoat.py` uses the full zero-load B-component as the moat. The
newer `_codex_zero_moat_prefix.py` enumerates all connected zero-load submoats
inside the zero B-component and scans all connected maxcuts.

Runs:

```text
python problems/23/writeup/_zeromoat.py
python problems/23/writeup/_codex_zero_moat_prefix.py --nmin 7 --nmax 9 --workers 60
python problems/23/writeup/_codex_zero_moat_prefix.py --nmin 10 --nmax 10 --workers 60
python problems/23/writeup/_codex_zero_moat_prefix.py --nmin 11 --nmax 11 --workers 60
```

Results:

```text
N=7..11 all connected maxcuts: premises=0, certs=0, missing=0.
glued battery all connected maxcuts: cases=24, premises=0, certs=0, missing=0.
```

The N=12 leaf caveat has four saturated zero-gate records, but in all four the
K-component of the saturated vertex already meets O:

```text
N=12 leaf: sat-z configs=4, C-meets-O=4, C-disjoint-O=0.
```

So the zero-moat prefix-switch lemma is not refuted by the current exact gate,
but the exact premise is vacuous on the tested census and glued batteries. It is
not yet a load-bearing closure route unless a nonvacuous premise instance is
found or the proof shows directly that the premise cannot occur.
