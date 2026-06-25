"""Extract the order-9 SDP optimizer x* (the 'fooling graphon') for moment-PSD + deficit + localizers,
then characterize it: edge density, support graphs, and the gap between best BCL-cut mono-density and
the TRUE maxcut mono-density on x* (the looseness)."""
import pickle, numpy as np, cvxpy as cp
import flag_engine as fe, flag_cutgen as fc, flag_localizer as floc, multi_loc as ml
C=pickle.load(open("cache_n9.pkl","rb")); states=C["states"]; ns=len(states); dedge=C["dedge"]; t=C["t"]
deftypes=C["deftypes"]; Pflats=[(lab,tt,Pf) for (lab,tt,sg,fl,s,Pf,Pi) in C["moments"]]
def maxcut(n,A):
    adj=[[(A[u]>>v)&1 for v in range(n)] for u in range(n)]; best=0
    for mask in range(1<<(n-1)):
        side=[(mask>>u)&1 for u in range(n)]; cut=sum(1 for u in range(n) for v in range(u+1,n) if adj[u][v] and side[u]!=side[v])
        best=max(best,cut)
    return best
dmono=np.array([2*(sum(1 for u in range(n) for v in range(u+1,n) if (A[u]>>v)&1)-maxcut(n,A))/(n*n) for (n,A) in states])
G=C["Gbase"].copy(); Mrows=[]; locs=ml.build_locs(C,["C5","C4","2K2","P4","K13"],t)
x=cp.Variable(ns,nonneg=True); eta=cp.Variable()
cons=[cp.sum(x)==1, dedge@x>=0.2486, dedge@x<=0.3197, G@x>=eta]
for (lab,tt,Pf) in Pflats: cons.append(cp.reshape(Pf@x,(tt,tt),order="C")>>0)
pr=cp.Problem(cp.Maximize(eta),cons); val=pr.solve()
xs=np.array(x.value).ravel()
print(f"order-9 SDP (moment-PSD+deficit, no loc cuts): eta={val:+.7f}", flush=True)
print(f"  x* d_edge = {float(dedge@xs):.4f}  (band [0.2486,0.3197])", flush=True)
print(f"  x* TRUE d_mono (sum x_G dmono_G) = {float(dmono@xs):.6f}  (target 0.08; brute band-max ~0.04-0.05)", flush=True)
top=np.argsort(xs)[::-1][:8]
print("  top support graphs (idx, x, d_edge, d_mono):", flush=True)
for i in top:
    if xs[i]>1e-4:
        n,A=states[i]; e=sum(1 for u in range(n) for v in range(u+1,n) if (A[u]>>v)&1)
        print(f"    {i}: x={xs[i]:.4f} d_edge={e/36:.3f} d_mono={dmono[i]:.4f}", flush=True)
print("DONE", flush=True)
