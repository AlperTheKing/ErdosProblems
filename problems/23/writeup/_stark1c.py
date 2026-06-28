"""STAR-K1, STAR-K1-6/5, and P5-DEFICIT (Codex 94/96/97), exact. P5 => STAR-K1 via ell>=5 (h_q=T(q)-a_q>=4a_q).
   P5-DEFICIT:  sum_{q: a_q>0, R_q>0} a_q R_q/(N-4a_q) >= D,  with N-4a_q>0 for included terms.
   Lean: Codex sharp family C5(1,m,m/2,2,m) m<=30 + census N=9..11 |O|=1 + Mycielskians + glued. No head pipe."""
import subprocess
from fractions import Fraction as F
from _h import dec, GENG
from _opencap import build_K
from _bdef_construct import Cn, union_disjoint, mycielski, is_triangle_free
from _stark1 import odd_blowup, gmins

def metrics(adj, side, n):
    r=build_K(adj,side,n)
    if r is None: return None
    K,T=r; N=n
    O=[v for v in range(n) if T[v]>N]
    if len(O)!=1: return None
    o=O[0]; D=T[o]-N
    if D<=0: return None
    LB1=F(0); P5=F(0); denbad=0
    for q in range(n):
        if q==o: continue
        aq=K[o][q]; Rq=F(N)-T[q]
        if aq>0 and Rq>0:
            LB1+=aq*Rq/(aq+Rq)
            den=F(N)-4*aq
            if den<=0: denbad+=1
            else: P5+=aq*Rq/den
    return dict(o=o,D=D,LB1=LB1,P5=P5,denbad=denbad,
                ok1=(LB1>=D), ok65=(LB1>=F(6,5)*D), okP5=(P5>=D and denbad==0),
                r1=LB1/D, rP5=(P5/D))

def run(nm,n,E,acc):
    adj,cuts=gmins(n,E)
    for s in cuts:
        d=metrics(adj,s,n)
        if d is None: continue
        acc['tot']+=1
        if not d['ok1']: acc['f1']+=1
        if not d['ok65']: acc['f65']+=1
        if not d['okP5']: acc['fP5']+=1
        if acc['minrP5'] is None or d['rP5']<acc['minrP5']: acc['minrP5']=d['rP5']; acc['wit']=(nm,d['o'])

if __name__=="__main__":
    print("=== STAR-K1 / 6-5 / P5-DEFICIT (pure-K |O|=1) exact ===",flush=True)
    print("--- Codex sharp family C5(1,m,m/2,2,m) ---",flush=True)
    for m in (4,8,20,30):
        sizes=[1,m,m//2,2,m]; nn,E,adj,side=odd_blowup(5,sizes)
        d=metrics(adj,side,sum(sizes))
        if d is None: print(f"  m={m}: not |O|=1"); continue
        print(f"  C5(1,{m},{m//2},2,{m}) N={sum(sizes)}: r1={float(d['r1']):.5f} P5/D={float(d['rP5']):.5f} K1={d['ok1']} 6/5={d['ok65']} P5={d['okP5']} denbad={d['denbad']}",flush=True)
    d=metrics(*( (lambda t:(t[2],t[3],t[0]))(odd_blowup(5,[1,48,6,8,48])) )) if False else metrics(*(lambda r:(r[2],r[3],r[0]))(odd_blowup(5,[1,48,6,8,48])))
    print(f"  C5(1,48,6,8,48) N=111: r1={float(d['r1']):.5f} P5/D={float(d['rP5']):.5f} K1={d['ok1']} 6/5={d['ok65']} P5={d['okP5']}",flush=True)
    accm={'tot':0,'f1':0,'f65':0,'fP5':0,'minrP5':None,'wit':None}
    cur=(5,Cn(5))
    for _ in range(2): cur=mycielski(*cur); run(f"Myc{cur[0]}",cur[0],cur[1],accm)
    cur=(7,Cn(7)); cur=mycielski(*cur); run("MycC7",cur[0],cur[1],accm)
    print(f"  Mycielskians: |O|=1 cuts={accm['tot']} K1-FAIL={accm['f1']} 6/5-FAIL={accm['f65']} P5-FAIL={accm['fP5']} min-P5/D={float(accm['minrP5']) if accm['minrP5'] else None}",flush=True)
    accg={'tot':0,'f1':0,'f65':0,'fP5':0,'minrP5':None,'wit':None}
    g15=mycielski(7,Cn(7)); gr=mycielski(5,Cn(5))
    for iN,iE in [(5,Cn(5)),(7,Cn(7))]:
        for gN,gE in [g15,gr]:
            for br in [[(0,0)],[(0,1)],[(0,2)],[(0,0),(2,3)]]:
                if any(j>=gN for _,j in br): continue
                n,E=union_disjoint((iN,iE),(gN,gE))
                for (i,j) in br: E=E+[(i,iN+j)]
                if n>22 or not is_triangle_free(n,E): continue
                run(f"isl{iN}+gad{gN}",n,E,accg)
    print(f"  glued battery: |O|=1 cuts={accg['tot']} K1-FAIL={accg['f1']} 6/5-FAIL={accg['f65']} P5-FAIL={accg['fP5']} min-P5/D={float(accg['minrP5']) if accg['minrP5'] else None}",flush=True)
    for nnn in range(9,12):
        outg=subprocess.run([GENG,"-tc",str(nnn)],capture_output=True,text=True).stdout.split()
        acc={'tot':0,'f1':0,'f65':0,'fP5':0,'minrP5':None,'wit':None}
        for g6 in outg:
            n,E=dec(g6); run(g6,n,E,acc)
        print(f"  census N={nnn}: |O|=1 cuts={acc['tot']} K1-FAIL={acc['f1']} 6/5-FAIL={acc['f65']} P5-FAIL={acc['fP5']} min-P5/D={float(acc['minrP5']) if acc['minrP5'] else None} wit={acc['wit']}",flush=True)
