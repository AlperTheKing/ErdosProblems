"""Collect ALL local-obstruction witnesses for m=9..12 and compute structure stats:
max edge multiplicity, #edges with mult=m (universal waist edges), whether a 2-edge cut
of F is crossed by every atom's support, and mQ<=T^2 status (expected: all witnesses fail it).
"""
import subprocess, json
from collections import deque
from multiprocessing import Pool
from d3_local_obstruction import parse_g6, bfs, GENG

def all_witnesses_for_F(g6, m):
    n, adj, edges = parse_g6(g6)
    e = len(edges)
    assert e == m - 1
    eidx = {}
    for k,(i,j) in enumerate(edges):
        eidx[(i,j)] = k; eidx[(j,i)] = k
    dist = [bfs(adj,n,s) for s in range(n)]
    pairs = []
    for u in range(n):
        for v in range(u+1,n):
            if dist[u][v]==4:
                du,dv=dist[u],dist[v]
                sup=0
                for (x,y) in edges:
                    if du[x]+1+dv[y]==4 or du[y]+1+dv[x]==4:
                        sup |= 1<<eidx[(x,y)]
                pairs.append(((u,v),sup))
    if len(pairs) < m: return []
    full=(1<<e)-1
    res=[]
    P=len(pairs)
    # DFS all solutions (bounded; these F are tiny)
    sols=[]
    mult=[0]*e
    nb={}
    chosen=[]
    def dfs(i, need):
        if need==0:
            if all(x>=2 for x in mult):
                sols.append(list(chosen))
            return
        if P-i<need: return
        (u,v),s = pairs[i]
        if not (nb.get(u,set()) & nb.get(v,set())):
            nb.setdefault(u,set()).add(v); nb.setdefault(v,set()).add(u)
            b=s
            while b:
                c=(b&-b).bit_length()-1; mult[c]+=1; b&=b-1
            chosen.append(i)
            dfs(i+1,need-1)
            chosen.pop()
            b=s
            while b:
                c=(b&-b).bit_length()-1; mult[c]-=1; b&=b-1
            nb[u].discard(v); nb[v].discard(u)
        dfs(i+1,need)
    dfs(0,m)
    out=[]
    for sol in sols:
        sups=[pairs[i][1] for i in sol]
        atoms=[pairs[i][0] for i in sol]
        # stats
        mults=[sum(1 for s in sups if (s>>c)&1) for c in range(e)]
        T=sum(bin(s).count('1') for s in sups)
        Q=sum(x*x for x in mults)
        out.append({"g6":g6,"atoms":atoms,"maxmult":max(mults),
                    "n_full_edges":sum(1 for x in mults if x==m),
                    "mQ_le_T2": m*Q <= T*T, "m":m,"T":T,"Q":Q})
    return out

def worker(args):
    return all_witnesses_for_F(*args)

if __name__=="__main__":
    for m in (9,10,11,12):
        e=m-1
        lines=[]
        for n in range(5,e+2):
            p=subprocess.run([GENG,"-q","-c","-b",str(n),f"{e}:{e}"],capture_output=True,text=True)
            lines += [l for l in p.stdout.splitlines() if l.strip()]
        allw=[]
        with Pool(16) as pool:
            for w in pool.imap_unordered(worker,[(l,m) for l in lines],chunksize=8):
                allw += w
        if not allw:
            print(f"m={m}: no witnesses"); continue
        maxmults=[w["maxmult"] for w in allw]
        fulls=[w["n_full_edges"] for w in allw]
        mq=[w["mQ_le_T2"] for w in allw]
        print(f"m={m}: total witness atom-sets={len(allw)} over {len(set(w['g6'] for w in allw))} F-graphs; "
              f"min(maxmult)={min(maxmults)} max(maxmult)={max(maxmults)}; "
              f"witnesses with an all-atoms edge (mult=m): {sum(1 for x in fulls if x>0)}/{len(allw)}; "
              f"mQ<=T2 holds in {sum(mq)}/{len(allw)} (expect 0)", flush=True)
        # show a witness with the SMALLEST max multiplicity (most spread = hardest to kill by waist arguments)
        wmin=min(allw,key=lambda w:w["maxmult"])
        print("   most-spread witness:",wmin, flush=True)
