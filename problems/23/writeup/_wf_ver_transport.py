"""ADVERSARIAL re-verification of route 'transport' (independent re-implementation).
CENTRAL INEQUALITY claimed (for all tau>=0):
  Phi(tau) = int_0^tau [ (N^2 - 25*beta + 25*N - 50*s)*|H_s| - 5*N*(dB(H_s)-dM(H_s)) ] ds >= 0
Per T-filtration slab [t_j, t_j+w_j):
  contrib_j = w_j*|H_j|*( (N^2-25*beta) - 25*(2*t_j+w_j-N) ) - 5*N*w_j*(dB_j-dM_j)
  Phi at breakpoint k = prefix_{j<k} contrib_j >= 0  (claimed; extremal const 0 at C5 balanced blow-up).
I re-implement the load struct (via my own copy of struct_for_side semantics through the shared helper),
the H_s superlevel sets, boundary (dB,dM), the slab decomposition, the prefix sums -- ALL exact Fraction --
and HUNT for any breakpoint with Phi<0. I do NOT import the claimant's gate file.

Also: I separately verify the IDENTITY  25*(Gamma*(N^2/25 - beta) - INT_{c=5}) == Phi(inf)
to confirm Phi(inf)>=0 <=> LOAD-PSC-c5 (the reduction), independently per config.

Run from E:/Projects/ErdosProblems/problems/23/writeup."""
import subprocess
from fractions import Fraction as F
from _h import dec, GENG, Bconn, geos, bdist_restr, maxcut_all
from _stark1 import gmins
from _bdef_construct import mycielski, Cn, union_disjoint
from _verify_two_lane import build_two_lane
from _wf_lrsbreak_0 import build_k_lane
from _wf_lrsbreak_0c import greedy_chords

# ---- independent load-struct (re-derived, not imported from _satzmu_conn) ----
def my_struct(n, adj, side):
    """Return (M, T list[Fraction], dB/dM-ready data) or None.
    Bad edges M = monochromatic. For each f, geodesics = shortest alternating B-paths (geos), ell=#verts on a
    geodesic, weight sh = ell/|cyc|, each geodesic deposits 1 (times sh) on each vertex it passes through.
    T(v) = sum over f of sh_f * (#geodesics of f through v).  Handshake: sum_v T_v = sum_f ell_f^2."""
    M=[(u,v) for u in range(n) for v in adj[u] if v>u and side[u]==side[v]]
    if not M: return None
    T=[F(0)]*n
    Gamma=F(0)
    for f in M:
        Ps=geos(adj,side,f[0],f[1])
        if not Ps: return None
        ell=len(Ps[0])            # all shortest geodesics have same #vertices
        # sanity: every path same length
        if any(len(P)!=ell for P in Ps): return None
        sh=F(ell,len(Ps))
        for P in Ps:
            for v in P: T[v]+=sh
        Gamma+=F(ell)**2
    return M,T,Gamma

def boundary(n,adj,side,Hset):
    """dB = #cut-edges (side differ) crossing boundary of H; dM = #bad-edges (same side) crossing boundary."""
    dB=dM=0
    Hset=set(Hset)
    for u in Hset:
        for v in adj[u]:
            if v in Hset: continue
            if side[u]!=side[v]: dB+=1
            else: dM+=1
    return dB,dM

def check_config(name, n, adj, side, acc):
    if not Bconn(n,adj,side): return
    st=my_struct(n,adj,side)
    if st is None: return
    M,T,Gamma=st
    beta=len(M); N=n
    # breakpoints = distinct positive load values (H_s changes only there). s in [t_j,t_{j+1}).
    levels=sorted(set([F(0)]+[v for v in set(T) if v>0]))
    # build slabs
    slabs=[]   # (t_j, w_j, |H_j|, dB_j, dM_j)
    for j in range(len(levels)-1):
        tj=levels[j]; wj=levels[j+1]-tj
        Hset=set(v for v in range(n) if T[v]>tj)
        if not Hset:  # H empty -> contributes 0 (|H|=0, dB=dM=0). skip but keep prefix continuity
            slabs.append((tj,wj,0,0,0)); continue
        dB,dM=boundary(n,adj,side,Hset)
        slabs.append((tj,wj,len(Hset),dB,dM))
    # prefix sums of contrib_j ; track minimum running balance
    D0=F(N*N)-25*beta
    cum=F(0); mn=F(0)   # Phi(0)=0; min over all breakpoints incl 0
    first_neg=None
    for (tj,wj,Hsz,dB,dM) in slabs:
        contrib = wj*F(Hsz)*( D0 - 25*(2*tj+wj-F(N)) ) - 5*F(N)*wj*F(dB-dM)
        cum += contrib
        if cum<mn: mn=cum
        if cum<0 and first_neg is None:
            first_neg=(name,n,beta,float(cum),float(tj+wj))
    Phi_inf=cum
    # ---- independent reduction identity check: 25*(Gamma*(N^2/25-beta) - INT_c5) == Phi_inf ----
    # INT_c5 = int_0^inf [ (2s-N)|H_s| + (N/5)(dB-dM) ] ds  over slabs
    sumT  = sum(T)                      # = Gamma (handshake)
    sumT2 = sum(t*t for t in T)
    # int (2s-N)|H_s| ds = sum_slab |H| * int_{tj}^{tj+wj}(2s-N) ds = sum |H|*( (tj+wj)^2 - tj^2 - N*wj )
    int_2sN=F(0); int_dd=F(0)
    for (tj,wj,Hsz,dB,dM) in slabs:
        int_2sN += F(Hsz)*( (tj+wj)*(tj+wj) - tj*tj - F(N)*wj )
        int_dd  += F(dB-dM)*wj
    INT_c5 = int_2sN + F(N,5)*int_dd
    lhs_load = Gamma*(F(N*N,25)-beta) - INT_c5        # LOAD-PSC-c5 residual (>=0 == target)
    identity_ok = (25*lhs_load == Phi_inf)
    # also sanity handshake sum T == Gamma
    handshake_ok = (sumT==Gamma)

    acc['n']+=1
    if not handshake_ok: acc['handshake_bad'].append(name)
    if not identity_ok:
        acc['identity_bad'].append((name,float(25*lhs_load),float(Phi_inf)))
    if mn<acc['min'][0]: acc['min']=(mn,name,n,beta)
    if Phi_inf<acc['phiinf_min'][0]: acc['phiinf_min']=(Phi_inf,name,n,beta)
    if mn<0:
        acc['viol']+=1
        if acc['first'] is None: acc['first']=first_neg
    # track Phi(inf) exactness to 0 (should hit 0 only on balanced C5 blowups)
    if Phi_inf==0:
        acc['phiinf_zero'].append((name,n,beta))

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

if __name__=="__main__":
    acc={'n':0,'viol':0,'first':None,'min':(F(10**18),'','',''),
         'phiinf_min':(F(10**18),'','',''),'identity_bad':[],'handshake_bad':[],
         'phiinf_zero':[]}
    # two-lane L=8..20
    for L in range(8,21,2):
        n,E,side,_=build_two_lane(L); check_config("two-lane-L%d"%L,n,adj_of(n,E),side,acc)
    print("  two-lane done: viol=%d minrun=%s"%(acc['viol'],float(acc['min'][0])),flush=True)
    # k-lane breakers
    for (Ll,k,gap) in [(12,4,6),(14,4,8),(16,5,8)]:
        bad=greedy_chords(Ll,k,gap); n,E,side,bad=build_k_lane(Ll,k,bad)
        check_config("klane-L%dk%dg%d"%(Ll,k,gap),n,adj_of(n,E),side,acc)
    print("  k-lane breakers done: viol=%d minrun=%s"%(acc['viol'],float(acc['min'][0])),flush=True)
    # census geng -tc N=7..11, ALL gmin cuts
    for nn in range(7,12):
        outg=subprocess.run([GENG,"-tc",str(nn)],capture_output=True,text=True).stdout.split()
        a0=acc['viol']
        for g6 in outg:
            n,E=dec(g6); adj,cuts=gmins(n,E)
            for s in cuts: check_config("cen%s"%g6,n,adj,s,acc)
        print("  census N=%d (viol+%d) total-configs=%d"%(nn,acc['viol']-a0,acc['n']),flush=True)
    # C5/C7/C9 blow-ups t=1..5
    for cyc in (5,7,9):
        for t in range(1,6):
            n,E=blowup([t]*cyc)
            if n>26: continue
            adj,cuts=gmins(n,E)
            for s in (cuts[:2] if cuts else []): check_config("C%d[%d]"%(cyc,t),n,adj,s,acc)
    # non-uniform blow-ups
    for parts in [[2,2,2,2,3],[1,5,2,2,5],[1,4,2,4,2,4,2],[3,3,3,3,2],[1,3,2,2,3],[1,48,6,8,48][:0] or [3,1,3,1,3]]:
        n,E=blowup(parts)
        if n>40: continue
        adj,cuts=gmins(n,E)
        for s in (cuts[:2] if cuts else []): check_config("nu%s"%parts,n,adj,s,acc)
    print("  blow-ups done: viol=%d"%acc['viol'],flush=True)
    # Mycielskians + glued islands
    grot=mycielski(5,Cn(5)); mycg=mycielski(grot[0],grot[1])
    def bridge(b1,b2,u,v):
        nn,E=union_disjoint(b1,b2); n1=b1[0]; return nn, E+[(u, n1+v)]
    cases=[("Grotzsch",grot),("Myc(Grotzsch)N23",mycg),("M(C7)",mycielski(7,Cn(7))),
           ("M(C9)",mycielski(9,Cn(9))),
           ("bridge(C7,Grotzsch)",bridge((7,Cn(7)),mycielski(5,Cn(5)),0,0)),
           ("bridge(C9,C9)",bridge((9,Cn(9)),(9,Cn(9)),0,0))]
    for name,(nn,E) in cases:
        adj,cuts=gmins(nn,E)
        for s in cuts[:3]: check_config(name,nn,adj,s,acc)
    print("  Mycielskians + glued done: viol=%d"%acc['viol'],flush=True)
    # a few extra ad-hoc triangle-free graphs (Petersen, C11, C13, Kneser-ish via geng dense)
    pet_n=10; pet_E=[(i,(i+1)%5) for i in range(5)]+[(5+i,5+(i+2)%5) for i in range(5)]+[(i,5+i) for i in range(5)]
    for s in (gmins(pet_n,pet_E)[1][:3]): check_config("Petersen",pet_n,gmins(pet_n,pet_E)[0],s,acc)
    for cyc in (11,13):
        n,E=blowup([1]*cyc); adj,cuts=gmins(n,E)
        for s in (cuts[:1] if cuts else []): check_config("C%d"%cyc,n,adj,s,acc)
    for cyc,t in [(11,2),(13,2),(7,3),(5,4)]:
        n,E=blowup([t]*cyc)
        if n>40: continue
        adj,cuts=gmins(n,E)
        for s in (cuts[:1] if cuts else []): check_config("C%d[%d]"%(cyc,t),n,adj,s,acc)
    print("  ad-hoc extras done: viol=%d"%acc['viol'],flush=True)

    print("\n==== RESULTS ====",flush=True)
    print("  total configs checked = %d"%acc['n'])
    print("  reduction-identity 25*(LOAD-PSC-c5 residual)==Phi(inf): %s (%d mismatches)"%(
        "ALL MATCH" if not acc['identity_bad'] else "MISMATCH", len(acc['identity_bad'])))
    if acc['identity_bad']: print("    mismatches (first 5):", acc['identity_bad'][:5])
    print("  handshake sum_v T_v == Gamma: %s"%("ALL OK" if not acc['handshake_bad'] else acc['handshake_bad'][:5]))
    print("  CENTRAL INEQUALITY Phi(tau)>=0 at every breakpoint:")
    print("    violations (min running balance < 0) = %d"%acc['viol'])
    print("    min running balance over battery = %s  at %s"%(float(acc['min'][0]),acc['min'][1:]))
    if acc['first']: print("    FIRST VIOLATION: %s"%(acc['first'],))
    print("  Phi(inf) min over battery = %s at %s"%(float(acc['phiinf_min'][0]),acc['phiinf_min'][1:]))
    print("  configs with Phi(inf) exactly 0 (extremal): %s"%(acc['phiinf_zero'][:10]))
    print("\n  === CENTRAL INEQUALITY %s ; reduction-to-LOAD-PSC-c5 %s ==="%(
        "HOLDS (0 violations)" if acc['viol']==0 else "FAILS",
        "CONFIRMED (identity)" if not acc['identity_bad'] else "BROKEN"),flush=True)
