import subprocess, sys, os
from beta import *
from cut3 import cut3, neighbors

GENG=r"E:\Projects\ErdosProblems\tools\nauty2_8_9\geng.exe"

def parse_g6_line(line):
    line=line.strip()
    if not line: return None
    s=line.encode()
    # nauty graph6 decode
    data=s
    p=0
    n=data[0]-63
    p=1
    bits=[]
    for c in data[p:]:
        v=c-63
        for k in range(5,-1,-1):
            bits.append((v>>k)&1)
    adj=[0]*n
    idx=0
    for j in range(1,n):
        for i in range(j):
            if idx<len(bits) and bits[idx]:
                adj[i]|=1<<j; adj[j]|=1<<i
            idx+=1
    return adj,n

def gen(n, mine=0, maxe=None, trianglefree=True):
    args=[GENG, '-q']
    if trianglefree: args.append('-t')  # girth>=4 means triangle-free
    args.append(str(n))
    if maxe is not None:
        args.append(f"{mine}:{maxe}")
    out=subprocess.run(args, capture_output=True, text=True)
    for line in out.stdout.splitlines():
        r=parse_g6_line(line)
        if r: yield r

def max_beta_over_n(N, verbose=False):
    best=-1; bestadj=None
    cnt=0
    for adj,n in gen(N):
        cnt+=1
        b=beta(adj,n)
        if b>best:
            best=b; bestadj=(list(adj),n)
    return best, bestadj, cnt

if __name__=="__main__":
    N=int(sys.argv[1])
    b,ba,cnt=max_beta_over_n(N)
    print(f"N={N}: max beta over all triangle-free = {b}  (over {cnt} graphs)")
    # what's the conjectured cap? N=5n => n=N/5, cap=n^2. For N not mult of 5, cap = floor-type
    # general conjecture: beta <= floor(N/5)... actually beta<= (N/5)^2 only for N=5n.
    # Erdos #23 sharp value: max beta for triangle-free on N vtx. Known extremal = balanced C5 blowup
    print("  best graph adj:", ba[0])
