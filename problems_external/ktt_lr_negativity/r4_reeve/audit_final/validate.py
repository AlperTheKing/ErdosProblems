"""Mandated validation gate: my constructor vs engines A and B on many triples."""
import random, subprocess, os, sys
from hive import lattice_points, _partial

ENG_DIR = "E:/Projects/ErdosProblems/problems_external/ktt_lr_negativity/engine"
ENG_A = os.path.join(ENG_DIR, "lr_hive.exe")
ENG_B = os.path.join(ENG_DIR, "engineB_lrrule.py")

random.seed(20260722)

def rand_part(maxlen, maxpart):
    L = random.randint(1, maxlen)
    parts = sorted([random.randint(0, maxpart) for _ in range(L)], reverse=True)
    while parts and parts[-1]==0: parts.pop()
    return parts or [1]

def make_nu(lam, mu):
    s = [ (lam[k] if k<len(lam) else 0)+(mu[k] if k<len(mu) else 0) for k in range(4)]
    # random box moves down keeping partition & length<=4
    for _ in range(random.randint(0,6)):
        k = random.randint(0,2)
        if s[k] > s[k+1] and s[k] > 0:
            s[k]-=1; s[k+1]+=1
        # re-sort to keep weakly decreasing
        s = sorted(s, reverse=True)
    while s and s[-1]==0: s.pop()
    return s or [1]

def part_str(p):
    return ",".join(str(x) for x in p)

def main():
    N = int(sys.argv[1]) if len(sys.argv)>1 else 700
    maxpart = int(sys.argv[2]) if len(sys.argv)>2 else 5
    triples=[]
    for _ in range(N):
        lam=rand_part(4,maxpart); mu=rand_part(4,maxpart)
        nu=make_nu(lam,mu)
        if _partial(nu,4)!=_partial(lam,4)+_partial(mu,4):
            continue
        triples.append((lam,mu,nu))
    # engine batch files
    bf = "batch.txt"
    with open(bf,"w") as f:
        for lam,mu,nu in triples:
            f.write(f"{part_str(lam)};{part_str(mu)};{part_str(nu)};1000000\n")
    outA = subprocess.run([ENG_A,"--batch",bf],capture_output=True,text=True).stdout.split()
    outB = subprocess.run([sys.executable,ENG_B,"--batch",bf],capture_output=True,text=True).stdout.split()
    assert len(outA)==len(triples), (len(outA),len(triples))
    assert len(outB)==len(triples), (len(outB),len(triples))
    mism=0; nonzero=0
    for (lam,mu,nu),a,b in zip(triples,outA,outB):
        mine = lattice_points(lam,mu,nu)
        if str(mine)!=a or str(mine)!=b:
            mism+=1
            print("MISMATCH",lam,mu,nu,"mine",mine,"A",a,"B",b)
        if mine>0: nonzero+=1
    print(f"triples={len(triples)} nonzero={nonzero} mismatches={mism}")

if __name__=="__main__":
    main()
