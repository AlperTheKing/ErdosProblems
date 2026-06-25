import subprocess, math
from harness import *
GENG="E:/Projects/ErdosProblems/tools/nauty2_8_9/geng.exe"
def parse_g6(line,h):
    s=line.strip()
    n0=ord(s[0])-63; bits=s[1:]; bitstr=[]
    for ch in bits:
        v=ord(ch)-63
        for k in range(5,-1,-1): bitstr.append((v>>k)&1)
    edges=[]; pos=0
    for j in range(1,n0):
        for i in range(j):
            if pos<len(bitstr) and bitstr[pos]==1: edges.append((i,j))
            pos+=1
    return n0,edges
for h in [11,12]:
    lo=math.ceil(0.2486*h*h/2); hi=math.floor(0.3197*h*h/2)
    bestrec=None
    for e in range(lo,hi+1):
        out=subprocess.run([GENG,"-tc",str(h),f"{e}:{e}"],capture_output=True,text=True)
        lines=[l for l in out.stdout.strip().split("\n") if l]
        if not lines: continue
        # batch in chunks of 4000
        for k in range(0,len(lines),4000):
            chunk=lines[k:k+4000]
            decoded=[parse_g6(l,h) for l in chunk]
            res=evalmany(decoded)
            for (n0,eds),(b,ee,mc,d,tf) in zip(decoded,res):
                if tf and (bestrec is None or b>bestrec[0]):
                    bestrec=(b,e,d,25.0*b/(h*h),eds)
    if bestrec:
        b,e,d,score,eds=bestrec
        print(f"h={h}: best beta={b} e={e} dens={d:.4f} blowup-ratio={score:.3f}")
        print(f"   edges={eds}")
