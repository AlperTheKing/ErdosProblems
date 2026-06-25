import itertools

# Fast beta on a fixed vertex set via meet-in-the-middle-free incremental Gray-code maxcut.
# For up to ~15 active vertices. We compute MaxCut by iterating colorings in Gray code,
# maintaining the cut value incrementally using adjacency bitmasks.

def maxcut_graymask(active, adjmask):
    # active: sorted list of vertices; adjmask[v] = bitmask of neighbors (over full labels)
    # Relabel to 0..k-1
    vl=active
    k=len(vl)
    pos={v:i for i,v in enumerate(vl)}
    # local adjacency: ladj[i] = bitmask over local indices
    ladj=[0]*k
    medges=0
    for i,v in enumerate(vl):
        nb=adjmask[v]
        for j in range(i+1,k):
            w=vl[j]
            if (nb>>w)&1:
                ladj[i]|=(1<<j); ladj[j]|=(1<<i); medges+=1
    if k==0: return 0,0
    # Gray code over assignments of side bits to local vertices 0..k-1.
    # color bitmask 'c'; cut = number of edges with endpoints differently colored.
    # Maintain cut incrementally: flipping vertex i changes cut by
    #   (neighbors of i on same side) - (neighbors of i on opposite side) BEFORE flip.
    c=0
    # initial cut=0 (all same side)
    cut=0
    best=0
    # number of neighbors of i currently on the SAME side as i:
    # We'll recompute via popcount of (ladj[i] & samemask). Maintain 'color' c.
    for step in range(1,(1<<k)):
        i=(step & -step).bit_length()-1  # index of bit that flips in gray code
        # before flipping i: neighbors of i that are same-colored contribute, opposite contribute.
        nb=ladj[i]
        # same-colored neighbors: those j with bit (c>>j&1)==(c>>i&1)
        ci=(c>>i)&1
        # mask of vertices colored same as i:
        # same = (c if ci else ~c) restricted to k bits
        full=(1<<k)-1
        same = (c if ci else (~c)&full)
        same_nb = nb & same
        opp_nb = nb & (~same & full)
        # flipping i: same become cut(+), opp become uncut(-)
        cut += bin(same_nb).count("1") - bin(opp_nb).count("1")
        c ^= (1<<i)
        if cut>best: best=cut
    return best, medges

def beta_fast(active, adjmask):
    mc,m=maxcut_graymask(active,adjmask)
    return m-mc

def min5drop_fast(N, edges):
    adjmask=[0]*N
    for (u,v) in edges:
        adjmask[u]|=1<<v; adjmask[v]|=1<<u
    allv=list(range(N))
    bG=beta_fast(allv,adjmask)
    best=None; bestS=None
    for S in itertools.combinations(range(N),5):
        sm=set(S)
        rem=[v for v in range(N) if v not in sm]
        bGS=beta_fast(rem,adjmask)
        d=bG-bGS
        if best is None or d<best:
            best=d; bestS=S
            if best<0: break
    return best,bestS,bG

if __name__=="__main__":
    # sanity vs slow
    from h2_redteam import min5drop
    def c5b3():
        E=[]
        for i in range(5):
            j=(i+1)%5
            for a in range(3):
                for b in range(3):
                    E.append((i*3+a,j*3+b))
        return sorted(set(tuple(sorted(e)) for e in E))
    E=c5b3()
    print("fast", min5drop_fast(15,E))
    print("slow", min5drop(15,E))
