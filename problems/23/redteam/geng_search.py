import subprocess, math
from harness import *
GENG="E:/Projects/ErdosProblems/tools/nauty2_8_9/geng.exe"

def parse_g6(line, n):
    # decode graph6
    line=line.strip()
    data=line
    # standard graph6 decode
    def decode(s):
        # first char(s) encode n
        idx=0
        n0=ord(s[0])-63
        bits=s[1:]
        # build bit string
        bitstr=[]
        for ch in bits:
            v=ord(ch)-63
            for k in range(5,-1,-1):
                bitstr.append((v>>k)&1)
        edges=[]
        pos=0
        for j in range(1,n0):
            for i in range(j):
                if pos<len(bitstr) and bitstr[pos]==1:
                    edges.append((i,j))
                pos+=1
        return n0,edges
    return decode(data)

def beta_base(N,edges):
    return evalone(N,edges)[0]

best={}
for h in [6,7,8,9,10]:
    lo=math.ceil(0.2486*h*h/2); hi=math.floor(0.3197*h*h/2)
    bestrec=None
    for e in range(lo,hi+1):
        # enumerate triangle-free graphs with h vertices, e edges
        out=subprocess.run([GENG,"-tc",str(h),f"{e}:{e}"],capture_output=True,text=True)
        lines=[l for l in out.stdout.strip().split("\n") if l]
        # batch evaluate
        graphs=[]
        decoded=[]
        for ln in lines:
            n0,eds=parse_g6(ln,h)
            decoded.append((n0,eds))
            graphs.append((n0,eds))
        if not graphs: continue
        res=evalmany(graphs)
        for (n0,eds),(b,ee,mc,d,tf) in zip(decoded,res):
            score=25.0*b/(h*h)  # ratio after blow-up
            if bestrec is None or b>bestrec[0] or (b==bestrec[0] and score>bestrec[3]):
                if tf:
                    bestrec=(b,e,d,score,eds)
    if bestrec:
        b,e,d,score,eds=bestrec
        best[h]=bestrec
        print(f"h={h}: best beta={b} e={e} dens={d:.4f} blowup-ratio={score:.3f} (N^2/25 target)")
        print(f"   edges={eds}")
