#!/usr/bin/env python3
"""Hunt specifically for the 'cut-tight pocket': a connected-B max-cut config where peeling a
bad edge's shortest geodesic makes condition (i) CD-on-remainder FAIL (delta_M'(S) > delta_B'(S)
for some S in the keep set). This is the one peel-failure mode the fan-out NEVER reported as
binding (brooms fail via (ii), thetas/unbalanced fall short of tight). If (i) can be binding at
high ratio, that is the dangerous direction.

Strategy: scan all triangle-free connected graphs N<=13 from geng, and for each m>=2 instance
compute -- per bad edge -- which of (i)/(ii)/(iii) fails. Record graphs where for EVERY bad edge
the failure includes (i)CD (i.e. (i) is essential, not maskable by another edge), and report the
HIGHEST ratio among them. Also report the highest ratio where (i) fails for the *chosen-best* edge.
"""
import sys, subprocess
from peel_check import (gamma_of, Bconnected, maxcut_all, bdistB,
                        shortest_path_B, cut_dom, is_triangle_free)

GENG = r"E:\Projects\ErdosProblems\tools\nauty2_8_9\geng.exe"

def g6(line):
    data=[ord(c)-63 for c in line.strip()]; n=data[0]; bits=[]
    for x in data[1:]:
        for k in range(5,-1,-1): bits.append((x>>k)&1)
    adj=[set() for _ in range(n)]; idx=0
    for j in range(1,n):
        for i in range(j):
            if idx<len(bits) and bits[idx]: adj[i].add(j); adj[j].add(i)
            idx+=1
    return n,adj

def best_side(n,adj):
    mc,cuts=maxcut_all(n,adj)
    best=None
    for sd in cuts:
        if not Bconnected(n,adj,sd): continue
        G,M=gamma_of(n,adj,sd)
        if G is None: continue
        if best is None or G<best[0]: best=(G,M,sd)
    return best

def peel_failmodes(n,adj,side,G,M):
    """For each bad edge, return set of failing conditions among {i,ii,iii} (empty=safe)."""
    modes=[]
    for (u,v) in M:
        P=shortest_path_B(n,adj,side,u,v)
        if P is None: modes.append(("noP",None)); continue
        C=set(P); s=len(C); keep=[x for x in range(n) if x not in C]
        if not keep: modes.append(("all",None)); continue
        Mp=[(a,b) for (a,b) in M if a in keep and b in keep]
        Gp=0; conn_ok=True
        for (a,b) in Mp:
            d=bdistB(n,adj,side,a,banned=C).get(b,-1)
            if d<0: conn_ok=False; break
            Gp+=(d+1)**2
        f=set()
        if not conn_ok:
            f.add("ii")
        else:
            L=G-Gp; bound=2*s*n-s*s
            if L>bound: f.add("iii")
            cd=cut_dom(keep,n,adj,side,Mp)
            if cd is False: f.add("i")
            elif cd is None: f.add("keep>22")
        modes.append((tuple(sorted(f)) if f else "SAFE", (u,v,P)))
    return modes

def scan(N, res, mod, ratio_gate=0.50):
    p=subprocess.Popen([GENG,"-tcq",str(N),f"{res}/{mod}"],stdout=subprocess.PIPE,text=True)
    best_i_binding=(-1.0,None)      # highest ratio where chosen-best edge's only path fails incl (i)
    best_all_i=(-1.0,None)          # highest ratio where EVERY edge's failure set contains 'i'
    cnt_i_appears=0; total=0
    for line in p.stdout:
        line=line.strip()
        if not line: continue
        n,adj=g6(line)
        b=best_side(n,adj)
        if b is None: continue
        G,M,sd=b
        if len(M)<2: continue
        ratio=G/(n*n)
        if ratio<ratio_gate: continue
        total+=1
        modes=peel_failmodes(n,adj,sd,G,M)
        # is there ANY safe edge? if yes not interesting for obstruction
        any_safe=any(m[0]=="SAFE" for m in modes)
        # does 'i' appear in any failure?
        i_in_any=any(isinstance(m[0],tuple) and "i" in m[0] for m in modes)
        if i_in_any: cnt_i_appears+=1
        # EVERY edge fails AND every failure set contains 'i' (i is unavoidable)
        all_fail_with_i = (not any_safe) and all(
            (isinstance(m[0],tuple) and "i" in m[0]) for m in modes)
        if all_fail_with_i and ratio>best_all_i[0]:
            best_all_i=(ratio,(line,n,len(M),G,n*n))
        # no safe peel at all (obstruction-shaped) regardless of mode
        if not any_safe and ratio>best_i_binding[0]:
            best_i_binding=(ratio,(line,n,len(M),G,n*n, [m[0] for m in modes]))
    p.wait()
    return total, cnt_i_appears, best_i_binding, best_all_i

if __name__=="__main__":
    N=int(sys.argv[1]); res=int(sys.argv[2]); mod=int(sys.argv[3])
    gate=float(sys.argv[4]) if len(sys.argv)>4 else 0.50
    t,ci,bi,ba=scan(N,res,mod,gate)
    print(f"N={N} shard {res}/{mod} gate>={gate}: m>=2&ratio>=gate checked={t}; "
          f"#with (i) appearing anywhere={ci}")
    print(f"  highest-ratio NO-SAFE-PEEL: {bi[0]:.4f} {bi[1]}")
    print(f"  highest-ratio EVERY-edge-fails-WITH-(i): {ba[0]:.4f} {ba[1]}")
