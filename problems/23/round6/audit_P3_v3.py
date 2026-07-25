"""audit_P3_v3.py -- audit of P3.md's open statement V3 (VEGA-infinity).

P3.md states V3 with the six special atoms sitting "at circle position 2/3, 0, 1/3 respectively and
joined to that position's far-arc", the arcs being X=(0,1/3), Y=(1/3,2/3), Z=(2/3,1), and then
asserts:
    "Every Vega graph is the atomic instance of V3 with mu = the uniform measure on the
     (3i-1)-th roots of unity minus at most the point 2i ... Conversely V3 => V1 for every i."

Test: instantiate V3 literally (atoms at j/(3i-1), specials attached to the FIXED arcs) and compare
the attachment sets with Upsilon_i's actual X, Y, Z.  Then check the rule P3.md states correctly in
its own section (a): each special sits at circle POSITION 2i, 1, i+1/2 and is joined to the far arc
of that position.
"""
from audit_P3_core import upsilon_adj

print('(A) V3 exactly as written in P3.md: fixed arcs X=(0,1/3), Y=(1/3,2/3), Z=(2/3,1)')
print('    atoms at j/(3i-1), j = 1..3i-1')
bad = 0
for i in (2, 3, 4, 5, 8, 20):
    L = 3 * i - 1
    Xl = [j for j in range(1, L + 1) if 0 < j / L < 1 / 3]
    Yl = [j for j in range(1, L + 1) if 1 / 3 < j / L < 2 / 3]
    Zl = [j for j in range(1, L + 1) if 2 / 3 < j / L < 1]
    Xr, Yr, Zr = list(range(1, i + 1)), list(range(i + 1, 2 * i + 1)), list(range(2 * i + 1, L + 1))
    ok = (Xl == Xr and Yl == Yr and Zl == Zr)
    bad += (not ok)
    print('  i=%-3d V3-literal sizes=(%d,%d,%d)   Upsilon_i sizes=(%d,%d,%d)   identical: %s'
          % (i, len(Xl), len(Yl), len(Zl), len(Xr), len(Yr), len(Zr), ok))
    if i <= 3:
        print('        V3-literal : X=%s Y=%s Z=%s' % (Xl, Yl, Zl))
        print('        Upsilon_%d  : X=%s Y=%s Z=%s' % (i, Xr, Yr, Zr))
        missing = [j for j in range(1, L + 1) if j not in Xl + Yl + Zl]
        print('        atoms with NO special attached under V3-literal: %s' % missing)
print('  V3-literal instances that equal Upsilon_i : %d of 6   ->  V3 => V1 FAILS as written'
      % (6 - bad))

print()
print('(B) the rule P3.md states correctly in its own section (a): far arc of the actual position')
print('    a,u at circle point 2i ; b,v at 1 ; c,w at the half-integer i+1/2')
allok = True
for i in (2, 3, 4, 5, 8, 20):
    L = 3 * i - 1

    def far(p):
        return [j for j in range(1, L + 1) if 3 * min((j - p) % L, (p - j) % L) > L]
    a1 = far(2 * i) == list(range(1, i + 1))
    b1 = far(1) == list(range(i + 1, 2 * i + 1))
    c1 = far(i + 0.5) == list(range(2 * i + 1, L + 1))
    allok = allok and a1 and b1 and c1
    print('  i=%-3d  farArc(2i)==X : %-5s   farArc(1)==Y : %-5s   farArc(i+1/2)==Z : %s'
          % (i, a1, b1, c1))
print('  all correct :', allok)
print()
print('CONCLUSION: V3 as written does NOT have the Vega graphs as atomic instances, so')
print('            "V3 => V1 for every i" is FALSE as stated.  The fix is to make the three')
print('            positions parameters (2i/(3i-1), 1/(3i-1), (i+1/2)/(3i-1)) rather than the')
print('            fixed limits 2/3, 0, 1/3 -- i.e. to use the rule of section (a).')

# sanity: the circle rule d>1/3 on the (3i-1)-th roots of unity really is Gamma_i
print()
for i in (2, 3, 5):
    L = 3 * i - 1
    adj, _ = upsilon_adj(i)
    ok = True
    for u in range(1, L + 1):
        for v in range(u + 1, L + 1):
            circ = 3 * min((u - v) % L, (v - u) % L) > L
            if circ != (v in adj[u]):
                ok = False
    print('  sanity: circle rule d>1/3 on %d atoms reproduces Gamma_%d inside Upsilon_%d : %s'
          % (L, i, i, ok))
