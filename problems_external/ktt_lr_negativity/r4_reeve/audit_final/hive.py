"""Independent r=4 hive-polytope constructor built from Buch's definition.
Exact integer arithmetic only. Validated against engines A and B before use."""
from fractions import Fraction
from itertools import product

# hive nodes (i,j), 0<=j<=i<=4 ; interior free = (2,1),(3,1),(3,2)
INTERIOR = [(2,1),(3,1),(3,2)]

def _partial(part, k):
    # sum of first k parts (parts padded to length 4 with zeros)
    p = list(part) + [0]*4
    return sum(p[:k])

def border_values(lam, mu, nu):
    """Return dict of fixed border labels for the 15-node size-4 hive."""
    h = {}
    # left side j=0 : nu partial sums
    for i in range(5):
        h[(i,0)] = _partial(nu, i)
    # right diagonal j=i : lam partial sums
    for i in range(5):
        h[(i,i)] = _partial(lam, i)
    # bottom row i=4 : from lam-corner (4,4)=|lam| add mu going left
    L = _partial(lam,4)
    for j in range(5):
        h[(4,j)] = L + _partial(mu, 4-j)
    return h

# The 18 rhombus inequalities (>=0 form: LHS - RHS >= 0)
def rhombus_rows():
    rows = []
    # (a) h(i,j)+h(i+1,j+1) >= h(i+1,j)+h(i,j+1) ; 0<=i<=3,0<=j<=i-1
    for i in range(4):
        for j in range(0, i):
            rows.append(( [(i,j,1),(i+1,j+1,1),(i+1,j,-1),(i,j+1,-1)] ))
    # (b) h(i,j+1)+h(i+1,j+1) >= h(i,j)+h(i+1,j+2) ; 0<=i<=3,0<=j<=i-1
    for i in range(4):
        for j in range(0, i):
            rows.append(( [(i,j+1,1),(i+1,j+1,1),(i,j,-1),(i+1,j+2,-1)] ))
    # (c) h(i+1,j)+h(i+1,j+1) >= h(i,j)+h(i+2,j+1) ; 0<=i<=2,0<=j<=i
    for i in range(3):
        for j in range(0, i+1):
            rows.append(( [(i+1,j,1),(i+1,j+1,1),(i,j,-1),(i+2,j+1,-1)] ))
    return rows

ROWS = rhombus_rows()
assert len(ROWS)==18, len(ROWS)

def constraints(lam, mu, nu):
    """Return list of (a1,a2,a3, rhs) meaning a1*x1+a2*x2+a3*x3 >= rhs,
       with x1=h(2,1),x2=h(3,1),x3=h(3,2). Border folded into rhs."""
    h = border_values(lam, mu, nu)
    idx = {INTERIOR[0]:0, INTERIOR[1]:1, INTERIOR[2]:2}
    cons = []
    for row in ROWS:
        coef = [0,0,0]
        const = 0  # constant contribution to LHS
        for (i,j,c) in row:
            if (i,j) in idx:
                coef[idx[(i,j)]] += c
            else:
                const += c*h[(i,j)]
        # LHS = coef.x + const >= 0  ->  coef.x >= -const
        cons.append((coef[0],coef[1],coef[2], -const))
    return cons

def _bounds(cons):
    # crude interval bounds per coordinate from single-coordinate constraints; else fallback box
    return None

def feasible_box(lam,mu,nu):
    # bounding box for x1,x2,x3 from border monotonicity: each interior label lies
    # between neighbouring border labels; use generous [0, |nu|].
    N = _partial(nu,4)
    return (0, N)

def lattice_points(lam,mu,nu, t=1):
    """Exact count of integer hive interior labels for stretch t."""
    lam=[t*a for a in lam]; mu=[t*a for a in mu]; nu=[t*a for a in nu]
    cons = constraints(lam,mu,nu)
    lo,hi = feasible_box(lam,mu,nu)
    cnt=0
    for x1 in range(lo,hi+1):
        # prune with constraints depending only on x1
        ok1=True
        for (a,b,c,r) in cons:
            if b==0 and c==0:
                if a>0 and a*x1 < r: ok1=False;break
                if a<0 and a*x1 < r: ok1=False;break
                if a==0 and 0 < r: ok1=False;break
        if not ok1: continue
        for x2 in range(lo,hi+1):
            ok2=True
            for (a,b,c,r) in cons:
                if c==0:
                    if a*x1+b*x2 < r: ok2=False;break
            if not ok2: continue
            for x3 in range(lo,hi+1):
                good=True
                for (a,b,c,r) in cons:
                    if a*x1+b*x2+c*x3 < r:
                        good=False;break
                if good: cnt+=1
    return cnt

if __name__=="__main__":
    import sys
    lam=[int(x) for x in sys.argv[1].split(',') if x!='']
    mu=[int(x) for x in sys.argv[2].split(',') if x!='']
    nu=[int(x) for x in sys.argv[3].split(',') if x!='']
    print(lattice_points(lam,mu,nu))
