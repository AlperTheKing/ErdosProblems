#!/usr/bin/env python3
"""Stress-test GPT-Pro's variational 'cut-pressure rigidity' premise for delta=0 (#23).

For a triangle-free graph G (vertex = graphon atom of measure 1/N):
  beta = e - maxcut;  d_mono = 2 beta / N^2;  d_edge = 2 e / N^2.
  P(i,j)  = Pr[i,j same side] over ALL maximum cuts          (cut-pressure kernel)
  C_W(i,j)= |N(i) cap N(j)| / N                              (common-neighbour kernel)
GPT's rigidity premise: a high-d_mono (>=2/25) critical graphon has P = 1/5 + 2 C_W and is C5-type
(=> d_edge >= 2/5). PREDICTION: P=1/5+2C_W holds for C5-type (C5, C5[2]) and FAILS for non-C5;
and every IN-BAND graph has d_mono < 2/25 (slack). We also fit P = a + b*C_W to see if a non-C5
graph is even 'stationary-compatible' (collinear (C_W,P) cloud).
"""
import itertools, numpy as np

def maxcut_and_optcuts(N, edges):
    best=-1; opt=[]
    E=edges
    for mask in range(1<<N):
        side=[(mask>>i)&1 for i in range(N)]
        c=sum(1 for a,b in E if side[a]!=side[b])
        if c>best: best=c; opt=[mask]
        elif c==best: opt.append(mask)
    return best, opt

def kernels(N, edges, opt):
    adj=[set() for _ in range(N)]
    for a,b in edges: adj[a].add(b); adj[b].add(a)
    P=np.zeros((N,N)); C=np.zeros((N,N))
    for i in range(N):
        for j in range(N):
            same=sum(1 for m in opt if ((m>>i)&1)==((m>>j)&1))
            P[i,j]=same/len(opt)
            C[i,j]=len(adj[i]&adj[j])/N
    return P,C

def has_triangle(N,edges):
    adj=[set() for _ in range(N)]
    for a,b in edges: adj[a].add(b); adj[b].add(a)
    return any(adj[a]&adj[b] for a,b in edges)

def cyc(n): return n,[(i,(i+1)%n) for i in range(n)]
def blowupC5(t):
    N=5*t; E=[]
    for i in range(5):
        for a in range(t):
            for b in range(t):
                E.append((i*t+a, ((i+1)%5)*t+b))
    return N,E
def petersen():
    out=[(i,(i+1)%5) for i in range(5)]; inn=[(5+i,5+((i+2)%5)) for i in range(5)]
    return 10, out+inn+[(i,5+i) for i in range(5)]
def grotzsch():
    E=[(i,(i+1)%5) for i in range(5)]
    for i in range(5): E+=[(5+i,(i-1)%5),(5+i,(i+1)%5)]
    for i in range(5): E.append((10,5+i))
    return 11,E

graphs=[("C5",*cyc(5)),("C5[2]",*blowupC5(2)),("C7",*cyc(7)),("C9",*cyc(9)),
        ("Petersen",*petersen()),("Grotzsch",*grotzsch())]
TWO25=2/25
print(f"{'graph':10} {'N':>3} {'e':>3} {'beta':>4} {'d_mono':>7} {'d_edge':>7} {'band?':>6} "
      f"{'maxdev(P-1/5-2C)':>16} {'fit P=a+bC resid':>16} {'(a,b)':>14}")
for name,N,E in graphs:
    assert not has_triangle(N,E), name
    mc,opt=maxcut_and_optcuts(N,E); beta=len(E)-mc
    dmono=2*beta/N**2; dedge=2*len(E)/N**2
    P,C=kernels(N,E,opt)
    pf=P[np.triu_indices(N,1)]; cf=C[np.triu_indices(N,1)]
    dev=float(np.max(np.abs(pf-(0.2+2*cf))))
    # least-squares fit P = a + b C
    A=np.vstack([np.ones_like(cf),cf]).T
    coef,res,_,_=np.linalg.lstsq(A,pf,rcond=None)
    resid=float(np.sqrt(np.mean((A@coef-pf)**2)))
    inband = 0.2486<=dedge<=0.3197
    print(f"{name:10} {N:3d} {len(E):3d} {beta:4.0f} {dmono:7.4f} {dedge:7.4f} {str(inband):>6} "
          f"{dev:16.4f} {resid:16.4f}   ({coef[0]:.3f},{coef[1]:.3f})")
print()
print("Read: C5/C5[2] should have maxdev=0 (P=1/5+2C exact). In-band rows (band?=True) should have")
print("d_mono < 2/25 = 0.0800 (slack) AND maxdev>0 (P=1/5+2C fails => rigidity is C5-exclusive).")
