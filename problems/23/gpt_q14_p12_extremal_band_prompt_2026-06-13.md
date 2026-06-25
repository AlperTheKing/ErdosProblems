CONTEXT:
We are attacking Erdos problem #23 through the local branch proof for a(30)=36.
The q=15 branch is closed.  The current obstruction is the q=14, t=2 branch.

The remaining cap=74 equality layer has this label profile on R, |R|=14, with two
root colours:

- z=3 zero-labelled R vertices;
- s1=s2=5 singleton-labelled R vertices;
- d=1 double-labelled R vertex;
- U=12;
- p=e(A,B)=12, with |A|=|B|=6;
- e_R=25;
- cap = 123 - p - U - e_R = 74.

R-edges are only between disjoint labels and R is triangle-free.  For q14/t=2
the label-local domination is: if an R-vertex is missing colour i, it has at
least 2 R-neighbours whose label contains i.

Because p=12 and every A/B vertex has at least two neighbours across the
A-B cut, the bipartite graph G[A,B] is exactly 2-regular on 6+6 vertices.
Also every A or B vertex has total degree at least 7 into the local model, so
each A/B vertex needs at least 5 incident R-neighbours.

The SAT encoding also enforces:

1. zero-labelled r has at least 2 neighbours in A and at least 2 in B;
   singleton-labelled r has at least 1 in A and at least 1 in B;
2. deg_R(r)+deg_A(r)+deg_B(r) >= 8-|label(r)|;
3. for each r, deg_A(r)+deg_B(r) <= p/2 = 6;
4. if r hits a and b then ab is a nonedge of A-B;
5. if rr' is an R-edge then r,r' cannot both hit the same A-vertex or the same B-vertex;
6. every A/B vertex sees both root colours through R-neighbours;
7. every missing A-B pair has at least two common R-neighbours;
8. every pair inside A, and inside B, has a common neighbour in R or across A-B;
9. every R-A and R-B incidence has at least two local common neighbours;
10. the paired rooted-cut inequalities are enforced exactly.

I split e_R=25 by category:

ZZ, ZS1, ZS2, ZD, S1S2

where Z is the zero-labelled class, D is the double-labelled vertex, and
S1/S2 are singleton classes.

There are 3500 possible category profiles.  At 10k SAT conflicts, 3376 are
UNSAT and 124 remain UNKNOWN.  Re-running those 124 at 100k conflicts closed
none.  The UNKNOWN band is:

- by S1S2 count: 10:43, 11:33, 12:23, 13:14, 14:7, 15:3, 16:1;
- by (ZZ,ZD): (0,3):28, (0,2):21, (0,1):15, (1,2):15, (0,0):10,
  (1,1):10, (2,2):10, (1,0):6, (2,1):6, (2,0):3.

The most extreme UNKNOWN is:

  ZZ=0, ZS1=3, ZS2=3, ZD=3, S1S2=16.

A no-conflict-limit SAT run on that one profile timed out after 600s.

STATUS:
Compute alone is no longer an efficient path.  We need a structural lemma for
this p=12 cap=74 band, ideally eliminating the whole 124-profile UNKNOWN band
or adding a small sound inequality/cut that can be encoded.

QUESTION:
Give a rigorous mathematical attack on this exact remaining band.  Prefer a
short lemma involving the category counts ZZ, ZS1, ZS2, ZD, S1S2 or the
2-regular A-B structure.  The target is to prove that no q14/t=2 local model
can satisfy z=3, s1=s2=5, d=1, p=12, e_R=25, cap=74 under the constraints
above.  If a full contradiction is not visible, identify the sharpest missing
sublemma and a concrete additional exact check that would decide it.

REQUIREMENTS:
Do not handwave.  Decompose every counting step.  If you use a theorem, cite it
only if you are sure it exists.  End by listing the weakest steps of your own
answer.
