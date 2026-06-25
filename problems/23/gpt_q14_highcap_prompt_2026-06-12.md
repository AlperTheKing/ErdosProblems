CONTEXT: Erdős #23 / a(30)=36 low-codegree finite proof attempt. We are in the q=14,t=2 branch.

Setup: triangle-free/maximal setting after choosing a nonedge xy with |C|=t=2 common neighbours c1,c2. Let A=N(x)\C and B=N(y)\C, so |A|=|B|=6. Let R be the remaining 14 vertices. For r in R, label L(r) subset {1,2} records which c_i are adjacent to r. Counts:
  z = |label 0|, s1=|{1}|, s2=|{2}|, d=|{1,2}|, z+s1+s2+d=14,
  U=s1+s2+2d, p=e(A,B), eR=e(R), cap=123-p-eR-U = e(A∪B,R).
Allowed R-edges only between disjoint labels; R is triangle-free.

Verified scalar constraints already used:
  s1+d>=6, s2+d>=6;
  if s1>0 then s2>=2, if s2>0 then s1>=2;
  if z>0 and d=0 then s1,s2>=2; if z>0 and d=1 then s1,s2>=1;
  eR >= max(13, 2 max(s1,s2)+h(d) z), h(0)=4,h(1)=3,h(d>=2)=2;
  eR <= floor(z^2/4)+z(s1+s2+d)+s1*s2;
  p+eR>=37, p<=11+eR, p>=U+eR-39;
  cap >= 112-U-2eR, cap>=84-2p;
  cap >= 4z + max(2(s1+s2), d==0 ? 24 : 12);
  paired rooted W=D/Mantel cut: bd(D)_lb=eR-(floor(z^2/4)+z(s1+s2)+s1*s2) <= (eR+53-U-p+2m_D)/2, m_D=min(d,s1)+min(d,s2).

Exact fixed-label SAT verifier also enforces:
  R-triangle-free, exact p/eR/cap, A/B degree and missing AB constraints,
  every A/B vertex hits each U_i, nonedge-codegree thresholds, R-degree,
  x-r and y-r nonedge codegree lower bounds, fixed paired-rooted cuts.

Verified computation:
  q=15 is closed by shadow lemma eR >= 3 max(n1,n2).
  q=14,t=2 is closed for cap<=40 by exact fixed-label batches:
    cap<=38 via batches + incidence bound,
    cap39: 577/577 UNSAT,
    cap40: 665/665 UNSAT.

Current remaining q14/t2 scalar frontier:
  35234 rows, cap=41..74.
  cap counts: 41:696,42:788,43:821,44:927,45:949,46:1043,47:1046,48:1112,49:1094,50:1152,51:1122,52:1194,53:1166,54:1227,55:1195,56:1257,57:1224,58:1297,59:1261,60:1325,61:1287,62:1364,63:1321,64:1386,65:1329,66:1371,67:1247,68:1193,69:963,70:795,71:530,72:348,73:151,74:53.
  largest label-count shapes among cap>=41: (z,d,s1,s2)=(6,4,2,2),(5,3,3,3),(4,2,4,4) each 429 rows; (5,4,3,2),(5,4,2,3),(3,2,4,5),(4,3,4,3),(4,3,3,4),(3,2,5,4) each 404; (8,6,0,0) has 400.

STATUS: Need a mathematical high-cap reduction. Brute force from cap41..74 is possible but probably wasteful; we want a lemma that strengthens cap lower bounds or eliminates high-cap count profiles. Current q14/t2 proof is NOT complete.

QUESTION: Find one rigorous new q14/t2 lemma, preferably scalar/counting or a small structural reduction, that is not already among the listed constraints and that eliminates a large part of cap>=41, ideally proving cap<=40 or forcing a very narrow exceptional family. Please give a complete proof from the setup. If no such lemma is valid, identify the exact missing obstruction and a targeted finite experiment that would decide it.

REQUIREMENTS: Be adversarial. Do not re-state existing constraints. Every inequality must specify what incidences/edges are counted and why each object is counted at most/at least that many times. End by listing weakest steps and any assumptions not explicit in the setup.
