#!/usr/bin/env python3
"""ADVERSARIAL: evaluate the FULL dual cert combination Phi(W) = sum lam g_r(W) + sum gam m_j(W) + band(W)
at the GRAPHON level, EXACTLY, on triangle-free band step-graphons W, and test whether Phi(W) <= delta.

The cert verifies Phi(H) <= delta on finite n=9 states H. The CLOSURE claims this implies Phi(W) <= delta
for all band graphons W. If we find a triangle-free band graphon W with Phi(W) > delta, the finite-to-graphon
transfer is BROKEN (cert unsound). If always Phi(W) <= delta, that supports soundness.

Graphon deficit g_r(W): roots R drawn with part-weights (must induce sigma), each non-root point x has a
profile class = its adjacency pattern to the k roots; q(x) = p(class) in {0,1} (side-0 prob). Then
  mono_edge(R) = E_{x,y indep}[ adj_W(x,y) * ( q_x q_y + (1-q_x)(1-q_y) ) ] / E_{x,y}[ adj_W(x,y) ]   ??? NO.
gr_exact divides by Cm2 = C(m,2) (ALL non-root pairs), and sums q_u q_v+(1-q_u)(1-q_v) ONLY over ADJACENT
pairs. So per roots R:  g_r contribution = ( sum_{adj pairs} mono ) / C(m,2) - t.  Graphon analog:
  inner(R) = E_{x,y indep over W minus roots}[ adj_W(x,y) * ( q_x q_y + (1-q_x)(1-q_y) ) ] - t,
then g_r(W) = E_R[ inner(R) ]  (R ranges over ordered root part-assignments inducing sigma, weight=prod alpha).
This matches the n->inf limit of gr_exact (Cm2 ~ m^2/2 and the double sum ~ m^2/2 * E[...]).

Moment m_j(W) = vv^T M^sigma(W) vv with M the PSD Gram form from g1_exact_psd.build_M.
band(W) = mu*(e_W - LO) + nu*(HI - e_W); cert has mu=nu=0.
"""
import pickle, itertools, sys
from fractions import Fraction as Fr
import flag_engine as fe
import flag_sdp as fs
import g1_exact_psd as g1
import prove_cert as pc

LO = Fr(1243,5000); HI = Fr(3197,10000); T = Fr(2,25)

def profile_class(parts_root_adj):
    # given a tuple of bools (adjacent to root i?), return frozenset of root-indices adjacent
    return frozenset(i for i,b in enumerate(parts_root_adj) if b)

def gr_graphon(k, Asig, pmap, m, Tadj, alpha):
    """Exact graphon deficit g_r(W) for step graphon W=(m parts, Tadj 0/1 template, alpha weights)."""
    sigma=(k,Asig)
    # precompute adjacency between parts a,b (a!=b) per template; same part => nonadjacent
    def padj(a,b):
        return a!=b and ((Tadj[a]>>b)&1)
    g=Fr(0)
    for p in itertools.product(range(m),repeat=k):
        # roots induce sigma?
        ok=True
        for a in range(k):
            for b in range(a+1,k):
                e=1 if padj(p[a],p[b]) else 0
                sg=1 if (Asig[a]>>b)&1 else 0
                if e!=sg: ok=False;break
            if not ok:break
        if not ok: continue
        wR=Fr(1)
        for a in p: wR*=alpha[a]
        if wR==0: continue
        # q(class) for each part c: profile class of a point in part c = its adjacency to roots
        qpart=[]
        for c in range(m):
            cls=profile_class(tuple(padj(c,p[i]) for i in range(k)))
            qpart.append(pmap.get(cls, Fr(1,2)))
        # inner = E_{x,y indep}[ adj_W(x,y)*(q_x q_y + (1-q_x)(1-q_y)) ] - t
        # x in part cx w.prob alpha[cx], y in part cy w.prob alpha[cy]; adj only if padj(cx,cy)
        inner=Fr(0)
        for cx in range(m):
            for cy in range(m):
                if padj(cx,cy):
                    qx=qpart[cx]; qy=qpart[cy]
                    inner+=alpha[cx]*alpha[cy]*(qx*qy+(1-qx)*(1-qy))
        inner-=T
        g+=wR*inner
    return g

def edge_density_graphon(m,Tadj,alpha):
    s=Fr(0)
    for i in range(m):
        for j in range(m):
            if i!=j and (Tadj[i]>>j)&1: s+=alpha[i]*alpha[j]
    return s

def main():
    C=pc.load(9)
    moms=C["moments"]
    info={lab:(sigma,flags,s) for (lab,tt,sigma,flags,s,Pf,Pint) in moms}
    cert=pickle.load(open("dual_cert_n9.pkl","rb"))
    prov=cert["prov"]; ndix=cert["ndix"]; nmix=cert["nmix"]
    lam=[Fr(x) for x in cert["lam"]]; gam=[Fr(x) for x in cert["gam"]]
    mu=Fr(cert["mu"]); nu=Fr(cert["nu"])
    delta=Fr(cert["maxPhi_num"],cert["maxPhi_den"])
    print(f"delta = {float(delta):.6e}  mu={mu} nu={nu}", flush=True)

    # graphons to test: cert claims for ALL triangle-free band graphons.
    tests=[]
    tests.append(("C5_equal",5,g1.cyc(5),[Fr(1,5)]*5))
    tests.append(("C7_equal",7,g1.cyc(7),[Fr(1,7)]*7))
    tests.append(("C9_equal",9,g1.cyc(9),[Fr(1,9)]*9))
    tests.append(("Petersen",10,g1.petersen(),[Fr(1,10)]*10))
    a=Fr(3,14); b=Fr(5,28)
    tests.append(("C5_w_band",5,g1.cyc(5),[a,a,a,b,b]))
    # weighted C7 to land in band, several tilts
    import random
    random.seed(3)
    def cyc(mm): return g1.cyc(mm)
    # parametric weighted C5: weights (x,x,x,y,y) scanned to hit band densities
    for num in range(1,40):
        x=Fr(num,200)
        # 3x+2y=1 -> y=(1-3x)/2
        y=(1-3*x)/2
        if y<=0: continue
        de=edge_density_graphon(5,cyc(5),[x,x,x,y,y])
        if LO<=de<=HI:
            tests.append((f"C5w_x{num}",5,cyc(5),[x,x,x,y,y]))

    # precompute graphon Gram M per sigma per template inside loop
    worst=(Fr(-10**9),"")
    for (name,m,Tadj,alpha) in tests:
        de=edge_density_graphon(m,Tadj,alpha)
        tf=g1.tri_free(m,Tadj)
        if not tf:
            print(f"[skip {name}: not tri-free]"); continue
        Phi=Fr(0)
        # deficits
        for c,i in enumerate(ndix):
            if lam[c]==0: continue
            pr=prov[i]
            if pr[0]=="deficit":
                _,k,A,cls,pp=pr; pmap={cls[ii]:Fr(int(pp[ii])) for ii in range(len(cls))}
            else:
                _,k,A,pmap=pr
            Phi+=lam[c]*gr_graphon(k,A,pmap,m,Tadj,alpha)
        # moments
        Mcache={}
        for c,j in enumerate(nmix):
            if gam[c]==0: continue
            pr=prov[j]; _,lab,sigma,s,vv=pr
            if lab not in Mcache:
                sig2,flags,s2=info[lab]
                M,_=g1.build_M(sigma,flags,s,m,Tadj,alpha)
                Mcache[lab]=(M,len(flags))
            M,t=Mcache[lab]
            vvr=[Fr(x) for x in vv]
            q=Fr(0)
            for ii in range(t):
                if vvr[ii]==0: continue
                vi=vvr[ii]
                row=M[ii]
                for jj in range(t):
                    if vvr[jj]!=0 and row[jj]!=0:
                        q+=vi*row[jj]*vvr[jj]
            Phi+=gam[c]*q
        Phi+=mu*(de-LO)+nu*(HI-de)
        inband = LO<=de<=HI
        flag = "OK" if Phi<=delta else "**VIOLATION**"
        print(f"{name:>12}  d_edge={float(de):.4f} inband={inband} Phi(W)={float(Phi):+.6e} {flag} (Phi-delta={float(Phi-delta):+.3e})",flush=True)
        if inband and Phi>worst[0]:
            worst=(Phi,name)
    print(f"\nWORST in-band Phi(W) = {float(worst[0]):+.6e} at {worst[1]}  (delta={float(delta):.6e})")
    print("CERT GRAPHON-SOUND on tested band graphons" if worst[0]<=delta else "CERT VIOLATED at graphon level")

if __name__=="__main__": main()
