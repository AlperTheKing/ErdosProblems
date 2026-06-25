import time, itertools
import prove_cert as pc, flag_engine as fe
C=pc.load(9); states9=C["states"]
t0=time.time()
canon9={ fe.canonical(9,A): i for i,(n,A) in enumerate(states9) }
print(f"canon9 build (1897 canonicals): {time.time()-t0:.2f}s",flush=True)
g10=fe.enumerate_graphs(10,triangle_free=True)
print(f"T_10={len(g10)}",flush=True)
t0=time.time()
for j in range(200):
    n,A=g10[j]
    for v in range(10):
        verts=[u for u in range(10) if u!=v]
        m,B=fe.induced(A,verts); key=fe.canonical(m,B); hi=canon9.get(key,-1)
dt=time.time()-t0
print(f"D 200 J (2000 canon9): {dt:.2f}s -> full ~{dt/200*12172:.0f}s",flush=True)
