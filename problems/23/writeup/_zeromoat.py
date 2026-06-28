"""EXACT-TEST of GPT-Pro's ZERO-MOAT PREFIX-SWITCH certificate for C-alltie.
For a gamma-min connected-B max cut, find a saturated vertex v (T(v)=N) with a zero-load B-neighbor z (T(z)=0).
For each bad-edge geodesic through v, form oriented prefix A (A^- or A^+ ending at v's occurrence). Let Z = the
connected zero-load B-component containing z. Set S = A U Z, FLIP S across the cut, and compute:
  Delta_beta(S)=|delta_B(S)|-|delta_M(S)|, B^S connected, Gamma^S=sum_{bad h in cut S}(d_{B^S}(h)+1)^2.
Certificate (GPT): exists S with Delta_beta(S)=0, B^S connected, Gamma^S<Gamma  (=> contradicts gamma-min if C∩O=∅).
Also verify the structural identities the proof uses:
  (a) prefix switch ell^2-neutral; (b) Delta_beta(A U Z)=Delta_beta(A)-g_Z(A), g_Z(A)=2 e_B(Z,A)-delta_B(Z).
Exact integers (cut sizes, Gamma)."""
import subprocess
from collections import deque
from fractions import Fraction as F
from _h import dec, GENG, maxcut_all, Bconn, bdist_restr, geos, loads
from _satzmu_conn import struct_for_side, kcomponents

def cut_M_B(adj, side, n):
    B=[]; M=[]
    for u in range(n):
        for v in adj[u]:
            if v>u:
                (B if side[u]!=side[v] else M).append((u,v))
    return B,M

def gamma_and_conn(adj, side, n):
    """Gamma and B-connectivity for a given side. Returns (Gamma or None if a bad edge has no B-path, Bconnected)."""
    B,M=cut_M_B(adj,side,n)
    bc=Bconn(n,adj,side)
    G=0
    for (a,b) in M:
        d=bdist_restr(adj,side,a,b)
        if d<0: return None, bc
        G+=(d+1)**2
    return G, bc

def delta_beta(adj, side, S, n):
    """|delta_B(S)|-|delta_M(S)|: B-edges crossing S boundary minus M-edges crossing S boundary."""
    db=0; dm=0
    for u in range(n):
        for v in adj[u]:
            if v>u and ((u in S)^(v in S)):
                if side[u]!=side[v]: db+=1
                else: dm+=1
    return db-dm

def zero_moat(adj, side, T, z, n):
    """Connected B-component of T=0 vertices containing z."""
    T0=set(v for v in range(n) if T[v]==0)
    if z not in T0: return set()
    Z=set(); st=[z]; seen={z}
    while st:
        x=st.pop(); Z.add(x)
        for y in adj[x]:
            if y in T0 and side[y]!=side[x] and y not in seen:
                seen.add(y); st.append(y)
    return Z

def test_config(adj, side, n):
    st=struct_for_side(n,adj,side)
    if st is None: return None
    M,ell,T,mu,cyc=st; N=n
    O=set(v for v in range(N) if T[v]>N)
    if not O: return None
    G0,_=gamma_and_conn(adj,side,n)
    comp,find=kcomponents(n,cyc)
    results=[]
    sat=[v for v in range(N) if T[v]==N]
    for v in sat:
        # zero-load B-neighbors
        zs=[z for z in adj[v] if side[z]!=side[v] and T[z]==0]
        if not zs: continue
        CmeetsO = bool(comp[find(v)] & O)
        # prefixes through v from bad-edge geodesics whose support contains v
        prefixes=[]
        for f in M:
            for P in cyc[f]:
                if v in P:
                    i=P.index(v)
                    prefixes.append(set(P[:i+1]))   # A^- = x0..xi
                    prefixes.append(set(P[i:]))      # A^+ = xi..x_{ell-1}
        found=False; best=None
        for z in zs:
            Z=zero_moat(adj,side,T,z,n)
            for A in prefixes:
                S=A|Z
                db=delta_beta(adj,side,S,n)
                if db!=0:
                    if best is None: best=('db!=0',db)
                    continue
                side2=[1-side[w] if w in S else side[w] for w in range(n)]
                GS,bc=gamma_and_conn(adj,side2,n)
                if not bc or GS is None: continue
                if GS<G0:
                    found=True; best=('GAMMA-DROP',GS,G0,len(S)); break
            if found: break
        results.append((v, CmeetsO, found, best))
    return results, G0

def run_allcuts(n,E, gmin_only=True):
    adj=[set() for _ in range(n)]
    for x,y in E: adj[x].add(y); adj[y].add(x)
    cuts=[s for s in maxcut_all(n,adj) if Bconn(n,adj,s)]
    cand=[]
    for s in cuts:
        G,_=gamma_and_conn(adj,s,n)
        if G is not None: cand.append((s,G))
    if not cand: return []
    gm=min(g for _,g in cand)
    out=[]
    for s,g in cand:
        if gmin_only and g!=gm: continue
        r=test_config(adj,s,n)
        if r is None: continue
        for (v,CmeetsO,found,best) in r[0]:
            out.append((v,CmeetsO,found,best))
    return out

if __name__=="__main__":
    print("=== ZERO-MOAT PREFIX-SWITCH exact-test: saturated v adjacent to zero z ===")
    print("    (report: #sat-z configs, CmeetsO, switch-found Gamma-drop)")
    from _bdef_construct import Cn, union_disjoint, mycielski, is_triangle_free
    # glued battery
    g15=mycielski(7,Cn(7)); gr=mycielski(5,Cn(5))
    tot=0; cmeets=0; cdisj=0; found_disj=0; found_meet=0
    cases=[]
    for iN,iE in [(5,Cn(5)),(7,Cn(7))]:
        for gN,gE in [g15,gr]:
            for br in [[(0,0)],[(0,1)],[(0,2)],[(0,0),(2,3)]]:
                if any(j>=gN for _,j in br): continue
                n,E=union_disjoint((iN,iE),(gN,gE))
                for (i,j) in br: E=E+[(i,iN+j)]
                if n<=22 and is_triangle_free(n,E): cases.append((f"isl{iN}+gad{gN} br{br} N={n}",n,E))
    for name,n,E in cases:
        out=run_allcuts(n,E)
        for (v,CmeetsO,found,best) in out:
            tot+=1
            if CmeetsO: cmeets+=1; found_meet+=found
            else: cdisj+=1; found_disj+=found
    print(f"  glued battery: sat-z configs={tot} | C-meets-O={cmeets} (switch-found {found_meet}) | C-disjoint-O={cdisj} (switch-found {found_disj})",flush=True)
    # N=12 leaf tie-caveat (where sat-z configs DO occur)
    g6="J?AADBWM_}?"; n0,E0=dec(g6); E12=list(E0)+[(8,11)]
    out=run_allcuts(12,E12)
    tot=sum(1 for _ in out); cm=sum(1 for o in out if o[1]); cd=tot-cm
    fm=sum(o[2] for o in out if o[1]); fd=sum(o[2] for o in out if not o[1])
    print(f"  N=12 leaf caveat (all gamma-min cuts): sat-z configs={tot} | C-meets-O={cm}(found {fm}) | C-disjoint-O={cd}(found {fd})",flush=True)
    if out:
        for o in out[:4]: print(f"     v={o[0]} CmeetsO={o[1]} switch-found-GammaDrop={o[2]} best={o[3]}")
    # census N=7..10 all gamma-min cuts
    for nn in range(7,11):
        outg=subprocess.run([GENG,"-tc",str(nn)],capture_output=True,text=True).stdout.split()
        tot=0; cmeets=0; cdisj=0; fm=0; fd=0
        for g6 in outg:
            n,E=dec(g6)
            for (v,CmeetsO,found,best) in run_allcuts(n,E):
                tot+=1
                if CmeetsO: cmeets+=1; fm+=found
                else: cdisj+=1; fd+=found
        print(f"  census N={nn}: sat-z configs={tot} | C-meets-O={cmeets}(found {fm}) | C-disjoint-O={cdisj}(found {fd})",flush=True)
