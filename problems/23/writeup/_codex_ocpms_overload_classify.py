import subprocess
from collections import Counter, defaultdict, deque
from fractions import Fraction as F
from _h import dec, GENG, Bconn
from _stark1 import gmins
from _satzmu_conn import struct_for_side
from _codex_ocpms_gate import kcomp


def bdist(n,B,src):
    adj=[set() for _ in range(n)]
    for a,b in B:
        adj[a].add(b); adj[b].add(a)
    d=[None]*n; d[src]=0; q=deque([src])
    while q:
        u=q.popleft()
        for v in adj[u]:
            if d[v] is None:
                d[v]=d[u]+1; q.append(v)
    return d

rows=[]
for g6 in subprocess.run([GENG,'-tc','10'],capture_output=True,text=True).stdout.split():
    n,E=dec(g6)
    adj=[set() for _ in range(n)]
    for a,b in E:
        adj[a].add(b); adj[b].add(a)
    try:
        _,cuts=gmins(n,E)
    except Exception:
        continue
    for side in cuts:
        if not Bconn(n,adj,side): continue
        st=struct_for_side(n,adj,side)
        if st is None: continue
        M,ell,T,cyc=st[0],st[1],st[2],st[4]
        if not M: continue
        B=[e for e in E if side[e[0]]!=side[e[1]]]
        for f in M:
            L=ell[f]
            for P in cyc[f]:
                R=sum(T[v] for v in P)
                if R<=L*n: continue
                C=kcomp(n,M,cyc,set(P))
                Pset=set(P)
                I=sum(F(1,len(cyc[g]))*sum(len(Pset & set(Q)) for Q in cyc[g]) for g in M)
                Def=n*n-25*len(M)
                margin=F(2)*Def-75*(I-n)
                d0=bdist(n,B,P[0]); d4=bdist(n,B,P[-1])
                interval={v for v in range(n) if d0[v] is not None and d4[v] is not None and d0[v]+d4[v]==L-1}
                on=[]; off=[]
                for g in M:
                    if set(g)<=interval:
                        on.append(g)
                    else:
                        off.append(g)
                contribs=[]
                for g in M:
                    cg=F(1,len(cyc[g]))*sum(len(Pset & set(Q)) for Q in cyc[g])
                    contribs.append((g,cg,'on' if set(g)<=interval else 'off'))
                rows.append((g6,''.join(map(str,side)),f,tuple(P),margin,I,Def,tuple(M),tuple(on),tuple(off),tuple(contribs)))

print('over_rows',len(rows))
print('graphs',Counter(r[0] for r in rows))
print('margins',Counter(str(r[4]) for r in rows))
print('I',Counter(str(r[5]) for r in rows))
print('off_count',Counter(len(r[9]) for r in rows))
for r in sorted(rows, key=lambda x:(x[4],x[0],x[1],x[3])):
    print('ROW g6=%s side=%s f=%s P=%s margin=%s I=%s M=%s on=%s off=%s contrib=%s' % (r[0],r[1],r[2],r[3],r[4],r[5],r[7],r[8],r[9],r[10]))
