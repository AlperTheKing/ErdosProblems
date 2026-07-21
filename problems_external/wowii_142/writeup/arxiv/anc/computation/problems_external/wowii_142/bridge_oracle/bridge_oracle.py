#!/usr/bin/env python3
"""WOWII 142 bridge oracle: exact falsifier tests for candidate bridges.

Bridges tested (t = largestInducedTreeSize, g = girth>0, f = eccSet(periphery),
D = diameter; all slacks recorded as integers in THIRDS: slack3 = 3*slack):

  R1 (geodesic-base): (2/3)g + f <= D + 1 + max_P M_P(P), max over diametral
     geodesics P.  M_P(P) = max |F| over induced forests F in G - V(P) whose
     every component sends exactly one edge (counted with multiplicity) into P.
     Consumer = Lemma M-P (rigorous), so R1 true => C142 hard branch closes.
  R2 (cycle-base): f <= g/3 - 1 + max_K M(K), max over shortest cycles K.
     M(K) as in wowii_144/wave2/lemma_e_tests.M_of_cycle (exists z in K, each
     forest component sends exactly one edge into K - {z}).
  R3 (structure map): the set  2g + 3f > 3(D+1)  where T1 (t >= D+1) alone
     fails; girth histogram, excess distribution, R1/R2 slacks restricted.
  R4: (2/3)g + f <= max(D + ceil(g/2) - 1, g - 1 + max_K M(K)).

Exactness policy:
  * M values computed by EXACT enumeration per connected component of
    G - V(P) / G - V(K) (components are non-adjacent, so the optimum is
    additive across components; validated against brute enumeration).
  * Components larger than COMP_CAP fall back to a greedy LOWER bound and the
    graph is flagged capped; likewise geodesic/cycle enumeration caps.
    A capped value can only UNDER-report max M, i.e. under-report slack, so
    capped negative slacks are 'suspect', not violations, and are re-verified
    with raised caps where feasible.
  * Diametral geodesics: exact via shortest-path DAG for n <= EXACT_N (>= the
    required n <= 11); capped at GEOD_CAP_LARGE sets for larger n.
  * All arithmetic integer (thirds).  No floats anywhere.

Output: bridge_oracle_results.json, equality_slacks.json (this directory).
"""

from __future__ import annotations

import hashlib
import json
import random
import sys
import time
from collections import Counter
from multiprocessing import Pool
from pathlib import Path

import networkx as nx

ROOT = Path(__file__).resolve().parent               # .../wowii_142/bridge_oracle
W142 = ROOT.parent
PE = W142.parent
W141 = PE / "wowii_141" / "oracle"
W144O = PE / "wowii_144" / "oracle"
W144W2 = PE / "wowii_144" / "wave2"
for p in (W141, W144O, W144W2):
    sys.path.insert(0, str(p))

from invariants import (  # noqa: E402
    all_pairs_dist,
    ecc_set,
    eccentricities,
    edges_in_mask,
    girth,
    graph_connected,
    nx_to_bitadj,
)
from sweep_families import build_family_graphs, random_graphs  # noqa: E402
from bridge_tests import adversarial_graphs, shortest_cycles  # noqa: E402
from route_b_tests import (  # noqa: E402
    chorded_cycle,
    cycle_random_legs,
    cycle_random_trees,
    forced_girth_random,
    gen_theta,
    trap_family,
)
from lemma_e_tests import M_of_cycle, components_of_mask  # noqa: E402

SEED = 20260718
COMP_CAP = 17          # exact per-component enumeration up to 2^17 subsets
COMP_CAP_RECHECK = 22  # raised cap for the suspect re-verification pass
EXACT_N = 14           # geodesic sets enumerated exactly for n <= EXACT_N
GEOD_CAP_SMALL = 20000  # cannot be hit for n <= 14 (< 2^14 vertex sets)
GEOD_CAP_LARGE = 500
CYC_CAP = 250
MAX_VIOL = 50
OUT = ROOT / "bridge_oracle_results.json"
OUT_EQ = ROOT / "equality_slacks.json"
EQ_JSON = W142 / "oracle" / "equality_cases.json"


def bits_list(mask: int) -> list[int]:
    out = []
    while mask:
        b = mask & -mask
        mask ^= b
        out.append(b.bit_length() - 1)
    return out


# --------------------------------------------------------------- geodesics

def diametral_geodesic_sets(n, adj, dist, D, cap):
    """All vertex sets of geodesics between diametral pairs (shortest-path DAG
    DFS).  Geodesics are induced paths, so vertex set <-> path.  Returns
    (set_of_masks, capped)."""
    sets: set[int] = set()
    for u in range(n):
        du = dist[u]
        for v in range(u + 1, n):
            if du[v] != D:
                continue
            dv = dist[v]
            stack = [(u, 1 << u)]
            while stack:
                x, mask = stack.pop()
                if x == v:
                    sets.add(mask)
                    if len(sets) >= cap:
                        return sets, True
                    continue
                nb = adj[x]
                dx = du[x]
                while nb:
                    b = nb & -nb
                    nb ^= b
                    y = b.bit_length() - 1
                    if du[y] == dx + 1 and dv[y] == D - dx - 1:
                        stack.append((y, mask | b))
    return sets, False


# --------------------------------------------------------------- M machinery

def greedy_one_edge(adj, comp_mask, target_mask):
    """Greedy LOWER bound: grow a single induced tree from a seed with exactly
    one edge into target; additions have 0 target-edges and 1 neighbor in S."""
    best = 0
    for seed in bits_list(comp_mask):
        if (adj[seed] & target_mask).bit_count() != 1:
            continue
        smask = 1 << seed
        grew = True
        while grew:
            grew = False
            rem = comp_mask & ~smask
            while rem:
                b = rem & -rem
                rem ^= b
                w = b.bit_length() - 1
                if (adj[w] & target_mask) == 0 and (adj[w] & smask).bit_count() == 1:
                    smask |= b
                    grew = True
        c = smask.bit_count()
        if c > best:
            best = c
    return best


def exact_best_vec(adj, comp_mask, base_mask, zbits, floor):
    """For one connected component `comp_mask` of G - V(base), for each zb in
    zbits (0 = nothing removed): max |F|, F subset of comp inducing a forest
    whose every component has exactly one edge into base_mask minus zb
    (edge count with multiplicity).  Subsets of size <= floor are skipped
    (only sound when the caller ensures they cannot matter)."""
    nz = len(zbits)
    best = [0] * nz
    verts = bits_list(comp_mask)
    k = len(verts)
    vbits = [1 << v for v in verts]
    for sub in range(1, 1 << k):
        sz = sub.bit_count()
        thr = min(best)
        if floor is not None and floor > thr:
            thr = floor
        if sz <= thr:
            continue
        mask = 0
        t = sub
        while t:
            b = t & -t
            t ^= b
            mask |= vbits[b.bit_length() - 1]
        # cheap forest reject: a forest on sz vertices has <= sz - 1 edges
        ne = edges_in_mask(adj, mask)
        if ne > sz - 1:
            continue
        comps = components_of_mask(adj, mask)
        if ne != sz - len(comps):
            continue
        pertot = []
        for cm in comps:
            tot = 0
            zc = [0] * nz
            cc = cm
            while cc:
                b = cc & -cc
                cc ^= b
                a = adj[b.bit_length() - 1] & base_mask
                if a:
                    tot += a.bit_count()
                    for i in range(nz):
                        if a & zbits[i]:
                            zc[i] += 1
            pertot.append((tot, zc))
        for i in range(nz):
            if best[i] >= sz:
                continue
            ok = True
            for tot, zc in pertot:
                if tot - zc[i] != 1:
                    ok = False
                    break
            if ok:
                best[i] = sz
    return best


def M_collection_max(n, adj, entries, comp_cap):
    """entries: list of (forbidden_mask, base_mask, zbits).  Returns
    (max over entries of max_z sum over components, capped).

    Per entry, components of G - forbidden are non-adjacent, so for fixed z
    the optimum is the SUM of per-component optima.  Pruning: in the largest
    component we skip subsets of size <= best_global - max_z(sum others):
    such subsets cannot push any z's total above the running global max, so
    the returned MAX is exact (individual entry values may be pruned)."""
    full = (1 << n) - 1
    best_global = 0          # empty forest is always admissible
    capped = False
    for forbidden, base_mask, zbits in entries:
        outside = full & ~forbidden
        if outside == 0:
            continue
        comps = components_of_mask(adj, outside)
        comps.sort(key=lambda m: m.bit_count())
        nz = len(zbits)
        sums = [0] * nz
        for ci, cm in enumerate(comps):
            csz = cm.bit_count()
            last = ci == len(comps) - 1
            if csz > comp_cap:
                capped = True
                vals = [greedy_one_edge(adj, cm, base_mask & ~zb) for zb in zbits]
            else:
                floor = (best_global - max(sums)) if last else None
                vals = exact_best_vec(adj, cm, base_mask, zbits, floor)
            sums = [s + v for s, v in zip(sums, vals)]
        cand = max(sums)
        if cand > best_global:
            best_global = cand
    return best_global, capped


def M_P_brute(n, adj, pmask):
    """Brute-force M_P over ALL subsets of V - V(P) (validation only)."""
    best = 0
    outside = bits_list(((1 << n) - 1) & ~pmask)
    no = len(outside)
    for sub in range(1, 1 << no):
        sz = sub.bit_count()
        if sz <= best:
            continue
        mask = 0
        t = sub
        while t:
            b = t & -t
            t ^= b
            mask |= 1 << outside[b.bit_length() - 1]
        ne = edges_in_mask(adj, mask)
        comps = components_of_mask(adj, mask)
        if ne != sz - len(comps):
            continue
        ok = True
        for cm in comps:
            tot = 0
            cc = cm
            while cc:
                b = cc & -cc
                cc ^= b
                tot += (adj[b.bit_length() - 1] & pmask).bit_count()
            if tot != 1:
                ok = False
                break
        if ok:
            best = sz
    return best


# --------------------------------------------------------------- evaluation

def eval_one(task, comp_cap=COMP_CAP, geod_cap_large=GEOD_CAP_LARGE,
             cyc_cap=CYC_CAP):
    name, g6s = task
    try:
        G = nx.from_graph6_bytes(g6s.encode("ascii"))
        n, adj = nx_to_bitadj(G)
        rec = {"name": name, "g6": g6s, "n": n}
        if n < 2 or not graph_connected(n, adj):
            rec["skip"] = "disconnected"
            return rec
        g = girth(n, adj)
        if g == 0:
            rec["skip"] = "acyclic"
            return rec
        dist = all_pairs_dist(n, adj)
        ecc = eccentricities(n, dist)
        D = max(ecc)
        periph = 0
        for v in range(n):
            if ecc[v] == D:
                periph |= 1 << v
        f = ecc_set(n, dist, periph)
        rec.update(girth=g, D=D, f=f)

        # ---- R1
        cap = GEOD_CAP_SMALL if n <= EXACT_N else geod_cap_large
        gsets, gcapped = diametral_geodesic_sets(n, adj, dist, D, cap)
        entries = [(pm, pm, (0,)) for pm in sorted(gsets)]
        maxMP, mp_capped = M_collection_max(n, adj, entries, comp_cap)
        r1_capped = gcapped or mp_capped
        # NOTE on gcapped: max_P is a max, a capped enumeration under-reports
        # it, so slack is a lower bound -> negative slack only 'suspect'.
        r1_slack3 = 3 * (D + 1 + maxMP) - 2 * g - 3 * f
        rec["R1"] = {"slack3": r1_slack3, "capped": r1_capped, "maxMP": maxMP,
                     "n_geod": len(gsets), "geod_capped": gcapped}

        # ---- R2 (and the M(K) arm of R4)
        Ks = shortest_cycles(G, g)
        cyc_capped = False
        if len(Ks) > cyc_cap:
            Ks = Ks[:cyc_cap]
            cyc_capped = True
        entries = []
        for K in Ks:
            kv = sorted(K)
            km = 0
            for v in kv:
                km |= 1 << v
            entries.append((km, km, [1 << v for v in kv]))
        maxMK, mk_capped = M_collection_max(n, adj, entries, comp_cap)
        r2_capped = cyc_capped or mk_capped
        r2_slack3 = (g - 3 + 3 * maxMK) - 3 * f
        rec["R2"] = {"slack3": r2_slack3, "capped": r2_capped, "maxMK": maxMK,
                     "n_cycles": len(Ks), "cyc_capped": cyc_capped}

        # ---- R4
        arm1_slack3 = 3 * (D + (g + 1) // 2 - 1) - 2 * g - 3 * f
        arm2_slack3 = 3 * (g - 1 + maxMK) - 2 * g - 3 * f
        r4_slack3 = max(arm1_slack3, arm2_slack3)
        r4_capped = r2_capped and arm1_slack3 < 0
        rec["R4"] = {"slack3": r4_slack3, "capped": r4_capped}

        # ---- R3 membership: T1 alone (t >= D+1) fails iff excess3 > 0
        rec["excess3"] = 2 * g + 3 * f - 3 * (D + 1)
        return rec
    except Exception as exc:  # keep the pool alive; report
        return {"name": name, "g6": g6s, "skip": f"error: {exc!r}"}


def eval_one_pool(task):
    return eval_one(task)


# --------------------------------------------------------------- validation

def run_validation(tasks):
    """Cross-check the decomposed M computation against brute enumeration on
    small graphs (n <= 10): per-geodesic M_P vs M_P_brute, per-cycle M(K) vs
    lemma_e_tests.M_of_cycle, and collection-max vs max-of-brutes."""
    checked_p = checked_k = graphs = 0
    for name, g6s in tasks:
        if checked_p >= 800 and checked_k >= 800:
            break
        G = nx.from_graph6_bytes(g6s.encode("ascii"))
        n, adj = nx_to_bitadj(G)
        if n < 2 or n > 10 or not graph_connected(n, adj):
            continue
        g = girth(n, adj)
        if g == 0:
            continue
        graphs += 1
        dist = all_pairs_dist(n, adj)
        D = max(max(r) for r in dist)
        gsets, capped = diametral_geodesic_sets(n, adj, dist, D, 10 ** 6)
        assert not capped
        brute_p = {}
        for pm in gsets:
            v1 = M_collection_max(n, adj, [(pm, pm, (0,))], 99)[0]
            v2 = M_P_brute(n, adj, pm)
            assert v1 == v2, ("M_P mismatch", name, g6s, pm, v1, v2)
            brute_p[pm] = v2
            checked_p += 1
        if gsets:
            vall = M_collection_max(
                n, adj, [(pm, pm, (0,)) for pm in sorted(gsets)], 99)[0]
            assert vall == max(brute_p.values()), ("maxP mismatch", name, g6s)
        brute_k = []
        entries = []
        for K in shortest_cycles(G, g):
            kv = sorted(K)
            km = 0
            for v in kv:
                km |= 1 << v
            zb = [1 << v for v in kv]
            v1 = M_collection_max(n, adj, [(km, km, zb)], 99)[0]
            v2 = M_of_cycle(n, adj, kv)
            assert v1 == v2, ("M_K mismatch", name, g6s, kv, v1, v2)
            brute_k.append(v2)
            entries.append((km, km, zb))
            checked_k += 1
        if entries:
            vall = M_collection_max(n, adj, entries, 99)[0]
            assert vall == max(brute_k), ("maxK mismatch", name, g6s)
    return graphs, checked_p, checked_k


# --------------------------------------------------------------- corpora

def bipartite_corpus(rng: random.Random):
    out = []
    for k in range(3, 8):
        G = nx.complete_bipartite_graph(k, k)
        G.remove_edges_from((i, k + i) for i in range(k))
        out.append((f"crown({k})", G))
    for a in range(2, 5):
        for b in range(a, 7):
            out.append((f"Kbip({a},{b})", nx.complete_bipartite_graph(a, b)))
    for a in range(2, 5):
        for b in range(a, 8):
            if a * b <= 28:
                out.append((f"grid({a}x{b})", nx.grid_2d_graph(a, b)))
    for i in range(700):
        a = rng.randrange(3, 9)
        b = rng.randrange(3, 9)
        p = (0.25, 0.35, 0.5, 0.7)[i % 4]
        G = nx.bipartite.random_graph(a, b, p, seed=rng.randrange(2 ** 31))
        if G.number_of_nodes() >= 2 and nx.is_connected(G):
            out.append((f"bipRand(a={a},b={b},p={p},i={i})", G))
    for i in range(250):
        m = rng.randrange(4, 11)
        G = nx.cycle_graph(2 * m)
        for _ in range(rng.randrange(1, 4)):
            u = rng.randrange(2 * m)
            off = rng.randrange(3, 2 * m - 2)
            if off % 2 == 1:
                G.add_edge(u, (u + off) % (2 * m))
        out.append((f"evenChord(m={m},i={i})", G))
    for i in range(150):
        nn = rng.randrange(5, 10)
        G = nx.gnp_random_graph(nn, 0.45, seed=rng.randrange(2 ** 31))
        if not nx.is_connected(G) or G.number_of_edges() < nn:
            continue
        H = nx.Graph()
        for j, (u, v) in enumerate(G.edges()):
            H.add_edge(u, f"s{j}")
            H.add_edge(f"s{j}", v)
        out.append((f"subdiv(n={nn},i={i})", H))
    return out


def build_corpus():
    rng = random.Random(SEED)
    corpora: list[tuple[str, nx.Graph]] = []
    for graph in nx.graph_atlas_g():
        if graph.number_of_nodes() >= 2 and nx.is_connected(graph):
            corpora.append(("atlas", graph))
    corpora += build_family_graphs()
    corpora += random_graphs(random.Random(SEED))
    corpora += adversarial_graphs()
    corpora += trap_family()
    for _ in range(1500):
        corpora.append(cycle_random_legs(rng))
    for _ in range(1000):
        corpora.append(cycle_random_trees(rng))
    for _ in range(800):
        corpora.append(chorded_cycle(rng))
    for _ in range(600):
        corpora.append(gen_theta(rng))
    got = tries = 0
    while got < 800 and tries < 15000:
        tries += 1
        r = forced_girth_random(rng, gmin=5)
        if r is not None:
            corpora.append(r)
            got += 1
    got = tries = 0
    while got < 300 and tries < 8000:
        tries += 1
        r = forced_girth_random(rng, gmin=4)
        if r is not None:
            corpora.append(r)
            got += 1
    corpora += bipartite_corpus(rng)

    tasks, seen = [], set()
    for name, G in corpora:
        if G is None or G.number_of_nodes() < 2:
            continue
        if not nx.is_connected(G):
            continue
        Gi = nx.convert_node_labels_to_integers(G, ordering="default")
        g6s = nx.to_graph6_bytes(Gi, header=False).decode("ascii").strip()
        if g6s in seen:
            continue
        seen.add(g6s)
        tasks.append((name, g6s))
    return tasks


# --------------------------------------------------------------- aggregation

def new_sec():
    return {"count": 0, "capped_count": 0, "viol": [], "suspect": [],
            "min_slack3": None, "min_wit": None,
            "min_slack3_uncapped": None, "min_wit_uncapped": None,
            "hist": Counter(), "tight": []}


def witness(rec):
    return (f"{rec['name']} [{rec['g6']}] n={rec['n']} g={rec['girth']} "
            f"D={rec['D']} f={rec['f']}")


def add_to_sec(sec, rec, key):
    d = rec[key]
    sl = d["slack3"]
    sec["count"] += 1
    sec["hist"][sl] += 1
    if d["capped"]:
        sec["capped_count"] += 1
    if sec["min_slack3"] is None or sl < sec["min_slack3"]:
        sec["min_slack3"] = sl
        sec["min_wit"] = witness(rec)
    if not d["capped"]:
        if (sec["min_slack3_uncapped"] is None
                or sl < sec["min_slack3_uncapped"]):
            sec["min_slack3_uncapped"] = sl
            sec["min_wit_uncapped"] = witness(rec)
    if sl < 0:
        tgt = sec["suspect"] if d["capped"] else sec["viol"]
        if len(tgt) < MAX_VIOL:
            entry = {"family": rec["name"], "graph6": rec["g6"],
                     "n": rec["n"], "girth": rec["girth"], "D": rec["D"],
                     "f": rec["f"], "slack3": sl}
            entry.update({k: v for k, v in d.items() if k != "slack3"})
            tgt.append(entry)
    elif sl == 0 and len(sec["tight"]) < 30:
        sec["tight"].append(witness(rec))


def main():
    t0 = time.time()
    print("building corpus ...", flush=True)
    tasks = build_corpus()
    print(f"corpus: {len(tasks)} distinct connected graphs", flush=True)

    print("validation pass (decomposed M vs brute) ...", flush=True)
    vg, vp, vk = run_validation(tasks)
    print(f"validation OK: {vg} graphs, {vp} geodesic M_P checks, "
          f"{vk} cycle M(K) checks, 0 mismatches", flush=True)

    secs = {k: new_sec() for k in ("R1", "R2", "R4")}
    r3 = {"members": 0, "girth_hist": Counter(), "excess3_hist": Counter(),
          "examples": [], "R1_min_slack3": None, "R1_viol": 0,
          "R2_min_slack3": None, "R2_viol": 0, "R1_wit": None, "R2_wit": None}
    skipped = Counter()
    records_for_recheck = []
    done = 0

    with Pool(8) as pool:
        for rec in pool.imap_unordered(eval_one_pool, tasks, chunksize=16):
            done += 1
            if done % 1000 == 0:
                print(f"  {done}/{len(tasks)} graphs "
                      f"({time.time() - t0:.0f}s)", flush=True)
            if "skip" in rec:
                skipped[rec["skip"].split(":")[0]] += 1
                if rec["skip"].startswith("error"):
                    print("  WORKER ERROR:", rec, flush=True)
                continue
            for key in ("R1", "R2", "R4"):
                add_to_sec(secs[key], rec, key)
                if rec[key]["slack3"] < 0 and rec[key]["capped"]:
                    records_for_recheck.append(rec)
            if rec["excess3"] > 0:
                r3["members"] += 1
                r3["girth_hist"][rec["girth"]] += 1
                r3["excess3_hist"][rec["excess3"]] += 1
                if len(r3["examples"]) < 40:
                    r3["examples"].append(witness(rec)
                                          + f" excess3={rec['excess3']}")
                for key in ("R1", "R2"):
                    sl = rec[key]["slack3"]
                    mk = f"{key}_min_slack3"
                    if r3[mk] is None or sl < r3[mk]:
                        r3[mk] = sl
                        r3[f"{key}_wit"] = witness(rec)
                    if sl < 0 and not rec[key]["capped"]:
                        r3[f"{key}_viol"] += 1

    print(f"main pass done in {time.time() - t0:.0f}s; "
          f"skipped: {dict(skipped)}", flush=True)

    # ---- suspect re-verification with raised caps (exact where feasible)
    rechecked = []
    seen_rc = set()
    for rec in records_for_recheck:
        if rec["g6"] in seen_rc:
            continue
        seen_rc.add(rec["g6"])
        rec2 = eval_one((rec["name"], rec["g6"]), comp_cap=COMP_CAP_RECHECK,
                        geod_cap_large=4000, cyc_cap=2000)
        rechecked.append(rec2)
        print("  recheck:", rec2, flush=True)

    # ---- equality-case tightness (113 graphs; any adopted bridge must be
    #      nonnegative there and its tight structure is diagnostic)
    eq_raw = json.loads(EQ_JSON.read_text())["equality_cases"]
    eq_out = {"count": 0, "per_bridge": {}}
    eq_secs = {k: {"min_slack3": None, "hist": Counter(), "neg": []}
               for k in ("R1", "R2", "R4")}
    for case in eq_raw:
        rec = eval_one((f"eq[{case['first_seen_as']}]", case["g6"]))
        if "skip" in rec:
            continue
        eq_out["count"] += 1
        for key in ("R1", "R2", "R4"):
            sl = rec[key]["slack3"]
            s = eq_secs[key]
            s["hist"][sl] += 1
            if s["min_slack3"] is None or sl < s["min_slack3"]:
                s["min_slack3"] = sl
            if sl < 0:
                s["neg"].append({"graph6": rec["g6"], "slack3": sl,
                                 "capped": rec[key]["capped"]})
    for key, s in eq_secs.items():
        eq_out["per_bridge"][key] = {
            "min_slack3": s["min_slack3"],
            "hist": {str(a): b for a, b in sorted(s["hist"].items())},
            "negatives": s["neg"],
        }

    result = {
        "test": "WOWII142_bridge_oracle_R1_R2_R3_R4",
        "seed": SEED,
        "caps": {"COMP_CAP": COMP_CAP, "EXACT_N": EXACT_N,
                 "GEOD_CAP_LARGE": GEOD_CAP_LARGE, "CYC_CAP": CYC_CAP},
        "corpus_size": len(tasks),
        "skipped": dict(skipped),
        "validation": {"graphs": vg, "geodesic_checks": vp,
                       "cycle_checks": vk, "mismatches": 0},
        "slack_unit": "thirds (slack3 = 3*slack, exact integers)",
    }
    for key in ("R1", "R2", "R4"):
        sec = secs[key]
        result[key] = {
            "count": sec["count"],
            "capped_count": sec["capped_count"],
            "violation_count": len(sec["viol"]),
            "suspect_count": len(sec["suspect"]),
            "violations": sec["viol"][:MAX_VIOL],
            "suspects": sec["suspect"][:MAX_VIOL],
            "min_slack3": sec["min_slack3"], "min_witness": sec["min_wit"],
            "min_slack3_uncapped": sec["min_slack3_uncapped"],
            "min_witness_uncapped": sec["min_wit_uncapped"],
            "tight_count": sec["hist"].get(0, 0),
            "tight_examples": sec["tight"],
            "hist": {str(a): b for a, b in sorted(sec["hist"].items())},
        }
    result["R3"] = {
        "definition": "graphs with 2g+3f > 3(D+1), i.e. T1 (t>=D+1) alone "
                      "does not close C142",
        "members": r3["members"],
        "girth_hist": {str(a): b for a, b in sorted(r3["girth_hist"].items())},
        "excess3_hist": {str(a): b
                         for a, b in sorted(r3["excess3_hist"].items())},
        "R1_min_slack3_on_members": r3["R1_min_slack3"],
        "R1_uncapped_violations_on_members": r3["R1_viol"],
        "R1_min_witness": r3["R1_wit"],
        "R2_min_slack3_on_members": r3["R2_min_slack3"],
        "R2_uncapped_violations_on_members": r3["R2_viol"],
        "R2_min_witness": r3["R2_wit"],
        "examples": r3["examples"],
    }
    result["suspect_rechecks"] = rechecked
    encoded = (json.dumps(result, indent=2, sort_keys=True) + "\n").encode()
    OUT.write_bytes(encoded)
    print("results sha256:", hashlib.sha256(encoded).hexdigest().upper())

    eq_encoded = (json.dumps(eq_out, indent=2, sort_keys=True) + "\n").encode()
    OUT_EQ.write_bytes(eq_encoded)
    print("equality sha256:", hashlib.sha256(eq_encoded).hexdigest().upper())

    for key in ("R1", "R2", "R4"):
        r = result[key]
        print(f"{key}: count={r['count']} viol={r['violation_count']} "
              f"suspect={r['suspect_count']} min3={r['min_slack3']} "
              f"min3_uncapped={r['min_slack3_uncapped']} "
              f"tight={r['tight_count']}")
        print("   wit:", r["min_witness"])
    print(f"R3: members={result['R3']['members']} "
          f"girth_hist={result['R3']['girth_hist']} "
          f"R1viol={r3['R1_viol']} R2viol={r3['R2_viol']}")
    print(f"total {time.time() - t0:.0f}s")


if __name__ == "__main__":
    main()
