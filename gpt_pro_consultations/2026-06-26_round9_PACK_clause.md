# GPT-Pro round 9: (A-ST) reduced to a SINGLE clause -- prefix-defect PACKING (2026-06-26)

Thread c/6a3b8a74 (i39, 8536 chars). Step-1 drove GPT to CLOSE the token-charging proof of (A-ST):
h(A(C)-2(N-h))_+ <= (N^2-Gamma)_+. AUDITED. The (ST) certificate was already exact-validated N<=11 (0 viol/71302).

## RESULT: near-complete proof of (A-ST); reduces ALL of delta=0 to ONE disjointness lemma (PACK).
Structure GPT supplied:
- TOKEN SETUP: min-overshoot peel C, h=|C|, U=V(G)\C; each incident bad edge f in F(C) sends ell(f) tokens along
  its shortest B-geodesic to U; tri-free+shortest cap each U-vertex at <=2 tokens => A(C)<=2(N-h) UNLESS overcharge
  (a hub w in U gets >2 tokens from nonparallel-overlapping geodesics of distinct incident bad edges).
- (PT) PREFIX TRANSPORT [= Step-2's PROVED prefix-defect transport lemma, local form]: an excess token tau at w
  (nonparallel shared-vertex overlap) yields, for each cyclic prefix s in V(C), a CD-defect atom D(tau,s)>=1.
  So each excess token has h candidate defect atoms.
- (PACK) PREFIX-DEFECT PACKING [THE SOLE REMAINING GAP]: the atoms D(tau,s) can be chosen pairwise DISJOINT over
  (tau,s) in E x V(C). Equivalently sum_{tau,s} D(tau,s) <= (N^2-Gamma)_+, D>=1. Then h|E| <= sum D <= (N^2-Gamma)_+
  => A-ST. Failure mode of a bare pairwise "shared vertex gives defect": a hub can produce the SAME defect atom
  repeatedly (multiplicity) -- (PACK) forbids that double-counting.
- WHERE HYPOTHESES ENTER (GPT, explicit):
  * tri-free => ell>=5, induced odd cycle;  shortestness => geodesic token path;
  * GAMMA-MINIMALITY of the cut: converts transported CD-defect into GENUINE square-deficit N^2-Gamma (else a
    shared-prefix defect only says the routing is inefficient, not that the graph has real deficit);
  * MIN-OVERSHOOT choice: eliminates untransportable excess tokens -- if an excess token produced NO packed prefix
    defect, the incident bad edge f would have a sibling cycle C_f with ov(C_f)<ov(C) (the theta overlap uncrosses
    without square loss; the exchanged peel gains b(ell(f))-b(h) without matching ell-loss), contradicting min-overshoot.

## Status
delta=0 OPEN but now reduced to the SINGLE combinatorial lemma (PACK) = disjoint packing of the transported
prefix-defect atoms, ON TOP of Step-2's already-PROVED prefix transport (PT). The rest (min-overshoot eliminates
untransportable tokens; Gamma-minimality converts defect->deficit; the inequality h|E|<=deficit = my exact-validated
(A-ST)/(ST)) is supplied. This is the most concrete state of delta=0 all session: one disjointness clause closes it.
7th reformulation; none closed, but this is a near-proof modulo (PACK). No false closure. (PACK) is Step-2's
transport machinery + disjointness -- relayed to them as the precise final target.
See [[erdos23-gamma-geodesic-peel-angle]] [[erdos23-delta0-cut-pressure-rigidity]] [[erdos23-agent-channel]].
