from harness import *
# The optimal h=8 base graph (ratio 0.781)
h8=[(0,4),(1,5),(0,6),(1,6),(2,6),(3,6),(2,7),(3,7),(4,7),(5,7)]
b,e,mc,d,tf=evalone(8,h8)
print(f"h8 base: N=8 e={e} beta={b} maxcut={mc} dens={d:.4f} tf={tf} ratio={25*b/64:.3f}")

def blowup(N,edges,t):
    NN=N*t; ee=[]
    for u,v in edges:
        for a in range(t):
            for c in range(t):
                ee.append((u*t+a,v*t+c))
    return NN,sorted(set((min(x,y),max(x,y)) for x,y in ee))

for t in [2,3]:
    N,e=blowup(8,h8,t)
    b,ee,mc,d,tf=evalone(N,e)
    print(f"h8[{t}]: N={N} e={ee} beta={b} dens={d:.4f} tf={tf} band={in_band(N,ee)} N^2/25={N*N/25:.2f} ratio={25*b/(N*N):.3f}")
    if t==3:
        print("EDGES_h8x3",e)
