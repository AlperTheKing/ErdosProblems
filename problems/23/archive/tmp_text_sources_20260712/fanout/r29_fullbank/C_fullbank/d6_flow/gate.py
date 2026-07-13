#!/usr/bin/env python3
"""Exact finite FullBank allocation gate (integer max-flow; no floats)."""
import argparse, hashlib, json, math
from collections import deque
from fractions import Fraction
from pathlib import Path

KINDS = {"door", "vertexSlack", "c5Base", "prune"}

def Q(x):
    if isinstance(x, int): return Fraction(x)
    if not isinstance(x, str): raise ValueError("rationals must be JSON integers or strings")
    return Fraction(x)

def qs(x): return str(x.numerator) if x.denominator == 1 else f"{x.numerator}/{x.denominator}"
def lcm(a,b): return abs(a*b)//math.gcd(a,b)

def add(g,u,v,c):
    g[u].append([v,c,len(g[v])]); g[v].append([u,0,len(g[u])-1])

def maxflow(g,s,t):
    total=0
    while True:
        level=[-1]*len(g); level[s]=0; q=deque([s])
        while q:
            u=q.popleft()
            for v,c,_ in g[u]:
                if c and level[v]<0: level[v]=level[u]+1; q.append(v)
        if level[t]<0: return total
        it=[0]*len(g)
        def dfs(u,f):
            if u==t:return f
            while it[u]<len(g[u]):
                e=g[u][it[u]]; v,c,r=e
                if c and level[v]==level[u]+1:
                    z=dfs(v,min(f,c))
                    if z: e[1]-=z; g[v][r][1]+=z; return z
                it[u]+=1
            return 0
        while (z:=dfs(s,10**100)): total+=z

def run(data):
    errors=[]; locals_=data.get("locals",[]); tokens=data.get("tokens",[])
    root=Path(__file__).resolve().parents[5]
    for name,a in data.get("canonicalArtifacts",{}).items():
        try:
            p=root/a["path"]; actual=hashlib.sha256(p.read_bytes()).hexdigest()
            if actual.lower()!=a["sha256"].lower(): errors.append(f"canonical artifact hash mismatch: {name}")
        except (KeyError,OSError) as e: errors.append(f"canonical artifact unreadable: {name}: {e}")
    lids=[x.get("id") for x in locals_]; tids=[x.get("id") for x in tokens]
    if len(set(lids))!=len(lids): errors.append("duplicate local id")
    if len(set(tids))!=len(tids): errors.append("duplicate token id")
    keys=[]
    for x in tokens:
        if x.get("kind") not in KINDS: errors.append(f"bad kind: {x.get('kind')}")
        keys.append((x.get("component"),x.get("kind"),x.get("source")))
        if not x.get("provider",{}).get("assumed",False): errors.append(f"token {x.get('id')} capacity lacks explicit provider assumption")
    if len(set(keys))!=len(keys): errors.append("duplicate (component,kind,source) token")
    try:
        demands=[Q(x["demandQ"]) for x in locals_]; caps=[Q(x["capacityQ"]) for x in tokens]
    except (KeyError,ValueError,ZeroDivisionError) as e: errors.append(str(e)); demands=[]; caps=[]
    if any(x<0 for x in demands+caps): errors.append("negative demand or capacity")
    allowed=[]
    for i,L in enumerate(locals_):
        row=[]
        for j,T in enumerate(tokens):
            # Component equality is mandatory; reach/provider incidence may only remove arcs.
            if L.get("component")==T.get("component") and T.get("id") in L.get("allowedTokens",[]): row.append(j)
        allowed.append(row)
    if errors: return {"schema":"r29_fullbank_exact_flow_output_v1","status":"INVALID","errors":errors}
    scale=1
    for x in demands+caps: scale=lcm(scale,x.denominator)
    D=[int(x*scale) for x in demands]; C=[int(x*scale) for x in caps]
    nL=len(D); nT=len(C); s=0; lo=1; to=lo+nL; sink=to+nT; g=[[] for _ in range(sink+1)]
    for i,d in enumerate(D): add(g,s,lo+i,d)
    edgepos={}
    INF=sum(D)
    for i,js in enumerate(allowed):
        for j in js: edgepos[i,j]=len(g[lo+i]); add(g,lo+i,to+j,INF)
    for j,c in enumerate(C): add(g,to+j,sink,c)
    value=maxflow(g,s,sink); alloc=[]
    for (i,j),p in edgepos.items():
        used=g[to+j][g[lo+i][p][2]][1]
        if used: alloc.append({"local":lids[i],"token":tids[j],"spendQ":qs(Fraction(used,scale))})
    unmet=[]
    got={x:0 for x in lids}
    for a in alloc: got[a["local"]]+=Q(a["spendQ"])
    for i,x in enumerate(lids):
        if got[x]<demands[i]: unmet.append({"local":x,"unmetQ":qs(demands[i]-got[x])})
    return {"schema":"r29_fullbank_exact_flow_output_v1","status":"FEASIBLE" if value==sum(D) else "INFEASIBLE",
      "arithmetic":{"method":"Dinic on denominator-LCM-scaled integers","scale":scale},
      "totalDemandQ":qs(sum(demands,Fraction())),"maxFlowQ":qs(Fraction(value,scale)),
      "allocation":alloc,"unmet":unmet,"checks":{"tokenKeyUnique":True,"tokenCapacityGlobal":True,
      "noCrossComponentSpend":True,"noDoubleSpendGlobally":True,"demandCoveredBySolvedFlow":value==sum(D)}}

if __name__=="__main__":
    ap=argparse.ArgumentParser(); ap.add_argument("input",nargs="?",default="input.json"); ap.add_argument("-o","--output",default="output.json"); a=ap.parse_args()
    d=json.loads(Path(a.input).read_text(encoding="utf-8")); out=run(d)
    out["inputSha256"]=hashlib.sha256(Path(a.input).read_bytes()).hexdigest()
    Path(a.output).write_text(json.dumps(out,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print(json.dumps(out,sort_keys=True))
