import time, flag_engine as fe
t0=time.time()
g10 = fe.enumerate_graphs(10, triangle_free=True)
print(f"T_10 triangle-free count = {len(g10)} in {time.time()-t0:.1f}s")
print("sample state[0]:", g10[0], " type:", type(g10[0]))
# test canonical + induced
n,A = g10[100]
verts=[0,1,2,3,4,5,6,7,8]
m,B = fe.induced(A, verts)
key = fe.canonical(m, B)
print(f"induced 9-vtx delete-v9: m={m}, canonical key type={type(key)}")
