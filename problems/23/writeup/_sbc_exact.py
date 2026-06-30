"""EXACT (rational LDL, no float) gate of SBC: rho(O)+|M| <= N+N^2/25  <=>  (c*I - O) PSD, c=N+N^2/25-|M|.
Complements Codex _sbc_gate.py (float rho). Battery: census N<=10 + blowups + Mycielskians + glued islands +
two-lane L=8..24 + ADVERSARIAL high-rho+high-|M|: two-lane(L) bridged to C5[t]/C7[t] blowups (boost rho AND |M|),
and stacked two two-lanes. Exact verdict; also confirm EXACT tightness at C(2k+1)[q] extremal (c=N, NI-O PSD with
a zero pivot)."""
import subprocess
from fractions import Fraction as F
from _h import dec, GENG, Bconn
from _satzmu_conn import struct_for_side
from _stark1 import gmins
from _bdef_construct import mycielski, Cn, union_disjoint
from _verify_two_lane import build_two_lane

def build_O(n,M,cyc):
    pf=[]
    for g in M:
        Ps=cyc[g]; k=len(Ps); d={}
        for P in Ps:
            for v in P: d[v]=d.get(v,F(0))+F(1,k)
        pf.append(d)
    m=len(M); O=[[F(0)]*m for _ in range(m)]
    for i in range(m):
        for j in range(i,m):
            s=F(0); di=pf[i]; dj=pf[j]
            for v,pv in di.items():
                if v in dj: s+=pv*dj[v]
            O[i][j]=s; O[j][i]=s
    return O

def is_psd(A):
    m=len(A); Aw=[row[:] for row in A]
    for k in range(m):
        piv=Aw[k][k]
        if piv<0: return False,'negpiv'
        if piv==0:
            for j in range(m):
                if Aw[k][j]!=0: return False,'zerorow'
            continue
        for i in range(k+1,m):
            if Aw[i][k]==0: continue
            f=Aw[i][k]/piv
            for j in range(k,m): Aw[i][j]-=f*Aw[k][j]
    return True,'ok'

def sbc_exact(name,n,adj,side,acc,want_tight=False):
    if not Bconn(n,adj,side): return
    st=struct_for_side(n,adj,side)
    if st is None: return
    M,ell,T,mu,cyc=st
    if not M: return
    m=len(M); O=build_O(n,M,cyc)
    c=F(n)+F(n*n,25)-m
    A=[[ (c-O[i][j]) if i==j else (-O[i][j]) for j in range(m)] for i in range(m)]
    ok,why=is_psd(A)
    acc['tested']+=1
    if not ok:
        acc['viol']+=1
        if acc['fviol'] is None: acc['fviol']=(name,n,m,str(c),why)
    if want_tight:
        # at extremal c should equal N; verify exact tightness: (N)I-O PSD and (N-1/1000)I-O NOT necessarily;
        acc['tight'].append((name,n,m,str(c),str(F(n)),ok))

def adj_of(n,E):
    a=[set() for _ in range(n)]
    for x,y in E: a[x].add(y); a[y].add(x)
    return a
def blowup(parts):
    mm=len(parts); off=[0]*(mm+1)
    for i in range(mm): off[i+1]=off[i]+parts[i]
    nn=off[mm]; EE=[]
    for i in range(mm):
        j=(i+1)%mm
        for a in range(off[i],off[i+1]):
            for b in range(off[j],off[j+1]): EE.append((min(a,b),max(a,b)))
    return nn,sorted(set(EE))
def bridge_g(b1,b2,u,v):
    nn,E=union_disjoint(b1,b2); n1=b1[0]; return nn, E+[(u,n1+v)]

def glue_twolane_blowup(L,parts):
    # two-lane(L) side + C(len(parts))-blowup part-respecting max-cut side, bridged so bridge is a cut edge
    n1,E1,side1,bad=build_two_lane(L)
    n2,E2=blowup(parts)
    # blowup max cut: alternate parts as far as possible (odd cycle: one frustrated). Use parity by part index.
    Lc=len(parts); off=[0]
    for s in parts: off.append(off[-1]+s)
    side2=[0]*n2
    for i in range(Lc):
        for v in range(off[i],off[i+1]): side2[v]=i%2
    # combine
    n=n1+n2; E=set(E1)
    for x,y in E2: E.add((x+n1,y+n1))
    side=side1+side2
    # bridge: pick a two-lane vertex u and a blowup vertex w with side[u]!=side[w]
    u=0; w=None
    for vv in range(n1,n):
        if side[vv]!=side[u]: w=vv; break
    if w is None: return None
    E.add((min(u,w),max(u,w)))
    return n,sorted(E),side

if __name__=="__main__":
    acc=dict(tested=0,viol=0,fviol=None,tight=[])
    # two-lane long
    for L in (8,12,16,20,24):
        n,E,side,bad=build_two_lane(L); sbc_exact("twolane%d"%L,n,adj_of(n,E),side,acc)
    # extremal tightness (C5[t],C7[t]) -- need the gamma-min max cut via gmins
    for cyc in (5,7):
        for t in (1,2,3):
            n,E=blowup([t]*cyc)
            if n>21: continue
            adj,cuts=gmins(n,E)
            for s in cuts[:1]: sbc_exact("C%d[%d]"%(cyc,t),n,adj,s,acc,want_tight=True)
    # Mycielskians + glued islands
    for nm,(nn,E) in [("Grotzsch",mycielski(5,Cn(5))),("M(C7)",mycielski(7,Cn(7))),
                      ("C7|Grotzsch",bridge_g((7,Cn(7)),mycielski(5,Cn(5)),0,0)),("C5|C7",bridge_g((5,Cn(5)),(7,Cn(7)),0,0))]:
        adj,cuts=gmins(nn,E)
        for s in cuts[:2]: sbc_exact(nm,nn,adj,s,acc)
    # ADVERSARIAL: two-lane glued to blowup (high rho + high |M|)
    for L in (8,12,16):
        for parts in ([2,2,2,2,2],[3,3,3,3,3],[2,2,2,2,2,2,2]):
            g=glue_twolane_blowup(L,parts)
            if g is None: continue
            n,E,side=g
            if n>60: continue
            adj=adj_of(n,E)
            sbc_exact("TL%d+C%d%s"%(L,len(parts),parts),n,adj,side,acc)
    # census N<=10 exact
    for nn in range(5,11):
        outg=subprocess.run([GENG,"-tc",str(nn)],capture_output=True,text=True).stdout.split()
        for g6 in outg:
            n,E=dec(g6); adj,cuts=gmins(n,E)
            for s in cuts: sbc_exact("cen%s"%g6,n,adj,s,acc)
        print("  census N=%d done (tested=%d viol=%d)"%(nn,acc['tested'],acc['viol']),flush=True)
    print("\n  SBC EXACT (rational LDL): (N+N^2/25-|M|)I - O PSD.  tested=%d  violations=%d  %s"%(
        acc['tested'],acc['viol'],acc['fviol'] or ''),flush=True)
    print("  extremal tightness (name,N,|M|,c,N,c==N&PSD):",flush=True)
    for d in acc['tight']: print("    %s c=%s vs N=%s PSD=%s  tight=%s"%(d[0],d[3],d[4],d[5],d[3]==d[4]),flush=True)
    print("  === SBC EXACT %s ==="%("HOLDS on full battery + two-lane + adversarial glued" if acc['viol']==0 else "*** FAILS ***"),flush=True)
