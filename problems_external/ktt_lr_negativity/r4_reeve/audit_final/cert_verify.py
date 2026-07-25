"""Independent replay of the r=4 edge-basis certificate linear algebra.
Own code, own B construction, exact Fraction. No import of the checker."""
import json, hashlib
from fractions import Fraction as F
from math import gcd

CERT="E:/Projects/ErdosProblems/problems_external/ktt_lr_negativity/r4_reeve/q2_basis_witness_certificate.json"

def prim(v):
    g=0
    for x in v: g=gcd(g,abs(x))
    if g==0: return tuple(v)
    v=tuple(x//g for x in v)
    # canonical sign: first nonzero positive
    for x in v:
        if x!=0:
            if x<0: v=tuple(-y for y in v)
            break
    return v

def cross(a,b):
    return (a[1]*b[2]-a[2]*b[1], a[2]*b[0]-a[0]*b[2], a[0]*b[1]-a[1]*b[0])

def rank(rows):
    rows=[[F(x) for x in r] for r in rows]
    if not rows: return 0
    ncol=len(rows[0]); r=0
    rows=[row[:] for row in rows]
    pr=0
    for c in range(ncol):
        piv=None
        for i in range(pr,len(rows)):
            if rows[i][c]!=0: piv=i;break
        if piv is None: continue
        rows[pr],rows[piv]=rows[piv],rows[pr]
        pv=rows[pr][c]
        rows[pr]=[x/pv for x in rows[pr]]
        for i in range(len(rows)):
            if i!=pr and rows[i][c]!=0:
                f=rows[i][c]
                rows[i]=[a-f*b for a,b in zip(rows[i],rows[pr])]
        pr+=1
        if pr==len(rows): break
    return pr

def main():
    raw=open(CERT,'rb').read()
    print("certificate_sha256=",hashlib.sha256(raw).hexdigest())
    c=json.loads(raw)
    normals=[tuple(n) for n in c['normals']]
    pairs=[tuple(p) for p in c['nonparallel_pairs']]   # list of [i,j] index pairs? or normal pairs?
    print("pairs[0]=",pairs[0], " len pairs=",len(pairs))
    # detect pair encoding: indices into normals, or normal vectors
    if all(isinstance(p[0],int) for p in pairs):
        idxpairs=[(p[0],p[1]) for p in pairs]
    else:
        # pairs are [normal_i, normal_j]
        nlookup={tuple(n):k for k,n in enumerate(normals)}
        idxpairs=[(nlookup[tuple(p[0])],nlookup[tuple(p[1])]) for p in pairs]
    # Build B: 45 x 99. For pair k=(i,j): u=prim(n_i x n_j); block i += u, block j += -u
    NP=len(idxpairs)
    B=[[0]*NP for _ in range(45)]
    for k,(i,j) in enumerate(idxpairs):
        u=prim(cross(normals[i],normals[j]))
        for t in range(3):
            B[3*i+t][k]+=u[t]
            B[3*j+t][k]-=u[t]
    rB=rank(B)
    print("rank(B)=",rB," ker_dim=",NP-rB)
    # M from witnesses' edge_lengths
    W=c['witnesses']
    M=[w['edge_lengths'] for w in W]
    print("num_witnesses=",len(M)," edge_vec_len=",len(M[0]))
    rM=rank(M)
    print("rank(M)=",rM)
    # B . M^T == 0 ?
    bad=0
    for w in M:
        for brow in B:
            s=sum(bx*wx for bx,wx in zip(brow,w))
            if s!=0: bad+=1;break
    print("witness_edge_vectors_in_ker(B): ", "ALL" if bad==0 else f"{bad} FAIL")
    # mu
    mu=[F(s) for s in c['mu']]
    print("len(mu)=",len(mu)," min(mu)=",min(mu)," any_negative=",any(x<0 for x in mu))
    # a = recorded a1 of witnesses
    a=[F(w['a1']) for w in W]
    # M . mu == a ?
    okmu=True
    for w,av in zip(M,a):
        s=sum(F(wx)*mx for wx,mx in zip(w,mu))
        if s!=av: okmu=False; print("  Mmu!=a for a witness",s,av)
    print("M.mu == a (recorded a1) :", okmu)
    # rowspan(M)==ker(B): rank(M)+rank(B)==99 and M rows in ker B
    print("rowspan(M)==ker(B):", (rM+rB==NP) and (bad==0))
    # self-consistency: each witness recorded a1 == interpolation of L_0..5
    idfail=0
    for w in W:
        L=w['L_0_through_5']
        a1i=F(-11*L[0]+18*L[1]-9*L[2]+2*L[3],6)
        if a1i!=F(w['a1']): idfail+=1
        # also a1 == Lambda . mu
        s=sum(F(wx)*mx for wx,mx in zip(w['edge_lengths'],mu))
        if s!=F(w['a1']): idfail+=1
    print("witness a1==interp==Lambda.mu :", "ALL OK" if idfail==0 else f"{idfail} FAIL")

if __name__=="__main__":
    main()
