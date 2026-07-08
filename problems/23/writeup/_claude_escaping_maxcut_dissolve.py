r"""Confirm the escaping-lens structure DISSOLVES at the true max cut of GPT-Pro's 14-vtx pattern.
The given (escaping-lens) cut has 3 same-side bad edges {e=x-y, f=z-w, h=x-z}. The true max cut has beta=2. Show WHICH
bad edge becomes bichromatic (a cut edge) under a true max cut -- i.e. the escaping atom / lens is broken by maximality.
Reliable, exact, small. Run from problems/23/writeup."""
from itertools import product

V = ['x','z','y','w','a','b','c','r1','r2','r3','r4','r5','r6','r7']
idx = {v: i for i, v in enumerate(V)}
Bedges = [('x','a'),('a','b'),('b','c'),('c','y'),('z','c'),('a','w'),
          ('x','r1'),('r1','r2'),('r2','r3'),('r3','r4'),('r4','r5'),('r5','r6'),('r6','r7'),('r7','z')]
Medges = [('x','y'),('z','w'),('x','z')]   # e,f,h
E = Bedges + Medges
n = len(V)
names = {('x','y'):'e=x-y', ('z','w'):'f=z-w', ('x','z'):'h=x-z (escaping atom)'}

def cut_size(s):  return sum(1 for (u,w) in E if s[idx[u]] != s[idx[w]])
def bad_edges(s): return [(u,w) for (u,w) in E if s[idx[u]] == s[idx[w]]]

best = -1; maxcuts = []
for bits in product((0,1), repeat=n):
    c = cut_size(bits)
    if c > best:
        best = c; maxcuts = [bits]
    elif c == best:
        maxcuts.append(bits)

given = tuple((1 if v in ['a','c','r1','r3','r5','r7'] else 0) for v in V)
print("=== escaping structure dissolves at max cut (GPT-Pro 14-vtx) ===")
print("GIVEN escaping-lens cut: size %d, bad edges = %s" % (cut_size(given), [names.get(e,e) for e in bad_edges(given)]))
print("TRUE max cut size = %d ; number of distinct max cuts = %d" % (best, len(maxcuts)))
# among max cuts, which of {e,f,h} can stay bad?
stays_bad = {e: False for e in Medges}
for s in maxcuts:
    bad = set(bad_edges(s))
    for e in Medges:
        if e in bad:
            stays_bad[e] = True
print("At the true MAX cut(s), can each given bad edge remain bad (same-side)?")
for e in Medges:
    print("  %-24s stays-bad-at-some-maxcut = %s" % (names[e], stays_bad[e]))
# show one representative max cut's bad edges
rep = maxcuts[0]
print("Representative max cut bad edges: %s" % [names.get(e,e) for e in bad_edges(rep)])
print("=" * 60)
h = ('x','z')
if not stays_bad[h]:
    print("CONFIRMED: the ESCAPING ATOM h=x-z is NEVER a bad edge at any maximum cut -- maximality turns it into a cut")
    print("edge, so the balanced-neutral escaping lens CANNOT exist at a max cut of this graph. This is the maximality")
    print("mechanism in concrete form: the escaping-atom configuration is a strictly-sub-maximal artifact.")
else:
    print("NOTE: h can remain bad at some max cut -- the escaping atom may survive maximality here; examine the lens.")
