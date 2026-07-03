# BANK0 writeup section (GPT-Pro sibling thread 6a45e152, 2026-07-04; extracted via
# offset-stitched slices, reverse-transformed; verbatim up to whitespace normalization
# at seam joins; one 50-char span reconstructed from context, marked [*]).

BANK0. The all-length-five base inequality

The purpose of this section is to replace the empty-mask coefficient comparison by a structural base inequality.

Bank0. Let G be triangle-free. Let B be a connected maximum cut, chosen Gamma-minimal among connected maximum cuts, and let M be the set of bad edges, m = |M|. Suppose every bad edge has shortest odd-cycle length 5, equivalently every shortest B-geodesic closing a bad edge has four B-edges and hence gives a length-five row. Then

    N^2 - 25m >= 0.

This proves eta >= 0 in the only Branch-A case where eta is not already supplied by a longer row. Indeed, Bank-L gives eta >= (L^2-25)/25 whenever a positive row of length L>5 exists. Thus the pure all-length-five case is the sole case requiring Bank0. Together with the six proper-mask A1 cones and the full-mask ODL certificate, Bank0 supplies the missing nonnegativity needed for C5-RS.

The inequality is tight on balanced blowups of C5. If G = C5[t], then N = 5t, m = t^2, and N^2-25m = 0.

The proof is by contradiction. Fix an N-minimal counterexample to Bank0: G is triangle-free, B is connected, maximum and Gamma-minimal, every bad edge has length 5, and 25m>N^2. All packet, corridor, and completion certificates below are interpreted inside this fixed counterexample.

Lemma 1. Mass identity and pressure. [PROVEN]

For each bad edge f, let R_f be the set of shortest B-geodesics joining the endpoints of f. Since all bad edges have length 5, each row P in R_f has exactly five vertices. Define

    p_f(v) = |{P in R_f : v in P}| / |R_f|,

and define the global length-five load

    s(v) = sum_{f in M} p_f(v).

Then

    sum_{v in V} s(v) = 5m.

Proof. For a fixed bad edge f,

    sum_v p_f(v) = 5,

because every row in R_f has five vertices. Therefore

    sum_v s(v)
   = sum_v sum_f p_f(v)
   = sum_f sum_v p_f(v)
   = 5m.

Define the Bank0 pressure of a set U by

    Pi(U) = 5 sum_{u in U} s(u) - N |U|,

and equivalently define

    nu_0(U) = N |U| - 5 sum_{u in U} s(u) = -Pi(U).

Then

    Pi(V) = 25m - N^2 > 0,

because the counterexample has 25m>N^2. Thus V has positive pressure.

Only the all-length-five hypothesis is used in the identity. The counterexample assumption is used only to obtain Pi(V)>0.

Lemma 2. Minimal closed positive packet. [CERTIFICATE: CLOSURE-TRACE]

There exists a nonempty closed packet U with

    Pi(U) > 0,

minimal under inclusion among closed packets. Consequently every nonempty proper closed subpacket U' of U satisfies

    Pi(U') <= 0,

or equivalently

    nu_0(U') >= 0.

The closure is the least closure under the following four rules.

C1. Row-interval closure. If a certified length-five row P = (p0,p1,p2,p3,p4) has two vertices in the packet, then the row interval between them is added.

C2. Fixed door, orientation, and first-exit closure. Fix a bad edge f, an oriented terminal endpoint tau of f, and a first-exit blue door e. If a shortest f-row, oriented from tau, has its tau-terminal prefix inside the packet and first exits through e, then every shortest f-row with the same oriented terminal tau and the same first-exit door e contributes the corresponding terminal prefix. This rule is stated with the door and orientation fixed; it is not an unrestricted row-family closure.

C3. Blue-detour closure. If a row edge xy inside the packet has a certified row-deleted blue detour D from x to y, then the internal vertices of D are added. The detour certificate records that D lies in the blue graph with the row edge xy deleted.

C4. Terminal-shadow completion. If a terminal shadow inside the packet exits through its first blue door, then the completed terminal-shadow cell determined by that first exit is added.

The closure-trace verifier emits a finite trace of C1-C4 steps and checks that the final packet is closed. Since Pi(V)>0, at least one closed positive packet exists, namely V. Minimality is taken among the closed positive packets.

Closure minimality is used later through the implication that no proper closed subpacket has positive pressure. Gamma-minimality is not used in this lemma except insofar as it supplies the certified shortest rows and first-exit data.

Lemma 3. Owned-core corridor partition. [CERTIFICATE: OWNED-CORRIDOR PARTITION]

Let U be the minimal closed positive packet of Lemma 2. The terminal-shadow and blue-detour closure data produce geometric corridors

    Chat_1, ..., Chat_r.

These geometric supports are allowed to overlap only at certified articulation vertices of one of the following types:

    SH0  terminal root;
    SH1  first-exit door endpoint;
    SH2  row split or row rejoin vertex;
    SH3  blue-detour endpoint;
    SH4  osculation vertex.

For every v in U, let Claim(v) be the set of geometric corridors containing v. The verifier checks Claim(v) is nonempty. A fixed canonical order on corridors is chosen, and the owner of v is

    own(v) = min Claim(v).

Define the owned core of corridor c by

    V_c = {v in U : own(v) = c}.

Then

    U = disjoint union_c V_c,

and the exact pressure decomposition is

    nu_0(U) = sum_c nu_0(c),

where

    nu_0(c) = N |V_c| - 5 sum_{v in V_c} s(v).

Equivalently, in row-atom coordinates s(v) = sum_J y_J 1_{v in J},

    nu_0(c) = N |V_c| - 5 sum_J y_J |J cap V_c|.

The verifier obligations are:

    CLAIM_NONEMPTY: every v in U is contained in at least one geometric corridor;
    OWN_IN_GEOM: V_c subset Chat_c for every c;
    OWN_PARTITION: the V_c are pairwise disjoint and have union U;
    SHARED_TYPE: every multiply claimed vertex is of type SH0-SH4;
    LOAD_ACCOUNT: nu_0(U) = sum_c nu_0(c).

Since U has Pi(U)>0, one has nu_0(U)<0. Hence at least one owned corridor c satisfies

    nu_0(c)<0.

All corridor crossing and labeling certificates may use the geometric support Chat_c, but the numerical deficit is computed on the owned core V_c. This prevents double counting of shared terminals, doors, detour endpoints, and osculation vertices.

Lemma 4. CrossCap capacity certificate. [CERTIFICATE: CROSSCAP / T=2 CORRIDOR ENGINE]

Let c be an owned corridor with

    nu_0(c)<0.

If the geometric corridor Chat_c contains a crossing terminal-shadow lens, then there is a completed switch S such that

    N sigma(S) <= nu_0(c) < 0,

where

    sigma(S) = delta_B(S)-delta_M(S).

This contradicts maximality of the cut, because every switch in a maximum cut satisfies sigma(S) >= 0.

The CrossCap certificate consists of:

    a crossing pair of terminal shadows;
    the primitive lens L between them;
    the completed switch S = Comp(L);
    a blue-capacity map from the blue boundary of S to the corridor capacity side;
    a row-demand cover map from the row atoms in the owned corridor core to the bad crossings of S;
    the residual decomposition.

The verified integer identity has the form

    N sigma(S) <= nu_0(c) + residual(c),

where residual(c) <= 0 after summing the signed residual pieces emitted by the certificate. Equivalently, the verifier checks the displayed inequality N sigma(S) <= nu_0(c) directly after LCM clearing.

If a corridor has a boundary-sharing ambiguity not discharged by the direct CrossCap map, the verifier uses the fallback variable a_C. The fallback decomposition splits the residual into a principal CrossCap term plus a_C, and the certificate supplies either

    a_C <= 0,

or a local switch completion whose nonnegative sigma eliminates a_C. This is the CrossCap fallback mode accepted by the T=2 corridor engine.

Max-cut is used only at the final contradiction sigma(S) >= 0. Gamma-minimality and all-length-five enter in the legality of the completed terminal-shadow switch and the certified shortest-row shadows. Triangle-freeness enters in the first-split/last-rejoin and osculation exclusions used by the completion verifier.

Lemma 5. Noncrossing LABEL certificate. [CERTIFICATE: PRIMITIVE-LENS VOLTAGE]

Let c be an owned corridor with nu_0(c)<0 and suppose no CrossCap crossing certificate applies. If all primitive-lens gates listed below pass and no head-on osculation residual remains, then the geometric corridor Chat_c has a well-defined label

    lambda_c : Chat_c -> Z/5Z

such that every row segment, bad-edge closure, terminal shadow, and certified blue detour in Chat_c has the prescribed C5 voltage. In particular every graph edge in the labelled corridor joins adjacent C5-classes.

The following elementary fact is used throughout.

Lemma A. Five-sign row monotonicity. [PROVEN]

Let lambda:V(G)->Z/5Z be any graph homomorphism to C5, meaning every graph edge changes the label by +1 or -1. Let P = (p0,p1,p2,p3,p4) be a length-five row, with four blue row edges p_i p_{i+1} and the bad closing edge p4 p0. For i = 0,...,3 set

    eps_i = lambda(p_{i+1}) - lambda(p_i) in {+1,-1},

and set

    eps_4 = lambda(p0) - lambda(p4) in {+1,-1}.

Around the closed five-edge row cycle,

    eps_0 + eps_1 + eps_2 + eps_3 + eps_4 = 0 mod 5.

The integer sum of five signs is one of -5,-3,-1,1,3,5. The only values congruent to 0 mod 5 are +/-5. Thus all five signs are equal. Therefore the row is class-monotone, up to reflection:

    lambda(p_j) = lambda(p0) + j eps_0  mod 5.

No shortestness is required beyond the fact that the row is a five-edge closed cycle.

The voltage lemma is proved by primitive-lens reduction. Build the voltage graph of the corridor. Row intervals carry their row-index voltage. A bad closing edge carries voltage +1 in the oriented row cycle. A terminal shadow carries the voltage inherited from its row interval. A D-certified blue detour carries the voltage supplied by its detour label certificate.

If a closed voltage walk has nonzero total voltage, choose one with minimal support and then with the fewest strand changes. Splitting at repeated vertices gives a smaller nonzero closed walk, so the walk contains a primitive nonzero lens: two internally disjoint corridor chains with the same endpoints but different total voltage. The primitive lens is one of the following finite types.

    RR        row interval versus row interval;
    RB        row interval versus bad closure;
    RD        row interval versus blue detour;
    DD        blue detour versus blue detour;
    TT-same   same-root terminal shadow versus terminal shadow;
    TT-opp    opposite-root terminal shadow versus terminal shadow;
    TR        terminal shadow versus row segment;
    TD        terminal shadow versus blue detour;
    BAD       bad closure versus an alternative path;
    OSC       osculation.

The verifier outcomes are:

    RR: zero voltage, shorter-row contradiction, triangle, or theta crossing;
    RB: row-cycle zero, shorter bad geodesic, or theta crossing;
    RD: compatible D-label, crossing, shorter row, or triangle;
    DD: reduction to RD or theta crossing;
    TT-same: nested zero, disjoint, or Type-I crossing;
    TT-opp: common transfer zero, Type-I crossing, Type-II crossing, or OSC;
    TR: same-row zero or first-split/last-rejoin theta crossing;
    TD: D-label reduction to TR, crossing, shorter row, triangle, or OSC;
    BAD: row-cycle zero, shorter bad geodesic, theta crossing, or OSC.

The osculation cases are:

    OSC0  same-direction shared edge, merged;
    OSC1  opposite-direction shared first-exit edge, true head-on residual;
    OSC2  vertex-only nonalternating touch, split;
    OSC3  vertex-only alternating touch, crossing;
    OSC4  triple touch.

For OSC4, the laminar triple-touch case splits into pairwise OSC2 cases, the alternating triple-touch case is crossing, and the head-on triple-touch case is the only true OSC4 residual. Thus the only true residual gates are OSC1 and OSC4-head-on.

All nonzero primitive lenses are therefore eliminated by either CrossCap, shorter-row impossibility, triangle-freeness, compatible detour voltage, or the explicit OSC residual gate. Hence every closed walk in the corridor voltage graph has total voltage zero. A label is obtained by fixing one root label and defining the label of any vertex as the voltage of a path from the root. Closed-walk zero gives path independence.

The RR, RB, TT, TR, and Type-I/Type-II crossing cases are identical to the T=1/T=2 terminal-shadow corridor engine. The RD, DD, TD, BAD, and OSC4 cases are the additional Bank0 blue-detour cases.

Lemma 6. Extension of a labelled packet. [PROVEN MODULO CERTIFICATE: BH2/BH3 BLUE-HANDLE GATES]

Let U be the minimal closed positive packet of Lemma 2. Suppose a negative owned corridor of U is in the LABEL branch of Lemma 5 and all CrossCap and OSC residuals are discharged. Suppose further that the BH2 and BH3 blue-handle gates below are discharged. Then

    U = V.

Proof. Assume U is not all of V. Since B is connected, some connected component Y of B[V\U] has a blue edge to U.

First suppose Y contains a row-visible vertex y, meaning s(y)>0. Then y lies on a certified length-five row. By C1 row-interval closure, C2 fixed-door row-family closure, or C4 terminal-shadow completion, the row-visible part of Y is absorbed into U unless it creates a crossing or OSC residual. The LABEL branch has no unresolved CrossCap or OSC residual, so this is impossible.

Thus every vertex of Y is row-invisible:

    s(y) = 0 for all y in Y.

A row-invisible vertex is incident to no bad edge. Indeed, every endpoint of a bad edge lies on every shortest row closing that bad edge and therefore has positive load. Since all bad edges have length 5, any bad edge incident to y would make y row-visible. Hence Y is blue-only:

    E_M(Y,V) = empty.

If Y attaches to V\Y through a single vertex t, then delete Y\{t}. This is the blue-pendant peel. No bad edge is deleted, every length-five bad-edge witness survives, m is unchanged, N strictly decreases, B-connectedness survives through t, and the inequality 25m>N^2 remains true for the smaller graph. This contradicts N-minimality of the counterexample. This is the only peel used in the proof.

Therefore Y is multi-attached. Choose two attachment vertices a,b in U and a shortest blue path through Y,

    D = a = y0, y1, ..., yL = b,

with y1,...,y_{L-1} in Y. This is a blue detour between U-vertices.

Let

    Delta = lambda(b)-lambda(a) in Z/5Z.

A blue path of length L can be labelled compatibly exactly when Delta belongs to

    W_L = {L-2r mod 5 : 0 <= r <= L}.

The finite table is

    W_2 = {0, +/-2};
    W_3 = {+/-1, +/-2};
    W_L = Z/5Z for L >= 4.

If the detour is compatible, C3 absorbs its internal vertices and extends the label, contradicting closure. If it is incompatible, then either L = 2 and Delta = +/-1, or L = 3 and Delta = 0. These are precisely the BH2 and BH3 residual gates.

The BH2 gate records a length-two blue handle

    a-y-b,

with y outside U, s(y) = 0, ay and by blue, and lambda(b)-lambda(a) = +/-1. Triangle-freeness only implies a and b are nonadjacent; max-cut alone does not forbid the pattern. The certificate must supply one of:

    BH2_CROSS, a completed switch S with N sigma(S) <= nu_0(c)<0;
    BH2_OSC, a discharged head-on osculation;
    BH2_FORBID, a local impossibility certificate.

The BH3 gate records a length-three blue handle

    a-y1-y2-b,

with y1,y2 outside U, row-invisible, all three edges blue, and lambda(a) = lambda(b). The certificate must similarly supply BH3_CROSS, BH3_OSC, or BH3_FORBID.

Once BH2 and BH3 are discharged, no outside blue component Y can exist. Since B is connected, U = V.

The proof uses B-connectedness to find Y, all-length-five to show row-invisible vertices are bad-edge-free, closure minimality through C1-C4, triangle-freeness only in the local BH2 nonadjacency check, max-cut only through the CrossCap alternatives, and N-minimality only in the blue-pendant peel.

Lemma 7. Template-cut inequalities from a global C5-label. [PROVEN AND FORMALIZED]

Assume the LABEL branch extends to all vertices, so there is a graph homomorphism

    lambda:V(G)->Z/5Z

to C5. Let

    V_i = lambda^{-1}(i),     n_i = |V_i|,

and let e_i be the number of graph edges between V_i and V_{i+1}, indices modulo 5. Since lambda is a C5-homomorphism, all graph edges lie between adjacent classes, so the total edge set is the disjoint union of the five class-edge sets counted by e_i.

For each i, compare the maximum cut B with the C5-template cut that makes only the class-edge V_i -- V_{i+1} monochromatic. In that template cut, the bad edges are exactly the e_i edges between V_i and V_{i+1}. Since B is maximum and has m bad edges,

    m <= e_i

for every i.

Also,

    e_i <= n_i n_{i+1}

because there are at most n_i n_{i+1} edges between V_i and V_{i+1}.

Thus

    m <= e_i <= n_i n_{i+1}       for all i.

Only max-cut is used for m <= e_i. The C5-hom property is used to ensure the template cut has exactly e_i bad edges and no other bad edges. No gamma-minimality is used in this lemma.

Lemma 8. AM-GM finish. [PROVEN AND FORMALIZED]

Assume nonnegative numbers n_0,...,n_4 sum to N and satisfy

    m <= n_i n_{i+1}

for every cyclic i. Then

    m <= N^2/25.

Proof. From m <= n_i n_{i+1},

    sqrt(m) <= sqrt(n_i n_{i+1}).

By the two-variable AM-GM inequality,

    sqrt(n_i n_{i+1}) <= (n_i + n_{i+1})/2.

Therefore

    sqrt(m) <= (n_i + n_{i+1})/2

for every i. Summing over the five cyclic pairs gives

    5 sqrt(m) <= (1/2) sum_i (n_i + n_{i+1}) = N.

Hence

    sqrt(m) <= N/5,

and so

    m <= N^2/25.

Equality requires equality in every two-variable AM-GM step and every template-cut inequality, hence n_0 = ... = n_4 = N/5 and m = n_i n_{i+1}. Thus the balanced C5 blowups are the tight examples.

Completion of Bank0.

Assume a minimal counterexample. Lemma 1 gives Pi(V)>0. Lemma 2 gives a minimal closed positive packet U. Lemma 3 partitions U into owned corridor cores, and because nu_0(U)<0, some owned corridor c has nu_0(c)<0. If c crosses, Lemma 4 gives a completed switch S with N sigma(S)<0, contradicting max-cut. If c is noncrossing and non-head-on, Lemma 5 gives a C5-label on its geometric support. Lemma 6 extends the LABEL branch to U = V, after discharging BH2/BH3 and the OSC residuals. Therefore the whole graph has a C5-homomorphism. Lemma 7 gives m <= e_i <= n_i n_{i+1} for every i, and Lemma 8 gives m <= N^2/25. This contradicts 25m>N^2.

Hence every B-connected Gamma-minimal maximum cut of a triangle-free graph with all bad edges of length 5 satisfies

    N^2 - 25m >= 0.

This proves Bank0.

Certificate ledger.

Certificate name Consumer lemma Verifier/status
CLOSURE-TRACE Lemma 2 Checks C1-C4 closure steps; certificate gate
OWNED-CORRIDOR PARTITION Lemma 3 Checks CLAIM_NONEMPTY, OWN_IN_GEOM, OWN_PARTITION, SHARED_TYPE, LOAD_ACCOUNT; certificate gate
CROSSCAP Lemma 4 Integer-flow switch certificate; accepted T=2 mode
a_C FALLBACK Lemma 4 Residual decomposition fallback for CrossCap; certificate gate
PRIMITIVE-LENS VOLTAGE Lemma 5 RR/RB/RD/DD/TT/TR/TD/BAD/OSC case verifier; shared with NCH-Hall
OSC1 Lemma 5 Head-on first-exit osculation residual; local gate
OSC4-HEAD-ON Lemma 5 Triple-touch head-on residual; local gate
BLUE-PENDANT PEEL Lemma 6 Proven from N-minimality, row-invisibility, blue-only appendage, single attachment
BH2 BLUE-HANDLE Lemma 6 Length-two incompatible handle; residual gate
BH3 BLUE-HANDLE Lemma 6 Length-three incompatible handle; residual gate
TEMPLATE-CUT CHECK Lemma 7 Formalized Lean theorem: max-cut comparison with five C5-template cuts
AMGM-FINISH Lemma 8 Formalized Lean theorem: two-variable cyclic AM-GM
COVER-EXTRACTION Lemma 8 / final Algebra formalized; cover-extraction gate remains where quotient cover data are emitted

Validation note. The global Bank0 statement has been census-validated with zero failures through N = 11 among pure length-five Gamma-minimal connected maximum cuts, and it is tight on balanced C5 blowups C5[t]. The local per-comp[onent support inequality is fal][*]se and is not used; the proof uses owned-core corridor accounting plus global extension to the C5-template cut inequalities.
