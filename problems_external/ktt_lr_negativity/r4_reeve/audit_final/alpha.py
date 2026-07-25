"""Independent check of the STRUCTURAL route: compute the Berline-Vergne edge
coefficient alpha for each of the 99 r=4 normal pairs via the closed-form Gram
formula in UNIFORM_CODIM2_POSITIVITY.md, verify a1 = Lambda.alpha on real hive
polytopes, and confirm every alpha >= 1/12 with atlas minimum."""
import json, random
from fractions import Fraction as F
from math import gcd
from edges import NORMALS, IDXPAIRS, lambda_vec
from hive import constraints,_partial
from scan import coeffs
from out_of_sample import hive_to_nb

def dot(u,v): return sum(a*b for a,b in zip(u,v))

def sat_index(u,v):
    minors=[u[0]*v[1]-u[1]*v[0], u[0]*v[2]-u[2]*v[0], u[1]*v[2]-u[2]*v[1]]
    g=0
    for m in minors: g=gcd(g,abs(m))
    return g

def alpha_formula(u,v):
    q=sat_index(u,v)
    A=dot(u,u); Bb=dot(v,v); C=dot(u,v)
    if q==1:
        return F(1,4) - F(C,12)*(F(1,A)+F(1,Bb))
    else:  # q==2
        s=tuple((u[t]+v[t]) for t in range(3))   # 2*s_true
        t_=tuple((u[t]-v[t]) for t in range(3))  # 2*t_true
        # s_true=(u+v)/2 etc; <s_true,s_true>=<s,s>/4
        As=F(dot(s,s),4); Bt=F(dot(t_,t_),4)
        return F(As+2*Bt, 6*(As+Bt))

def build_atlas():
    at={}
    for k,(i,j) in enumerate(IDXPAIRS):
        at[k]=alpha_formula(NORMALS[i],NORMALS[j])
    return at

def main():
    at=build_atlas()
    vals=list(at.values())
    print("num_edge_types=",len(vals))
    print("min_alpha=",min(vals)," max_alpha=",max(vals))
    print("all_alpha_ge_1/12:",all(a>=F(1,12) for a in vals))
    print("all_alpha_gt_0:",all(a>0 for a in vals))
    # index-2 pairs
    idx2=[k for k,(i,j) in enumerate(IDXPAIRS) if sat_index(NORMALS[i],NORMALS[j])==2]
    print("num_index2_pairs=",len(idx2)," their_alpha=",sorted(set(at[k] for k in idx2)))
    # verify a1 = Lambda.alpha on fresh hives
    random.seed(11)
    def rp(mp): return sorted([random.randint(1,mp) for _ in range(4)],reverse=True)
    def mk(lam,mu):
        s=[lam[k]+mu[k] for k in range(4)]
        for _ in range(random.randint(0,12)):
            k=random.randint(0,2)
            if s[k]>s[k+1] and s[k]>0: s[k]-=1;s[k+1]+=1
            s=sorted(s,reverse=True)
        return s
    checked=0; badformula=0; bound12=0; bound19=0
    for _ in range(600):
        lam=rp(18);mu=rp(18);nu=mk(lam,mu)
        if _partial(nu,4)!=_partial(lam,4)+_partial(mu,4): continue
        a0,a1,a2,a3,Ls=coeffs(lam,mu,nu)
        if Ls[1]==0 or a3<=0: continue
        b=hive_to_nb(lam,mu,nu)
        if b in (None,"BADNORMAL"): continue
        try: Lam,verts=lambda_vec(NORMALS,b)
        except AssertionError: continue
        checked+=1
        val=sum(F(Lam[k])*at[k] for k in range(len(Lam)))
        if val!=a1: badformula+=1;
        tot=sum(Lam)
        if not (a1>=F(1,12)*tot): bound12+=1
        if not (a1>=F(1,9)*tot):  bound19+=1
    print(f"fresh_hives_checked={checked}")
    print(f"a1 != Lambda.alpha_formula fails = {badformula}")
    print(f"a1 < (1/12)*totlen fails = {bound12}")
    print(f"a1 < (1/9)*totlen fails  = {bound19}")

if __name__=="__main__":
    main()
