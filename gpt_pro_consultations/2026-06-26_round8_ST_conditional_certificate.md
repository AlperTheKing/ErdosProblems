# GPT-Pro round 8: (A')/(LEP) NOT provable from exchange alone; precise target = (ST) conditional certificate (2026-06-26)

Thread c/6a3b8a74 (i37, 9808 chars; preamble flagged "detour charging lemma"). Step-1 drove GPT to PROVE
(A')/(LEP) at Gamma>=N^2 via exchange-minimality + sub-tightness certificate, armed with my exact data
(C5[q] tight, 0 fails Gamma>=N^2 N<=11 + M(Petersen), exactly 3 Gamma<N^2 violations). AUDITED; (ST) exact-tested.

## VERDICT (honest)
Exchange-minimality alone does NOT prove (A')/(LEP). Exact obstruction: peeling an incident LONG bad edge f
gives a LARGER N^2-drop budget b(k)=2kN-k^2 (k>h), and that extra budget can ABSORB the very excess we want to
forbid -- so C_f need not beat the min-overshoot C. Exchange gives a LOWER bound on L(C_f)-L(C); to force a
contradiction (prove A') one needs an UPPER bound on the incident mass = "the missing mass theorem". Stall.

## The precise target = (ST) conditional certificate
   (ST)   h*(A(C)-2(N-h))_+ + (H(C)-Delta(C))_+  <=  (N^2 - Gamma(G))_+      [min-overshoot peel C]
Any excess in (A') or (LEP) is bounded by the Gamma-DEFICIT. If Gamma>=N^2 the RHS=0, forcing (A')+(LEP).
EXACTLY matches my data: the only (A')/(LEP) violations are the 3 sub-tight N=11 graphs (Gamma=100 def21 A-excess;
Gamma=74 def47 LEP-excess), all Gamma<N^2.

## Concrete proof STRATEGY for (A') (token assignment) -- gap = overlap
(A') A(C)=sum_{f in F(C)} ell(f) <= 2(N-h) "should" hold by TOKEN ASSIGNMENT: each incident bad edge f=xy (x in C)
gets ell(f) tokens; its shortest B-geodesic supplies a token path; charge tokens to vertices OUTSIDE C; triangle-
free + shortestness should cap each outside vertex at <=2 tokens => A(C)<=2(N-h). The OBSTRUCTION: OVERLAP --
shortest geodesics from different incident bad edges can SHARE hubs/tails (a vertex gets >2 tokens). That overlap
is exactly what the 3 sub-tight N=11 examples exhibit, and it is bounded by the Gamma-deficit => (A-ST):
   h*(A(C)-2(N-h))_+ <= (N^2-Gamma)_+.  Plus the analogous (LEP-ST) => (ST).
Where hypotheses enter: triangle-free => ell(f)>=5 (d_B>=4) + induced odd cycle (no B-shortcut); shortestness =>
the token path is a geodesic; Gamma>=N^2 => the deficit budget is 0 (forces no overlap excess).

## Status
delta=0 OPEN. Round 8 is honest + sharp: exchange insufficient (lower not upper bound), the precise open lemma is
(ST) = "geodesic-overlap excess <= Gamma-deficit" (a token-charging / missing-mass theorem). Same Gamma>=N^2-
conditional hard core as Step-2's (A')/(LEP) and my graphon rigidity -- now with a concrete token-assignment
proof strategy whose ONLY gap is the overlap-vs-deficit bound. (ST) exact-test: see verify_ST.py result.
6th proposed closing reformulated, none closed; no false closure. Relayed to Step-2.
See [[erdos23-gamma-geodesic-peel-angle]] [[erdos23-delta0-cut-pressure-rigidity]] [[erdos23-agent-channel]].
