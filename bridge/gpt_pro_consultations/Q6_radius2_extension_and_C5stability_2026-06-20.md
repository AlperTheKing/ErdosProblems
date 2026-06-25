# Q6 — TWO high-value questions for GPT Pro (ready to relay), 2026-06-20

Context: the a_7 proof (`Q5`) established, for {C3,C5}-free G on N vertices,
MaxCut(G) >= e/2 + (1/2N) Σ_u d(u)^2, hence β <= N^2/32. Step-2 extended the SAME
radius-2-ball method to ALL triangle-free graphs and VERIFIED it (below). Two
questions arise; QUESTION 1 could prove the whole Erdős #23, QUESTION 2 closes the
now-unlocked C5-stability route.

================================================================================
## QUESTION 1 (highest value — could prove Erdős #23 for ALL N, killing the need
## for H2/peeling/Step-1). Refine the radius-2 method to reach β <= N^2/25.

DEFINITIONS. G triangle-free, N vertices, e edges, β(G)=e-MaxCut(G). For each vertex
v: L1=N(v) (independent, since triangle-free), L2={dist-2 vertices}, e2(v)=#edges
inside L2. The radius-2 ball is H_v=G[{v}∪L1∪L2].

STEP-2's VERIFIED extension (exact, 0 counterexamples over ALL triangle-free graphs
N<=10): colour H_v by ({v}∪L2 | L1) — this cuts exactly S_v:=Σ_{u∈L1} d(u) edges
(all edges incident to L1) and leaves the e2(v) intra-L2 edges monochromatic; then
2-colour everything at distance >=3 uniformly at random. Each outside edge crosses
w.p. 1/2, so
        MaxCut(G) >= e/2 + S_v/2 − e2(v)/2     (for every v),
and averaging over v (using Σ_v S_v = Σ_u d(u)^2):
        β(G) <= e/2 − (1/2N) Σ_u d(u)^2 + (1/2N) Σ_v e2(v).
Here Σ_v e2(v) = Σ_{edges xy} #{v : dist(v,x)=dist(v,y)=2} is a C5-structure term
(each such (v,xy) yields a 5-cycle v-a-x-y-b-v with a∈N(v)∩N(x), b∈N(v)∩N(y), a≠b;
a=b would give a triangle). In the C5-free case e2(v)=0 and we recover β<=N^2/32.

THE OBSTRUCTION (Step-2 computed): the displayed bound is VALID but NOT always
<=N^2/25 — it holds for 11787/12172 triangle-free 10-vertex graphs but OVERSHOOTS on
~3% (worst: e=15, β=3, yet RHS=6 > N^2/25=4). The looseness has two sources: (i) we
used the fixed colouring (leaving ALL L2-edges monochromatic) instead of MaxCut(H_v),
which could cut some L2-edges; (ii) e2(v) is over-counted across different v.

ASK: (a) Replace S_v/2 − e2(v)/2 by a tighter per-vertex bound using MaxCut(H_v)
(H_v is triangle-free; can one cut S_v edges AND ≥ half the e2(v) L2-edges, i.e.
MaxCut(H_v) >= S_v + e2(v)/2 − loss?). (b) Bound Σ_v e2(v) exactly via the C5-count /
codegrees and combine with Σd(u)^2 (Cauchy-Schwarz or a weighted average over v) to
prove β(G) <= N^2/25 for ALL triangle-free G. (c) CRITICAL CHECK: the refined bound
must be EXACTLY tight at C5[n] (β=n^2=N^2/25, which is C5-saturated) — verify the
C5-correction exactly accounts for the gap 1/32 → 1/25 there. (d) If 1/25 is
unreachable, what exact finite constant does the refined method give (improving on
BCL's asymptotic 1/23.5)? A finite β<=cN^2 with c<1/23.5, valid for ALL N, would
already be new.

================================================================================
## QUESTION 2 (closes the C5-stability route given a(30)=36 + induction). 

FACTS NOW PROVEN (Step-2): (i) a_7(5n)<n^2, so any triangle-free G on 5n vertices
with β(G)>=n^2 contains an INDUCED C5 (Q5/A7). (ii) MERGE-PRESERVES-BETA: a codeg-0
nonedge uv with some max cut placing u,v together can be contracted (identify u,v→w,
N(w)=N(u)⊔N(v)) preserving β exactly. (iii) STRICT-FLIP: a frozen same-side codeg-0
pair has 2m(u)<c(u) in every max cut. (iv) MC3: a 2-DOMINATING induced C5 forces
β<=n^2. (v) C5HOM: hom-to-C5 ⟹ β<=n^2. GOAL: prove no triangle-free G on 5n vertices
has β>=n^2+1 (equivalently the frozen-pair MC4).

ASK: Given the guaranteed induced C5 in a β>=n^2 graph, derive β<=n^2. Concretely:
(a) Can the induced C5 always be taken (or grown) to be 2-DOMINATING (every vertex
has a neighbour in it), so MC3 applies? (b) If not, use MERGE: does a β=n^2
triangle-free graph admit a codeg-0 frozen pair whose merge stays triangle-free,
giving an induction to a(5n-1)? (c) Or a direct stability argument: β>=n^2 ⟹ G is
within bounded edit-distance of C5[n] (using that C5-free graphs are far, β<=25n^2/32),
then finite cleanup. Identify the cleanest closure.

================================================================================
## QUESTION 3 (quick confirmation). Does Wang-Yang-Zhao "arXiv:2408.05547" prove that
a triangle-free graph with minimum codegree > N/8 is homomorphic to C5, and is this
EXACT for all finite N or only asymptotic ("n large")? (Decisive for whether the
general-n low-codegree extraction lemma is usable.) Also: any FINITE-N codegree- or
minimum-degree-to-homomorphism threshold theorems for triangle-free graphs
(Andrásfai-Erdős-Sós line, Letzter-Snyder, Ebsen-Schacht)?
