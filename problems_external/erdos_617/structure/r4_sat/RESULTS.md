# Prepared R4 exact lane

No R4 solver was launched while the aggregate worker cap was occupied.

The frozen base graph passed its existing exact verifier:

```
VERIFIED n=26 e=61 alpha=5 omega=5 degrees=4^15,5^4,6^7 six_sets_checked=230230
```

The complete permutation CNF generator reported:

```
R4_CNF_GENERATED vars=162604 clauses=705702 p=2704 a=158600 y=1300 permutation_alo=208 permutation_amo=67600 a_definition=475800 a_implies_y=158600 y_reverse=1300 fixed_copy_units=244 cross_copy_amo=1950 symmetry=copy0_identity_only
```

The independent semantic auditor reported:

```
R4_CNF_AUDIT_OK vars=162604 clauses=705702 p=2704 a=158600 y=1300 bidirectional_a=1 bidirectional_y=1 symmetry=copy0_identity_only
```

The raw packing checker rejected the adversarial all-identity fixture:

```
R4_PACKING_REJECTED edge overlap at 0,1
```

SHA-256:

```
generate_r4_packing_cnf.cpp 07E0A91B412A7045123C4F38B2262EFE865BFE2E1B125E9FBB4A52E82F4AD541
audit_r4_packing_cnf.cpp    A88C64AB6F7ACE70B412E9F55E55A66A0CE246AC75317E5BC05A918E3E9637FE
verify_r4_packing.cpp       B7C43A74A1528F6E8398C346617711AF3082F23FB04E09F66D7176D35CC84F44
decode_r4_model.cpp         FFED489D6D02BB5A720033E796B432C1D76B25AFC2FAC1D40F57D6A772B6A531
r4_packing.cnf              458540B6E543E955AC59ED35F793083D5DADD70FA3870915F9464C5AF3B3FB61
```

SAT semantics are exact in both directions. The first copy is fixed to the
identity by a proved host-relabeling normalization; no other symmetry
breaker is present.
