import sys

def parts_exact5(N):
    out=[]
    def rec(rem, k, mx, cur):
        if k==0:
            if rem==0: out.append(tuple(cur))
            return
        lo = max(1, -(-rem//k))
        hi = min(mx, rem-(k-1))
        for p in range(hi, lo-1, -1):
            rec(rem-p, k-1, p, cur+[p])
    rec(N,5,N,[])
    return out

def subpartitions(nu):
    res=[]
    r=len(nu)
    def rec(i, prev, cur):
        if i==r:
            res.append(tuple(x for x in cur if x>0))
            return
        for v in range(min(prev, nu[i]), -1, -1):
            rec(i+1, v, cur+[v])
    rec(0, nu[0], [])
    return res

def triples_for_nu(nu):
    N=sum(nu)
    subs=subpartitions(nu)
    bysum={}
    for s in subs: bysum.setdefault(sum(s),[]).append(s)
    out=[]
    for a in range(0, N//2+1):
        b=N-a
        if a not in bysum or b not in bysum: continue
        A=bysum[a]; B=bysum[b]
        if a==b:
            for i,l in enumerate(A):
                for m in A[i:]:
                    out.append((l,m,nu))
        else:
            for l in A:
                for m in B:
                    out.append((l,m,nu))
    return out

if __name__=="__main__":
    NMAX=int(sys.argv[1]) if len(sys.argv)>1 else 26
    tot=0; nunum=0; per={}
    for N in range(5, NMAX+1):
        for nu in parts_exact5(N):
            nunum+=1
            c=len(triples_for_nu(nu))
            per[N]=per.get(N,0)+c
            tot+=c
    print("nu count",nunum,"triples(unordered lam,mu)",tot)
    for N in sorted(per): print(N, per[N])
