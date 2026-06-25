import maxell_sumell_test as T
for N in [7,8,9]:
    inst=T.connectedB_ells(N)
    viol=0; worst=0.0; wd=None
    for (n,ells) in inst:
        mx=max(ells); S=sum(ells); r=mx*S/(n*n)
        if r>1+1e-9: viol+=1
        if r>worst: worst=r; wd=(n,sorted(ells),mx,S)
    print(f"N={N}: inst={len(inst)} worst(max*sum/N^2)={worst:.4f} viol={viol} wd={wd}")
print("SMALLDONE")
