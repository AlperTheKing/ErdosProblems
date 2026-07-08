r"""Cross-check the 'no real counter-pattern' claim on GPT-Pro's explicit 14-vertex escaping-atom pattern.
Both channels concluded every escaping-atom / demand-excess attempt is a NON-maximum cut (whose true max cut removes a
bad edge and collapses it to something reducible). Here we brute-force the TRUE max cut of GPT-Pro's 14-vertex graph and
compare to the GIVEN cut (which has 3 bad edges e=x-y, f=z-w, h=x-z). If the given cut is NOT maximum, that confirms the
pattern is not a genuine max-cut obstruction (consistent with GPT-Pro's 'not a deficient minimal cage' + the workflow's
'non-maximum cut collapse'). EXACT integer brute force over all 2^14 sides. Run from problems/23/writeup."""
from itertools import product

V = ['x','z','y','w','a','b','c','r1','r2','r3','r4','r5','r6','r7']
idx = {v: i for i, v in enumerate(V)}
given = {v: 0 for v in ['x','z','y','w','b','r2','r4','r6']}
for v in ['a','c','r1','r3','r5','r7']:
    given[v] = 1
# ALL edges of the host graph = blue cut edges + bad edges (the host is B ∪ M)
Bedges = [('x','a'),('a','b'),('b','c'),('c','y'),('z','c'),('a','w'),
          ('x','r1'),('r1','r2'),('r2','r3'),('r3','r4'),('r4','r5'),('r5','r6'),('r6','r7'),('r7','z')]
Medges = [('x','y'),('z','w'),('x','z')]
E = Bedges + Medges
n = len(V)

def cut_size(side):
    return sum(1 for (u, w) in E if side[idx[u]] != side[idx[w]])

def bad_count(side):
    # bad edges = monochromatic edges of the host under THIS side assignment (all of E that are same-side)
    return sum(1 for (u, w) in E if side[idx[u]] == side[idx[w]])

given_vec = tuple(given[v] for v in V)
given_cut = cut_size(given_vec)
given_bad = bad_count(given_vec)

best_cut = -1
best_assign = None
for bits in product((0, 1), repeat=n):
    c = cut_size(bits)
    if c > best_cut:
        best_cut = c; best_assign = bits

# among all TRUE max cuts, the minimum #bad edges
maxcut_bad = min(bad_count(bits) for bits in product((0,1), repeat=n) if cut_size(bits) == best_cut)

print("=== max-cut cross-check of GPT-Pro's 14-vertex escaping-atom pattern ===")
print("total host edges |E| =", len(E), "(", len(Bedges), "blue +", len(Medges), "bad given)")
print("GIVEN cut: size =", given_cut, " bad(monochromatic) edges =", given_bad)
print("TRUE MAX cut: size =", best_cut, " -> beta(maxcut) = |E| - maxcut =", len(E) - best_cut)
print("min #bad-edges over all max cuts =", maxcut_bad)
print("=" * 62)
if given_cut < best_cut:
    print("CONFIRMED: the GIVEN cut (with the 3-bad-edge escaping-lens structure) is NOT a maximum cut")
    print("(given cut %d < true max cut %d). So the escaping-atom pattern is a NON-maximum cut; its true max" % (given_cut, best_cut))
    print("cut has beta=%d < 3, removing bad edges and collapsing the obstruction. This is exactly the workflow's" % (len(E)-best_cut))
    print("'every counter-attempt is a non-max-cut' finding and GPT-Pro's 'not a deficient minimal cage' -- the")
    print("pattern proves local geometry is insufficient but is NOT a genuine max-cut counterexample.")
elif given_cut == best_cut:
    print("NOTE: the given cut IS a maximum cut (beta = %d)." % (len(E) - best_cut))
    print("Then the escaping-atom structure survives at a genuine max cut -- examine whether it is Gamma-minimal")
    print("and whether it forms a reducible base leaf; if it survives ALL reductions it would be significant.")
else:
    print("IMPOSSIBLE (given > max) -- bug.")
