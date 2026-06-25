from beta import *
from search_small import gen
import sys

def remove_vertex(adj,n,v):
    # relabel removing v
    keep=[u for u in range(n) if u!=v]
    idx={u:i for i,u in enumerate(keep)}
    m=n-1
    adj2=[0]*m
    for u in keep:
        for w in keep:
            if (adj[u]>>w)&1:
                adj2[idx[u]]|=1<<idx[w]
    return adj2,m

def degree(adj,n,v):
    return bin(adj[v]).count('1')

def check_deletion_bound(N):
    viol=0; checked=0
    tight_min_deg=0
    for adj,n in gen(N):
        b=beta(adj,n)
        for v in range(n):
            adj2,m=remove_vertex(adj,n,v)
            b2=beta(adj2,m)
            if b > b2 + degree(adj,n,v)//2:
                viol+=1
        checked+=1
    return checked, viol

if __name__=="__main__":
    for N in range(5,11):
        c,v=check_deletion_bound(N)
        print(f"N={N}: checked {c}, deletion-bound violations={v}")
