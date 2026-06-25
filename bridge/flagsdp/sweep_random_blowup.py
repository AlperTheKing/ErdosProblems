import random
from fractions import Fraction as F
from sweep_dmono_audit import U8_from_graph_weighted, dmono_weighted
from validate_dmono_le_u8 import cyc, petersen
random.seed(7)
C5C5=[0]*10
for i in range(5):
    C5C5[i]|=1<<((i+1)%5); C5C5[(i+1)%5]|=1<<i
    C5C5[5+i]|=1<<(5+(i+1)%5); C5C5[5+(i+1)%5]|=1<<(5+i)
templates=[("C5",5,cyc(5)),("C7",7,cyc(7))]
worst=1e9; nviol=0; ntest=0
for (nm,n,A) in templates:
    for trial in range(20):
        raw=[random.randint(1,9) for _ in range(n)]
        s=sum(raw); vw=[F(r,s) for r in raw]
        dm=dmono_weighted(n,A,vw)
        if dm<=1e-15: continue
        U8=U8_from_graph_weighted(n,A,vw)
        gap=U8-dm; ntest+=1
        if gap<worst: worst=gap
        if gap< -1e-9:
            nviol+=1
            print("VIOLATION %s weights=%s d_mono=%.6e U8=%.6e gap=%.3e"%(nm,[str(x) for x in vw],dm,U8,gap),flush=True)
print("random-blowup C5/C7: tested=%d violations=%d worst gap(U8-dmono)=%.4e"%(ntest,nviol,worst),flush=True)
