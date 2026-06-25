# Erdős #1159 — bounded-intersection blocking sets in finite projective planes
Statement (erdosproblems.com/1159, [ELS]/Ben Green list): is there a constant C>1
such that EVERY finite projective plane P has a point set S with 1 <= |S∩l| <= C
for every line l? Known: Erdős–Silverman–Stein |S∩l| << log n achievable. OPEN
(infinitary in the family; uniform C is the hard core).

## Computational census (verified, 2026-06-13)
minC(q) := min over point-sets S in PG(2,q) of max_line |S∩l|, s.t. every line met.
- q=2 (Fano, 7 pts/7 lines): minC = 3. Hand-verified: a 3-pt triangle misses
  exactly 1 of the 7 lines, so max-intersection <= 2 blocking is impossible; a line
  (3 pts) blocks all with max 3. So minC=3.
- q=3 (13 pts/13 lines): minC = 3 (brute over 2^13). witness size 6.
Tool: problems/1159/pg_minC.py (exact subset search; valid for prime q only via Z/q).

## NEXT (longer-horizon)
- GF(q) arithmetic for prime-power q=4,8,9 (Z/q wrong there).
- q>=4: brute infeasible (2^21..2^91); use ILP/SAT: binary-search C, feasibility =
  "exists S with 1<=|S∩l|<=C for all lines" (a covering+packing ILP).
- Theorem target (the genuinely-new result): an explicit algebraic construction giving
  a uniform constant C for Desarguesian PG(2,q) (beating ESS log n) — candidate
  ingredients: unions of conics/ovals (meet lines in <=2) patched to also block
  external lines; or Baer-subplane / unital based sets. This is research-level, not a
  quick computation.
STATUS: data census started; core is hard/open. Banked new result this run remains #944 Thm C.
