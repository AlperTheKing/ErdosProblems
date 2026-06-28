"""Hard refutation search for SAT-ZMU: find a CONFIG with a saturated vertex (T=N) ON a zero-mu cut edge.
Strategy: (1) identify census N=11 witnesses (graphs with BOTH a saturated vertex AND a zero-mu edge);
(2) blow them up (t=2,3) and perturb, re-scan for coincidence (sat vertex on a zero-mu edge);
(3) random triangle-free N=12..14 scan. Exact Fraction. Report first SAT-ZMU violation."""
import subprocess, itertools, random
from fractions import Fraction as F
from _h import dec, GENG, loads
from _zmu import mu_edges
from _superphi import blow

def scan(info):
    N=info['n']; T=info['T']
    O=[v for v in range(N) if T[v]>N]
    if not O: return None
    sat=set(v for v in range(N) if T[v]==N)
    if not sat: return ('no-sat',len(O))
    mu=mu_edges(info)
    zedges=[tuple(sorted(e)) for e,val in mu.items() if val==0]
    if not zedges: return ('no-zero-mu',len(sat))
    viol=[(u,v) for (u,v) in zedges if u in sat or v in sat]
    return ('both', sat, zedges, viol)

def witnesses_N11():
    outg=subprocess.run([GENG,"-tc","11"],capture_output=True,text=True).stdout.split()
    w=[]
    for g6 in outg:
        n,E=dec(g6); info=loads(n,E)
        if info is None: continue
        r=scan(info)
        if r and r[0]=='both':
            w.append((g6,r[1],r[2],r[3]))
    return w

if __name__=="__main__":
    print("=== SAT-ZMU hard refutation search ===")
    print("--- N=11 witnesses (sat vert + zero-mu edge coexist) ---")
    W=witnesses_N11()
    for (g6,sat,ze,viol) in W:
        print(f"  {g6}: saturated={sorted(sat)} zero-mu-edges={ze} SAT-ZMU-viol={viol}",flush=True)
    print(f"  [{len(W)} witnesses]")
    # blow up witnesses and perturb
    print("--- blow-ups of witnesses (t=2,3): does a sat vertex land on a zero-mu edge? ---")
    found=[]
    for (g6,_,_,_) in W:
        for t in (2,3):
            nn,EE=blow(g6,t)
            if nn>33: continue
            info=loads(nn,EE)
            if info is None: continue
            r=scan(info)
            if r and r[0]=='both' and r[3]:
                print(f"  *** VIOLATION {g6}[{t}] N={nn}: {r[3]}",flush=True); found.append((g6,t,r[3]))
            else:
                tag = r[0] if r else 'noO'
                print(f"  {g6}[{t}] N={nn}: {tag}"+("" if not (r and r[0]=='both') else f" sat={len(r[1])} zmu={len(r[2])} viol={len(r[3])}"),flush=True)
    # random triangle-free N=12..14
    print("--- random triangle-free N=12..14 scan ---")
    tot=0; viol=0
    for nn in (12,13,14):
        # sample via geng with -c and a count cap
        outg=subprocess.run([GENG,"-tcf",str(nn),"-d3","-D5"],capture_output=True,text=True).stdout.split()
        random.seed(nn); random.shuffle(outg); outg=outg[:1500]
        for g6 in outg:
            n,E=dec(g6); info=loads(n,E)
            if info is None: continue
            r=scan(info)
            tot+=1
            if r and r[0]=='both' and r[3]:
                print(f"  *** VIOLATION {g6} N={nn}: {r[3]}",flush=True); viol+=1; found.append((g6,1,r[3]))
        print(f"  N={nn}: scanned, running viol={viol}",flush=True)
    print(f"\nTOTAL SAT-ZMU violations found: {len(found)}")
    for f in found[:5]: print("   ",f)
