"""ROUTE per-component SPECTRAL gate for (CV).

(CV) per K-component c:  w^T O_c w  <=  (N+eta) * Gamma_c,
  where O_c[f,g] = <p_f,p_g> = sum_v p_f(v)p_g(v) (edge-Gram, f,g bad edges of c),
  w_f = ell_f/|cyc_f|, Gamma_c = sum_{f in c} ell_f^2, eta = N^2/25 - beta.

Two algebraic identities used here (both EXACT):
  Gamma_c = sum_f ell_f^2 = w^T D w   with   D = diag(|cyc_f|^2),  since ell_f = w_f*|cyc_f|.
  ||w||^2 = sum_f w_f^2  <= Gamma_c    (because |cyc_f|^2 >= 1 so ell_f^2 = w_f^2|cyc_f|^2 >= w_f^2).

Candidates tested per component:
  (CV)   w^T O_c w <= (N+eta) Gamma_c                       -- the target itself (sum_v T_v^2 form).
  (i)    rho(O_c) <= N + eta                                -- spectral radius of edge-Gram.
         IMPLICATION: w^T O_c w <= rho(O_c)||w||^2 <= (N+eta)||w||^2 <= (N+eta)Gamma_c => (CV).
         Tested EXACTLY as PSD of (N+eta) I - O_c (O_c sym PSD => rho<=t iff tI-O_c PSD).
  (ii)   (N+eta) D - O_c PSD  (D=diag(|cyc_f|^2))           -- the w-free M/quadratic form.
         IMPLICATION: w^T O_c w <= (N+eta) w^T D w = (N+eta)Gamma_c => (CV).  Equality-tight form.
  (GERSH) for every bad edge f in c:  R_f := sum_{g in c} <p_f,p_g>/(|cyc_f||cyc_g|) <= N+eta.
         This is the Gershgorin row-bound of the symmetric normalized matrix
         Dm[f,g]=<p_f,p_g>/(|cyc_f||cyc_g|) (entrywise >=0, so |Dm|=Dm).
         IMPLICATION: rho(Dm) <= max_f R_f <= N+eta  =>  (N+eta)D - O_c = D^{1/2}((N+eta)I-Dm)D^{1/2} PSD
                      => (ii) => (CV).  A SINGLE SCALAR inequality per bad edge -- the provable target.
         Equivalently R_f = (1/|cyc_f|) sum_v p_f(v) * Tw(v),  Tw(v):=sum_g p_g(v)/|cyc_g|.

EXACT PSD test via symmetric LDL (Bunch-free, rational pivots; reports min pivot sign).
Full standing battery. Fractions only; NEVER floats for pass/fail.
"""
import subprocess
from fractions import Fraction as F
from _h import dec, GENG, Bconn
from _satzmu_conn import struct_for_side, kcomponents
from _stark1 import gmins
from _bdef_construct import mycielski, Cn, union_disjoint
from _verify_two_lane import build_two_lane
from _wf_lrsbreak_0 import build_k_lane
from _wf_lrsbreak_0c import greedy_chords


def psd_exact(Msym):
    """EXACT PSD test of symmetric rational matrix Msym (list of lists of Fraction).
    Returns (is_psd, min_diag_marker). Uses symmetric Gaussian elimination with row/col
    pivoting to be robust to singular (zero-pivot) cases:
      - if a pivot is < 0  -> NOT PSD (indefinite), return False.
      - if a pivot is = 0  -> its whole remaining row/col must be 0 for PSD; else NOT PSD.
      - if a pivot is > 0  -> eliminate.
    Returns (True/False, the most-negative quantity seen [0 if psd]).
    """
    m=len(Msym)
    A=[[Msym[i][j] for j in range(m)] for i in range(m)]
    worst=F(0)
    used=[False]*m
    for _ in range(m):
        # pick an unused index with nonzero diagonal (prefer to expose negativity early)
        piv=None
        for i in range(m):
            if not used[i] and A[i][i]!=0:
                piv=i; break
        if piv is None:
            # all remaining diagonals are zero. For PSD, all remaining off-diagonals among
            # unused must be zero too.
            for i in range(m):
                if used[i]: continue
                for j in range(m):
                    if used[j]: continue
                    if A[i][j]!=0:
                        return (False, F(-1))  # zero diag with nonzero entry => indefinite
            return (True, worst)
        d=A[piv][piv]
        if d<0:
            return (False, d)
        # eliminate piv from all other unused rows/cols
        used[piv]=True
        for i in range(m):
            if used[i]: continue
            if A[i][piv]!=0:
                f=A[i][piv]/d
                for j in range(m):
                    if used[j]: continue
                    A[i][j]-=f*A[piv][j]
    return (True, worst)


def chk(name,n,adj,side,acc):
    if not Bconn(n,adj,side): return
    st=struct_for_side(n,adj,side)
    if st is None: return
    M,ell,T,mu,cyc=st
    if not M: return
    beta=len(M); N=n
    eta=F(n*n,25)-beta
    A=F(N)+eta  # = N + N^2/25 - beta
    # p_f(v): number of geodesics of f through v
    Pf={}
    for f in M:
        Ps=cyc[f]; cnt={}
        for p in Ps:
            for v in p: cnt[v]=cnt.get(v,0)+1
        Pf[f]={v:F(cnt[v]) for v in cnt}
    comp_map,find=kcomponents(n,cyc); cid=[find(u) for u in range(n)]
    # group bad edges by component (a bad edge's component = component of any vertex on its geodesics)
    edges_by_comp={}
    for f in M:
        anyv=cyc[f][0][0]
        edges_by_comp.setdefault(find(anyv),[]).append(f)
    for croot,fs in edges_by_comp.items():
        kf=len(fs)
        # O_c[a,b] = <p_fa, p_fb>
        Oc=[[F(0)]*kf for _ in range(kf)]
        for a in range(kf):
            pa=Pf[fs[a]]
            for b in range(a,kf):
                pb=Pf[fs[b]]
                # overlap sum over shared vertices
                keys=pa.keys() & pb.keys() if len(pa)<len(pb) else pb.keys() & pa.keys()
                s=sum(pa[v]*pb[v] for v in keys)
                Oc[a][b]=s; Oc[b][a]=s
        w=[F(ell[f],len(cyc[f])) for f in fs]
        cycsz=[F(len(cyc[f])) for f in fs]
        Gamma=sum(ell[f]*ell[f] for f in fs)  # = sum ell^2
        if Gamma==0: continue
        # quadratic form w^T O_c w  (== sum_{v in c} T_v^2)
        qf=sum(w[a]*Oc[a][b]*w[b] for a in range(kf) for b in range(kf))
        acc['nc']+=1
        # ---- (CV) direct ----
        margin_cv=A*Gamma-qf
        if margin_cv<acc['cv_min'][0]: acc['cv_min']=(margin_cv,name,N,beta,kf,str(Gamma))
        if margin_cv<0:
            acc['cv_viol']+=1
            if acc['cv_first'] is None: acc['cv_first']=(name,N,beta,kf,str(margin_cv))
        # ---- (i) rho(O_c) <= A : test PSD of A*I - O_c ----
        S=[[ (A if i==j else F(0)) - Oc[i][j] for j in range(kf)] for i in range(kf)]
        ok_i,wi=psd_exact(S)
        if not ok_i:
            acc['i_viol']+=1
            if acc['i_first'] is None: acc['i_first']=(name,N,beta,kf,'rho>A')
        # ---- (ii) (A) D - O_c PSD, D=diag(|cyc_f|^2) ----
        S2=[[ (A*cycsz[i]*cycsz[i] if i==j else F(0)) - Oc[i][j] for j in range(kf)] for i in range(kf)]
        ok_ii,wii=psd_exact(S2)
        if not ok_ii:
            acc['ii_viol']+=1
            if acc['ii_first'] is None: acc['ii_first']=(name,N,beta,kf,'AD-O not PSD')
        # ---- (GERSH) row-bound: R_f = sum_g Oc[f,g]/(cyc_f cyc_g) <= A, for every f ----
        for i in range(kf):
            Rf=sum(Oc[i][j]/(cycsz[i]*cycsz[j]) for j in range(kf))
            gmargin=A-Rf
            if gmargin<acc['g_min'][0]: acc['g_min']=(gmargin,name,N,beta,kf,str(A))
            if gmargin<0:
                acc['g_viol']+=1
                if acc['g_first'] is None: acc['g_first']=(name,N,beta,kf,str(gmargin))
        # track sufficiency-chain slack: ||w||^2 vs Gamma; and qf/||w||^2 (Rayleigh) vs A
        normw2=sum(x*x for x in w)
        if normw2>0:
            rayl=qf/normw2  # <= rho(O_c)
            if rayl>acc['max_rayleigh'][0]:
                acc['max_rayleigh']=(rayl, name, N, str(A), kf)


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
    acc={'nc':0,
         'cv_viol':0,'cv_first':None,'cv_min':(F(10**18),'','','','',''),
         'i_viol':0,'i_first':None,
         'ii_viol':0,'ii_first':None,
         'g_viol':0,'g_first':None,'g_min':(F(10**18),'','','','',''),
         'max_rayleigh':(F(-1),'','','',0)}
    for L in range(8,21,2):
        n,E,side,_=build_two_lane(L); chk("two-lane-L%d"%L,n,adj_of(n,E),side,acc)
    for (Ll,k,gap) in [(12,4,6),(14,4,8),(16,5,8)]:
        bad=greedy_chords(Ll,k,gap); n,E,side,bad=build_k_lane(Ll,k,bad); chk("klane-L%dk%d"%(Ll,k),n,adj_of(n,E),side,acc)
    print("  two-lane+k-lane: CV viol=%d  (i)viol=%d  (ii)viol=%d"%(acc['cv_viol'],acc['i_viol'],acc['ii_viol']),flush=True)
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
    print("  blow-ups + Mycielskians + glued done: CV viol=%d  (i)viol=%d  (ii)viol=%d"%(acc['cv_viol'],acc['i_viol'],acc['ii_viol']),flush=True)
    for nn in range(7,12):
        outg=subprocess.run([GENG,"-tc",str(nn)],capture_output=True,text=True).stdout.split()
        v0=(acc['cv_viol'],acc['i_viol'],acc['ii_viol'])
        for g6 in outg:
            n,E=dec(g6); adj,cuts=gmins(n,E)
            for s in cuts: chk("cen%s"%g6,n,adj,s,acc)
        print("  census N=%d (CV+%d i+%d ii+%d)"%(nn,acc['cv_viol']-v0[0],acc['i_viol']-v0[1],acc['ii_viol']-v0[2]),flush=True)
    print("\n  components tested=%d"%acc['nc'],flush=True)
    print("  (CV)  violations=%d   MIN margin=%s @ %s"%(acc['cv_viol'],float(acc['cv_min'][0]),acc['cv_min'][1:]),flush=True)
    print("  (i) rho(O_c)<=N+eta  violations=%d  first=%s"%(acc['i_viol'],acc['i_first']),flush=True)
    print("  (ii) (N+eta)D-O_c PSD violations=%d  first=%s"%(acc['ii_viol'],acc['ii_first']),flush=True)
    print("  (GERSH) R_f<=N+eta violations=%d  MIN margin=%s @ %s  first=%s"%(acc['g_viol'],float(acc['g_min'][0]),acc['g_min'][1:],acc['g_first']),flush=True)
    mr=acc['max_rayleigh']
    print("  max Rayleigh qf/||w||^2 = %s  (vs A=%s) @ %s"%(float(mr[0]),mr[3],(mr[1],mr[2],mr[4])),flush=True)
    print("  === (CV) %s | (i)rho-route %s | (ii)D-PSD-route %s | (GERSH)row-route %s ==="%(
        "HOLDS" if not acc['cv_viol'] else "FAILS",
        "HOLDS" if not acc['i_viol'] else "FAILS",
        "HOLDS" if not acc['ii_viol'] else "FAILS",
        "HOLDS" if not acc['g_viol'] else "FAILS"),flush=True)
