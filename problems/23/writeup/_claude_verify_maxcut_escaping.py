r"""DECISIVE falsifier-first verification of GPT-Pro's 11-vertex counterpattern (2026-07-09): an escaping atom at a
GENUINE MAXIMUM cut (refuting NoEscapingAtomAtMaxCut). Checks ALL claims exactly: triangle-free; the given cut is
MAXIMUM (brute force 2^11); all three bad edges e=p-y, f=q-w, h=p-q have ell=5; W={a,b,b',c,y,w} has door signature
deltaB(W)={p-a,q-c}, deltaM(W)={p-y,q-w}; h=p-q is ESCAPING (endpoints p,q outside W, geodesic p-a-b-c-q through W);
Gamma-minimal (every max cut has >=3 bad edges => Gamma>=75). If all pass, the direct-maximality path is REFUTED.
EXACT integer. Run from problems/23/writeup."""
from itertools import product
from collections import deque

V = ['p','q','a','b','bb','c','y','w','r1','r2','r3']   # bb = b'
idx = {v: i for i, v in enumerate(V)}
given = {v: 0 for v in ['p','q','b','bb','y','w','r2']}   # Red = 0
for v in ['a','c','r1','r3']:
    given[v] = 1                                          # Blue = 1
B = [('p','a'),('a','b'),('b','c'),('c','y'),('q','c'),('c','bb'),('bb','a'),('a','w'),
     ('p','r1'),('r1','r2'),('r2','r3'),('r3','q')]
M = [('p','y'),('q','w'),('p','q')]   # e, f, h
E = B + M
n = len(V)
adjB = {v:set() for v in V}
for u,w in B: adjB[u].add(w); adjB[w].add(u)
adjAll = {v:set() for v in V}
for u,w in E: adjAll[u].add(w); adjAll[w].add(u)

def blue_dist(s,t):
    d={s:0}; q=deque([s])
    while q:
        u=q.popleft()
        for w in adjB[u]:
            if w not in d: d[w]=d[u]+1; q.append(w)
    return d.get(t)
def geo_vertices(s,t):
    ds={s:0}; q=deque([s])
    while q:
        u=q.popleft()
        for w in adjB[u]:
            if w not in ds: ds[w]=ds[u]+1; q.append(w)
    D=ds.get(t)
    if D is None: return set()
    dt={t:0}; q=deque([t])
    while q:
        u=q.popleft()
        for w in adjB[u]:
            if w not in dt: dt[w]=dt[u]+1; q.append(w)
    return {v for v in V if ds.get(v) is not None and dt.get(v) is not None and ds[v]+dt[v]==D}

print("=== VERIFY GPT-Pro 11-vtx escaping-atom-at-max-cut counterpattern ===")
# 1 bichromatic B under given cut
b_ok = all(given[u]!=given[w] for u,w in B)
print("1. B bichromatic (proper cut):", b_ok)
# 2 triangle-free
tri=[]
for i in range(n):
    for j in range(i+1,n):
        for k in range(j+1,n):
            x1,y1,z1=V[i],V[j],V[k]
            if y1 in adjAll[x1] and z1 in adjAll[x1] and z1 in adjAll[y1]: tri.append((x1,y1,z1))
print("2. triangle-free:", len(tri)==0, tri if tri else "")
# 3 bad edges monochromatic + ell
print("3. bad edges (mono, ell):")
ells={}
for (u,w) in M:
    mono=given[u]==given[w]; d=blue_dist(u,w); ells[(u,w)]=(None if d is None else d+1)
    print("   %s-%s mono=%s ell=%s"%(u,w,mono,ells[(u,w)]))
# 4 cut is MAXIMUM (brute force)
def cut_size(bits): return sum(1 for (u,w) in E if bits[idx[u]]!=bits[idx[w]])
gvec=tuple(given[v] for v in V)
gcut=cut_size(gvec)
best=-1; nmax=0; minbad=99
for bits in product((0,1),repeat=n):
    c=cut_size(bits)
    if c>best: best=c; nmax=1
    elif c==best: nmax+=1
for bits in product((0,1),repeat=n):
    if cut_size(bits)==best: minbad=min(minbad, len(E)-best)
print("4. given cut size=%d ; TRUE max cut=%d ; #maxcuts=%d ; is-given-max=%s"%(gcut,best,nmax,gcut==best))
gamma_maxcut = (len(E)-best)   # beta at max cut = #bad edges
print("   beta at max cut = |E|-maxcut = %d (Gamma-min = %d*25 = %d if all ell5)"%(gamma_maxcut, gamma_maxcut, gamma_maxcut*25))
# 5 door signature of W
W={'a','b','bb','c','y','w'}
def crossing(edges): return sorted([tuple(sorted((u,w))) for (u,w) in edges if (u in W)!=(w in W)])
dB=crossing(B); dM=crossing(M)
print("5. W=%s"%sorted(W))
print("   deltaB(W)=%s (want p-a,q-c)"%dB)
print("   deltaM(W)=%s (want p-y,q-w)"%dM)
# 6 h escaping
gh=geo_vertices('p','q')
h_out = ('p' not in W) and ('q' not in W)
print("6. h=p-q geodesic-support=%s ; endpoints outside W=%s ; support-cap-W=%s"%(sorted(gh),h_out,sorted(gh & W)))
escaping = h_out and len(gh & W)>0
print("   => h ESCAPING:", escaping)
print("="*64)
all_ell5 = all(ells[m]==5 for m in M)
is_max = (gcut==best)
ok_dB = set(map(frozenset,dB))=={frozenset(('p','a')),frozenset(('c','q'))}
ok_dM = set(map(frozenset,dM))=={frozenset(('p','y')),frozenset(('q','w'))}
verdict = (len(tri)==0 and all_ell5 and is_max and ok_dB and ok_dM and escaping)
print("VERDICT: tri-free=%s all-ell5=%s cut-is-MAX=%s doorB=%s doorM=%s h-escaping=%s"%(len(tri)==0,all_ell5,is_max,ok_dB,ok_dM,escaping))
if verdict:
    print("CONFIRMED: escaping atom h=p-q survives at a GENUINE MAXIMUM cut (beta=%d, Gamma=%d, N=%d, N^2=%d => NON-deficient)."%(gamma_maxcut,gamma_maxcut*25,n,n*n))
    print("=> NoEscapingAtomAtMaxCut is FALSE. The direct-maximality path is REFUTED. The crux remains the full-bank")
    print("   Hall/absorption theorem for the FULL escape closure (GPT-Pro EscapingClosureDichotomy, full branch).")
else:
    print("MISMATCH -- GPT-Pro's counterpattern does NOT check out; the direct-maximality path may still be viable. Re-examine.")
