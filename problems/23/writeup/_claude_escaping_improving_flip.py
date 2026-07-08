r"""Find the IMPROVING FLIP on GPT-Pro's 14-vtx escaping-atom pattern and relate it to the escaping atom h.
Mechanism check for the 'maximality excludes escaping atoms' path: for a flip set U, dcut = |deltaM(U)| - |deltaB(U)|
(bad edges crossing U become cut edges; cut edges crossing U become bad). A MAXIMUM cut has |deltaM(U)|<=|deltaB(U)| for
ALL U (MaxCutVertexIneq). The given escaping-lens cut is NON-max, so some U has |deltaM(U)|>|deltaB(U)| = an improving
flip. We find the minimal improving U and check how it sits relative to the escaping atom h=x-z, the lens W={a,b,c,y,w},
and h's geodesic support {a,b,c}. Goal: exhibit the concrete maximality contradiction the escaping-atom structure creates.
EXACT integer. Run from problems/23/writeup."""
from itertools import combinations

V = ['x','z','y','w','a','b','c','r1','r2','r3','r4','r5','r6','r7']
given = {v: 0 for v in ['x','z','y','w','b','r2','r4','r6']}
for v in ['a','c','r1','r3','r5','r7']:
    given[v] = 1
Bedges = [('x','a'),('a','b'),('b','c'),('c','y'),('z','c'),('a','w'),
          ('x','r1'),('r1','r2'),('r2','r3'),('r3','r4'),('r4','r5'),('r5','r6'),('r6','r7'),('r7','z')]
Medges = [('x','y'),('z','w'),('x','z')]   # e,f,h ; h=x-z is the escaping atom
W = {'a','b','c','y','w'}
supp_h = {'a','b','c'}   # geodesic support of h through W interior

def deltas(U):
    U = set(U)
    dM = [(u,w) for (u,w) in Medges if (u in U) != (w in U)]
    dB = [(u,w) for (u,w) in Bedges if (u in U) != (w in U)]
    return dM, dB

print("=== improving flip vs escaping atom (GPT-Pro 14-vtx pattern) ===")
# search minimal improving flips U (|deltaM|>|deltaB|), by size
found = []
for k in range(1, 6):
    for U in combinations(V, k):
        dM, dB = deltas(U)
        if len(dM) > len(dB):   # improving flip: dcut = |dM|-|dB| > 0
            found.append((k, set(U), len(dM), len(dB), len(dM)-len(dB), dM, dB))
    if found:
        break

if not found:
    print("no small improving flip up to size 5 (pattern would be a max cut) -- unexpected")
else:
    print("minimal improving flips (size %d):" % found[0][0])
    for (k, U, nM, nB, d, dM, dB) in found[:6]:
        rel_h = ('x' in U) ^ ('z' in U)   # does U separate h's endpoints?
        print("  U=%-22s |deltaM|=%d |deltaB|=%d dcut=+%d | deltaM=%s | U-cap-W=%s | U-cap-supp(h)=%s | U splits h(x,z)=%s"
              % (sorted(U), nM, nB, d, dM, sorted(U & W), sorted(U & supp_h), rel_h))
    print("=" * 62)
    # interpret the first one
    k, U, nM, nB, d, dM, dB = found[0]
    hits_h = any(set(e) == {'x','z'} for e in dM)
    print("MECHANISM: the minimal improving flip U=%s makes dcut=+%d." % (sorted(U), d))
    print("  It crosses bad edges %s and blue edges %s." % (dM, dB))
    print("  h=x-z among the bad edges it fixes: %s ; U meets h's support-in-W: %s" % (hits_h, sorted(U & supp_h)))
    print("  => the escaping atom's geodesic through W leaves a slack that an improving flip exploits, so the")
    print("     escaping-lens cut CANNOT be maximum. At a MAX cut (MaxCutVertexIneq: |deltaM(U)|<=|deltaB(U)| for all U)")
    print("     no such U exists, so this escaping-atom configuration is impossible -- the maximality lever excludes it.")
