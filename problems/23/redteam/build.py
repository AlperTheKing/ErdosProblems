import itertools
from beta_tools import is_triangle_free, beta, maxcut_fast

def c5_blowup(n):
    # parts 0..4 each size n; vertex id = part*n + i
    N=5*n
    edges=[]
    for p in range(5):
        q=(p+1)%5
        for i in range(n):
            for j in range(n):
                edges.append((p*n+i, q*n+j))
    return N, edges

for n in range(1,5):
    N,e=c5_blowup(n)
    tf,_=is_triangle_free(N,e)
    b,ee,mc=beta(N,e)
    dens=2*ee/(N*N)
    print(f"C5[{n}] N={N} e={ee} tf={tf} beta={b} (n^2={n*n}) maxcut={mc} density={dens:.4f}")
