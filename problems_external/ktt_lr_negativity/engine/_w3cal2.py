import random, subprocess, time, collections, sys
sys.path.insert(0,".")
from hive_poly import analyze
EX="./lr_hive.exe"
def rpart(w,k,rng,distinct=True):
    while True:
        cuts=sorted(rng.sample(range(1,w),k-1))
        p=[];prev=0
        for c in cuts+[w]:
            p.append(c-prev);prev=c
        p.sort(reverse=True)
        if not distinct or len(set(p))==k: return tuple(p)
rng=random.Random(31); tr=[]
for _ in range(20000):
    wl=rng.randint(21,30); wm=rng.randint(21,30)
    tr.append((rpart(wl,6,rng),rpart(wm,6,rng),rpart(wl+wm,6,rng,False)))
s=lambda p:",".join(map(str,p))
open("_w3cal2.txt","w").write("\n".join(f"{s(a)};{s(b)};{s(c)};25" for a,b,c in tr)+"\n")
log=open("_w3cal2.log","w",buffering=1)
t=time.time(); out=subprocess.run([EX,"--batch","_w3cal2.txt"],capture_output=True,text=True).stdout.split("\n")
log.write("screen(cap25) %d in %.2fs\n"%(len(tr),time.time()-t))
cs=[(tr[i],int(v)) for i,v in enumerate(out) if v.strip().isdigit() and int(v)>0]
log.write("nonzero&c<=25: %d\n"%len(cs))
band=[(t_,v) for t_,v in cs if 8<=v<=25]
log.write("c in [8,25]: %d\n"%len(band)); rng.shuffle(band)
t0=time.time(); H=collections.Counter(); K=collections.Counter(); best=[];n=0
for (lam,mu,nu),c in band:
    if time.time()-t0>150: break
    r=analyze(lam,mu,nu,K=18,seed=5)
    if r is None: continue
    n+=1; H[r["dim_lo"]]+=1; K[r["maxden"]]+=1
    best.append((c-r["dim_lo"],c,r["dim_lo"],r["maxden"],lam,mu,nu))
log.write("analyzed %d in %.1fs -> %.2f s/triple\n"%(n,time.time()-t0,(time.time()-t0)/max(n,1)))
log.write("dim hist %s\nden hist %s\n"%(sorted(H.items()),sorted(K.items())))
best.sort()
for z in best[:5]: log.write("c-dim=%d c=%d dim=%d den=%d %s %s %s\n"%z)
log.write("DONE\n")
