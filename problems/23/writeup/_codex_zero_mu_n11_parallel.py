import multiprocessing as mp
import subprocess
from fractions import Fraction as F

from _h import dec, GENG, loads
from _edgeload import edge_loads


def check_g6(g6):
    n, E = dec(g6)
    info = loads(n, E)
    if info is None or not any(t > n for t in info["T"]):
        return (0, 0, 0, 0, None)
    mu, _ = edge_loads(info)
    zero = both_load = sat_endpoint = both_pos_under = 0
    ex = None
    for e in info["Bset"]:
        if mu.get(e, F(0)) != 0:
            continue
        a, b = e
        Ta, Tb = info["T"][a], info["T"][b]
        zero += 1
        fail = None
        if Ta > 0 and Tb > 0:
            both_load += 1
            fail = "both_load"
        if Ta == n or Tb == n:
            sat_endpoint += 1
            fail = fail or "sat_endpoint"
        if 0 < Ta <= n and 0 < Tb <= n:
            both_pos_under += 1
            fail = fail or "both_pos_under"
        if fail and ex is None:
            ex = (fail, g6, e, str(Ta), str(Tb), [str(x) for x in info["T"]])
    return (zero, both_load, sat_endpoint, both_pos_under, ex)


if __name__ == "__main__":
    graphs = subprocess.run([GENG, "-tc", "11"], capture_output=True, text=True).stdout.split()
    totals = [0, 0, 0, 0]
    first = None
    with mp.Pool(processes=60) as pool:
        for i, res in enumerate(pool.imap_unordered(check_g6, graphs, chunksize=32), 1):
            for j in range(4):
                totals[j] += res[j]
            if res[4] is not None and first is None:
                first = res[4]
            if i % 5000 == 0:
                print("done", i, "totals", totals, "first", first, flush=True)
    print("FINAL graphs", len(graphs), "totals", totals, "first", first, flush=True)
