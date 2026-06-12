import re
lines=[l.strip() for l in open("sixreg_n11.out") if l.strip().startswith("[(")]
print("parsed graphs:",len(lines))
graphs=[]
for l in lines:
    es=re.findall(r"\((\d+),(\d+)\)",l)
    graphs.append([(int(a),int(b)) for a,b in es])
print("edge counts ok:", all(len(g)==33 for g in graphs))
N=11
def col3(adj, rmv=None, rme=None):
    order=[v for v in range(N) if v!=rmv]
    color={}
    def bt(i):
        if i==len(order): return True
        v=order[i]
        for c in range(3):
            ok=True
            for u in order[:i]:
                e=(min(u,v),max(u,v))
                if e in adj and color[u]==c:
                    if rme and e==rme: continue
                    ok=False; break
            if ok:
                color[v]=c
                if bt(i+1): return True
                del color[v]
        return False
    return bt(0)
res={"threecol":0,"notvc":0,"vc_but_crit":0,"TARGET":0}
targets=[]
for gi,es in enumerate(graphs):
    adj=set(es)
    if col3(adj): res["threecol"]+=1; continue
    vc=all(col3(adj,rmv=v) for v in range(N))
    if not vc: res["notvc"]+=1; continue
    crit=any(col3(adj,rme=e) for e in es)
    if crit: res["vc_but_crit"]+=1
    else: res["TARGET"]+=1; targets.append((gi,es))
print(res)
for gi,es in targets:
    print("TARGET graph index",gi,"edges:",es)
