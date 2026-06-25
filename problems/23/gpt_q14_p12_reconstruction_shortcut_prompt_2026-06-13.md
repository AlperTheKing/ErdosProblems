CONTEXT:
We are attacking Erdos problem #23 via the low-codegree route to a(30)=36.
The q=15 branch is closed.  The active branch is q=14, t=2, cap=74,
p=12.  Earlier certificates close low caps and 76 small-quotient cap74/p12
R-categories.  There remain 48 heavy R-categories.

The current q=14/t=2 model has:
- root nonedge xy with codegree 2;
- two common neighbours c1,c2;
- A=N(x)\{c1,c2}, B=N(y)\{c1,c2};
- |A|=|B|=5;
- R has 14 vertices, labelled by membership in the c1/c2 neighbourhoods:
  Z, S1, S2, D.
- p=e(A,B)=12, so A--B is one of the three 2-regular complement templates:
  3C4, C6+C6, C8+C4.

VERIFIED LEMMA V143:
For u in S1 and v in S2, write X_r=N_A(r), Y_r=N_B(r), and
Z(u,v)=|{z in Z : zu and zv are R-edges}|.
Then

  uv is an R-edge  iff  Z(u,v)+|X_u cap X_v|+|Y_u cap Y_v| = 0.

The value 1 is impossible, and value >=2 forces uv to be a nonedge.
This follows from triangle-freeness and the minimum nonedge-codegree-2
hypothesis in the q=14 branch.

CURRENT VERIFICATION:
A C++ reconstruction verifier enumerates zero-skeleton orbits and A/B
incidence states, reconstructs all S1--S2 R-edges by V143, and then checks:
exact category counts, cap74, R triangle-free/disjointness, local domination,
R/A/B degree lower bounds, A/B colour-hit constraints, missing A--B and same
side codegrees, A--R/B--R codegrees, and fixed R--R nonedge codegrees.

It has closed category idx=275, idx=279, and idx=339.  The remaining heavy
categories are still being enumerated.  Some runs are memory-heavy.

QUESTION:
Find a rigorous structural shortcut that reduces or eliminates the remaining
q=14/t=2 cap74 p=12 heavy categories without enumerating all A/B incidence
states.

Please focus on the V143 reconstruction formula.  Is there a hand-checkable
lemma of the following kind?

  In the q=14/t=2, p=12, cap74 setup, every heavy category forces either
  (i) a violation of V143 because some S1--S2 pair has common-neighbour count 1,
  (ii) a cap74 excess from A/B incidence sums,
  (iii) a missing A--B or R--R nonedge with codegree <2, or
  (iv) a reducible symmetric compression that maps it to one of the already
  closed small-quotient categories.

Give a complete proof if possible.  If no full shortcut exists, identify the
smallest extra invariant that should be added to the verifier to kill many
heavy categories.  Be explicit and adversarial: list the weakest step and any
counter-pattern that might survive.
