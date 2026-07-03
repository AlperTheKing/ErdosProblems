# Bank-L Pressure-Cover Refined Target (Codex)

Status: exact finite evidence only; not a theorem yet.

Source artifacts:

- `tmp/bankl_lcb_certs_n11_v2.jsonl`
- `tmp/bankl_pq_positive_rows_v2.jsonl`
- `tmp/bankl_pq_nonuniform_residue_profile.json`
- `tmp/bankl_pq_attachment_profile.json`
- `tmp/bankl_clean_damage_failures.json`
- `tmp/bankl_clean_damage_failure_profile.json`
- `tmp/bankl_pc_refined_taxonomy_v1.json`

## Pressure Identity

For an L > 5 row Q, let W = V(Q), r = N - L, and define bare packet data

- p = e_M(W)
- h = |delta_M(W)|
- d = |delta_B(W)|

Then

P_Q = 25(p - 1) + 25(d + h)/2 - 2Lr,

rho_Q = 25(eta - B(W)),

and the exact identity is

-Delta_Q = rho_Q - P_Q.

Rows with P_Q <= 0 are free by packet exchange. The hard theorem is rho_Q >= P_Q^+.

## Verified N <= 11 Taxonomy

From the v2 JSONL artifact:

- free_packet_Pneg: 3688 rows
- tight_Pzero: 34 rows
- clean_damage_branch: 9731 rows
- clean_nuK_escape: 7 rows
- residue_detour: 112 rows
- residue_nuK: 675 rows

Total: 14247 rows.

The 10525 positive-pressure rows consist of:

- 9738 clean rows with p=1,h=0
- 787 nonclean residue rows

The residue rows are all L=7,r=4,m=2, with either p=1,h=1 or p=2,h=0.

## Rejected Lemma

The pure damage lemma is false:

min optimal off-row recoloring damage <= floor(2Lr/25)

fails on 7 clean rows. All failures have

N=11, L=7, r=4, m=2, p=1, h=0, d=6, P_Q=19, rho_Q=66.

The off-row blue graph is two disjoint edges, the off-row bad graph is one edge, beta_R=0, and min damage is 3 while floor(2Lr/25)=2.

## Refined Proof Target

Prove the following branch statement for every L > 5 row Q.

1. Packet-free branch.
   If P_Q <= 0, packet exchange gives rho_Q >= P_Q.

2. Clean damage branch.
   Assume P_Q > 0 and p=1,h=0. If there is an off-row recoloring preserving at most beta_R bad off-row edges and damaging at most floor(2Lr/25) row-boundary blue edges, then

   m - 1 <= beta_R + damage <= r^2/25 + 2Lr/25,

   hence Bank-L / pressure-cover follows.

   This branch covers 9731 of 9738 clean positive rows in the N<=11 artifact.

3. Clean nuK escape branch.
   If the clean damage branch fails, prove existence of a canonical completed terminal switch S with nuK(S) sufficient to pay -Delta_Q in the exact identity certificate.

   In the N<=11 artifact, the only failures are 7 dense m=2 rows; each has a single terminal nuK term:

   target -Delta_Q = 47,
   nuK(S) = 98,
   coefficient = 47/98.

4. Nonclean residue branch.
   If P_Q > 0 but (p,h) != (1,0), prove the existing detour/nuK dichotomy. In N<=11, all such rows are L=7,r=4,m=2; 112 are detour-certified and 675 are nuK-certified.

## Desired Structural Lemma

The final Pressure-Cover theorem should be stated as:

Every positive-pressure row is either packet-free, damage-covered, detour-covered, or terminal-nuK-covered, with an exact nonnegative identity proving -Delta_Q >= 0.

The important correction is that damage-covered alone is false. The dense two-bad-edge pattern forces a terminal-switch escape term.
