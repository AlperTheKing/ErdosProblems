#!/usr/bin/env python3
"""Exhaustive stdlib-only verifier for Proposition prop:rotor8-neutral of
sections/claude_eight_vertex_rotor.tex (eight-vertex neutral square rotor).

Graph R (Definition def:rotor8): vertices a,b,p,q,x,y,m,v; edges
  ax, yb, pm, vq  (pendants),  xm, my, yv, vx  (square),  ab, pq  (bad);
cut V0 = {x,y,p,q}, V1 = {m,v,a,b}; B = the eight crossing edges,
M = {ab, pq}.

Claimed permutation: sigma = (x m y v)(a p b q).

Checks (each printed PASS/FAIL):
  CHECK1 sigma is a graph automorphism of R: adjacency is preserved for
         ALL 28 unordered vertex pairs (edges -> edges, non-edges ->
         non-edges), hence sigma(E) = E.
  CHECK2 sigma has order exactly 4: sigma^4 = id and sigma^k != id for
         k = 1, 2, 3.
  CHECK3 cut compatibility: sigma exchanges the shores
         (sigma(V0) = V1 and sigma(V1) = V0) and fixes both edge classes
         setwise: sigma(B) = B, sigma(M) = M.
  CHECK4 states recomputed from scratch and transitivity:
         d_B(a,b) = d_B(p,q) = 4 by breadth-first search in B; ALL
         B-geodesics enumerated (layered exhaustive search: exactly two
         per bad edge); the selections are exactly the four resulting
         pairs; sigma maps selections to selections and its action on
         the four states is a single 4-cycle, hence transitive.
  CHECK5 the paper's explicit orbit labels: sigma maps geodesics
         A_m -> B_y -> A_v -> B_x -> A_m (as paths, up to reversal) and
         states w_mx -> w_my -> w_vy -> w_vx -> w_mx.

Exact set/integer arithmetic only; no third-party imports; ASCII output.
Prints PASS_ROTOR8_AUTOMORPHISM and exits 0 only if every check passes.
"""
import sys
from itertools import combinations, product

failures = []


def report(name, ok, detail=""):
    tag = "PASS" if ok else "FAIL"
    line = "%s %s" % (tag, name)
    if detail:
        line += " | " + detail
    print(line)
    if not ok:
        failures.append(name)


# ------------------------------------------------------------------ graph
V = ("a", "b", "p", "q", "x", "y", "m", "v")
pendant = [("a", "x"), ("y", "b"), ("p", "m"), ("v", "q")]
square = [("x", "m"), ("m", "y"), ("y", "v"), ("v", "x")]
bad_list = [("a", "b"), ("p", "q")]

B = frozenset(frozenset(e) for e in pendant + square)
M = frozenset(frozenset(e) for e in bad_list)
E = B | M
assert len(V) == 8 and len(B) == 8 and len(M) == 2 and len(E) == 10

V0 = frozenset(("x", "y", "p", "q"))
V1 = frozenset(("m", "v", "a", "b"))
assert V0 | V1 == frozenset(V) and not (V0 & V1)

# sigma = (x m y v)(a p b q)
sigma = {"x": "m", "m": "y", "y": "v", "v": "x",
         "a": "p", "p": "b", "b": "q", "q": "a"}


def apply_perm(perm, k):
    """perm composed with itself k times, as a dict on V."""
    out = {u: u for u in V}
    for _ in range(k):
        out = {u: perm[out[u]] for u in V}
    return out


def edge_image(perm, e):
    u, w = tuple(e)
    return frozenset((perm[u], perm[w]))


# ------------------------------------------------------- CHECK1 automorphism
ok1 = sorted(sigma) == sorted(V) and sorted(sigma.values()) == sorted(V)
bad_pairs = []
for u, w in combinations(V, 2):
    if (frozenset((u, w)) in E) != (frozenset((sigma[u], sigma[w])) in E):
        bad_pairs.append((u, w))
ok1 = ok1 and not bad_pairs
ok1 = ok1 and {edge_image(sigma, e) for e in E} == set(E)
report("CHECK1_automorphism", ok1,
       "all 28 vertex pairs adjacency-preserved; sigma(E)=E"
       if ok1 else "violations: %s" % bad_pairs)

# ------------------------------------------------------- CHECK2 order four
identity = {u: u for u in V}
powers = {k: apply_perm(sigma, k) for k in (1, 2, 3, 4)}
ok2 = (powers[4] == identity
       and all(powers[k] != identity for k in (1, 2, 3)))
report("CHECK2_order_four", ok2,
       "sigma^4=id; sigma^k!=id for k=1,2,3" if ok2 else
       "powers equal to id: %s" % [k for k in (1, 2, 3) if powers[k] == identity])

# ------------------------------------------------- CHECK3 cut compatibility
img_V0 = frozenset(sigma[u] for u in V0)
img_V1 = frozenset(sigma[u] for u in V1)
img_B = {edge_image(sigma, e) for e in B}
img_M = {edge_image(sigma, e) for e in M}
ok3 = (img_V0 == V1 and img_V1 == V0 and img_B == set(B) and img_M == set(M))
report("CHECK3_shore_swap_cut_preserved", ok3,
       "sigma(V0)=V1, sigma(V1)=V0, sigma(B)=B, sigma(M)=M" if ok3 else
       "sigma(V0)=%s sigma(B)==B:%s sigma(M)==M:%s"
       % (sorted(img_V0), img_B == set(B), img_M == set(M)))

# --------------------------------------- CHECK4 states from scratch + orbit
# Adjacency of the crossing graph B only.
adjB = {u: set() for u in V}
for e in B:
    u, w = tuple(e)
    adjB[u].add(w)
    adjB[w].add(u)


def bfs_dist(src):
    dist = {src: 0}
    frontier = [src]
    while frontier:
        nxt = []
        for u in frontier:
            for w in adjB[u]:
                if w not in dist:
                    dist[w] = dist[u] + 1
                    nxt.append(w)
        frontier = nxt
    return dist


def canon(path):
    """A geodesic and its reversal are the same object."""
    rev = tuple(reversed(path))
    return min(tuple(path), rev)


def all_geodesics(s, t):
    """ALL shortest s-t paths in B: layered exhaustive extension along
    strictly distance-decreasing steps (complete by BFS optimality)."""
    dist_t = bfs_dist(t)
    if s not in dist_t:
        return None, []
    d = dist_t[s]
    paths = []

    def extend(path):
        u = path[-1]
        if u == t:
            paths.append(canon(path))
            return
        for w in sorted(adjB[u]):
            if dist_t.get(w, -1) == dist_t[u] - 1:
                extend(path + [w])

    extend([s])
    return d, sorted(set(paths))


fam = {}          # bad edge -> sorted list of canonical geodesics
dist_ok = True
detail4 = []
for e in M:
    u, w = sorted(e)
    d, paths = all_geodesics(u, w)
    fam[e] = paths
    detail4.append("d_B(%s,%s)=%s #geodesics=%d" % (u, w, d, len(paths)))
    if d != 4 or len(paths) != 2:
        dist_ok = False

bad_edges_sorted = sorted(M, key=sorted)
states = set()
for choice in product(*(fam[e] for e in bad_edges_sorted)):
    states.add(frozenset(zip(bad_edges_sorted, choice)))
n_states_ok = (len(states) == 4)


def sigma_on_state(state):
    """Apply sigma vertexwise; returns the image selection, or None if some
    image path is not a geodesic of the image bad edge."""
    out = []
    for e, path in state:
        e2 = edge_image(sigma, e)
        p2 = canon([sigma[u] for u in path])
        if e2 not in fam or p2 not in fam[e2]:
            return None
        out.append((e2, p2))
    return frozenset(out)


action = {}
closed = True
for st in states:
    im = sigma_on_state(st)
    if im is None or im not in states:
        closed = False
        break
    action[st] = im

transitive = False
single_4cycle = False
if closed and n_states_ok:
    st0 = next(iter(states))
    orbit = [st0]
    cur = st0
    for _ in range(3):
        cur = action[cur]
        orbit.append(cur)
    transitive = (len(set(orbit)) == 4 and set(orbit) == states
                  and action[orbit[-1]] == st0)
    # every state has orbit size 4 (equivalent here, checked anyway)
    single_4cycle = all(
        len({s, action[s], action[action[s]],
             action[action[action[s]]]}) == 4 for s in states)

ok4 = dist_ok and n_states_ok and closed and transitive and single_4cycle
report("CHECK4_states_recomputed_transitive", ok4,
       "; ".join(detail4) + "; 4 selections; sigma-action = single 4-cycle "
       "(transitive)" if ok4 else
       "%s; #states=%d closed=%s transitive=%s"
       % ("; ".join(detail4), len(states), closed, transitive))

# ------------------------------------------- CHECK5 the paper's exact orbit
ok5 = False
detail5 = ""
if ok4:
    e_ab = frozenset(("a", "b"))
    e_pq = frozenset(("p", "q"))
    # label recomputed geodesics by their middle vertex (position 2 of 5)
    lab = {}
    for path in fam[e_ab]:
        lab["A_" + path[2]] = path        # expects A_m, A_v
    for path in fam[e_pq]:
        lab["B_" + path[2]] = path        # expects B_x, B_y
    if sorted(lab) == ["A_m", "A_v", "B_x", "B_y"]:
        # geodesic cycle A_m -> B_y -> A_v -> B_x -> A_m (up to reversal)
        geo_cycle = ["A_m", "B_y", "A_v", "B_x", "A_m"]
        geo_ok = all(
            canon([sigma[u] for u in lab[geo_cycle[i]]]) == lab[geo_cycle[i + 1]]
            for i in range(4))

        def state_of(na, nb):
            return frozenset([(e_ab, lab[na]), (e_pq, lab[nb])])

        w = {"w_mx": state_of("A_m", "B_x"), "w_my": state_of("A_m", "B_y"),
             "w_vy": state_of("A_v", "B_y"), "w_vx": state_of("A_v", "B_x")}
        st_cycle = ["w_mx", "w_my", "w_vy", "w_vx", "w_mx"]
        states_ok = set(w.values()) == states
        st_ok = all(action[w[st_cycle[i]]] == w[st_cycle[i + 1]]
                    for i in range(4))
        ok5 = geo_ok and states_ok and st_ok
        detail5 = ("sigma: A_m->B_y->A_v->B_x->A_m and "
                   "w_mx->w_my->w_vy->w_vx->w_mx" if ok5 else
                   "geo_ok=%s states_ok=%s st_ok=%s"
                   % (geo_ok, states_ok, st_ok))
    else:
        detail5 = "unexpected geodesic labels: %s" % sorted(lab)
else:
    detail5 = "skipped (CHECK4 failed)"
report("CHECK5_paper_orbit_labels", ok5, detail5)

# ------------------------------------------------------------------ verdict
if failures:
    print("FAIL_ROTOR8_AUTOMORPHISM (%s)" % ", ".join(failures))
    sys.exit(1)
print("PASS_ROTOR8_AUTOMORPHISM")
sys.exit(0)
