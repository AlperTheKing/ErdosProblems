CONTEXT: Erdős #23 q14/t2 cap74, active row z=8,d=6,p=16,e_R=21,(ZZ,ZD)=(0,21). Verifier now has: exact A/B state law; full local codegrees; checkerboard + 489 rooted lazy cuts; terminal touched-column equality c_d+m_d=6; touched c_d<=4; outside-D visibility; touched c=4 inclusion; full tight-zero reroot scalar p*_z+eR*_z=37; reroot profile D' in {1,2,3,4,6}; reroot singleton balance D'+L'=6 and D'+R'=6; optional pair-counts; optional heavy-pair excess and one-defect touched-load.

Already closed in z8 p16 (0,21): zero-degree profiles (6,0,1,1), (5,2,0,1), and (5,1,2,0). Active now: zero D-degree profile (n2,n3,n4,n5)=(4,3,1,0). Thus t=4 tight zeros; the four non-tight zeros have D-degrees 3,3,3,4 (total non-tight D incidences 13). Coarse footprint branches u=2,3,4,5 all mostly UNKNOWN at 180s.

Pair-skeleton branching for t=4 gave:
- u=2, tight footprint (4,4): INFEASIBLE quickly.
- u=3: orbit (4,3,1) INFEASIBLE; orbits (4,2,2) and (3,3,2) UNKNOWN.
- u=4: all seven orbits UNKNOWN at 120s: (4,2,1,1), two (3,3,1,1), two (3,2,2,1), two (2,2,2,2).
- u=5 not yet fully tested.

QUESTION: Give the next mathematically safe P-free strengthening/branch for this t=4 profile. Prefer the analogue of the heavy-heavy excess / one-defect lemma used for t=5, but adapted to non-tight zero degrees 3,3,3,4 and t=4. State exact CP-SAT constraints. Which u=3/u=4 pair-skeletons should get D'<=4, heavy-excess branches, or touched-load equalities? Avoid fixed A/B-template enumeration.

REQUIREMENTS: Use only the assumptions listed. Flag dependence on cap<74/q<14 frontier closure. If a pure skeleton contradiction exists for a listed orbit, prove it. End with weakest steps.
