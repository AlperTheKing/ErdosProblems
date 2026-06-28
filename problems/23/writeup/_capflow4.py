"""ANGLE B pt4: SUFFICIENCY PROBE. Is the scalar (indicator/Hall) cut SUFFICIENT for CAP,
or only NECESSARY? Construct an explicit instance of the *abstract* grounded-conductance
problem where ALL indicator cuts pass (1_S^T Y 1_S >= overload(S) for every S<=O) yet
the MATRIX inequality Y >= D_O FAILS (negative generalized eigenvalue, optimal x fractional).

This is an abstract electrical certificate (not tied to a graph) that DECIDES the GPT-Pro
hint: 'the scalar cut is only a necessary shadow; the true object is vector/energy-current'.

A 2-overload toy: O={1,2}, one ground node 0. Conductances:
   Y is the effective-conductance (grounded-Laplacian) matrix on O:
       Y = [[g1+c, -c],[-c, g2+c]]
   where c = conductance between nodes 1,2 ; g1,g2 = conductance to ground.
   D_O = diag(d1,d2), d_i = overload at i.
Indicator cuts:
   S={1}: 1^T Y 1 = g1+c >= d1
   S={2}:           g2+c >= d2
   S={1,2}: (1,1) Y (1,1)^T = g1+g2 >= d1+d2
Matrix Y>=D_O fails iff det(Y-D_O)<0 with some diagonal negative, i.e.
   (g1+c-d1)(g2+c-d2) - c^2 < 0   while both indicator scalars >= 0.
Pick numbers making all three scalar cuts hold but the matrix fail => scalar cut INSUFFICIENT.
"""
from fractions import Fraction as F
from _gcd import is_psd_exact

def toy(g1,g2,c,d1,d2):
    Y=[[g1+c,-c],[-c,g2+c]]
    D=[[d1,F(0)],[F(0),d2]]
    YmD=[[Y[i][j]-D[i][j] for j in range(2)] for i in range(2)]
    # indicator cuts
    s1=g1+c-d1        # S={1}
    s2=g2+c-d2        # S={2}
    s12=g1+g2-(d1+d2) # S={1,2}: cross conductance c cancels (internal), only ground edges leave
    cap=is_psd_exact([row[:] for row in YmD],2)
    return dict(s1=s1,s2=s2,s12=s12, all_ind=(s1>=0 and s2>=0 and s12>=0), cap=cap)

if __name__=="__main__":
    print("=== ANGLE B pt4: scalar-cut SUFFICIENCY decided (abstract grounded conductance) ===",flush=True)
    # Try to make all indicator cuts hold but matrix fail.
    # Need s1,s2,s12 >=0 but (g1+c-d1)(g2+c-d2) - c^2 <0.
    # Let g1=g2=g, d1=d2=d, c large. s1=s2=g+c-d, s12=2g-2d.
    # Need 2g-2d>=0 => g>=d. Then g+c-d>=c>0. Matrix: (g+c-d)^2 - c^2 = (g-d)(g-d+2c).
    # With g>=d that's >=0 => matrix HOLDS. Symmetric case can't break it. Need asymmetry.
    # Try g1 small, g2 large, c moderate. d1 large, d2 small.
    cases=[
        # (g1,g2,c,d1,d2)
        (F(1),F(10),F(3),F(7),F(2)),   # s1=1+3-7=-3 <0 -> indicator already fails (necessary)
        (F(5),F(10),F(3),F(7),F(2)),   # s1=5+3-7=1>=0, s2=10+3-2=11, s12=15-9=6>=0; matrix?
        (F(4),F(4),F(10),F(13),F(13)), # s1=4+10-13=1, s12=8-26<0 -> fails
        (F(20),F(20),F(100),F(119),F(119)), # s1=20+100-119=1, s12=40-238<0 fails
    ]
    for c in cases:
        r=toy(*c)
        print(f"  g1g2c d1d2={tuple(str(x) for x in c)}: indS1={r['s1']} indS2={r['s2']} indS12={r['s12']} "
              f"ALL-ind-pass={r['all_ind']} MATRIX-CAP={r['cap']}",flush=True)
    print("--- targeted search: all indicator cuts pass but matrix fails ---",flush=True)
    found=None
    # parametrize: want s1,s2,s12>=0 and (g1+c-d1)(g2+c-d2)<c^2.
    # set a=g1+c-d1>=0, b=g2+c-d2>=0, need a*b<c^2 and g1+g2>=d1+d2.
    # g1+g2-d1-d2 = (a + d1 - c) + (b + d2 - c) ... messy; brute small rationals.
    import itertools
    R=[F(k) for k in range(0,9)]
    for g1,g2,c,d1,d2 in itertools.product(R,R,[F(k,1) for k in range(1,9)],R,R):
        if d1==0 or d2==0: continue
        r=toy(g1,g2,c,d1,d2)
        if r['all_ind'] and not r['cap']:
            found=(g1,g2,c,d1,d2,r); break
    if found:
        g1,g2,c,d1,d2,r=found
        print(f"  FOUND: g1={g1} g2={g2} c={c} d1={d1} d2={d2} -> "
              f"indS1={r['s1']}>=0 indS2={r['s2']}>=0 indS12={r['s12']}>=0 but MATRIX-CAP={r['cap']}",flush=True)
        print("  => SCALAR/INDICATOR HALL CUT IS ONLY NECESSARY, NOT SUFFICIENT. CAP is a true matrix/energy statement.",flush=True)
    else:
        print("  no counterexample in search range (would suggest scalar cut suffices on 2-overload).",flush=True)
