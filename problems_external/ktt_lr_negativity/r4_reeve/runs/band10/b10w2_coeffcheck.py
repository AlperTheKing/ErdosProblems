import random, sys, json
from fractions import Fraction
sys.path.insert(0,'.')
import hive4
rng=random.Random(4242)
def tri(g):
    a,b,c=g[0:3],g[3:6],g[6:9]
    D=(3*c[2]+2*c[1]+c[0])-(3*a[2]+2*a[1]+a[0])-(3*b[2]+2*b[1]+b[0])
    if D%4: return None
    k=D//4; l4=k if k>=0 else 0; n4=-k if k<0 else 0
    return ([l4+a[2]+a[1]+a[0],l4+a[2]+a[1],l4+a[2],l4],
            [b[2]+b[1]+b[0],b[2]+b[1],b[2],0],
            [n4+c[2]+c[1]+c[0],n4+c[2]+c[1],n4+c[2],n4])
n=0; mina1=None; mina2=None; mina3=None; argmin=None; bad=[]
while n<800:
    g=[rng.randint(0,10) for _ in range(9)]
    t=tri(g)
    if t is None: continue
    r=hive4.analyze(*t)
    if r["dim"]!=3: continue
    n+=1
    P=list(r["poly"])+[Fraction(0)]*(4-len(r["poly"]))
    if mina1 is None or P[1]<mina1: mina1=P[1]; argmin=(g,r["c"],str(r["volume_normalized"]),r["hstar"])
    if mina2 is None or P[2]<mina2: mina2=P[2]
    if mina3 is None or P[3]<mina3: mina3=P[3]
    if min(P)<0: bad.append((g,[str(x) for x in P]))
    if not r["verified"]: bad.append(("interp_fail",g))
print(json.dumps({"n_dim3":n,"min_a1":str(mina1),"min_a2":str(mina2),"min_a3":str(mina3),
                  "argmin_a1":[argmin[0],argmin[1],argmin[2],argmin[3]],
                  "n_negative_or_failed":len(bad),"bad":bad[:5]},indent=1))
