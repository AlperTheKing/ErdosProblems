# GPT Pro: CD-PRESERVATION proof — TERMINAL minimum-exposure geodesic + prefix-transport (chat 6a3e68cf)

GPT Pro (Comprehensive). Drove browser myself. Answer to "prove CD-preservation (i) for a shortest geodesic".

## HEADLINE CORRECTION
"Every shortest bad geodesic preserves CD" is TOO STRONG. Repair: choose a TERMINAL / MINIMUM-EXPOSURE
shortest geodesic (no successor), not an arbitrary one. Structural route:
   UNSAFE peel  ==>  a SUCCESSOR geodesic of same-or-shorter length.
Choose a shortest bad geodesic with NO successor => that one is CD-preserving. On c5paths20 this identifies
the END C5-atoms of the theta chain as the safe peels (NOT arbitrary internal theta C5's).

## 1. Obstruction algebra
Signed cut weight w(A)=delta_B(A)-delta_M(A); CD = w(A)>=0 for all A. C={v_0..v_r}, r even, v_0v_r in M,
path edges v_i v_{i+1} in B. R=V\C. CD-after-deletion: w_R(S)=delta_{B[R]}(S)-delta_{M[R]}(S)>=0 all S subset R.
Fail => exists S with w_R(S)=-eta<0 (residual improving flip). Signed attachment e^sigma(A,D)=e_B(A,D)-e_M(A,D).
 - CD on S:      0<=w(S)=w_R(S)+e^sigma(C,S)      => e^sigma(C,S)>=eta.
 - CD on S∪C:    0<=w(S∪C)=w_R(S)+e^sigma(C,R\S)  => e^sigma(C,R\S)>=eta.
Obstruction guarded BOTH sides by signed B-excess into C.

## 2. PREFIX-TRANSPORT (the key inequality)
Prefix P_i={v_0..v_i}, 0<=i<r. Signed boundary inside C is 0 (cuts one B-edge v_i v_{i+1} + the mono edge
v_0 v_r: 1-1=0). Apply CD to S∪P_i (w_R(S)=-eta):
   e^sigma(P_i,S) - e^sigma(P_i,R\S) <= w(S)     for every zero-prefix P_i.   [PREFIX-TRANSPORT]
Same for suffixes Q_i={v_i..v_r}. In a tight obstruction w(S)=0: every zero-prefix/suffix sees >= as much
signed attachment from R\S as from S. THIS REPLACES the global five-shell layering.

## 3. What shortestness buys (rigid local attachment geometry)
 A. No B-chords: v_i v_j in B, j-i>1 would give a shorter geodesic v_0..v_i v_j..v_r. None exist.
 B. Outside B-attachments span <=2: z notin C, z v_i, z v_j in B => |i-j|<=2 (else z shortcuts). Bipartite
    parity => only z v_i, z v_{i+2} in B.
 C. No adjacent mixed triangle: z v_i in B => z v_{i-1}, z v_{i+1} notin M (else triangle z,v_i,v_{i±1}).
 D. Bad-edge endpoints cannot share a B-neighbor: xy in M, x v_i, y v_i in B => triangle. So residual bad edge
    xy in M[R] crossing obstructing shore S has SEPARATED B-attachments. With C min bad length r+1 and
    x v_i, y v_j in B: d_B(x,y)<=|i-j|+2; since >=r => |i-j|>=r-2. For 5-geodesic (r=4): distance exactly 2
    along C = the C5-SUCCESSOR mechanism.

## 4. Shortestness essential but NOT sufficient alone (two CONCRETE checkable examples)
(a) NON-shortest path fails CD (N=11): X={0,1,2,3,4}, Y={5,6,7,8,9,10},
    B={(4,10),(3,7),(1,8),(0,9),(4,6),(2,9),(1,7),(3,6),(1,10),(0,5),(2,5),(4,7),(3,5),(2,8)}, M={(0,4),(7,9)}.
    Tri-free, B connected, CD holds. Bad edge (0,4) true shortest d_B=4 (e.g. 0-5-3-7-4). Induced LONGER even
    B-path 0-5-2-8-1-10-4 (len 6); delete it, remaining {3,6,7,9}, S={9}: delta_{B'}=0, delta_{M'}=1 (bad edge
    (7,9)) => CD FAILS. Pins role of shortestness.
(b) Even SHORTEST fails outside high-Gamma (N=8): X={0,1}, Y={2,3,4,5,6,7},
    B={(1,2),(0,4),(1,5),(0,6),(0,2),(1,7),(0,5),(1,3)}, M={(6,7),(3,4)}. Bad edge (6,7) shortest geodesic
    6-0-2-1-7 (C5); delete leaves {3,4,5}, bad edge (3,4), S={3} no supporting B-edge => CD FAILS. Gamma=50<64=N^2
    so does NOT threaten the lemma (Gamma<N^2), but shows proof cannot be "shortest => CD-preserving" alone.

## 5. Correct repair: TERMINAL minimum-exposure geodesic
Residual CD-defect D(C)=max_{S subset V\C}(delta_{M'}(S)-delta_{B'}(S))_+ ; D(C)=0 <=> CD-preservation.
CHOOSE a shortest bad geodesic minimizing D(C), terminal under the successor relation.
Successor: D(C)=eta>0, inclusion-minimal violating shore S; prefix/suffix ineqs => residual improvement
blocked by signed B-capacity on C; shortestness => brackets at distance r-2 => new C5-atom. Unsafe C produces
another shortest geodesic C' sharing a long subpath. 5-geodesic schematic: residual bad edge xy in M[R] with
x v_1 in B, y v_3 in B => C'=(x,v_1,v_2,v_3,y), xy in M, another shortest C5-geodesic.
REPAIR LEMMA to prove/test: D(C')<D(C), or lexicographically (D(C'),Lambda(C'))<(D(C),Lambda(C)) where
Lambda(C)=max_{S in W(C)} max_i (e^sigma(P_i,S)-e^sigma(P_i,R\S)), W(C)=shores attaining D(C). Finite descent;
terminal geodesic has D(C)=0.

## 6. Concrete first test on c5paths20
For every shortest 5-geodesic C compute D(C)=max_{S}(delta_{M'}(S)-delta_{B'}(S))_+. Terminal-successor lemma:
D(C)>0 => every inclusion-minimal violating shore S yields a successor C'=(x,v_1,v_2,v_3,y) [or reversed
(x,v_3,v_2,v_1,y)] with xy in M, x v_1, y v_3 in B, and (D(C'),Lambda(C'))<(D(C),Lambda(C)). Safe peels = the
terminal elements with D(C)=0. On chain (20,400)->(15,225)->(10,100)->(5,25): the END C5-atoms.

## THE ONE INEQUALITY to build the proof around
   e^sigma(P_i,S) - e^sigma(P_i,R\S) <= w(S)   for every zero-prefix P_i.   (replaces global five-shell layering)
