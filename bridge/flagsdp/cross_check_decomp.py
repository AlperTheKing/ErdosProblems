import numpy as np, pickle
from cutting_plane_u8 import maxcut_coloring
# Load decomp and witness; compute U8^LP(q) two ways and compare to compute_U8.
D9=pickle.load(open("u8_decomp.pkl","rb")); decomp=D9["decomp"]; nR=D9["nR"]
q=np.load("witness.npz",allow_pickle=True)["q"]
nJ=len(decomp)
# Build w_R(A,B) from q via decomp (as the LP does)
W=[dict() for _ in range(nR)]
for jj in range(nJ):
    qj=float(q[jj])
    if qj<=0: continue
    for (rid,Aset,Bset) in decomp[jj]:
        key=(Aset,Bset)
        W[rid][key]=W[rid].get(key,0.0)+qj/90.0
# min_mono per R = selfloop + (tot_off - exact maxcut)
U8_exact=0.0
for rid in range(nR):
    if not W[rid]: continue
    profs=set(); off={}; sl=0.0
    for (a,b),w in W[rid].items():
        profs.add(a); profs.add(b)
        if a==b: sl+=w
        else:
            aa,bb=tuple(sorted([a,b],key=lambda s:(len(s),sorted(s))))
            off[(aa,bb)]=off.get((aa,bb),0.0)+w
    # exact maxcut over profiles (brute, small)
    nodes=list(profs); idx={v:i for i,v in enumerate(nodes)}
    el=[(idx[a],idx[b],w) for (a,b),w in off.items()]
    nn=len(nodes); best=0.0
    if nn>0:
        for mask in range(1<<(nn-1)):
            c=0.0
            for a,b,w in el:
                if ((mask>>a)&1)!=((mask>>b)&1): c+=w
            if c>best: best=c
    U8_exact += sl + (sum(off.values())-best)
print(f"U8^LP(witness) [decomp, exact maxcut] = {U8_exact:.8e}")
print(f"  (compute_U8.py reported U_8 ~ 4.83e-4; 2/25={2/25:.6e})")
# Now the LP's per-R cut value with the maxcut_coloring used in add_rows
W2=[dict() for _ in range(nR)]; sup=np.where(q>1e-12)[0]
for jj in sup:
    qj=float(q[jj])
    for (rid,Aset,Bset) in decomp[jj]:
        key=(Aset,Bset) if (len(Aset),Aset)<=(len(Bset),Bset) else (Bset,Aset)
        W2[rid][key]=W2[rid].get(key,0.0)+qj/90.0
cm={}
for rid in range(nR):
    if not W2[rid]: continue
    profs=set(); off={}
    for (a,b),w in W2[rid].items():
        profs.add(a); profs.add(b)
        if a!=b: off[(a,b)]=off.get((a,b),0.0)+w
    cm[rid]=maxcut_coloring(list(profs),off)
# L_{R,c}(q) summed = sum over R of mono mass under cm
acc={rid:{} for rid in cm}
for jj in range(nJ):
    for (rd,Aset,Bset) in decomp[jj]:
        if rd in cm and cm[rd].get(Aset,0)==cm[rd].get(Bset,0):
            a=acc[rd]; a[jj]=a.get(jj,0)+1
Usum=0.0
for rid,a in acc.items():
    js=np.fromiter(a.keys(),int,len(a)); cs=np.fromiter(a.values(),float,len(a))/90.0
    Usum += float(cs@q[js]) if len(js) else 0.0
print(f"sum_R L_(R,sigma*)(witness) [LP cut, maxcut_coloring] = {Usum:.8e}")
print(f"diff (LP cut - exact min_mono) = {Usum-U8_exact:+.3e}  (should be >=0; 0 if sigma* optimal)")
