# LEMMA C3 stress test: apply the claimed <=15-vertex recipe VERBATIM to every
# vertex x satisfying the STATED cleanliness hypothesis, in K68 (pg_s1) and
# K318 (gq_s1); check the produced colouring is proper on K-x with (2,2,2) trace.
# Two readings of "pad-target":
#   strict  = bulk endpoint of a pad edge only (x itself MAY be a pad-target)
#   loose   = additionally require x not a pad-target
import json, sys
from collections import deque, Counter

def run(path):
    d = json.load(open(path)); inst = d['inst']; n = inst['n']
    E = {(min(int(a),int(b)), max(int(a),int(b))) for a, b in inst['edges']}
    adj = [set() for _ in range(n)]
    for a, b in E: adj[a].add(b); adj[b].add(a)
    g = inst['gadget']; gv = set(g.values())
    nb = inst['nb']
    side1 = set(inst['side1'])
    side2 = set(range(nb)) - side1
    padt = {int(b) for a, b in inst['pads']}            # bulk endpoints of pads
    padt_UT = {int(b) for a, b in inst['pads'] if int(a) in (g['U'], g['T'])}
    # phi0 (0-indexed colours): side1->0, side2->1, gadget (A,B,U,T,V,W)->(0,1,2,2,0,1)
    phi0 = [None]*n
    for v in range(nb): phi0[v] = 0 if v in side1 else 1
    for k, c in {'A':0,'B':1,'U':2,'T':2,'V':0,'W':1}.items(): phi0[g[k]] = c
    assert all(phi0[a] != phi0[b] for a, b in E), "phi0 improper?!"

    def ball2(x):
        b = set(adj[x])
        for y in adj[x]: b |= adj[y]
        b.discard(x)
        return b

    results = {'strict': [0,0,[]], 'loose': [0,0,[]]}
    deg = [len(adj[v]) for v in range(n)]
    for x in range(nb):
        if deg[x] != 6: continue
        clean_strict = (not (set(adj[x]) & padt)) and (not (ball2(x) & padt_UT))
        clean_loose = clean_strict and (x not in padt)
        if not clean_strict: continue
        # apply recipe verbatim
        ys = sorted(adj[x])
        ok, why = apply_recipe(x, ys, n, E, adj, side1, side2, gv, phi0)
        for mode, clean in (('strict', clean_strict), ('loose', clean_loose)):
            if clean:
                results[mode][0] += 1
                if ok: results[mode][1] += 1
                else: results[mode][2].append((x, why, 'x_is_padtarget' if x in padt else ''))
    for mode in ('strict', 'loose'):
        tot, okc, fails = results[mode]
        print(f"{path} [{mode}]: clean x = {tot}, recipe succeeded = {okc}, failed = {len(fails)}")
        if fails: print("   failures:", fails[:8])

def apply_recipe(x, ys, n, E, adj, side1, side2, gv, phi0):
    if any(y in gv for y in ys):
        return False, "N(x) contains a gadget vertex (recipe side assumption broken)"
    cs = 0 if x in side1 else 1     # colour of x's side
    co = 1 - cs                     # opposite side colour
    col = list(phi0)
    y1, y2, y3, y4, y5, y6 = ys
    col[y1] = 2; col[y2] = 2
    col[y3] = cs; col[y4] = cs
    for z in (adj[y3] | adj[y4]) - {x}:
        col[z] = 2
    # check properness on K - x and trace
    for a, b in E:
        if a == x or b == x: continue
        if col[a] == col[b]:
            return False, f"improper edge ({a},{b}) both colour {col[a]}"
    tr = Counter(col[y] for y in ys)
    if any(tr[c] != 2 for c in (0,1,2)):
        return False, f"trace {dict(tr)}"
    return True, ""

if __name__ == '__main__':
    for p in sys.argv[1:]:
        run(p)
