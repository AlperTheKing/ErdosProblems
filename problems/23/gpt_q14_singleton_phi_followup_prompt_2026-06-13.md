CONTEXT: Erd?s #23 / a(30)=36 low-codegree proof attempt. q=15 is closed. Active branch: q=14/t=2/cap74/p=12 heavy reconstruction-state verifier.

VERIFIED:
- S1-S2 reconstruction lemma: dynamic S1-S2 edges are forced by zero-common-neighbour count plus A/B-state overlaps.
- Neighbour-union capacity: for every r, m_r + |union_{u in N_R(r)} X_u| + |union_{u in N_R(r)} Y_u| <= 12.
- New singleton Phi rooted-cut lemma: for every R-vertex r, d_R(r) <= m_r + |ell(r)|.
- Current C++ verifier enforces S1-S2 reconstruction, local domination, R-degree lower bounds, A/B degree constraints, A/B and R codegree constraints, optional static/full union capacity, and optional singleton Phi.

COMPUTATIONAL STATUS:
- 16 of 48 heavy q14/cap74/p12 categories are closed.
- Open hard leaves include idx341 zi=16 template=3C4 and idx219 zi=77 C6+C6, zi=81 C6+C6, zi=86 C6+C6, zi=86 3C4.
- Full all-mask rooted cuts are too heavy when encoded naively as CNF.

QUESTION: Find the smallest next rigorous q14/cap74/p12 rooted-cut consequence after singleton Phi that is (1) unconditional in the terminal q=14 model, (2) cheap to encode in the state verifier, and (3) likely to eliminate the remaining hard leaves. Prefer a cut involving |W|=2 or a local pair (r,s), not all 2^14 masks. Give a complete derivation from the rooted-cut inequalities and specify exact CNF/PB form.

REQUIREMENTS: Be adversarial. If the proposed cut depends on q<14 reroot closure, mark it conditional. Do not suggest broad SAT sweeps. End with weakest step.
