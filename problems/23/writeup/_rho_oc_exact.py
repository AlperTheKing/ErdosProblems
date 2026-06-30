"""EXACT cert: rho(O_c) <= N+eta per K-component  <=>  S_c:=(N+eta)I - O_c is PSD. Implies (CV) via Rayleigh.
O_{fg} = sum_v p_f(v)p_g(v)/(|cyc_f||cyc_g|), p_f(v)=#geodesics of f through v. All Fraction (exact).
Also test the STRONGER Gershgorin row-sum bound: max_f sum_g |O_{fg}| <= N+eta (would give (CV) immediately).
PSD via exact LDL^T (PSD <=> in-order pivots >=0 and any zero pivot has zero row -- valid since PSD zero-diag=>zero-row).
Full battery; report PSD violations + Gershgorin max ratio."""
import subprocess
from fractions import Fraction as F
from _h import dec, GENG, Bconn
from _satzmu_conn import struct_for_side, kcomponents
from _stark1 import gmins
from _bdef_construct import mycielski, Cn, union_disjoint
from _verify_two_lane import build_two_lane
from _wf_lrsbreak_0 import build_k_lane
from _wf_lrsbreak_0c import greedy_chords

def is_psd(S):
    # S: list of lists of Fraction, symmetric. In-order LDL^T PSD test.
    n=len(S); A=[row[:] for row in S]
    for k in range(n):
        p=A[k][k]
        if p<0: return False
        if p==0:
            for j in range(k+1,n):
                if A[k][j]!=0: return False
            continue
        for i in range(k+1,n):
            if A[i][k]==0: continue
            fac=A[i][k]/p
            for j in range(k,n):
                A[i][j]-=fac*A[k][j]
    return True

def chk(name,n,adj,side,acc):
    if not Bconn(n,adj,side): return
    st=struct_for_side(n,adj,side)
    if st is None: return
    M,ell,T,mu,cyc=st
    if not M: return
    m=len(M); A=F(n)+F(n*n,25)-m
    Mlist=list(M)
    # p_f(v) counts and |cyc_f|
    pf=[]; cf=[]
    for f in Mlist:
        Ps=cyc[f]; cf.append(len(Ps))
        col={}
        for v in range(n):
            cnt=sum(1 for Pp in Ps if v in Pp)
            if cnt: col[v]=cnt
        pf.append(col)
    comp_map,find=kcomponents(n,cyc)
    fcomp=[find(cyc[f][0][0]) for f in Mlist]
    comps={}
    for fi,c in enumerate(fcomp): comps.setdefault(c,[]).append(fi)
    for c,idx in comps.items():
        sz=len(idx)
        # O_c[a][b] = sum_v pf[ia][v]*pf[ib][v] / (cf[ia]*cf[ib])
        O=[[F(0)]*sz for _ in range(sz)]
        for a in range(sz):
            ia=idx[a]; ca=cf[ia]; pa=pf[ia]
            for b in range(a,sz):
                ib=idx[b]; cb=cf[ib]; pb=pf[ib]
                s=0
                for v,x in pa.items():
                    y=pb.get(v)
                    if y: s+=x*y
                val=F(s,ca*cb)
                O[a][b]=val; O[b][a]=val
        # Gershgorin row sums
        rowmax=max(sum(O[a]) for a in range(sz))
        ratio=rowmax/A
        if ratio>acc['gersh'][0]: acc['gersh']=(ratio,name,n,m,sz)
        # PSD of A*I - O
        S=[[ (A-O[a][a]) if a==b else -O[a][b] for b in range(sz)] for a in range(sz)]
        acc['nc']+=1
        if not is_psd(S):
            acc['psdviol']+=1
            if acc['first'] is None: acc['first']=(name,''.join(map(str,side)),n,m,sz)

def blowup(parts):
    mm=len(parts); off=[0]*(mm+1)
    for i in range(mm): off[i+1]=off[i]+parts[i]
    nn=off[mm]; EE=[]
    for i in range(mm):
        j=(i+1)%mm
        for a in range(off[i],off[i+1]):
            for b in range(off[j],off[j+1]): EE.append((min(a,b),max(a,b)))
    return nn,sorted(set(EE))
def adj_of(n,E):
    a=[set() for _ in range(n)]
    for x,y in E: a[x].add(y); a[y].add(x)
    return a
def bridge(b1,b2,u,v):
    nn,E=union_disjoint(b1,b2); n1=b1[0]; return nn, E+[(u,n1+v)]

if __name__=="__main__":
    acc={'nc':0,'psdviol':0,'first':None,'gersh':(F(-1),'','','','')}
    for L in range(8,21,2):
        n,E,side,_=build_two_lane(L); chk("two-lane-L%d"%L,n,adj_of(n,E),side,acc)
    for (Ll,k,gap) in [(12,4,6),(14,4,8),(16,5,8)]:
        bad=greedy_chords(Ll,k,gap); n,E,side,bad=build_k_lane(Ll,k,bad); chk("klane-L%dk%d"%(Ll,k),n,adj_of(n,E),side,acc)
    print("  two-lane+k-lane: psdviol=%d gershmax=%.4f"%(acc['psdviol'],float(acc['gersh'][0])),flush=True)
    for c in (5,7,9):
        for t in range(1,6):
            n,E=blowup([t]*c)
            if n>26: continue
            adj,cuts=gmins(n,E)
            for s in (cuts[:2] if cuts else []): chk("C%d[%d]"%(c,t),n,adj,s,acc)
    for parts in [[2,2,2,2,3],[1,5,2,2,5],[1,4,2,4,2,4,2],[3,3,3,3,2],[1,3,2,2,3]]:
        n,E=blowup(parts)
        if n>26: continue
        adj,cuts=gmins(n,E)
        for s in (cuts[:2] if cuts else []): chk("nu%s"%parts,n,adj,s,acc)
    grot=mycielski(5,Cn(5)); mycg=mycielski(grot[0],grot[1])
    for nm,(nn,E) in [("Grotzsch",grot),("Myc(Grotzsch)",mycg),("M(C7)",mycielski(7,Cn(7))),("M(C9)",mycielski(9,Cn(9))),
                      ("C7|Grotzsch",bridge((7,Cn(7)),mycielski(5,Cn(5)),0,0)),("C9|C9",bridge((9,Cn(9)),(9,Cn(9)),0,0)),
                      ("C5|C7",bridge((5,Cn(5)),(7,Cn(7)),0,0))]:
        adj,cuts=gmins(nn,E)
        for s in cuts[:3]: chk(nm,nn,adj,s,acc)
    print("  blow-ups + Mycielskians + glued: psdviol=%d gershmax=%.4f"%(acc['psdviol'],float(acc['gersh'][0])),flush=True)
    for nn in range(7,12):
        outg=subprocess.run([GENG,"-tc",str(nn)],capture_output=True,text=True).stdout.split()
        for g6 in outg:
            n,E=dec(g6); adj,cuts=gmins(n,E)
            for s in cuts: chk("cen%s"%g6,n,adj,s,acc)
        print("  census N=%d: psdviol=%d gershmax=%.4f"%(nn,acc['psdviol'],float(acc['gersh'][0])),flush=True)
    print("\n  components=%d  PSD((N+eta)I-O_c) violations=%d"%(acc['nc'],acc['psdviol']),flush=True)
    if acc['first']: print("  first PSD violation: %s"%(acc['first'],),flush=True)
    print("  Gershgorin MAX row-sum/(N+eta) = %s ~ %.5f at %s"%(acc['gersh'][0],float(acc['gersh'][0]),acc['gersh'][1:]),flush=True)
    print("  === rho(O_c)<=N+eta (PSD) %s ; Gershgorin %s ==="%(
        "HOLDS => proves (CV)" if not acc['psdviol'] else "FAILS",
        "ALSO holds (trivial proof!)" if acc['gersh'][0]<=1 else "exceeds 1 (need PSD not Gershgorin)"),flush=True)
