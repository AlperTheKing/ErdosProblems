# R29 restricted selector-invariance lemma

## Definitions

Let `H={0,1,2}` and let `Omega` be the product of the 676 canonical R29
selector families, each containing its 680 shortest rows.  For `omega in
Omega`, let `D_omega(A)` be the current ActiveScoped CollisionHalf plus HitNeed
demand on `A subseteq H`.  Let `N^R_omega(A)` be the set of distinct ordered
FreeHalf triples `(x,y,h)`, `h in {0,1}`, reachable from `A` by exactly the
current sameFirst/sameOwner and rowCompanion rules, after the active-edge
`h=0` reservations.  Source claims are set-unioned over owners and reasons.

## Theorem

For every `omega in Omega`, the owner demand vector and complete source-mask
histogram are

```text
(D_omega({0}),D_omega({1}),D_omega({2})) = (6651,6651,6651),
#{s : ownerMask(s)=1} = #{s : ownerMask(s)=2} = #{s : ownerMask(s)=4} = 5775,
#{s : ownerMask(s)=7} = 2600,
all other source-mask classes are empty.
```

Consequently all eight shore values are selector-invariant.  In particular,

```text
D_omega(H) = 19953,
|N^R_omega(H)| = 17325 + 2600 = 19925,
D_omega(H) - |N^R_omega(H)| = 28.
```

This is a projection invariant.  The selected union, the whole active
component, outside attachments, and the FullBank source ledger are not
selector-invariant.

## Structural proof

1. Independent BFS enumeration gives 680 rows in each of 676 selector
   families, partitioned as 676 anchor and 4 local rows.  All 459680 local
   options avoid the traffic set `C={0,...,54}`, hence avoid every hub and
   every hub companion.  Their possible row supports comprise 5408 blue
   edges and contain no hub-incident edge.

2. The 676 rigid traffic rows are `(u,1,0,2,v)` for 26 left leaves `u` and 26
   right leaves `v`.  Thus each hub has row load 676 and companion set exactly
   `C`.  Its pair multiplicities are 676 against each of the three hubs
   (including itself), 26 against each of 52 leaves, and zero elsewhere.
   Therefore

   ```text
   CollisionHalf(h) = 2*(3*(676-1)+52*(26-1)) = 6650.
   ```

3. Delete every edge that any selector option can support and retain only
   fixed-row selected vertices.  The remaining 18 guaranteed active edges
   put all three hubs in a 19-vertex component containing bad edge
   `(2762,2766)`.  Hub 0 reaches its endpoints along the fixed paths

   ```text
   0-55-2764-2781-2772-2763-2780-2771-2762,
   0-55-2764-2773-2782-2765-2774-2783-2766.
   ```

   Every tuple deletes only a subset of the 5408 possible selector-support
   edges.  The only active incident edge is `(0,55)`, `(1,2929)`, or
   `(2,2930)`, respectively.  Hence demanded active degree is one and

   ```text
   HitNeed(h) = max(0,1-max(0,2943-5*676)) = 1.
   ```

4. For sameFirst/sameOwner, each owner has `2943-55=2888` free second
   coordinates and two halves.  Exactly its fixed active cable half is
   reserved, giving `2*2888-1=5775` sources per owner and 17325 total.

5. Within `C`, zero-co-occurrence ordered pairs are exactly distinct leaves
   on the same side: `2*26*25=1300`.  Each leaf has signed degree one, so the
   pair switch has signed degree two and passes the nonnegative-loss test.
   Neither half is reserved, giving `2*1300=2600` rowCompanion sources.  They
   are shared by all three owners and are disjoint from sameFirst sources.

## Smallest extension falsifier

Let `omega_A` be all-anchor.  Replace only selector family 0's row

```text
(735,55,59,56,2760)
```

by the local row

```text
(735,732,59,56,2760)
```

to obtain `omega_L`.  Under the R23 outsideAttachment rule,

```text
|OutsideHalf_omega_A(H)| = 912600,
|OutsideHalf_omega_L(H)| = 909900.
```

Thus Hamming distance one is already a falsifier to extending `19925`
invariance to the real outsideAttachment/c5Base relation.  At `omega_A`, the
ordered pair `(732,734)` is Free and both outside components attach to traffic
leaf 16, a companion of every hub.

The same replacement changes the hub active component from 19 to 73 vertices,
its blue boundary from 1441 to 1469 edges, and anchor row load from 677 to 676.
It removes support edges `(55,59),(55,735)` and adds
`(59,732),(732,735)`.  These are exact breaking channels for real Door,
vertexSlack, and prune predicates.

## Predicate boundary

| Predicate or kind | R29 hub-shore verdict |
|---|---|
| sameFirst/sameOwner | Invariant; 17325 total. |
| commonBad | Invariant empty pool: hubs 0,1,2 have no bad neighbours. |
| rowCompanion | Invariant; 2600 shared sources. |
| outsideAttachment | Not invariant; exact one-row change is 912600 to 909900. |
| Door | Not covered: active component/boundary inputs change 19/1441 to 73/1469. |
| vertexSlack | Not covered: active domain and row-load inputs change. |
| c5Base | Not invariant when realized by outsideAttachment; change is 2700 half-sources. |
| prune | Not covered: selected row and four support-edge inputs change explicitly. |

## Replay

From the repository root:

```powershell
python tmp\fanout\r29_fullbank\D_invariance\verify_selector_invariance.py
python tmp\fanout\r29_fullbank\D_invariance\verify_outside_attachment_breaker.py
```

Both scripts use integer arithmetic only.
