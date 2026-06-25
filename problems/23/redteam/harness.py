import subprocess, random, itertools

EXE="./maxcut.exe"

def evalmany(graphs):
    lines=[str(len(graphs))]
    for N,edges in graphs:
        lines.append(f"{N} {len(edges)}")
        for u,v in edges: lines.append(f"{u} {v}")
    inp="\n".join(lines)+"\n"
    out=subprocess.run([EXE],input=inp,capture_output=True,text=True)
    res=[]
    for line in out.stdout.strip().split("\n"):
        b,e,mc,d,tf=line.split()
        res.append((int(b),int(e),int(mc),float(d),int(tf)))
    return res

def evalone(N,edges):
    return evalmany([(N,edges)])[0]

def density(N,e): return 2*e/(N*N)
def in_band(N,e):
    d=density(N,e); return 0.2486<d<0.3197

def c5_blowup_parts(sizes):
    offs=[0]
    for s in sizes: offs.append(offs[-1]+s)
    N=offs[5]; edges=[]
    for p in range(5):
        q=(p+1)%5
        for i in range(sizes[p]):
            for j in range(sizes[q]):
                edges.append((offs[p]+i, offs[q]+j))
    return N,edges
