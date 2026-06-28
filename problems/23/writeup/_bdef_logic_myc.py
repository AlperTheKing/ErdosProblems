"""Logic audit on the larger iterated Mycielskians (N=31, N=47) using loads_onecut (representative
max cut). Verifies junctions J1/J2/J3 there too. These are the finite-depth-proof-breaking family."""
from _bdef_logic import analyze, report, mycielski
from _bdef_stress2 import loads_onecut

if __name__ == "__main__":
    print("=== iterated Mycielskian logic audit (loads_onecut representative max cut) ===")
    C5 = (5, [(i, (i + 1) % 5) for i in range(5)])
    C7 = (7, [(i, (i + 1) % 7) for i in range(7)])
    n1, E1 = mycielski(*C5)        # Grotzsch 11
    n2, E2 = mycielski(n1, E1)     # 23
    n3, E3 = mycielski(n2, E2)     # 47
    m1, F1 = mycielski(*C7)        # 15
    m2, F2 = mycielski(m1, F1)     # 31
    m3, F3 = mycielski(m2, F2)     # 63 (skip, too big for bb maxcut)
    fam = [("Myc(Grotzsch) N=23", (n2, E2)),
           ("Myc^3(C5) N=47", (n3, E3)),
           ("Myc(Myc(C7)) N=31", (m2, F2))]
    for nm, (nn, EE) in fam:
        info = loads_onecut(nn, EE)
        if info is None:
            print(f"  {nm}: loads_onecut=None")
            continue
        report(analyze(info, nm), deep=True)
