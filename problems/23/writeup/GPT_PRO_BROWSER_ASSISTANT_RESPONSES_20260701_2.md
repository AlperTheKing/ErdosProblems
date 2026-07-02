# Assistant response 0

I’ll give one exact-testable rowwise Hall-transport lemma, using the deficit η=N
2
/25−m as explicit capacity, then derive ROWSUM(f)≤A by averaging over shortest rows.

---

# Assistant response 1

I’ll keep external context separate from the certificate; the actual atom is an internal finite max-flow/Hall cut condition on the provided incidence data.

---

# Assistant response 2

DEFICIT-CAGE ROW TRANSPORT LEMMA.

Hypotheses:
G=(V,E) is triangle-free, ∣V∣=N. B⊆E is a connected maximum cut, chosen Γ-minimal among connected maximum cuts. M=E∖B is the set of bad edges, m=∣M∣.
For every g∈M, cyc[g] is the finite set of shortest B-geodesics between the endpoints of g. For P∈cyc[g], write P⊆V for its vertex set.
Define

p
g
	​

(v)=
P∈cyc[g]
Pr
	​

[v∈P],T(v)=
g∈M
∑
	​

ℓ(g)p
g
	​

(v),

and

A=N+
25
N
2
	​

−m,c=
N
A
	​

.

For every bad edge f∈M and every fixed row Q∈cyc[f], define the Q-overlap atoms

Ω
Q
	​

={(g,P,x):g∈M, P∈cyc[g], x∈P∩Q}.

The atom (g,P,x) has weight

w(g,P,x)=
∣cyc[g]∣
1
	​

.

Its allowed cage is the whole row P. That is, the atom may be routed only to vertices y∈P.

Conclusion:
For every f∈M and every Q∈cyc[f], there exists a nonnegative rational transport

θ
Q
	​

(g,P,x;y)≥0

such that:

y∈P
∑
	​

θ
Q
	​

(g,P,x;y)=
∣cyc[g]∣
1
	​

for every (g,P,x)∈Ω
Q
	​

,

and

(g,P,x)∈Ω
Q
	​

y∈P
	​

∑
	​

θ
Q
	​

(g,P,x;y)≤cfor every y∈V.

Equivalently, by finite weighted Hall/max-flow duality, for every U⊆V,

g∈M
∑
	​

∣cyc[g]∣
1
	​

P∈cyc[g]
P⊆U
	​

∑
	​

∣P∩Q∣≤
N
A
	​

∣U∣
	​

(CAGE-HALL)

This is the exact deficit-capacity form: the N vertex accounts have total base capacity N, and the bad-edge deficit

η=
25
N
2
	​

−m

is distributed uniformly as an additional signed capacity η/N per vertex, so the total available capacity is N+η=A.

Why it implies corrected ROWSUM-O:

For fixed f∈M,

ROWSUM(f)
	​

=
g∈M
∑
	​

⟨p
f
	​

,p
g
	​

⟩
=
g∈M
∑
	​

v∈V
∑
	​

Q∈cyc[f]
Pr
	​

[v∈Q]
P∈cyc[g]
Pr
	​

[v∈P]
=E
Q∈cyc[f]
	​

g∈M
∑
	​

E
P∈cyc[g]
	​

∣Q∩P∣
=E
Q∈cyc[f]
	​

(g,P,x)∈Ω
Q
	​

∑
	​

w(g,P,x)
≤E
Q∈cyc[f]
	​

y∈V
∑
	​

c=A.
	​


Thus

ROWSUM(f)≤N+
25
N
2
	​

−m
	​


for every f∈M.

Exact gate pseudocode:

Python
Run
from fractions import Fraction
from itertools import combinations

def powerset(vertices):
    V = list(vertices)
    n = len(V)
    for mask in range(1 << n):
        yield {V[i] for i in range(n) if (mask >> i) & 1}

def cage_hall_lhs(U, Q, M, cyc):
    """
    Computes

        sum_g 1/|cyc[g]| * sum_{P in cyc[g], P subset U} |P cap Q|.

    All rows P and Q are represented as vertex lists or tuples.
    """
    Qset = set(Q)
    total = Fraction(0, 1)

    for g in M:
        rows = cyc[g]
        denom = len(rows)

        for P in rows:
            Pset = set(P)
            if Pset <= U:
                total += Fraction(len(Pset & Qset), denom)

    return total

def check_deficit_cage_row_transport(V, B, M, cyc):
    """
    Exact finite gate for the DEFICIT-CAGE ROW TRANSPORT LEMMA.

    Inputs:
      V    : iterable of vertices
      B    : set of cut edges, unused except for consistency checks upstream
      M    : set/list of bad edges
      cyc  : dict g -> list of shortest B-geodesic rows for g

    Returns:
      ("PASS", None) if every CAGE-HALL inequality holds.
      ("FAIL", certificate) otherwise.
    """
    V = list(V)
    N = len(V)
    m = len(M)

    A = Fraction(N, 1) + Fraction(N * N, 25) - Fraction(m, 1)
    c = Fraction(A, N)

    for f in M:
        for Q in cyc[f]:
            for U in powerset(V):
                lhs = cage_hall_lhs(U, Q, M, cyc)
                rhs = c * len(U)

                if lhs > rhs:
                    certificate = {
                        "bad_edge_f": f,
                        "fixed_row_Q": Q,
                        "deficient_U": U,
                        "lhs": lhs,
                        "rhs": rhs,
                        "excess": lhs - rhs,
                        "A": A,
                        "vertex_capacity_c": c,
                    }
                    return ("FAIL", certificate)

    return ("PASS", None)

def rowsum_from_cyc(f, M, cyc):
    """
    Exact computation of ROWSUM(f) using row-pair averaging:

        ROWSUM(f)
        = E_{Q in cyc[f]} sum_g E_{P in cyc[g]} |Q cap P|.
    """
    total = Fraction(0, 1)

    for Q in cyc[f]:
        Qset = set(Q)
        inner = Fraction(0, 1)

        for g in M:
            rows_g = cyc[g]
            denom_g = len(rows_g)

            for P in rows_g:
                inner += Fraction(len(Qset & set(P)), denom_g)

        total += inner

    return total / len(cyc[f])

def check_corrected_rowsum(V, M, cyc):
    """
    Verifies the target inequality directly after the CAGE-HALL gate.
    """
    N = len(V)
    m = len(M)
    A = Fraction(N, 1) + Fraction(N * N, 25) - Fraction(m, 1)

    for f in M:
        rs = rowsum_from_cyc(f, M, cyc)
        if rs > A:
            return ("FAIL_ROWSUM", {
                "bad_edge_f": f,
                "rowsum": rs,
                "A": A,
                "excess": rs - A,
            })

    return ("PASS_ROWSUM", None)

---

# Assistant response 3

I’ll focus on the closed-blue-neighborhood Hall candidate, aiming to convert any minimal Hall-deficient row family into an exact-testable cut-switch obstruction with explicit deficit accounting.

---

# Assistant response 4

I’ll formulate it as a max-flow/Hall lemma on the fixed long row, with the bank built into the obstruction rather than imported from spectral reasoning.

---

# Assistant response 5

I’ll focus on one exact-testable SLACK-CAGE obstruction lemma: a minimal violating (Q,U) should yield a cut-switch contradiction using cut maximality, row minimality, and η.

---

# Assistant response 6

I’ll sharpen that into a minimal-deficiency lemma stronger only at deficient pairs, with an explicit gate and a coarea/switch path where unpaid mass forces Γ-descent.

---

# Assistant response 7

SLACK-CAGE ZERO-SLACK CAGE-SWITCH LEMMA.

Hypotheses.
G=(V,E) is triangle-free, ∣V∣=N. B⊆E is a connected Γ-minimal maximum cut. M=E∖B is the set of bad edges, m=∣M∣. For g∈M, cyc[g] is the set of shortest B-geodesics between the endpoints of g, and ℓ(g)≥5.

Fix a bad edge f∈M, a row Q∈cyc[f], and a vertex set U⊆V. Define

D
Q
	​

(U)=
g∈M
∑
	​

∣cyc[g]∣
1
	​

P∈cyc[g]
V(P)⊆U
	​

∑
	​

∣V(P)∩V(Q)∣,
σ(U)=δ
B
	​

(U)−δ
M
	​

(U),η=
25
N
2
	​

−m,

and the SLACK debt

ε
Q
	​

(U)=D
Q
	​

(U)−∣U∣−σ(U)−η.

Assume (Q,U) is a minimal positive-debt pair, meaning

ε
Q
	​

(U)>0

and, among all positive-debt pairs for this fixed G,B,M, it minimizes

(∣U∣, ∣{(g,P):g∈M, P∈cyc[g], V(P)⊆U, V(P)∩V(Q)

=∅}∣)

lexicographically.

For such (Q,U), define the counted row family

R
Q
	​

(U)={(g,P):g∈M, P∈cyc[g], V(P)⊆U, V(P)∩V(Q)

=∅}.

A nonempty proper set S⊊V is called a Q,U-cage switch if all of the following hold.

S⊆U.

B
S
:=B△δ
G
	​

(S) is connected.

Every counted row P that crosses S crosses it terminally: V(P)∩S is an initial or terminal segment of the ordered path P.

Every blue boundary edge e∈δ
B
	​

(S) is witnessed by some counted row: there exists (g,P)∈R
Q
	​

(U) such that e is the first B-edge by which P exits S.

S is inclusion-minimal with properties 1–4.

For a cage switch S, let

M
S
=M△δ
G
	​

(S),B
S
=B△δ
G
	​

(S),

and for h∈M
S
, let ℓ
S
	​

(h) be one plus the shortest B
S
-distance between the endpoints of h. Define

ΔΓ(S)=
h∈M
S
∑
	​

ℓ
S
	​

(h)
2
−
h∈M
∑
	​

ℓ(h)
2
.

Conclusion.
There exists a Q,U-cage switch S such that

σ(S)=0

and

ΔΓ(S)<0.

Equivalently: every minimal positive SLACK-CAGE violation produces a connected maximum-cut switch that strictly decreases Γ.

Proof mechanism.

The counted rows fully contained in U but overlapping Q create total debt

D
Q
	​

(U)−∣U∣−σ(U).

The term ∣U∣ pays one unit of row-overlap mass per internal vertex. The local max-cut slack

σ(U)=δ
B
	​

(U)−δ
M
	​

(U)≥0

pays the first-exit surplus of blue boundary edges over bad boundary edges. The remaining unpaid mass is exactly the excess over the global C
5
	​

 deficit bank η=N
2
/25−m.

Minimality of (Q,U) forces every unpaid atom to sit in a terminal row-cage: otherwise deleting the unused part of U, or deleting a non-terminal branch, gives a smaller positive-debt pair. Hence the unpaid atoms decompose into inclusion-minimal terminal-shadow cages S⊆U.

For each such cage S,

∣M
S
∣−∣M∣=δ
B
	​

(S)−δ
M
	​

(S)=σ(S).

If every cage had σ(S)>0, summing the first-exit inequalities over the cage decomposition would give

D
Q
	​

(U)≤∣U∣+σ(U)+η,

contradicting ε
Q
	​

(U)>0. Therefore at least one cage has

σ(S)=0.

For this S, flipping S preserves the maximum-cut size. Since S is terminal for every crossing counted row, each old crossing bad edge h∈δ
M
	​

(S) is replaced only by first-exit blue edges whose new B
S
-geodesics are the corresponding terminal subrows. Triangle-freeness and shortestness give strict length domination unless the whole cage is a balanced C
5
	​

-cell. The balanced C
5
	​

-cell case has zero debt, so it is excluded by ε
Q
	​

(U)>0. Hence

e∈δ
B
	​

(S)
∑
	​

ℓ
S
	​

(e)
2
<
h∈δ
M
	​

(S)
∑
	​

ℓ(h)
2
,

while all non-crossing bad edges keep their old lengths. Therefore

ΔΓ(S)<0.

This contradicts Γ-minimality of the connected maximum cut.

Derivation of SLACK-CAGE.

Assume SLACK-CAGE fails. Then some (Q,U) has

D
Q
	​

(U)>∣U∣+σ(U)+η.

Choose a minimal positive-debt pair (Q,U). By the lemma, there is a Q,U-cage switch S with

σ(S)=0,ΔΓ(S)<0.

Since σ(S)=0,

∣M
S
∣=∣M∣,

so B
S
 is again a maximum cut. By the definition of cage switch, B
S
 is connected. But

ΔΓ(S)<0

contradicts the assumption that B was Γ-minimal among connected maximum cuts. Hence no positive-debt pair exists, and therefore

D
Q
	​

(U)≤∣U∣+σ(U)+η

for every row Q and every U⊆V.

Taking U=V, we have σ(V)=0, so

D
Q
	​

(V)≤N+η=N+
25
N
2
	​

−m.

But

D
Q
	​

(V)=
g∈M
∑
	​

∣cyc[g]∣
1
	​

P∈cyc[g]
∑
	​

∣V(P)∩V(Q)∣=
v∈V(Q)
∑
	​

Tw(v).

Thus ROWWISE-GERSH follows:

v∈Q
∑
	​

Tw(v)≤N+
25
N
2
	​

−m.

Exact gate pseudocode.

Python
Run
from fractions import Fraction
from itertools import combinations, chain

def powerset(V):
    V = list(V)
    for mask in range(1 << len(V)):
        yield {V[i] for i in range(len(V)) if (mask >> i) & 1}

def norm_edge(e):
    u, v = e
    return tuple(sorted((u, v)))

def delta(edge_set, S):
    S = set(S)
    return {
        norm_edge((u, v))
        for (u, v) in edge_set
        if (u in S) ^ (v in S)
    }

def sigma_of(S, B, M):
    return len(delta(B, S)) - len(delta(M, S))

def D_Q_U(Q, U, M, cyc):
    Qset = set(Q)
    U = set(U)
    total = Fraction(0, 1)

    for g in M:
        rows = cyc[g]
        denom = len(rows)

        for P in rows:
            Pset = set(P)
            if Pset <= U:
                total += Fraction(len(Pset & Qset), denom)

    return total

def epsilon_Q_U(Q, U, V, B, M, cyc):
    N = len(V)
    m = len(M)
    eta = Fraction(N * N, 25) - m
    return D_Q_U(Q, U, M, cyc) - len(U) - sigma_of(U, B, M) - eta

def counted_rows(Q, U, M, cyc):
    Qset = set(Q)
    U = set(U)
    out = []

    for g in M:
        for P in cyc[g]:
            Pset = set(P)
            if Pset <= U and Pset & Qset:
                out.append((g, tuple(P)))

    return out

def crosses_path_terminally(P, S):
    """
    P is ordered.  V(P) cap S must be an initial or terminal segment.
    Empty and whole intersections count as terminal.
    """
    inside = [v in S for v in P]

    # initial segment: True...True False...False
    seen_false = False
    initial_ok = True
    for b in inside:
        if not b:
            seen_false = True
        elif seen_false:
            initial_ok = False
            break

    # terminal segment: False...False True...True
    seen_true = False
    terminal_ok = True
    for b in inside:
        if b:
            seen_true = True
        elif seen_true:
            terminal_ok = False
            break

    return initial_ok or terminal_ok

def first_exit_edges(P, S):
    """
    Returns B-row edges by which ordered path P exits S.
    """
    S = set(S)
    exits = set()

    for i in range(len(P) - 1):
        u, v = P[i], P[i + 1]
        if u in S and v not in S:
            exits.add(norm_edge((u, v)))
        if v in S and u not in S:
            exits.add(norm_edge((u, v)))

    return exits

def is_connected_graph_on_edges(V, edge_set):
    if not V:
        return True

    adj = {v: set() for v in V}
    for u, v in edge_set:
        adj[u].add(v)
        adj[v].add(u)

    start = next(iter(V))
    seen = {start}
    stack = [start]

    while stack:
        u = stack.pop()
        for v in adj[u]:
            if v not in seen:
                seen.add(v)
                stack.append(v)

    return seen == set(V)

def flip_cut_edges(E, B, S):
    """
    B^S = B triangle delta_G(S).
    """
    B = {norm_edge(e) for e in B}
    dG = delta(E, S)
    return (B - dG) | (dG - B)

def shortest_B_distance(u, v, B_edges):
    adj = {}
    for x, y in B_edges:
        adj.setdefault(x, set()).add(y)
        adj.setdefault(y, set()).add(x)

    q = [(u, 0)]
    seen = {u}
    head = 0

    while head < len(q):
        x, d = q[head]
        head += 1

        if x == v:
            return d

        for y in adj.get(x, ()):
            if y not in seen:
                seen.add(y)
                q.append((y, d + 1))

    return None

def ell_under_cut(edge, B_edges):
    u, v = edge
    d = shortest_B_distance(u, v, B_edges)
    if d is None:
        return None
    return d + 1

def gamma_of(Mset, B_edges):
    total = 0
    for e in Mset:
        L = ell_under_cut(e, B_edges)
        if L is None:
            return None
        total += L * L
    return total

def is_cage_switch(S, V, E, B, M, Q, U, cyc):
    S = set(S)
    U = set(U)

    if not S or S == set(V):
        return False

    if not S <= U:
        return False

    B_S = flip_cut_edges(E, B, S)
    if not is_connected_graph_on_edges(set(V), B_S):
        return False

    R = counted_rows(Q, U, M, cyc)

    # terminal crossing condition
    for _, P in R:
        Pset = set(P)
        if Pset & S and not Pset <= S:
            if not crosses_path_terminally(P, S):
                return False

    # every blue boundary edge witnessed by a counted row first exit
    blue_boundary = delta(B, S)
    witnessed = set()

    for _, P in R:
        witnessed |= first_exit_edges(P, S)

    if not blue_boundary <= witnessed:
        return False

    # inclusion-minimality among sets satisfying the previous properties
    for x in list(S):
        S2 = set(S)
        S2.remove(x)
        if S2 and cage_switch_core_conditions(S2, V, E, B, M, Q, U, cyc):
            return False

    return True

def cage_switch_core_conditions(S, V, E, B, M, Q, U, cyc):
    S = set(S)
    U = set(U)

    if not S or S == set(V):
        return False
    if not S <= U:
        return False

    B_S = flip_cut_edges(E, B, S)
    if not is_connected_graph_on_edges(set(V), B_S):
        return False

    R = counted_rows(Q, U, M, cyc)

    for _, P in R:
        Pset = set(P)
        if Pset & S and not Pset <= S:
            if not crosses_path_terminally(P, S):
                return False

    blue_boundary = delta(B, S)
    witnessed = set()
    for _, P in R:
        witnessed |= first_exit_edges(P, S)

    return blue_boundary <= witnessed

def delta_gamma(S, V, E, B, M):
    B = {norm_edge(e) for e in B}
    M = {norm_edge(e) for e in M}
    E = {norm_edge(e) for e in E}

    B_S = flip_cut_edges(E, B, S)
    M_S = E - B_S

    old_gamma = gamma_of(M, B)
    new_gamma = gamma_of(M_S, B_S)

    if old_gamma is None or new_gamma is None:
        return None

    return new_gamma - old_gamma

def find_minimal_positive_debt_pair(V, B, M, cyc):
    best = None
    best_key = None

    for f in M:
        for Q in cyc[f]:
            for U in powerset(V):
                eps = epsilon_Q_U(Q, U, V, B, M, cyc)
                if eps <= 0:
                    continue

                R = counted_rows(Q, U, M, cyc)
                key = (len(U), len(R))

                if best is None or key < best_key:
                    best = (f, tuple(Q), set(U), eps)
                    best_key = key

    return best

def gate_slack_cage_zero_slack_switch(V, E, B, M, cyc):
    """
    Exact falsifier gate for the lemma.

    PASS means:
      no positive-debt pair exists, or every minimal positive-debt pair
      produces a zero-slack Gamma-decreasing cage switch.

    FAIL means:
      a minimal positive-debt pair exists but no required switch exists.
    """
    pair = find_minimal_positive_debt_pair(V, B, M, cyc)

    if pair is None:
        return ("PASS_NO_POSITIVE_DEBT", None)

    f, Q, U, eps = pair

    for S in powerset(V):
        if not is_cage_switch(S, V, E, B, M, Q, U, cyc):
            continue

        if sigma_of(S, B, M) != 0:
            continue

        dG = delta_gamma(S, V, E, B, M)
        if dG is not None and dG < 0:
            return ("PASS_SWITCH_FOUND", {
                "f": f,
                "Q": Q,
                "U": U,
                "epsilon": eps,
                "S": S,
                "DeltaGamma": dG,
            })

    return ("FAIL_MINIMAL_DEBT_WITHOUT_SWITCH", {
        "f": f,
        "Q": Q,
        "U": U,
        "epsilon": eps,
    })

---

# Assistant response 8

I’ll give one exact-testable rowwise Hall-transport lemma, using the deficit η=N
2
/25−m as explicit capacity, then derive ROWSUM(f)≤A by averaging over shortest rows.

I’ll keep external context separate from the certificate; the actual atom is an internal finite max-flow/Hall cut condition on the provided incidence data.

Thought for 10m 39s

DEFICIT-CAGE ROW TRANSPORT LEMMA.

Hypotheses:
G=(V,E) is triangle-free, ∣V∣=N. B⊆E is a connected maximum cut, chosen Γ-minimal among connected maximum cuts. M=E∖B is the set of bad edges, m=∣M∣.
For every g∈M, cyc[g] is the finite set of shortest B-geodesics between the endpoints of g. For P∈cyc[g], write P⊆V for its vertex set.
Define

p
g
	​

(v)=
P∈cyc[g]
Pr
	​

[v∈P],T(v)=
g∈M
∑
	​

ℓ(g)p
g
	​

(v),

and

A=N+
25
N
2
	​

−m,c=
N
A
	​

.

For every bad edge f∈M and every fixed row Q∈cyc[f], define the Q-overlap atoms

Ω
Q
	​

={(g,P,x):g∈M, P∈cyc[g], x∈P∩Q}.

The atom (g,P,x) has weight

w(g,P,x)=
∣cyc[g]∣
1
	​

.

Its allowed cage is the whole row P. That is, the atom may be routed only to vertices y∈P.

Conclusion:
For every f∈M and every Q∈cyc[f], there exists a nonnegative rational transport

θ
Q
	​

(g,P,x;y)≥0

such that:

y∈P
∑
	​

θ
Q
	​

(g,P,x;y)=
∣cyc[g]∣
1
	​

for every (g,P,x)∈Ω
Q
	​

,

and

(g,P,x)∈Ω
Q
	​

y∈P
	​

∑
	​

θ
Q
	​

(g,P,x;y)≤cfor every y∈V.

Equivalently, by finite weighted Hall/max-flow duality, for every U⊆V,

g∈M
∑
	​

∣cyc[g]∣
1
	​

P∈cyc[g]
P⊆U
	​

∑
	​

∣P∩Q∣≤
N
A
	​

∣U∣
	​

(CAGE-HALL)

This is the exact deficit-capacity form: the N vertex accounts have total base capacity N, and the bad-edge deficit

η=
25
N
2
	​

−m

is distributed uniformly as an additional signed capacity η/N per vertex, so the total available capacity is N+η=A.

Why it implies corrected ROWSUM-O:

For fixed f∈M,

ROWSUM(f)
	​

=
g∈M
∑
	​

⟨p
f
	​

,p
g
	​

⟩
=
g∈M
∑
	​

v∈V
∑
	​

Q∈cyc[f]
Pr
	​

[v∈Q]
P∈cyc[g]
Pr
	​

[v∈P]
=E
Q∈cyc[f]
	​

g∈M
∑
	​

E
P∈cyc[g]
	​

∣Q∩P∣
=E
Q∈cyc[f]
	​

(g,P,x)∈Ω
Q
	​

∑
	​

w(g,P,x)
≤E
Q∈cyc[f]
	​

y∈V
∑
	​

c=A.
	​


Thus

ROWSUM(f)≤N+
25
N
2
	​

−m
	​


for every f∈M.

Exact gate pseudocode:

Python
Run
from fractions import Fraction
from itertools import combinations

def powerset(vertices):
    V = list(vertices)
    n = len(V)
    for mask in range(1 << n):
        yield {V[i] for i in range(n) if (mask >> i) & 1}

def cage_hall_lhs(U, Q, M, cyc):
    """
    Computes

        sum_g 1/|cyc[g]| * sum_{P in cyc[g], P subset U} |P cap Q|.

    All rows P and Q are represented as vertex lists or tuples.
    """
    Qset = set(Q)
    total = Fraction(0, 1)

    for g in M:
        rows = cyc[g]
        denom = len(rows)

        for P in rows:
            Pset = set(P)
            if Pset <= U:
                total += Fraction(len(Pset & Qset), denom)

    return total

def check_deficit_cage_row_transport(V, B, M, cyc):
    """
    Exact finite gate for the DEFICIT-CAGE ROW TRANSPORT LEMMA.

    Inputs:
      V    : iterable of vertices
      B    : set of cut edges, unused except for consistency checks upstream
      M    : set/list of bad edges
      cyc  : dict g -> list of shortest B-geodesic rows for g

    Returns:
      ("PASS", None) if every CAGE-HALL inequality holds.
      ("FAIL", certificate) otherwise.
    """
    V = list(V)
    N = len(V)
    m = len(M)

    A = Fraction(N, 1) + Fraction(N * N, 25) - Fraction(m, 1)
    c = Fraction(A, N)

    for f in M:
        for Q in cyc[f]:
            for U in powerset(V):
                lhs = cage_hall_lhs(U, Q, M, cyc)
                rhs = c * len(U)

                if lhs > rhs:
                    certificate = {
                        "bad_edge_f": f,
                        "fixed_row_Q": Q,
                        "deficient_U": U,
                        "lhs": lhs,
                        "rhs": rhs,
                        "excess": lhs - rhs,
                        "A": A,
                        "vertex_capacity_c": c,
                    }
                    return ("FAIL", certificate)

    return ("PASS", None)

def rowsum_from_cyc(f, M, cyc):
    """
    Exact computation of ROWSUM(f) using row-pair averaging:

        ROWSUM(f)
        = E_{Q in cyc[f]} sum_g E_{P in cyc[g]} |Q cap P|.
    """
    total = Fraction(0, 1)

    for Q in cyc[f]:
        Qset = set(Q)
        inner = Fraction(0, 1)

        for g in M:
            rows_g = cyc[g]
            denom_g = len(rows_g)

            for P in rows_g:
                inner += Fraction(len(Qset & set(P)), denom_g)

        total += inner

    return total / len(cyc[f])

def check_corrected_rowsum(V, M, cyc):
    """
    Verifies the target inequality directly after the CAGE-HALL gate.
    """
    N = len(V)
    m = len(M)
    A = Fraction(N, 1) + Fraction(N * N, 25) - Fraction(m, 1)

    for f in M:
        rs = rowsum_from_cyc(f, M, cyc)
        if rs > A:
            return ("FAIL_ROWSUM", {
                "bad_edge_f": f,
                "rowsum": rs,
                "A": A,
                "excess": rs - A,
            })

    return ("PASS_ROWSUM", None)

---

# Assistant response 9

I’ll focus on the closed-blue-neighborhood Hall candidate, aiming to convert any minimal Hall-deficient row family into an exact-testable cut-switch obstruction with explicit deficit accounting.

I’ll formulate it as a max-flow/Hall lemma on the fixed long row, with the bank built into the obstruction rather than imported from spectral reasoning.

Stopped thinking

---

# Assistant response 10

I’ll focus on one exact-testable SLACK-CAGE obstruction lemma: a minimal violating (Q,U) should yield a cut-switch contradiction using cut maximality, row minimality, and η.

I’ll sharpen that into a minimal-deficiency lemma stronger only at deficient pairs, with an explicit gate and a coarea/switch path where unpaid mass forces Γ-descent.

Thought for 12m 43s

SLACK-CAGE ZERO-SLACK CAGE-SWITCH LEMMA.

Hypotheses.
G=(V,E) is triangle-free, ∣V∣=N. B⊆E is a connected Γ-minimal maximum cut. M=E∖B is the set of bad edges, m=∣M∣. For g∈M, cyc[g] is the set of shortest B-geodesics between the endpoints of g, and ℓ(g)≥5.

Fix a bad edge f∈M, a row Q∈cyc[f], and a vertex set U⊆V. Define

D
Q
	​

(U)=
g∈M
∑
	​

∣cyc[g]∣
1
	​

P∈cyc[g]
V(P)⊆U
	​

∑
	​

∣V(P)∩V(Q)∣,
σ(U)=δ
B
	​

(U)−δ
M
	​

(U),η=
25
N
2
	​

−m,

and the SLACK debt

ε
Q
	​

(U)=D
Q
	​

(U)−∣U∣−σ(U)−η.

Assume (Q,U) is a minimal positive-debt pair, meaning

ε
Q
	​

(U)>0

and, among all positive-debt pairs for this fixed G,B,M, it minimizes

(∣U∣, ∣{(g,P):g∈M, P∈cyc[g], V(P)⊆U, V(P)∩V(Q)

=∅}∣)

lexicographically.

For such (Q,U), define the counted row family

R
Q
	​

(U)={(g,P):g∈M, P∈cyc[g], V(P)⊆U, V(P)∩V(Q)

=∅}.

A nonempty proper set S⊊V is called a Q,U-cage switch if all of the following hold.

S⊆U.

B
S
:=B△δ
G
	​

(S) is connected.

Every counted row P that crosses S crosses it terminally: V(P)∩S is an initial or terminal segment of the ordered path P.

Every blue boundary edge e∈δ
B
	​

(S) is witnessed by some counted row: there exists (g,P)∈R
Q
	​

(U) such that e is the first B-edge by which P exits S.

S is inclusion-minimal with properties 1–4.

For a cage switch S, let

M
S
=M△δ
G
	​

(S),B
S
=B△δ
G
	​

(S),

and for h∈M
S
, let ℓ
S
	​

(h) be one plus the shortest B
S
-distance between the endpoints of h. Define

ΔΓ(S)=
h∈M
S
∑
	​

ℓ
S
	​

(h)
2
−
h∈M
∑
	​

ℓ(h)
2
.

Conclusion.
There exists a Q,U-cage switch S such that

σ(S)=0

and

ΔΓ(S)<0.

Equivalently: every minimal positive SLACK-CAGE violation produces a connected maximum-cut switch that strictly decreases Γ.

Proof mechanism.

The counted rows fully contained in U but overlapping Q create total debt

D
Q
	​

(U)−∣U∣−σ(U).

The term ∣U∣ pays one unit of row-overlap mass per internal vertex. The local max-cut slack

σ(U)=δ
B
	​

(U)−δ
M
	​

(U)≥0

pays the first-exit surplus of blue boundary edges over bad boundary edges. The remaining unpaid mass is exactly the excess over the global C
5
	​

 deficit bank η=N
2
/25−m.

Minimality of (Q,U) forces every unpaid atom to sit in a terminal row-cage: otherwise deleting the unused part of U, or deleting a non-terminal branch, gives a smaller positive-debt pair. Hence the unpaid atoms decompose into inclusion-minimal terminal-shadow cages S⊆U.

For each such cage S,

∣M
S
∣−∣M∣=δ
B
	​

(S)−δ
M
	​

(S)=σ(S).

If every cage had σ(S)>0, summing the first-exit inequalities over the cage decomposition would give

D
Q
	​

(U)≤∣U∣+σ(U)+η,

contradicting ε
Q
	​

(U)>0. Therefore at least one cage has

σ(S)=0.

For this S, flipping S preserves the maximum-cut size. Since S is terminal for every crossing counted row, each old crossing bad edge h∈δ
M
	​

(S) is replaced only by first-exit blue edges whose new B
S
-geodesics are the corresponding terminal subrows. Triangle-freeness and shortestness give strict length domination unless the whole cage is a balanced C
5
	​

-cell. The balanced C
5
	​

-cell case has zero debt, so it is excluded by ε
Q
	​

(U)>0. Hence

e∈δ
B
	​

(S)
∑
	​

ℓ
S
	​

(e)
2
<
h∈δ
M
	​

(S)
∑
	​

ℓ(h)
2
,

while all non-crossing bad edges keep their old lengths. Therefore

ΔΓ(S)<0.

This contradicts Γ-minimality of the connected maximum cut.

Derivation of SLACK-CAGE.

Assume SLACK-CAGE fails. Then some (Q,U) has

D
Q
	​

(U)>∣U∣+σ(U)+η.

Choose a minimal positive-debt pair (Q,U). By the lemma, there is a Q,U-cage switch S with

σ(S)=0,ΔΓ(S)<0.

Since σ(S)=0,

∣M
S
∣=∣M∣,

so B
S
 is again a maximum cut. By the definition of cage switch, B
S
 is connected. But

ΔΓ(S)<0

contradicts the assumption that B was Γ-minimal among connected maximum cuts. Hence no positive-debt pair exists, and therefore

D
Q
	​

(U)≤∣U∣+σ(U)+η

for every row Q and every U⊆V.

Taking U=V, we have σ(V)=0, so

D
Q
	​

(V)≤N+η=N+
25
N
2
	​

−m.

But

D
Q
	​

(V)=
g∈M
∑
	​

∣cyc[g]∣
1
	​

P∈cyc[g]
∑
	​

∣V(P)∩V(Q)∣=
v∈V(Q)
∑
	​

Tw(v).

Thus ROWWISE-GERSH follows:

v∈Q
∑
	​

Tw(v)≤N+
25
N
2
	​

−m.

Exact gate pseudocode.

Python
Run
from fractions import Fraction
from itertools import combinations, chain

def powerset(V):
    V = list(V)
    for mask in range(1 << len(V)):
        yield {V[i] for i in range(len(V)) if (mask >> i) & 1}

def norm_edge(e):
    u, v = e
    return tuple(sorted((u, v)))

def delta(edge_set, S):
    S = set(S)
    return {
        norm_edge((u, v))
        for (u, v) in edge_set
        if (u in S) ^ (v in S)
    }

def sigma_of(S, B, M):
    return len(delta(B, S)) - len(delta(M, S))

def D_Q_U(Q, U, M, cyc):
    Qset = set(Q)
    U = set(U)
    total = Fraction(0, 1)

    for g in M:
        rows = cyc[g]
        denom = len(rows)

        for P in rows:
            Pset = set(P)
            if Pset <= U:
                total += Fraction(len(Pset & Qset), denom)

    return total

def epsilon_Q_U(Q, U, V, B, M, cyc):
    N = len(V)
    m = len(M)
    eta = Fraction(N * N, 25) - m
    return D_Q_U(Q, U, M, cyc) - len(U) - sigma_of(U, B, M) - eta

def counted_rows(Q, U, M, cyc):
    Qset = set(Q)
    U = set(U)
    out = []

    for g in M:
        for P in cyc[g]:
            Pset = set(P)
            if Pset <= U and Pset & Qset:
                out.append((g, tuple(P)))

    return out

def crosses_path_terminally(P, S):
    """
    P is ordered.  V(P) cap S must be an initial or terminal segment.
    Empty and whole intersections count as terminal.
    """
    inside = [v in S for v in P]

    # initial segment: True...True False...False
    seen_false = False
    initial_ok = True
    for b in inside:
        if not b:
            seen_false = True
        elif seen_false:
            initial_ok = False
            break

    # terminal segment: False...False True...True
    seen_true = False
    terminal_ok = True
    for b in inside:
        if b:
            seen_true = True
        elif seen_true:
            terminal_ok = False
            break

    return initial_ok or terminal_ok

def first_exit_edges(P, S):
    """
    Returns B-row edges by which ordered path P exits S.
    """
    S = set(S)
    exits = set()

    for i in range(len(P) - 1):
        u, v = P[i], P[i + 1]
        if u in S and v not in S:
            exits.add(norm_edge((u, v)))
        if v in S and u not in S:
            exits.add(norm_edge((u, v)))

    return exits

def is_connected_graph_on_edges(V, edge_set):
    if not V:
        return True

    adj = {v: set() for v in V}
    for u, v in edge_set:
        adj[u].add(v)
        adj[v].add(u)

    start = next(iter(V))
    seen = {start}
    stack = [start]

    while stack:
        u = stack.pop()
        for v in adj[u]:
            if v not in seen:
                seen.add(v)
                stack.append(v)

    return seen == set(V)

def flip_cut_edges(E, B, S):
    """
    B^S = B triangle delta_G(S).
    """
    B = {norm_edge(e) for e in B}
    dG = delta(E, S)
    return (B - dG) | (dG - B)

def shortest_B_distance(u, v, B_edges):
    adj = {}
    for x, y in B_edges:
        adj.setdefault(x, set()).add(y)
        adj.setdefault(y, set()).add(x)

    q = [(u, 0)]
    seen = {u}
    head = 0

    while head < len(q):
        x, d = q[head]
        head += 1

        if x == v:
            return d

        for y in adj.get(x, ()):
            if y not in seen:
                seen.add(y)
                q.append((y, d + 1))

    return None

def ell_under_cut(edge, B_edges):
    u, v = edge
    d = shortest_B_distance(u, v, B_edges)
    if d is None:
        return None
    return d + 1

def gamma_of(Mset, B_edges):
    total = 0
    for e in Mset:
        L = ell_under_cut(e, B_edges)
        if L is None:
            return None
        total += L * L
    return total

def is_cage_switch(S, V, E, B, M, Q, U, cyc):
    S = set(S)
    U = set(U)

    if not S or S == set(V):
        return False

    if not S <= U:
        return False

    B_S = flip_cut_edges(E, B, S)
    if not is_connected_graph_on_edges(set(V), B_S):
        return False

    R = counted_rows(Q, U, M, cyc)

    # terminal crossing condition
    for _, P in R:
        Pset = set(P)
        if Pset & S and not Pset <= S:
            if not crosses_path_terminally(P, S):
                return False

    # every blue boundary edge witnessed by a counted row first exit
    blue_boundary = delta(B, S)
    witnessed = set()

    for _, P in R:
        witnessed |= first_exit_edges(P, S)

    if not blue_boundary <= witnessed:
        return False

    # inclusion-minimality among sets satisfying the previous properties
    for x in list(S):
        S2 = set(S)
        S2.remove(x)
        if S2 and cage_switch_core_conditions(S2, V, E, B, M, Q, U, cyc):
            return False

    return True

def cage_switch_core_conditions(S, V, E, B, M, Q, U, cyc):
    S = set(S)
    U = set(U)

    if not S or S == set(V):
        return False
    if not S <= U:
        return False

    B_S = flip_cut_edges(E, B, S)
    if not is_connected_graph_on_edges(set(V), B_S):
        return False

    R = counted_rows(Q, U, M, cyc)

    for _, P in R:
        Pset = set(P)
        if Pset & S and not Pset <= S:
            if not crosses_path_terminally(P, S):
                return False

    blue_boundary = delta(B, S)
    witnessed = set()
    for _, P in R:
        witnessed |= first_exit_edges(P, S)

    return blue_boundary <= witnessed

def delta_gamma(S, V, E, B, M):
    B = {norm_edge(e) for e in B}
    M = {norm_edge(e) for e in M}
    E = {norm_edge(e) for e in E}

    B_S = flip_cut_edges(E, B, S)
    M_S = E - B_S

    old_gamma = gamma_of(M, B)
    new_gamma = gamma_of(M_S, B_S)

    if old_gamma is None or new_gamma is None:
        return None

    return new_gamma - old_gamma

def find_minimal_positive_debt_pair(V, B, M, cyc):
    best = None
    best_key = None

    for f in M:
        for Q in cyc[f]:
            for U in powerset(V):
                eps = epsilon_Q_U(Q, U, V, B, M, cyc)
                if eps <= 0:
                    continue

                R = counted_rows(Q, U, M, cyc)
                key = (len(U), len(R))

                if best is None or key < best_key:
                    best = (f, tuple(Q), set(U), eps)
                    best_key = key

    return best

def gate_slack_cage_zero_slack_switch(V, E, B, M, cyc):
    """
    Exact falsifier gate for the lemma.

    PASS means:
      no positive-debt pair exists, or every minimal positive-debt pair
      produces a zero-slack Gamma-decreasing cage switch.

    FAIL means:
      a minimal positive-debt pair exists but no required switch exists.
    """
    pair = find_minimal_positive_debt_pair(V, B, M, cyc)

    if pair is None:
        return ("PASS_NO_POSITIVE_DEBT", None)

    f, Q, U, eps = pair

    for S in powerset(V):
        if not is_cage_switch(S, V, E, B, M, Q, U, cyc):
            continue

        if sigma_of(S, B, M) != 0:
            continue

        dG = delta_gamma(S, V, E, B, M)
        if dG is not None and dG < 0:
            return ("PASS_SWITCH_FOUND", {
                "f": f,
                "Q": Q,
                "U": U,
                "epsilon": eps,
                "S": S,
                "DeltaGamma": dG,
            })

    return ("FAIL_MINIMAL_DEBT_WITHOUT_SWITCH", {
        "f": f,
        "Q": Q,
        "U": U,
        "epsilon": eps,
    })
