import sys, subprocess, networkx as nx
from referee_factored import is_triangle_free, all_max_cuts, analyze

GENG = r"E:\Projects\ErdosProblems\tools\nauty2_8_9\geng.exe"

def parse_g6(line):
    return nx.from_graph6_bytes(line.strip().encode())

def run(Nmin, Nmax):
    worst_LS = 0.0   # max ratio LS/N^2 over all instances
    worst_G  = 0.0   # max ratio Gamma/N^2
    n_LS_viol = 0
    n_G_viol  = 0
    worst_inst = None
    total = 0
    # also track: among instances where ells are NOT all equal, is L*S strictly > Gamma? (claim)
    LSeqG_when_unequal = 0
    unequal_count = 0
    # track separation between LS and N^2 at non-extremal: smallest slack N^2-LS that is >0
    for N in range(Nmin, Nmax+1):
        # -t : triangle-free, -c : connected
        p = subprocess.run([GENG, "-tc", str(N)], capture_output=True)
        lines = p.stdout.split(b"\n")
        for ln in lines:
            if not ln.strip(): continue
            G = nx.from_graph6_bytes(ln.strip())
            G = nx.convert_node_labels_to_integers(G)
            best, cuts, nodes = all_max_cuts(G)
            for X in cuts:
                r = analyze(G, X)
                if r is None: continue
                total += 1
                rLS = r['LS']/r['N2']
                rG  = r['Gamma']/r['N2']
                if rLS > worst_LS:
                    worst_LS = rLS; worst_inst = (N, ln.strip().decode(), sorted(r['ells']), r['L'], r['S'], r['LS'], r['N2'])
                worst_G = max(worst_G, rG)
                if r['LS'] > r['N2']: n_LS_viol += 1
                if r['Gamma'] > r['N2']: n_G_viol += 1
                # claim: L*S > Gamma whenever ells unequal
                if len(set(r['ells'])) > 1:
                    unequal_count += 1
                    if r['LS'] == r['Gamma']:
                        LSeqG_when_unequal += 1
        print(f"  N={N} done; cumulative instances(cut,connB,M>0)={total} "
              f"maxLS/N^2={worst_LS:.4f} maxGamma/N^2={worst_G:.4f} "
              f"LSviol={n_LS_viol} Gviol={n_G_viol}", flush=True)
    print()
    print(f"TOTAL instances {total}")
    print(f"max L*S/N^2  = {worst_LS:.6f}  (violations: {n_LS_viol})")
    print(f"max Gamma/N^2 = {worst_G:.6f}  (violations: {n_G_viol})")
    print(f"worst L*S instance: {worst_inst}")
    print(f"unequal-ell instances: {unequal_count}; of those L*S==Gamma: {LSeqG_when_unequal}")

if __name__ == "__main__":
    a = int(sys.argv[1]) if len(sys.argv)>1 else 5
    b = int(sys.argv[2]) if len(sys.argv)>2 else 9
    run(a,b)
