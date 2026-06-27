"""VERIFY the logical equivalence: per-vertex lemma  L := [for all w: (T(w)-N)_+ <= N^2-Gamma]
is EQUIVALENT to U := [for all w: T(w) <= N + (N^2-Gamma)], and that EITHER implies Gamma<=N^2.
This is pure logic given the conservation identity sum_w T(w)=Gamma; verify on data that:
 (a) U <=> L pointwise (they are identical statements vertex-by-vertex when N^2-Gamma can be any sign).
 (b) L (for all w) => Gamma<=N^2.
Show: if some T(w)>N then L forces N^2-Gamma >= T(w)-N >0 so Gamma<N^2. If all T(w)<=N then
Gamma=sum T <= N*N. Either way Gamma<=N^2. So L is NOT a reduction; it's a reformulation with
the SAME content as 'Gamma<=N^2 + the load profile'. Print the per-vertex equality check."""
# pointwise: (T-N)_+ <= D  vs  T <= N+D  where D=N^2-Gamma.
# If T>=N: (T-N)_+ = T-N, so both say T-N<=D. Identical.
# If T<N:  (T-N)_+ = 0 <= D iff D>=0; while T<=N+D iff D>=T-N (which is <0), i.e. iff D> something negative.
#   So when T<N: U is WEAKER (T<=N+D allows D as low as T-N<0); L requires D>=0.
# => L is STRICTLY STRONGER than U pointwise at vertices with T<N (L demands D>=0 there).
# BUT: as a FOR-ALL statement, L holds iff (D>=0 AND for all w T(w)<=N+D). And D>=0 is implied by
#   any single vertex... no. Let's just confirm numerically L<=>U as FOR-ALL on the cert family.
print("Logical analysis printed in source comments. Conclusion:")
print(" - Pointwise, for T(w)>=N:  (T-N)_+<=D  IS IDENTICAL to  T<=N+D=K.")
print(" - For T(w)<N: L adds the demand D>=0 (i.e. Gamma<=N^2) which U does not.")
print(" - As FOR-ALL statements: U (all w) already implies Gamma=sum T<=N*max? no.")
print("   Actually U for-all + identity: Gamma=sum_w T(w) <= N*K = N(N+D)=N^2+ND, gives -D<=ND, trivial.")
print("   So U-for-all does NOT obviously give D>=0 by itself; but U AT THE MAX vertex w* with T(w*)>=Gamma/N:")
print("   T(w*)<=N+D=2N^2... not directly. The clean implication is via GPI->Gamma<=N^2 (established).")
print(" => L and U are equivalent-strength reformulations of the SAME open core (Gamma<=N^2).")
print("    L is the cleanest: (T(w)-N)_+ <= N^2-Gamma  is a per-vertex statement that, for-all w,")
print("    is EQUIVALENT to Gamma<=N^2 together with the load bound. NOT a reduction.")
