import itertools, sys
from functools import lru_cache

def edges_of(adj, n):
    E=[]
    for i in range(n):
        for j in range(i+1,n):
            if adj[i]>>j &1: E.append((i,j))
    return E

def num_edges(adj,n):
    return sum(bin(adj[i]>>(i+1)).count('1') for i in range(n))

def maxcut(adj, n):
    # brute force over 2^(n-1) partitions (fix vertex 0 in side 0)
    E = edges_of(adj,n)
    best=0
    for mask in range(1<<(n-1)):
        full = mask<<1  # vertex0 = side0
        c=0
        for (i,j) in E:
            if ((full>>i)&1)!=((full>>j)&1): c+=1
        if c>best: best=c
    return best

def beta(adj,n):
    return num_edges(adj,n)-maxcut(adj,n)

def maxcut_fast(adj,n):
    # iterate assignment by incremental? keep simple, n<=16
    E=edges_of(adj,n)
    deg_e=E
    best=0
    for mask in range(1<<(n-1)):
        full=mask<<1
        c=0
        for (i,j) in deg_e:
            if ((full>>i)^(full>>j))&1: c+=1
        if c>best:best=c
    return best

def is_triangle_free(adj,n):
    for i in range(n):
        Ni=adj[i]
        j=i+1
        while j<n:
            if (Ni>>j)&1:
                if Ni & adj[j]: return False
            j+=1
    return True

# C5 blowup C5[m1..m5]
def c5_blowup(ms):
    n=sum(ms)
    # assign blocks
    blocks=[]
    idx=0
    for m in ms:
        blocks.append(list(range(idx,idx+m))); idx+=m
    adj=[0]*n
    for c in range(5):
        nxt=(c+1)%5
        for a in blocks[c]:
            for b in blocks[nxt]:
                adj[a]|=1<<b; adj[b]|=1<<a
    return adj,n

if __name__=="__main__":
    for nn in [1,2,3]:
        adj,n=c5_blowup([nn]*5)
        print("C5[",nn,"] N=",n," e=",num_edges(adj,n)," beta=",beta(adj,n)," n^2=",nn*nn)
