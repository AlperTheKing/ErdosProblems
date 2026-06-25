CONTEXT:
We are working only on the finite a(30)=36 track for Erdos problem #23, not
claiming the full general #23 reduction.  In the q13/r0=8/t=2 five-label
branch, support profile 6195 has label counts

  cnt = (0,0,3,2,3,3,0,2)

with labels

  0,1,2 : label 2
  3,4   : label 3
  5,6,7 : label 4
  8,9,10: label 5
  11,12 : label 7.

For the e_R=12 high-M row, your C6 projection lemma on local vertices
X={0,1,2}, H={8,9,10} closed all six masks: p <= p_XH <= 21, contradicting
p>=25.

I implemented an independent C++ checker:

  search23/verify_projection_6195_row.cpp

It projects A/B states to X union H, enumerates all projected 6-multisets on
each shore, imposes projected column sums and all projected R/R pair-cover
requirements internal to X union H, and maximizes p_XH.  For e_R=12 it
reproduces p_XH<=21 for all six masks.

NEW DATA:
For e_R=13, there are 72 local skeleton masks.  I ran the same generalized
projection checker on rows:

  p=24, max_total_excess=5
  p=25, max_total_excess=5

Result:

  p=24: 54 CLOSE, 18 OPEN
  p=25: 54 CLOSE, 18 OPEN

The open masks are exactly the same structural class.  In every open case:

  projection_types = 17
  need_pairs = 2
  worst_p_proj = 28

Representative open mask:

  mask = 0xfd8a38

For this mask, on local vertices X={0,1,2}, H={8,9,10}, the local R-edges are:

  0-8, 0-9, 0-10,
  1-8, 1-10,
  2-8, 2-9.

So the X-H graph is K_{3,3} minus only two edges:

  missing pairs: (1,9), (2,10).

The local nonedge/codegree needs are:

  (1,9): need 2 A/B common neighbours
  (2,10): need 2 A/B common neighbours

All other local nonedges have need 0 due to label or R common neighbours.

The legal projected independent sets are 17:

  {}, {0}, {1}, {0,1}, {2}, {0,2}, {1,2}, {0,1,2},
  {8}, {9}, {1,9}, {8,9},
  {10}, {2,10}, {8,10}, {9,10}, {8,9,10}.

The checker finds the worst projected upper bound already at the floor target:

  floor_local = (4,5,5,3,4,4)
  worst_target = (4,5,5,3,4,4)
  worst_p_proj = 28.

QUESTION:
Find a rigorous P-free strengthening that closes this e_R=13 open projection
class, ideally proving p <= 23 (to close p=24,25) or at least p <= 24/25 as
useful partial closures.  Do not use fixed A/B template enumeration.

Please focus on the representative mask 0xfd8a38 first.  A good answer would
identify one additional valid projected/typewise constraint missing from my
current projection checker, or a hand-counting lemma using the above local
structure plus the full q13/t=2 constraints:

  - triangle-freeness,
  - every R-nonedge has codegree at least 2,
  - root-to-R codegree,
  - A/R and B/R codegree,
  - A/A and B/B codegree,
  - p is induced by disjoint A/B states,
  - full Psi rooted cuts if needed,
  - H14 anti-tightness is allowed only if explicitly stated.

REQUIREMENTS:
Give a rigorous argument or a precise finite certificate formulation smaller
than fixed A/B template enumeration.  Explicitly flag any step that is only a
heuristic.  End by listing the weakest steps in your own answer.
