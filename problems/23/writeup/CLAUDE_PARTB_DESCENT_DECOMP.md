# Part B (singleton Γ-descent): exact decomposition of the hub flip

**Status:** mechanism pinned exactly on the k-chord failure family (the ONLY family producing
interval-Hall failures — census N≤11 never fails). Gate: `_descent_decomp_gate.py`, 20/20 clean.

## Setup
G triangle-free; s a connected-B **maximum** cut; f a unique-geodesic bad edge with geodesic path
P=(x_0,…,x_{L−1}) (L = ℓ(f) vertices; the unique shortest alternating/cut-edge path between f's
endpoints). For a bad (monochromatic) edge e, ℓ_s(e) = bdist_restr(e)+1 = #vertices of the shortest
alternating path between its endpoints; Γ(s) = Σ_{bad e} ℓ_s(e)².

Interval-Hall failure at I=[a,b]: Σ_{i∈I}(S(x_i)−1) > cap(I). Max-load hub x* = x_{i*},
i* = argmax_{i∈I}(S(x_i)−1). Let s' = s with x* moved to the other side.

## EXACT decomposition (20/20 on k-chord k∈{3,4,6}, clen∈{4,5,6,7})
Write B0, B1 for the bad-edge sets of s, s'. At x*: exactly 2 cut-edges (the path edges
(x_{i*−1},x*),(x*,x_{i*+1})) and exactly 2 bad edges (P-contained "bracket" rows). The flip:

1. **Cut-tight.** cutsize(s')=cutsize(s); s' connected-B. (2 cut-edges→bad, 2 bad→cut.)
2. **INCIDENT-EXCHANGE is ℓ-multiset-neutral.** The 2 path-edges that become bad have the SAME
   multiset of ℓ-values as the 2 bracket bad-edges that become cut. (Not just Σℓ² equal — the
   multiset {ℓ} is equal.) Reason: flipping x* leaves the short odd cycles through x* unchanged as
   subgraphs; it only moves the monochromatic edge around each such cycle, preserving its ℓ.
   ⇒ contributes **0** to ΔΓ.
3. **Only f changes ℓ among retained bad edges.** Shortened-set == {f} exactly (20/20); 0 retained
   edges ever lengthen; every bad edge other than f keeps its ℓ. f's geodesic threaded x* via the
   now-broken alternation, so it reroutes through the chord/detour: ℓ_{s'}(f) < ℓ_s(f) strictly.
   Representative: f=(0,12), ℓ 13→7, ΔΓ = 7²−13² = −120.

**Net identity:** ΔΓ = Γ(s')−Γ(s) = ℓ_{s'}(f)² − ℓ_s(f)² < 0. Everything else cancels exactly.

So **Part B ⟺**: at a max-load hub of an interval-Hall failure, flipping x*
 (i) preserves cut size, (ii) preserves B-connectivity, (iii) strictly shortens f's geodesic,
 (iv) preserves the ℓ-multiset of all other bad edges.
Then ΔΓ<0 contradicts γ-minimality ⇒ on a γ-min cut no interval-Hall failure ⇒ UPO.

## UPDATE: shortcut direction now CONSTRUCTIVE (_straddle_shortcut_gate.py, 6/6)
The hub x* is the SHARED ENDPOINT of two straddling P-contained bad chords g1=(y,x*), g2=(x*,z) with
pos(y)<i*<pos(z) (k-chord: consecutive chords like (0,4),(4,8) sharing x*=4). Given that:
  CONSTRUCT  Q = P[0..pos(y)] + [x*] + P[pos(z)..end].
  After flipping x*: (y,x*),(x*,z) become CUT edges; Q is a valid ALTERNATING f-path (verified) with
  len(Q) = pos(y)+1 + (L-pos(z)) + 1 < L. Hence ℓ_{s'}(f) <= len(Q) < ℓ_s(f). STRICT shortening, PROVEN
  by explicit construction (not BFS). _shortcut_probe.py: f=(0,12) -> Q=[0,4,8,9,10,11,12] (13->7);
  f=(0,18) -> [0,6,12,...,18] (19->9).
So "chorded-straddle hub  =>  strict Γ-descent" is a PROVEN implication (S1&S3 => descent).

## THE SINGLE REMAINING OBLIGATION (Part B heart)
  (B*)  interval-Hall failure (demand(I)>cap(I))  =>  some vertex x* of P is the SHARED ENDPOINT of two
        straddling P-contained bad chords (g1=(y,x*), g2=(x*,z), pos(y)<pos(x*)<pos(z)), and x* is
        cut-tight (#incident cut-edges = #incident bad-edges).
Everything else is proven: (S1&S3)=>explicit shorter f-route=>ΔΓ=ℓ'(f)²-ℓ(f)²<0=>¬γ-min.
Note the shortcut needs chords INCIDENT to x* (sharing it as an endpoint), NOT merely passing through;
that incidence is the crux where odd-girth>=5 + the contained-overload (D_contained>=ℓ(f)-4>=1 via
Part A spare-unit) must force a degree->=2 straddle vertex in the P-contained chord graph.

## Older framing: three obligations (now folded into (B*))
- (B-i)  cut-tightness: x* has equal #cut-edges and #bad-edges incident (=2,2 on k-chord).
- (B-ii) incident-exchange ℓ-multiset neutrality (local odd-cycle relabel; odd-girth=5 gives the
  bracket-C5 ↔ path-C5 swap on clen=4; general clen gives Cℓ↔Cℓ).
- (B-iii) f's geodesic strictly shortens at the max-load hub: the interval-Hall OVERLOAD is exactly
  the existence of a shorter alternating f-route once x* is flipped. This is the heart; it ties the
  Hall deficit (demand>cap) to a concrete shortcut anchored at the argmax-load vertex.

## (B*) PROOF PATH via a clean max-cut lemma (validated)
The crux of (B*) reduces to a max-cut interval lemma:
  (M)  On a GLOBAL maximum connected-B cut, two P-contained bad chords never INTERIOR-overlap; they meet
       only at endpoints.  [_chord_overlap_maxness.py: 3434/3434 interior-overlaps occur ONLY on non-max
       cuts, 0 on global-max, census N<=9 all connected-B cuts.]
Given (M), (B*) follows:
  - overload demand(I)>cap(I) with span-coverage+capacity (cap absorbs ~1 unit/position) forces load >= 2
    at some position x_i (concentration);
  - load >= 2 at x_i means >= 2 P-contained chords cover x_i;
  - by (M) those two chords meet only at endpoints, so they share x_i as a COMMON ENDPOINT => x_i is a
    bracket junction (one chord ends at x_i from the left, one starts to the right).  QED (B*).
N=26 exact corroboration (_single_chord_maxcheck.py): single/disjoint chords on a global-max cut produce
NO interval-Hall overload at all; only the chaining (junction) layout overloads, and it has a junction.
So the remaining proof obligation collapses to (M) -- a pure max-cut switching statement (no demand/cap),
provable from the switching inequality + odd-girth>=5. This is the clean target for the (B*) proof.

## SEPARATE half: FAN-AVERAGING genuinely needed (multi-geo BINDS at N)
_rowsum_max_gate.py: max rowsum/N over gamma-min = 1.0000 EXACTLY for UNIQUE-path f (binding), and ALSO
1.0000 for MULTI-geodesic f (at N=10). rowsum never exceeds N (0 violations). So the multi-geodesic
(fan-averaging) half is NOT slack/soft -- it binds at N and needs its own argument: rowsum(f)=(1/k)sum_j
UPO_j <= N even though individual UPO_j can exceed N (36 cases at N=10). Genuine variance/Jensen over f's
geodesic fan. (Earlier "multi max 0.92N" was a max-absolute-vs-max-ratio reporting artifact -- corrected.)

## Caveat (honesty)
All 20 validated cases are k-chord. Census max cuts NEVER fail interval Hall, so no independent
failure family stresses this decomposition. The clean "only f shortens" structure is a strongly-
supported conjecture for general interval-Hall failures, not yet proven general. The previous
GPT-Pro GET (decoupled endpoint-tax E≤c) was FALSE on census γ-min (E=6/5>c=1); this ΔΓ identity is
a DIFFERENT, coupled object and survives every exact check so far.
