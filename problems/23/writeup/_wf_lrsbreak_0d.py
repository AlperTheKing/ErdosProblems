"""Last push at the genuine LRS-family (PATH/ROW/LRS): try to break them on a CP-SAT GLOBAL-max cut.
Strategy: denser lanes (k=5,6) keep parity cut dominant (so it stays the true max) while path chords pile
concentrated load. Sweep L,k,gap and odd L. Report any GLOBALMAX case breaking PATH/ROW/LRS; else confirm survival.
Also try chord patterns biased to ONE endpoint (star at vertex 0) to spike a single T value."""
from fractions import Fraction as F
from _wf_lrsbreak_0 import build_k_lane, trifree, cutsize, cpmax, lrs_check
from _h import Bconn

def greedy_chords(L,k,gap,order=None):
    base_n,base_E,_,_=build_k_lane(L,k,[])
    adj=[set() for _ in range(base_n)]
    for a,b in base_E: adj[a].add(b); adj[b].add(a)
    chords=[]
    cand=[(a,b) for a in range(0,L+1) for b in range(a+gap,L+1) if (a%2)==(b%2)]
    if order=='star':  # prioritize chords incident to 0 then 1 to spike one load
        cand.sort(key=lambda e:(min(e), e))
    for (a,b) in cand:
        if b in adj[a] or (adj[a]&adj[b]): continue
        adj[a].add(b);adj[b].add(a);chords.append((a,b))
    return chords

rows=[]
gm_break_lrs=[]
for L in [9,10,11,12,13,14,15,16]:
    for k in (3,4,5,6):
        for gap in (4,6,8,10):
            for order in (None,'star'):
                bad=greedy_chords(L,k,gap,order)
                if not bad: continue
                n,E,side,bad=build_k_lane(L,k,bad)
                adj=[set() for _ in range(n)]
                for a,b in E: adj[a].add(b); adj[b].add(a)
                if not trifree(n,adj) or not Bconn(n,adj,side): continue
                pc=cutsize(n,adj,side)
                opt,bd,iso=cpmax(n,E,40)
                gm=(pc==opt==bd) and iso
                r=lrs_check(n,adj,side)
                if r is None: continue
                lrsbroken=[nm for nm,ok in [('PATH-LRS',r['PATH_ok']),('ROW-LRS',r['ROW_ok']),('LRS',r['LRS_ok'])] if not ok]
                if gm and lrsbroken:
                    gm_break_lrs.append((L,k,gap,order,lrsbroken,r))
                    print("*** LRS-FAMILY BREAK on GLOBALMAX: L=%d k=%d gap=%d ord=%s broken=%s ratioM=%.3f ROWslack=%.3f"%(
                        L,k,gap,order,lrsbroken,float(r['ratioM']),float(r['rowworst'][0])),flush=True)
                rows.append((gm,L,k,gap,order,r['absM'],float(r['ratioM']),float(r['rowworst'][0]),r['B2_ok'],lrsbroken,opt,pc))
# report best (smallest ROW-LRS slack) among GLOBALMAX cases
gmrows=[x for x in rows if x[0]]
gmrows.sort(key=lambda x:x[7])
print("=== Tightest ROW-LRS slacks among CP-SAT GLOBALMAX cases ===")
for x in gmrows[:12]:
    print("  L=%d k=%d gap=%d ord=%s |M|=%d ratioM=%.3f ROWslack=%.3f B2ok=%s lrsbroken=%s"%(
        x[1],x[2],x[3],x[4],x[5],x[6],x[7],x[8],x[9]))
print("=== GLOBALMAX cases that broke PATH/ROW/LRS ===",[(L,k,gap,o,b) for (L,k,gap,o,b,_) in gm_break_lrs])
# also: smallest ROW slack overall (incl non-globalmax) to show the boundary
allrows=sorted(rows,key=lambda x:x[7])
print("=== smallest ROW-LRS slack OVERALL (incl non-max, NOT breakers) ===")
for x in allrows[:6]:
    print("  GLOBALMAX=%s L=%d k=%d gap=%d ord=%s ROWslack=%.3f opt=%d cut=%d"%(x[0],x[1],x[2],x[3],x[4],x[7],x[10],x[11]))
