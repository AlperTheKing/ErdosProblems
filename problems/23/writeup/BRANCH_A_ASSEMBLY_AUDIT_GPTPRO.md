# Branch-A / GERSH_{L=5} FINAL CONDITIONAL ASSEMBLY AUDIT (GPT-Pro, 2026-07-03)

Target: GERSH_{L=5}: ROWSUM(Q) <= N + eta. Chain: A1 + ODL => C5-RS => net-DW' =>
GERSH_{L=5} (PROVEN conditional).

## Tree (status per node)
1. C5-RS layer: 1.1 statement PROVEN from 1.2-1.5; 1.2 P=empty PROVEN; 1.3 P proper:
   X(P) <= (25/N+2/3)etabar via A1, 2/3<=1 => beta_P <= 1 comes FROM A1 (no separate
   dichotomy) — CERT-PENDING through A1; 1.4 P=Z5 needs ODL.
2. A1: 2.1 statement CERT-PENDING; 2.2 six-cone reduction PROVEN (dihedral); 2.3 six
   ConeCerts CERT-PENDING (failure = local PMTS cone repair); 2.4 four-mask 7/30
   CERT-PENDING (absorption works for any beta_4 <= 3/10 — slack 7/30 -> 3/10).
3. ODL full-mask tree: 3.1-3.5 overfull closure + Type A/B disposal PROVEN;
   3.6 interior non-passive classification PROVEN conditional on G1;
   3.7 door-count split (q=3 seed / q>=4 A1-5mask) PROVEN as bookkeeping conditional on
   Seed3; **3.8 q<3 EXCLUSION: PENDING (structural)**.
4. Seeds: 4.2.2 EQ CERT-1 PROVEN; 4.2.3 EQ CERT-2 CERT-PENDING (LP-1 + product/SOS
   fallback; failure = local cone repair); 4.2.4 EQ passive AM CERT-PENDING (3 layer
   master cubes x 11 EQ row templates, fallback 27 sigs x 11 rows); 4.2.7 V1/V3 cubes
   CERT-PENDING; 4.3.1 SIB S7 = 36 gates CERT-PENDING; 4.3.2 SIB AM (3 cubes x 13 rows,
   fallback 27x13) CERT-PENDING.
5. 4-door: 5.2 A1-5mask PROVEN conditional on 5.3 five 4-mask certs (=M4 cone);
   5.4 + N>=10 PROVEN.
6. AM passive: 6.1 reduction PROVEN; 6.2 27 signatures = 3 layers x (2^2-1)^2 PROVEN;
   6.3 master-cube uniformity PROVEN as reduction, certs pending.
7. Non-passive: 7.1-7.2 Type A/B PROVEN; 7.3 Type C (non-C5-hom) PENDING through G1;
   7.4 Type D PROVEN conditional on G1.
8. **8.1 G1 non-C5-hom non-overfull lemma: PENDING (structural)** — if active closure
   is not C5-hom then I(Q) <= N. Failure = branch redesign (Groetzsch-type components).

## 10. CERTIFICATE-PENDING ledger (the complete remaining list)
10.1 A1 six ConeCerts (PMTSCone) — failure local.
10.2/5.3 five 4-mask 7/30 ConeCerts — failure local (slack to 3/10).
**10.3 G1: overfull rows are C5-hom (equiv: non-C5-hom => not overfull) — STRUCTURAL;
     failure = new ODL branch.**
**10.4 q<3 exclusion: saturated overfull core has >=3 effective doors — STRUCTURAL;
     failure = 1/2-door branch.**
**10.5 Seed3: saturated 3-door overfull cores reduce to EQ or SIB — STRUCTURAL;
     failure = third seed family.**
10.6 EQ-CERT2 LP (seed-vanishing; product/SOS fallback) — failure local.
10.7 EQ-AM master Bernstein (3 cubes x 11 rows; fallback 27x11) — failure local.
10.8 SIB-S7 36-gate family — failure local.
10.9 SIB-AM master Bernstein (3 cubes x 13 rows; fallback 27x13) — failure local.

## 11. Proven ledger
C5-RS reduction, beta_P<=1-from-A1, uniform width N/5, C5-RS=>net-DW', net-DW'=>GERSH_{L=5},
door bookkeeping, 4-door N>=10, A1-5mask arithmetic, EQ height, EQ CERT-1, AM reduction,
master-cube formulation (+vertex refutation), Type A/B/D classification (cond. G1).

## ASSESSMENT (Claude)
Only 10.3/10.4/10.5 are STRUCTURAL (graph lemmas, branch-level risk if false); everything
else is polynomial-certificate work with local-repair failure modes. NEXT: (a) census
validation gates for G1/q<3/Seed3 (Codex — closure/saturation infra), (b) GPT-Pro proofs
for the three structural lemmas, G1 first.
