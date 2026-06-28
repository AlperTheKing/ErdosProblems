# Focused GPT-Pro consult: constant-load K-component bridge for GCD cond1

We are proving the remaining delta=0 step of Erdos Problem #23. Please do not suggest broad computation; I need one concrete proof lemma or a counter-proof mechanism.

## Definitions
Fix a gamma-min connected-B maximum cut of a triangle-free graph G on N vertices.
- B = cut edges, connected bipartite graph.
- M = bad edges (monochromatic).
- For bad edge f=(a,b), P_f is the set of shortest B-geodesics from a to b, ell(f)=dist_B(a,b)+1 odd >=5.
- p_f(v)=Pr_{P in P_f}[v in P].
- T(v)=sum_f ell(f) p_f(v).
- K=PP^T, so K-components are components of the positive shortest-geodesic traffic hypergraph: vertices are connected if they occur together on some shortest bad-edge geodesic support.
- Equivalently, omega-components for the GCD route, since positive omega edges match positive mu traffic.

The GCD route proves the theorem if we prove H=L_omega+diag(N-T) >= 0. Schur cond1 reduces to ruling out a proper omega/K component C with
  T(v)=N for all v in C
  and no omega-boundary to overloaded vertices O={T>N}.

## New candidate lemma
CONSTANT-LOAD-SELFCAP:
If C is a proper positive K/omega component and T is constant on C, say T(v)=lambda for all v in C, then
  lambda <= |C|.

This directly kills a dangerous cond1 component, because lambda=N and |C|<N.

Stronger bridge that would imply it:
CONSTANT-LOAD-COMPONENT-BRIDGE:
If C is a proper positive K/omega component and T is constant on C, then the global cut restricted to G[C] is a full gamma-min connected maximum cut of G[C]. Then induction gives Gamma_C <= |C|^2, while Gamma_C=sum_{v in C}T(v)=lambda|C|.

## Exact evidence
Both statements survived exact scans:
- census N=7..11, all connected triangle-free graphs. N=11: 90842 graphs, 15205 constant-load proper components, 0 violations for both selfcap and bridge.
- glued-island battery that killed broader false statements: 0 violations.
- named/blow-up spot checks: 0 violations.

## Important false routes to avoid
- General component selfcap T(v)<=|C| is false on glued islands. The constant-load hypothesis is essential.
- O-K-SUPPORT (every positive K component meets O) is false on glued islands.
- Zero-mu edge sum T(u)+T(v)<=N is false; do not use EDGE-SHADOW-CAP.
- Pure subset/Hall/maxflow and finite-depth Neumann proxies are too weak/false.

## Structural facts that are true/provable
For a K/omega component C:
1. No bad edge has exactly one endpoint in C. Otherwise its shortest geodesic support connects across C.
2. Any B-boundary edge between C and V\C has zero shortest-geodesic traffic mu=0. Otherwise a positive-traffic geodesic using that edge connects across C.
So the boundary of C consists of geodesically idle B-edges.

The remaining gap:
Global maxcut alone does not force the restricted cut on C to be a maxcut of G[C], because an internal cut improvement may be paid for by losing boundary B-edges. The hope is that gamma-minimality plus constant load forbids this subsidy, or directly implies lambda<=|C|.

## What I need
Give a rigorous proof route for CONSTANT-LOAD-SELFCAP or the stronger bridge. Be precise: define the switch/recoloring or energy comparison, and show where constant T on C is used. If you think the bridge is too strong, propose the weakest exact lemma that still proves lambda<=|C|. Avoid computational suggestions unless they identify a falsifiable intermediate inequality.
