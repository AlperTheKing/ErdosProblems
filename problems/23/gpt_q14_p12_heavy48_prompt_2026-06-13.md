CONTEXT:
We are attacking Erdos problem #23 via the a(30)=36 low-codegree route.
The q=15 branch is closed.  The active branch is q=14/t=2, cap74, p=12.

The current cap74 row is

  (z,s1,s2,d,p,e_R,U) = (3,5,5,1,12,25,12).

So R has 14 vertices split as:

  Z: 3 zero-labelled vertices,
  S1: 5 singleton-1 vertices,
  S2: 5 singleton-2 vertices,
  D: 1 doubleton vertex.

R-edges are counted by five category variables:

  ZZ, ZS1, ZS2, ZD, S1S2,

where each row below has total e_R=25.  The R-category constraints are the
disjoint-label rule, triangle-freeness, and the q14/t2 per-vertex local
domination constraints.  These leave exactly 124 R-feasible category profiles.

Verified computation so far:

1. A general R quotient counter/emitter was validated on the extreme category
   (ZZ,ZS1,ZS2,ZD,S1S2)=(0,3,3,3,16), matching the independent old count
   quotient=18418.

2. The all-category quotient run over the 124 R-feasible categories gives
   total quotient count 732715.

3. All categories with quotient <=1000 have now been emitted and checked by
   the fixed-R A-only verifier:

   categories=76, quotient representatives=11706,
   UNSAT=11706, SAT=0, UNKNOWN=0.

Remaining frontier:

  48 heavy categories, total quotient representatives 721009.

Grouped by (ZZ,ZD), the remaining heavy categories are:

  (0,3): 19 cats, sumQ=538317, maxQ=80386
  (0,2): 10 cats, sumQ=108982, maxQ=19901
  (1,2):  8 cats, sumQ=49575,  maxQ=10952
  (0,1):  4 cats, sumQ=12258,  maxQ=3944
  (1,1):  3 cats, sumQ=5635,   maxQ=2633
  (2,2):  3 cats, sumQ=5189,   maxQ=2389
  (2,1):  1 cat,  sumQ=1053,   maxQ=1053

The largest remaining categories are:

  idx  ZZ ZS1 ZS2 ZD S1S2 quotient
  275   0   4   4  3   14   80386
  339   0   5   4  3   13   58675
  279   0   4   5  3   13   58675
  215   0   3   5  3   14   53064
  335   0   5   3  3   14   53064
  211   0   3   4  3   15   43701
  271   0   4   3  3   15   43701
  399   0   6   3  3   13   27350
  219   0   3   6  3   13   27350
  343   0   5   5  3   12   22545
  342   0   5   5  2   13   19901
  207   0   3   3  3   16   18418
  338   0   5   4  2   14   17191
  278   0   4   5  2   14   17191
  403   0   6   4  3   12   15596
  283   0   4   6  3   12   15596
  282   0   4   6  2   13   12878
  402   0   6   4  2   13   12878
  1262  1   5   4  2   13   10952
  1202  1   4   5  2   13   10952

Previous useful GPT-derived but independently checked facts:

- Since p=12, the A-B graph P is 2-regular on 6+6 vertices.
- If P were C12, too few vertices could have m_r=6, so P is disconnected.
  Thus P has templates C8+C4, C6+C6, or 3C4.
- State tables for independent sets in those three templates are small:
  329, 324, and 343 states respectively.
- The current fixed-R verifier is reliable when R is fixed, but brute-forcing
  all remaining quotient representatives is not a satisfying proof route.

STATUS:
We need a structural lemma or a much smaller exact certificate for the 48 heavy
categories.  The biggest mass is (ZZ=0,ZD=3), especially high S1S2.

QUESTION:
Find the highest-leverage rigorous next step.  Ideally prove a structural
lemma that excludes most or all of the remaining heavy categories, especially
the (ZZ=0,ZD=3) block.  If a full lemma is not available, give a precise finite
state verifier/certificate design that is substantially smaller than checking
721009 fixed-R quotient representatives and whose constraints are strong enough
to be trusted as a proof certificate rather than a black-box SAT run.

REQUIREMENTS:
Give a complete mathematical argument where possible.  If you propose a finite
certificate, specify the exact state variables, constraints, and certificate
format.  Do not assume any unverified q<14 closure unless explicitly marked
conditional.  End by listing the weakest steps of your own answer.
