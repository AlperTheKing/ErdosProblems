"""FINAL exact characterization at the GAMMA-MINIMIZING max cut (the lemma's hypothesis).
Confirm on gmins cuts (census N<=11) + hard witnesses:
  (i)   Dout = sum_{v notin P}(N-T_v) >= 0
  (ii)  B_L = L*Dout + (L+25)*Din - disp >= 0     (Din=sum_{i}(N-T_i), disp=S^2-L^2 q)
  (iii) worst ratio disp / ((L+25)Din + L Dout)  (tightness; <1 strictly off blow-up)
Report violations + worst ratio + tight family.
"""
import sys, subprocess
from fractions import Fraction as F
from _h import dec, GENG, Bconn, geos
from _stark1 import gmins
from _bdef_construct import Cn, mycielski

def struct(n,adj,side):
    M=[(u,v) for u in range(n) for v in adj[u] if v>u and side[u]==side[v]]
    if not M or not Bconn(n,adj,side): return None
    T=[F(0)]*n; ell={}; cyc={}
    for f in M:
        Ps=geos(adj,side,f[0],f[1])
        if not Ps: return None
        cyc[f]=Ps; ell[f]=len(Ps[0]); sh=F(ell[f],len(Ps))
        T=[T[i]+(sh*sum(1 for P in Ps if i in P)) for i in range(n)]
    return M,ell,T,cyc

def scan(n,E,cuts):
    adj=[set() for _ in range(n)]
    for a,b in E: adj[a].add(b); adj[b].add(a)
    nDoutNeg=0; nBneg=0; rows=0; worst=None; minB=None; minDout=None
    for side in cuts:
        st=struct(n,adj,side)
        if st is None: continue
        M,ell,T,cyc=st; N=F(n); Gamma=sum(T); Tall=N*N-Gamma
        for f in M:
            L=ell[f]
            if L%2==0: continue
            for P in cyc[f]:
                if len(P)!=L: continue
                rows+=1
                Ti=[T[i] for i in P]
                Din=sum(N-t for t in Ti); Dout=Tall-Din
                if Dout<0: nDoutNeg+=1
                if minDout is None or Dout<minDout: minDout=Dout
                h=[t/N for t in Ti]; S=sum(h)
                q=min(h[i]*h[(i+1)%L] for i in range(L))
                disp=S*S-(L*L)*q
                B=L*Dout+(L+25)*Din-disp
                if B<0: nBneg+=1
                if minB is None or B<minB: minB=B
                den=L*Dout+(L+25)*Din
                if den>0:
                    r=disp/den
                    if worst is None or r>worst[0]: worst=(r,n,L)
    return dict(rows=rows,nDoutNeg=nDoutNeg,nBneg=nBneg,worst=worst,minB=minB,minDout=minDout)

def main():
    agg=dict(rows=0,nDoutNeg=0,nBneg=0,worst=None,minB=None,minDout=None)
    for nn in range(5,12):
        outg=subprocess.run([GENG,"-tc",str(nn)],capture_output=True,text=True).stdout.split()
        for g6 in outg:
            n,E=dec(g6)
            adj,cuts=gmins(n,E)
            r=scan(n,E,cuts)
            agg['rows']+=r['rows']; agg['nDoutNeg']+=r['nDoutNeg']; agg['nBneg']+=r['nBneg']
            if r['minB'] is not None and (agg['minB'] is None or r['minB']<agg['minB']): agg['minB']=r['minB']
            if r['minDout'] is not None and (agg['minDout'] is None or r['minDout']<agg['minDout']): agg['minDout']=r['minDout']
            if r['worst'] is not None and (agg['worst'] is None or r['worst'][0]>agg['worst'][0]): agg['worst']=r['worst']
    print("GMIN cuts census N<=11:")
    print("  rows=%d  Dout<0=%d  B_L<0=%d"%(agg['rows'],agg['nDoutNeg'],agg['nBneg']))
    print("  min B_L=%s  min Dout=%s"%(str(agg['minB']),str(agg['minDout'])))
    print("  worst ratio disp/((L+25)Din+L Dout)=%s (N=%d,L=%d)"%
          (str(agg['worst'][0]),agg['worst'][1],agg['worst'][2]) if agg['worst'] else "n/a")

if __name__=="__main__":
    main()
