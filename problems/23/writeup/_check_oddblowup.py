from _stark1 import odd_blowup, gmins
from _opencap import opencap
from _stark_multi import stark_multi
from _h import maxcut_all

for sizes in [[2,2,2,2,3],[3,3,2,2,3]]:
    n,E,adj,side=odd_blowup(5,sizes)
    cutsz=sum(1 for u in range(n) for v in adj[u] if v>u and side[u]!=side[v])
    mc=max(sum(1 for u in range(n) for v in adj[u] if v>u and s[u]!=s[v]) for s in maxcut_all(n,adj))
    c=opencap(adj,side,n); sm=stark_multi(adj,side,n)
    cert = c.get('cert') if (c and not c.get('skip')) else c
    print(f"C5{sizes} N={n}: side%2 cutsize={cutsz} maxcut={mc} is_maxcut={cutsz==mc}; full-g(side%2)cert={cert} STARK-multi-PSD={sm['psd'] if sm else None}")
    adj2,gcuts=gmins(n,E)
    gm_tot=0; gm_fail=0; gm_fullg_fail=0
    for s in gcuts:
        d=stark_multi(adj2,s,n); cc=opencap(adj2,s,n)
        if d and not d.get('skip'):
            gm_tot+=1
            if not d['psd']: gm_fail+=1
            if cc and not cc.get('skip') and not cc['cert']: gm_fullg_fail+=1
    print(f"   gamma-min: {len(gcuts)} cuts, STARK-multi tested={gm_tot} FAILS={gm_fail} full-g-FAILS={gm_fullg_fail}")
